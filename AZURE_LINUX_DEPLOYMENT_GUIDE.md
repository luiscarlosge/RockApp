# Azure App Service Linux Deployment Guide

## Rock and Roll Forum Jam en Español - Linux Deployment

This guide provides step-by-step instructions for deploying the Flask-SocketIO application to Azure App Service on Linux.

## Prerequisites

- Azure subscription
- Azure CLI installed (optional)
- The `app.zip` deployment package

## Deployment Package Contents

The `app.zip` file contains:

### Core Application Files
- `app.py` - Main Flask application with SocketIO
- `startup_linux.py` - Linux-optimized startup script
- `gunicorn.conf.py` - Gunicorn configuration for production
- `requirements_linux.txt` - Python dependencies (renamed to requirements.txt in zip)
- `runtime_linux.txt` - Python runtime version (renamed to runtime.txt in zip)

### Python Modules
- `csv_data_processor.py` - Data processing module
- `spanish_translations.py` - Spanish language support
- `global_state_manager.py` - Real-time state management
- `socketio_fallback_config.py` - WebSocket fallback configuration

### Static Assets
- `static/` - CSS, JavaScript, and other static files
- `templates/` - Jinja2 HTML templates

### Configuration Files
- `azure_linux_config.json` - Azure-specific configuration
- `azure_linux_deploy.sh` - Deployment script
- `Dockerfile` - Container configuration (optional)
- `.deployment` - Azure deployment configuration

### Data Files
- `Data.csv` - Song and musician assignment data

## Step 1: Create Azure App Service

### Using Azure Portal

1. **Navigate to Azure Portal** (https://portal.azure.com)

2. **Create a new App Service:**
   - Click "Create a resource"
   - Search for "App Service"
   - Click "Create"

3. **Configure Basic Settings:**
   - **Subscription:** Select your Azure subscription
   - **Resource Group:** Create new or select existing
   - **Name:** Choose a unique name (e.g., `rock-app-linux-[random]`)
   - **Publish:** Code
   - **Runtime stack:** Python 3.11
   - **Operating System:** Linux
   - **Region:** Choose your preferred region

4. **Configure App Service Plan:**
   - Create new or select existing
   - **Pricing tier:** B1 Basic or higher (required for WebSockets)

5. **Review and Create:**
   - Review settings
   - Click "Create"

### Using Azure CLI

```bash
# Create resource group
az group create --name rock-app-rg --location "East US"

# Create App Service plan
az appservice plan create \
  --name rock-app-plan \
  --resource-group rock-app-rg \
  --sku B1 \
  --is-linux

# Create App Service
az webapp create \
  --resource-group rock-app-rg \
  --plan rock-app-plan \
  --name rock-app-linux-unique \
  --runtime "PYTHON|3.11"
```

## Step 2: Configure Application Settings

### Required Application Settings

Navigate to **Configuration > Application settings** and add:

```
FLASK_ENV=production
FLASK_DEBUG=False
WEBSOCKET_ENABLED=true
SOCKETIO_ASYNC_MODE=eventlet
SOCKETIO_PING_TIMEOUT=60
SOCKETIO_PING_INTERVAL=25
SOCKETIO_CORS_ALLOWED_ORIGINS=*
PYTHONPATH=/home/site/wwwroot
```

### Enable WebSockets

1. Go to **Configuration > General settings**
2. Set **Web sockets** to **On**
3. Click **Save**

### Set Startup Command

1. Go to **Configuration > General settings**
2. Set **Startup Command** to:
   ```
   gunicorn --config gunicorn.conf.py startup_linux:application
   ```
3. Click **Save**

## Step 3: Deploy Application

### Method A: Azure CLI Deployment

```bash
az webapp deployment source config-zip \
  --resource-group rock-app-rg \
  --name rock-app-linux-unique \
  --src app.zip
```

### Method B: Azure Portal Deployment

1. **Navigate to Deployment Center:**
   - Go to your App Service in Azure Portal
   - Click "Deployment Center" in the left menu

2. **Configure ZIP Deploy:**
   - Select "ZIP Deploy" as source
   - Click "Browse" and select `app.zip`
   - Click "Deploy"

3. **Monitor Deployment:**
   - Watch the deployment progress
   - Check logs for any errors

### Method C: VS Code Deployment

1. **Install Azure App Service Extension:**
   - Open VS Code
   - Install "Azure App Service" extension

2. **Deploy:**
   - Right-click on `app.zip`
   - Select "Deploy to Web App"
   - Choose your App Service

## Step 4: Verify Deployment

### Check Application Status

1. **Navigate to your App Service URL:**
   ```
   https://your-app-name.azurewebsites.net
   ```

2. **Test API Endpoints:**
   ```
   https://your-app-name.azurewebsites.net/api/health
   https://your-app-name.azurewebsites.net/api/songs
   ```

3. **Test WebSocket Connection:**
   - Open the application in a browser
   - Check browser developer tools for WebSocket connections
   - Test real-time functionality

### Monitor Logs

1. **Enable Application Logging:**
   - Go to **Monitoring > App Service logs**
   - Enable **Application logging (Filesystem)**
   - Set level to **Information**

2. **View Live Logs:**
   - Go to **Monitoring > Log stream**
   - Monitor real-time application logs

3. **Check Deployment Logs:**
   - Go to **Deployment Center**
   - Click on latest deployment
   - View deployment logs

## Step 5: Production Configuration

### Security Settings

1. **HTTPS Only:**
   - Go to **Settings > TLS/SSL settings**
   - Enable **HTTPS Only**

2. **Custom Domain (Optional):**
   - Go to **Settings > Custom domains**
   - Add your custom domain
   - Configure SSL certificate

### Performance Optimization

1. **Enable Application Insights:**
   - Go to **Settings > Application Insights**
   - Enable monitoring
   - Configure alerts

2. **Configure Auto-scaling:**
   - Go to **Settings > Scale out (App Service plan)**
   - Configure scale rules based on CPU/memory

3. **Enable Compression:**
   - Already configured in `gunicorn.conf.py`
   - Verify in **Configuration > General settings**

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

**Symptoms:** 502 Bad Gateway or application timeout

**Solutions:**
- Check **Log stream** for startup errors
- Verify **Startup Command** is correct
- Ensure all dependencies are in `requirements.txt`
- Check Python version matches `runtime.txt`

#### 2. WebSocket Connection Fails

**Symptoms:** Real-time features don't work, WebSocket errors in browser

**Solutions:**
- Verify **Web sockets** are enabled in Configuration
- Check that `eventlet` is installed
- Ensure gunicorn uses `eventlet` worker class
- Test with polling transport first

#### 3. Static Files Not Loading

**Symptoms:** CSS/JS files return 404 errors

**Solutions:**
- Verify static files are in the deployment package
- Check Flask static file configuration
- Ensure proper file permissions

#### 4. Database/CSV File Issues

**Symptoms:** Data not loading, file not found errors

**Solutions:**
- Verify `Data.csv` is in the deployment package
- Check file path in application code
- Ensure proper file permissions

### Debugging Commands

```bash
# Check application logs
az webapp log tail --resource-group rock-app-rg --name rock-app-linux-unique

# SSH into container (if enabled)
az webapp ssh --resource-group rock-app-rg --name rock-app-linux-unique

# Check deployment status
az webapp deployment list --resource-group rock-app-rg --name rock-app-linux-unique
```

### Log Analysis

Common log patterns to look for:

```
# Successful startup
Starting Gunicorn server for Rock App Linux
Worker spawned (pid: XXXX)
Application with SocketIO configured successfully for Linux

# WebSocket issues
WebSocket connection failed
eventlet worker not found

# File not found issues
FileNotFoundError: Data.csv
No such file or directory
```

## Performance Monitoring

### Key Metrics to Monitor

1. **Response Time:** < 2 seconds for API calls
2. **CPU Usage:** < 80% average
3. **Memory Usage:** < 80% of allocated memory
4. **WebSocket Connections:** Monitor concurrent connections
5. **Error Rate:** < 1% of requests

### Setting Up Alerts

1. **Navigate to Application Insights**
2. **Create Alert Rules for:**
   - High response time (> 5 seconds)
   - High error rate (> 5%)
   - High CPU usage (> 90%)
   - Failed WebSocket connections

## Backup and Recovery

### Automated Backups

1. **Enable Backup:**
   - Go to **Settings > Backups**
   - Configure backup schedule
   - Set retention policy

2. **Backup Components:**
   - Application files
   - Configuration settings
   - Data files (if stored in app)

### Disaster Recovery

1. **Deployment Slots:**
   - Use staging slots for testing
   - Implement blue-green deployments
   - Quick rollback capability

2. **Multi-Region Deployment:**
   - Deploy to multiple Azure regions
   - Use Traffic Manager for failover
   - Replicate data across regions

## Scaling Considerations

### Horizontal Scaling

- **Auto-scale Rules:** Based on CPU, memory, or custom metrics
- **Load Balancing:** Automatic with multiple instances
- **Session Affinity:** Disable for better load distribution

### Vertical Scaling

- **App Service Plan Tiers:** Scale up for more CPU/memory
- **Premium Plans:** Better performance and features
- **Isolated Plans:** Dedicated hardware for high-traffic apps

## Security Best Practices

1. **Environment Variables:** Store secrets in Application Settings
2. **HTTPS Only:** Force HTTPS for all connections
3. **CORS Configuration:** Restrict origins in production
4. **Authentication:** Implement if required
5. **Rate Limiting:** Protect against abuse
6. **Security Headers:** Configure appropriate headers

## Maintenance

### Regular Tasks

1. **Update Dependencies:** Keep Python packages updated
2. **Monitor Logs:** Regular log analysis
3. **Performance Review:** Monthly performance analysis
4. **Security Updates:** Apply security patches
5. **Backup Verification:** Test backup restoration

### Update Deployment

To update the application:

1. Create new `app.zip` with updated files
2. Deploy using same method as initial deployment
3. Monitor deployment logs
4. Verify functionality
5. Rollback if issues occur

## Support Resources

- **Azure Documentation:** https://docs.microsoft.com/azure/app-service/
- **Flask-SocketIO Documentation:** https://flask-socketio.readthedocs.io/
- **Gunicorn Documentation:** https://gunicorn.org/
- **Azure Support:** Create support ticket in Azure Portal

## Conclusion

This deployment guide provides comprehensive instructions for deploying the Rock and Roll Forum Jam en Español application to Azure App Service on Linux. Follow the steps carefully and refer to the troubleshooting section if you encounter issues.

For additional support or questions, refer to the Azure documentation or create a support ticket.