#!/bin/bash

# ----------------------
# Azure App Service Linux Deployment Script
# For Python Flask Application with SocketIO
# ----------------------

set -e

echo "Starting Azure App Service Linux deployment..."

# Get deployment paths
DEPLOYMENT_SOURCE=${DEPLOYMENT_SOURCE:-$PWD}
DEPLOYMENT_TARGET=${DEPLOYMENT_TARGET:-/home/site/wwwroot}
ARTIFACTS=${ARTIFACTS:-/tmp/artifacts}

echo "Deployment source: $DEPLOYMENT_SOURCE"
echo "Deployment target: $DEPLOYMENT_TARGET"

# Create artifacts directory if it doesn't exist
mkdir -p "$ARTIFACTS"

# Function to log and execute commands
execute_cmd() {
    echo "Executing: $*"
    if ! "$@"; then
        echo "Command failed: $*"
        exit 1
    fi
}

# ----------------------
# 1. Copy application files
# ----------------------
echo "Copying application files..."

# Create target directory if it doesn't exist
mkdir -p "$DEPLOYMENT_TARGET"

# Copy all files except excluded ones
rsync -av \
    --exclude='.git' \
    --exclude='.gitignore' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='.hypothesis' \
    --exclude='node_modules' \
    --exclude='.vscode' \
    --exclude='deploy.sh' \
    --exclude='.deployment' \
    "$DEPLOYMENT_SOURCE/" "$DEPLOYMENT_TARGET/"

echo "Application files copied successfully"

# ----------------------
# 2. Verify critical files
# ----------------------
echo "Verifying critical files..."

# Check for Data.csv
if [ ! -f "$DEPLOYMENT_TARGET/Data.csv" ]; then
    echo "ERROR: Data.csv file is missing from deployment"
    exit 1
else
    echo "✓ Data.csv file found"
fi

# Check for startup.py
if [ ! -f "$DEPLOYMENT_TARGET/startup.py" ]; then
    echo "ERROR: startup.py file is missing from deployment"
    exit 1
else
    echo "✓ startup.py file found"
fi

# Check for requirements.txt
if [ ! -f "$DEPLOYMENT_TARGET/requirements.txt" ]; then
    echo "ERROR: requirements.txt file is missing from deployment"
    exit 1
else
    echo "✓ requirements.txt file found"
fi

# Check for app.py
if [ ! -f "$DEPLOYMENT_TARGET/app.py" ]; then
    echo "ERROR: app.py file is missing from deployment"
    exit 1
else
    echo "✓ app.py file found"
fi

# ----------------------
# 3. Install Python dependencies
# ----------------------
echo "Installing Python dependencies..."

cd "$DEPLOYMENT_TARGET"

# Upgrade pip
execute_cmd python -m pip install --upgrade pip

# Install requirements
execute_cmd python -m pip install -r requirements.txt

echo "Python dependencies installed successfully"

# ----------------------
# 4. Set up application configuration
# ----------------------
echo "Setting up application configuration..."

# Create a simple web.config for Azure App Service Linux (optional)
cat > "$DEPLOYMENT_TARGET/web.config" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="/opt/python/3.9/bin/python"
                  arguments="startup.py"
                  stdoutLogEnabled="true"
                  stdoutLogFile="/home/LogFiles/python.log"
                  startupTimeLimit="60"
                  requestTimeout="00:04:00">
      <environmentVariables>
        <environmentVariable name="PYTHONPATH" value="/home/site/wwwroot" />
        <environmentVariable name="PORT" value="%HTTP_PLATFORM_PORT%" />
        <environmentVariable name="WEBSITE_HOSTNAME" value="%WEBSITE_HOSTNAME%" />
      </environmentVariables>
    </httpPlatform>
    <webSocket enabled="true" />
  </system.webServer>
</configuration>
EOF

# ----------------------
# 5. Validate Python application
# ----------------------
echo "Validating Python application..."

# Test import of main modules
python -c "
import sys
sys.path.insert(0, '.')
try:
    from app import app
    print('✓ Flask app imports successfully')
except Exception as e:
    print(f'✗ Flask app import failed: {e}')
    sys.exit(1)

try:
    from startup import application
    print('✓ Startup module imports successfully')
except Exception as e:
    print(f'✗ Startup module import failed: {e}')
    sys.exit(1)

try:
    import flask_socketio
    print('✓ Flask-SocketIO available')
except Exception as e:
    print(f'✗ Flask-SocketIO import failed: {e}')
    sys.exit(1)
"

# ----------------------
# 6. Set proper permissions
# ----------------------
echo "Setting file permissions..."

# Make startup.py executable
chmod +x "$DEPLOYMENT_TARGET/startup.py"

# Set proper permissions for the application directory
find "$DEPLOYMENT_TARGET" -type f -name "*.py" -exec chmod 644 {} \;
find "$DEPLOYMENT_TARGET" -type d -exec chmod 755 {} \;

# ----------------------
# 7. Create startup command file for Azure
# ----------------------
echo "Creating startup command configuration..."

# Create a startup command file that Azure App Service can use
cat > "$DEPLOYMENT_TARGET/startup_command.txt" << 'EOF'
python startup.py
EOF

# ----------------------
# 8. Log deployment information
# ----------------------
echo "Logging deployment information..."

echo "Deployment completed at: $(date)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Working directory: $(pwd)"
echo "Files in deployment target:"
ls -la "$DEPLOYMENT_TARGET" | head -20

echo "Python packages installed:"
pip list | grep -E "(Flask|socketio|gunicorn|pandas)" || true

# ----------------------
# 9. Final validation
# ----------------------
echo "Performing final validation..."

# Check if all critical Python modules can be imported
python -c "
import sys
import os
sys.path.insert(0, '.')

modules_to_test = [
    'flask',
    'flask_socketio', 
    'pandas',
    'csv_data_processor',
    'global_state_manager',
    'spanish_translations'
]

failed_imports = []
for module in modules_to_test:
    try:
        __import__(module)
        print(f'✓ {module}')
    except ImportError as e:
        print(f'✗ {module}: {e}')
        failed_imports.append(module)

if failed_imports:
    print(f'Failed to import: {failed_imports}')
    sys.exit(1)
else:
    print('All critical modules imported successfully')
"

echo ""
echo "=============================================="
echo "✅ AZURE LINUX DEPLOYMENT COMPLETED SUCCESSFULLY"
echo "=============================================="
echo ""
echo "Application Details:"
echo "- Flask application with SocketIO support"
echo "- Song Order Enhancement features enabled"
echo "- Spanish language support included"
echo "- Real-time synchronization ready"
echo "- WebSocket support configured for Azure"
echo ""
echo "Startup Information:"
echo "- Main application file: startup.py"
echo "- Port: Configured via PORT environment variable"
echo "- Host: 0.0.0.0 (all interfaces)"
echo "- WebSocket: Enabled with fallback to polling"
echo ""
echo "Next Steps:"
echo "1. Configure Azure App Service startup command: 'python startup.py'"
echo "2. Enable WebSocket support in Azure App Service configuration"
echo "3. Set any required environment variables"
echo "4. Monitor application logs for successful startup"
echo ""
echo "Deployment completed successfully!"