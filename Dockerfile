FROM python:3.8-slim-buster

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY TelebotSync.py .
COPY util.py .
COPY credentials.json .
COPY token.json .
COPY database_handler.py .
COPY firebase_cred.json .

CMD ["python3", "TelebotSync.py"]