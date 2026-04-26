FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY .env .env 2>/dev/null || true

RUN mkdir -p output certs && useradd -m arca && chown -R arca:arca /app
USER arca

EXPOSE 8501

CMD ["streamlit", "run", "src/web/streamlit_app.py"]
