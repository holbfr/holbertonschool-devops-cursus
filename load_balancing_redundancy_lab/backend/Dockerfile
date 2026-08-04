FROM python:3.12-slim

WORKDIR /app

ENV HOST=0.0.0.0

ENV PORT=5000

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python3", "app.py"]
