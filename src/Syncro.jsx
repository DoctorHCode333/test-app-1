$ /GenApps/PYTHON_APPLICATIONS/WordCloudServer/wordCloudServerVenv/bin/gunicorn wordCloudServer:app \ --certfile=/GenApp
s/Certs/certificate \ --keyfile=/GenApps/Certs/certificate_key \ -w 4 \ -b 0.0.0.0:5000
[2025-07-24 11:37:14 -0400] [2741956] [INFO] Starting gunicorn 23.0.0
[2025-07-24 11:37:14 -0400] [2741956] [INFO] Listening at: http://127.0.0.1:8000 (2741956)
[2025-07-24 11:37:14 -0400] [2741956] [INFO] Using worker: sync
[2025-07-24 11:37:14 -0400] [2741957] [INFO] Booting worker with pid: 2741957
