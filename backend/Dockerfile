# Multi-stage Dockerfile for AI Geometry Tutor Backend with Asymptote support
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
    ASYMPTOTE_MAGICKPATH="/usr/bin"

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

# Create necessary directory structure and __init__.py files
RUN mkdir -p /app/api/asymptote && \
    touch /app/api/asymptote/__init__.py

# Copy application code
COPY api/__init__.py /app/api/
COPY api/main.py /app/api/
COPY api/tutor.py /app/api/

COPY api/asymptote/viz_tool.py /app/api/asymptote/
COPY api/asymptote/viz_prompts.py /app/api/asymptote/
COPY api/asymptote/olympiad.asy /app/

COPY geometry_tutor /app/geometry_tutor
COPY run_api_server.py /app/

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "run_api_server.py", "--host", "0.0.0.0", "--port", "8000"]
