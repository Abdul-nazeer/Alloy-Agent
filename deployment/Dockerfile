FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend ./backend
COPY data ./data

# Create necessary directories
RUN mkdir -p backend/data logs

# Expose API port (Railway uses dynamic PORT)
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run FastAPI with uvicorn (Railway provides PORT env var)
CMD ["sh", "-c", "uvicorn backend.src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

