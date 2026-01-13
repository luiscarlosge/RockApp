"""
CSV Data Processor for Musician Song Selector

This module handles loading, parsing, and processing of song assignment data
from CSV files. It provides methods for data caching, retrieval, and formatting
for frontend consumption with comprehensive error handling and retry mechanisms.
"""

import csv
import re
import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from functools import wraps


def retry_on_failure(max_attempts=3, delay=1.0, backoff_factor=2.0):
    """
    Decorator to retry operations on failure with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Factor to multiply delay by after each failure
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logging.error(f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}")
            
            raise last_exception
        return wrapper
    return decorator


@dataclass
class Song:
    """Data class representing a song with musician assignments."""
    artist: str
    song: str
    lead_guitar: Optional[str]
    rhythm_guitar: Optional[str]
    bass: Optional[str]
    battery: Optional[str]  # Drums
    singer: Optional[str]
    keyboards: Optional[str]
    time: str
    song_id: str  # Generated unique identifier


@dataclass
class OrderedSong(Song):
    """Data class representing a song with order information and musician assignments."""
    order: int
    next_song_id: Optional[str] = None
    previous_song_id: Optional[str] = None


class CSVDataProcessor:
    """
    Processes CSV data containing song assignments and musician information.
    
    Handles loading, parsing, caching, and formatting of song data for
    the musician song selector application with comprehensive error handling,
    retry mechanisms, and data consistency validation.
    """
    
    def __init__(self, csv_file_path: str = "Data.csv"):
        """
        Initialize the CSV data processor.
        
        Args:
            csv_file_path: Path to the CSV file containing song data
        """
        self.csv_file_path = csv_file_path
        self._songs_cache: List[OrderedSong] = []
        self._songs_by_id: Dict[str, OrderedSong] = {}
        self._songs_by_order: Dict[int, OrderedSong] = {}
        self._dropdown_cache: List[Dict] = []
        self._data_loaded = False
        self._last_modified_time = None
        self._cache_timestamp = None
        self._data_integrity_hash = None
        self._fallback_data = None
        self._error_count = 0
        self._max_error_threshold = 5
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    def _calculate_data_hash(self, data: List[OrderedSong]) -> str:
        """
        Calculate a hash of the data for integrity checking.
        
        Args:
            data: List of OrderedSong objects
            
        Returns:
            Hash string representing the data
        """
        import hashlib
        data_str = str(sorted([(s.song_id, s.artist, s.song, s.order) for s in data]))
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _validate_data_integrity(self, data: List[OrderedSong]) -> Tuple[bool, List[str]]:
        """
        Validate data integrity and consistency.
        
        Args:
            data: List of OrderedSong objects to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for duplicate song IDs
        song_ids = [song.song_id for song in data]
        if len(song_ids) != len(set(song_ids)):
            duplicates = [sid for sid in set(song_ids) if song_ids.count(sid) > 1]
            issues.append(f"Duplicate song IDs found: {duplicates}")
        
        # Check for duplicate order values
        orders = [song.order for song in data if song.order is not None]
        if len(orders) != len(set(orders)):
            duplicates = [order for order in set(orders) if orders.count(order) > 1]
            issues.append(f"Duplicate order values found: {duplicates}")
        
        # Check for empty required fields
        for song in data:
            if not song.artist or not song.song:
                issues.append(f"Missing artist or song title for ID: {song.song_id}")
            if not song.time:
                issues.append(f"Missing duration for song: {song.song_id}")
            if song.order is None or song.order < 0:
                issues.append(f"Invalid order value for song: {song.song_id}")
        
        # Check for data consistency across musicians
        all_musicians = set()
        for song in data:
            for instrument_assignment in [song.lead_guitar, song.rhythm_guitar, 
                                        song.bass, song.battery, song.singer, song.keyboards]:
                if instrument_assignment:
                    all_musicians.add(instrument_assignment.strip())
        
        # Validate musician name consistency (no obvious typos)
        musician_list = list(all_musicians)
        for i, musician1 in enumerate(musician_list):
            for musician2 in musician_list[i+1:]:
                # Simple similarity check for potential typos
                if self._are_names_similar(musician1, musician2):
                    issues.append(f"Potential name inconsistency: '{musician1}' vs '{musician2}'")
        
        return len(issues) == 0, issues
    
    def _are_names_similar(self, name1: str, name2: str, threshold: float = 0.8) -> bool:
        """
        Check if two names are suspiciously similar (potential typos).
        
        Args:
            name1: First name to compare
            name2: Second name to compare
            threshold: Similarity threshold (0-1)
            
        Returns:
            True if names are suspiciously similar
        """
        # Simple Levenshtein distance approximation
        if abs(len(name1) - len(name2)) > 2:
            return False
        
        # Convert to lowercase for comparison
        n1, n2 = name1.lower(), name2.lower()
        
        # If one is a substring of the other, they might be similar
        if n1 in n2 or n2 in n1:
            return len(n1) > 3 and len(n2) > 3  # Only flag if names are substantial
        
        # Simple character overlap check
        common_chars = set(n1) & set(n2)
        total_chars = set(n1) | set(n2)
        
        if len(total_chars) == 0:
            return False
        
        similarity = len(common_chars) / len(total_chars)
        return similarity > threshold and abs(len(n1) - len(n2)) <= 1
    
    def _create_fallback_data(self) -> List[OrderedSong]:
        """
        Create minimal fallback data in case of complete data failure.
        
        Returns:
            List of minimal OrderedSong objects for fallback
        """
        return [
            OrderedSong(
                artist="Sistema",
                song="Datos no disponibles",
                lead_guitar=None,
                rhythm_guitar=None,
                bass=None,
                battery=None,
                singer=None,
                keyboards=None,
                time="0:00",
                song_id="fallback-no-data",
                order=1
            )
        ]
    
    def _handle_data_error(self, error: Exception, operation: str):
        """
        Handle data-related errors with appropriate logging and fallback.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
        """
        self._error_count += 1
        self.logger.error(f"Data error in {operation}: {str(error)}")
        
        if self._error_count >= self._max_error_threshold:
            self.logger.critical(f"Error threshold exceeded ({self._max_error_threshold}). Activating fallback mode.")
            if not self._fallback_data:
                self._fallback_data = self._create_fallback_data()
    
    def _recover_from_cache(self) -> bool:
        """
        Attempt to recover from cached data if available.
        
        Returns:
            True if recovery was successful, False otherwise
        """
        if self._songs_cache and len(self._songs_cache) > 0:
            self.logger.info("Recovering from cached data")
            return True
        return False
    
    def _is_cache_valid(self) -> bool:
        """
        Check if the current cache is still valid based on file modification time.
        
        Returns:
            True if cache is valid, False if needs refresh
        """
        try:
            import os
            current_mtime = os.path.getmtime(self.csv_file_path)
            return (self._last_modified_time is not None and 
                    current_mtime == self._last_modified_time and
                    self._data_loaded)
        except (OSError, FileNotFoundError):
            return False
    
    def _update_cache_timestamp(self):
        """Update the cache timestamp and file modification time."""
        try:
            import os
            self._last_modified_time = os.path.getmtime(self.csv_file_path)
            self._cache_timestamp = time.time()
        except (OSError, FileNotFoundError):
            self._last_modified_time = None
            self._cache_timestamp = None
    
    def _generate_song_id(self, artist: str, song: str) -> str:
        """
        Generate a unique song ID from artist and song name.
        
        Args:
            artist: The artist name
            song: The song title
            
        Returns:
            A URL-friendly unique identifier for the song
        """
        # Combine artist and song, convert to lowercase
        combined = f"{artist}-{song}".lower()
        
        # Replace spaces and special characters with hyphens
        song_id = re.sub(r'[^a-z0-9]+', '-', combined)
        
        # Remove leading/trailing hyphens and multiple consecutive hyphens
        song_id = re.sub(r'^-+|-+$', '', song_id)
        song_id = re.sub(r'-+', '-', song_id)
        
        return song_id
        """
        Generate a unique song ID from artist and song name.
        
        Args:
            artist: The artist name
            song: The song title
            
        Returns:
            A URL-friendly unique identifier for the song
        """
        # Combine artist and song, convert to lowercase
        combined = f"{artist}-{song}".lower()
        
        # Replace spaces and special characters with hyphens
        song_id = re.sub(r'[^a-z0-9]+', '-', combined)
        
        # Remove leading/trailing hyphens and multiple consecutive hyphens
        song_id = re.sub(r'^-+|-+$', '', song_id)
        song_id = re.sub(r'-+', '-', song_id)
        
        return song_id
    
    def _clean_assignment(self, assignment: str) -> Optional[str]:
        """
        Clean and validate musician assignment data.
        
        Args:
            assignment: Raw assignment string from CSV
            
        Returns:
            Cleaned assignment string or None if empty/invalid
        """
        if assignment is None or assignment == "" or str(assignment).strip() == "":
            return None
        return str(assignment).strip()
    
    def _parse_order_value(self, order_value: str, default_order: int) -> int:
        """
        Parse and validate order value from CSV.
        
        Args:
            order_value: Raw order value from CSV
            default_order: Default order to use if parsing fails
            
        Returns:
            Valid integer order value
        """
        if order_value is None or str(order_value).strip() == "":
            return default_order
        
        try:
            parsed_order = int(float(str(order_value).strip()))
            if parsed_order <= 0:
                self.logger.warning(f"Invalid order value {parsed_order}, using default {default_order}")
                return default_order
            return parsed_order
        except (ValueError, TypeError):
            self.logger.warning(f"Could not parse order value '{order_value}', using default {default_order}")
            return default_order
    
    @retry_on_failure(max_attempts=3, delay=0.5)
    def load_songs(self) -> List[OrderedSong]:
        """
        Load and parse songs from the CSV file with intelligent caching,
        comprehensive error handling, and data integrity validation.
        
        Returns:
            List of OrderedSong objects loaded from the CSV file
            
        Raises:
            FileNotFoundError: If the CSV file cannot be found
            ValueError: If the CSV file is empty or malformed
            Exception: For other unexpected errors
        """
        # Check if cache is still valid
        if self._is_cache_valid():
            return self._songs_cache.copy()
        
        try:
            # Clear existing cache
            self._songs_cache.clear()
            self._songs_by_id.clear()
            self._songs_by_order.clear()
            self._dropdown_cache.clear()
            
            # Load CSV data using built-in csv module with enhanced error handling
            with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
                # Detect CSV dialect for better parsing
                sample = csvfile.read(1024)
                csvfile.seek(0)
                dialect = csv.Sniffer().sniff(sample)
                
                reader = csv.DictReader(csvfile, dialect=dialect)
                
                # Check if file has data
                rows = list(reader)
                if not rows:
                    raise ValueError(f"CSV file is empty: {self.csv_file_path}")
                
                # Validate required columns - handle both "Battery" and "Drums" column names
                required_columns = ['Artist', 'Song', 'Lead Guitar', 'Rythm Guitar', 
                                  'Bass', 'Lead Singer', 'Keyboards', 'Time']
                # Check for either "Battery" or "Drums" column
                drums_column = None
                if 'Battery' in reader.fieldnames:
                    drums_column = 'Battery'
                elif 'Drums' in reader.fieldnames:
                    drums_column = 'Drums'
                else:
                    required_columns.append('Battery')  # Will be reported as missing
                
                missing_columns = [col for col in required_columns if col not in reader.fieldnames]
                if missing_columns:
                    raise ValueError(f"Missing required columns: {missing_columns}")
                
                # Process each row in the CSV with validation
                processed_songs = []
                max_order = 0
                
                for row_num, row in enumerate(rows, start=2):  # Start at 2 for header
                    try:
                        # Validate required fields
                        if not row.get('Artist') or not row.get('Song'):
                            self.logger.warning(f"Row {row_num}: Missing artist or song title, skipping")
                            continue
                        
                        # Generate unique song ID
                        song_id = self._generate_song_id(row['Artist'], row['Song'])
                        
                        # Parse order value with default assignment
                        order_value = self._parse_order_value(row.get('Order'), max_order + 1)
                        max_order = max(max_order, order_value)
                        
                        # Create OrderedSong object with cleaned assignments
                        song = OrderedSong(
                            artist=str(row['Artist']).strip(),
                            song=str(row['Song']).strip(),
                            lead_guitar=self._clean_assignment(row['Lead Guitar']),
                            rhythm_guitar=self._clean_assignment(row['Rythm Guitar']),  # Note: CSV has typo "Rythm"
                            bass=self._clean_assignment(row['Bass']),
                            battery=self._clean_assignment(row[drums_column]) if drums_column else None,
                            singer=self._clean_assignment(row['Lead Singer']),
                            keyboards=self._clean_assignment(row['Keyboards']),
                            time=str(row['Time']).strip() if row.get('Time') else "0:00",
                            song_id=song_id,
                            order=order_value
                        )
                        
                        processed_songs.append(song)
                        
                    except Exception as e:
                        self.logger.warning(f"Row {row_num}: Error processing row: {str(e)}, skipping")
                        continue
                
                if not processed_songs:
                    raise ValueError("No valid songs could be processed from CSV file")
                
                # Sort songs by order
                processed_songs.sort(key=lambda s: s.order)
                
                # Validate data integrity
                is_valid, issues = self._validate_data_integrity(processed_songs)
                if not is_valid:
                    self.logger.warning(f"Data integrity issues found: {issues}")
                    # Continue with data but log issues
                
                # Store processed data
                self._songs_cache = processed_songs
                for song in processed_songs:
                    self._songs_by_id[song.song_id] = song
                    self._songs_by_order[song.order] = song
                
                # Build song relationships (next/previous)
                self._build_song_relationships()
                
                # Calculate data integrity hash
                self._data_integrity_hash = self._calculate_data_hash(processed_songs)
                
                # Pre-populate dropdown cache for faster access
                self._populate_dropdown_cache()
                
                self._data_loaded = True
                self._update_cache_timestamp()
                self._error_count = 0  # Reset error count on successful load
                
                self.logger.info(f"Successfully loaded {len(processed_songs)} songs from CSV")
                return self._songs_cache.copy()
                
        except FileNotFoundError as e:
            self._handle_data_error(e, "load_songs")
            if self._recover_from_cache():
                self.logger.info("Recovered from cache after file not found error")
                return self._songs_cache.copy()
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")
            
        except ValueError as e:
            self._handle_data_error(e, "load_songs")
            if self._recover_from_cache():
                self.logger.info("Recovered from cache after validation error")
                return self._songs_cache.copy()
            raise ValueError(f"CSV validation error: {str(e)}")
            
        except Exception as e:
            self._handle_data_error(e, "load_songs")
            if self._recover_from_cache():
                self.logger.info("Recovered from cache after unexpected error")
                return self._songs_cache.copy()
            elif self._fallback_data:
                self.logger.warning("Using fallback data due to critical errors")
                self._songs_cache = self._fallback_data
                self._populate_dropdown_cache()
                return self._songs_cache.copy()
            raise Exception(f"Unexpected error loading CSV data: {str(e)}")
    
    def _populate_dropdown_cache(self):
        """Pre-populate the dropdown cache for faster access, sorted by order."""
        self._dropdown_cache.clear()
        for song in self._songs_cache:
            self._dropdown_cache.append({
                "song_id": song.song_id,
                "display_name": f"{song.artist} - {song.song}",
                "artist": song.artist,
                "song": song.song,
                "order": song.order
            })
        
        # Sort by order first, then by artist and song title as fallback
        self._dropdown_cache.sort(key=lambda x: (x["order"], x["artist"], x["song"]))
    
    def get_song_by_id(self, song_id: str) -> Optional[OrderedSong]:
        """
        Retrieve a specific song by its unique ID.
        
        Args:
            song_id: The unique identifier for the song
            
        Returns:
            OrderedSong object if found, None otherwise
        """
        if not self._data_loaded:
            self.load_songs()
        
        return self._songs_by_id.get(song_id)
    
    def get_all_songs(self) -> List[OrderedSong]:
        """
        Get all loaded songs sorted by order.
        
        Returns:
            List of all OrderedSong objects sorted by order
        """
        if not self._data_loaded:
            self.load_songs()
        
        return self._songs_cache.copy()
    
    def get_song_by_order(self, order: int) -> Optional[OrderedSong]:
        """
        Retrieve a specific song by its order number.
        
        Args:
            order: The order number of the song
            
        Returns:
            OrderedSong object if found, None otherwise
        """
        if not self._data_loaded:
            self.load_songs()
        
        return self._songs_by_order.get(order)
    
    def get_songs_sorted_by_order(self) -> List[OrderedSong]:
        """
        Get all songs sorted by order field.
        
        Returns:
            List of OrderedSong objects sorted by order
        """
        if not self._data_loaded:
            self.load_songs()
        
        return sorted(self._songs_cache, key=lambda s: s.order)
    
    def get_musician_songs_by_order(self, musician: str) -> List[Dict]:
        """
        Get all songs for a musician sorted by order.
        
        Args:
            musician: The musician name
            
        Returns:
            List of song dictionaries sorted by order
        """
        return self.get_musician_songs(musician)  # Already sorts by order
    
    def get_next_song(self, current_song_id: str) -> Optional[OrderedSong]:
        """
        Get the next song in the performance order.
        
        Args:
            current_song_id: The ID of the current song
            
        Returns:
            OrderedSong object of the next song, or None if current song is last
        """
        if not self._data_loaded:
            self.load_songs()
        
        current_song = self._songs_by_id.get(current_song_id)
        if not current_song:
            return None
        
        # Find the next song by order
        sorted_songs = sorted(self._songs_cache, key=lambda s: s.order)
        
        for i, song in enumerate(sorted_songs):
            if song.song_id == current_song_id:
                # Return next song if it exists
                if i + 1 < len(sorted_songs):
                    return sorted_songs[i + 1]
                break
        
        return None
    
    def get_previous_song(self, current_song_id: str) -> Optional[OrderedSong]:
        """
        Get the previous song in the performance order.
        
        Args:
            current_song_id: The ID of the current song
            
        Returns:
            OrderedSong object of the previous song, or None if current song is first
        """
        if not self._data_loaded:
            self.load_songs()
        
        current_song = self._songs_by_id.get(current_song_id)
        if not current_song:
            return None
        
        # Find the previous song by order
        sorted_songs = sorted(self._songs_cache, key=lambda s: s.order)
        
        for i, song in enumerate(sorted_songs):
            if song.song_id == current_song_id:
                # Return previous song if it exists
                if i > 0:
                    return sorted_songs[i - 1]
                break
        
        return None
    
    def _build_song_relationships(self):
        """
        Build next/previous song relationship mapping for all songs.
        This method updates the next_song_id and previous_song_id fields.
        """
        # Don't call load_songs here to avoid recursion
        if not self._songs_cache:
            return
        
        # Sort songs by order
        sorted_songs = sorted(self._songs_cache, key=lambda s: s.order)
        
        # Update relationships
        for i, song in enumerate(sorted_songs):
            # Set next song ID
            if i + 1 < len(sorted_songs):
                song.next_song_id = sorted_songs[i + 1].song_id
            else:
                song.next_song_id = None
            
            # Set previous song ID
            if i > 0:
                song.previous_song_id = sorted_songs[i - 1].song_id
            else:
                song.previous_song_id = None
    
    def get_next_song_info(self, current_song_id: str) -> Optional[Dict]:
        """
        Get formatted information about the next song.
        
        Args:
            current_song_id: The ID of the current song
            
        Returns:
            Dictionary with next song information, or None if no next song
        """
        next_song = self.get_next_song(current_song_id)
        if not next_song:
            return None
        
        return {
            "song_id": next_song.song_id,
            "title": f"{next_song.artist} - {next_song.song}",
            "artist": next_song.artist,
            "song": next_song.song,
            "order": next_song.order,
            "time": next_song.time
        }
    
    def format_song_display(self, song_data: OrderedSong) -> Dict:
        """
        Format song data for frontend display.
        
        Args:
            song_data: OrderedSong object to format
            
        Returns:
            Dictionary formatted for JSON response
        """
        return {
            "song_id": song_data.song_id,
            "artist": song_data.artist,
            "song": song_data.song,
            "time": song_data.time,
            "order": song_data.order,
            "assignments": {
                "Lead Guitar": song_data.lead_guitar,
                "Rhythm Guitar": song_data.rhythm_guitar,
                "Bass": song_data.bass,
                "Battery": song_data.battery,
                "Singer": song_data.singer,
                "Keyboards": song_data.keyboards
            }
        }
    
    def get_songs_for_dropdown(self) -> List[Dict]:
        """
        Get songs formatted for dropdown display with caching.
        
        Returns:
            List of dictionaries with song info for dropdown
        """
        if not self._data_loaded or not self._is_cache_valid():
            self.load_songs()
        
        # Return cached dropdown data
        return self._dropdown_cache.copy()
    
    def get_musicians_for_dropdown(self) -> List[Dict]:
        """
        Return list of all musicians for dropdown population.
        
        Returns:
            List of dictionaries with musician info for dropdown
        """
        if not self._data_loaded:
            self.load_songs()
        
        musicians = set()
        
        # Extract all musicians from all songs
        for song in self._songs_cache:
            if song.lead_guitar:
                musicians.add(song.lead_guitar)
            if song.rhythm_guitar:
                musicians.add(song.rhythm_guitar)
            if song.bass:
                musicians.add(song.bass)
            if song.battery:
                musicians.add(song.battery)
            if song.singer:
                musicians.add(song.singer)
            if song.keyboards:
                musicians.add(song.keyboards)
        
        # Convert to list of dictionaries and sort
        musician_list = [{"id": musician, "name": musician} for musician in sorted(musicians)]
        return musician_list
    
    def get_musician_songs(self, musician_name: str) -> List[Dict]:
        """
        Return all songs for a specific musician with instruments, sorted by order.
        
        Args:
            musician_name: The name of the musician
            
        Returns:
            List of dictionaries with song info and instruments for the musician
        """
        if not self._data_loaded:
            self.load_songs()
        
        musician_songs = []
        
        for song in self._songs_cache:
            instruments = []
            
            # Check each instrument assignment
            if song.lead_guitar == musician_name:
                instruments.append("Guitarra Principal")
            if song.rhythm_guitar == musician_name:
                instruments.append("Guitarra Rítmica")
            if song.bass == musician_name:
                instruments.append("Bajo")
            if song.battery == musician_name:
                instruments.append("Batería")
            if song.singer == musician_name:
                instruments.append("Voz")
            if song.keyboards == musician_name:
                instruments.append("Teclados")
            
            # If musician plays in this song, add it to the list
            if instruments:
                musician_songs.append({
                    "id": song.song_id,
                    "title": f"{song.artist} - {song.song}",
                    "artist": song.artist,
                    "song": song.song,
                    "duration": song.time,
                    "order": song.order,
                    "instruments": instruments
                })
        
        # Sort by order first, then by artist and song title as fallback
        musician_songs.sort(key=lambda x: (x["order"], x["artist"], x["song"]))
        return musician_songs
    
    def get_musician_by_id(self, musician_id: str) -> Optional[Dict]:
        """
        Return musician details by ID.
        
        Args:
            musician_id: The musician identifier (same as name in this case)
            
        Returns:
            Dictionary with musician details or None if not found
        """
        if not self._data_loaded:
            self.load_songs()
        
        # Check if musician exists in any song
        all_musicians = {m["id"] for m in self.get_musicians_for_dropdown()}
        
        if musician_id not in all_musicians:
            return None
        
        return {
            "id": musician_id,
            "name": musician_id,
            "songs": self.get_musician_songs(musician_id)
        }
    
    def format_musician_songs_display(self, musician_songs: List[Dict]) -> Dict:
        """
        Format musician songs for frontend display.
        
        Args:
            musician_songs: List of songs for a musician
            
        Returns:
            Dictionary formatted for JSON response
        """
        return {
            "songs": musician_songs,
            "total_songs": len(musician_songs)
        }
    
    def get_data_health_status(self) -> Dict:
        """
        Get comprehensive data health status for monitoring.
        
        Returns:
            Dictionary containing data health metrics
        """
        return {
            "data_loaded": self._data_loaded,
            "songs_count": len(self._songs_cache),
            "cache_valid": self._is_cache_valid(),
            "error_count": self._error_count,
            "error_threshold": self._max_error_threshold,
            "fallback_active": self._fallback_data is not None and self._songs_cache == self._fallback_data,
            "last_update": self._cache_timestamp,
            "data_integrity_hash": self._data_integrity_hash
        }
    
    def validate_data_consistency(self) -> Dict:
        """
        Perform comprehensive data consistency validation.
        
        Returns:
            Dictionary containing validation results
        """
        if not self._data_loaded:
            self.load_songs()
        
        is_valid, issues = self._validate_data_integrity(self._songs_cache)
        
        # Additional consistency checks
        musicians_per_song = {}
        songs_per_musician = {}
        
        for song in self._songs_cache:
            # Count musicians per song
            musician_count = sum(1 for assignment in [
                song.lead_guitar, song.rhythm_guitar, song.bass, 
                song.battery, song.singer, song.keyboards
            ] if assignment)
            musicians_per_song[song.song_id] = musician_count
            
            # Count songs per musician
            for assignment in [song.lead_guitar, song.rhythm_guitar, song.bass, 
                             song.battery, song.singer, song.keyboards]:
                if assignment:
                    if assignment not in songs_per_musician:
                        songs_per_musician[assignment] = 0
                    songs_per_musician[assignment] += 1
        
        return {
            "is_valid": is_valid,
            "issues": issues,
            "total_songs": len(self._songs_cache),
            "total_musicians": len(songs_per_musician),
            "avg_musicians_per_song": sum(musicians_per_song.values()) / len(musicians_per_song) if musicians_per_song else 0,
            "avg_songs_per_musician": sum(songs_per_musician.values()) / len(songs_per_musician) if songs_per_musician else 0,
            "musicians_with_most_songs": sorted(songs_per_musician.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def clear_error_state(self):
        """
        Clear error state and reset error counters.
        """
        self._error_count = 0
        self._fallback_data = None
        self.logger.info("Error state cleared")
    
    def force_reload(self) -> List[Song]:
        """
        Force reload data from CSV file, bypassing cache.
        
        Returns:
            List of Song objects loaded from the CSV file
        """
        self._data_loaded = False
        self._cache_timestamp = None
        self._last_modified_time = None
        self.clear_error_state()
        return self.load_songs()