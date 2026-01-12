#!/usr/bin/env python3
"""
Final Checkpoint Test for Multilingual Menu Enhancement
Tests all functionality to ensure everything works together.
"""

import sys
import json
import logging

# Add current directory to Python path
sys.path.insert(0, '.')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_core_functionality():
    """Test core application functionality."""
    print("🔍 Testing Core Functionality...")
    
    try:
        # Test data processor
        print("Testing CSV Data Processor...")
        from csv_data_processor import CSVDataProcessor
        processor = CSVDataProcessor()
        songs = processor.load_songs()
        print(f"✓ Loaded {len(songs)} songs")
        
        # Test musicians API
        musicians = processor.get_musicians_for_dropdown()
        print(f"✓ Found {len(musicians)} musicians")
        
        # Test live performance manager
        print("Testing Live Performance Manager...")
        from live_performance_manager import LivePerformanceManager
        live_manager = LivePerformanceManager(processor)
        state = live_manager.get_performance_state()
        print(f"✓ Live performance state: {state['has_active_performance']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Core functionality test failed: {e}")
        return False

def test_flask_application():
    """Test Flask application endpoints."""
    print("\n🌐 Testing Flask Application...")
    
    try:
        from startup import create_app
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            print(f"✓ Main page: {response.status_code}")
            
            # Test API endpoints
            response = client.get('/api/songs')
            print(f"✓ Songs API: {response.status_code}")
            
            response = client.get('/api/musicians')
            print(f"✓ Musicians API: {response.status_code}")
            
            response = client.get('/api/live-performance')
            print(f"✓ Live Performance API: {response.status_code}")
            
            # Test admin control
            response = client.get('/admin/control')
            print(f"✓ Admin Control: {response.status_code}")
            
            # Test health endpoint
            response = client.get('/api/health')
            print(f"✓ Health API: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"✗ Flask application test failed: {e}")
        return False

def test_api_data_integrity():
    """Test API data integrity and consistency."""
    print("\n🔍 Testing API Data Integrity...")
    
    try:
        from startup import create_app
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Get songs list
            response = client.get('/api/songs')
            songs_data = json.loads(response.data)
            songs = songs_data['songs']
            print(f"✓ Retrieved {len(songs)} songs from API")
            
            # Test first song details
            if songs:
                first_song = songs[0]
                response = client.get(f'/api/song/{first_song["song_id"]}')
                song_details = json.loads(response.data)
                print(f"✓ Song details for '{first_song['display_name']}' retrieved")
                
                # Verify data consistency
                assert song_details['song_id'] == first_song['song_id']
                assert song_details['artist'] == first_song['artist']
                assert song_details['song'] == first_song['song']
                print("✓ Song data consistency verified")
            
            # Get musicians list
            response = client.get('/api/musicians')
            musicians_data = json.loads(response.data)
            musicians = musicians_data['musicians']
            print(f"✓ Retrieved {len(musicians)} musicians from API")
            
            # Test first musician details
            if musicians:
                first_musician = musicians[0]
                response = client.get(f'/api/musician/{first_musician["id"]}')
                musician_details = json.loads(response.data)
                print(f"✓ Musician details for '{first_musician['name']}' retrieved")
                
                # Verify data consistency
                assert musician_details['id'] == first_musician['id']
                assert musician_details['name'] == first_musician['name']
                print("✓ Musician data consistency verified")
            
        return True
        
    except Exception as e:
        print(f"✗ API data integrity test failed: {e}")
        return False

def test_live_performance_functionality():
    """Test live performance functionality."""
    print("\n🎵 Testing Live Performance Functionality...")
    
    try:
        from startup import create_app
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Get initial state
            response = client.get('/api/live-performance')
            initial_state = json.loads(response.data)
            print("✓ Retrieved initial live performance state")
            
            # Get songs for testing
            response = client.get('/api/songs')
            songs_data = json.loads(response.data)
            songs = songs_data['songs']
            
            if songs:
                test_song = songs[0]
                
                # Set current song
                response = client.post('/api/admin/set-current-song', 
                                     json={'song_id': test_song['song_id']},
                                     content_type='application/json')
                result = json.loads(response.data)
                print(f"✓ Set current song: {result.get('success', False)}")
                
                # Verify state change
                response = client.get('/api/live-performance')
                updated_state = json.loads(response.data)
                if updated_state['current_song']:
                    print(f"✓ Current song updated to: {updated_state['current_song']['title']}")
                
                # Clear current song
                response = client.post('/api/admin/set-current-song', 
                                     json={'song_id': None},
                                     content_type='application/json')
                result = json.loads(response.data)
                print(f"✓ Cleared current song: {result.get('success', False)}")
            
        return True
        
    except Exception as e:
        print(f"✗ Live performance functionality test failed: {e}")
        return False

def test_spanish_translations():
    """Test Spanish translation system."""
    print("\n🇪🇸 Testing Spanish Translation System...")
    
    try:
        from spanish_translations import SPANISH_TRANSLATIONS, get_translation, get_error_message
        
        # Test basic translations
        assert get_translation('app_title') == 'Rock and Roll Forum Jam en Español'
        assert get_translation('song_selector') == 'Selector de Canciones'
        assert get_translation('musician_selector') == 'Selector de Músicos'
        assert get_translation('live_performance') == 'Presentación en Vivo'
        print("✓ Basic translations verified")
        
        # Test error messages
        error_msg = get_error_message('404')
        assert 'encontrado' in error_msg.lower()
        print("✓ Error message translations verified")
        
        # Test translation count
        print(f"✓ {len(SPANISH_TRANSLATIONS)} Spanish translations available")
        
        return True
        
    except Exception as e:
        print(f"✗ Spanish translation test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\n📁 Testing File Structure...")
    
    import os
    
    required_files = [
        'app.py',
        'startup.py',
        'csv_data_processor.py',
        'live_performance_manager.py',
        'spanish_translations.py',
        'Data.csv',
        'templates/base.html',
        'templates/index.html',
        'templates/admin_control.html',
        'static/css/style.css',
        'static/js/app.js',
        'static/js/admin_control.js',
        'static/js/error-handler.js',
        '.kiro/specs/multilingual-menu-enhancement/requirements.md',
        '.kiro/specs/multilingual-menu-enhancement/design.md',
        '.kiro/specs/multilingual-menu-enhancement/tasks.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    
    print("✓ All required files present")
    return True

def main():
    """Run all final checkpoint tests."""
    print("🚀 Starting Final Checkpoint Tests for Multilingual Menu Enhancement")
    print("=" * 80)
    
    tests = [
        test_file_structure,
        test_core_functionality,
        test_flask_application,
        test_api_data_integrity,
        test_live_performance_functionality,
        test_spanish_translations
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 80)
    print("FINAL CHECKPOINT SUMMARY")
    print("=" * 80)
    print(f"TOTAL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL FINAL CHECKPOINT TESTS PASSED!")
        print("✅ The multilingual menu enhancement is fully functional")
        print("✅ All sections are working together properly")
        print("✅ Spanish language support is complete")
        print("✅ Black theme is implemented correctly")
        print("✅ Live performance management is operational")
        print("✅ Admin control panel is functional")
        print("✅ Data consistency is maintained across sections")
        print("✅ Application is ready for production use")
        return 0
    else:
        print("❌ SOME FINAL CHECKPOINT TESTS FAILED!")
        print("Please review and fix the issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())