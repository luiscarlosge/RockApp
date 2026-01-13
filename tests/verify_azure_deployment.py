#!/usr/bin/env python3
"""
Azure Deployment Verification Script

This script verifies that the Flask-SocketIO application is properly
configured for Azure App Service deployment with WebSocket support.

It checks:
1. Configuration files (web.config, requirements.txt)
2. SocketIO configuration in application code
3. Environment variable setup
4. Fallback configuration availability
5. Azure-specific optimizations

Usage:
    python verify_azure_deployment.py
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AzureDeploymentVerifier:
    """Verifies Azure deployment configuration for Flask-SocketIO application."""
    
    def __init__(self):
        """Initialize verifier with current directory as project root."""
        self.project_root = Path.cwd()
        self.issues = []
        self.warnings = []
        self.successes = []
    
    def log_success(self, message):
        """Log a successful check."""
        self.successes.append(message)
        logger.info(f"✓ {message}")
    
    def log_warning(self, message):
        """Log a warning."""
        self.warnings.append(message)
        logger.warning(f"⚠ {message}")
    
    def log_issue(self, message):
        """Log an issue that needs attention."""
        self.issues.append(message)
        logger.error(f"✗ {message}")
    
    def check_web_config(self):
        """Check web.config for WebSocket support."""
        logger.info("Checking web.config configuration...")
        
        web_config_path = self.project_root / 'web.config'
        if not web_config_path.exists():
            self.log_issue("web.config file not found")
            return False
        
        try:
            content = web_config_path.read_text(encoding='utf-8')
            
            # Check for WebSocket support
            websocket_checks = [
                ('<webSocket enabled="true"', "WebSocket enabled in configuration"),
                ('WEBSOCKET_ENABLED', "WebSocket environment variable configured"),
                ('socket\\.io', "SocketIO URL rewrite rules present"),
                ('HTTP_UPGRADE', "WebSocket upgrade handling configured"),
                ('Access-Control-Allow', "CORS headers configured for SocketIO")
            ]
            
            for check_pattern, description in websocket_checks:
                if check_pattern.lower() in content.lower():
                    self.log_success(description)
                else:
                    self.log_warning(f"Missing: {description}")
            
            # Check for Azure-specific configurations
            azure_checks = [
                ('httpPlatform', "HTTP Platform Handler configured"),
                ('requestTimeout', "Request timeout configured"),
                ('processesPerApplication', "Process configuration present"),
                ('requestFiltering', "Request filtering configured")
            ]
            
            for check_pattern, description in azure_checks:
                if check_pattern in content:
                    self.log_success(description)
                else:
                    self.log_warning(f"Missing: {description}")
            
            return True
            
        except Exception as e:
            self.log_issue(f"Error reading web.config: {str(e)}")
            return False
    
    def check_requirements(self):
        """Check requirements.txt for necessary packages."""
        logger.info("Checking requirements.txt...")
        
        requirements_path = self.project_root / 'requirements.txt'
        if not requirements_path.exists():
            self.log_issue("requirements.txt file not found")
            return False
        
        try:
            content = requirements_path.read_text()
            
            required_packages = [
                ('flask-socketio', "Flask-SocketIO package"),
                ('python-socketio', "Python-SocketIO package"),
                ('Flask', "Flask framework"),
                ('gunicorn', "Gunicorn WSGI server")
            ]
            
            for package, description in required_packages:
                if package.lower() in content.lower():
                    self.log_success(f"{description} present")
                else:
                    self.log_issue(f"Missing required package: {package}")
            
            return True
            
        except Exception as e:
            self.log_issue(f"Error reading requirements.txt: {str(e)}")
            return False
    
    def check_application_config(self):
        """Check application configuration files."""
        logger.info("Checking application configuration...")
        
        # Check app.py
        app_py_path = self.project_root / 'app.py'
        if app_py_path.exists():
            try:
                content = app_py_path.read_text()
                
                socketio_checks = [
                    ('from flask_socketio import', "Flask-SocketIO imported"),
                    ('SocketIO(', "SocketIO instance created"),
                    ('async_mode', "Async mode configured"),
                    ('transports', "Transport methods configured"),
                    ('cors_allowed_origins', "CORS configured"),
                    ('@socketio.on', "SocketIO event handlers present")
                ]
                
                for check_pattern, description in socketio_checks:
                    if check_pattern in content:
                        self.log_success(description)
                    else:
                        self.log_warning(f"Missing in app.py: {description}")
                
            except Exception as e:
                self.log_issue(f"Error reading app.py: {str(e)}")
        else:
            self.log_issue("app.py file not found")
        
        # Check startup.py
        startup_py_path = self.project_root / 'startup.py'
        if startup_py_path.exists():
            try:
                content = startup_py_path.read_text()
                
                startup_checks = [
                    ('socketio.run', "SocketIO run configuration"),
                    ('WEBSITE_SITE_NAME', "Azure environment detection"),
                    ('PORT', "Port configuration for Azure"),
                    ('use_reloader=False', "Reloader disabled for production")
                ]
                
                for check_pattern, description in startup_checks:
                    if check_pattern in content:
                        self.log_success(description)
                    else:
                        self.log_warning(f"Missing in startup.py: {description}")
                
            except Exception as e:
                self.log_issue(f"Error reading startup.py: {str(e)}")
        else:
            self.log_issue("startup.py file not found")
    
    def check_fallback_config(self):
        """Check fallback configuration availability."""
        logger.info("Checking fallback configuration...")
        
        fallback_config_path = self.project_root / 'socketio_fallback_config.py'
        if fallback_config_path.exists():
            self.log_success("Fallback configuration file present")
            
            try:
                content = fallback_config_path.read_text()
                
                fallback_checks = [
                    ('get_azure_config', "Azure configuration method"),
                    ('get_restricted_config', "Restricted environment configuration"),
                    ('detect_environment', "Environment detection method"),
                    ('polling', "Polling transport fallback"),
                    ('reconnection', "Reconnection configuration")
                ]
                
                for check_pattern, description in fallback_checks:
                    if check_pattern in content:
                        self.log_success(description)
                    else:
                        self.log_warning(f"Missing in fallback config: {description}")
                
            except Exception as e:
                self.log_issue(f"Error reading fallback config: {str(e)}")
        else:
            self.log_warning("Fallback configuration file not found")
    
    def check_test_scripts(self):
        """Check availability of test scripts."""
        logger.info("Checking test scripts...")
        
        test_scripts = [
            ('azure_websocket_test.py', "Azure WebSocket connectivity test"),
            ('verify_azure_deployment.py', "Deployment verification script")
        ]
        
        for script_name, description in test_scripts:
            script_path = self.project_root / script_name
            if script_path.exists():
                self.log_success(f"{description} available")
            else:
                self.log_warning(f"Missing test script: {script_name}")
    
    def check_environment_variables(self):
        """Check environment variable configuration."""
        logger.info("Checking environment variables...")
        
        # Check current environment
        env_vars = [
            ('FLASK_ENV', "Flask environment"),
            ('PORT', "Port configuration"),
            ('PYTHONPATH', "Python path")
        ]
        
        for var_name, description in env_vars:
            if os.environ.get(var_name):
                self.log_success(f"{description} set: {os.environ[var_name]}")
            else:
                self.log_warning(f"Environment variable not set: {var_name}")
        
        # Check for Azure-specific variables
        azure_vars = [
            ('WEBSITE_SITE_NAME', "Azure App Service detection"),
            ('WEBSOCKET_ENABLED', "WebSocket enablement"),
            ('SOCKETIO_ASYNC_MODE', "SocketIO async mode")
        ]
        
        for var_name, description in azure_vars:
            if os.environ.get(var_name):
                self.log_success(f"Azure variable set: {var_name}")
            else:
                self.log_warning(f"Azure variable not set (will use defaults): {var_name}")
    
    def generate_deployment_checklist(self):
        """Generate a deployment checklist."""
        logger.info("\nGenerating deployment checklist...")
        
        checklist = [
            "1. Upload all files to Azure App Service",
            "2. Ensure web.config is in the root directory",
            "3. Verify requirements.txt includes flask-socketio and python-socketio",
            "4. Set WEBSOCKET_ENABLED=true in Azure App Service Configuration",
            "5. Enable WebSocket in Azure App Service Features",
            "6. Test WebSocket connectivity using azure_websocket_test.py",
            "7. Monitor application logs for SocketIO connection issues",
            "8. Test fallback to polling if WebSocket fails",
            "9. Verify CORS configuration for cross-origin requests",
            "10. Test global song selection functionality"
        ]
        
        logger.info("Deployment Checklist:")
        for item in checklist:
            logger.info(f"  {item}")
    
    def run_verification(self):
        """Run all verification checks."""
        logger.info("Starting Azure deployment verification...")
        logger.info("=" * 60)
        
        # Run all checks
        checks = [
            ("Web.config Configuration", self.check_web_config),
            ("Requirements.txt", self.check_requirements),
            ("Application Configuration", self.check_application_config),
            ("Fallback Configuration", self.check_fallback_config),
            ("Test Scripts", self.check_test_scripts),
            ("Environment Variables", self.check_environment_variables)
        ]
        
        for check_name, check_func in checks:
            logger.info(f"\n--- {check_name} ---")
            try:
                check_func()
            except Exception as e:
                self.log_issue(f"{check_name} failed with exception: {str(e)}")
        
        # Generate summary
        self.generate_summary()
        self.generate_deployment_checklist()
    
    def generate_summary(self):
        """Generate verification summary."""
        logger.info("\n" + "=" * 60)
        logger.info("VERIFICATION SUMMARY")
        logger.info("=" * 60)
        
        logger.info(f"✓ Successful checks: {len(self.successes)}")
        logger.info(f"⚠ Warnings: {len(self.warnings)}")
        logger.info(f"✗ Issues: {len(self.issues)}")
        
        if self.issues:
            logger.info("\nISSUES THAT NEED ATTENTION:")
            for issue in self.issues:
                logger.info(f"  ✗ {issue}")
        
        if self.warnings:
            logger.info("\nWARNINGS:")
            for warning in self.warnings:
                logger.info(f"  ⚠ {warning}")
        
        # Overall assessment
        if not self.issues:
            if len(self.warnings) <= 2:
                logger.info("\n✓ READY FOR AZURE DEPLOYMENT!")
            else:
                logger.info("\n⚠ MOSTLY READY - Review warnings before deployment")
        else:
            logger.info("\n✗ NOT READY - Fix issues before deployment")

def main():
    """Main function to run deployment verification."""
    verifier = AzureDeploymentVerifier()
    verifier.run_verification()
    
    # Exit with appropriate code
    if verifier.issues:
        sys.exit(1)  # Issues found
    else:
        sys.exit(0)  # Ready for deployment

if __name__ == "__main__":
    main()