FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package app/ (không copy .env, data — xem .dockerignore)
COPY app/ ./app/

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.address", "0.0.0.0", "--server.port", "8501"]