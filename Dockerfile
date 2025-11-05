# 🧬 KONOMI SYSTEM - Dockerfile
# Lightweight container for CPU-based distributed AI
# No GPU required!

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./

# Expose ports
# 3001: REST API
# 3002: WebSocket
EXPOSE 3001 3002

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV EVGPU_CORES=4

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3001/health')" || exit 1

# Default command (REST API)
CMD ["python", "api_rest.py"]
