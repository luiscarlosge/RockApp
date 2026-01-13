#!/bin/bash
"""
Local deployment script for Azure App Service Linux
Creates the deployment package and provides deployment instructions
"""

set -e

echo "=== Azure App Service Linux Deployment Script ==="
echo "Creating deployment package for Rock and Roll Forum Jam en Español"
echo ""

# Clean up any existing deployment files
echo "Cleaning up previous deployment files..."
rm -f app.zip
rm -rf deploy_temp

# Create temporary deployment directory
echo "Creating deployment package..."
mkdir -p deploy_temp

# Copy application files
echo "Copying application files..."
cp app.py deploy_temp/
cp startup_linux.py deploy_temp/
cp gunicorn.conf.py deploy_temp/
cp requirements_linux.txt deploy_temp/requirements.txt
cp runtime_linux.txt deploy_temp/runtime.txt
cp azure_linux_deploy.sh deploy_temp/
cp Dockerfile deploy_temp/
cp Data.csv deploy_temp/

# Copy Python modules
echo "Copying Python modules..."
cp csv_data_processor.py deploy_temp/
cp spanish_translations.py deploy_temp/
cp global_state_manager.py deploy_temp/
cp socketio_fallback_config.py deploy_temp/

# Copy static files and templates
echo "Copying static files and templates..."
cp -r static deploy_temp/
cp -r templates deploy_temp/

# Copy configuration files
echo "Copying configuration files..."
cp azure_linux_config.json deploy_temp/

# Create .deployment file for Azure
cat > deploy_temp/.deployment << 'EOF'
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
ENABLE_ORYX_BUILD=true
PRE_BUILD_SCRIPT_PATH=azure_linux_deploy.sh
EOF

# Create web.config for Azure (even though it's Linux, some settings are still used)
cat > deploy_temp/web.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <webSocket enabled="true" />
    <httpProtocol>
      <customHeaders>
        <add name="Access-Control-Allow-Origin" value="*" />
        <add name="Access-Control-Allow-Methods" value="GET, POST, OPTIONS, PUT, DELETE" />
        <add name="Access-Control-Allow-Headers" value="Content-Type, Authorization, X-Requested-With" />
      </customHeaders>
    </httpProtocol>
  </system.webServer>
</configuration>
EOF

# Create the zip file
echo "Creating app.zip..."
cd deploy_temp
zip -r ../app.zip . -x "*.pyc" "*/__pycache__/*" "*.git*" "*.DS_Store*"
cd ..

# Clean up temporary directory
rm -rf deploy_temp

echo ""
echo "=== Deployment Package Created Successfully ==="
echo "File: app.zip"
echo "Size: $(du -h app.zip | cut -f1)"
echo ""
echo "=== Deployment Instructions ==="
echo ""
echo "1. Create Azure App Service (Linux):"
echo "   - Runtime: Python 3.11"
echo "   - Operating System: Linux"
echo "   - Enable WebSockets in Configuration > General settings"
echo ""
echo "2. Configure Application Settings:"
echo "   FLASK_ENV=production"
echo "   FLASK_DEBUG=False"
echo "   WEBSOCKET_ENABLED=true"
echo "   SOCKETIO_ASYNC_MODE=eventlet"
echo ""
echo "3. Set Startup Command:"
echo "   gunicorn --config gunicorn.conf.py startup_linux:application"
echo ""
echo "4. Deploy using one of these methods:"
echo ""
echo "   Method A - Azure CLI:"
echo "   az webapp deployment source config-zip --resource-group <resource-group> --name <app-name> --src app.zip"
echo ""
echo "   Method B - Azure Portal:"
echo "   - Go to Deployment Center"
echo "   - Choose 'ZIP Deploy'"
echo "   - Upload app.zip"
echo ""
echo "   Method C - VS Code:"
echo "   - Install Azure App Service extension"
echo "   - Right-click app.zip and select 'Deploy to Web App'"
echo ""
echo "5. Verify deployment:"
echo "   - Check https://<your-app-name>.azurewebsites.net"
echo "   - Monitor logs in Log stream"
echo "   - Test WebSocket functionality"
echo ""
echo "=== Additional Configuration ==="
echo ""
echo "For production environments, consider:"
echo "- Enable Application Insights for monitoring"
echo "- Configure custom domain and SSL certificate"
echo "- Set up deployment slots for staging"
echo "- Configure auto-scaling rules"
echo "- Set up backup and disaster recovery"
echo ""
echo "=== Troubleshooting ==="
echo ""
echo "If deployment fails:"
echo "1. Check the deployment logs in Azure Portal"
echo "2. Verify all required files are in app.zip"
echo "3. Ensure Python version matches runtime.txt"
echo "4. Check startup command is correct"
echo "5. Review Application Settings configuration"
echo ""
echo "For WebSocket issues:"
echo "1. Ensure WebSockets are enabled in App Service configuration"
echo "2. Check that eventlet is installed (in requirements.txt)"
echo "3. Verify gunicorn is using eventlet worker class"
echo "4. Test with polling transport first, then WebSocket"
echo ""
echo "Deployment package ready: app.zip"