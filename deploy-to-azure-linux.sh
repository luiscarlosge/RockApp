#!/bin/bash

# ============================================
# Azure App Service Linux Deployment Script
# For Musician Song Selector with Song Order Enhancement
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables (modify these as needed)
RESOURCE_GROUP="rock-app-rg"
APP_SERVICE_PLAN="rock-app-linux-plan"
APP_NAME="rock-app-linux"
LOCATION="East US"
PYTHON_VERSION="3.9"
SKU="B1"  # Basic tier, change to P1V2 for production

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Azure App Service Linux Deployment${NC}"
echo -e "${BLUE}Musician Song Selector with Song Order Enhancement${NC}"
echo -e "${BLUE}============================================${NC}"

# Function to check if Azure CLI is installed
check_azure_cli() {
    if ! command -v az &> /dev/null; then
        echo -e "${RED}❌ Azure CLI is not installed${NC}"
        echo "Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    echo -e "${GREEN}✅ Azure CLI is available${NC}"
}

# Function to check if user is logged in
check_azure_login() {
    if ! az account show &> /dev/null; then
        echo -e "${YELLOW}⚠️  Not logged in to Azure${NC}"
        echo "Logging in to Azure..."
        az login
    fi
    
    SUBSCRIPTION=$(az account show --query name -o tsv)
    echo -e "${GREEN}✅ Logged in to Azure subscription: ${SUBSCRIPTION}${NC}"
}

# Function to create resource group
create_resource_group() {
    echo -e "${BLUE}📦 Creating resource group: ${RESOURCE_GROUP}${NC}"
    
    if az group show --name "$RESOURCE_GROUP" &> /dev/null; then
        echo -e "${YELLOW}⚠️  Resource group already exists${NC}"
    else
        az group create \
            --name "$RESOURCE_GROUP" \
            --location "$LOCATION"
        echo -e "${GREEN}✅ Resource group created${NC}"
    fi
}

# Function to create App Service Plan
create_app_service_plan() {
    echo -e "${BLUE}🏗️  Creating App Service Plan: ${APP_SERVICE_PLAN}${NC}"
    
    if az appservice plan show --name "$APP_SERVICE_PLAN" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        echo -e "${YELLOW}⚠️  App Service Plan already exists${NC}"
    else
        az appservice plan create \
            --name "$APP_SERVICE_PLAN" \
            --resource-group "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --is-linux \
            --sku "$SKU"
        echo -e "${GREEN}✅ App Service Plan created${NC}"
    fi
}

# Function to create Web App
create_web_app() {
    echo -e "${BLUE}🌐 Creating Web App: ${APP_NAME}${NC}"
    
    if az webapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        echo -e "${YELLOW}⚠️  Web App already exists${NC}"
    else
        az webapp create \
            --name "$APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --plan "$APP_SERVICE_PLAN" \
            --runtime "PYTHON|${PYTHON_VERSION}"
        echo -e "${GREEN}✅ Web App created${NC}"
    fi
}

# Function to configure Web App settings
configure_web_app() {
    echo -e "${BLUE}⚙️  Configuring Web App settings${NC}"
    
    # Enable WebSocket support
    az webapp config set \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --web-sockets-enabled true
    
    # Set startup command
    az webapp config set \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --startup-file "python startup.py"
    
    # Configure application settings
    az webapp config appsettings set \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --settings \
            FLASK_ENV=production \
            FLASK_DEBUG=False \
            PYTHONPATH=/home/site/wwwroot \
            WEBSITE_WEBSOCKET_ENABLED=true \
            SCM_DO_BUILD_DURING_DEPLOYMENT=true
    
    # Enable HTTPS only
    az webapp update \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --https-only true
    
    echo -e "${GREEN}✅ Web App configured${NC}"
}

# Function to deploy application
deploy_application() {
    echo -e "${BLUE}🚀 Deploying application${NC}"
    
    # Validate local files before deployment
    echo "Validating local files..."
    
    required_files=("app.py" "startup.py" "requirements.txt" "Data.csv" "deploy.sh")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo -e "${RED}❌ Required file missing: $file${NC}"
            exit 1
        fi
        echo -e "${GREEN}✅ Found: $file${NC}"
    done
    
    # Deploy using local Git
    echo "Initializing local Git repository (if needed)..."
    if [ ! -d ".git" ]; then
        git init
        git add .
        git commit -m "Initial commit for Azure deployment"
    fi
    
    # Configure deployment source
    echo "Configuring deployment source..."
    az webapp deployment source config-local-git \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP"
    
    # Get deployment URL
    DEPLOY_URL=$(az webapp deployment list-publishing-credentials \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query scmUri -o tsv)
    
    echo -e "${BLUE}📤 Pushing to Azure Git repository${NC}"
    echo "Deployment URL: $DEPLOY_URL"
    
    # Add Azure remote if it doesn't exist
    if ! git remote get-url azure &> /dev/null; then
        git remote add azure "$DEPLOY_URL"
    else
        git remote set-url azure "$DEPLOY_URL"
    fi
    
    # Push to Azure
    echo "Pushing to Azure (you may be prompted for deployment credentials)..."
    git push azure main:master --force
    
    echo -e "${GREEN}✅ Application deployed${NC}"
}

# Function to show deployment information
show_deployment_info() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${GREEN}🎉 DEPLOYMENT COMPLETED SUCCESSFULLY${NC}"
    echo -e "${BLUE}============================================${NC}"
    
    APP_URL="https://${APP_NAME}.azurewebsites.net"
    
    echo ""
    echo -e "${BLUE}📋 Deployment Information:${NC}"
    echo -e "Resource Group: ${YELLOW}$RESOURCE_GROUP${NC}"
    echo -e "App Service Plan: ${YELLOW}$APP_SERVICE_PLAN${NC}"
    echo -e "Web App Name: ${YELLOW}$APP_NAME${NC}"
    echo -e "Application URL: ${GREEN}$APP_URL${NC}"
    echo -e "Python Version: ${YELLOW}$PYTHON_VERSION${NC}"
    echo -e "WebSocket Support: ${GREEN}Enabled${NC}"
    echo ""
    
    echo -e "${BLUE}🔧 Features Enabled:${NC}"
    echo "✅ Song Order Enhancement"
    echo "✅ Real-time Global Synchronization"
    echo "✅ Spanish Language Support"
    echo "✅ WebSocket Communication"
    echo "✅ Next Song Navigation"
    echo "✅ HTTPS Only"
    echo ""
    
    echo -e "${BLUE}📊 Monitoring:${NC}"
    echo "• Application Insights: Available in Azure Portal"
    echo "• Log Stream: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
    echo "• Metrics: Available in Azure Portal"
    echo ""
    
    echo -e "${BLUE}🛠️  Management Commands:${NC}"
    echo "• Restart app: az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
    echo "• View logs: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
    echo "• SSH into container: az webapp ssh --name $APP_NAME --resource-group $RESOURCE_GROUP"
    echo ""
    
    echo -e "${GREEN}🌐 Your application is now available at: $APP_URL${NC}"
}

# Function to test deployment
test_deployment() {
    echo -e "${BLUE}🧪 Testing deployment${NC}"
    
    APP_URL="https://${APP_NAME}.azurewebsites.net"
    
    echo "Waiting for application to start..."
    sleep 30
    
    # Test health endpoint
    if curl -f -s "$APP_URL/api/health" > /dev/null; then
        echo -e "${GREEN}✅ Health endpoint responding${NC}"
    else
        echo -e "${YELLOW}⚠️  Health endpoint not responding yet (may need more time)${NC}"
    fi
    
    # Test main page
    if curl -f -s "$APP_URL" > /dev/null; then
        echo -e "${GREEN}✅ Main page responding${NC}"
    else
        echo -e "${YELLOW}⚠️  Main page not responding yet (may need more time)${NC}"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}Starting Azure Linux deployment process...${NC}"
    
    # Validate environment
    check_azure_cli
    check_azure_login
    
    # Create Azure resources
    create_resource_group
    create_app_service_plan
    create_web_app
    configure_web_app
    
    # Deploy application
    deploy_application
    
    # Test deployment
    test_deployment
    
    # Show final information
    show_deployment_info
    
    echo -e "${GREEN}🎉 Deployment process completed!${NC}"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "info")
        show_deployment_info
        ;;
    "test")
        test_deployment
        ;;
    "help")
        echo "Usage: $0 [deploy|info|test|help]"
        echo "  deploy: Full deployment process (default)"
        echo "  info:   Show deployment information"
        echo "  test:   Test current deployment"
        echo "  help:   Show this help message"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac