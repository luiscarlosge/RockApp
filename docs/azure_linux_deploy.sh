#!/bin/bash
"""
Azure App Service Linux deployment script
Handles the deployment and configuration of the Flask-SocketIO application
"""

set -e

echo "Starting Azure Linux deployment..."

# Set environment variables
export PYTHONPATH="/home/site/wwwroot"
export FLASK_ENV="production"
export FLASK_DEBUG="False"
export WEBSOCKET_ENABLED="true"

# Create necessary directories
mkdir -p /home/site/wwwroot/logs
mkdir -p /home/site/wwwroot/tmp

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements_linux.txt

# Verify critical files exist
echo "Verifying application files..."
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found!"
    exit 1
fi

if [ ! -f "Data.csv" ]; then
    echo "ERROR: Data.csv not found!"
    exit 1
fi

if [ ! -f "startup_linux.py" ]; then
    echo "ERROR: startup_linux.py not found!"
    exit 1
fi

# Set file permissions
chmod +x startup_linux.py
chmod +x gunicorn.conf.py

# Test application startup
echo "Testing application startup..."
python -c "from app import app; print('Flask app imported successfully')"
python -c "from startup_linux import application; print('Application factory working')"

echo "Azure Linux deployment completed successfully!"

# Start the application with Gunicorn
echo "Starting application with Gunicorn..."
exec gunicorn --config gunicorn.conf.py startup_linux:application