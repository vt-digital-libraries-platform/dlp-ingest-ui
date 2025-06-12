FROM ubuntu
LABEL authors="Lee Hunter <whunter@vt.edu>"
WORKDIR /home/ubuntu/dlp-ingest-ui
EXPOSE 8000
RUN apt update && apt upgrade -y 
RUN apt install build-essential git python3-full python3-pip python3-virtualenv wget -y && rm -rf /var/lib/apt/lists/*
RUN virtualenv ./venv
RUN . ./venv/bin/activate
COPY requirements.txt .
RUN ./venv/bin/pip install -r requirements.txt
COPY . .

CMD ["/bin/bash", "./startup.sh"]
