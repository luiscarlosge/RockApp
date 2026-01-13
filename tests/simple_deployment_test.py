#!/usr/bin/env python3
"""
Simple Azure Deployment Test Script
Tests basic file structure and configuration for Azure App Service compatibility.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_file_exists(filepath, description):
    """Check if a required file exists."""
    if os.path.exists(filepath):
        logger.info(f"✓ {description} found: {filepath}")
        return True
    else:
        logger.error(f"✗ {description} missing: {filepath}")
        return False

def check_file_content(filepath, required_content, description):
    """Check if a file contains required content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if required_content in content:
                logger.info(f"✓ {description} contains required content")
                return True
            else:
                logger.error(f"✗ {description} missing required content: {required_content}")
                return False
    except Exception as e:
        logger.error(f"✗ Error reading {filepath}: {e}")
        return False

def main():
    """Main deployment test function."""
    logger.info("Starting Azure deployment compatibility test...")
    
    all_tests_passed = True
    
    # Check required files
    required_files = [
        ('startup.py', 'Startup script'),
        ('app.py', 'Main application'),
        ('web.config', 'Azure web configuration'),
        ('requirements.txt', 'Python dependencies'),
        ('Data.csv', 'CSV data file'),
        ('templates/index.html', 'Main template'),
        ('static/css/style.css', 'CSS stylesheet'),
        ('static/js/app.js', 'JavaScript file'),
        ('.deployment', 'Azure deployment config'),
        ('deploy.cmd', 'Azure deployment script'),
        ('runtime.txt', 'Python runtime specification')
    ]
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_tests_passed = False
    
    # Check file contents
    content_checks = [
        ('startup.py', 'application = create_app()', 'Startup script application factory'),
        ('web.config', 'httpPlatformHandler', 'Web.config HTTP platform handler'),
        ('requirements.txt', 'Flask', 'Requirements.txt Flask dependency'),
        ('runtime.txt', 'python-3.9', 'Runtime.txt Python version'),
        ('.deployment', 'deploy.cmd', 'Deployment config command'),
        ('Data.csv', 'Artist,Song', 'CSV data header')
    ]
    
    for filepath, content, description in content_checks:
        if os.path.exists(filepath):
            if not check_file_content(filepath, content, description):
                all_tests_passed = False
    
    # Check CSV data structure
    try:
        with open('Data.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) > 1:
                logger.info(f"✓ CSV data file contains {len(lines)-1} data rows")
            else:
                logger.error("✗ CSV data file appears to be empty")
                all_tests_passed = False
    except Exception as e:
        logger.error(f"✗ Error reading CSV file: {e}")
        all_tests_passed = False
    
    # Check directory structure
    required_dirs = ['static', 'static/css', 'static/js', 'templates']
    for directory in required_dirs:
        if os.path.isdir(directory):
            logger.info(f"✓ Directory exists: {directory}")
        else:
            logger.error(f"✗ Directory missing: {directory}")
            all_tests_passed = False
    
    # Test basic Python syntax
    try:
        import ast
        
        python_files = ['app.py', 'startup.py', 'csv_data_processor.py']
        for py_file in python_files:
            if os.path.exists(py_file):
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    ast.parse(content)
                    logger.info(f"✓ {py_file} has valid Python syntax")
            
    except SyntaxError as e:
        logger.error(f"✗ Syntax error in {py_file}: {e}")
        all_tests_passed = False
    except Exception as e:
        logger.error(f"✗ Error checking Python syntax: {e}")
        all_tests_passed = False
    
    # Summary
    if all_tests_passed:
        logger.info("🎉 All basic deployment tests passed! Application structure is ready for Azure deployment.")
        logger.info("Next steps:")
        logger.info("1. Install dependencies: pip install -r requirements.txt")
        logger.info("2. Test locally: python startup.py")
        logger.info("3. Deploy to Azure App Service")
        return 0
    else:
        logger.error("❌ Some deployment tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())