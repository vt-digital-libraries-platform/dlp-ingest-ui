#!/bin/bash
. /root/.bashrc
cd /home/ubuntu/dlp-ingest-ui/src

GUI=true /home/ubuntu/dlp-ingest-ui/venv/bin/python -m gunicorn --bind :8000 --workers=1 --threads=15 application