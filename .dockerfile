# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /library

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE $PORT

# Run migrations and start the server with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backendDjango.wsgi:application"]