#!/bin/bash
cd ./src
git clone https://github.com/vt-digital-libraries-platform/dlp-ingest
cd ./dlp-ingest
git checkout ui
cd ..
mv dlp-ingest dlp_ingest

venv
GUI=true python -m gunicorn --bind :8000 --workers=1 --threads=15 application