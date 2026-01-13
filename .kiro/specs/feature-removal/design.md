# Design Document

## Overview

This design outlines the systematic removal of live performance and admin control features from the Rock and Roll Forum Jam en Español application. The removal will simplify the application architecture while preserving all core song and musician selector functionality.

The approach focuses on clean removal with minimal disruption to existing functionality, ensuring the application remains stable and maintainable after the changes.

## Architecture

### Current Architecture
The application currently has three main sections:
1. **Song Selector** - Core functionality for browsing songs and viewing musician assignments
2. **Musician Selector** - Core functionality for browsing musicians and their song assignments  
3. **Live Performance** - Real-time display of current/next songs (TO BE REMOVED)

### Target Architecture
After removal, the application will have a simplified two-section architecture:
1. **Song Selector** - Preserved with all existing functionality
2. **Musician Selector** - Preserved with all existing functionality

### Architectural Changes
- Remove live performance section from the main application layout
- Simplify navigation menu to two sections only
- Remove all live performance backend services and APIs
- Remove admin control panel and related infrastructure
- Maintain existing cross-section navigation between song and musician selectors

## Components and Interfaces

### Frontend Components to Remove

#### JavaScript Classes
- `LivePerformanceManager` class in `static/js/app.js`
- Admin control functionality in `static/js/admin_control.js`
- Enhanced polling manager dependencies for live performance

#### HTML Templates
- `templates/admin_control.html` - Complete removal
- Live performance section in `templates/base.html`
- Navigation menu items for live performance

#### CSS Styles
- Live performance card styles
- Admin control panel styles
- Performance status indicators

### Backend Components to Remove

#### Python Classes
- `LivePerformanceManager` class in `live_performance_manager.py`
- All live performance session management
- Live performance data consistency validation

#### API Endpoints
- `/api/live-performance` - GET endpoint for performance state
- `/api/admin/set-current-song` - POST endpoint for setting current song
- `/api/admin/set-next-song` - POST endpoint for setting next song
- `/admin/control` - Admin control panel route
- All related admin API endpoints

#### Dependencies
- Session-based state management for live performance
- Circuit breaker patterns for live performance APIs
- Live performance data caching

### Components to Preserve

#### Frontend Components
- `MusicianSongSelector` class - Complete preservation
- `MusicianSelector` class - Complete preservation
- `HamburgerMenuSystem` class - Modified to remove live performance navigation
- Cross-section navigation functionality
- Error handling and loading states

#### Backend Components
- All song-related API endpoints (`/api/songs`, `/api/song/<id>`)
- All musician-related API endpoints (`/api/musicians`, `/api/musician/<id>`)
- `CSVDataProcessor` class - Complete preservation
- Core Flask application structure
- Spanish translations system

## Data Models

### No Data Model Changes Required
The removal of live performance features does not require changes to the underlying data models since:
- Song data structure remains unchanged
- Musician data structure remains unchanged
- CSV data processing remains unchanged
- Only session-based live performance state is removed (no persistent data)

### Session Data Cleanup
- Remove live performance session keys
- Clean up any live performance-related session storage
- Maintain existing session functionality for other features

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Converting EARS to Properties

Based on the prework analysis, I'll create properties that validate the key aspects of the feature removal while avoiding redundancy.

**Property 1: Removed endpoints return 404 errors**
*For any* removed live performance or admin control endpoint URL, making an HTTP request should return a 404 status code
**Validates: Requirements 2.1, 2.3, 3.1**

**Property 2: Core functionality preservation**
*For any* song or musician selector operation that worked before removal, the same operation should continue to work correctly after removal
**Validates: Requirements 4.1, 4.2, 4.4, 7.2**

**Property 3: Navigation system functionality**
*For any* valid navigation action between song selector and musician selector, the navigation should work correctly and display the appropriate section
**Validates: Requirements 4.3, 5.3**

**Property 4: Application stability**
*For any* application startup or core operation, the application should run without errors related to removed functionality
**Validates: Requirements 7.1, 7.3**

**Property 5: Live performance polling removal**
*For any* application session, no HTTP requests should be made to live performance endpoints
**Validates: Requirements 1.4**

## Error Handling

### Error Handling Strategy
The removal process must maintain robust error handling for the remaining functionality while cleanly removing error handling for removed features.

#### Preserved Error Handling
- Song API error handling remains unchanged
- Musician API error handling remains unchanged
- Navigation error handling remains unchanged
- General application error handling remains unchanged

#### Removed Error Handling
- Live performance API error handling
- Admin control error handling
- Session-based live performance error recovery
- Live performance polling error handling

#### New Error Handling
- 404 responses for removed endpoints
- Graceful handling of references to removed functionality
- Clean error messages for removed features

### Error Recovery Patterns
- Maintain existing retry mechanisms for song and musician APIs
- Remove retry mechanisms for live performance APIs
- Preserve circuit breaker patterns for remaining functionality
- Remove circuit breaker patterns for removed functionality

## Testing Strategy

### Dual Testing Approach
The testing strategy combines unit tests for specific removal verification and property-based tests for comprehensive functionality validation.

#### Unit Tests
Unit tests will verify specific aspects of the removal:
- Specific files and templates are removed
- Specific API endpoints return 404
- Specific JavaScript classes are undefined
- Specific UI elements are not present
- Application starts without errors

#### Property-Based Tests
Property-based tests will verify universal properties across the system:
- All removed endpoints consistently return 404 errors
- All core functionality continues to work correctly
- Navigation works properly between all valid sections
- Application remains stable under various conditions
- No live performance requests are made during any session

### Property-Based Testing Configuration
- Use Python's `hypothesis` library for property-based testing
- Configure each test to run minimum 100 iterations
- Each property test references its design document property
- Tag format: **Feature: feature-removal, Property {number}: {property_text}**

### Test Categories

#### Removal Verification Tests
- Verify removed files don't exist
- Verify removed API endpoints return 404
- Verify removed UI elements are not present
- Verify removed JavaScript functionality is undefined

#### Functionality Preservation Tests
- Verify song selector works correctly
- Verify musician selector works correctly
- Verify navigation between sections works
- Verify cross-section links work correctly

#### Integration Tests
- Verify application starts successfully
- Verify end-to-end user workflows work
- Verify error handling works correctly
- Verify no live performance requests are made

#### Performance Tests
- Verify application performance is maintained or improved
- Verify memory usage is reduced after removal
- Verify startup time is maintained or improved