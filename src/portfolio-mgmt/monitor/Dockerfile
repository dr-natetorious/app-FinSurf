FROM python:3.8

WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -r requirements.txt -t /app
ENTRYPOINT [ "/usr/bin/python3", "/app/main.py" ]
