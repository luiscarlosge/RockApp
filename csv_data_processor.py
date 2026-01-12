"""
CSV Data Processor for Musician Song Selector

This module handles loading, parsing, and processing of song assignment data
from CSV files. It provides methods for data caching, retrieval, and formatting
for frontend consumption.
"""

import csv
import re
import time
from typing import List, Dict, Optional
from dataclasses import dataclass


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


class CSVDataProcessor:
    """
    Processes CSV data containing song assignments and musician information.
    
    Handles loading, parsing, caching, and formatting of song data for
    the musician song selector application.
    """
    
    def __init__(self, csv_file_path: str = "Data.csv"):
        """
        Initialize the CSV data processor.
        
        Args:
            csv_file_path: Path to the CSV file containing song data
        """
        self.csv_file_path = csv_file_path
        self._songs_cache: List[Song] = []
        self._songs_by_id: Dict[str, Song] = {}
        self._dropdown_cache: List[Dict] = []
        self._data_loaded = False
        self._last_modified_time = None
        self._cache_timestamp = None
    
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
    
    def load_songs(self) -> List[Song]:
        """
        Load and parse songs from the CSV file with intelligent caching.
        
        Returns:
            List of Song objects loaded from the CSV file
            
        Raises:
            FileNotFoundError: If the CSV file cannot be found
            ValueError: If the CSV file is empty or malformed
        """
        # Check if cache is still valid
        if self._is_cache_valid():
            return self._songs_cache.copy()
        
        try:
            # Clear existing cache
            self._songs_cache.clear()
            self._songs_by_id.clear()
            self._dropdown_cache.clear()
            
            # Load CSV data using built-in csv module
            with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Check if file has data
                rows = list(reader)
                if not rows:
                    raise ValueError(f"CSV file is empty: {self.csv_file_path}")
                
                # Process each row in the CSV
                for row in rows:
                    # Generate unique song ID
                    song_id = self._generate_song_id(row['Artist'], row['Song'])
                    
                    # Create Song object with cleaned assignments
                    song = Song(
                        artist=str(row['Artist']).strip(),
                        song=str(row['Song']).strip(),
                        lead_guitar=self._clean_assignment(row['Lead Guitar']),
                        rhythm_guitar=self._clean_assignment(row['Rythm Guitar']),  # Note: CSV has typo "Rythm"
                        bass=self._clean_assignment(row['Bass']),
                        battery=self._clean_assignment(row['Battery']),
                        singer=self._clean_assignment(row['Singer']),
                        keyboards=self._clean_assignment(row['Keyboards']),
                        time=str(row['Time']).strip(),
                        song_id=song_id
                    )
                    
                    # Add to cache
                    self._songs_cache.append(song)
                    self._songs_by_id[song_id] = song
            
            # Pre-populate dropdown cache for faster access
            self._populate_dropdown_cache()
            
            self._data_loaded = True
            self._update_cache_timestamp()
            return self._songs_cache.copy()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")
        except KeyError as e:
            raise ValueError(f"Missing required column in CSV file: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error loading CSV data: {e}")
    
    def _populate_dropdown_cache(self):
        """Pre-populate the dropdown cache for faster access."""
        self._dropdown_cache.clear()
        for song in self._songs_cache:
            self._dropdown_cache.append({
                "song_id": song.song_id,
                "display_name": f"{song.artist} - {song.song}",
                "artist": song.artist,
                "song": song.song
            })
        
        # Sort by artist, then by song title
        self._dropdown_cache.sort(key=lambda x: (x["artist"], x["song"]))
    
    def get_song_by_id(self, song_id: str) -> Optional[Song]:
        """
        Retrieve a specific song by its unique ID.
        
        Args:
            song_id: The unique identifier for the song
            
        Returns:
            Song object if found, None otherwise
        """
        if not self._data_loaded:
            self.load_songs()
        
        return self._songs_by_id.get(song_id)
    
    def get_all_songs(self) -> List[Song]:
        """
        Get all loaded songs.
        
        Returns:
            List of all Song objects
        """
        if not self._data_loaded:
            self.load_songs()
        
        return self._songs_cache.copy()
    
    def format_song_display(self, song_data: Song) -> Dict:
        """
        Format song data for frontend display.
        
        Args:
            song_data: Song object to format
            
        Returns:
            Dictionary formatted for JSON response
        """
        return {
            "song_id": song_data.song_id,
            "artist": song_data.artist,
            "song": song_data.song,
            "time": song_data.time,
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