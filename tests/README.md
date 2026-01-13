# Tests Directory

This directory contains all test files for the Rock and Roll Forum application.

## Test Files

### Integration Tests
- `integration_test.py` - Comprehensive integration tests for song order enhancement
- `test_complete_workflows.py` - End-to-end user workflow tests
- `final_integration_test.py` - Final integration tests for WebSocket removal

### Unit Tests
- `simple_test.py` - Simple functionality verification tests
- `test_socketio_integration.py` - SocketIO integration tests

### Deployment Tests
- `simple_deployment_test.py` - Azure deployment compatibility tests
- `azure_websocket_test.py` - Azure WebSocket connectivity tests
- `test-azure-linux-deployment.sh` - Azure Linux deployment test script

## Running Tests

### Python Tests
```bash
# Run all Python tests
python -m pytest tests/

# Run specific test file
python tests/test_complete_workflows.py
python tests/integration_test.py
python tests/simple_test.py
```

### Shell Script Tests
```bash
# Make executable and run
chmod +x tests/test-azure-linux-deployment.sh
./tests/test-azure-linux-deployment.sh your-app-name
```

## Test Categories

### 1. Functionality Tests
- Core application features
- API endpoints
- Data processing
- Spanish language support

### 2. Integration Tests
- Component interaction
- End-to-end workflows
- Error handling
- Performance requirements

### 3. Deployment Tests
- Azure App Service compatibility
- File structure validation
- Configuration verification
- WebSocket connectivity

## Test Requirements

Most tests require the application to be running or importable. Ensure you have:
- Python dependencies installed (`pip install -r requirements.txt`)
- Application files in the parent directory
- Test data (Data.csv) available

## Continuous Integration

These tests are designed to be run in CI/CD pipelines and provide comprehensive coverage of the application's functionality and deployment readiness.