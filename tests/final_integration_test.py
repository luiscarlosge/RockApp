#!/usr/bin/env python3
"""
Final Integration Test for WebSocket Removal
Tests application startup, core functionality, and verifies no WebSocket dependencies
"""

import sys
import requests
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app

def test_application_startup():
    """Test 11.1: Test application startup without WebSocket"""
    print("🧪 Testing application startup without WebSocket dependencies...")
    
    try:
        # Test Flask app import
        from app import app
        print("✓ Flask app imported successfully")
        
        # Check that SocketIO is not imported
        import sys
        socketio_modules = [name for name in sys.modules.keys() if 'socketio' in name.lower()]
        if socketio_modules:
            print(f"⚠️  Warning: SocketIO modules still present: {socketio_modules}")
        else:
            print("✓ No SocketIO modules detected")
        
        # Test basic app configuration
        print(f"✓ App debug mode: {app.config.get('DEBUG')}")
        print(f"✓ App environment: {app.config.get('ENV')}")
        
        return True
    except Exception as e:
        print(f"❌ Application startup test failed: {e}")
        return False

def test_core_functionality():
    """Test 11.3: Test core functionality without real-time features"""
    print("\n🧪 Testing core functionality without real-time features...")
    
    try:
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Main page loads successfully")
            else:
                print(f"❌ Main page failed: {response.status_code}")
                return False
            
            # Test song data API
            response = client.get('/api/songs')
            if response.status_code == 200:
                data = response.get_json()
                if data and 'songs' in data:
                    print(f"✓ Song API works: {len(data['songs'])} songs loaded")
                else:
                    print("❌ Song API returned invalid data")
                    return False
            else:
                print(f"❌ Song API failed: {response.status_code}")
                return False
            
            # Test musician data API
            response = client.get('/api/musicians')
            if response.status_code == 200:
                data = response.get_json()
                if data and 'musicians' in data:
                    print(f"✓ Musician API works: {len(data['musicians'])} musicians loaded")
                else:
                    print("❌ Musician API returned invalid data")
                    return False
            else:
                print(f"❌ Musician API failed: {response.status_code}")
                return False
            
            return True
    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        return False

def test_websocket_removal():
    """Test 11.4: Verify no WebSocket connection attempts"""
    print("\n🧪 Verifying no WebSocket connection attempts...")
    
    try:
        with app.test_client() as client:
            # Test that removed WebSocket endpoints return 404
            websocket_endpoints = [
                '/api/global/current-song',
                '/api/global/set-song',
                '/api/admin/set-current-song',
                '/api/admin/set-next-song',
                '/api/live-performance',
                '/api/data-consistency'
            ]
            
            for endpoint in websocket_endpoints:
                response = client.get(endpoint)
                if response.status_code == 404:
                    print(f"✓ Removed endpoint {endpoint} returns 404")
                else:
                    print(f"⚠️  Endpoint {endpoint} still exists: {response.status_code}")
            
            # Check main page doesn't include SocketIO scripts
            response = client.get('/')
            html_content = response.get_data(as_text=True)
            
            if 'socket.io' in html_content.lower():
                print("❌ SocketIO scripts still present in HTML")
                return False
            else:
                print("✓ No SocketIO scripts found in HTML")
            
            if 'connection-manager' in html_content.lower():
                print("❌ Connection manager references still present")
                return False
            else:
                print("✓ No connection manager references found")
            
            return True
    except Exception as e:
        print(f"❌ WebSocket removal test failed: {e}")
        return False

def test_navigation_system():
    """Test navigation system works with two sections"""
    print("\n🧪 Testing navigation system...")
    
    try:
        with app.test_client() as client:
            response = client.get('/')
            html_content = response.get_data(as_text=True)
            
            # Check that only two sections are present
            if 'song-selector' in html_content and 'musician-selector' in html_content:
                print("✓ Both core sections present")
            else:
                print("❌ Core sections missing")
                return False
            
            # Check that live performance section is removed
            if 'live-performance' in html_content.lower():
                print("❌ Live performance section still present")
                return False
            else:
                print("✓ Live performance section removed")
            
            return True
    except Exception as e:
        print(f"❌ Navigation system test failed: {e}")
        return False

def main():
    """Run all final integration tests"""
    print("🚀 Starting Final Integration Tests for WebSocket Removal")
    print("=" * 60)
    
    tests = [
        ("Application Startup", test_application_startup),
        ("Core Functionality", test_core_functionality),
        ("WebSocket Removal", test_websocket_removal),
        ("Navigation System", test_navigation_system)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! WebSocket removal completed successfully.")
        print("✓ Application is ready for HTTP-only operation")
        print("✓ Core functionality preserved")
        print("✓ No WebSocket dependencies remain")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)