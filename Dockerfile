FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .

ENTRYPOINT ["python", "read_emails.py"]
