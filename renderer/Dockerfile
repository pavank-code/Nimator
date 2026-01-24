FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies for Manim and FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    python3-dev \
    build-essential \
    texlive \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-science \
    dvipng \
    cm-super \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app ./app

# Create output directories
RUN mkdir -p /app/outputs /app/temp

# Set Manim configuration
ENV MANIM_MEDIA_DIR=/app/temp/manim_media

# Command to run the worker
CMD ["python", "-m", "app.worker"]