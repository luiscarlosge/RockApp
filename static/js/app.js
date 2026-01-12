/**
 * Musician Song Selector - Frontend JavaScript
 * Handles song selection and display of musician assignments with performance optimizations
 */

class MusicianSongSelector {
    constructor() {
        this.songSelect = document.getElementById('songSelect');
        this.loadingState = document.getElementById('loadingState');
        this.errorState = document.getElementById('errorState');
        this.songDetails = document.getElementById('songDetails');
        this.emptyState = document.getElementById('emptyState');
        this.songTitle = document.getElementById('songTitle');
        this.songArtist = document.getElementById('songArtist');
        this.songDuration = document.getElementById('songDuration');
        this.musicianAssignments = document.getElementById('musicianAssignments');
        this.errorMessage = document.getElementById('errorMessage');
        
        // Performance optimization: Cache data and DOM elements
        this.songs = [];
        this.songsById = new Map(); // Fast lookup by ID
        this.currentSongId = null;
        this.lastRenderedSongId = null;
        this.songDetailsCache = new Map(); // Cache song details to avoid re-fetching
        
        // Performance optimization: Reusable DOM elements
        this.instrumentCardTemplate = null;
        this.createInstrumentCardTemplate();
        
        // Performance optimization: Debounce rapid selections
        this.selectionTimeout = null;
        
        this.init();
    }
    
    createInstrumentCardTemplate() {
        /**
         * Create a reusable template for instrument cards to avoid repeated DOM creation
         */
        this.instrumentCardTemplate = document.createElement('div');
        this.instrumentCardTemplate.className = 'col-12 col-sm-6 col-lg-4 mb-3';
        this.instrumentCardTemplate.innerHTML = `
            <div class="instrument-card">
                <div class="instrument-name">
                    <i class="bi me-1" aria-hidden="true"></i>
                    <span class="instrument-text"></span>
                </div>
                <div class="assignment-text"></div>
            </div>
        `;
    }
    
    init() {
        // Load songs on page load
        this.loadSongs();
        
        // Set up event listeners
        this.songSelect.addEventListener('change', (e) => {
            this.handleSongSelection(e.target.value);
        });
        
        // Add keyboard navigation support
        this.songSelect.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                this.handleSongSelection(e.target.value);
            }
        });
        
        // Show empty state initially
        this.showEmptyState();
    }
    
    async loadSongs() {
        try {
            this.showLoadingIndicator('Loading songs...');
            
            const response = await fetch('/api/songs');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.songs && Array.isArray(data.songs)) {
                this.songs = data.songs;
                
                // Performance optimization: Create fast lookup map
                this.songsById.clear();
                this.songs.forEach(song => {
                    this.songsById.set(song.song_id, song);
                });
                
                this.populateDropdown(data.songs);
                this.hideLoadingIndicator();
                this.showEmptyState();
            } else {
                throw new Error('Invalid response format');
            }
        } catch (error) {
            console.error('Error loading songs:', error);
            this.hideLoadingIndicator();
            this.showError('Unable to load songs. Please refresh the page to try again.');
        }
    }
    
    populateDropdown(songs) {
        // Performance optimization: Use document fragment for batch DOM updates
        const fragment = document.createDocumentFragment();
        
        // Create default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Select a song...';
        fragment.appendChild(defaultOption);
        
        // Songs are already sorted from the server, no need to sort again
        songs.forEach(song => {
            const option = document.createElement('option');
            option.value = song.song_id;
            option.textContent = song.display_name;
            option.setAttribute('data-artist', song.artist);
            option.setAttribute('data-song', song.song);
            fragment.appendChild(option);
        });
        
        // Single DOM update
        this.songSelect.innerHTML = '';
        this.songSelect.appendChild(fragment);
        
        // Enable the dropdown
        this.songSelect.disabled = false;
    }
    
    async handleSongSelection(songId) {
        if (!songId) {
            this.currentSongId = null;
            this.hideSongDetails();
            this.showEmptyState();
            return;
        }
        
        // Performance optimization: Prevent duplicate requests
        if (this.currentSongId === songId) {
            return;
        }
        
        // Performance optimization: Debounce rapid selections
        if (this.selectionTimeout) {
            clearTimeout(this.selectionTimeout);
        }
        
        this.selectionTimeout = setTimeout(async () => {
            await this._loadSongDetails(songId);
        }, 100); // 100ms debounce
    }
    
    async _loadSongDetails(songId) {
        this.currentSongId = songId;
        
        // Performance optimization: Check cache first
        if (this.songDetailsCache.has(songId)) {
            const cachedData = this.songDetailsCache.get(songId);
            this.displaySongDetails(cachedData);
            return;
        }
        
        this.showLoadingIndicator('Loading song details...');
        
        try {
            const response = await fetch(`/api/song/${encodeURIComponent(songId)}`);
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Song not found');
                } else {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
            }
            
            const data = await response.json();
            
            if (data && data.song_id) {
                // Performance optimization: Cache the response
                this.songDetailsCache.set(songId, data);
                this.displaySongDetails(data);
            } else {
                throw new Error('Invalid song data received');
            }
        } catch (error) {
            console.error('Error loading song details:', error);
            this.hideLoadingIndicator();
            this.showError(`Unable to load details for the selected song: ${error.message}`);
            
            // Reset dropdown selection on error
            this.songSelect.value = '';
            this.currentSongId = null;
        }
    }
    
    displaySongDetails(songData) {
        // Performance optimization: Skip re-rendering if same song
        if (this.lastRenderedSongId === songData.song_id) {
            this.hideLoadingIndicator();
            this.hideError();
            this.hideEmptyState();
            this.songDetails.classList.remove('d-none');
            return;
        }
        
        this.hideLoadingIndicator();
        this.hideError();
        this.hideEmptyState();
        
        // Performance optimization: Batch DOM updates
        this.updateSongInfo(songData);
        this.updateMusicianAssignments(songData.assignments);
        
        // Show song details with smooth transition
        this.songDetails.classList.remove('d-none');
        
        // Cache the last rendered song ID
        this.lastRenderedSongId = songData.song_id;
        
        // Announce to screen readers
        this.announceToScreenReader(`Loaded details for ${songData.artist} - ${songData.song}`);
    }
    
    updateSongInfo(songData) {
        /**
         * Performance optimization: Update song info elements efficiently
         */
        // Use textContent for better performance than innerHTML
        this.songTitle.textContent = songData.song;
        this.songArtist.textContent = `by ${songData.artist}`;
        this.songDuration.textContent = songData.time;
    }
    
    updateMusicianAssignments(assignments) {
        /**
         * Performance optimization: Efficient DOM manipulation for assignments
         */
        // Define instruments in the specified order
        const instruments = [
            { key: 'Lead Guitar', icon: 'bi-music-note-beamed' },
            { key: 'Rhythm Guitar', icon: 'bi-music-note-beamed' },
            { key: 'Bass', icon: 'bi-music-note' },
            { key: 'Battery', icon: 'bi-circle' }, // Drums
            { key: 'Singer', icon: 'bi-mic' },
            { key: 'Keyboards', icon: 'bi-keyboard' }
        ];
        
        // Performance optimization: Use document fragment for batch updates
        const fragment = document.createDocumentFragment();
        
        instruments.forEach(instrument => {
            const assignment = assignments[instrument.key];
            const isAssigned = assignment && assignment.trim() !== '';
            
            // Clone the template for better performance
            const col = this.instrumentCardTemplate.cloneNode(true);
            
            // Update the cloned elements
            const card = col.querySelector('.instrument-card');
            const icon = col.querySelector('.bi');
            const instrumentText = col.querySelector('.instrument-text');
            const assignmentText = col.querySelector('.assignment-text');
            
            // Set card class
            card.className = isAssigned ? 'instrument-card assigned' : 'instrument-card unassigned';
            
            // Set icon class
            icon.className = `bi ${instrument.icon} me-1`;
            
            // Set text content
            instrumentText.textContent = instrument.key;
            assignmentText.textContent = isAssigned ? assignment : 'Not assigned';
            assignmentText.className = isAssigned ? 'musician-name' : 'unassigned-text';
            
            fragment.appendChild(col);
        });
        
        // Single DOM update
        this.musicianAssignments.innerHTML = '';
        this.musicianAssignments.appendChild(fragment);
    }
    
    showLoadingIndicator(message = 'Loading...') {
        this.hideError();
        this.hideSongDetails();
        this.hideEmptyState();
        
        // Update loading message if provided
        const loadingText = this.loadingState.querySelector('p');
        if (loadingText && message) {
            loadingText.textContent = message;
        }
        
        this.loadingState.classList.remove('d-none');
        
        // Disable dropdown during loading
        this.songSelect.disabled = true;
    }
    
    hideLoadingIndicator() {
        this.loadingState.classList.add('d-none');
        this.songSelect.disabled = false;
    }
    
    showError(message) {
        this.hideLoadingIndicator();
        this.hideSongDetails();
        this.hideEmptyState();
        
        this.errorMessage.textContent = message;
        this.errorState.classList.remove('d-none');
        
        // Announce error to screen readers
        this.announceToScreenReader(`Error: ${message}`);
    }
    
    hideError() {
        this.errorState.classList.add('d-none');
    }
    
    showEmptyState() {
        this.hideError();
        this.hideSongDetails();
        this.hideLoadingIndicator();
        this.emptyState.classList.remove('d-none');
    }
    
    hideEmptyState() {
        this.emptyState.classList.add('d-none');
    }
    
    hideSongDetails() {
        this.songDetails.classList.add('d-none');
    }
    
    // Accessibility helper
    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        // Remove after announcement
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
    
    // Public method to get current song data
    getCurrentSong() {
        return this.songs.find(song => song.song_id === this.currentSongId) || null;
    }
    
    // Public method to refresh data
    async refresh() {
        this.currentSongId = null;
        this.lastRenderedSongId = null;
        this.songSelect.value = '';
        
        // Performance optimization: Clear caches on refresh
        this.songsById.clear();
        this.songDetailsCache.clear();
        
        await this.loadSongs();
    }
    
    // Performance optimization: Clear caches when needed
    clearCache() {
        this.songDetailsCache.clear();
        this.lastRenderedSongId = null;
    }
    
    // Performance optimization: Preload popular songs
    async preloadPopularSongs() {
        // Preload first 3 songs for better perceived performance
        const songsToPreload = this.songs.slice(0, 3);
        
        for (const song of songsToPreload) {
            if (!this.songDetailsCache.has(song.song_id)) {
                try {
                    const response = await fetch(`/api/song/${encodeURIComponent(song.song_id)}`);
                    if (response.ok) {
                        const data = await response.json();
                        this.songDetailsCache.set(song.song_id, data);
                    }
                } catch (error) {
                    // Silently fail preloading - not critical
                    console.debug('Preload failed for song:', song.song_id);
                }
            }
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create global instance for debugging/testing
    window.musicianSongSelector = new MusicianSongSelector();
    
    // Performance optimization: Preload popular songs after initial load
    setTimeout(() => {
        if (window.musicianSongSelector && window.musicianSongSelector.songs.length > 0) {
            window.musicianSongSelector.preloadPopularSongs();
        }
    }, 1000); // Wait 1 second after initial load
    
    // Add error handling for unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
        if (window.musicianSongSelector) {
            window.musicianSongSelector.showError('An unexpected error occurred. Please refresh the page.');
        }
    });
});

// Add CSS class for screen reader only content
const style = document.createElement('style');
style.textContent = `
    .sr-only {
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
    }
`;
document.head.appendChild(style);