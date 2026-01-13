/**
 * Navigation State Manager for Cross-Section Navigation
 * Handles navigation between sections with proper preselection and menu synchronization
 */

class NavigationStateManager {
    constructor() {
        this.currentSection = 'song-selector';
        this.navigationHistory = [];
    }
    
    /**
     * Navigate to target section with preselection
     * @param {string} targetSection - The section to navigate to
     * @param {string} itemType - Type of item to preselect ('Musician' or 'Song')
     * @param {string} itemId - ID or name of item to preselect
     */
    static navigateWithPreselection(targetSection, itemType, itemId) {
        // Store selection in sessionStorage
        sessionStorage.setItem(`preselected${itemType}`, itemId);
        
        // Navigate to target section
        if (window.hamburgerMenu) {
            window.hamburgerMenu.goToSection(targetSection);
        }
        
        // Ensure target section is initialized
        NavigationStateManager.ensureSectionInitialized(targetSection);
        
        // Apply preselection after navigation
        setTimeout(() => {
            NavigationStateManager.applyPreselection(targetSection, itemType, itemId);
        }, 300);
        
        // Record navigation in history
        NavigationStateManager.recordNavigation(targetSection, itemType, itemId);
    }
    
    /**
     * Ensure the target section is properly initialized
     * @param {string} targetSection - The section to initialize
     */
    static ensureSectionInitialized(targetSection) {
        switch (targetSection) {
            case 'musician-selector':
                if (window.musicianSelector && !window.musicianSelector.isInitialized) {
                    window.musicianSelector.init();
                }
                break;
            case 'song-selector':
                // Song selector is already initialized on page load
                break;
            case 'live-performance':
                if (window.livePerformanceManager && !window.livePerformanceManager.isInitialized) {
                    window.livePerformanceManager.init();
                }
                break;
        }
    }
    
    /**
     * Apply preselection to the target section
     * @param {string} targetSection - The section where preselection should be applied
     * @param {string} itemType - Type of item to preselect
     * @param {string} itemId - ID or name of item to preselect
     */
    static applyPreselection(targetSection, itemType, itemId) {
        if (targetSection === 'musician-selector' && itemType === 'Musician') {
            // Preselect musician by name
            if (window.musicianSelector && window.musicianSelector.selectMusicianByName) {
                window.musicianSelector.selectMusicianByName(itemId);
            }
        } else if (targetSection === 'song-selector' && itemType === 'Song') {
            // Preselect song by ID
            if (window.musicianSongSelector && window.musicianSongSelector.songSelect) {
                window.musicianSongSelector.songSelect.value = itemId;
                window.musicianSongSelector.handleSongSelection(itemId);
            }
        }
    }
    
    /**
     * Record navigation in history for debugging and analytics
     * @param {string} targetSection - The section navigated to
     * @param {string} itemType - Type of item preselected
     * @param {string} itemId - ID or name of item preselected
     */
    static recordNavigation(targetSection, itemType, itemId) {
        const navigationEntry = {
            timestamp: Date.now(),
            targetSection: targetSection,
            itemType: itemType,
            itemId: itemId,
            userAgent: navigator.userAgent.substring(0, 50) // Truncated for privacy
        };
        
        // Store in sessionStorage for debugging
        const history = JSON.parse(sessionStorage.getItem('navigationHistory') || '[]');
        history.push(navigationEntry);
        
        // Keep only last 10 entries to avoid storage bloat
        if (history.length > 10) {
            history.shift();
        }
        
        sessionStorage.setItem('navigationHistory', JSON.stringify(history));
    }
    
    /**
     * Enhanced navigation for musician links in song details
     * @param {string} musicianName - Name of the musician to navigate to
     */
    static navigateToMusicianFromSong(musicianName) {
        NavigationStateManager.navigateWithPreselection('musician-selector', 'Musician', musicianName);
        
        // Announce navigation to screen readers
        NavigationStateManager.announceToScreenReader(`Navegando al selector de músicos para ${musicianName}`);
    }
    
    /**
     * Enhanced navigation for song links in musician details
     * @param {string} songId - ID of the song to navigate to
     */
    static navigateToSongFromMusician(songId) {
        NavigationStateManager.navigateWithPreselection('song-selector', 'Song', songId);
        
        // Announce navigation to screen readers
        NavigationStateManager.announceToScreenReader('Navegando al selector de canciones');
    }
    
    /**
     * Announce navigation changes to screen readers
     * @param {string} message - Message to announce
     */
    static announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        // Remove after announcement
        setTimeout(() => {
            if (document.body.contains(announcement)) {
                document.body.removeChild(announcement);
            }
        }, 1000);
    }
    
    /**
     * Get navigation history for debugging
     * @returns {Array} Navigation history entries
     */
    static getNavigationHistory() {
        return JSON.parse(sessionStorage.getItem('navigationHistory') || '[]');
    }
    
    /**
     * Clear navigation history
     */
    static clearNavigationHistory() {
        sessionStorage.removeItem('navigationHistory');
    }
}

// Make NavigationStateManager globally available
window.NavigationStateManager = NavigationStateManager;