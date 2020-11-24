FROM python:3.8

COPY requirements.txt .
RUN apt-get -y update && apt-get -y install npm zip git \
  && npm install -g aws-cdk \
  && pip install -r requirements.txt
