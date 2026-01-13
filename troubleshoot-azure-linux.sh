#!/bin/bash

# ============================================
# Azure Linux Deployment Troubleshooting Script
# Helps diagnose common deployment issues
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
echo -e "${BLUE}Azure Linux Deployment Troubleshooting${NC}"
echo -e "${BLUE}App: $APP_NAME | Resource Group: $RESOURCE_GROUP${NC}"
echo -e "${BLUE}============================================${NC}"

# Function to check Azure CLI and login
check_azure_setup() {
    echo -e "${BLUE}🔍 Checking Azure CLI setup...${NC}"
    
    if ! command -v az &> /dev/null; then
        echo -e "${RED}❌ Azure CLI not installed${NC}"
        return 1
    fi
    
    if ! az account show &> /dev/null; then
        echo -e "${RED}❌ Not logged in to Azure${NC}"
        echo "Run: az login"
        return 1
    fi
    
    echo -e "${GREEN}✅ Azure CLI setup OK${NC}"
    return 0
}

# Function to check app service status
check_app_service() {
    echo -e "${BLUE}🔍 Checking App Service status...${NC}"
    
    if ! az webapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        echo -e "${RED}❌ App Service not found${NC}"
        return 1
    fi
    
    local state=$(az webapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query state -o tsv)
    echo -e "App Service state: ${GREEN}$state${NC}"
    
    local runtime=$(az webapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query siteConfig.linuxFxVersion -o tsv)
    echo -e "Runtime: ${GREEN}$runtime${NC}"
    
    return 0
}

# Function to check startup command
check_startup_command() {
    echo -e "${BLUE}🔍 Checking startup command...${NC}"
    
    local startup_file=$(az webapp config show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query appCommandLine -o tsv)
    
    if [ -z "$startup_file" ] || [ "$startup_file" = "null" ]; then
        echo -e "${YELLOW}⚠️  No startup command configured${NC}"
        echo "Recommended: python3 startup.py"
        
        read -p "Do you want to set the startup command now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            az webapp config set \
                --name "$APP_NAME" \
                --resource-group "$RESOURCE_GROUP" \
                --startup-file "python3 startup.py"
            echo -e "${GREEN}✅ Startup command set to: python3 startup.py${NC}"
        fi
    else
        echo -e "Startup command: ${GREEN}$startup_file${NC}"
        
        if [[ "$startup_file" == *"python "* ]] && [[ "$startup_file" != *"python3"* ]]; then
            echo -e "${YELLOW}⚠️  Using 'python' instead of 'python3' - this may cause issues${NC}"
            echo "Consider updating to: python3 startup.py"
        fi
    fi
}

# Function to check WebSocket configuration
check_websocket_config() {
    echo -e "${BLUE}🔍 Checking WebSocket configuration...${NC}"
    
    local websocket_enabled=$(az webapp config show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query webSocketsEnabled -o tsv)
    
    if [ "$websocket_enabled" = "true" ]; then
        echo -e "${GREEN}✅ WebSocket enabled${NC}"
    else
        echo -e "${YELLOW}⚠️  WebSocket not enabled${NC}"
        
        read -p "Do you want to enable WebSocket now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            az webapp config set \
                --name "$APP_NAME" \
                --resource-group "$RESOURCE_GROUP" \
                --web-sockets-enabled true
            echo -e "${GREEN}✅ WebSocket enabled${NC}"
        fi
    fi
}

# Function to check application settings
check_app_settings() {
    echo -e "${BLUE}🔍 Checking application settings...${NC}"
    
    local settings=$(az webapp config appsettings list --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" -o table)
    echo "$settings"
    
    # Check for critical settings
    local flask_env=$(az webapp config appsettings list --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query "[?name=='FLASK_ENV'].value" -o tsv)
    local pythonpath=$(az webapp config appsettings list --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query "[?name=='PYTHONPATH'].value" -o tsv)
    
    if [ -z "$flask_env" ]; then
        echo -e "${YELLOW}⚠️  FLASK_ENV not set${NC}"
    fi
    
    if [ -z "$pythonpath" ]; then
        echo -e "${YELLOW}⚠️  PYTHONPATH not set${NC}"
    fi
}

# Function to show recent logs
show_recent_logs() {
    echo -e "${BLUE}🔍 Showing recent application logs...${NC}"
    
    echo "Last 50 log entries:"
    az webapp log tail --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --provider application &
    local log_pid=$!
    
    sleep 10
    kill $log_pid 2>/dev/null || true
    
    echo ""
    echo "To continue monitoring logs, run:"
    echo "az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
}

# Function to check deployment status
check_deployment_status() {
    echo -e "${BLUE}🔍 Checking deployment status...${NC}"
    
    local deployments=$(az webapp deployment list --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query "[0].{status:status,author:author,message:message,receivedTime:receivedTime}" -o table)
    echo "$deployments"
}

# Function to test application endpoints
test_endpoints() {
    echo -e "${BLUE}🔍 Testing application endpoints...${NC}"
    
    local app_url="https://${APP_NAME}.azurewebsites.net"
    
    # Test health endpoint
    echo -n "Testing health endpoint... "
    if curl -f -s --max-time 10 "$app_url/api/health" > /dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
    
    # Test main page
    echo -n "Testing main page... "
    if curl -f -s --max-time 10 "$app_url" > /dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
    
    echo "Application URL: $app_url"
}

# Function to provide common solutions
show_common_solutions() {
    echo -e "${BLUE}🔧 Common Solutions:${NC}"
    echo ""
    
    echo -e "${YELLOW}1. Python command not found:${NC}"
    echo "   - Ensure startup command uses 'python3' not 'python'"
    echo "   - Update startup command: az webapp config set --name $APP_NAME --resource-group $RESOURCE_GROUP --startup-file 'python3 startup.py'"
    echo ""
    
    echo -e "${YELLOW}2. Module import errors:${NC}"
    echo "   - Check that all files were deployed correctly"
    echo "   - Verify requirements.txt includes all dependencies"
    echo "   - Check PYTHONPATH is set to /home/site/wwwroot"
    echo ""
    
    echo -e "${YELLOW}3. WebSocket not working:${NC}"
    echo "   - Enable WebSocket: az webapp config set --name $APP_NAME --resource-group $RESOURCE_GROUP --web-sockets-enabled true"
    echo "   - Check that client connects to correct WebSocket endpoint"
    echo ""
    
    echo -e "${YELLOW}4. Application not starting:${NC}"
    echo "   - Check application logs for detailed error messages"
    echo "   - Verify startup.py exists and is executable"
    echo "   - Ensure all required environment variables are set"
    echo ""
    
    echo -e "${YELLOW}5. Slow startup or timeouts:${NC}"
    echo "   - Consider upgrading to a higher SKU (P1V2 or higher)"
    echo "   - Enable 'Always On' to prevent cold starts"
    echo "   - Check for long-running initialization code"
}

# Main execution
main() {
    echo -e "${BLUE}Starting troubleshooting process...${NC}"
    echo ""
    
    # Run all checks
    check_azure_setup || exit 1
    echo ""
    
    check_app_service
    echo ""
    
    check_startup_command
    echo ""
    
    check_websocket_config
    echo ""
    
    check_app_settings
    echo ""
    
    check_deployment_status
    echo ""
    
    test_endpoints
    echo ""
    
    show_recent_logs
    echo ""
    
    show_common_solutions
    
    echo ""
    echo -e "${GREEN}🎯 Troubleshooting completed!${NC}"
    echo ""
    echo "If issues persist:"
    echo "1. Check the full deployment guide: AZURE_LINUX_DEPLOYMENT_GUIDE.md"
    echo "2. Review Azure App Service documentation"
    echo "3. Contact support with the information gathered above"
}

# Handle script arguments
case "${1:-troubleshoot}" in
    "troubleshoot"|"")
        main
        ;;
    "logs")
        show_recent_logs
        ;;
    "test")
        test_endpoints
        ;;
    "solutions")
        show_common_solutions
        ;;
    "help")
        echo "Usage: $0 [troubleshoot|logs|test|solutions|help] [app-name] [resource-group]"
        echo "  troubleshoot: Run full troubleshooting (default)"
        echo "  logs:         Show recent application logs"
        echo "  test:         Test application endpoints"
        echo "  solutions:    Show common solutions"
        echo "  help:         Show this help message"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac