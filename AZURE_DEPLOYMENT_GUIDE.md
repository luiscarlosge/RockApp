# Azure App Service Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Musician Song Selector application to Azure App Service.

## Prerequisites

- Azure subscription with App Service capability
- Azure CLI installed (optional, for command-line deployment)
- Git repository (for continuous deployment)

## Deployment Files Created

The following files have been configured for Azure App Service deployment:

### Core Application Files
- `startup.py` - Enhanced Azure-compatible startup script with logging and error handling
- `app.py` - Main Flask application with Azure-specific configurations
- `web.config` - IIS configuration for Azure App Service Python runtime
- `requirements.txt` - Python dependencies specification

### Deployment Configuration Files
- `.deployment` - Azure deployment configuration
- `deploy.cmd` - Custom deployment script for Azure
- `runtime.txt` - Python runtime version specification (Python 3.9)

### Data and Static Files
- `Data.csv` - Song assignment data (included in deployment package)
- `static/` - CSS, JavaScript, and other static assets
- `templates/` - Jinja2 HTML templates

## Azure App Service Configuration

### Environment Variables
The application automatically detects Azure App Service environment and configures itself accordingly:

- `WEBSITE_SITE_NAME` - Automatically set by Azure (indicates Azure environment)
- `PORT` - Automatically set by Azure App Service
- `SECRET_KEY` - Should be set in Azure App Service configuration
- `FLASK_ENV` - Set to 'production' in Azure environment

### Recommended Azure App Service Settings

1. **Runtime Stack**: Python 3.9
2. **Startup Command**: `startup.py` (automatically detected)
3. **Always On**: Enabled (to prevent cold starts)
4. **ARR Affinity**: Disabled (for better performance)

## Deployment Methods

### Method 1: Azure Portal Deployment

1. **Create App Service**:
   - Go to Azure Portal
   - Create new App Service
   - Select Python 3.9 runtime stack
   - Choose appropriate pricing tier

2. **Configure Deployment**:
   - Go to Deployment Center
   - Choose deployment source (GitHub, Azure DevOps, etc.)
   - Configure continuous deployment

3. **Set Environment Variables**:
   - Go to Configuration > Application Settings
   - Add `SECRET_KEY` with a secure random value
   - Save configuration

### Method 2: Azure CLI Deployment

```bash
# Create resource group
az group create --name myResourceGroup --location "East US"

# Create App Service plan
az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku B1 --is-linux

# Create web app
az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name myMusicianApp --runtime "PYTHON|3.9"

# Configure startup command
az webapp config set --resource-group myResourceGroup --name myMusicianApp --startup-file startup.py

# Deploy from local Git
az webapp deployment source config-local-git --name myMusicianApp --resource-group myResourceGroup

# Set environment variables
az webapp config appsettings set --resource-group myResourceGroup --name myMusicianApp --settings SECRET_KEY="your-secret-key-here"
```

### Method 3: ZIP Deployment

1. Create a ZIP file containing all application files
2. Use Azure CLI or REST API to deploy:

```bash
az webapp deployment source config-zip --resource-group myResourceGroup --name myMusicianApp --src app.zip
```

## File Structure for Deployment

Ensure your deployment package includes:

```
/
├── startup.py              # Azure startup script
├── app.py                  # Main Flask application
├── csv_data_processor.py   # Data processing module
├── web.config              # IIS configuration
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python version
├── .deployment             # Azure deployment config
├── deploy.cmd              # Deployment script
├── Data.csv                # Song data (CRITICAL - must be included)
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── templates/
    ├── base.html
    └── index.html
```

## Testing Deployment

### Local Testing
Run the deployment test script to verify configuration:

```bash
python3 simple_deployment_test.py
```

### Local Simulation
Test the application locally using the Azure-compatible startup script:

```bash
PORT=5001 python3 startup.py
```

### Post-Deployment Verification

After deployment, verify the following:

1. **Application Loads**: Visit your Azure App Service URL
2. **API Endpoints Work**: Test `/api/songs` and `/api/song/<song_id>`
3. **CSV Data Accessible**: Ensure song data loads correctly
4. **Static Files Served**: Check CSS and JavaScript loading
5. **Responsive Design**: Test on mobile and desktop

## Troubleshooting

### Common Issues

1. **CSV File Not Found**:
   - Ensure `Data.csv` is included in deployment package
   - Check file permissions and encoding

2. **Static Files Not Loading**:
   - Verify `static/` directory structure
   - Check web.config static content configuration

3. **Application Won't Start**:
   - Check Azure App Service logs
   - Verify Python version compatibility
   - Ensure all dependencies in requirements.txt

4. **Performance Issues**:
   - Enable "Always On" in Azure App Service
   - Consider upgrading to higher pricing tier
   - Monitor application insights

### Logging and Monitoring

The application includes comprehensive logging:

- **Startup Logs**: Application initialization and configuration
- **Error Logs**: Detailed error information with stack traces
- **Performance Logs**: Response times and caching information

Access logs through:
- Azure Portal > App Service > Log stream
- Azure Portal > App Service > Advanced Tools (Kudu)
- Application Insights (if configured)

## Security Considerations

1. **Environment Variables**: Store sensitive data in Azure App Service configuration
2. **HTTPS**: Enable HTTPS-only in Azure App Service settings
3. **Authentication**: Consider adding Azure AD authentication if needed
4. **CORS**: Configure CORS settings if accessing from different domains

## Performance Optimization

The application includes several performance optimizations:

1. **Response Caching**: API responses cached for 10 minutes
2. **Static File Caching**: Browser caching headers set
3. **Memory Caching**: In-memory cache for frequently accessed data
4. **Efficient Data Loading**: CSV data loaded once at startup

## Monitoring and Maintenance

1. **Application Insights**: Enable for detailed monitoring
2. **Health Checks**: Monitor `/api/songs` endpoint
3. **Log Analysis**: Regular review of application logs
4. **Performance Metrics**: Monitor response times and error rates

## Support

For deployment issues:
1. Check Azure App Service documentation
2. Review application logs in Azure Portal
3. Test locally using the provided test scripts
4. Verify all required files are included in deployment package