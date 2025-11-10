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
    "orderBy": "conversationStart"
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

