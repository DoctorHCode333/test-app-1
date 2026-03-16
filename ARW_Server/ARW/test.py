import traceback

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import re
import tempfile
from datetime import datetime
import logging
from typing import List, Dict, Tuple, Optional
import json
from dataclasses import dataclass
from pydub import AudioSegment
import io
import PureCloudPlatformClientV2 as pc2
from PureCloudPlatformClientV2.rest import ApiException
import time
import pprint

import os

AudioSegment.converter = r"C:\Harsh_official\ffmpeg-8.0-full_build\ffmpeg-8.0-full_build\bin\ffmpeg.exe"

os.environ['REQUESTS_CA_BUNDLE'] = "C:\Harsh_official\Zscaler Root CA.crt"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, sent_wildcard=True, vary_header=True)

@dataclass
class RedactionSegment:
    start_time: float
    end_time: float
    phrase: str
    reason: str

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
            print("Host:", self.api_client.access_token)

        except ApiException as ex:
                logger.error(f"SDK error getting recordings: {ex}")




class GenesysAudioRedactor:
    def __init__(self, client_id: str, client_secret: str, environment: str):
        # Keep signature for compatibility; environment not needed with SDK region enum
        self.auth = GenesysCloudAuth(client_id, client_secret)

        # Initialize SDK API clients
        self.recording_api = pc2.RecordingApi(self.auth.api_client)
        self.conversations_api = pc2.ConversationsApi(self.auth.api_client)
        self.sta_api = pc2.SpeechTextAnalyticsApi(self.auth.api_client)

    # ---------- SDK REPLACEMENTS START ----------

    def get_conversation_recording(self, conversation_id: str) -> Optional[Dict]:
        """
        Use RecordingApi to get recordings entities for a conversation.
        This endpoint can return empty initially while processing; we retry briefly.
        """
        try:
            max_attempts = 5
            wait_seconds = 2

            for attempt in range(1, max_attempts + 1):
                recs = self.recording_api.get_conversation_recordings(conversation_id,locale="en-US")
                # print(recs)
                # recs is list[Recording]; empty list typically means still processing
                if recs:
                    # Take first recording
                    rec = recs[0]
                    print(rec.id)
                    # media_uris is a dict-like (e.g., {"0": RecordingMediaUri(media_uri="...")})
                    media_uri = None
                    try:
                        # Some SDK versions expose as dict; be defensive
                        if hasattr(rec, "media_uris") and rec.media_uris:
                            # Get the first entry
                            first_key = list(rec.media_uris.keys())[0]
                            media_uri = rec.media_uris[first_key].media_uri
                    except Exception:
                        media_uri = None

                    return {
                        'recording_id': rec.id,
                        'conversation_id': conversation_id,
                        'media_uri': media_uri,
                        # Old path returned transcript_uris; we now fetch via STA API
                        'transcript_uris': []
                    }

                if attempt < max_attempts:
                    logger.info("Recording not ready yet (attempt %d/%d). Retrying in %ss...",
                                attempt, max_attempts, wait_seconds)
                    time.sleep(wait_seconds)

            logger.warning(f"No recordings found for conversation {conversation_id} after retries")
            return None

        except ApiException as e:
            logger.error(f"SDK error getting recordings: {e}")
            traceback.print_exc()
            return None

    def _find_voice_communication_id(self, conversation_dict: Dict) -> Optional[str]:
        """
        Find the 'communicationId' for the customer's voice leg.
        Community guidance: look under the participant with purpose 'customer',
        then in the 'calls' array. [4](https://community.genesys.com/discussion/access-to-call-transcripts-using-the-developer-api)
        """
        try:
            for p in conversation_dict.get("participants", []):
                if str(p.get("purpose", "")).lower() == "customer" or str(p.get("purpose", "")).lower() == "external":
                    # Look for calls array under this participant
                    calls = p.get("calls", [])
                    for c in calls:
                        # Prefer 'id' as the communicationId
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

    def get_transcript_data(self, conversation_id: str, recording_id: str) -> Optional[Dict]:
        """
        Use Speech & Text Analytics to get a pre-signed transcript URL,
        then download the transcript JSON.
        - GET via SDK: /speechandtextanalytics/conversations/{conversationId}/communications/{communicationId}/transcripturls
        - Then requests.get() to the pre-signed URL to obtain JSON transcript.
        Docs & community confirm this is how to export transcripts. [5](https://help.mypurecloud.com/faqs/can-i-download-a-voice-transcript/)[4](https://community.genesys.com/discussion/access-to-call-transcripts-using-the-developer-api)
        """
        try:
            # Need the communicationId for the voice leg
            convo_obj = self.conversations_api.get_conversation(conversation_id)
            convo_dict = convo_obj.to_dict() if hasattr(convo_obj, "to_dict") else convo_obj
            communication_id = self._find_voice_communication_id(convo_dict)

            if not communication_id:
                logger.warning("Could not determine communicationId for conversation %s", conversation_id)
                return None

            # Try the plural form first (transcripturls), then fallback to singular (transcripturl)
            try:
                urls_resp = self.sta_api.get_speechandtextanalytics_conversation_communication_transcripturls(
                    conversation_id, communication_id
                )

                urls_dict = urls_resp.to_dict() if hasattr(urls_resp, "to_dict") else urls_resp
                # Typical payload contains list of { 'transcriptFileUrl': 'https://...' }
                transcript_urls = urls_dict.get("transcript_urls") or urls_dict.get("urls") or []
                if not transcript_urls and "transcript_file_url" in urls_dict:
                    transcript_urls = [ {"transcriptFileUrl": urls_dict["transcript_file_url"]} ]
            except pc2.rest.ApiException:
                # Older/alt method name
                url_resp = self.sta_api.get_speechandtextanalytics_conversation_communication_transcripturl(
                    conversation_id, communication_id
                )
                url_dict = url_resp.to_dict() if hasattr(url_resp, "to_dict") else url_resp
                transcript_urls = [ {"transcriptFileUrl": url_dict.get("transcript_file_url")} ]

            # Pick the first valid URL
            presigned_url = None
            for u in transcript_urls:
                presigned_url = u.get("transcriptFileUrl") or u.get("url")
                if presigned_url:
                    break

            if not presigned_url:
                logger.warning("No transcript URL returned for conversation %s", conversation_id)
                return None

            # Download transcript JSON from the pre-signed URL (not a Genesys API call)
            r = requests.get(presigned_url, timeout=30)
            r.raise_for_status()
            return r.json()

        except pc2.rest.ApiException as e:
            logger.error(f"SDK error fetching transcript URL(s): {e}")
            return None
        except requests.RequestException as e:
            logger.error(f"Error downloading transcript JSON: {e}")
            traceback.print_exc()
            return None

    def get_conversation_details(self, conversation_id: str) -> Optional[Dict]:
        """Use ConversationsApi to fetch conversation details (as dict)."""
        try:
            convo = self.conversations_api.get_conversation(conversation_id)
            return convo.to_dict() if hasattr(convo, "to_dict") else convo
        except pc2.rest.ApiException as e:
            logger.error(f"SDK error getting conversation details: {e}")
            traceback.print_exc()
            return None

    # ---------- SDK REPLACEMENTS END ----------

    def extract_participant_data(self, conversation_details: Dict) -> Dict[str, any]:

        participant_info = {}

        # if 'name' in conversation_details:
        #     participant_info['name'] = conversation_details['FNAME']
        # if 'ANI' in conversation_details:
        #     participant_info['ani'] = conversation_details['ANI']
        # if 'dnis' in conversation_details:
        #     participant_info['dnis'] = conversation_details['dnis']
        # if 'address' in conversation_details:
        #     participant_info['address'] = conversation_details['Address']

        return participant_info

    def detect_pii_patterns(self, text: str) -> List[Dict]:

        patterns = {
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b(?:\d{4}[\s-]?){3}\d{4}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'date_of_birth': r'\b(?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12]\d|3[01])[-/](?:19|20)\d{2}\b',
            'zip_code': r'\b\d{5}(?:-\d{4})?\b',
            'account_number': r'\b(?:account|acct)[\s#:]*(\d{6,})\b',
            'routing_number': r'\b\d{9}\b',
            'license_plate': r'\b[A-Z0-9]{2,3}[-\s]?[A-Z0-9]{3,4}\b',
            'medicare_id': r'\b\d{3}-\d{2}-\d{4}[A-Z]\b'
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

    def find_participant_data_in_transcript(self, transcript_data: Dict, participants: Dict) -> List[RedactionSegment]:
        redaction_segments = []
        if 'transcript' not in transcript_data or 'phrases' not in transcript_data['transcript']:
            return redaction_segments

        for phrase in transcript_data['transcript']['phrases']:
            phrase_text = phrase.get('text', '').lower()
            start_time = phrase.get('startTimeMs', 0) / 1000.0
            duration = phrase.get('durationMs', 0) / 1000.0
            end_time = start_time + duration

            for participant_id, participant_info in participants.items():
                for field, value in participant_info.items():
                    if value and len(str(value)) > 2 and str(value).lower() in phrase_text:
                        redaction_segments.append(RedactionSegment(
                            start_time=start_time,
                            end_time=end_time,
                            phrase=phrase_text,
                            reason=f"Participant {field}: {value}"
                        ))
                        break
        return redaction_segments

    def find_pii_in_transcript(self, transcript_data: Dict) -> List[RedactionSegment]:
        redaction_segments = []
        if 'transcript' not in transcript_data or 'phrases' not in transcript_data['transcript']:
            return redaction_segments

        for phrase in transcript_data['transcript']['phrases']:
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
        return redaction_segments

    def merge_overlapping_segments(self, segments: List[RedactionSegment]) -> List[RedactionSegment]:
        if not segments:
            return segments
        segments.sort(key=lambda x: x.start_time)
        merged = [segments[0]]
        for current in segments[1:]:
            last = merged[-1]
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

    def download_audio_file(self, media_uri: str) -> bytes:
        """
        Download audio from the pre-signed media URI returned by RecordingApi.
        This is not a Genesys API call.
        """
        try:
            response = requests.get(media_uri, stream=True, timeout=60)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            traceback.print_exc()
            raise

    def redact_audio_with_pydub(self, audio_data: bytes, segments: List[RedactionSegment]) -> bytes:
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            if not segments:
                output_buffer = io.BytesIO()
                audio.export(output_buffer, format="mp3", bitrate="128k")
                return output_buffer.getvalue()

            redacted_audio = audio
            for segment in sorted(segments, key=lambda x: x.start_time, reverse=True):
                start_ms = int(segment.start_time * 1000)
                end_ms = int(segment.end_time * 1000)
                start_ms = max(0, min(start_ms, len(redacted_audio)))
                end_ms = max(start_ms, min(end_ms, len(redacted_audio)))
                if start_ms < end_ms:
                    silence = AudioSegment.silent(duration=end_ms - start_ms)
                    redacted_audio = redacted_audio[:start_ms] + silence + redacted_audio[end_ms:]

            output_buffer = io.BytesIO()
            redacted_audio.export(output_buffer, format="mp3", bitrate="128k")
            return output_buffer.getvalue()

        except Exception as e:
            logger.error(f"Error redacting audio: {e}")
            traceback.print_exc()
            raise

    def process_conversation(self, conversation_id: str, attributes) -> Dict:
        try:
            # Step 1: Get recording information (SDK)
            recording_info = self.get_conversation_recording(conversation_id)
            if not recording_info:
                return {'error': 'No recording found for conversation'}

            # Step 2: Get conversation details for participant data (SDK)
            # conversation_details = self.get_conversation_details(conversation_id)

            participants = self.extract_participant_data(attributes) if attributes else {}

            # Step 3: Get transcript data (SDK -> pre-signed download)
            transcript_data = self.get_transcript_data(conversation_id, recording_info['recording_id'])
            if not transcript_data:
                return {'error': 'Failed to fetch transcript data'}

            # Step 4: Find redaction segments
            participant_segments = self.find_participant_data_in_transcript(transcript_data, participants)
            pii_segments = self.find_pii_in_transcript(transcript_data)
            merged_segments = self.merge_overlapping_segments(participant_segments + pii_segments)
            logger.info(f"Found {len(merged_segments)} segments to redact")

            # Step 5: Download and redact audio
            if not recording_info.get('media_uri'):
                return {'error': 'No media URI available for this recording'}
            # audio_data = self.download_audio_file(recording_info['media_uri'])en-US
            redacted_audio_data = self.download_audio_file(recording_info['media_uri'])
            # redacted_audio_data = self.redact_audio_with_pydub(audio_data, merged_segments)

            # Save to temporary file
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_file.write(redacted_audio_data)
            output_file.close()

            return {
                'success': True,
                'redacted_audio_file': output_file.name,
                'segments_redacted': len(merged_segments),
                'redaction_details': [
                    {
                        'start_time': seg.start_time,
                        'end_time': seg.end_time,
                        'duration': seg.end_time - seg.start_time,
                        'reason': seg.reason
                    } for seg in merged_segments
                ]
            }

        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            traceback.print_exc()
            return {'error': str(e)}

# Global redactor instance
redactor = None

def init_redactor():
    global redactor
    # These are hard-coded in your sample; consider ENV variables for prod
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
        conversation_id = data['conversationId']
        attributes = data['attributes']
        if not conversation_id:
            return jsonify({'error': 'conversation_id is required'}), 400

        logger.info(f"Processing redaction request for conversation: {conversation_id}")
        result = redactor.process_conversation(conversation_id,attributes)
        if 'error' in result:
            return jsonify(result), 400

        response = send_file(
            result['redacted_audio_file'],
            as_attachment=True,
            download_name=f'redacted_{conversation_id}.mp3',
            mimetype='audio/mpeg'
        )
        response.headers['X-Segments-Redacted'] = str(result['segments_redacted'])
        response.headers['X-Redaction-Details'] = json.dumps(result['redaction_details'])

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
        if redactor:
            token = redactor.auth.get_access_token()
            auth_status = "authenticated" if token else "authentication_failed"
        else:
            auth_status = "not_initialized"
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'auth_status': auth_status
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
        logger.info("Starting Genesys Cloud Audio Redaction API")
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Failed to initialize: {e}")
        logger.info("Server will start but authentication may fail until environment variables are set")

    app.run(debug=True, host='0.0.0.0', port=5001)
