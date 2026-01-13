# Implementation Plan: Feature Removal

## Overview

This implementation plan systematically removes live performance and admin control features while preserving all core song and musician selector functionality. Based on analysis of the current codebase, all targeted components are present and need to be removed in the specified order to minimize risk.

## Tasks

- [x] 1. Remove admin control functionality
- [x] 1.1 Remove admin control template and route
  - Delete `templates/admin_control.html` file
  - Remove `/admin/control` route from `app.py`
  - _Requirements: 2.1, 2.2_

- [x] 1.2 Remove admin control JavaScript
  - Delete `static/js/admin_control.js` file
  - _Requirements: 2.4, 6.1_

- [x] 1.3 Remove admin API endpoints
  - Remove `/api/admin/set-current-song` endpoint from `app.py`
  - Remove `/api/admin/set-next-song` endpoint from `app.py`
  - Remove `/api/admin/clear-errors` endpoint from `app.py`
  - Remove `/api/admin/invalidate-cache` endpoint from `app.py`
  - _Requirements: 2.3_

- [ ]* 1.4 Write property test for admin endpoint removal
  - **Property 1: Removed endpoints return 404 errors**
  - **Validates: Requirements 2.1, 2.3, 3.1**

- [x] 2. Remove live performance backend services
- [x] 2.1 Remove LivePerformanceManager class and imports
  - Delete `live_performance_manager.py` file
  - Remove `from live_performance_manager import LivePerformanceManager` from `app.py`
  - Remove `live_performance_manager = LivePerformanceManager(data_processor)` initialization
  - _Requirements: 3.2, 6.3_

- [x] 2.2 Remove live performance API endpoints
  - Remove `/api/live-performance` endpoint from `app.py`
  - Remove `/api/data-consistency` endpoint from `app.py`
  - _Requirements: 3.1_

- [x] 2.3 Remove live performance session management
  - Remove session configuration for live performance from `app.py`
  - Remove session-based state management code
  - _Requirements: 3.3_

- [ ]* 2.4 Write property test for live performance endpoint removal
  - **Property 1: Removed endpoints return 404 errors**
  - **Validates: Requirements 2.1, 2.3, 3.1**

- [x] 3. Remove live performance frontend components
- [x] 3.1 Remove LivePerformanceManager JavaScript class
  - Remove LivePerformanceManager class from `static/js/app.js` (lines 1576-1919)
  - Remove live performance initialization code from main app initialization
  - _Requirements: 1.3, 6.1_

- [x] 3.2 Remove enhanced polling manager dependencies
  - Remove enhanced polling manager script reference from `templates/base.html`
  - Delete `static/js/enhanced-polling-manager.js` file
  - _Requirements: 1.4, 6.1_

- [x] 3.3 Remove live performance UI elements
  - Remove live performance section from `templates/base.html` (lines 95-150 approximately)
  - Remove live performance navigation menu item from hamburger menu
  - _Requirements: 1.1, 1.2, 1.3_

- [ ]* 3.4 Write property test for live performance polling removal
  - **Property 5: Live performance polling removal**
  - **Validates: Requirements 1.4**

- [x] 4. Update navigation system
- [x] 4.1 Update HamburgerMenuSystem class
  - Remove live performance section from navigation logic in `static/js/app.js`
  - Update section initialization to handle only two sections (song-selector, musician-selector)
  - Remove live performance references from keyboard shortcuts (Alt+3)
  - _Requirements: 5.1, 5.2_

- [x] 4.2 Update navigation menu HTML
  - Remove live performance menu item from hamburger menu in `templates/base.html`
  - Update menu accessibility attributes for two-section navigation
  - _Requirements: 5.1, 5.2, 5.4_

- [ ]* 4.3 Write property test for navigation functionality
  - **Property 3: Navigation system functionality**
  - **Validates: Requirements 4.3, 5.3**

- [x] 5. Clean up unused dependencies and styles
- [x] 5.1 Remove unused CSS styles
  - Remove live performance card styles from `static/css/style.css`
  - Remove admin control panel styles
  - _Requirements: 6.2_

- [x] 5.2 Clean up Python imports and variables
  - Remove unused imports from `app.py` (LivePerformanceManager)
  - Remove live performance related global variables and error handling
  - Clean up circuit breaker references for removed endpoints
  - _Requirements: 6.3_

- [x] 5.3 Remove unused HTML template sections
  - Clean up any remaining live performance template references
  - Remove unused template blocks and script references
  - _Requirements: 6.4_

- [x] 6. Verify core functionality preservation
- [x] 6.1 Test song selector functionality
  - Verify song loading works correctly
  - Verify song details display works correctly
  - Verify cross-section navigation to musician selector works
  - _Requirements: 4.1_

- [ ]* 6.2 Write property test for core functionality preservation
  - **Property 2: Core functionality preservation**
  - **Validates: Requirements 4.1, 4.2, 4.4, 7.2**

- [x] 6.3 Test musician selector functionality
  - Verify musician loading works correctly
  - Verify musician details display works correctly
  - Verify cross-section navigation to song selector works
  - _Requirements: 4.2_

- [x] 6.4 Test navigation between sections
  - Verify hamburger menu works correctly with two sections
  - Verify section switching works correctly
  - Verify keyboard navigation works correctly (Alt+1, Alt+2, Alt+m)
  - _Requirements: 4.3_

- [x] 7. Final integration and stability testing
- [x] 7.1 Test application startup
  - Verify application starts without errors
  - Verify no live performance related errors in logs
  - Verify no import errors for removed modules
  - _Requirements: 7.1_

- [ ]* 7.2 Write property test for application stability
  - **Property 4: Application stability**
  - **Validates: Requirements 7.1, 7.3**

- [x] 7.3 Run existing test suite
  - Run all existing tests for song and musician functionality
  - Verify all tests pass after removal
  - _Requirements: 7.4_

- [x] 7.4 Perform end-to-end testing
  - Test complete user workflows
  - Verify error handling works correctly
  - Verify application performance is maintained
  - _Requirements: 7.2, 7.3_

- [ ] 8. Final checkpoint - Ensure all tests pass
- Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster implementation
- Each task references specific requirements for traceability
- The order of tasks minimizes risk by removing backend services before frontend components
- Core functionality testing ensures no regressions are introduced
- Property tests validate universal correctness properties
- Unit tests validate specific removal requirements
- All targeted files and components have been verified to exist in the current codebase
- Test Azure App Repo