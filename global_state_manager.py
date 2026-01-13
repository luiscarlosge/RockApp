"""
Global State Manager for Song Order Enhancement
Manages shared state for global song selection and real-time synchronization.
"""

import time
import logging
from typing import Optional, Dict, Set, Any
from threading import Lock
from flask_socketio import emit
from spanish_translations import get_translation, get_error_message

class GlobalStateManager:
    """
    Manages global song selection state and session synchronization.
    
    This class handles:
    - Shared state management for global song selection
    - Session tracking and management
    - Broadcasting song selection changes
    - Conflict resolution for concurrent updates
    """
    
    def __init__(self):
        """Initialize the global state manager."""
        self.current_song_id: Optional[str] = None
        self.current_song_data: Optional[Dict] = None
        self.connected_sessions: Set[str] = set()
        self.last_update_time: float = 0
        self.last_update_session: Optional[str] = None
        self._lock = Lock()  # Thread safety for concurrent access
        self.logger = logging.getLogger(__name__)
        
        # Session metadata tracking
        self.session_metadata: Dict[str, Dict] = {}
        
        # Conflict resolution settings
        self.conflict_resolution_strategy = "last_write_wins"
        self.max_concurrent_updates = 5
        self.update_timeout = 30  # seconds
        
        self.logger.info("GlobalStateManager initialized")
    
    def add_session(self, session_id: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add a new session to the global state tracking.
        
        Args:
            session_id: Unique session identifier
            metadata: Optional session metadata (user agent, connection time, etc.)
            
        Returns:
            bool: True if session was added successfully
        """
        try:
            with self._lock:
                self.connected_sessions.add(session_id)
                self.session_metadata[session_id] = {
                    'connected_at': time.time(),
                    'last_activity': time.time(),
                    'metadata': metadata or {}
                }
                
                self.logger.info(f"Session added: {session_id}. Total sessions: {len(self.connected_sessions)}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error adding session {session_id}: {str(e)}")
            return False
    
    def remove_session(self, session_id: str) -> bool:
        """
        Remove a session from global state tracking.
        
        Args:
            session_id: Session identifier to remove
            
        Returns:
            bool: True if session was removed successfully
        """
        try:
            with self._lock:
                self.connected_sessions.discard(session_id)
                self.session_metadata.pop(session_id, None)
                
                self.logger.info(f"Session removed: {session_id}. Total sessions: {len(self.connected_sessions)}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error removing session {session_id}: {str(e)}")
            return False
    
    def update_session_activity(self, session_id: str) -> None:
        """
        Update the last activity timestamp for a session.
        
        Args:
            session_id: Session identifier to update
        """
        try:
            with self._lock:
                if session_id in self.session_metadata:
                    self.session_metadata[session_id]['last_activity'] = time.time()
        except Exception as e:
            self.logger.error(f"Error updating session activity {session_id}: {str(e)}")
    
    def update_global_song(self, song_id: str, song_data: Dict, session_id: str) -> Dict[str, Any]:
        """
        Update the global song selection with enhanced conflict resolution and error handling.
        
        Args:
            song_id: ID of the selected song
            song_data: Complete song data including assignments and next song info
            session_id: Session that initiated the update
            
        Returns:
            Dict containing update result and any conflicts
        """
        try:
            current_time = time.time()
            
            with self._lock:
                # Update session activity
                self.update_session_activity(session_id)
                
                # Enhanced conflict detection with timing analysis
                conflict_detected = False
                conflict_type = None
                conflict_severity = 'low'
                
                if (self.last_update_time > 0 and 
                    current_time - self.last_update_time < 2.0 and  # Within 2 seconds
                    self.last_update_session != session_id):
                    
                    conflict_detected = True
                    time_diff = current_time - self.last_update_time
                    
                    if time_diff < 0.5:
                        conflict_type = 'concurrent_rapid'
                        conflict_severity = 'high'
                    elif time_diff < 1.0:
                        conflict_type = 'concurrent_medium'
                        conflict_severity = 'medium'
                    else:
                        conflict_type = 'concurrent_slow'
                        conflict_severity = 'low'
                    
                    self.logger.warning(f"Concurrent update detected: {session_id} vs {self.last_update_session}, "
                                      f"time_diff: {time_diff:.3f}s, severity: {conflict_severity}")
                
                # Apply enhanced conflict resolution strategy
                resolution_applied = None
                if conflict_detected:
                    if self.conflict_resolution_strategy == "last_write_wins":
                        resolution_applied = "last_write_wins"
                        self.logger.info(f"Applying last-write-wins: {session_id} overwrites {self.last_update_session}")
                    elif self.conflict_resolution_strategy == "first_write_wins":
                        # Reject the update if first-write-wins is configured
                        self.logger.info(f"Rejecting update from {session_id} due to first-write-wins policy")
                        return {
                            'success': False,
                            'error': 'Update rejected due to concurrent modification (first-write-wins policy)',
                            'conflict_detected': True,
                            'conflict_type': conflict_type,
                            'conflict_severity': conflict_severity,
                            'resolution_applied': 'first_write_wins_rejection',
                            'session_id': session_id
                        }
                    else:
                        resolution_applied = "default_last_write_wins"
                
                # Validate song data integrity
                if not self._validate_song_data(song_data):
                    self.logger.error(f"Invalid song data provided by session {session_id}")
                    return {
                        'success': False,
                        'error': 'Invalid song data format',
                        'session_id': session_id
                    }
                
                # Create backup of previous state for potential rollback
                previous_state = {
                    'song_id': self.current_song_id,
                    'song_data': self.current_song_data,
                    'update_time': self.last_update_time,
                    'update_session': self.last_update_session
                }
                
                # Update global state
                self.current_song_id = song_id
                self.current_song_data = song_data
                self.last_update_time = current_time
                self.last_update_session = session_id
                
                # Prepare comprehensive result
                result = {
                    'success': True,
                    'previous_song_id': previous_state['song_id'],
                    'new_song_id': song_id,
                    'conflict_detected': conflict_detected,
                    'conflict_type': conflict_type,
                    'conflict_severity': conflict_severity,
                    'resolution_applied': resolution_applied,
                    'update_time': current_time,
                    'session_id': session_id,
                    'state_backup': previous_state
                }
                
                self.logger.info(f"Global song updated to {song_id} by session {session_id}"
                               f"{' (conflict resolved)' if conflict_detected else ''}")
                return result
                
        except Exception as e:
            self.logger.error(f"Error updating global song: {str(e)}")
            return {
                'success': False,
                'error': f'Internal error during update: {str(e)}',
                'error_type': 'internal_error',
                'session_id': session_id
            }
    
    def _validate_song_data(self, song_data: Dict) -> bool:
        """
        Validate song data integrity.
        
        Args:
            song_data: Song data to validate
            
        Returns:
            bool: True if data is valid
        """
        try:
            # Check required fields
            required_fields = ['song_id', 'artist', 'song']
            for field in required_fields:
                if field not in song_data or not song_data[field]:
                    self.logger.warning(f"Missing required field: {field}")
                    return False
            
            # Validate data types
            if not isinstance(song_data.get('assignments', {}), dict):
                self.logger.warning("Invalid assignments format")
                return False
            
            # Additional validation can be added here
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating song data: {str(e)}")
            return False
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current global state.
        
        Returns:
            Dict containing current song selection and session information
        """
        try:
            with self._lock:
                return {
                    'current_song_id': self.current_song_id,
                    'current_song_data': self.current_song_data,
                    'connected_sessions': len(self.connected_sessions),
                    'last_update_time': self.last_update_time,
                    'last_update_session': self.last_update_session,
                    'session_list': list(self.connected_sessions)
                }
        except Exception as e:
            self.logger.error(f"Error getting current state: {str(e)}")
            return {
                'current_song_id': None,
                'current_song_data': None,
                'connected_sessions': 0,
                'error': str(e)
            }
    
    def broadcast_song_change(self, song_id: str, song_data: Dict, exclude_session: Optional[str] = None) -> Dict[str, Any]:
        """
        Broadcast song selection change to all connected sessions with enhanced error handling.
        
        Args:
            song_id: ID of the newly selected song
            song_data: Complete song data to broadcast
            exclude_session: Optional session ID to exclude from broadcast
            
        Returns:
            Dict containing broadcast result information
        """
        try:
            broadcast_data = {
                'song_id': song_id,
                'song_data': song_data,
                'timestamp': time.time(),
                'message': get_translation('song_changed')
            }
            
            successful_broadcasts = 0
            failed_broadcasts = 0
            failed_sessions = []
            broadcast_errors = []
            
            with self._lock:
                target_sessions = self.connected_sessions.copy()
                if exclude_session:
                    target_sessions.discard(exclude_session)
            
            # Enhanced broadcast with individual session error tracking
            for session_id in target_sessions:
                try:
                    # Import here to avoid circular imports
                    from flask_socketio import emit
                    
                    # Attempt broadcast to specific session
                    emit('song_changed', broadcast_data, room=session_id)
                    successful_broadcasts += 1
                    self.logger.debug(f"Broadcasted song change to session {session_id}")
                    
                    # Update session activity on successful broadcast
                    self.update_session_activity(session_id)
                    
                except Exception as broadcast_error:
                    failed_broadcasts += 1
                    failed_sessions.append(session_id)
                    broadcast_errors.append({
                        'session_id': session_id,
                        'error': str(broadcast_error),
                        'error_type': type(broadcast_error).__name__
                    })
                    self.logger.error(f"Failed to broadcast to session {session_id}: {str(broadcast_error)}")
                    
                    # Mark session for potential cleanup if broadcast fails consistently
                    self._mark_session_for_cleanup(session_id, 'broadcast_failure')
            
            # Calculate broadcast success rate
            total_sessions = len(target_sessions)
            success_rate = (successful_broadcasts / total_sessions * 100) if total_sessions > 0 else 100
            
            # Determine overall broadcast status
            broadcast_status = 'success'
            if failed_broadcasts > 0:
                if success_rate < 50:
                    broadcast_status = 'critical_failure'
                elif success_rate < 80:
                    broadcast_status = 'partial_failure'
                else:
                    broadcast_status = 'minor_failure'
            
            result = {
                'success': broadcast_status == 'success',
                'status': broadcast_status,
                'total_sessions': total_sessions,
                'successful_broadcasts': successful_broadcasts,
                'failed_broadcasts': failed_broadcasts,
                'success_rate': success_rate,
                'failed_sessions': failed_sessions,
                'broadcast_errors': broadcast_errors,
                'song_id': song_id,
                'timestamp': time.time()
            }
            
            # Log broadcast results
            if broadcast_status == 'success':
                self.logger.info(f"Broadcast completed successfully: {successful_broadcasts}/{total_sessions} sessions")
            else:
                self.logger.warning(f"Broadcast completed with issues ({broadcast_status}): "
                                  f"{successful_broadcasts}/{total_sessions} sessions successful")
            
            # Trigger cleanup for failed sessions if needed
            if failed_broadcasts > 0:
                self._schedule_failed_session_cleanup(failed_sessions)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Critical error during broadcast: {str(e)}")
            return {
                'success': False,
                'status': 'critical_error',
                'error': str(e),
                'error_type': type(e).__name__,
                'song_id': song_id,
                'timestamp': time.time()
            }
    
    def _mark_session_for_cleanup(self, session_id: str, reason: str):
        """
        Mark a session for potential cleanup due to errors.
        
        Args:
            session_id: Session to mark for cleanup
            reason: Reason for marking (e.g., 'broadcast_failure')
        """
        try:
            if session_id in self.session_metadata:
                if 'cleanup_markers' not in self.session_metadata[session_id]:
                    self.session_metadata[session_id]['cleanup_markers'] = []
                
                self.session_metadata[session_id]['cleanup_markers'].append({
                    'reason': reason,
                    'timestamp': time.time()
                })
                
                # If session has multiple cleanup markers, consider it for removal
                cleanup_count = len(self.session_metadata[session_id]['cleanup_markers'])
                if cleanup_count >= 3:  # 3 strikes rule
                    self.logger.warning(f"Session {session_id} marked for cleanup due to {cleanup_count} failures")
                    
        except Exception as e:
            self.logger.error(f"Error marking session {session_id} for cleanup: {str(e)}")
    
    def _schedule_failed_session_cleanup(self, failed_sessions: list):
        """
        Schedule cleanup for sessions that failed to receive broadcasts.
        
        Args:
            failed_sessions: List of session IDs that failed
        """
        try:
            # In a production environment, this could trigger a background task
            # For now, we'll just log the need for cleanup
            if failed_sessions:
                self.logger.info(f"Scheduling cleanup check for {len(failed_sessions)} failed sessions")
                
                # Could implement actual cleanup scheduling here
                # For example, using a task queue or background thread
                
        except Exception as e:
            self.logger.error(f"Error scheduling session cleanup: {str(e)}")
    
    def cleanup_inactive_sessions(self, timeout_seconds: int = 300) -> int:
        """
        Clean up sessions that have been inactive for too long with enhanced error handling.
        
        Args:
            timeout_seconds: Timeout in seconds for inactive sessions (default: 5 minutes)
            
        Returns:
            int: Number of sessions cleaned up
        """
        try:
            current_time = time.time()
            inactive_sessions = []
            cleanup_reasons = {}
            
            with self._lock:
                for session_id, metadata in self.session_metadata.items():
                    should_cleanup = False
                    cleanup_reason = None
                    
                    # Check for inactivity timeout
                    last_activity = metadata.get('last_activity', 0)
                    if current_time - last_activity > timeout_seconds:
                        should_cleanup = True
                        cleanup_reason = f'inactive_for_{int(current_time - last_activity)}s'
                    
                    # Check for cleanup markers (repeated failures)
                    cleanup_markers = metadata.get('cleanup_markers', [])
                    if len(cleanup_markers) >= 3:
                        should_cleanup = True
                        cleanup_reason = f'multiple_failures_{len(cleanup_markers)}'
                    
                    # Check for stale connections (connected but no recent activity)
                    connected_at = metadata.get('connected_at', current_time)
                    if (current_time - connected_at > 3600 and  # Connected for more than 1 hour
                        current_time - last_activity > 1800):   # No activity for 30 minutes
                        should_cleanup = True
                        cleanup_reason = 'stale_connection'
                    
                    if should_cleanup:
                        inactive_sessions.append(session_id)
                        cleanup_reasons[session_id] = cleanup_reason
                
                # Remove inactive sessions
                for session_id in inactive_sessions:
                    self.connected_sessions.discard(session_id)
                    removed_metadata = self.session_metadata.pop(session_id, None)
                    
                    if removed_metadata:
                        self.logger.info(f"Cleaned up session {session_id}: {cleanup_reasons[session_id]}")
            
            if inactive_sessions:
                self.logger.info(f"Cleaned up {len(inactive_sessions)} inactive sessions")
                
                # Emit cleanup event for monitoring
                try:
                    from flask_socketio import emit
                    emit('session_cleanup', {
                        'cleaned_sessions': len(inactive_sessions),
                        'remaining_sessions': len(self.connected_sessions),
                        'cleanup_reasons': cleanup_reasons,
                        'timestamp': current_time
                    }, room='global_session')
                except Exception as emit_error:
                    self.logger.warning(f"Failed to emit cleanup event: {str(emit_error)}")
            
            return len(inactive_sessions)
            
        except Exception as e:
            self.logger.error(f"Error cleaning up inactive sessions: {str(e)}")
            return 0
    
    def recover_from_error(self, error_type: str, error_context: Dict = None) -> Dict[str, Any]:
        """
        Attempt to recover from various error conditions.
        
        Args:
            error_type: Type of error to recover from
            error_context: Additional context about the error
            
        Returns:
            Dict containing recovery result
        """
        try:
            recovery_actions = []
            recovery_success = False
            
            self.logger.info(f"Attempting recovery from error: {error_type}")
            
            if error_type == 'broadcast_failure':
                # Attempt to recover from broadcast failures
                recovery_actions.append('cleanup_failed_sessions')
                cleaned_count = self.cleanup_inactive_sessions(timeout_seconds=60)  # Shorter timeout for recovery
                
                recovery_actions.append('validate_session_integrity')
                valid_sessions = self._validate_session_integrity()
                
                recovery_success = True
                
            elif error_type == 'state_corruption':
                # Attempt to recover from state corruption
                recovery_actions.append('validate_current_state')
                state_valid = self._validate_current_state()
                
                if not state_valid:
                    recovery_actions.append('reset_to_safe_state')
                    self._reset_to_safe_state()
                
                recovery_success = state_valid or True  # Reset always succeeds
                
            elif error_type == 'session_sync_failure':
                # Attempt to recover from session sync failures
                recovery_actions.append('force_session_resync')
                resync_result = self._force_session_resync()
                
                recovery_success = resync_result.get('success', False)
                
            elif error_type == 'memory_leak':
                # Attempt to recover from memory issues
                recovery_actions.append('cleanup_old_sessions')
                cleaned_count = self.cleanup_inactive_sessions(timeout_seconds=30)
                
                recovery_actions.append('clear_stale_metadata')
                cleared_count = self._clear_stale_metadata()
                
                recovery_success = True
                
            else:
                # Generic recovery
                recovery_actions.append('general_cleanup')
                self.cleanup_inactive_sessions()
                recovery_success = True
            
            result = {
                'success': recovery_success,
                'error_type': error_type,
                'recovery_actions': recovery_actions,
                'timestamp': time.time(),
                'context': error_context or {}
            }
            
            if recovery_success:
                self.logger.info(f"Recovery successful for {error_type}: {recovery_actions}")
            else:
                self.logger.error(f"Recovery failed for {error_type}: {recovery_actions}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during recovery attempt: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': error_type,
                'recovery_actions': [],
                'timestamp': time.time()
            }
    
    def _validate_session_integrity(self) -> int:
        """
        Validate integrity of all sessions and remove invalid ones.
        
        Returns:
            int: Number of valid sessions remaining
        """
        try:
            valid_sessions = set()
            
            with self._lock:
                for session_id in self.connected_sessions.copy():
                    if session_id in self.session_metadata:
                        metadata = self.session_metadata[session_id]
                        
                        # Validate session metadata
                        if (isinstance(metadata, dict) and 
                            'connected_at' in metadata and 
                            'last_activity' in metadata):
                            valid_sessions.add(session_id)
                        else:
                            # Remove invalid session
                            self.connected_sessions.discard(session_id)
                            self.session_metadata.pop(session_id, None)
                            self.logger.warning(f"Removed invalid session: {session_id}")
                    else:
                        # Remove session without metadata
                        self.connected_sessions.discard(session_id)
                        self.logger.warning(f"Removed session without metadata: {session_id}")
            
            return len(valid_sessions)
            
        except Exception as e:
            self.logger.error(f"Error validating session integrity: {str(e)}")
            return 0
    
    def _validate_current_state(self) -> bool:
        """
        Validate the current global state.
        
        Returns:
            bool: True if state is valid
        """
        try:
            # Check if current song data is consistent
            if self.current_song_id and not self.current_song_data:
                self.logger.warning("Current song ID exists but no song data")
                return False
            
            if self.current_song_data and not self.current_song_id:
                self.logger.warning("Current song data exists but no song ID")
                return False
            
            # Validate song data structure if present
            if self.current_song_data:
                required_fields = ['song_id', 'artist', 'song']
                for field in required_fields:
                    if field not in self.current_song_data:
                        self.logger.warning(f"Missing required field in song data: {field}")
                        return False
            
            # Check timestamp consistency
            if self.last_update_time > time.time() + 60:  # Future timestamp (allow 1 minute clock skew)
                self.logger.warning("Last update time is in the future")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating current state: {str(e)}")
            return False
    
    def _reset_to_safe_state(self):
        """
        Reset global state to a safe, consistent state.
        """
        try:
            with self._lock:
                self.current_song_id = None
                self.current_song_data = None
                self.last_update_time = 0
                self.last_update_session = None
            
            self.logger.info("Global state reset to safe state")
            
        except Exception as e:
            self.logger.error(f"Error resetting to safe state: {str(e)}")
    
    def _force_session_resync(self) -> Dict[str, Any]:
        """
        Force resynchronization of all sessions.
        
        Returns:
            Dict containing resync result
        """
        try:
            current_state = self.get_current_state()
            
            # Broadcast current state to all sessions
            from flask_socketio import emit
            
            resync_data = {
                'type': 'force_resync',
                'current_state': current_state,
                'timestamp': time.time()
            }
            
            emit('force_resync', resync_data, room='global_session')
            
            return {
                'success': True,
                'sessions_notified': len(self.connected_sessions),
                'current_state': current_state
            }
            
        except Exception as e:
            self.logger.error(f"Error forcing session resync: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _clear_stale_metadata(self) -> int:
        """
        Clear stale metadata from session tracking.
        
        Returns:
            int: Number of metadata entries cleared
        """
        try:
            cleared_count = 0
            current_time = time.time()
            
            with self._lock:
                # Remove metadata for sessions that are no longer connected
                stale_sessions = []
                for session_id in self.session_metadata.keys():
                    if session_id not in self.connected_sessions:
                        stale_sessions.append(session_id)
                
                for session_id in stale_sessions:
                    self.session_metadata.pop(session_id, None)
                    cleared_count += 1
                
                # Clear old cleanup markers
                for session_id, metadata in self.session_metadata.items():
                    if 'cleanup_markers' in metadata:
                        old_markers = []
                        for marker in metadata['cleanup_markers']:
                            if current_time - marker.get('timestamp', 0) > 3600:  # 1 hour old
                                old_markers.append(marker)
                        
                        for old_marker in old_markers:
                            metadata['cleanup_markers'].remove(old_marker)
                            cleared_count += 1
            
            if cleared_count > 0:
                self.logger.info(f"Cleared {cleared_count} stale metadata entries")
            
            return cleared_count
            
        except Exception as e:
            self.logger.error(f"Error clearing stale metadata: {str(e)}")
            return 0
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get information about a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with session information or None if not found
        """
        try:
            with self._lock:
                if session_id in self.session_metadata:
                    session_info = self.session_metadata[session_id].copy()
                    session_info['is_active'] = session_id in self.connected_sessions
                    return session_info
                return None
        except Exception as e:
            self.logger.error(f"Error getting session info for {session_id}: {str(e)}")
            return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the global state manager.
        
        Returns:
            Dict containing health information
        """
        try:
            with self._lock:
                current_time = time.time()
                
                # Calculate session statistics
                active_sessions = len(self.connected_sessions)
                total_sessions = len(self.session_metadata)
                
                # Check for stale sessions
                stale_sessions = 0
                if self.session_metadata:
                    for metadata in self.session_metadata.values():
                        last_activity = metadata.get('last_activity', 0)
                        if current_time - last_activity > 300:  # 5 minutes
                            stale_sessions += 1
                
                return {
                    'status': 'healthy',
                    'active_sessions': active_sessions,
                    'total_sessions': total_sessions,
                    'stale_sessions': stale_sessions,
                    'current_song_id': self.current_song_id,
                    'last_update_age': current_time - self.last_update_time if self.last_update_time > 0 else None,
                    'uptime': current_time
                }
        except Exception as e:
            self.logger.error(f"Error getting health status: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }