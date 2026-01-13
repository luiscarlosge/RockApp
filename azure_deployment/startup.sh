#!/bin/bash

# Azure App Service startup script for Rock and Roll Forum Jam en Español
# This script starts the Flask application using Gunicorn

echo "Starting Rock and Roll Forum Jam en Español..."
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Files in directory: $(ls -la)"

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Start the application with Gunicorn
echo "Starting application with Gunicorn..."
gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 app:app