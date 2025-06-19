# Dockerfile for IQDB API Python
FROM python:3.13-slim

# Metadata
LABEL maintainer="hieuxyz <khongbt446@gmail.com>"
LABEL description="IQDB API Python - Reverse image search library"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY examples/ ./examples/
COPY pyproject.toml setup.py MANIFEST.in ./

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash iqdb && \
    chown -R iqdb:iqdb /app

USER iqdb

# Default command
CMD ["python", "-c", "import iqdb_api; print('IQDB API Python v' + iqdb_api.__version__ + ' ready!')"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import iqdb_api; print('OK')" || exit 1
