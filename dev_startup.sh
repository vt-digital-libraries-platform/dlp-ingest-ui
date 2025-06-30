#!/bin/bash
cd ./src
rm -rf dlp_ingest
git clone --branch ui https://github.com/vt-digital-libraries-platform/dlp-ingest dlp_ingest
cd ..
virtualenv dlp-ingest-ui-env
source dlp-ingest-ui-env/bin/activate
pip install -r requirements.txt --quiet
cd ./src
clear

INGEST_ENV_YAML="test_env_defaults.yml" \
GUI=true python -m gunicorn --bind :8000 --workers=1 --threads=15 application