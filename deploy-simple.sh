#!/bin/bash

# ----------------------
# Simple Azure App Service Linux Deployment Script
# Minimal approach with hardcoded python3
# ----------------------

set -e

echo "=== Simple Azure Linux Deployment ==="
echo "Using hardcoded python3 command"

# Get deployment paths
DEPLOYMENT_SOURCE=${DEPLOYMENT_SOURCE:-$PWD}
DEPLOYMENT_TARGET=${DEPLOYMENT_TARGET:-/home/site/wwwroot}

echo "Source: $DEPLOYMENT_SOURCE"
echo "Target: $DEPLOYMENT_TARGET"

# Create target directory
mkdir -p "$DEPLOYMENT_TARGET"

# Copy files
echo "Copying files..."
cp -r "$DEPLOYMENT_SOURCE"/* "$DEPLOYMENT_TARGET/" 2>/dev/null || true

# Remove deployment files from target
rm -f "$DEPLOYMENT_TARGET/deploy.sh"
rm -f "$DEPLOYMENT_TARGET/deploy-simple.sh"
rm -f "$DEPLOYMENT_TARGET/.deployment"

# Change to target directory
cd "$DEPLOYMENT_TARGET"

# Check Python availability
echo "Checking Python..."
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
    echo "Using python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
    echo "Using python"
else
    echo "ERROR: No Python found"
    exit 1
fi

echo "Python version: $($PYTHON_CMD --version)"

# Install dependencies
echo "Installing dependencies..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

# Test imports
echo "Testing imports..."
$PYTHON_CMD -c "
import flask
import flask_socketio
import pandas
print('✓ Core modules imported successfully')
"

# Create startup file
echo "$PYTHON_CMD startup.py" > startup_command.txt

echo "✅ Simple deployment completed"
echo "Startup command: $PYTHON_CMD startup.py"