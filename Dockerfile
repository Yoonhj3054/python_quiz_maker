FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render automatically sets the PORT environment variable.
CMD gunicorn app:app --bind 0.0.0.0:$PORT
