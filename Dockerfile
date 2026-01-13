# Azure App Service Linux compatible Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /home/site/wwwroot

# Set environment variables
ENV PYTHONPATH=/home/site/wwwroot
ENV FLASK_ENV=production
ENV FLASK_DEBUG=False
ENV WEBSOCKET_ENABLED=true
ENV SOCKETIO_ASYNC_MODE=eventlet
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_linux.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_linux.txt

# Copy application files
COPY . .

# Set file permissions
RUN chmod +x startup_linux.py && \
    chmod +x azure_linux_deploy.sh

# Create necessary directories
RUN mkdir -p logs tmp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "startup_linux:application"]