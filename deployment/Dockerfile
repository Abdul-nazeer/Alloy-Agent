FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including DNS tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    dnsutils \
    iputils-ping \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Update CA certificates for HTTPS
RUN update-ca-certificates

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with retry
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --retries 5 --timeout 100 -r requirements.txt

# Copy application code
COPY backend ./backend
COPY data ./data

# Create necessary directories
RUN mkdir -p backend/data logs

# Expose API port
EXPOSE 8000

# Set Python path and environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run database migration then start server
CMD python3 backend/migrate_database.py && \
    uvicorn backend.src.api.main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 75

