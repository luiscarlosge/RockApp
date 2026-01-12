"""
Live Performance Manager for Rock and Roll Forum Jam en Español

This module handles the state management for live performance tracking,
including current and next song selections with session-based persistence
and comprehensive data consistency validation.
"""

import logging
import time
from typing import Optional, Dict, Any, List, Tuple
from flask import session
from csv_data_processor import CSVDataProcessor


class LivePerformanceManager:
    """
    Manages live performance state including current and next song selections.
    
    Provides session-based persistence for performance state, methods
    for updating and retrieving current performance information, and
    comprehensive data consistency validation across all sections.
    """
    
    def __init__(self, data_processor: CSVDataProcessor):
        """
        Initialize the Live Performance Manager.
        
        Args:
            data_processor: CSVDataProcessor instance for song data access
        """
        self.data_processor = data_processor
        self._session_key_current = 'live_performance_current_song'
        self._session_key_next = 'live_performance_next_song'
        self._session_key_timestamp = 'live_performance_timestamp'
        self._session_key_data_hash = 'live_performance_data_hash'
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Data consistency tracking
        self._last_consistency_check = None
        self._consistency_check_interval = 300  # 5 minutes
        self._data_version_cache = {}
    
    def _get_current_data_hash(self) -> str:
        """
        Get current data hash for consistency checking.
        
        Returns:
            Hash representing current data state
        """
        try:
            health_status = self.data_processor.get_data_health_status()
            return health_status.get("data_integrity_hash", "unknown")
        except Exception as e:
            self.logger.warning(f"Could not get data hash: {str(e)}")
            return "error"
    
    def _validate_data_consistency(self) -> Dict[str, Any]:
        """
        Validate data consistency across all sections.
        
        Returns:
            Dictionary containing consistency validation results
        """
        current_time = time.time()
        
        # Skip if recently checked
        if (self._last_consistency_check and 
            current_time - self._last_consistency_check < self._consistency_check_interval):
            return {"skipped": True, "reason": "recently_checked"}
        
        self._last_consistency_check = current_time
        
        try:
            # Get current data hash
            current_hash = self._get_current_data_hash()
            session_hash = session.get(self._session_key_data_hash)
            
            consistency_results = {
                "timestamp": current_time,
                "data_hash_changed": current_hash != session_hash,
                "current_hash": current_hash,
                "session_hash": session_hash,
                "issues": [],
                "warnings": []
            }
            
            # Update session hash
            session[self._session_key_data_hash] = current_hash
            
            # Validate current and next songs still exist
            current_id = self.get_current_song_id()
            next_id = self.get_next_song_id()
            
            if current_id:
                current_song = self.data_processor.get_song_by_id(current_id)
                if not current_song:
                    consistency_results["issues"].append(f"Current song {current_id} no longer exists")
                    self.set_current_song(None)
                else:
                    # Validate song data integrity
                    song_validation = self._validate_song_data(current_song)
                    if song_validation["issues"]:
                        consistency_results["warnings"].extend(song_validation["issues"])
            
            if next_id:
                next_song = self.data_processor.get_song_by_id(next_id)
                if not next_song:
                    consistency_results["issues"].append(f"Next song {next_id} no longer exists")
                    self.set_next_song(None)
                else:
                    # Validate song data integrity
                    song_validation = self._validate_song_data(next_song)
                    if song_validation["issues"]:
                        consistency_results["warnings"].extend(song_validation["issues"])
            
            # Cross-validate with other sections
            cross_validation = self._cross_validate_with_sections()
            consistency_results.update(cross_validation)
            
            return consistency_results
            
        except Exception as e:
            self.logger.error(f"Error during consistency validation: {str(e)}")
            return {
                "timestamp": current_time,
                "error": str(e),
                "issues": ["Consistency validation failed"]
            }
    
    def _validate_song_data(self, song) -> Dict[str, Any]:
        """
        Validate individual song data integrity.
        
        Args:
            song: Song object to validate
            
        Returns:
            Dictionary containing validation results
        """
        issues = []
        
        # Check required fields
        if not song.artist or not song.song:
            issues.append(f"Song {song.song_id} missing required fields")
        
        if not song.time:
            issues.append(f"Song {song.song_id} missing duration")
        
        # Check musician assignments
        assignments = [song.lead_guitar, song.rhythm_guitar, song.bass, 
                      song.battery, song.singer, song.keyboards]
        assigned_count = sum(1 for assignment in assignments if assignment)
        
        if assigned_count == 0:
            issues.append(f"Song {song.song_id} has no musician assignments")
        
        return {"issues": issues}
    
    def _cross_validate_with_sections(self) -> Dict[str, Any]:
        """
        Cross-validate data consistency with other application sections.
        
        Returns:
            Dictionary containing cross-validation results
        """
        validation_results = {
            "song_selector_consistency": True,
            "musician_selector_consistency": True,
            "cross_section_links": True,
            "issues": []
        }
        
        try:
            # Validate that songs in performance state exist in song selector
            current_id = self.get_current_song_id()
            next_id = self.get_next_song_id()
            
            if current_id:
                songs_list = self.data_processor.get_songs_for_dropdown()
                song_ids = [song["song_id"] for song in songs_list]
                if current_id not in song_ids:
                    validation_results["song_selector_consistency"] = False
                    validation_results["issues"].append(f"Current song {current_id} not in song selector")
            
            if next_id:
                songs_list = self.data_processor.get_songs_for_dropdown()
                song_ids = [song["song_id"] for song in songs_list]
                if next_id not in song_ids:
                    validation_results["song_selector_consistency"] = False
                    validation_results["issues"].append(f"Next song {next_id} not in song selector")
            
            # Validate musician consistency
            if current_id:
                current_song = self.data_processor.get_song_by_id(current_id)
                if current_song:
                    musicians_in_song = self._get_musicians_from_song(current_song)
                    musicians_list = self.data_processor.get_musicians_for_dropdown()
                    available_musicians = [m["id"] for m in musicians_list]
                    
                    for musician in musicians_in_song:
                        if musician not in available_musicians:
                            validation_results["musician_selector_consistency"] = False
                            validation_results["issues"].append(f"Musician {musician} in current song not in musician selector")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error during cross-validation: {str(e)}")
            validation_results["issues"].append(f"Cross-validation error: {str(e)}")
            return validation_results
    
    def _get_musicians_from_song(self, song) -> List[str]:
        """
        Extract all musicians from a song.
        
        Args:
            song: Song object
            
        Returns:
            List of musician names
        """
        musicians = []
        assignments = [song.lead_guitar, song.rhythm_guitar, song.bass, 
                      song.battery, song.singer, song.keyboards]
        
        for assignment in assignments:
            if assignment and assignment.strip():
                musicians.append(assignment.strip())
        
        return musicians
    
    def get_data_consistency_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive data consistency report.
        
        Returns:
            Dictionary containing detailed consistency report
        """
        try:
            # Force consistency check
            self._last_consistency_check = None
            consistency_check = self._validate_data_consistency()
            
            # Get data processor health
            data_health = self.data_processor.get_data_health_status()
            data_consistency = self.data_processor.validate_data_consistency()
            
            # Get performance state
            performance_state = self.get_performance_state()
            
            report = {
                "timestamp": time.time(),
                "overall_status": "healthy",
                "data_processor": {
                    "health": data_health,
                    "consistency": data_consistency
                },
                "live_performance": {
                    "state": performance_state,
                    "consistency": consistency_check
                },
                "cross_validation": consistency_check.get("cross_section_links", True),
                "recommendations": []
            }
            
            # Determine overall status
            issues_count = len(consistency_check.get("issues", []))
            if issues_count > 0:
                report["overall_status"] = "degraded" if issues_count < 3 else "unhealthy"
            
            # Generate recommendations
            if consistency_check.get("data_hash_changed"):
                report["recommendations"].append("Data has changed - consider refreshing all sections")
            
            if not data_consistency.get("is_valid"):
                report["recommendations"].append("Data integrity issues detected - review data source")
            
            if data_health.get("fallback_active"):
                report["recommendations"].append("System is using fallback data - check data source")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating consistency report: {str(e)}")
            return {
                "timestamp": time.time(),
                "overall_status": "error",
                "error": str(e)
            }
    
    def invalidate_cache(self) -> None:
        """
        Invalidate all cached data to force refresh.
        """
        self._data_version_cache.clear()
        self._last_consistency_check = None
        session.pop(self._session_key_data_hash, None)
        self.logger.info("Live performance cache invalidated")
    
    def set_current_song(self, song_id: Optional[str]) -> bool:
        """
        Set the current playing song with data consistency validation.
        
        Args:
            song_id: The unique identifier for the song, or None to clear
            
        Returns:
            True if successfully set, False if song not found
        """
        if song_id is None:
            session[self._session_key_current] = None
            session[self._session_key_timestamp] = time.time()
            self.logger.info("Current song cleared")
            return True
        
        # Validate that the song exists
        song = self.data_processor.get_song_by_id(song_id)
        if song is None:
            self.logger.warning(f"Attempted to set non-existent song as current: {song_id}")
            return False
        
        # Validate song data integrity
        song_validation = self._validate_song_data(song)
        if song_validation["issues"]:
            self.logger.warning(f"Song {song_id} has data issues: {song_validation['issues']}")
        
        session[self._session_key_current] = song_id
        session[self._session_key_timestamp] = time.time()
        session.permanent = True  # Make session persistent
        
        self.logger.info(f"Current song set to: {song_id}")
        
        # Trigger consistency check
        self._validate_data_consistency()
        
        return True
    
    def set_next_song(self, song_id: Optional[str]) -> bool:
        """
        Set the next song in queue with data consistency validation.
        
        Args:
            song_id: The unique identifier for the song, or None to clear
            
        Returns:
            True if successfully set, False if song not found
        """
        if song_id is None:
            session[self._session_key_next] = None
            session[self._session_key_timestamp] = time.time()
            self.logger.info("Next song cleared")
            return True
        
        # Validate that the song exists
        song = self.data_processor.get_song_by_id(song_id)
        if song is None:
            self.logger.warning(f"Attempted to set non-existent song as next: {song_id}")
            return False
        
        # Validate song data integrity
        song_validation = self._validate_song_data(song)
        if song_validation["issues"]:
            self.logger.warning(f"Song {song_id} has data issues: {song_validation['issues']}")
        
        session[self._session_key_next] = song_id
        session[self._session_key_timestamp] = time.time()
        session.permanent = True  # Make session persistent
        
        self.logger.info(f"Next song set to: {song_id}")
        
        # Trigger consistency check
        self._validate_data_consistency()
        
        return True
    
    def get_current_song_id(self) -> Optional[str]:
        """
        Get the current song ID from session.
        
        Returns:
            Current song ID or None if not set
        """
        return session.get(self._session_key_current)
    
    def get_next_song_id(self) -> Optional[str]:
        """
        Get the next song ID from session.
        
        Returns:
            Next song ID or None if not set
        """
        return session.get(self._session_key_next)
    
    def get_current_song_details(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about the current song.
        
        Returns:
            Dictionary with current song details or None if not set
        """
        current_id = self.get_current_song_id()
        if current_id is None:
            return None
        
        song = self.data_processor.get_song_by_id(current_id)
        if song is None:
            # Clean up invalid session data
            self.set_current_song(None)
            return None
        
        return self._format_song_for_performance(song)
    
    def get_next_song_details(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about the next song.
        
        Returns:
            Dictionary with next song details or None if not set
        """
        next_id = self.get_next_song_id()
        if next_id is None:
            return None
        
        song = self.data_processor.get_song_by_id(next_id)
        if song is None:
            # Clean up invalid session data
            self.set_next_song(None)
            return None
        
        return self._format_song_for_performance(song)
    
    def get_performance_state(self) -> Dict[str, Any]:
        """
        Return current performance state with both current and next songs and consistency validation.
        
        Returns:
            Dictionary containing current and next song information with consistency data
        """
        # Perform consistency check
        consistency_check = self._validate_data_consistency()
        
        performance_state = {
            "current_song": self.get_current_song_details(),
            "next_song": self.get_next_song_details(),
            "has_active_performance": self.get_current_song_id() is not None,
            "last_updated": session.get(self._session_key_timestamp),
            "data_consistency": {
                "last_check": consistency_check.get("timestamp"),
                "issues_count": len(consistency_check.get("issues", [])),
                "warnings_count": len(consistency_check.get("warnings", [])),
                "data_hash_changed": consistency_check.get("data_hash_changed", False)
            }
        }
        
        return performance_state
    
    def _format_song_for_performance(self, song) -> Dict[str, Any]:
        """
        Format song data specifically for live performance display.
        
        Args:
            song: Song object to format
            
        Returns:
            Dictionary formatted for performance display with Spanish labels
        """
        # Get the basic song formatting
        formatted = self.data_processor.format_song_display(song)
        
        # Add performance-specific formatting
        musicians = []
        
        # Convert assignments to musician list with Spanish instrument names
        assignments = formatted.get("assignments", {})
        for instrument_en, musician in assignments.items():
            if musician:  # Only include assigned musicians
                # Translate instrument names to Spanish
                instrument_es = self._translate_instrument_to_spanish(instrument_en)
                musicians.append({
                    "name": musician,
                    "instrument": instrument_es,
                    "instrument_en": instrument_en
                })
        
        # Sort musicians by instrument order for consistent display
        instrument_order = {
            "Lead Guitar": 1,
            "Rhythm Guitar": 2, 
            "Bass": 3,
            "Battery": 4,
            "Singer": 5,
            "Keyboards": 6
        }
        
        musicians.sort(key=lambda m: instrument_order.get(m["instrument_en"], 99))
        
        return {
            "id": formatted["song_id"],
            "title": formatted["song"],
            "artist": formatted["artist"],
            "duration": formatted["time"],
            "full_title": f"{formatted['artist']} - {formatted['song']}",
            "musicians": musicians,
            "total_musicians": len(musicians)
        }
    
    def _translate_instrument_to_spanish(self, instrument_en: str) -> str:
        """
        Translate instrument names from English to Spanish.
        
        Args:
            instrument_en: English instrument name
            
        Returns:
            Spanish instrument name
        """
        translations = {
            "Lead Guitar": "Guitarra Principal",
            "Rhythm Guitar": "Guitarra Rítmica", 
            "Bass": "Bajo",
            "Battery": "Batería",
            "Singer": "Voz",
            "Keyboards": "Teclados"
        }
        
        return translations.get(instrument_en, instrument_en)
    
    def clear_performance_state(self) -> None:
        """
        Clear all performance state from session.
        """
        session.pop(self._session_key_current, None)
        session.pop(self._session_key_next, None)
    
    def persist_state(self) -> None:
        """
        Ensure state is persisted to session storage.
        
        This method is called automatically by set methods,
        but can be called explicitly if needed.
        """
        session.permanent = True
        # Flask automatically handles session persistence
        # This method exists for API compatibility
        pass
    
    def validate_state(self) -> Dict[str, bool]:
        """
        Validate current performance state and clean up invalid data with comprehensive consistency checking.
        
        Returns:
            Dictionary indicating validity of current and next song selections and consistency status
        """
        current_valid = True
        next_valid = True
        
        # Check current song
        current_id = self.get_current_song_id()
        if current_id is not None:
            song = self.data_processor.get_song_by_id(current_id)
            if song is None:
                self.set_current_song(None)
                current_valid = False
                self.logger.warning(f"Cleaned up invalid current song: {current_id}")
        
        # Check next song
        next_id = self.get_next_song_id()
        if next_id is not None:
            song = self.data_processor.get_song_by_id(next_id)
            if song is None:
                self.set_next_song(None)
                next_valid = False
                self.logger.warning(f"Cleaned up invalid next song: {next_id}")
        
        # Perform comprehensive consistency check
        consistency_check = self._validate_data_consistency()
        
        return {
            "current_song_valid": current_valid,
            "next_song_valid": next_valid,
            "state_cleaned": not (current_valid and next_valid),
            "consistency_issues": len(consistency_check.get("issues", [])),
            "consistency_warnings": len(consistency_check.get("warnings", [])),
            "data_hash_changed": consistency_check.get("data_hash_changed", False)
        }