#!/bin/bash
cd "Real project"
source venv/bin/activate

# Generate SSL certificates if they don't exist
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo "Generating SSL certificates..."
    bash generate_ssl_cert.sh
fi

nohup python fastapi_app.py > fastapi.log 2>&1 &
echo "FastAPI avviato in background! (log: fastapi.log)"
echo "Server running on HTTPS: https://localhost:8443"
