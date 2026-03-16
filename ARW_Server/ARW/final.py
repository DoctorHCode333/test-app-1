import traceback
import io
import os
import re
import json
import time
import base64
import logging
import tempfile
import requests
import numpy as np
import threading
import secrets
import hashlib
from pathlib import Path

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import wave
import PureCloudPlatformClientV2 as pc2
from PureCloudPlatformClientV2.rest import ApiException

from flask import Flask, request, jsonify, send_file, Response, make_response
from flask_cors import CORS

from datetime import datetime, timezone



# ---- Environment (keep your Zscaler cert if required) ----
os.environ['REQUESTS_CA_BUNDLE'] = "C:\Harsh_official\Docs\ca-bundle.crt"
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, sent_wildcard=True, vary_header=True)

# ---------------- Models / Data ----------------

@dataclass
class RedactionSegment:
    start_time: float
    end_time: float
    phrase: str
    reason: str

# ---------------- Genesys Auth / APIs ----------------

class GenesysCloudAuth:
    def __init__(self, client_id: str, client_secret: str):
        # Region already agreed: usw2 (US West 2)
        pc2.configuration.host = pc2.PureCloudRegionHosts.us_west_2.get_api_host()
        self.api_client = pc2.ApiClient()
        try:
            self.api_client = pc2.ApiClient().get_client_credentials_token(
                client_id=client_id,
                client_secret=client_secret
            )
            print( self.api_client.access_token)
            logger.info("Authenticated to Genesys Cloud")
        except ApiException as ex:
            logger.error(f"SDK error getting token: {ex}")

    def get_access_token(self):
        # Health check helper
        return getattr(self.api_client, "access_token", None)


class GenesysAudioRedactor:
    def __init__(self, client_id: str, client_secret: str, environment: str):
        self.auth = GenesysCloudAuth(client_id, client_secret)
        # Initialize SDK API clients
        self.recording_api = pc2.RecordingApi(self.auth.api_client)
        self.conversations_api = pc2.ConversationsApi(self.auth.api_client)
        self.sta_api = pc2.SpeechTextAnalyticsApi(self.auth.api_client)
        self.conv_transcript = ""

    # --------------- Helpers: URL & HTTP ---------------

    @staticmethod
    def _add_query_param(uri: str, key: str, value: str) -> str:
        parsed = urlparse(uri)
        q = dict(parse_qsl(parsed.query))
        q[key] = value
        new_qs = urlencode(q)
        return urlunparse(parsed._replace(query=new_qs))

    def download_audio_file(self, media_uri: str) -> bytes:
        """
        Download audio from the pre-signed media URI (not a Genesys API call).
        """
        try:
            response = requests.get(media_uri, stream=True, timeout=120)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            traceback.print_exc()
            raise

    # --------------- WAV / PCM utilities (no ffmpeg) ---------------

    @staticmethod
    def _read_wav_bytes(b: bytes) -> Tuple[np.ndarray, int, int]:
        """
        Read WAV bytes into numpy array in float32 [-1, 1].
        Returns: (samples_float32_mono, sample_rate, num_channels_original)
        Supports 8/16/32-bit PCM. 24-bit PCM not supported here.
        """
        with wave.open(io.BytesIO(b), 'rb') as wf:
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            n_frames = wf.getnframes()
            frames = wf.readframes(n_frames)

        if sample_width == 1:
            # 8-bit unsigned PCM -> int16 -> float
            data = np.frombuffer(frames, dtype=np.uint8).astype(np.int16) - 128
            data = data.astype(np.float32) / 128.0
        elif sample_width == 2:
            data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        elif sample_width == 4:
            data = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
        else:
            raise ValueError(f"Unsupported WAV sample width: {sample_width} bytes")

        # Reshape to (num_frames, channels)
        if n_channels > 1:
            data = data.reshape(-1, n_channels)
            data = data.mean(axis=1)  # to mono
        # Now data is mono float32
        return data, frame_rate, n_channels

    @staticmethod
    def _write_wav_bytes(samples_mono: np.ndarray, sample_rate: int) -> bytes:
        """
        Write mono float32 [-1,1] samples as 16-bit PCM WAV bytes.
        """
        samples = np.clip(samples_mono, -1.0, 1.0)
        int16 = (samples * 32767.0).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(int16.tobytes())
        buf.seek(0)
        return buf.read()

    @staticmethod
    def _resample_if_needed(samples: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
        """
        Simple resampler using linear interpolation if sample rates differ.
        """
        if sr_in == sr_out:
            return samples
        # Create new time base
        dur_sec = len(samples) / sr_in
        t_in = np.linspace(0.0, dur_sec, num=len(samples), endpoint=False, dtype=np.float64)
        n_out = int(round(dur_sec * sr_out))
        t_out = np.linspace(0.0, dur_sec, num=n_out, endpoint=False, dtype=np.float64)
        # Interpolate
        return np.interp(t_out, t_in, samples).astype(np.float32)

    @staticmethod
    def _overlay_two_tracks(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Overlay two mono float32 tracks aligned at t=0 with -6 dB headroom on sum.
        Output length = max(len(a), len(b)).
        """
        n = max(len(a), len(b))
        a_pad = np.zeros(n, dtype=np.float32)
        b_pad = np.zeros(n, dtype=np.float32)
        a_pad[:len(a)] = a
        b_pad[:len(b)] = b
        # Mix with headroom (0.5 scaling)
        mix = 0.5 * (a_pad + b_pad)
        return np.clip(mix, -1.0, 1.0)

    @staticmethod
    def _apply_silence_segments(samples: np.ndarray, sr: int, segments: List[RedactionSegment]) -> np.ndarray:
        """
        Zero out (silence) the regions defined by segments.
        """
        if not segments:
            return samples
        out = samples.copy()
        for seg in segments:
            start_i = max(0, int(seg.start_time * sr))
            end_i = min(len(out), int(seg.end_time * sr))
            if end_i > start_i:
                out[start_i:end_i] = 0.0
        return out

    @staticmethod
    def ms_to_seconds_relative(ms_value: int, recording_start_ms: int) -> float:
        """
        Convert absolute millisecond timestamp (epoch time) to seconds relative to recording start.
        
        CRITICAL: Genesys provides transcript timestamps as absolute wall-clock time (epoch milliseconds),
        but audio recordings start from t=0. We MUST subtract the recording's actual start time to get
        the correct position in the audio file.
        
        Args:
            ms_value: Absolute timestamp in milliseconds (from transcript phrase)
            recording_start_ms: Absolute timestamp when the recording actually started
            
        Returns:
            float: Time in seconds from the start of the audio recording (t=0)
            
        Example:
            Recording starts at: 1733845800000 (epoch ms)
            Phrase timestamp:    1733845815000 (epoch ms)
            Result: (1733845815000 - 1733845800000) / 1000.0 = 15.0 seconds into the recording
        """
        if not recording_start_ms:
            logger.warning("No recording start time available, using raw timestamp conversion (may be inaccurate)")
            return ms_value / 1000.0
        return (ms_value - recording_start_ms) / 1000.0

    @staticmethod
    def calculate_cumulative_pause_before_time(annotations: List[Dict], phrase_start_ms: float, recording_start_ms: int) -> float:
        """
        Calculate cumulative pause/hold duration that occurred BEFORE a given phrase start time.
        
        This is critical because pauses occur at different times in the recording. We only want to
        subtract pauses that happened BEFORE the current phrase, not after.
        
        Args:
            annotations: List of annotation dictionaries from recording metadata
            phrase_start_ms: Absolute timestamp when the phrase starts (epoch ms)
            recording_start_ms: Absolute timestamp when recording started (epoch ms)           
        Returns:
            float: Cumulative pause/hold duration in seconds that occurred before this phrase
        """
        if not annotations or not recording_start_ms:
            return 0.0
        
        cumulative_pause_ms = 0
        
        for annotation in annotations:
            # Only process "Secure Pause" annotations - ignore regular pauses and holds
            annotation_description = annotation.get('description', '')
            if annotation_description != 'Secure Pause':
                continue
            
            # Try different location fields to find when pause occurred
            # absolute_location: absolute wall-clock time when pause started
            # location/recording_location: position in recording timeline (ms from recording start)
            # realtime_location: real-time position
            
            pause_absolute_start = annotation.get('absolute_location')
            pause_duration_ms = annotation.get('duration_ms', 0) or annotation.get('absolute_duration_ms', 0)
            
            if pause_absolute_start and phrase_start_ms:
                # Only count this pause if it STARTED before the phrase start time
                # Compare pause start location with phrase start time
                if pause_absolute_start < phrase_start_ms:
                    cumulative_pause_ms += pause_duration_ms
                    logger.debug(f"Secure Pause at {pause_absolute_start}ms (dur: {pause_duration_ms}ms) started before phrase at {phrase_start_ms}ms - COUNTED")
                else:
                    logger.debug(f"Secure Pause at {pause_absolute_start}ms (dur: {pause_duration_ms}ms) is at/after phrase at {phrase_start_ms}ms - SKIPPED")
        
        cumulative_pause_seconds = cumulative_pause_ms / 1000.0
        return cumulative_pause_seconds

    # --------------- Genesys SDK: Recordings / Transcripts ---------------

    def get_conversation_recording(self, conversation_id: str) -> Optional[Dict]:
        """
        Fetch recordings for a conversation; return a list of WAV media URIs (customer + agent). Retries briefly while recordings are processing.
        """
        try:
            max_attempts = 10
            wait_seconds = 20

            # opts = {
            # "maxWaitMs": 5000,
            # "formatId": "WEBM",
            # "mediaFormats": ["mediaFormats_example"]
            # }

            for attempt in range(1, max_attempts + 1):
                recs = self.recording_api.get_conversation_recordings(conversation_id,format_id="WAV",media_formats=['WAV'], locale="en-US")

                if recs:
                    all_wav_uris: List[str] = []
                    rec_ids: List[str] = []
                    recording_start_time_ms = None
                    all_annotations: List[Dict] = []  # Collect annotations from ALL recordings

                    for rec in recs:
                        # Debug: log all available recording attributes
                        logger.info(f"Recording object attributes: {dir(rec)}")
                        rec_dict = rec.to_dict() if hasattr(rec, "to_dict") else {}
                        logger.info(f"Recording metadata: {json.dumps(rec_dict, default=str, indent=2)}")
                        
                        rec_ids.append(getattr(rec, "id", None))
                        
                        # Collect annotations from this recording
                        rec_annotations = rec_dict.get('annotations', [])
                        if rec_annotations:
                            logger.info(f"Found {len(rec_annotations)} annotations in recording {getattr(rec, 'id', 'unknown')}")
                            all_annotations.extend(rec_annotations)  # Add to the combined list
                        
                        # Try to get recording start time (various possible field names)
                        if not recording_start_time_ms:
                            recording_start_time_ms = (
                                getattr(rec, "conversation_start_time", None) or
                                getattr(rec, "recording_start_time", None) or
                                getattr(rec, "start_time", None) or
                                rec_dict.get("conversationStartTime") or
                                rec_dict.get("recordingStartTime") or
                                rec_dict.get("startTime")
                            )
                        
                        media_uris = getattr(rec, "media_uris", None)

                        if media_uris:
                            # dict-like: {"0": RecordingMediaUri(media_uri=...), "1": ...}
                            for k in sorted(media_uris.keys(), key=str):
                                uri = media_uris[k].media_uri
                                if uri:
                                    all_wav_uris.append(uri)
                        else:
                            # Some orgs see single media_uri
                            uri = getattr(rec, "media_uri", None)
                            if uri:
                                uri_wav = self._add_query_param(uri, "formatId", "wav")
                                all_wav_uris.append(uri_wav)

                    # Deduplicate while preserving order
                    seen = set()
                    unique_uris = []
                    for u in all_wav_uris:
                        if u not in seen:
                            unique_uris.append(u)
                            seen.add(u)

                    if unique_uris:
                        # Convert recording_start_time_ms to integer if it's a string/datetime
                        if recording_start_time_ms:
                            if isinstance(recording_start_time_ms, str):
                                # Try parsing as ISO datetime string
                                try:
                                    dt = datetime.fromisoformat(recording_start_time_ms.replace('Z', '+00:00'))
                                    recording_start_time_ms = int(dt.timestamp() * 1000)
                                except:
                                    # Try parsing as numeric string
                                    try:
                                        recording_start_time_ms = int(float(recording_start_time_ms))
                                    except:
                                        logger.warning(f"Could not parse recording start time: {recording_start_time_ms}")
                                        recording_start_time_ms = None
                            elif isinstance(recording_start_time_ms, datetime):
                                recording_start_time_ms = int(recording_start_time_ms.timestamp() * 1000)
                            elif isinstance(recording_start_time_ms, float):
                                # Normalize to milliseconds if in seconds
                                recording_start_time_ms = int(recording_start_time_ms) if recording_start_time_ms > 1000000000000 else int(recording_start_time_ms * 1000)
                        
                        logger.info(f"Recording start time found: {recording_start_time_ms} (type: {type(recording_start_time_ms)})")
                        
                        # Log total annotations collected from all recordings
                        logger.info(f"Total annotations collected from {len(recs)} recording(s): {len(all_annotations)}")
                        
                        return {
                            "conversation_id": conversation_id,
                            "recording_ids": rec_ids,
                            "media_uris": unique_uris,
                            "recording_start_time_ms": recording_start_time_ms,
                            "annotations": all_annotations  # Return ALL annotations from ALL recordings
                        }

                    # URIs not yet populated; brief retry
                    # if attempt < max_attempts:
                    #     logger.info("Recordings present but no media URIs (attempt %d/%d). Retrying in %ss...",
                    #                 attempt, max_attempts, wait_seconds)
                    #     time.sleep(wait_seconds)
                    #     continue

                if attempt < max_attempts:
                    logger.info("Recording not ready yet (attempt %d/%d). Retrying in %ss...",
                                attempt, max_attempts, wait_seconds)
                    time.sleep(wait_seconds)
            logger.warning(f"No recordings found or no URIs for conversation {conversation_id} after retries")
            return None

        except ApiException as e:
            logger.error(f"SDK error getting recordings: {e}")
            traceback.print_exc()
            return None

    def _find_voice_communication_id(self, conversation_dict: Dict) -> Optional[str]:
        """
        Find the 'communicationId' for the customer's voice leg.
        """
        try:
            for p in conversation_dict.get("participants", []):
                if str(p.get("purpose", "")).lower() in ("customer", "external"):
                    for c in p.get("calls", []):
                        comm_id = c.get("id") or c.get("communicationId")
                        if comm_id:
                            return comm_id
            # Fallback: scan all participants
            for p in conversation_dict.get("participants", []):
                for c in p.get("calls", []):
                    comm_id = c.get("id") or c.get("communicationId")
                    if comm_id:
                        return comm_id
        except Exception:
            pass
        return None

    def _get_conversation_start_time(self, conversation_id: str) -> Optional[int]:
        """
        Get the conversation start time as a fallback if recording start time is not available.
        This searches for conversationStart timestamp in the conversation metadata.
        """
        try:
            convo_obj = self.conversations_api.get_conversation(conversation_id)
            convo_dict = convo_obj.to_dict() if hasattr(convo_obj, "to_dict") else convo_obj
            
            # Try various possible field names for conversation start
            start_time = (
                convo_dict.get("conversationStart") or
                convo_dict.get("startTime") or
                convo_dict.get("start_time")
            )
            
            if start_time:
                # Convert datetime string to milliseconds if needed
                if isinstance(start_time, str):
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    return int(dt.timestamp() * 1000)
                elif isinstance(start_time, datetime):
                    return int(start_time.timestamp() * 1000)
                elif isinstance(start_time, (int, float)):
                    # Already in milliseconds or seconds, normalize to ms
                    return int(start_time) if start_time > 1000000000000 else int(start_time * 1000)
            
            logger.debug(f"Conversation dict keys: {convo_dict.keys()}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting conversation start time: {e}")
            return None

    def get_transcript_data(self, conversation_id: str) -> Optional[Dict]:
        """
        Use Speech & Text Analytics to get a pre-signed transcript URL, then download JSON.
        """
        try:
            convo_obj = self.conversations_api.get_conversation(conversation_id)
            convo_dict = convo_obj.to_dict() if hasattr(convo_obj, "to_dict") else convo_obj
            communication_id = self._find_voice_communication_id(convo_dict)

            if not communication_id:
                logger.warning("Could not determine communicationId for conversation %s", conversation_id)
                return None

            # Try plural first
            try:
                urls_resp = self.sta_api.get_speechandtextanalytics_conversation_communication_transcripturls(
                    conversation_id, communication_id
                )
                urls_dict = urls_resp.to_dict() if hasattr(urls_resp, "to_dict") else urls_resp
                transcript_urls = urls_dict.get("transcript_urls") or urls_dict.get("urls") or []
                if not transcript_urls and "transcript_file_url" in urls_dict:
                    transcript_urls = [{"transcriptFileUrl": urls_dict["transcript_file_url"]}]
            except pc2.rest.ApiException:
                # Fallback to singular
                url_resp = self.sta_api.get_speechandtextanalytics_conversation_communication_transcripturl(
                    conversation_id, communication_id
                )
                url_dict = url_resp.to_dict() if hasattr(url_resp, "to_dict") else url_resp
                transcript_urls = [{"transcriptFileUrl": url_dict.get("transcript_file_url")}]

            presigned = None

            for u in transcript_urls:
                presigned = u.get("transcriptFileUrl") or u.get("url")
                if presigned:
                    break

            if not presigned:
                logger.warning("No transcript URL returned for conversation %s", conversation_id)
                return None
            r = requests.get(presigned, timeout=60)
            r.raise_for_status()
            return r.json()

        except pc2.rest.ApiException as e:
            logger.error(f"SDK error fetching transcript URL(s): {e}")
            return None
        except requests.RequestException as e:
            logger.error(f"Error downloading transcript JSON: {e}")
            traceback.print_exc()
            return None

    from typing import Dict, Optional

    def get_transcript(self,transcript_data: Dict) -> Optional[str]:
        """
        Parse Genesys Cloud conversation transcript and stitch phrases together
        grouped by participantPurpose (e.g., 'agent' vs 'customer').

        Args:
            transcript_data (Dict): Dictionary containing transcript details with
                                    structure similar to Genesys Cloud API response.

        Returns:
            Optional[str]: A formatted string combining conversation text by type,
                           or None if parsing fails.
        """
        try:
            transcripts = transcript_data.get("transcripts", [])
            if not transcripts:
                return None

            result = []
            current_type = None
            current_text = ""

            for transcript in transcripts:
                phrases = transcript.get("phrases", [])
                for phrase in phrases:
                    text = phrase.get("text", "").strip()
                    participant_purpose = phrase.get("participantPurpose", "").strip()

                    if not text or not participant_purpose:
                        continue

                    if participant_purpose != current_type:
                        # Push previous chunk if exists
                        if current_text:
                            if current_type=="internal":
                                result.append({"type": "#Agent", "text": current_text})
                            elif current_type=="external":
                                result.append({"type": "#Customer", "text": current_text})

                        # Start new chunk
                        current_type = participant_purpose
                        current_text = text
                    else:
                        # Append to current chunk
                        current_text += " " + text

            # Handle last chunk
            if current_text:
                result.append({"type": current_type, "text": current_text})

            # Format result as: type:"text" type:"text"
            formatted_result = "".join([f'{item["type"]}:" {item["text"]}"' for item in result])

            return formatted_result

        except Exception as e:
            import traceback
            print(f"Error while parsing transcript: {e}")
            traceback.print_exc()
            return None

    def get_conversation_details(self, conversation_id: str) -> Optional[Dict]:
        try:
            convo = self.conversations_api.get_conversation(conversation_id)
            return convo.to_dict() if hasattr(convo, "to_dict") else convo
        except pc2.rest.ApiException as e:
            logger.error(f"SDK error getting conversation details: {e}")
            traceback.print_exc()
            return None

    # --------------- PII Detection / Segments ---------------

    def extract_participant_data(self, conversation_details: Dict) -> Dict[str, any]:
        participant_info = {}
        if 'FNAME' in conversation_details:
            participant_info['name'] = conversation_details['FNAME']
        if 'LNAME' in conversation_details:
            participant_info['name'] = conversation_details['FNAME']
        if 'ANI' in conversation_details:
            participant_info['ani'] = conversation_details['ANI']
        if 'DNIS' in conversation_details:
            participant_info['dnis'] = conversation_details['DNIS']
        if 'Address' in conversation_details:
            participant_info['address'] = conversation_details['Address']
        if 'FullAddress' in conversation_details:
            participant_info['address'] = conversation_details['FullAddress']
        if 'Email' in conversation_details:
            participant_info['email'] = conversation_details['Email']
        if 'State' in conversation_details:
            participant_info['state'] = conversation_details['State']

        return participant_info

    @staticmethod
    def convert_spoken_number_to_digits(text: str) -> int:
        """
        Convert spoken/written numbers to their numeric value to count digits.
        Handles combinations like "six hundred sixty two" or "5 hundred and ninety seven"
        Returns the numeric value, or 0 if no number detected.
        """
        text = text.lower().strip()
        
        # Number word mappings
        ones = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19
        }
        
        tens = {
            'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
            'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
        }
        
        scales = {
            'hundred': 100,
            'thousand': 1000,
            'million': 1000000,
            'billion': 1000000000
        }
        
        # Split text into words and clean
        words = re.findall(r'\b[\w]+\b', text)
        
        current = 0
        result = 0
        
        for word in words:
            # Handle digit strings (like "5" in "5 hundred")
            if word.isdigit():
                current += int(word)
            elif word in ones:
                current += ones[word]
            elif word in tens:
                current += tens[word]
            elif word in scales:
                if word == 'hundred':
                    current = (current or 1) * 100
                else:
                    # thousand, million, billion
                    current = (current or 1) * scales[word]
                    result += current
                    current = 0
        
        return result + current
    
    @staticmethod
    def contains_three_digit_number(text: str) -> bool:
        """
        Check if text contains a number with 3 or more digits.
        Handles both numeric (123, 456) and spoken forms (six hundred, three hundred fifty).
        """
        text = text.lower()
        
        # Check for explicit digits (100+)
        if re.search(r'\b\d{3,}\b', text):
            return True
        
        # Look for spoken number patterns that indicate 3+ digits
        # Pattern 1: "X hundred" variations
        hundred_patterns = [
            r'\b(one|two|three|four|five|six|seven|eight|nine|\d)\s*hundred',
            r'\bhundred',  # Just "hundred" alone
        ]
        
        for pattern in hundred_patterns:
            if re.search(pattern, text):
                return True
        
        # Pattern 2: Large tens + ones combinations (e.g., "ninety seven" = 97 is < 100, but "five hundred ninety seven" = 597)
        # Check for thousand/million/billion
        if re.search(r'\b(thousand|million|billion)\b', text):
            return True
        
        # Try to parse the entire text as a spoken number
        try:
            # Look for number phrases by finding sequences of number words
            number_words = r'\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|\d+)\b'
            matches = re.findall(number_words, text)
            
            if len(matches) >= 2:  # At least 2 number words suggests a compound number
                # Join the matches and try to convert
                number_phrase = ' '.join(matches)
                value = GenesysAudioRedactor.convert_spoken_number_to_digits(number_phrase)
                if value >= 100:  # 3 digits or more
                    return True
        except:
            pass
        
        return False

    def detect_pii_patterns(self, text: str) -> List[Dict]:
        patterns = {
            # Matches U.S. Social Security Numbers like 123-45-6789 or 123456789
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',

            # Matches credit card numbers like 1234-5678-9012-3456 or 1234567890123456
            'credit_card': r'\b(?:\d{4}[\s-]?){3}\d{4}\b',

            # Matches U.S. phone numbers: (123) 456-7890, 123-456-7890, +1-123-456-7890
            'phone': r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',

            # Matches email addresses like user@example.com
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',

            # Matches multiple date of birth formats:
            # - MM/DD/YYYY or MM-DD-YYYY
            # - DD/MM/YYYY or DD-MM-YYYY
            # - YYYY-MM-DD
            # - Month DD, YYYY (e.g., January 15, 1990)
            'date_of_birth': (
                r'\b('
                r'(?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12]\d|3[01])[-/](?:19|20)\d{2}'  # MM/DD/YYYY or MM-DD-YYYY01])[-/](?:0[1-9]|1[0-2])[-/Y
                r'|'
                r'(?:19|20)\d{2}?:0?:0[1-9]|[12]\d|3[01]'  # YYYY-MM-DD
                r'|'
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+(?:19|20)\d{2}'  # Month DD, YYYY
                r')\b'
            ),

            # Matches U.S. ZIP codes: 12345 or 12345-6789
            'zip_code': r'\b\d{5}(?:-\d{4})?\b',

            # Matches account numbers preceded by "account" or "acct" and then digits (6 or more)
            'account_number': r'\b(?:account|acct)[\s#:]*(\d{6,})\b',

            # Matches routing numbers (exactly 9 digits)
            'routing_number': r'\b\d{9}\b',

            # Matches license plates with 2-3 alphanumeric chars, optional dash/space, then 3-4 alphanumeric chars
            # 'license_plate': r'\b[A-Z0-9]{2,3}[-\s]?[A-Z0-9]{3,4}\b',

            # Matches Medicare IDs like 123-45-6789A
            'medicare_id': r'\b\d{3}-\d{2}-\d{4}[A-Z]\b',
        }

        detected_pii = []
        
        # Check all regex patterns
        for pii_type, pattern in patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                detected_pii.append({
                    'type': pii_type,
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        # Check for spoken/written numbers with 3+ digits
        if self.contains_three_digit_number(text):
            detected_pii.append({
                'type': 'spoken_large_number',
                'text': text,
                'start': 0,
                'end': len(text)
            })
        
        return detected_pii

    def find_participant_data_in_transcript(self, transcript_data: Dict, participants_data: Dict, recording_start_ms: int = None, annotations: List[Dict] = None) -> List[RedactionSegment]:
        redaction_segments = []

        # print(transcript_data['transcripts'])
        if 'transcripts' not in transcript_data or 'phrases' not in transcript_data['transcripts'][0]:
            return redaction_segments
            
        for transcript in transcript_data['transcripts']:

            phrases = transcript.get('phrases', [])
            if not phrases:
                continue

            # COMMENTED OUT: Build a map of silence events by their start time for this transcript
            # silence_events = []
            # if 'analytics' in transcript:
            #     analytics = transcript.get('analytics', {})
            #     acoustic_events = analytics.get('acoustics', [])
            #     for event in acoustic_events:
            #         if event.get('eventType') == 'silence':
            #             silence_start_ms = event.get('startTimeMs', 0)
            #             silence_duration_ms = event.get('durationMs', 0)
            #             silence_events.append({
            #                 'start_ms': silence_start_ms,
            #                 'duration_ms': silence_duration_ms
            #             })
            #     logger.info(f"Found {len(silence_events)} silence events in transcript")
            #     print(silence_events)
            
            for phrase in phrases:
                start_ms = phrase.get('startTimeMs', 0)
                duration_ms = phrase['duration']['milliseconds']
                
                # COMMENTED OUT: Calculate cumulative silence BEFORE this phrase starts
                # cumulative_silence_ms = 0
                # for silence in silence_events:
                #     # Only count silence that ended before or at the phrase start
                #     silence_end_ms = silence['start_ms'] + silence['duration_ms']
                #     if silence_end_ms <= start_ms:
                #         cumulative_silence_ms += silence['duration_ms']
                

                
                # Convert to seconds relative to recording start, then subtract cumulative pause duration

                start_time = self.ms_to_seconds_relative(start_ms, recording_start_ms)
                # Calculate cumulative pause/hold that occurred BEFORE this phrase
                cumulative_pause_duration = self.calculate_cumulative_pause_before_time(
                    annotations or [], start_time*1000, recording_start_ms
                )

                start_time -= cumulative_pause_duration
                end_time = start_time + (duration_ms / 1000.0) + 3
                
                # Ensure times don't go negative
                start_time = max(0.0, start_time)
                end_time = max(start_time, end_time)
                
                phrase_text = phrase.get('text', '').lower()
                for field, value in participants_data.items():
                    if value and len(str(value)) > 2 and str(value).lower() in phrase_text:

                        self.conv_transcript = self.conv_transcript.replace(phrase_text,"[Redacted]")
                        redaction_segments.append(RedactionSegment(
                            start_time=start_time,
                            end_time=end_time,
                            phrase=phrase_text,
                            reason=f"Participant {field}: {value}"
                        ))
                        break
        return redaction_segments

    def find_pii_in_transcript(self, transcript_data: Dict, recording_start_ms: int = None, annotations: List[Dict] = None) -> List[RedactionSegment]:
        redaction_segments = []
        if 'transcripts' not in transcript_data or 'phrases' not in transcript_data['transcripts'][0]:
            return redaction_segments

        for transcript in transcript_data['transcripts']:
            phrases = transcript.get('phrases', [])
            if not phrases:
                continue

            # COMMENTED OUT: Build a map of silence events by their start time for this transcript
            # silence_events = []
            # if 'analytics' in transcript:
            #     analytics = transcript.get('analytics', {})
            #     acoustic_events = analytics.get('acoustics', [])
            #     for event in acoustic_events:
            #         if event.get('eventType') == 'silence':
            #             silence_start_ms = event.get('startTimeMs', 0)
            #             silence_duration_ms = event.get('silenceDurationMs', 0)
            #             silence_events.append({
            #                 'start_ms': silence_start_ms,
            #                 'duration_ms': silence_duration_ms
            #             })

            for phrase in phrases:
                phrase_text = phrase.get('text', '')
                start_ms = phrase.get('startTimeMs', 0)
                duration_ms = phrase.get('durationMs', 0) or phrase.get('duration', {}).get('milliseconds', 0)
                
                # COMMENTED OUT: Calculate cumulative silence BEFORE this phrase starts
                # cumulative_silence_ms = 0
                # for silence in silence_events:
                #     # Only count silence that ended before or at the phrase start
                #     silence_end_ms = silence['start_ms'] + silence['duration_ms']
                #     if silence_end_ms <= start_ms:
                #         cumulative_silence_ms += silence['duration_ms']
                
                # Calculate cumulative pause/hold that occurred BEFORE this phrase
                start_time = self.ms_to_seconds_relative(start_ms, recording_start_ms)
                # Calculate cumulative pause/hold that occurred BEFORE this phrase
                cumulative_pause_duration = self.calculate_cumulative_pause_before_time(
                    annotations or [], start_time * 1000, recording_start_ms
                )

                start_time -= cumulative_pause_duration
                end_time = start_time + (duration_ms / 1000.0) + 3
                
                # Ensure times don't go negative
                start_time = max(0.0, start_time)
                end_time = max(start_time, end_time)

                pii_matches = self.detect_pii_patterns(phrase_text)

                if pii_matches:
                    self.conv_transcript = self.conv_transcript.replace(phrase_text, "[Redacted]")
                    redaction_segments.append(RedactionSegment(
                        start_time=start_time,
                        end_time=end_time,
                        phrase=phrase_text,
                        reason=f"PII detected: {', '.join([m['type'] for m in pii_matches])}"
                    ))

        return redaction_segments

    def merge_overlapping_segments(self, segments: List[RedactionSegment]) -> List[RedactionSegment]:
        if not segments:
            return segments
        segments.sort(key=lambda x: x.start_time)
        merged = [segments[0]]
        for current in segments[1:]:
            last = merged[-1]
            # Merge if overlapping or within 0.5s
            if current.start_time <= last.end_time + 0.5:
                merged[-1] = RedactionSegment(
                    start_time=last.start_time,
                    end_time=max(last.end_time, current.end_time),
                    phrase=f"{last.phrase} | {current.phrase}",
                    reason=f"{last.reason} | {current.reason}"
                )
            else:
                merged.append(current)
        return merged

    # --------------- Core processing: overlay & redact (WAV end-to-end) ---------------

    def _overlay_wav_uris(self, wav_uris: List[str]) -> Tuple[bytes, int]:
        """
        Download up to two WAV URIs, overlay them from t=0 and return (mixed_wav_bytes, sample_rate).
        If only one URI present, return it as-is.
        """
        if not wav_uris:
            raise ValueError("No WAV URIs provided")

        # Download the first stream
        a_bytes = self.download_audio_file(wav_uris[0])
        a, sr_a, _ = self._read_wav_bytes(a_bytes)

        if len(wav_uris) == 1:
            # Return normalized WAV bytes (rewritten to ensure consistent format)
            out_bytes = self._write_wav_bytes(a, sr_a)
            return out_bytes, sr_a

        # Download the second stream
        b_bytes = self.download_audio_file(wav_uris[1])
        b, sr_b, _ = self._read_wav_bytes(b_bytes)

        # Resample if needed
        target_sr = sr_a
        if sr_b != target_sr:
            b = self._resample_if_needed(b, sr_b, target_sr)

        mixed = self._overlay_two_tracks(a, b)
        out_bytes = self._write_wav_bytes(mixed, target_sr)
        return out_bytes, target_sr

    def _redact_wav_by_silencing(self, wav_bytes: bytes, segments: List[RedactionSegment]) -> bytes:
        """
        Replace specified regions with silence and return WAV bytes (mono, 16-bit).
        """
        print("Here 527")
        samples, sr, _ = self._read_wav_bytes(wav_bytes)
        redacted = self._apply_silence_segments(samples, sr, segments)
        return self._write_wav_bytes(redacted, sr)

    def process_conversation(self, conversation_id: str, attributes) -> Dict:
        try:
            # Step 1: Get recording info & media URIs (WAV format)
            recording_info = self.get_conversation_recording(conversation_id)
            if not recording_info or not recording_info.get("media_uris"):
                return {'error': 'No recording media URIs found for conversation'}

            media_uris: List[str] = recording_info["media_uris"]
            recording_start_ms = recording_info.get("recording_start_time_ms")
            annotations = recording_info.get("annotations", [])
            
            # Log annotation details for debugging
            if annotations:
                logger.info(f"Found {len(annotations)} annotations in recording:")
                secure_pause_count = 0
                for ann in annotations:
                    # Only log Secure Pause annotations
                    if ann.get('description') == 'Secure Pause':
                        secure_pause_count += 1
                        logger.info(f"  - Secure Pause: location={ann.get('location')}ms, "
                                  f"absolute_location={ann.get('absolute_location')}ms, "
                                  f"duration={ann.get('duration_ms')}ms, "
                                  f"realtime_location={ann.get('realtime_location')}ms")
                logger.info(f"Found {secure_pause_count} Secure Pause annotations to subtract")
            
            # Fallback: if recording start time not available, try conversation start time
            if not recording_start_ms:
                logger.warning("⚠️  Recording start time not found in recording metadata, trying conversation start time...")
                recording_start_ms = self._get_conversation_start_time(conversation_id)
            
            if not recording_start_ms:
                logger.error("❌ CRITICAL: No timestamp reference available!")
                logger.error("❌ Redactions will likely occur at INCORRECT positions in the audio!")
                logger.error("❌ Consider using first transcript phrase time as approximate fallback...")
                # Last resort: use first transcript phrase (original buggy behavior)
            else:
                try:
                    # Ensure recording_start_ms is an integer
                    recording_start_ms = int(recording_start_ms) if recording_start_ms else None
                    if recording_start_ms:
                        logger.info(f"✓ Using recording start time: {recording_start_ms} ({datetime.fromtimestamp(recording_start_ms/1000, tz=timezone.utc)})")
                except (ValueError, TypeError) as e:
                    logger.error(f"❌ Invalid recording start time format: {recording_start_ms} - {e}")
                    recording_start_ms = None
            
            if len(media_uris) > 2:
                logger.info(f"Found {len(media_uris)} streams; using first two for overlay")

            # Step 2: (Optional) Get participant attributes if passed-in
            participants_data = self.extract_participant_data(attributes) if attributes else {}

            # Step 3: Get transcript for PII detection
            # Use first recording id for transcript linkage
            transcript_data = self.get_transcript_data(conversation_id)
            if not transcript_data:
                logger.warning("Transcript not available; proceeding without redaction")
                redaction_segments = []
            else:
                self.conv_transcript = self.get_transcript(transcript_data)
                participant_segments = self.find_participant_data_in_transcript(transcript_data, participants_data, recording_start_ms, annotations)
                pii_segments = self.find_pii_in_transcript(transcript_data, recording_start_ms, annotations)
                redaction_segments = self.merge_overlapping_segments(participant_segments + pii_segments)
            print(redaction_segments)
            logger.info(f"Segments to redact: {len(redaction_segments)}")

            # Step 4: Overlay streams (WAV -> WAV, no ffmpeg)
            mixed_wav_bytes, sr = self._overlay_wav_uris(media_uris[:2])
            
            # Validation: Log audio duration and transcript time range for verification
            audio_duration_sec = len(self._read_wav_bytes(mixed_wav_bytes)[0]) / sr
            logger.info(f"📊 Audio duration: {audio_duration_sec:.2f} seconds")
            
            if redaction_segments:
                first_seg = min(redaction_segments, key=lambda s: s.start_time)
                last_seg = max(redaction_segments, key=lambda s: s.end_time)
                logger.info(f"📊 Redaction time range: {first_seg.start_time:.2f}s to {last_seg.end_time:.2f}s")
                
                if last_seg.end_time > audio_duration_sec:
                    logger.error(f"❌ MISMATCH: Redaction extends beyond audio! Audio={audio_duration_sec:.2f}s, Last redaction={last_seg.end_time:.2f}s")
                    logger.error(f"❌ This indicates timestamp synchronization is still incorrect!")

            # Step 5: Apply redaction (silence) on mixed audio
            final_wav_bytes = self._redact_wav_by_silencing(mixed_wav_bytes, redaction_segments)

            # Step 6: Save to temp .wav and return path
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            output_file.write(final_wav_bytes)
            output_file.close()
            print(output_file.name)
            return {
                'success': True,
                'redacted_audio_file': output_file.name,
                'segments_redacted': len(redaction_segments),
                'conversation_text': self.conv_transcript,
                'redaction_details': [
                    {
                        'start_time': seg.start_time,
                        'end_time': seg.end_time,
                        'duration': seg.end_time - seg.start_time,
                        'reason': seg.reason
                    } for seg in redaction_segments
                ]
            }

        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            traceback.print_exc()
            return {'error': str(e)}


# ---------------- Flask wiring ----------------

# Cache management for temporary files
file_cache = {}  # {conversation_id: {'path': str, 'timestamp': float, 'transcript': str}}
cache_lock = threading.Lock()
CACHE_EXPIRY_SECONDS = 7200  # 2 hours

# Streaming token management (for anti-download protection)
# Format: {token: {'conversation_id': str, 'expires_at': float, 'ip': str}}
stream_tokens = {}
token_lock = threading.Lock()
TOKEN_EXPIRY_SECONDS = 3600  # 1 hour - tokens expire after 1 hour

def generate_stream_token(conversation_id: str, client_ip: str) -> str:
    """Generate a secure, time-limited token for streaming access"""
    token = secrets.token_urlsafe(32)
    expires_at = time.time() + TOKEN_EXPIRY_SECONDS
    
    with token_lock:
        # Clean up expired tokens first
        cleanup_expired_tokens()
        
        # Store new token
        stream_tokens[token] = {
            'conversation_id': conversation_id,
            'expires_at': expires_at,
            'ip': client_ip,
            'created_at': time.time()
        }
    
    logger.info(f"Generated stream token for conversation {conversation_id}, expires in {TOKEN_EXPIRY_SECONDS}s")
    return token

def validate_stream_token(token: str, conversation_id: str, client_ip: str) -> bool:
    """Validate streaming token - checks expiry, conversation ID, and IP"""
    with token_lock:
        if token not in stream_tokens:
            logger.warning(f"Invalid token attempt from {client_ip}")
            return False
        
        token_data = stream_tokens[token]
        
        # Check expiry
        if time.time() > token_data['expires_at']:
            logger.warning(f"Expired token attempt from {client_ip}")
            del stream_tokens[token]
            return False
        
        # Check conversation ID match
        if token_data['conversation_id'] != conversation_id:
            logger.warning(f"Token conversation ID mismatch from {client_ip}")
            return False
        
        # Check IP match (prevent token sharing)
        if token_data['ip'] != client_ip:
            logger.warning(f"Token IP mismatch: expected {token_data['ip']}, got {client_ip}")
            return False
        
        return True

def cleanup_expired_tokens():
    """Remove expired streaming tokens"""
    current_time = time.time()
    expired_tokens = [
        token for token, data in stream_tokens.items()
        if current_time > data['expires_at']
    ]
    
    for token in expired_tokens:
        del stream_tokens[token]
    
    if expired_tokens:
        logger.info(f"Cleaned up {len(expired_tokens)} expired stream tokens")

def cleanup_expired_cache():
    """Remove cached files older than 2 hours"""
    with cache_lock:
        current_time = time.time()
        expired_ids = []
        
        for conv_id, cache_data in file_cache.items():
            if current_time - cache_data['timestamp'] > CACHE_EXPIRY_SECONDS:
                # Delete the file
                try:
                    if os.path.exists(cache_data['path']):
                        os.unlink(cache_data['path'])
                        logger.info(f"Deleted expired cache file for conversation {conv_id}")
                except Exception as e:
                    logger.warning(f"Failed to delete expired cache file: {e}")
                expired_ids.append(conv_id)
        
        # Remove from cache dict
        for conv_id in expired_ids:
            del file_cache[conv_id]

def schedule_cleanup(conv_id: str, delay: int = CACHE_EXPIRY_SECONDS):
    """Schedule automatic cleanup of cached file after delay"""
    def cleanup():
        time.sleep(delay)
        with cache_lock:
            if conv_id in file_cache:
                cache_data = file_cache[conv_id]
                try:
                    if os.path.exists(cache_data['path']):
                        os.unlink(cache_data['path'])
                        logger.info(f"Auto-deleted cache file for conversation {conv_id} after {delay}s")
                except Exception as e:
                    logger.warning(f"Failed to auto-delete cache file: {e}")
                del file_cache[conv_id]
    
    thread = threading.Thread(target=cleanup, daemon=True)
    thread.start()

def send_file_with_range(file_path: str, mimetype: str = 'audio/mpeg') -> Response:
    """Send file with HTTP Range support for streaming"""
    file_size = os.path.getsize(file_path)
    range_header = request.headers.get('Range')
    
    if not range_header:
        # No range requested, send full file
        def generate():
            with open(file_path, 'rb') as f:
                chunk_size = 8192  # 8KB chunks
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        
        response = Response(generate(), mimetype=mimetype)
        response.headers['Content-Length'] = str(file_size)
        response.headers['Accept-Ranges'] = 'bytes'
        return response
    
    # Parse Range header (format: bytes=start-end)
    try:
        range_match = re.match(r'bytes=(\d*)-(\d*)', range_header)
        if not range_match:
            return Response('Invalid Range header', status=416)
        
        start = range_match.group(1)
        end = range_match.group(2)
        
        start = int(start) if start else 0
        end = int(end) if end else file_size - 1
        
        # Validate range
        if start >= file_size or start < 0 or end >= file_size or start > end:
            response = Response('Range not satisfiable', status=416)
            response.headers['Content-Range'] = f'bytes */{file_size}'
            return response
        
        content_length = end - start + 1
        
        def generate():
            with open(file_path, 'rb') as f:
                f.seek(start)
                remaining = content_length
                chunk_size = 8192  # 8KB chunks
                
                while remaining > 0:
                    read_size = min(chunk_size, remaining)
                    chunk = f.read(read_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        
        response = Response(generate(), status=206, mimetype=mimetype)
        response.headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response.headers['Content-Length'] = str(content_length)
        response.headers['Accept-Ranges'] = 'bytes'
        return response
        
    except Exception as e:
        logger.error(f"Error handling range request: {e}")
        return Response('Error processing range request', status=500)

redactor = None

def init_redactor():
    global redactor
    # TODO: move to environment variables for production
    CLIENT_ID = "a0023ccb-e42a-4b39-b680-57faaeeee8fc"
    CLIENT_SECRET = "_v6jYlJ0agW5-u5CqTmZK5WO7sbPNenXzW9ZxwcVecE"
    ENVIRONMENT = "usw2.pure.cloud"
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("GENESYS_CLIENT_ID and GENESYS_CLIENT_SECRET are required")
    redactor = GenesysAudioRedactor(CLIENT_ID, CLIENT_SECRET, ENVIRONMENT)
    logger.info("Genesys Cloud redactor initialized successfully")

@app.route('/redact-conversation', methods=['POST'])
def redact_conversation():
    try:
        if redactor is None:
            init_redactor()
        
        data = request.get_json()
        conversation_id = data.get('conversationId')
        attributes = data.get('attributes', {})

        if not conversation_id:
            return jsonify({'error': 'conversationId is required'}), 400

        # Clean up any expired cache entries and tokens first
        cleanup_expired_cache()
        cleanup_expired_tokens()
        
        # Get client IP for token validation
        client_ip = request.remote_addr or 'unknown'
        
        # Check if file exists in cache
        with cache_lock:
            if conversation_id in file_cache:
                cache_data = file_cache[conversation_id]
                cached_file = cache_data['path']
                
                # Verify file still exists
                if os.path.exists(cached_file):
                    logger.info(f"Serving cached file for conversation: {conversation_id}")
                    
                    # Generate a new streaming token
                    stream_token = generate_stream_token(conversation_id, client_ip)
                    
                    # Return JSON response with token instead of file
                    return jsonify({
                        'status': 'success',
                        'message': 'Audio ready for streaming',
                        'token': stream_token,
                        'transcript': cache_data.get('transcript', ''),
                        'cache_status': 'HIT',
                        'expires_in': TOKEN_EXPIRY_SECONDS
                    }), 200
                else:
                    # File was deleted, remove from cache
                    logger.warning(f"Cached file missing for conversation {conversation_id}, regenerating...")
                    del file_cache[conversation_id]
        
        # File not in cache or cache miss - process the conversation
        logger.info(f"Processing redaction request for conversation: {conversation_id}")
        result = redactor.process_conversation(conversation_id, attributes)
        
        if 'error' in result:
            return jsonify(result), 400

        wav_file = result['redacted_audio_file']
        transcript = result.get('conversation_text', '')
        
        # Convert WAV to MP3 (for now, we'll keep as WAV but can add conversion later)
        # For production, you'd want to use pydub or ffmpeg to convert to MP3
        # For now, we'll serve the WAV file as-is
        mp3_file = wav_file  # TODO: Add WAV to MP3 conversion if needed
        
        # Store in cache
        with cache_lock:
            file_cache[conversation_id] = {
                'path': mp3_file,
                'timestamp': time.time(),
                'transcript': transcript
            }
        
        # Schedule automatic cleanup after 2 hours
        schedule_cleanup(conversation_id)
        
        logger.info(f"Cached redacted file for conversation {conversation_id}")
        
        # Generate a new streaming token
        stream_token = generate_stream_token(conversation_id, client_ip)
        
        # Return JSON response with token instead of file
        return jsonify({
            'status': 'success',
            'message': 'Audio processed and ready for streaming',
            'token': stream_token,
            'transcript': transcript,
            'cache_status': 'MISS',
            'expires_in': TOKEN_EXPIRY_SECONDS
        }), 200

    except Exception as e:
        logger.error(f"API error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/redact-conversation-stream/<conversation_id>', methods=['GET'])
def stream_redacted_audio(conversation_id):
    """
    Stream cached redacted audio file with Range support and token validation.
    Requires a valid, non-expired token to prevent unauthorized downloads.
    """
    try:
        # Get token from query parameter
        token = request.args.get('token')
        if not token:
            logger.warning(f"Stream request without token for conversation {conversation_id}")
            return jsonify({'error': 'Unauthorized: Token required'}), 401
        
        # Get client IP
        client_ip = request.remote_addr or 'unknown'
        
        # Validate token
        if not validate_stream_token(token, conversation_id, client_ip):
            logger.warning(f"Invalid or expired token for conversation {conversation_id} from {client_ip}")
            return jsonify({'error': 'Unauthorized: Invalid or expired token'}), 401
        
        # Clean up expired cache first
        cleanup_expired_cache()
        
        # Check if file exists in cache
        with cache_lock:
            if conversation_id not in file_cache:
                return jsonify({'error': 'Audio not found or expired. Please process the conversation again.'}), 404
            
            cache_data = file_cache[conversation_id]
            cached_file = cache_data['path']
            
            # Verify file still exists on disk
            if not os.path.exists(cached_file):
                logger.warning(f"Cached file missing for conversation {conversation_id}")
                del file_cache[conversation_id]
                return jsonify({'error': 'Audio file not found on disk'}), 404
        
        logger.info(f"Streaming audio for conversation: {conversation_id} (IP: {client_ip})")
        
        # Stream the file with Range support
        # This allows the browser to only download the parts it needs
        response = send_file_with_range(cached_file, mimetype='audio/mpeg')
        response.headers['Access-Control-Expose-Headers'] = 'Accept-Ranges, Content-Range, Content-Length'
        
        # Anti-download headers
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Remove Content-Disposition to prevent "Save As" dialog
        if 'Content-Disposition' in response.headers:
            del response.headers['Content-Disposition']
        
        return response
        
    except Exception as e:
        logger.error(f"Error streaming audio: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        status = 'not_initialized'
        if redactor:
            token = redactor.auth.get_access_token()
            status = "authenticated" if token else "authentication_failed"
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'auth_status': status
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    try:
        init_redactor()
        logger.info("Starting Genesys Cloud Audio Redaction API (WAV-only, no ffmpeg)")
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Failed to initialize: {e}")
        logger.info("Server will start but authentication may fail until credentials are set")

    app.run(debug=True, host='0.0.0.0', port=5001)
