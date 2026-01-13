# Azure App Service Linux Deployment Guide

## Musician Song Selector with Song Order Enhancement

This guide explains how to deploy the enhanced Musician Song Selector application to Azure App Service using a Linux plan.

## Prerequisites

1. **Azure CLI installed**
   ```bash
   # Install Azure CLI (Ubuntu/Debian)
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # Or install via pip
   pip install azure-cli
   ```

2. **Azure subscription** with appropriate permissions

3. **Git installed** for deployment

## Quick Deployment

### Option 1: Automated Deployment (Recommended)

Run the automated deployment script:

```bash
# Make the script executable
chmod +x deploy-to-azure-linux.sh

# Run the deployment
./deploy-to-azure-linux.sh
```

This script will:
- Create all necessary Azure resources
- Configure the App Service for Linux
- Enable WebSocket support
- Deploy your application
- Test the deployment

### Option 2: Manual Deployment

#### Step 1: Login to Azure

```bash
az login
```

#### Step 2: Create Resource Group

```bash
az group create \
    --name "rock-app-rg" \
    --location "East US"
```

#### Step 3: Create App Service Plan (Linux)

```bash
az appservice plan create \
    --name "rock-app-linux-plan" \
    --resource-group "rock-app-rg" \
    --location "East US" \
    --is-linux \
    --sku B1
```

#### Step 4: Create Web App

```bash
az webapp create \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg" \
    --plan "rock-app-linux-plan" \
    --runtime "PYTHON|3.9"
```

#### Step 5: Configure Web App

```bash
# Enable WebSocket support
az webapp config set \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg" \
    --web-sockets-enabled true

# Set startup command
az webapp config set \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg" \
    --startup-file "python3 startup.py"

# Configure application settings
az webapp config appsettings set \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg" \
    --settings \
        FLASK_ENV=production \
        FLASK_DEBUG=False \
        PYTHONPATH=/home/site/wwwroot \
        WEBSITE_WEBSOCKET_ENABLED=true \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Enable HTTPS only
az webapp update \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg" \
    --https-only true
```

#### Step 6: Deploy Application

```bash
# Configure local Git deployment
az webapp deployment source config-local-git \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg"

# Initialize Git repository (if not already done)
git init
git add .
git commit -m "Initial commit for Azure deployment"

# Get deployment URL and add as remote
DEPLOY_URL=$(az webapp deployment list-publishing-credentials \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg" \
    --query scmUri -o tsv)

git remote add azure $DEPLOY_URL

# Push to Azure
git push azure main:master
```

## Application Features

The deployed application includes:

### ✅ Core Features
- **Song Order Enhancement**: Songs displayed and sorted by performance order
- **Next Song Navigation**: Automatic next song calculation and display
- **Spanish Language Support**: Complete Spanish interface and translations
- **Real-time Synchronization**: Global song selection across all sessions
- **WebSocket Support**: Real-time updates with fallback to polling

### ✅ Technical Features
- **Flask-SocketIO**: Real-time bidirectional communication
- **Azure Linux Compatibility**: Optimized for Azure App Service Linux
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: Robust error handling and recovery
- **Performance Optimized**: Fast loading and responsive interface

## Configuration

### Environment Variables

The following environment variables are automatically configured:

- `FLASK_ENV=production`
- `FLASK_DEBUG=False`
- `PYTHONPATH=/home/site/wwwroot`
- `WEBSITE_WEBSOCKET_ENABLED=true`
- `SCM_DO_BUILD_DURING_DEPLOYMENT=true`

### WebSocket Configuration

WebSocket support is enabled by default with the following features:
- Primary transport: WebSocket
- Fallback transport: Server-Sent Events and Polling
- Ping timeout: 60 seconds
- Ping interval: 25 seconds
- CORS enabled for all origins

## Monitoring and Troubleshooting

### View Application Logs

```bash
# Stream live logs
az webapp log tail \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg"

# Download log files
az webapp log download \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg"
```

### SSH into Container

```bash
az webapp ssh \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg"
```

### Restart Application

```bash
az webapp restart \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg"
```

### Health Check

Test the application health:

```bash
curl https://rock-app-linux.azurewebsites.net/api/health
```

## File Structure

The deployment includes these key files:

```
/home/site/wwwroot/
├── app.py                    # Main Flask application
├── startup.py               # Azure startup configuration
├── requirements.txt         # Python dependencies
├── Data.csv                # Song data
├── csv_data_processor.py   # Data processing logic
├── global_state_manager.py # Real-time state management
├── spanish_translations.py # Spanish language support
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   └── global-selector.html
├── static/                 # Static assets
│   ├── css/
│   └── js/
└── deploy.sh              # Linux deployment script
```

## Performance Considerations

### Scaling

For production use, consider upgrading to a higher SKU:

```bash
# Upgrade to Premium V2 for better performance
az appservice plan update \
    --name "rock-app-linux-plan" \
    --resource-group "rock-app-rg" \
    --sku P1V2
```

### Always On

Enable "Always On" to prevent cold starts:

```bash
az webapp config set \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg" \
    --always-on true
```

## Security

### HTTPS Only

HTTPS is enforced by default. All HTTP requests are redirected to HTTPS.

### Application Insights

Enable Application Insights for monitoring:

```bash
az monitor app-insights component create \
    --app "rock-app-insights" \
    --location "East US" \
    --resource-group "rock-app-rg"

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app "rock-app-insights" \
    --resource-group "rock-app-rg" \
    --query instrumentationKey -o tsv)

# Configure Application Insights
az webapp config appsettings set \
    --name "rock-app-linux" \
    --resource-group "rock-app-rg" \
    --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

## Troubleshooting

### Common Issues

1. **Application not starting**
   - Check logs: `az webapp log tail --name rock-app-linux --resource-group rock-app-rg`
   - Verify startup.py is present and executable
   - Check Python dependencies in requirements.txt

2. **WebSocket not working**
   - Ensure WebSocket is enabled in App Service configuration
   - Check that the client can connect to the WebSocket endpoint
   - Verify CORS settings if accessing from different domains

3. **Spanish translations not displaying**
   - Verify spanish_translations.py is deployed
   - Check that translation files are properly encoded (UTF-8)
   - Ensure templates are using the translation functions

4. **CSV data not loading**
   - Verify Data.csv is present in the deployment
   - Check file permissions and encoding
   - Review csv_data_processor.py logs

### Getting Help

- **Azure Documentation**: https://docs.microsoft.com/en-us/azure/app-service/
- **Flask-SocketIO Documentation**: https://flask-socketio.readthedocs.io/
- **Application Logs**: Use `az webapp log tail` for real-time debugging

## Cost Optimization

- **Basic Tier (B1)**: Suitable for development and testing
- **Standard Tier (S1)**: Good for small production workloads
- **Premium V2 (P1V2)**: Recommended for production with high availability needs

Monitor your usage and scale appropriately to optimize costs.

---

## Summary

This deployment guide provides everything needed to deploy the enhanced Musician Song Selector application to Azure App Service using Linux. The application includes song order enhancement, real-time synchronization, and Spanish language support, all optimized for Azure's Linux App Service platform.

For questions or issues, refer to the troubleshooting section or Azure documentation.