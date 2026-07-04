FROM python:3.11-slim

WORKDIR /app

# Cài thư viện trước — layer này được cache nếu requirements.txt không đổi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code (không copy .env, chroma_db, data — xem .dockerignore)
COPY phase4/app.py ./phase4/app.py

EXPOSE 8501

CMD ["streamlit", "run", "phase4/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
