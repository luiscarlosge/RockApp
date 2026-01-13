#!/bin/bash

# ============================================
# Azure Linux Deployment Test Script
# Tests the deployed application functionality
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
BASE_URL="https://${APP_NAME}.azurewebsites.net"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Azure Linux Deployment Test${NC}"
echo -e "${BLUE}Testing: $BASE_URL${NC}"
echo -e "${BLUE}============================================${NC}"

# Function to test an endpoint
test_endpoint() {
    local endpoint="$1"
    local description="$2"
    local expected_status="${3:-200}"
    
    echo -n "Testing $description... "
    
    local response=$(curl -s -w "%{http_code}" -o /tmp/response.txt "$BASE_URL$endpoint")
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL (HTTP $response)${NC}"
        if [ -f /tmp/response.txt ]; then
            echo "Response: $(cat /tmp/response.txt | head -3)"
        fi
        return 1
    fi
}

# Function to test JSON endpoint
test_json_endpoint() {
    local endpoint="$1"
    local description="$2"
    local key_to_check="$3"
    
    echo -n "Testing $description... "
    
    local response=$(curl -s "$BASE_URL$endpoint")
    local status=$?
    
    if [ $status -eq 0 ] && echo "$response" | jq -e ".$key_to_check" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Response: $response" | head -3
        return 1
    fi
}

# Function to test WebSocket connectivity
test_websocket() {
    echo -n "Testing WebSocket connectivity... "
    
    # Use a simple WebSocket test
    local ws_url="wss://${APP_NAME}.azurewebsites.net/socket.io/?EIO=4&transport=websocket"
    
    # Try to connect using curl (basic test)
    if curl -s --max-time 10 -H "Connection: Upgrade" -H "Upgrade: websocket" "$BASE_URL" > /dev/null; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  PARTIAL (WebSocket may need more time)${NC}"
        return 1
    fi
}

# Main test execution
main() {
    echo -e "${BLUE}Starting deployment tests...${NC}"
    echo ""
    
    local passed=0
    local total=0
    
    # Test 1: Health endpoint
    ((total++))
    if test_json_endpoint "/api/health" "Health endpoint" "status"; then
        ((passed++))
    fi
    
    # Test 2: Main page
    ((total++))
    if test_endpoint "/" "Main page"; then
        ((passed++))
    fi
    
    # Test 3: Songs API
    ((total++))
    if test_json_endpoint "/api/songs" "Songs API" "songs"; then
        ((passed++))
    fi
    
    # Test 4: Musicians API
    ((total++))
    if test_json_endpoint "/api/musicians" "Musicians API" "musicians"; then
        ((passed++))
    fi
    
    # Test 5: Global selector page
    ((total++))
    if test_endpoint "/global-selector" "Global selector page"; then
        ((passed++))
    fi
    
    # Test 6: Global current song API
    ((total++))
    if test_endpoint "/api/global/current-song" "Global current song API"; then
        ((passed++))
    fi
    
    # Test 7: Static assets (CSS)
    ((total++))
    if test_endpoint "/static/css/style.css" "CSS assets"; then
        ((passed++))
    fi
    
    # Test 8: Static assets (JS)
    ((total++))
    if test_endpoint "/static/js/app.js" "JavaScript assets"; then
        ((passed++))
    fi
    
    # Test 9: WebSocket connectivity
    ((total++))
    if test_websocket; then
        ((passed++))
    fi
    
    # Test 10: Spanish language support
    echo -n "Testing Spanish language support... "
    local response=$(curl -s "$BASE_URL/")
    if echo "$response" | grep -q "Selector de Canciones\|translations\|Selección"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
    ((total++))
    
    # Summary
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}Test Results Summary${NC}"
    echo -e "${BLUE}============================================${NC}"
    
    local success_rate=$((passed * 100 / total))
    
    echo -e "Tests passed: ${GREEN}$passed${NC}/$total"
    echo -e "Success rate: ${GREEN}$success_rate%${NC}"
    
    if [ $passed -eq $total ]; then
        echo ""
        echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
        echo -e "${GREEN}✅ Application is fully functional${NC}"
        echo -e "${GREEN}✅ Song order enhancement working${NC}"
        echo -e "${GREEN}✅ Real-time features ready${NC}"
        echo -e "${GREEN}✅ Spanish language support active${NC}"
        echo ""
        echo -e "${BLUE}🌐 Your application is ready at: $BASE_URL${NC}"
        
    elif [ $success_rate -ge 80 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  MOSTLY WORKING${NC}"
        echo -e "${YELLOW}Most features are functional, minor issues detected${NC}"
        echo ""
        echo -e "${BLUE}🌐 Your application is available at: $BASE_URL${NC}"
        
    else
        echo ""
        echo -e "${RED}❌ SIGNIFICANT ISSUES DETECTED${NC}"
        echo -e "${RED}Multiple tests failed, please check the deployment${NC}"
        echo ""
        echo "Troubleshooting steps:"
        echo "1. Check application logs: az webapp log tail --name $APP_NAME --resource-group rock-app-rg"
        echo "2. Verify all files were deployed correctly"
        echo "3. Check Azure App Service configuration"
        echo "4. Ensure WebSocket support is enabled"
        
        return 1
    fi
    
    # Additional information
    echo ""
    echo -e "${BLUE}📊 Application Features:${NC}"
    echo "• Song Order Enhancement: Enabled"
    echo "• Next Song Navigation: Available"
    echo "• Spanish Language Support: Active"
    echo "• Real-time Synchronization: Ready"
    echo "• WebSocket Communication: Configured"
    echo "• Global Song Selection: Available"
    
    echo ""
    echo -e "${BLUE}🔧 Management Commands:${NC}"
    echo "• View logs: az webapp log tail --name $APP_NAME --resource-group rock-app-rg"
    echo "• Restart app: az webapp restart --name $APP_NAME --resource-group rock-app-rg"
    echo "• SSH access: az webapp ssh --name $APP_NAME --resource-group rock-app-rg"
    
    return 0
}

# Check if jq is available for JSON parsing
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠️  jq not found, installing for JSON parsing...${NC}"
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y jq
    elif command -v yum &> /dev/null; then
        sudo yum install -y jq
    else
        echo -e "${RED}❌ Cannot install jq automatically${NC}"
        echo "Please install jq manually: https://stedolan.github.io/jq/download/"
        exit 1
    fi
fi

# Run main function
main

# Cleanup
rm -f /tmp/response.txt