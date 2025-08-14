from flask import Flask, request, jsonify, send_file
import requests
import re
import os
import tempfile
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple, Optional
import json
from dataclasses import dataclass
from pydub import AudioSegment
from pydub.generators import Sine
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@dataclass
class RedactionSegment:
    start_time: float
    end_time: float
    phrase: str
    reason: str

class GenesysCloudAuth:
    def __init__(self, client_id: str, client_secret: str, environment: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.environment = environment
        self.base_url = f"https://api.{environment}"
        self.access_token = None
        self.token_expires_at = None
        
    def get_access_token(self) -> str:
        """Get or refresh access token using client credentials grant"""
        # Check if we have a valid token
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at - timedelta(minutes=5)):
            return self.access_token
            
        # Get new token
        token_url = f"{self.base_url}/oauth/token"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Prepare credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers['Authorization'] = f'Basic {encoded_credentials}'
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Successfully obtained access token")
            return self.access_token
            
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            raise Exception(f"Authentication failed: {e}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with valid access token"""
        token = self.get_access_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

class GenesysAudioRedactor:
    def __init__(self, client_id: str, client_secret: str, environment: str):
        self.auth = GenesysCloudAuth(client_id, client_secret, environment)
        self.base_url = f"https://api.{environment}"

    def get_conversation_recording(self, conversation_id: str) -> Optional[Dict]:
        """Get recording information for a conversation"""
        try:
            url = f"{self.base_url}/api/v2/conversations/{conversation_id}/recordings"
            headers = self.auth.get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('entities'):
                logger.warning(f"No recordings found for conversation {conversation_id}")
                return None
                
            # Get the first recording
            recording = data['entities'][0]
            return {
                'recording_id': recording['id'],
                'conversation_id': conversation_id,
                'media_uri': recording.get('mediaUri'),
                'transcript_uris': recording.get('transcriptUris', [])
            }
            
        except requests.RequestException as e:
            logger.error(f"Error getting recording: {e}")
            return None

    def get_transcript_data(self, conversation_id: str, recording_id: str) -> Optional[Dict]:
        """Get transcript data from Genesys Cloud API"""
        try:
            # First get transcript URI
            url = f"{self.base_url}/api/v2/conversations/{conversation_id}/recordings/{recording_id}/transcripts"
            headers = self.auth.get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            transcript_data = response.json()
            
            # If we have transcripts, get the detailed data
            if transcript_data.get('transcripts'):
                # Get the first transcript
                transcript_id = transcript_data['transcripts'][0]['id']
                detail_url = f"{self.base_url}/api/v2/conversations/{conversation_id}/recordings/{recording_id}/transcripts/{transcript_id}"
                
                detail_response = requests.get(detail_url, headers=headers)
                detail_response.raise_for_status()
                
                return detail_response.json()
            
            return transcript_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching transcript: {e}")
            return None

    def get_conversation_details(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation details including participants"""
        try:
            url = f"{self.base_url}/api/v2/conversations/{conversation_id}"
            headers = self.auth.get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error getting conversation details: {e}")
            return None

    def extract_participant_data(self, conversation_details: Dict) -> Dict[str, any]:
        """Extract participant information from conversation details"""
        participants = {}
        
        if 'participants' in conversation_details:
            for participant in conversation_details['participants']:
                participant_id = participant.get('id', '')
                
                # Extract various participant data fields
                participant_info = {}
                
                # Basic info
                if 'name' in participant:
                    participant_info['name'] = participant['name']
                if 'ani' in participant:
                    participant_info['ani'] = participant['ani']
                if 'dnis' in participant:
                    participant_info['dnis'] = participant['dnis']
                
                # User info
                if 'user' in participant:
                    user = participant['user']
                    participant_info.update({
                        'user_name': user.get('name', ''),
                        'user_email': user.get('email', ''),
                        'user_id': user.get('id', '')
                    })
                
                # External contact info
                if 'externalContact' in participant:
                    contact = participant['externalContact']
                    participant_info.update({
                        'contact_name': contact.get('name', ''),
                        'first_name': contact.get('firstName', ''),
                        'last_name': contact.get('lastName', ''),
                        'contact_email': contact.get('workEmail', ''),
                        'phone_number': contact.get('workPhone', '')
                    })
                
                # Address info if available
                if 'address' in participant:
                    address = participant['address']
                    participant_info.update({
                        'address': address.get('address', ''),
                        'display_name': address.get('displayName', '')
                    })
                
                participants[participant_id] = participant_info
        
        return participants

    def detect_pii_patterns(self, text: str) -> List[Dict]:
        """Detect common PII patterns in text using regex"""
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
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detected_pii.append({
                    'type': pii_type,
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return detected_pii

    def find_participant_data_in_transcript(self, transcript_data: Dict, participants: Dict) -> List[RedactionSegment]:
        """Find participant data mentions in transcript phrases"""
        redaction_segments = []
        
        if 'transcript' not in transcript_data or 'phrases' not in transcript_data['transcript']:
            return redaction_segments
            
        for phrase in transcript_data['transcript']['phrases']:
            phrase_text = phrase.get('text', '').lower()
            start_time = phrase.get('startTimeMs', 0) / 1000.0
            duration = phrase.get('durationMs', 0) / 1000.0
            end_time = start_time + duration
            
            # Check against participant data
            for participant_id, participant_info in participants.items():
                for field, value in participant_info.items():
                    if value and len(str(value)) > 2:  # Only check meaningful values
                        if str(value).lower() in phrase_text:
                            redaction_segments.append(RedactionSegment(
                                start_time=start_time,
                                end_time=end_time,
                                phrase=phrase_text,
                                reason=f"Participant {field}: {value}"
                            ))
                            break  # Only add once per phrase
        
        return redaction_segments

    def find_pii_in_transcript(self, transcript_data: Dict) -> List[RedactionSegment]:
        """Find PII data in transcript phrases"""
        redaction_segments = []
        
        if 'transcript' not in transcript_data or 'phrases' not in transcript_data['transcript']:
            return redaction_segments
            
        for phrase in transcript_data['transcript']['phrases']:
            phrase_text = phrase.get('text', '')
            start_time = phrase.get('startTimeMs', 0) / 1000.0
            duration = phrase.get('durationMs', 0) / 1000.0
            end_time = start_time + duration
            
            # Detect PII patterns in this phrase
            pii_matches = self.detect_pii_patterns(phrase_text)
            
            if pii_matches:
                redaction_segments.append(RedactionSegment(
                    start_time=start_time,
                    end_time=end_time,
                    phrase=phrase_text,
                    reason=f"PII detected: {', '.join([match['type'] for match in pii_matches])}"
                ))
        
        return redaction_segments

    def merge_overlapping_segments(self, segments: List[RedactionSegment]) -> List[RedactionSegment]:
        """Merge overlapping or adjacent redaction segments"""
        if not segments:
            return segments
            
        # Sort segments by start time
        segments.sort(key=lambda x: x.start_time)
        
        merged = [segments[0]]
        
        for current in segments[1:]:
            last = merged[-1]
            
            # If segments overlap or are very close (within 0.5 seconds), merge them
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
        """Download audio file from Genesys Cloud"""
        try:
            headers = self.auth.get_headers()
            response = requests.get(media_uri, headers=headers, stream=True)
            response.raise_for_status()
            
            audio_data = b''
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    audio_data += chunk
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            raise

    def redact_audio_with_pydub(self, audio_data: bytes, segments: List[RedactionSegment]) -> bytes:
        """Redact audio using pydub by replacing segments with silence"""
        try:
            # Load audio from bytes
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            
            if not segments:
                # No redaction needed, return original
                output_buffer = io.BytesIO()
                audio.export(output_buffer, format="mp3", bitrate="128k")
                return output_buffer.getvalue()
            
            # Create a copy to work with
            redacted_audio = audio
            
            # Sort segments by start time (reverse order for proper indexing)
            segments_sorted = sorted(segments, key=lambda x: x.start_time, reverse=True)
            
            for segment in segments_sorted:
                start_ms = int(segment.start_time * 1000)
                end_ms = int(segment.end_time * 1000)
                
                # Ensure we don't go beyond audio length
                start_ms = max(0, min(start_ms, len(redacted_audio)))
                end_ms = max(start_ms, min(end_ms, len(redacted_audio)))
                
                if start_ms < end_ms:
                    # Create silence for this segment
                    silence_duration = end_ms - start_ms
                    silence = AudioSegment.silent(duration=silence_duration)
                    
                    # Replace the segment with silence
                    redacted_audio = (
                        redacted_audio[:start_ms] + 
                        silence + 
                        redacted_audio[end_ms:]
                    )
            
            # Export to MP3
            output_buffer = io.BytesIO()
            redacted_audio.export(output_buffer, format="mp3", bitrate="128k")
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error redacting audio: {e}")
            raise

    def process_conversation(self, conversation_id: str) -> Dict:
        """Main processing function"""
        try:
            # Step 1: Get recording information
            recording_info = self.get_conversation_recording(conversation_id)
            if not recording_info:
                return {'error': 'No recording found for conversation'}
            
            # Step 2: Get conversation details for participant data
            conversation_details = self.get_conversation_details(conversation_id)
            participants = {}
            if conversation_details:
                participants = self.extract_participant_data(conversation_details)
            
            # Step 3: Get transcript data
            transcript_data = self.get_transcript_data(conversation_id, recording_info['recording_id'])
            if not transcript_data:
                return {'error': 'Failed to fetch transcript data'}
            
            # Step 4: Find redaction segments
            participant_segments = self.find_participant_data_in_transcript(transcript_data, participants)
            pii_segments = self.find_pii_in_transcript(transcript_data)
            
            # Combine and merge segments
            all_segments = participant_segments + pii_segments
            merged_segments = self.merge_overlapping_segments(all_segments)
            
            logger.info(f"Found {len(merged_segments)} segments to redact")
            
            # Step 5: Download and redact audio
            if not recording_info.get('media_uri'):
                return {'error': 'No media URI available for this recording'}
            
            audio_data = self.download_audio_file(recording_info['media_uri'])
            redacted_audio_data = self.redact_audio_with_pydub(audio_data, merged_segments)
            
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
                    }
                    for seg in merged_segments
                ]
            }
            
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            return {'error': str(e)}

# Global redactor instance
redactor = None

def init_redactor():
    global redactor
    # Get credentials from environment variables
    CLIENT_ID = os.getenv('GENESYS_CLIENT_ID')
    CLIENT_SECRET = os.getenv('GENESYS_CLIENT_SECRET')
    ENVIRONMENT = os.getenv('GENESYS_ENVIRONMENT', 'mypurecloud.com')
    
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("GENESYS_CLIENT_ID and GENESYS_CLIENT_SECRET environment variables are required")
    
    redactor = GenesysAudioRedactor(CLIENT_ID, CLIENT_SECRET, ENVIRONMENT)
    logger.info("Genesys Cloud redactor initialized successfully")

@app.route('/redact-conversation', methods=['POST'])
def redact_conversation():
    """API endpoint to redact conversation audio and return the redacted file"""
    try:
        # Initialize redactor if not done
        if redactor is None:
            init_redactor()
        
        # Get conversation ID from request
        data = request.get_json()
        if not data or 'conversation_id' not in data:
            return jsonify({'error': 'conversation_id is required'}), 400
        
        conversation_id = data['conversation_id']
        logger.info(f"Processing redaction request for conversation: {conversation_id}")
        
        # Process the conversation
        result = redactor.process_conversation(conversation_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Return the redacted audio file with metadata in headers
        response = send_file(
            result['redacted_audio_file'],
            as_attachment=True,
            download_name=f'redacted_{conversation_id}.mp3',
            mimetype='audio/mpeg'
        )
        
        # Add custom headers with redaction info
        response.headers['X-Segments-Redacted'] = str(result['segments_redacted'])
        response.headers['X-Redaction-Details'] = json.dumps(result['redaction_details'])
        
        # Schedule cleanup of temp file
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
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test authentication if redactor is initialized
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
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Initialize the redactor on startup
    try:
        init_redactor()
        logger.info("Starting Genesys Cloud Audio Redaction API")
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        logger.info("Server will start but authentication may fail until environment variables are set")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
