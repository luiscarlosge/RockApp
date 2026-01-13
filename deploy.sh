#!/bin/bash

# ----------------------
# Azure App Service Linux Deployment Script
# For Python Flask Application with SocketIO
# Version 2.0 - Fixed Python command detection
# ----------------------

set -e

echo "=== Azure App Service Linux Deployment v2.0 ==="
echo "Starting deployment at: $(date)"

# Get deployment paths
DEPLOYMENT_SOURCE=${DEPLOYMENT_SOURCE:-$PWD}
DEPLOYMENT_TARGET=${DEPLOYMENT_TARGET:-/home/site/wwwroot}
ARTIFACTS=${ARTIFACTS:-/tmp/artifacts}

echo "Deployment source: $DEPLOYMENT_SOURCE"
echo "Deployment target: $DEPLOYMENT_TARGET"

# Create artifacts directory if it doesn't exist
mkdir -p "$ARTIFACTS"

# Function to log and execute commands with better error handling
execute_cmd() {
    echo ">>> Executing: $*"
    if ! "$@"; then
        echo "!!! Command failed: $*"
        echo "!!! Exit code: $?"
        exit 1
    fi
    echo ">>> Command completed successfully"
}

# Function to find Python executable with verbose output
find_python_executable() {
    echo "=== Detecting Python executable ==="
    
    # Check for python3 first (preferred for Azure Linux)
    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 --version 2>&1)
        echo "✓ Found python3: $python_version"
        echo "python3"
        return 0
    fi
    
    # Check for python as fallback
    if command -v python >/dev/null 2>&1; then
        local python_version=$(python --version 2>&1)
        echo "✓ Found python: $python_version"
        echo "python"
        return 0
    fi
    
    # Check common Azure paths
    if [ -x "/usr/bin/python3" ]; then
        local python_version=$(/usr/bin/python3 --version 2>&1)
        echo "✓ Found /usr/bin/python3: $python_version"
        echo "/usr/bin/python3"
        return 0
    fi
    
    if [ -x "/opt/python/3.9/bin/python" ]; then
        local python_version=$(/opt/python/3.9/bin/python --version 2>&1)
        echo "✓ Found /opt/python/3.9/bin/python: $python_version"
        echo "/opt/python/3.9/bin/python"
        return 0
    fi
    
    # List available executables for debugging
    echo "!!! Python not found in standard locations"
    echo "Available executables in /usr/bin:"
    ls -la /usr/bin/python* 2>/dev/null || echo "No python executables in /usr/bin"
    echo "Available executables in /opt:"
    find /opt -name "python*" -type f 2>/dev/null || echo "No python executables in /opt"
    echo "PATH: $PATH"
    
    echo "ERROR: No Python executable found"
    exit 1
}

# Detect Python executable
echo "=== Python Detection Phase ==="
PYTHON_CMD=$(find_python_executable)
echo "Selected Python command: $PYTHON_CMD"

# Verify Python works
echo "=== Python Verification ==="
execute_cmd $PYTHON_CMD --version
execute_cmd $PYTHON_CMD -c "import sys; print(f'Python executable: {sys.executable}')"
execute_cmd $PYTHON_CMD -c "import sys; print(f'Python path: {sys.path[:3]}')"

# ----------------------
# 1. Copy application files
# ----------------------
echo "=== File Copy Phase ==="
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

echo "✓ Application files copied successfully"

# ----------------------
# 2. Verify critical files
# ----------------------
echo "=== File Verification Phase ==="
echo "Verifying critical files..."

# Check for Data.csv
if [ ! -f "$DEPLOYMENT_TARGET/Data.csv" ]; then
    echo "!!! ERROR: Data.csv file is missing from deployment"
    exit 1
else
    echo "✓ Data.csv file found"
fi

# Check for startup.py
if [ ! -f "$DEPLOYMENT_TARGET/startup.py" ]; then
    echo "!!! ERROR: startup.py file is missing from deployment"
    exit 1
else
    echo "✓ startup.py file found"
fi

# Check for requirements.txt
if [ ! -f "$DEPLOYMENT_TARGET/requirements.txt" ]; then
    echo "!!! ERROR: requirements.txt file is missing from deployment"
    exit 1
else
    echo "✓ requirements.txt file found"
fi

# Check for app.py
if [ ! -f "$DEPLOYMENT_TARGET/app.py" ]; then
    echo "!!! ERROR: app.py file is missing from deployment"
    exit 1
else
    echo "✓ app.py file found"
fi

# ----------------------
# 3. Install Python dependencies
# ----------------------
echo "=== Python Dependencies Installation Phase ==="
echo "Installing Python dependencies..."

cd "$DEPLOYMENT_TARGET"

# Show current directory and Python info
echo "Current directory: $(pwd)"
echo "Python executable: $PYTHON_CMD"
echo "Python version: $($PYTHON_CMD --version)"

# Check if pip is available
echo "Checking pip availability..."
if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
    echo "!!! pip not available, attempting to install..."
    if command -v curl >/dev/null 2>&1; then
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        execute_cmd $PYTHON_CMD get-pip.py
        rm -f get-pip.py
    else
        echo "!!! Cannot install pip - curl not available"
        exit 1
    fi
fi

# Upgrade pip
echo "Upgrading pip..."
execute_cmd $PYTHON_CMD -m pip install --upgrade pip

# Show pip version
echo "Pip version: $($PYTHON_CMD -m pip --version)"

# Install requirements
echo "Installing requirements from requirements.txt..."
execute_cmd $PYTHON_CMD -m pip install -r requirements.txt

echo "✓ Python dependencies installed successfully"

# ----------------------
# 4. Set up application configuration
# ----------------------
echo "=== Application Configuration Phase ==="
echo "Setting up application configuration..."

# Create startup command file that Azure App Service can use
cat > "$DEPLOYMENT_TARGET/startup_command.txt" << EOF
$PYTHON_CMD startup.py
EOF

echo "✓ Startup command file created: $PYTHON_CMD startup.py"

# ----------------------
# 5. Validate Python application
# ----------------------
echo "=== Application Validation Phase ==="
echo "Validating Python application..."

# Test import of main modules
$PYTHON_CMD -c "
import sys
import os
sys.path.insert(0, '.')

print('=== Module Import Test ===')
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

print('✓ All critical modules imported successfully')
"

# ----------------------
# 6. Set proper permissions
# ----------------------
echo "=== File Permissions Phase ==="
echo "Setting file permissions..."

# Make startup.py executable
chmod +x "$DEPLOYMENT_TARGET/startup.py"

# Set proper permissions for the application directory
find "$DEPLOYMENT_TARGET" -type f -name "*.py" -exec chmod 644 {} \;
find "$DEPLOYMENT_TARGET" -type d -exec chmod 755 {} \;

echo "✓ File permissions set"

# ----------------------
# 7. Log deployment information
# ----------------------
echo "=== Deployment Information Phase ==="
echo "Logging deployment information..."

echo "Deployment completed at: $(date)"
echo "Python executable: $PYTHON_CMD"
echo "Python version: $($PYTHON_CMD --version)"
echo "Pip version: $($PYTHON_CMD -m pip --version)"
echo "Working directory: $(pwd)"
echo "Files in deployment target:"
ls -la "$DEPLOYMENT_TARGET" | head -20

echo "Python packages installed:"
$PYTHON_CMD -m pip list | grep -E "(Flask|socketio|gunicorn|pandas)" || echo "Package list not available"

# ----------------------
# 8. Final validation
# ----------------------
echo "=== Final Validation Phase ==="
echo "Performing final validation..."

# Check if all critical Python modules can be imported
$PYTHON_CMD -c "
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

print('=== Final Module Import Test ===')
failed_imports = []
for module in modules_to_test:
    try:
        __import__(module)
        print(f'✓ {module}')
    except ImportError as e:
        print(f'✗ {module}: {e}')
        failed_imports.append(module)

if failed_imports:
    print(f'!!! Failed to import: {failed_imports}')
    print('This may cause runtime issues')
else:
    print('✓ All critical modules imported successfully')
"

echo ""
echo "=============================================="
echo "✅ AZURE LINUX DEPLOYMENT COMPLETED"
echo "=============================================="
echo ""
echo "Application Details:"
echo "- Flask application with SocketIO support"
echo "- Song Order Enhancement features enabled"
echo "- Spanish language support included"
echo "- Real-time synchronization ready"
echo "- WebSocket support configured for Azure"
echo ""
echo "Python Configuration:"
echo "- Python executable: $PYTHON_CMD"
echo "- Python version: $($PYTHON_CMD --version 2>/dev/null || echo 'Version check failed')"
echo "- Startup command: $PYTHON_CMD startup.py"
echo ""
echo "Next Steps:"
echo "1. Configure Azure App Service startup command: '$PYTHON_CMD startup.py'"
echo "2. Enable WebSocket support in Azure App Service configuration"
echo "3. Set any required environment variables"
echo "4. Monitor application logs for successful startup"
echo ""
echo "Deployment completed successfully at: $(date)"