#!/bin/bash
gunicorn --workers=${WORKERS:-1} --threads ${THREADS:-1} --timeout 60 --bind :${PORT:-5050} --worker-class uvicorn.workers.UvicornWorker app.server:app