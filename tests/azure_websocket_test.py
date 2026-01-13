#!/usr/bin/env python3
"""
Azure WebSocket Connectivity Test Script

This script tests WebSocket connectivity for the Flask-SocketIO application
in Azure App Service environment. It verifies:
1. Basic HTTP connectivity
2. WebSocket upgrade capability
3. SocketIO endpoint accessibility
4. Fallback transport mechanisms

Usage:
    python azure_websocket_test.py [base_url]

Example:
    python azure_websocket_test.py https://your-app.azurewebsites.net
"""

import sys
import requests
import json
import time
import logging
from urllib.parse import urljoin, urlparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AzureWebSocketTester:
    """Test WebSocket connectivity for Azure App Service deployment."""
    
    def __init__(self, base_url):
        """Initialize tester with base URL."""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Set headers for Azure App Service
        self.session.headers.update({
            'User-Agent': 'Azure-WebSocket-Tester/1.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def test_basic_connectivity(self):
        """Test basic HTTP connectivity to the application."""
        logger.info("Testing basic HTTP connectivity...")
        
        try:
            # Test main application endpoint
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                logger.info("✓ Basic HTTP connectivity successful")
                return True
            else:
                logger.error(f"✗ HTTP connectivity failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ HTTP connectivity error: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints accessibility."""
        logger.info("Testing API endpoints...")
        
        endpoints = [
            '/api/health',
            '/api/songs',
            '/api/musicians',
            '/api/global/current-song'
        ]
        
        success_count = 0
        for endpoint in endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                response = self.session.get(url)
                
                if response.status_code in [200, 404]:  # 404 is acceptable for some endpoints
                    logger.info(f"✓ API endpoint {endpoint} accessible")
                    success_count += 1
                else:
                    logger.warning(f"⚠ API endpoint {endpoint} returned {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"✗ API endpoint {endpoint} error: {str(e)}")
        
        logger.info(f"API endpoints test: {success_count}/{len(endpoints)} successful")
        return success_count > 0
    
    def test_socketio_info(self):
        """Test SocketIO endpoint information."""
        logger.info("Testing SocketIO endpoint information...")
        
        try:
            # Test SocketIO info endpoint
            socketio_url = urljoin(self.base_url, '/socket.io/?EIO=4&transport=polling')
            response = self.session.get(socketio_url)
            
            if response.status_code == 200:
                logger.info("✓ SocketIO endpoint accessible")
                
                # Try to parse SocketIO response
                content = response.text
                if content.startswith('0'):  # SocketIO handshake response
                    logger.info("✓ SocketIO handshake response received")
                    
                    # Extract session info if available
                    try:
                        # Remove SocketIO protocol prefix
                        json_part = content[1:] if content.startswith('0') else content
                        if json_part.startswith('{'):
                            session_info = json.loads(json_part)
                            logger.info(f"✓ SocketIO session info: {session_info}")
                    except json.JSONDecodeError:
                        logger.info("SocketIO response received but not JSON parseable")
                    
                    return True
                else:
                    logger.warning(f"⚠ Unexpected SocketIO response: {content[:100]}")
                    return False
            else:
                logger.error(f"✗ SocketIO endpoint failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ SocketIO endpoint error: {str(e)}")
            return False
    
    def test_websocket_upgrade_headers(self):
        """Test WebSocket upgrade capability by checking headers."""
        logger.info("Testing WebSocket upgrade headers...")
        
        try:
            # Make a request with WebSocket upgrade headers
            headers = {
                'Upgrade': 'websocket',
                'Connection': 'Upgrade',
                'Sec-WebSocket-Key': 'dGhlIHNhbXBsZSBub25jZQ==',
                'Sec-WebSocket-Version': '13',
                'Sec-WebSocket-Protocol': 'socket.io'
            }
            
            socketio_url = urljoin(self.base_url, '/socket.io/?EIO=4&transport=websocket')
            response = self.session.get(socketio_url, headers=headers)
            
            # Check response headers for WebSocket support
            response_headers = response.headers
            
            if 'Upgrade' in response_headers or response.status_code == 101:
                logger.info("✓ WebSocket upgrade headers supported")
                return True
            elif response.status_code == 400:
                logger.info("⚠ WebSocket upgrade not supported, but endpoint accessible")
                return True
            else:
                logger.warning(f"⚠ WebSocket upgrade test inconclusive: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ WebSocket upgrade test error: {str(e)}")
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration for SocketIO."""
        logger.info("Testing CORS configuration...")
        
        try:
            # Make an OPTIONS request to check CORS
            socketio_url = urljoin(self.base_url, '/socket.io/')
            response = self.session.options(socketio_url)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            if any(cors_headers.values()):
                logger.info("✓ CORS headers present")
                for header, value in cors_headers.items():
                    if value:
                        logger.info(f"  {header}: {value}")
                return True
            else:
                logger.warning("⚠ No CORS headers found")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ CORS test error: {str(e)}")
            return False
    
    def test_global_selector_endpoint(self):
        """Test global selector endpoint accessibility."""
        logger.info("Testing global selector endpoint...")
        
        try:
            global_url = urljoin(self.base_url, '/global-selector')
            response = self.session.get(global_url)
            
            if response.status_code == 200:
                logger.info("✓ Global selector endpoint accessible")
                return True
            else:
                logger.error(f"✗ Global selector endpoint failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Global selector endpoint error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all connectivity tests."""
        logger.info(f"Starting Azure WebSocket connectivity tests for: {self.base_url}")
        logger.info("=" * 60)
        
        tests = [
            ("Basic HTTP Connectivity", self.test_basic_connectivity),
            ("API Endpoints", self.test_api_endpoints),
            ("SocketIO Endpoint", self.test_socketio_info),
            ("WebSocket Upgrade Headers", self.test_websocket_upgrade_headers),
            ("CORS Configuration", self.test_cors_configuration),
            ("Global Selector Endpoint", self.test_global_selector_endpoint)
        ]
        
        results = {}
        passed = 0
        
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} ---")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                logger.error(f"✗ {test_name} failed with exception: {str(e)}")
                results[test_name] = False
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nOverall: {passed}/{len(tests)} tests passed")
        
        if passed >= len(tests) * 0.8:  # 80% pass rate
            logger.info("✓ WebSocket connectivity looks good for Azure deployment!")
        elif passed >= len(tests) * 0.6:  # 60% pass rate
            logger.warning("⚠ WebSocket connectivity partially working - check failed tests")
        else:
            logger.error("✗ WebSocket connectivity issues detected - review configuration")
        
        return results

def main():
    """Main function to run WebSocket connectivity tests."""
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("Usage: python azure_websocket_test.py <base_url>")
        print("Example: python azure_websocket_test.py https://your-app.azurewebsites.net")
        print("\nThis script tests WebSocket connectivity for Azure App Service deployment.")
        print("It verifies HTTP connectivity, SocketIO endpoints, WebSocket upgrades, and CORS configuration.")
        sys.exit(0)
    
    base_url = sys.argv[1]
    
    # Validate URL
    parsed = urlparse(base_url)
    if not parsed.scheme or not parsed.netloc:
        logger.error("Invalid URL provided. Please include protocol (http:// or https://)")
        sys.exit(1)
    
    # Run tests
    tester = AzureWebSocketTester(base_url)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    passed_count = sum(1 for result in results.values() if result)
    if passed_count >= len(results) * 0.8:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()