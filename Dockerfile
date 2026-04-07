FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY README.md .
COPY pyproject.toml .

EXPOSE 8080

CMD ["sh", "-c", "uvicorn reporter.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
