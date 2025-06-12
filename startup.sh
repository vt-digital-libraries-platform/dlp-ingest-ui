#!/bin/bash
. /root/.bashrc
cd /home/ubuntu/dlp-ingest-ui/src
git clone https://github.com/vt-digital-libraries-platform/dlp-ingest
cd /home/ubuntu/dlp-ingest-ui/src/dlp-ingest
git checkout ui
cd /home/ubuntu/dlp-ingest-ui/src
mv dlp-ingest dlp_ingest

GUI=true /home/ubuntu/dlp-ingest-ui/venv/bin/python -m gunicorn --bind :8000 --workers=1 --threads=15 application