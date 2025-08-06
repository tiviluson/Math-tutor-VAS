# Multi-stage Dockerfile for AI Geometry Tutor Backend with Asymptote support
# Optimized for the new src/ directory structure

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for building Python packages
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Stage 2: Production runtime
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    ASYMPTOTE_TEXPATH="/usr/bin" \
    ASYMPTOTE_MAGICKPATH="/usr/bin" \
    PYTHONPATH="/app"

# Install runtime dependencies for Asymptote
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    asymptote \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-pictures \
    imagemagick \
    dvisvgm \
    ghostscript && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Fix ImageMagick policy for ghostscript
RUN sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code with new structure
COPY src/ /app/src/
COPY scripts/ /app/scripts/
COPY notebooks/ /app/notebooks/

# Create necessary directories
RUN mkdir -p /tmp/asymptote

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command using the new script location
CMD ["python", "scripts/run_api_server.py", "--host", "0.0.0.0", "--port", "8000"]