import datetime
import os
import sys
import time
import PureCloudPlatformClientV2
from PureCloudPlatformClientV2 import PureCloudRegionHosts
from PureCloudPlatformClientV2.rest import ApiException

# these imports are for EST time zone
# from datetime import datetime
# from pytz import timezone
# these imports are for utc

from datetime import datetime,timezone

print('-------------------------------------------------------------')
print('- Execute Bulk Action on recordings-')
print('-------------------------------------------------------------')

# Credentials
CLIENT_ID = ""
CLIENT_SECRET = ""
ORG_REGION = os.getenv ("GENESYS_CLOUD_REGION") # eg. us_east_1

# Set environment
# region = PureCloudPlatformClientV2.PureCloudRegionHosts[ORG_REGION]
region=PureCloudRegionHosts['us_east_1']
PureCloudPlatformClientV2.configuration.host = region.get_api_host()
print(CLIENT_ID,CLIENT_SECRET, type(CLIENT_ID))
# OAuth when using Client Credentials
api_client = PureCloudPlatformClientV2.api_client.ApiClient() \
            .get_client_credentials_token(CLIENT_ID, CLIENT_SECRET)


# Get the api
recording_api = PureCloudPlatformClientV2.RecordingApi(api_client)

# Build the create job query, for export action, set query.action = "EXPORT"
# For delete action, set query.action = "DELETE"
# For archive action, set query.action = "ARCHIVE"
# this is for utc
current_time=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
# this is for EST
# eastern=timezone('US/Eastren')
current_time=datetime.now(eastern).strftime("%Y-%m-%dT%H:%M:%S.000Z")

query = PureCloudPlatformClientV2.RecordingJobsQuery()
query.action = "ARCHIVE"

# query.action_date = "2029-01-01T00:00:00.000Z"

query.action_date = current_time

# Comment out integration id if using DELETE or ARCHIVE

# query.integration_id = ""

query.conversation_query = {
    "interval": "2020-12-01T05:30:00.000Z/2020-12-02T05:30:00.000Z",
    "order": "asc",
    "orderBy": "conversationStart",
    "conversationFilters": [
        {
            "type": "and",
            "clauses": [
                {
                    "type": "and",
                    "predicates": [
                        {"dimension": "mediaType", "value": "voice"},
                        {"dimension": "direction", "value": "outbound"}
                    ]
                }
            ]
        }
    ]
}

print(query)
try:
    # Call create_recording_job api
    create_job_response = recording_api.post_recording_jobs(query)
    job_id = create_job_response.id
    print(f"Successfully created recording bulk job { create_job_response}")
    print(job_id)
except ApiException as e:
    print(f"Exception when calling RecordingApi->post_recording_jobs: { e }")
    sys.exit()

# Call get_recording_job api
while True:
    try:
        get_recording_job_response = recording_api.get_recording_job(job_id)
        job_state = get_recording_job_response.state
        if job_state != 'PENDING':
            break
        else:
            print("Job state PENDING...")
            time.sleep(2)
    except ApiException as e:
        print(f"Exception when calling RecordingApi->get_recording_job: { e }")
        sys.exit()


if job_state == 'READY':
    try:
        execute_job_response = recording_api.put_recording_job(job_id, {"state": "PROCESSING"})
        job_state = execute_job_response.state
        print(f"Successfully execute recording bulk job { execute_job_response}")
    except ApiException as e:
        print(f"Exception when calling RecordingApi->put_recording_job: { e }")
        sys.exit()
else:
    print(f"Expected Job State is: READY, however actual Job State is: { job_state }")


# Call delete_recording_job api
# Can be canceled also in READY and PENDING states
# if job_state == 'PROCESSING':
#   try:
#        cancel_job_response = recording_api.delete_recording_job(job_id)
#        print(f"Successfully cancelled recording bulk job { cancel_job_response}")
#    except ApiException as e:
#        print(f"Exception when calling RecordingApi->delete_recording_job: { e }")
#        sys.exit()
#  try:
#    get_recording_jobs_response = recording_api.get_recording_jobs(
#        page_size=25,
#        page_number=1,
#        sort_by="userId",  # or "dateCreated"
#        state="CANCELLED",  # valid values FULFILLED, PENDING, READY, PROCESSING, CANCELLED, FAILED
#        show_only_my_jobs=True,
#        job_type="EXPORT",  # or "DELETE"
#    )
#    print(f"Successfully get recording bulk jobs { get_recording_jobs_response}")
#   except ApiException as e:
#    print(f"Exception when calling RecordingApi->get_recording_jobs: { e }")
#    sys.exit()

        while job_state == "PROCESSING":
            get_recording_job_response = recording_api.get_recording_job(job_id)
            job_state =  get_recording_job_response.state
            if job_state == 'PROCESSING':
                print("Job state PROCESSING...")
                time.sleep(10)
            else:
                print("Job state Complete...")
                break
        print("Job state ",job_state)
        print(f"Successfully execute recording bulk job { get_recording_job_response}")

We developed a secure, web-based application leveraging React and Node.js that transforms how organizations access and manage conversation recordings. The platform enables users to search for specific recordings, then instantly stream or download a redacted version, ensuring compliance and privacy. Access control is fully automated, dynamically assigning permissions based on user credentials to maintain robust security.
This solution addresses a critical industry challenge: traditional processes for retrieving and redacting recordings often take 7–8 business days and require significant manual effort. By automating search, redaction, and delivery, our application reduces turnaround time to mere minutes, dramatically improving operational efficiency and customer responsiveness.
The innovation lies in:

Real-time delivery of compliant recordings without manual intervention.
Role-based security automation, eliminating human error in access control.
Scalable architecture for enterprise environments, supporting high-volume requests.

This approach not only accelerates compliance workflows but also sets a new benchmark for speed, security, and user experience in contact center and regulated industries.

                                                                                     failed_recordings_api = get_recording_job_response.failed_recordings
        failed_recordings_api = 'https://api.mypurecloud.com' + failed_recordings_api
        # failed_recordings_api = 'https://api.usw2.pure.cloud' + failed_recordings_api
       
        archive_date = (datetime.now(timezone.utc) - timedelta(hours=4, minutes=30)) \
            .strftime("%Y-%m-%dT%H:%M:%S.000Z")
        print(archive_date)
        base_host = PureCloudPlatformClientV2.configuration.host
        failed_recordings_url = urljoin(base_host, failed_recordings_api)
        print(failed_recordings_url)

        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {api_client.access_token}",
            "Accept": "application/json"
        })


        page_size = 100
        cursor = None  

        total_seen = 0
        total_archived = 0
        errors = []

        while True:
            params = {
                "includeTotal": "false", 
                "pageSize": str(page_size)
            }
            if cursor:
                params["cursor"] = cursor

            resp = session.get(failed_recordings_url, params=params, timeout=30)
            try:
                resp.raise_for_status()
            except requests.HTTPError as http_err:
                print(f"[ERROR] GET failed recordings: {http_err} — URL={resp.url}")
                break

            data = resp.json() if resp.content else {}
            entities = data.get("entities", [])

            if not entities and not data.get("cursor"):
                break

            for entity in entities:
                total_seen += 1
                conversation_id = entity.get("conversationId")
                recording_id = entity.get("recordingId")

                if not conversation_id or not recording_id:
                    errors.append({"entity": entity, "error": "Missing conversationId or recordingId"})
                    continue        
                body = PureCloudPlatformClientV2.Recording()
                body.file_state = "ARCHIVE"  
                body.archive_date = archive_date 
                try:
                    api_response = recording_api.put_conversation_recording(
                        conversation_id,
                        recording_id,
                        body

                    )
                    total_archived += 1
                    if total_archived % 50 == 0:
                        print(
                            f"Archived {total_archived} / {total_seen} (last conv={conversation_id}, rec={recording_id})")
                except ApiException as e:
                    errors.append({
                        "conversationId": conversation_id,
                        "recordingId": recording_id,
                        "error": str(e)
                    })
            cursor = data.get("cursor")
            if not cursor:
                break

        # ---- Summary ----
        print("-------------------------------------------------------------")
        print(f"Archive date used for ALL records: {archive_date}")
        print(f"Failed recordings processed: {total_seen}")
        print(f"Successfully archived:        {total_archived}")
        print(f"Errors:                       {len(errors)}")
os.environ['REQUESTS_CA_BUNDLE'] = ""
                                                                                     
