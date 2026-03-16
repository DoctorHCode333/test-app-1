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

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import wave
import PureCloudPlatformClientV2 as pc2
from PureCloudPlatformClientV2.rest import ApiException

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from datetime import datetime, timezone



# ---- Environment (keep your Zscaler cert if required) ----
os.environ['REQUESTS_CA_BUNDLE'] = "C:\Harsh_official\Docs\Zscaler Root CA.crt"

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
    def ms_to_seconds_relative(ms_value: int, base_ms: int) -> float:
        """
        Convert absolute millisecond timestamp to seconds relative to base_ms.
        """
        return (ms_value - base_ms) / 1000.0

    # --------------- Genesys SDK: Recordings / Transcripts ---------------

    def get_conversation_recording(self, conversation_id: str) -> Optional[Dict]:
        """
        Fetch recordings for a conversation; return a list of WAV media URIs
        (customer + agent). Retries briefly while recordings are processing.
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

                    for rec in recs:
                        rec_ids.append(getattr(rec, "id", None))
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
                        return {
                            "conversation_id": conversation_id,
                            "recording_ids": rec_ids,
                            "media_uris": unique_uris
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
        if 'ANI' in conversation_details:
            participant_info['ani'] = conversation_details['ANI']
        if 'DNIS' in conversation_details:
            participant_info['dnis'] = conversation_details['DNIS']
        if 'Address' in conversation_details:
            participant_info['address'] = conversation_details['Address']

        return participant_info

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
            'license_plate': r'\b[A-Z0-9]{2,3}[-\s]?[A-Z0-9]{3,4}\b',

            # Matches Medicare IDs like 123-45-6789A
            'medicare_id': r'\b\d{3}-\d{2}-\d{4}[A-Z]\b',

            # Matches any sequence of 4 or more digits, but NOT if the number starts or ends with a dollar sign ($)
            # Example: matches "1234", "56789", but NOT "$1234" or "1234$"
            'long_number': r'(?<!\$)\b\d{4,}\b(?!\$)'
        }

        detected_pii = []
        for pii_type, pattern in patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                detected_pii.append({
                    'type': pii_type,
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        return detected_pii

    def find_participant_data_in_transcript(self, transcript_data: Dict, participants_data: Dict) -> List[RedactionSegment]:
        redaction_segments = []

        # print(transcript_data['transcripts'])
        if 'transcripts' not in transcript_data or 'phrases' not in transcript_data['transcripts'][0]:
            print("Entered Here")
            return redaction_segments
            # Use first phrase as base reference
        base_ms = transcript_data['transcripts'][0].get('startTime', 0)
        for transcript in transcript_data['transcripts']:

            phrases = transcript.get('phrases', [])
            if not phrases:
                continue



            for phrase in phrases:
                start_ms = phrase.get('startTimeMs', 0)
                duration_ms = phrase['duration']['milliseconds']
                start_time = self.ms_to_seconds_relative(start_ms, base_ms)+4
                end_time = start_time + (duration_ms / 1000.0)
                phrase_text = phrase.get('text', '').lower()
                for field, value in participants_data.items():
                    if value and len(str(value)) > 2 and str(value).lower() in phrase_text:

                        self.conv_transcript = self.conv_transcript.replace(phrase_text,"[Redacted]")
                        redaction_segments.append(RedactionSegment(
                            start_time=start_time/60,
                            end_time=end_time/60,
                            phrase=phrase_text,
                            reason=f"Participant {field}: {value}"
                        ))
                        break
        return redaction_segments

    def find_pii_in_transcript(self, transcript_data: Dict) -> List[RedactionSegment]:
        redaction_segments = []
        if 'transcripts' not in transcript_data or 'phrases' not in transcript_data['transcripts']:
            return redaction_segments

        for phrase in transcript_data['transcripts']['phrases']:
            phrase_text = phrase.get('text', '')
            start_time = phrase.get('startTimeMs', 0) / 1000.0
            duration = phrase.get('durationMs', 0) / 1000.0
            end_time = start_time + duration

            pii_matches = self.detect_pii_patterns(phrase_text)
            if pii_matches:
                redaction_segments.append(RedactionSegment(
                    start_time=start_time,
                    end_time=end_time,
                    phrase=phrase_text,
                    reason=f"PII detected: {', '.join([m['type'] for m in pii_matches])}"
                ))
        print(redaction_segments)
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
                participant_segments = self.find_participant_data_in_transcript(transcript_data, participants_data)
                pii_segments = self.find_pii_in_transcript(transcript_data)
                redaction_segments = self.merge_overlapping_segments(participant_segments + pii_segments)
            print(redaction_segments)
            logger.info(f"Segments to redact: {len(redaction_segments)}")

            # Step 4: Overlay streams (WAV -> WAV, no ffmpeg)
            mixed_wav_bytes, sr = self._overlay_wav_uris(media_uris[:2])

            # Step 5: Apply redaction (silence) on mixed audio
            final_wav_bytes = self._redact_wav_by_silencing(mixed_wav_bytes, redaction_segments)

            # Step 6: Save to temp .wav and return path
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            output_file.write(final_wav_bytes)
            output_file.close()

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

        logger.info(f"Processing redaction request for conversation: {conversation_id}")
        result = redactor.process_conversation(conversation_id, attributes)
        if 'error' in result:
            return jsonify(result), 400

        response = send_file(
            result['redacted_audio_file'],
            as_attachment=True,
            download_name=f'redacted_{conversation_id}.wav',
            mimetype='audio/wav'
        )
        # response.headers['X-Segments-Redacted'] = str(result['segments_redacted'])
        # response.headers['X-Redaction-Details'] = json.dumps(result['redaction_details'])

        response.headers['x-transcript'] = result.get('conversation_text', '')

        response.headers['Access-Control-Expose-Headers'] = 'x-transcript'

        temp_file = result['redacted_audio_file']

        @response.call_on_close
        def cleanup_temp_file():
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logger.info(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")

        return response

    except Exception as e:
        logger.error(f"API error: {e}")
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
