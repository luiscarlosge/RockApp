#!/bin/bash

# ============================================
# Quick Fix for Azure Python Command Issue
# Updates the startup command to use python3
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="${1:-rock-app-linux}"
RESOURCE_GROUP="${2:-rock-app-rg}"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Quick Fix: Azure Python Command Issue${NC}"
echo -e "${BLUE}App: $APP_NAME | Resource Group: $RESOURCE_GROUP${NC}"
echo -e "${BLUE}============================================${NC}"

# Function to check Azure CLI
check_azure_cli() {
    if ! command -v az &> /dev/null; then
        echo -e "${RED}❌ Azure CLI not installed${NC}"
        exit 1
    fi
    
    if ! az account show &> /dev/null; then
        echo -e "${RED}❌ Not logged in to Azure${NC}"
        echo "Run: az login"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Azure CLI ready${NC}"
}

# Function to fix startup command
fix_startup_command() {
    echo -e "${BLUE}🔧 Fixing startup command...${NC}"
    
    # Get current startup command
    local current_startup=$(az webapp config show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query appCommandLine -o tsv 2>/dev/null || echo "")
    
    echo "Current startup command: $current_startup"
    
    # Set the correct startup command
    echo "Setting startup command to: python3 startup.py"
    az webapp config set \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --startup-file "python3 startup.py"
    
    echo -e "${GREEN}✅ Startup command updated${NC}"
}

# Function to ensure WebSocket is enabled
enable_websocket() {
    echo -e "${BLUE}🔧 Ensuring WebSocket is enabled...${NC}"
    
    az webapp config set \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --web-sockets-enabled true
    
    echo -e "${GREEN}✅ WebSocket enabled${NC}"
}

# Function to set essential app settings
set_app_settings() {
    echo -e "${BLUE}🔧 Setting essential app settings...${NC}"
    
    az webapp config appsettings set \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --settings \
            FLASK_ENV=production \
            FLASK_DEBUG=False \
            PYTHONPATH=/home/site/wwwroot \
            WEBSITE_WEBSOCKET_ENABLED=true \
            SCM_DO_BUILD_DURING_DEPLOYMENT=true
    
    echo -e "${GREEN}✅ App settings configured${NC}"
}

# Function to restart the app
restart_app() {
    echo -e "${BLUE}🔄 Restarting application...${NC}"
    
    az webapp restart \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP"
    
    echo -e "${GREEN}✅ Application restarted${NC}"
}

# Function to test the fix
test_fix() {
    echo -e "${BLUE}🧪 Testing the fix...${NC}"
    
    local app_url="https://${APP_NAME}.azurewebsites.net"
    
    echo "Waiting 30 seconds for app to start..."
    sleep 30
    
    # Test health endpoint
    echo -n "Testing health endpoint... "
    if curl -f -s --max-time 15 "$app_url/api/health" > /dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${YELLOW}⚠️  Not responding yet${NC}"
    fi
    
    # Test main page
    echo -n "Testing main page... "
    if curl -f -s --max-time 15 "$app_url" > /dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${YELLOW}⚠️  Not responding yet${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Application URL: $app_url${NC}"
}

# Function to show logs
show_logs() {
    echo -e "${BLUE}📋 Recent application logs:${NC}"
    
    az webapp log tail --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --provider application &
    local log_pid=$!
    
    sleep 15
    kill $log_pid 2>/dev/null || true
    
    echo ""
    echo "To continue monitoring logs:"
    echo "az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
}

# Main execution
main() {
    echo -e "${BLUE}Starting quick fix process...${NC}"
    
    check_azure_cli
    fix_startup_command
    enable_websocket
    set_app_settings
    restart_app
    test_fix
    show_logs
    
    echo ""
    echo -e "${GREEN}🎉 Quick fix completed!${NC}"
    echo ""
    echo -e "${BLUE}Summary of changes:${NC}"
    echo "• Startup command: python3 startup.py"
    echo "• WebSocket: Enabled"
    echo "• App settings: Configured for production"
    echo "• Application: Restarted"
    echo ""
    echo -e "${BLUE}If the application still doesn't work:${NC}"
    echo "1. Check logs: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
    echo "2. Try redeploying with the fixed deployment script"
    echo "3. Run the troubleshooting script: ./troubleshoot-azure-linux.sh"
}

# Handle arguments
if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [app-name] [resource-group]"
    echo ""
    echo "Quick fix for Azure App Service Python command issues"
    echo ""
    echo "Arguments:"
    echo "  app-name        Azure App Service name (default: rock-app-linux)"
    echo "  resource-group  Azure Resource Group (default: rock-app-rg)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Use defaults"
    echo "  $0 my-app my-rg                     # Custom names"
    echo ""
    exit 0
fi

# Run main function
main