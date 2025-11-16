#!/bin/bash
cd "Real project"
source venv/bin/activate
nohup python fastapi_app.py > fastapi.log 2>&1 &
echo "FastAPI avviato in background! (log: fastapi.log)"
