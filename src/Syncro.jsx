/GenApps/PYTHON_APPLICATIONS/WordCloudServer/wordCloudServerVenv/bin/gunicorn wordCloudServer:app \
  --certfile=/GenApps/Certs/certificate \
  --keyfile=/GenApps/Certs/certificate_key \
  -w 4 \
  -b 0.0.0.0:5000
