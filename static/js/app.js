/**
 * Rock and Roll Forum Jam en Español - Frontend JavaScript
 * Handles song selection, musician selection, live performance display, and navigation menu system
 */

class HamburgerMenuSystem {
    constructor() {
        this.menuToggle = document.querySelector('.menu-toggle');
        this.menuOverlay = document.querySelector('.menu-overlay');
        this.menuItems = document.querySelectorAll('.menu-item');
        this.sections = document.querySelectorAll('.app-section');
        this.currentSection = 'song-selector'; // Default active section
        
        // Responsive behavior tracking
        this.isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        this.viewportWidth = window.innerWidth;
        this.viewportHeight = window.innerHeight;
        
        this.init();
    }
    
    init() {
        // Set up event listeners
        this.menuToggle.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMenu();
        });
        
        // Close menu when clicking overlay
        this.menuOverlay.addEventListener('click', (e) => {
            if (e.target === this.menuOverlay) {
                this.closeMenu();
            }
        });
        
        // Handle menu item clicks
        this.menuItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const sectionId = item.getAttribute('data-section');
                this.navigateToSection(sectionId);
                this.closeMenu();
            });
            
            // Enhanced touch support
            if (this.isTouch) {
                item.addEventListener('touchstart', (e) => {
                    item.style.backgroundColor = 'rgba(255, 215, 0, 0.1)';
                }, { passive: true });
                
                item.addEventListener('touchend', (e) => {
                    setTimeout(() => {
                        item.style.backgroundColor = '';
                    }, 150);
                }, { passive: true });
            }
        });
        
        // Handle keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isMenuOpen()) {
                this.closeMenu();
            }
            
            // Enhanced keyboard navigation for menu items
            if (this.isMenuOpen()) {
                const focusedElement = document.activeElement;
                const menuItems = Array.from(this.menuItems);
                const currentIndex = menuItems.indexOf(focusedElement);
                
                switch (e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        const nextIndex = (currentIndex + 1) % menuItems.length;
                        menuItems[nextIndex].focus();
                        break;
                    case 'ArrowUp':
                        e.preventDefault();
                        const prevIndex = currentIndex === 0 ? menuItems.length - 1 : currentIndex - 1;
                        menuItems[prevIndex].focus();
                        break;
                    case 'Home':
                        e.preventDefault();
                        menuItems[0].focus();
                        break;
                    case 'End':
                        e.preventDefault();
                        menuItems[menuItems.length - 1].focus();
                        break;
                    case 'Tab':
                        // Allow normal tab behavior within menu
                        if (e.shiftKey && currentIndex === 0) {
                            // If shift+tab on first item, close menu and focus toggle
                            e.preventDefault();
                            this.closeMenu();
                        } else if (!e.shiftKey && currentIndex === menuItems.length - 1) {
                            // If tab on last item, close menu and focus next element
                            e.preventDefault();
                            this.closeMenu();
                        }
                        break;
                }
            }
            
            // Global keyboard shortcuts
            if (e.altKey) {
                switch (e.key) {
                    case '1':
                        e.preventDefault();
                        this.navigateToSection('song-selector');
                        this.announceToScreenReader('Navegando al selector de canciones');
                        break;
                    case '2':
                        e.preventDefault();
                        this.navigateToSection('musician-selector');
                        this.announceToScreenReader('Navegando al selector de músicos');
                        break;
                    case 'm':
                        e.preventDefault();
                        this.toggleMenu();
                        this.announceToScreenReader('Alternando menú de navegación');
                        break;
                }
            }
        });
        
        // Handle viewport changes for responsive behavior
        window.addEventListener('resize', () => {
            this.handleViewportChange();
        });
        
        // Handle orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleViewportChange();
            }, 100);
        });
        
        // Set initial active section
        this.setActiveSection(this.currentSection);
        this.updateActiveMenuItem();
        
        // Initialize responsive behavior
        this.handleViewportChange();
    }
    
    handleViewportChange() {
        const newWidth = window.innerWidth;
        const newHeight = window.innerHeight;
        
        // Update viewport tracking
        this.viewportWidth = newWidth;
        this.viewportHeight = newHeight;
        
        // Close menu if viewport becomes too small
        if (this.isMenuOpen() && (newWidth < 320 || newHeight < 400)) {
            this.closeMenu();
        }
        
        // Adjust menu content positioning for small screens
        this.adjustMenuForViewport();
        
        // Notify sections of viewport change
        this.notifySectionsOfViewportChange();
    }
    
    adjustMenuForViewport() {
        const menuContent = document.querySelector('.menu-content');
        if (!menuContent) return;
        
        // Adjust menu size based on viewport
        if (this.viewportWidth < 480) {
            menuContent.style.maxWidth = '85vw';
            menuContent.style.maxHeight = '85vh';
        } else if (this.viewportWidth < 768) {
            menuContent.style.maxWidth = '90vw';
            menuContent.style.maxHeight = '90vh';
        } else {
            menuContent.style.maxWidth = '';
            menuContent.style.maxHeight = '';
        }
    }
    
    notifySectionsOfViewportChange() {
        // Notify all section managers of viewport changes
        if (window.musicianSelector && window.musicianSelector.handleViewportChange) {
            window.musicianSelector.handleViewportChange();
        }
        
        if (window.musicianSongSelector && window.musicianSongSelector.handleViewportChange) {
            window.musicianSongSelector.handleViewportChange();
        }
    }
    
    toggleMenu() {
        if (this.isMenuOpen()) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }
    
    openMenu() {
        this.menuToggle.classList.add('active');
        this.menuOverlay.classList.add('active');
        this.menuToggle.setAttribute('aria-expanded', 'true');
        this.menuOverlay.setAttribute('aria-hidden', 'false');
        
        // Focus first menu item for accessibility
        const firstMenuItem = this.menuItems[0];
        if (firstMenuItem) {
            setTimeout(() => firstMenuItem.focus(), 100);
        }
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = 'hidden';
        
        // Trap focus within menu
        this.trapFocus();
        
        // Announce menu opening to screen readers
        this.announceToScreenReader('Menú de navegación abierto');
    }
    
    closeMenu() {
        this.menuToggle.classList.remove('active');
        this.menuOverlay.classList.remove('active');
        this.menuToggle.setAttribute('aria-expanded', 'false');
        this.menuOverlay.setAttribute('aria-hidden', 'true');
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Remove focus trap
        this.removeFocusTrap();
        
        // Return focus to menu toggle
        this.menuToggle.focus();
        
        // Announce menu closing to screen readers
        this.announceToScreenReader('Menú de navegación cerrado');
    }
    
    trapFocus() {
        // Get all focusable elements within the menu
        const focusableElements = this.menuOverlay.querySelectorAll(
            'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        // Store the focus trap handler
        this.focusTrapHandler = (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    // Shift + Tab
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    // Tab
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        };
        
        document.addEventListener('keydown', this.focusTrapHandler);
    }
    
    removeFocusTrap() {
        if (this.focusTrapHandler) {
            document.removeEventListener('keydown', this.focusTrapHandler);
            this.focusTrapHandler = null;
        }
    }
    
    isMenuOpen() {
        return this.menuToggle.classList.contains('active');
    }
    
    navigateToSection(sectionId) {
        if (sectionId && sectionId !== this.currentSection) {
            this.setActiveSection(sectionId);
            this.currentSection = sectionId;
            this.updateActiveMenuItem();
            
            // Announce section change to screen readers
            this.announceToScreenReader(`Navegando a ${this.getSectionTitle(sectionId)}`);
            
            // Initialize section-specific functionality
            this.initializeSectionContent(sectionId);
            
            // Ensure menu state synchronization (Requirements 3.5)
            this.ensureMenuStateSynchronization(sectionId);
        }
    }
    
    /**
     * Ensure menu state is properly synchronized with current section
     * @param {string} sectionId - The current section ID
     */
    ensureMenuStateSynchronization(sectionId) {
        // Double-check that active menu item matches current section
        const activeMenuItem = document.querySelector(`[data-section="${sectionId}"]`);
        if (activeMenuItem) {
            // Remove active class from all menu items
            this.menuItems.forEach(item => {
                item.classList.remove('active');
            });
            
            // Add active class to current section menu item
            activeMenuItem.classList.add('active');
            
            // Update aria-current attribute for accessibility
            this.menuItems.forEach(item => {
                item.removeAttribute('aria-current');
            });
            activeMenuItem.setAttribute('aria-current', 'page');
        }
        
        // Verify synchronization
        const currentSection = this.getCurrentSection();
        const activeMenu = document.querySelector('.menu-item.active');
        
        if (activeMenu && activeMenu.getAttribute('data-section') !== currentSection) {
            console.warn('Menu state synchronization mismatch detected and corrected');
            this.updateActiveMenuItem(); // Force re-sync
        }
    }
    
    setActiveSection(sectionId) {
        // Hide all sections
        this.sections.forEach(section => {
            section.classList.remove('active');
        });
        
        // Show target section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
            
            // Scroll to top of section
            targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    updateActiveMenuItem() {
        // Remove active class from all menu items
        this.menuItems.forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to current section menu item
        const activeMenuItem = document.querySelector(`[data-section="${this.currentSection}"]`);
        if (activeMenuItem) {
            activeMenuItem.classList.add('active');
        }
    }
    
    getSectionTitle(sectionId) {
        const titles = {
            'song-selector': 'Selector de Canciones',
            'musician-selector': 'Selector de Músicos'
        };
        return titles[sectionId] || sectionId;
    }
    
    initializeSectionContent(sectionId) {
        // Initialize section-specific functionality when navigating
        switch (sectionId) {
            case 'musician-selector':
                if (window.musicianSelector && !window.musicianSelector.isInitialized) {
                    window.musicianSelector.init();
                }
                break;
            case 'song-selector':
                // Song selector is already initialized
                break;
        }
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
            if (document.body.contains(announcement)) {
                document.body.removeChild(announcement);
            }
        }, 1000);
    }
    
    // Public method to get current section
    getCurrentSection() {
        return this.currentSection;
    }
    
    // Public method to programmatically navigate
    goToSection(sectionId) {
        this.navigateToSection(sectionId);
    }
}

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
        
        // Spanish translations from server
        this.translations = window.translations || {};
        
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
    
    getTranslation(key, defaultValue = key) {
        return this.translations[key] || defaultValue;
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
        
        // Enhanced keyboard shortcuts for order-based navigation
        document.addEventListener('keydown', (e) => {
            // Only handle shortcuts when not in input fields
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
                return;
            }
            
            // Alt + Right Arrow: Go to next song
            if (e.altKey && e.key === 'ArrowRight') {
                e.preventDefault();
                this.navigateToNextSong();
            }
            
            // Alt + Left Arrow: Go to previous song
            if (e.altKey && e.key === 'ArrowLeft') {
                e.preventDefault();
                this.navigateToPreviousSong();
            }
            
            // Alt + N: Go to next song (alternative shortcut)
            if (e.altKey && e.key === 'n') {
                e.preventDefault();
                this.navigateToNextSong();
            }
            
            // Alt + P: Go to previous song (alternative shortcut)
            if (e.altKey && e.key === 'p') {
                e.preventDefault();
                this.navigateToPreviousSong();
            }
        });
        
        // Listen for data consistency changes
        window.addEventListener('dataConsistencyChange', () => {
            this.handleDataConsistencyChange();
        });
        
        // Listen for real-time song updates
        this.setupRealTimeIntegration();
        
        // Check for pre-selected song from session storage
        const preselectedSong = sessionStorage.getItem('preselectedSong');
        if (preselectedSong) {
            sessionStorage.removeItem('preselectedSong');
            // Wait for songs to load, then select
            setTimeout(() => {
                this.songSelect.value = preselectedSong;
                this.handleSongSelection(preselectedSong);
            }, 500);
        }
        
        // Show empty state initially
        this.showEmptyState();
        
        // Add keyboard shortcuts help
        this.addKeyboardShortcutsHelp();
    }
    
    /**
     * Set up real-time integration for global song synchronization
     * Requirements: 4.5, 6.1, 6.2
     */
    setupRealTimeIntegration() {
        // Wait for connection manager to be available
        if (window.connectionManager) {
            const socket = window.connectionManager.getSocket();
            if (socket) {
                // Listen for global song changes
                socket.on('song_changed', (data) => {
                    this.handleRealTimeSongChange(data);
                });
                
                // Listen for next song updates
                socket.on('next_song_updated', (data) => {
                    this.handleRealTimeNextSongUpdate(data);
                });
            }
        }
    }
    
    /**
     * Handle real-time song changes from other sessions
     * Requirements: 4.5, 6.2
     */
    handleRealTimeSongChange(data) {
        if (!data || !data.song_id) return;
        
        // Only update if it's a different song
        if (this.currentSongId !== data.song_id) {
            // Update dropdown selection without triggering change event
            if (this.songSelect) {
                this.songSelect.value = data.song_id;
            }
            
            // Load and display song details
            if (data.song_data) {
                this.displaySongDetails(data.song_data);
                this.currentSongId = data.song_id;
            } else {
                this._loadSongDetails(data.song_id);
            }
            
            // Show notification
            this.showRealTimeUpdateNotification(data.song_data);
        }
    }
    
    /**
     * Handle real-time next song updates with enhanced functionality
     * Requirements: 4.5, 2.5
     */
    handleRealTimeNextSongUpdate(data) {
        if (!data) return;
        
        // Update next song widget with new information
        this.updateNextSongWidget({ next_song: data.next_song });
        
        // Show notification about next song update
        if (data.next_song) {
            const message = `${this.getTranslation('next_song_updated', 'Siguiente canción actualizada')}: ${data.next_song.title}`;
            this.showTemporaryMessage(message, 'info');
            
            // Announce to screen readers
            this.announceToScreenReader(message);
        }
    }
    
    /**
     * Show notification for real-time updates
     * Requirements: 6.2, 6.3
     */
    showRealTimeUpdateNotification(songData) {
        if (!songData) return;
        
        const message = `Actualización automática: ${songData.artist} - ${songData.song}`;
        this.showTemporaryMessage(message, 'info');
        
        // Announce to screen readers
        this.announceToScreenReader(`Canción actualizada automáticamente: ${songData.artist} - ${songData.song}`);
    }
    
    /**
     * Show temporary message notification
     * Requirements: 6.3
     */
    showTemporaryMessage(message, type = 'info') {
        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'warning' ? 'alert-warning' : 'alert-info';
        const iconClass = type === 'success' ? 'bi-check-circle' : 
                         type === 'warning' ? 'bi-exclamation-triangle' : 'bi-info-circle';
        
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 80px;
            right: 20px;
            z-index: 9999;
            max-width: 350px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${iconClass} me-2" aria-hidden="true"></i>
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()" aria-label="Cerrar"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-dismiss after 4 seconds
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.remove();
            }
        }, 4000);
    }
    
    handleDataConsistencyChange() {
        /**
         * Handle data consistency changes by refreshing data if needed.
         */
        console.info('Data consistency change detected in song selector');
        
        // Clear cache and reload if we have data loaded
        if (this.songs.length > 0) {
            this.clearCache();
            this.loadSongs();
        }
        
        // Show notification to user
        this.announceToScreenReader('Los datos han sido actualizados');
    }
    
    async loadSongs() {
        try {
            this.showLoadingIndicator(this.getTranslation('data_loading', 'Cargando datos...'));
            
            const response = await window.errorHandler.enhancedFetch('/api/songs', {}, 'load_songs');
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
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
                throw new Error(this.getTranslation('invalid_data_format', 'Formato de datos inválido'));
            }
        } catch (error) {
            console.error('Error loading songs:', error);
            this.hideLoadingIndicator();
            const errorMessage = await window.errorHandler.handleApiError(error, 'load_songs');
            this.showError(errorMessage);
        }
    }
    
    populateDropdown(songs) {
        // Performance optimization: Use document fragment for batch DOM updates
        const fragment = document.createDocumentFragment();
        
        // Create default option with Spanish text
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = this.getTranslation('select_song', 'Seleccionar una canción...');
        fragment.appendChild(defaultOption);
        
        // Songs are already sorted by order from the server, no need to sort again
        songs.forEach(song => {
            const option = document.createElement('option');
            option.value = song.song_id;
            
            // Include order number in display name if available
            let displayName = song.display_name;
            if (song.order) {
                displayName = `${song.order}. ${displayName}`;
            }
            option.textContent = displayName;
            
            option.setAttribute('data-artist', song.artist);
            option.setAttribute('data-song', song.song);
            if (song.order) {
                option.setAttribute('data-order', song.order);
            }
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
        
        this.showLoadingIndicator(this.getTranslation('data_loading', 'Cargando datos...'));
        
        try {
            const response = await window.errorHandler.enhancedFetch(
                `/api/song/${encodeURIComponent(songId)}`, 
                {}, 
                'load_song_details'
            );
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data && data.song_id) {
                // Performance optimization: Cache the response
                this.songDetailsCache.set(songId, data);
                this.displaySongDetails(data);
            } else {
                throw new Error(this.getTranslation('invalid_data_format', 'Formato de datos inválido'));
            }
        } catch (error) {
            console.error('Error loading song details:', error);
            this.hideLoadingIndicator();
            const errorMessage = await window.errorHandler.handleApiError(error, 'load_song_details');
            this.showError(errorMessage);
            
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
        this.updateCrossSectionLinks(songData);
        
        // Show song details with smooth transition
        this.songDetails.classList.remove('d-none');
        
        // Cache the last rendered song ID
        this.lastRenderedSongId = songData.song_id;
        
        // Announce to screen readers
        this.announceToScreenReader(`Loaded details for ${songData.artist} - ${songData.song}`);
    }
    
    updateSongInfo(songData) {
        /**
         * Performance optimization: Update song info elements efficiently with enhanced order support
         * Requirements: 2.2, 5.1, 5.2
         */
        // Use textContent for better performance than innerHTML
        this.songTitle.textContent = songData.song;
        this.songArtist.textContent = `${this.getTranslation('by_artist', 'por')} ${songData.artist}`;
        this.songDuration.textContent = songData.time;
        
        // Enhanced order display with Spanish formatting
        const songOrderElement = document.getElementById('songOrder');
        if (songOrderElement && songData.order) {
            const orderText = `${this.getTranslation('order_label', 'Orden')}: ${songData.order}`;
            songOrderElement.textContent = orderText;
            songOrderElement.setAttribute('aria-label', `${this.getTranslation('song_order_aria', 'Orden de la canción')} ${songData.order}`);
            songOrderElement.classList.remove('d-none');
        } else if (songOrderElement) {
            songOrderElement.classList.add('d-none');
        }
        
        // Update next song widget with enhanced functionality
        this.updateNextSongWidget(songData);
        
        // Update page title with order information for better navigation
        if (songData.order) {
            document.title = `${songData.order}. ${songData.artist} - ${songData.song} | Rock and Roll Forum Jam`;
        } else {
            document.title = `${songData.artist} - ${songData.song} | Rock and Roll Forum Jam`;
        }
    }
    
    updateNextSongWidget(songData) {
        /**
         * Update next song widget display with enhanced functionality
         * Requirements: 2.2, 2.5, 5.1, 5.2
         */
        const nextSongWidget = document.getElementById('nextSongWidget');
        const noNextSongWidget = document.getElementById('noNextSongWidget');
        
        if (songData.next_song) {
            // Show next song widget
            if (nextSongWidget) {
                const nextSongTitle = document.getElementById('nextSongTitle');
                const nextSongArtist = document.getElementById('nextSongArtist');
                const nextSongOrder = document.getElementById('nextSongOrder');
                const selectNextSongBtn = document.getElementById('selectNextSongBtn');
                
                // Update content with Spanish formatting
                if (nextSongTitle) {
                    nextSongTitle.textContent = songData.next_song.title || songData.next_song.song;
                }
                if (nextSongArtist) {
                    const artist = songData.next_song.artist || this.getTranslation('unknown_artist', 'Artista desconocido');
                    nextSongArtist.textContent = `${this.getTranslation('by_artist', 'por')} ${artist}`;
                }
                if (nextSongOrder) {
                    nextSongOrder.textContent = `${this.getTranslation('order_label', 'Orden')}: ${songData.next_song.order}`;
                    nextSongOrder.setAttribute('aria-label', `${this.getTranslation('order_label', 'Orden')} ${songData.next_song.order}`);
                }
                
                // Enhanced next song selection button with keyboard support
                if (selectNextSongBtn) {
                    // Remove existing event listeners
                    const newBtn = selectNextSongBtn.cloneNode(true);
                    selectNextSongBtn.parentNode.replaceChild(newBtn, selectNextSongBtn);
                    
                    // Update button text and accessibility
                    newBtn.innerHTML = `
                        <i class="bi bi-arrow-right me-1" aria-hidden="true"></i>
                        ${this.getTranslation('select_next_song', 'Seleccionar')}
                    `;
                    newBtn.setAttribute('aria-label', 
                        `${this.getTranslation('select_next_song_aria', 'Seleccionar siguiente canción')}: ${songData.next_song.title}`
                    );
                    
                    // Add click handler
                    newBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        this.selectNextSong(songData.next_song);
                    });
                    
                    // Add keyboard navigation support
                    newBtn.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            this.selectNextSong(songData.next_song);
                        }
                    });
                }
                
                // Add keyboard navigation for the entire widget
                nextSongWidget.setAttribute('tabindex', '0');
                nextSongWidget.setAttribute('role', 'button');
                nextSongWidget.setAttribute('aria-label', 
                    `${this.getTranslation('next_song', 'Siguiente canción')}: ${songData.next_song.title} ${this.getTranslation('by_artist', 'por')} ${songData.next_song.artist}`
                );
                
                // Add keyboard handler for the widget
                const widgetKeyHandler = (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        this.selectNextSong(songData.next_song);
                    }
                };
                
                // Remove existing handler and add new one
                nextSongWidget.removeEventListener('keydown', widgetKeyHandler);
                nextSongWidget.addEventListener('keydown', widgetKeyHandler);
                
                nextSongWidget.classList.remove('d-none');
            }
            
            if (noNextSongWidget) {
                noNextSongWidget.classList.add('d-none');
            }
        } else {
            // Show no next song message with proper Spanish text
            if (nextSongWidget) {
                nextSongWidget.classList.add('d-none');
            }
            
            if (noNextSongWidget) {
                // Update the message content with Spanish translation
                const messageElement = noNextSongWidget.querySelector('p');
                if (messageElement) {
                    messageElement.textContent = this.getTranslation('no_next_song', 'Última canción del repertorio');
                }
                noNextSongWidget.classList.remove('d-none');
            }
        }
    }
    
    /**
     * Select next song with enhanced functionality and notifications
     * Requirements: 2.2, 2.5, 5.2
     */
    selectNextSong(nextSongData) {
        if (!nextSongData || !nextSongData.song_id) {
            console.warn('Invalid next song data provided');
            return;
        }
        
        // Update dropdown selection
        if (this.songSelect) {
            this.songSelect.value = nextSongData.song_id;
        }
        
        // Load song details
        this.handleSongSelection(nextSongData.song_id);
        
        // Show notification with Spanish text
        const message = `${this.getTranslation('navigated_to_next_song', 'Navegando a la siguiente canción')}: ${nextSongData.title || nextSongData.song}`;
        this.showTemporaryMessage(message, 'success');
        
        // Announce to screen readers
        this.announceToScreenReader(message);
        
        // Emit real-time update if connected
        if (window.connectionManager && window.connectionManager.isSocketConnected()) {
            const socket = window.connectionManager.getSocket();
            if (socket) {
                socket.emit('select_global_song', {
                    song_id: nextSongData.song_id,
                    source: 'next_song_navigation',
                    timestamp: Date.now()
                });
            }
        }
        
        // Scroll to top of song details for better UX
        const songDetails = document.getElementById('songDetails');
        if (songDetails) {
            songDetails.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    updateMusicianAssignments(assignments) {
        /**
         * Performance optimization: Efficient DOM manipulation for assignments with Spanish translations and enhanced accessibility
         */
        
        if (!assignments) {
            console.warn('No assignments provided to updateMusicianAssignments');
            this.musicianAssignments.innerHTML = '<div class="col-12"><p class="text-warning">No hay datos de asignaciones disponibles</p></div>';
            return;
        }
        
        // Define instruments in the specified order with Spanish translations
        const instruments = [
            { key: 'Lead Guitar', icon: 'bi-music-note-beamed', spanish: 'Guitarra Principal' },
            { key: 'Rhythm Guitar', icon: 'bi-music-note-beamed', spanish: 'Guitarra Rítmica' },
            { key: 'Bass', icon: 'bi-music-note', spanish: 'Bajo' },
            { key: 'Battery', icon: 'bi-circle', spanish: 'Batería' }, // Drums
            { key: 'Singer', icon: 'bi-mic', spanish: 'Voz' },
            { key: 'Keyboards', icon: 'bi-keyboard', spanish: 'Teclado' }
        ];
        
        // Performance optimization: Use document fragment for batch updates
        const fragment = document.createDocumentFragment();
        
        instruments.forEach((instrument, index) => {
            const assignment = assignments[instrument.key];
            const isAssigned = assignment && assignment.trim() !== '';
            
            // Clone the template for better performance
            const col = this.instrumentCardTemplate.cloneNode(true);
            
            // Update the cloned elements
            const card = col.querySelector('.instrument-card');
            const icon = col.querySelector('.bi');
            const instrumentText = col.querySelector('.instrument-text');
            const assignmentText = col.querySelector('.assignment-text');
            
            // Set card class and accessibility attributes
            card.className = isAssigned ? 'instrument-card assigned' : 'instrument-card unassigned';
            card.setAttribute('role', 'listitem');
            card.setAttribute('tabindex', '0');
            card.setAttribute('aria-label', `${instrument.spanish}: ${isAssigned ? assignment : 'Sin asignar'}`);
            
            // Set icon class
            icon.className = `bi ${instrument.icon} me-1`;
            
            // Set text content with Spanish translation
            instrumentText.textContent = instrument.spanish;
            assignmentText.textContent = isAssigned ? assignment : this.getTranslation('unassigned', 'Sin asignar');
            assignmentText.className = isAssigned ? 'musician-name' : 'unassigned-text';
            
            // Add keyboard navigation support
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    if (isAssigned) {
                        this.navigateToMusicianSelector(assignment);
                    }
                }
            });
            
            // Add click support for assigned musicians
            if (isAssigned) {
                card.style.cursor = 'pointer';
                card.addEventListener('click', () => {
                    this.navigateToMusicianSelector(assignment);
                });
            }
            
            fragment.appendChild(col);
        });
        
        // Single DOM update
        this.musicianAssignments.innerHTML = '';
        this.musicianAssignments.appendChild(fragment);
    }
    
    updateCrossSectionLinks(songData) {
        /**
         * Create cross-section navigation links to forward users to musician selector with enhanced accessibility
         */
        const crossSectionLinks = document.getElementById('crossSectionLinks');
        if (!crossSectionLinks) return;
        
        // Clear existing links
        crossSectionLinks.innerHTML = '';
        
        // Get unique musicians from assignments
        const musicians = new Set();
        Object.values(songData.assignments).forEach(musician => {
            if (musician && musician.trim() !== '') {
                musicians.add(musician.trim());
            }
        });
        
        // Create navigation links for each musician with enhanced accessibility
        musicians.forEach((musicianName, index) => {
            const link = document.createElement('button');
            link.className = 'btn btn-outline-warning btn-sm';
            link.innerHTML = `<i class="bi bi-person-fill me-1" aria-hidden="true"></i>${musicianName}`;
            link.setAttribute('aria-label', `Ver canciones de ${musicianName} en el selector de músicos`);
            link.setAttribute('type', 'button');
            link.setAttribute('role', 'button');
            link.setAttribute('tabindex', '0');
            
            // Add keyboard navigation support
            link.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.navigateToMusicianSelector(musicianName);
                }
            });
            
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToMusicianSelector(musicianName);
            });
            
            crossSectionLinks.appendChild(link);
        });
        
        // If no musicians, show a message
        if (musicians.size === 0) {
            const message = document.createElement('p');
            message.className = 'text-muted mb-0';
            message.textContent = this.getTranslation('no_musicians_assigned', 'No hay músicos asignados a esta canción');
            message.setAttribute('role', 'status');
            crossSectionLinks.appendChild(message);
        }
    }
    
    navigateToMusicianSelector(musicianName) {
        /**
         * Navigate to musician selector section and pre-select the musician
         * Enhanced with NavigationStateManager for better reliability
         */
        if (window.NavigationStateManager) {
            window.NavigationStateManager.navigateToMusicianFromSong(musicianName);
        } else {
            // Fallback to original implementation
            if (window.hamburgerMenu) {
                window.hamburgerMenu.goToSection('musician-selector');
                sessionStorage.setItem('preselectedMusician', musicianName);
                this.announceToScreenReader(`Navegando al selector de músicos para ${musicianName}`);
            }
        }
    }
    
    showLoadingIndicator(message = null) {
        this.hideError();
        this.hideSongDetails();
        this.hideEmptyState();
        
        // Update loading message with Spanish translation
        const loadingText = this.loadingState.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message || this.getTranslation('loading', 'Cargando...');
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
    
    /**
     * Add keyboard shortcuts help display
     * Requirements: 2.5, 5.2
     */
    addKeyboardShortcutsHelp() {
        // Create keyboard shortcuts help element
        const helpElement = document.createElement('div');
        helpElement.id = 'keyboardShortcutsHelp';
        helpElement.className = 'keyboard-shortcuts-help';
        helpElement.innerHTML = `
            <div class="card border-info">
                <div class="card-header bg-info text-white">
                    <h6 class="mb-0">
                        <i class="bi bi-keyboard me-2" aria-hidden="true"></i>
                        ${this.getTranslation('keyboard_shortcuts', 'Atajos de Teclado')}
                    </h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-12 col-md-6">
                            <small class="text-muted">
                                <strong>Alt + →</strong> o <strong>Alt + N</strong><br>
                                ${this.getTranslation('next_song_shortcut', 'Siguiente canción')}
                            </small>
                        </div>
                        <div class="col-12 col-md-6">
                            <small class="text-muted">
                                <strong>Alt + ←</strong> o <strong>Alt + P</strong><br>
                                ${this.getTranslation('previous_song_shortcut', 'Canción anterior')}
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add CSS for the help element
        const style = document.createElement('style');
        style.textContent = `
            .keyboard-shortcuts-help {
                position: fixed;
                bottom: 20px;
                right: 20px;
                max-width: 350px;
                z-index: 1000;
                opacity: 0.9;
                transition: opacity 0.3s ease;
            }
            
            .keyboard-shortcuts-help:hover {
                opacity: 1;
            }
            
            @media (max-width: 768px) {
                .keyboard-shortcuts-help {
                    bottom: 10px;
                    right: 10px;
                    left: 10px;
                    max-width: none;
                }
            }
        `;
        
        // Add style to head if not already added
        if (!document.getElementById('keyboardShortcutsStyle')) {
            style.id = 'keyboardShortcutsStyle';
            document.head.appendChild(style);
        }
        
        // Add help element to page
        document.body.appendChild(helpElement);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (helpElement && helpElement.parentNode) {
                helpElement.style.opacity = '0.7';
            }
        }, 10000);
        
        // Hide on click
        helpElement.addEventListener('click', () => {
            helpElement.style.display = 'none';
        });
    }
    
    /**
     * Navigate to next song in order sequence
     * Requirements: 2.2, 2.5
     */
    navigateToNextSong() {
        if (!this.currentSongId) {
            this.showTemporaryMessage(this.getTranslation('no_song_selected', 'No hay canción seleccionada'), 'warning');
            return;
        }
        
        // Find current song in the songs array
        const currentSong = this.songsById.get(this.currentSongId);
        if (!currentSong || !currentSong.order) {
            this.showTemporaryMessage(this.getTranslation('no_order_info', 'La canción actual no tiene información de orden'), 'warning');
            return;
        }
        
        // Find next song by order
        const nextSong = this.songs.find(song => song.order && song.order > currentSong.order);
        
        if (nextSong) {
            this.songSelect.value = nextSong.song_id;
            this.handleSongSelection(nextSong.song_id);
            
            const message = `${this.getTranslation('navigated_to_next_song', 'Navegando a la siguiente canción')}: ${nextSong.display_name}`;
            this.showTemporaryMessage(message, 'success');
            this.announceToScreenReader(message);
        } else {
            const message = this.getTranslation('no_next_song', 'No hay siguiente canción en el repertorio');
            this.showTemporaryMessage(message, 'info');
            this.announceToScreenReader(message);
        }
    }
    
    /**
     * Navigate to previous song in order sequence
     * Requirements: 2.2, 2.5
     */
    navigateToPreviousSong() {
        if (!this.currentSongId) {
            this.showTemporaryMessage(this.getTranslation('no_song_selected', 'No hay canción seleccionada'), 'warning');
            return;
        }
        
        // Find current song in the songs array
        const currentSong = this.songsById.get(this.currentSongId);
        if (!currentSong || !currentSong.order) {
            this.showTemporaryMessage(this.getTranslation('no_order_info', 'La canción actual no tiene información de orden'), 'warning');
            return;
        }
        
        // Find previous song by order (find the highest order that's less than current)
        const previousSong = this.songs
            .filter(song => song.order && song.order < currentSong.order)
            .sort((a, b) => b.order - a.order)[0]; // Sort descending and take first
        
        if (previousSong) {
            this.songSelect.value = previousSong.song_id;
            this.handleSongSelection(previousSong.song_id);
            
            const message = `${this.getTranslation('navigated_to_previous_song', 'Navegando a la canción anterior')}: ${previousSong.display_name}`;
            this.showTemporaryMessage(message, 'success');
            this.announceToScreenReader(message);
        } else {
            const message = this.getTranslation('no_previous_song', 'No hay canción anterior en el repertorio');
            this.showTemporaryMessage(message, 'info');
            this.announceToScreenReader(message);
        }
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
            if (document.body.contains(announcement)) {
                document.body.removeChild(announcement);
            }
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
    
    // Handle viewport changes for responsive behavior
    handleViewportChange() {
        const viewportWidth = window.innerWidth;
        
        // Adjust card layout based on viewport
        if (viewportWidth < 576) {
            // Ensure single column layout on very small screens
            const assignments = document.querySelectorAll('#musicianAssignments .col');
            assignments.forEach(col => {
                col.className = 'col-12 mb-3';
            });
        }
        
        // Adjust cross-section links layout
        const crossSectionLinks = document.getElementById('crossSectionLinks');
        if (crossSectionLinks && viewportWidth < 576) {
            crossSectionLinks.classList.add('d-flex', 'flex-column');
            const buttons = crossSectionLinks.querySelectorAll('.btn');
            buttons.forEach(btn => {
                btn.classList.add('mb-2');
                btn.style.width = '100%';
            });
        } else if (crossSectionLinks) {
            crossSectionLinks.classList.remove('d-flex', 'flex-column');
            const buttons = crossSectionLinks.querySelectorAll('.btn');
            buttons.forEach(btn => {
                btn.classList.remove('mb-2');
                btn.style.width = '';
            });
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize hamburger menu system first
    window.hamburgerMenu = new HamburgerMenuSystem();
    
    // Create global instance for debugging/testing
    window.musicianSongSelector = new MusicianSongSelector();
    
    // Initialize musician selector (will be lazy-loaded when section is accessed)
    window.musicianSelector = new MusicianSelector();
    
    // Initialize Socket.IO integration for real-time features
    initializeSocketIOIntegration();
    
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

/**
 * Initialize Socket.IO integration for real-time features
 * Requirements: 4.5, 6.1, 6.2, 6.3
 */
function initializeSocketIOIntegration() {
    // Wait for connection manager to be available
    if (window.connectionManager) {
        setupGlobalSongSynchronization();
        setupRealTimeEventHandlers();
    } else {
        // Wait for connection manager to initialize
        setTimeout(() => {
            initializeSocketIOIntegration();
        }, 500);
    }
}

/**
 * Set up global song selection synchronization
 * Requirements: 4.5, 6.2
 */
function setupGlobalSongSynchronization() {
    if (!window.connectionManager) return;
    
    const socket = window.connectionManager.getSocket();
    if (!socket) return;
    
    // Listen for global song changes
    socket.on('song_changed', (data) => {
        handleGlobalSongChange(data);
    });
    
    // Listen for session synchronization events
    socket.on('global_session_joined', (data) => {
        handleGlobalSessionJoined(data);
    });
    
    // Listen for connection status updates
    window.connectionManager.on('connected', () => {
        handleSocketConnected();
    });
    
    window.connectionManager.on('disconnected', () => {
        handleSocketDisconnected();
    });
    
    window.connectionManager.on('reconnected', () => {
        handleSocketReconnected();
    });
}

/**
 * Set up real-time event handlers for song selection
 * Requirements: 4.5, 6.1, 6.2
 */
function setupRealTimeEventHandlers() {
    if (!window.connectionManager) return;
    
    const socket = window.connectionManager.getSocket();
    if (!socket) return;
    
    // Handle real-time song updates
    socket.on('current_song_state', (data) => {
        updateLocalSongState(data);
    });
    
    // Handle session count updates
    socket.on('session_count_updated', (data) => {
        updateSessionCount(data.connected_sessions);
    });
    
    // Handle next song updates
    socket.on('next_song_updated', (data) => {
        updateNextSongDisplay(data);
    });
}

/**
 * Handle global song change events
 * Requirements: 4.5, 6.2
 */
function handleGlobalSongChange(data) {
    console.info('Global song changed:', data);
    
    // Update song selector if available
    if (window.musicianSongSelector && data.song_id) {
        // Update dropdown selection without triggering change event
        const songSelect = window.musicianSongSelector.songSelect;
        if (songSelect && songSelect.value !== data.song_id) {
            songSelect.value = data.song_id;
            
            // Load song details if not already loaded
            if (window.musicianSongSelector.currentSongId !== data.song_id) {
                window.musicianSongSelector._loadSongDetails(data.song_id);
            }
        }
    }
    
    // Show notification to user
    if (data.song_data) {
        showGlobalSongChangeNotification(data.song_data);
    }
    
    // Announce to screen readers
    announceToScreenReader(`Canción global actualizada: ${data.song_data?.artist} - ${data.song_data?.song}`);
}

/**
 * Handle global session joined events
 * Requirements: 4.5, 6.1
 */
function handleGlobalSessionJoined(data) {
    console.info('Joined global session:', data);
    
    // Update session count display if available
    if (data.current_state?.connected_sessions) {
        updateSessionCount(data.current_state.connected_sessions);
    }
    
    // Update current song if available
    if (data.current_song_details) {
        handleGlobalSongChange({
            song_id: data.current_song_details.song_id,
            song_data: data.current_song_details
        });
    }
}

/**
 * Handle socket connected events
 * Requirements: 6.1, 6.3
 */
function handleSocketConnected() {
    console.info('Socket.IO connected for real-time features');
    
    // Join global session automatically
    const socket = window.connectionManager.getSocket();
    if (socket) {
        socket.emit('join_global_session', {
            client_info: {
                page: window.location.pathname,
                userAgent: navigator.userAgent.substring(0, 100),
                language: navigator.language
            }
        });
    }
    
    // Show connection success notification
    showConnectionNotification('Conectado al sistema en tiempo real', 'success');
    
    // Enable real-time features
    enableRealTimeFeatures();
}

/**
 * Handle socket disconnected events
 * Requirements: 6.3
 */
function handleSocketDisconnected() {
    console.warn('Socket.IO disconnected');
    
    // Show disconnection notification
    showConnectionNotification('Desconectado del sistema en tiempo real', 'warning');
    
    // Disable real-time features
    disableRealTimeFeatures();
}

/**
 * Handle socket reconnected events
 * Requirements: 6.3
 */
function handleSocketReconnected() {
    console.info('Socket.IO reconnected');
    
    // Show reconnection success notification
    showConnectionNotification('Reconectado al sistema en tiempo real', 'success');
    
    // Re-enable real-time features
    enableRealTimeFeatures();
    
    // Rejoin global session
    const socket = window.connectionManager.getSocket();
    if (socket) {
        socket.emit('join_global_session');
    }
}

/**
 * Update local song state from real-time updates
 * Requirements: 4.5, 6.2
 */
function updateLocalSongState(data) {
    if (!data) return;
    
    // Update current song display
    if (data.current_song_data && window.musicianSongSelector) {
        const songData = data.current_song_data;
        
        // Update song selector dropdown
        if (window.musicianSongSelector.songSelect && songData.song_id) {
            window.musicianSongSelector.songSelect.value = songData.song_id;
        }
        
        // Update song details display
        if (window.musicianSongSelector.currentSongId !== songData.song_id) {
            window.musicianSongSelector.displaySongDetails(songData);
        }
    }
    
    // Update session count
    if (typeof data.connected_sessions === 'number') {
        updateSessionCount(data.connected_sessions);
    }
}

/**
 * Update session count display
 * Requirements: 6.1, 6.2
 */
function updateSessionCount(count) {
    // Update any session count displays on the page
    const sessionCountElements = document.querySelectorAll('[data-session-count]');
    sessionCountElements.forEach(element => {
        element.textContent = count || 0;
    });
    
    // Update global selector if available
    if (window.globalSongSelector) {
        window.globalSongSelector.updateSessionCount(count);
    }
}

/**
 * Update next song display from real-time updates
 * Requirements: 4.5
 */
function updateNextSongDisplay(data) {
    if (!data || !window.musicianSongSelector) return;
    
    // Update next song widget
    const nextSongWidget = document.getElementById('nextSongWidget');
    const noNextSongWidget = document.getElementById('noNextSongWidget');
    
    if (data.next_song) {
        // Update next song information
        const nextSongTitle = document.getElementById('nextSongTitle');
        const nextSongArtist = document.getElementById('nextSongArtist');
        const nextSongOrder = document.getElementById('nextSongOrder');
        
        if (nextSongTitle) nextSongTitle.textContent = data.next_song.title;
        if (nextSongArtist) nextSongArtist.textContent = `por ${data.next_song.artist}`;
        if (nextSongOrder) nextSongOrder.textContent = `Orden: ${data.next_song.order}`;
        
        if (nextSongWidget) nextSongWidget.classList.remove('d-none');
        if (noNextSongWidget) noNextSongWidget.classList.add('d-none');
    } else {
        if (nextSongWidget) nextSongWidget.classList.add('d-none');
        if (noNextSongWidget) noNextSongWidget.classList.remove('d-none');
    }
}

/**
 * Show global song change notification
 * Requirements: 4.5, 6.2
 */
function showGlobalSongChangeNotification(songData) {
    if (!songData) return;
    
    const message = `Canción global: ${songData.artist} - ${songData.song}`;
    showTemporaryNotification(message, 'info', 'bi-broadcast');
}

/**
 * Show connection status notification
 * Requirements: 6.3
 */
function showConnectionNotification(message, type = 'info') {
    const iconClass = type === 'success' ? 'bi-wifi' : 
                     type === 'warning' ? 'bi-wifi-off' : 'bi-info-circle';
    showTemporaryNotification(message, type, iconClass);
}

/**
 * Show temporary notification
 * Requirements: 6.3
 */
function showTemporaryNotification(message, type = 'info', iconClass = 'bi-info-circle') {
    const alertClass = type === 'success' ? 'alert-success' : 
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 80px;
        right: 20px;
        z-index: 9999;
        max-width: 350px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="${iconClass} me-2" aria-hidden="true"></i>
            <div class="flex-grow-1">${message}</div>
            <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()" aria-label="Cerrar"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-dismiss after 4 seconds
    setTimeout(() => {
        if (notification && notification.parentNode) {
            notification.remove();
        }
    }, 4000);
}

/**
 * Enable real-time features
 * Requirements: 6.1, 6.2
 */
function enableRealTimeFeatures() {
    // Add real-time indicators to UI
    const realTimeIndicators = document.querySelectorAll('[data-realtime-indicator]');
    realTimeIndicators.forEach(indicator => {
        indicator.classList.add('realtime-active');
        indicator.setAttribute('title', 'Sincronización en tiempo real activa');
    });
    
    // Enable real-time song selection if on global selector page
    if (window.globalSongSelector) {
        window.globalSongSelector.isConnected = true;
    }
}

/**
 * Disable real-time features
 * Requirements: 6.3
 */
function disableRealTimeFeatures() {
    // Remove real-time indicators from UI
    const realTimeIndicators = document.querySelectorAll('[data-realtime-indicator]');
    realTimeIndicators.forEach(indicator => {
        indicator.classList.remove('realtime-active');
        indicator.setAttribute('title', 'Sincronización en tiempo real desactivada');
    });
    
    // Disable real-time song selection if on global selector page
    if (window.globalSongSelector) {
        window.globalSongSelector.isConnected = false;
    }
}

/**
 * Announce message to screen readers
 * Requirements: 6.3
 */
function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
        if (document.body.contains(announcement)) {
            document.body.removeChild(announcement);
        }
    }, 1000);
}

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

class MusicianSelector {
    constructor() {
        this.musicianSelect = document.getElementById('musicianSelect');
        this.musicianLoadingState = document.getElementById('musicianLoadingState');
        this.musicianErrorState = document.getElementById('musicianErrorState');
        this.musicianDetails = document.getElementById('musicianDetails');
        this.musicianEmptyState = document.getElementById('musicianEmptyState');
        this.musicianName = document.getElementById('musicianName');
        this.musicianSongCount = document.getElementById('musicianSongCount');
        this.musicianSongs = document.getElementById('musicianSongs');
        this.musicianErrorMessage = document.getElementById('musicianErrorMessage');
        
        // Spanish translations from server
        this.translations = window.translations || {};
        
        // Performance optimization: Cache data and DOM elements
        this.musicians = [];
        this.musiciansById = new Map(); // Fast lookup by ID
        this.currentMusicianId = null;
        this.lastRenderedMusicianId = null;
        this.musicianDetailsCache = new Map(); // Cache musician details to avoid re-fetching
        
        // Performance optimization: Reusable DOM elements
        this.songCardTemplate = null;
        this.createSongCardTemplate();
        
        // Performance optimization: Debounce rapid selections
        this.selectionTimeout = null;
        
        this.isInitialized = false;
    }
    
    getTranslation(key, defaultValue = key) {
        return this.translations[key] || defaultValue;
    }
    
    createSongCardTemplate() {
        /**
         * Create a reusable template for song cards to avoid repeated DOM creation
         */
        this.songCardTemplate = document.createElement('div');
        this.songCardTemplate.className = 'col-12 col-sm-6 col-lg-4 mb-3';
        this.songCardTemplate.innerHTML = `
            <div class="song-card-small">
                <div class="song-title"></div>
                <div class="song-artist"></div>
                <div class="song-duration"></div>
                <div class="song-instruments"></div>
                <a href="#" class="forward-link">
                    <i class="bi bi-arrow-right-circle me-1" aria-hidden="true"></i>
                    Ver en Selector de Canciones
                </a>
            </div>
        `;
    }
    
    init() {
        if (this.isInitialized) {
            return;
        }
        
        // Load musicians on initialization
        this.loadMusicians();
        
        // Set up event listeners
        this.musicianSelect.addEventListener('change', (e) => {
            this.handleMusicianSelection(e.target.value);
        });
        
        // Add keyboard navigation support
        this.musicianSelect.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                this.handleMusicianSelection(e.target.value);
            }
        });
        
        // Check for pre-selected musician from session storage
        const preselectedMusician = sessionStorage.getItem('preselectedMusician');
        if (preselectedMusician) {
            sessionStorage.removeItem('preselectedMusician');
            // Wait for musicians to load, then select
            setTimeout(() => {
                this.selectMusicianByName(preselectedMusician);
            }, 500);
        }
        
        // Show empty state initially
        this.showEmptyState();
        
        this.isInitialized = true;
    }
    
    async loadMusicians() {
        try {
            this.showLoadingIndicator(this.getTranslation('data_loading', 'Cargando datos...'));
            
            const response = await fetch('/api/musicians');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data.musicians && Array.isArray(data.musicians)) {
                this.musicians = data.musicians;
                
                // Performance optimization: Create fast lookup map
                this.musiciansById.clear();
                this.musicians.forEach(musician => {
                    this.musiciansById.set(musician.id, musician);
                });
                
                this.populateDropdown(data.musicians);
                this.hideLoadingIndicator();
                this.showEmptyState();
            } else {
                throw new Error(this.getTranslation('invalid_data_format', 'Formato de datos inválido'));
            }
        } catch (error) {
            console.error('Error loading musicians:', error);
            this.hideLoadingIndicator();
            this.showError(error.message || this.getTranslation('failed_to_load_musicians', 'Error al cargar los músicos'));
        }
    }
    
    populateDropdown(musicians) {
        // Performance optimization: Use document fragment for batch DOM updates
        const fragment = document.createDocumentFragment();
        
        // Create default option with Spanish text
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = this.getTranslation('select_musician', 'Seleccionar un músico...');
        fragment.appendChild(defaultOption);
        
        // Musicians are already sorted from the server
        musicians.forEach(musician => {
            const option = document.createElement('option');
            option.value = musician.id;
            option.textContent = musician.name;
            fragment.appendChild(option);
        });
        
        // Single DOM update
        this.musicianSelect.innerHTML = '';
        this.musicianSelect.appendChild(fragment);
        
        // Enable the dropdown
        this.musicianSelect.disabled = false;
    }
    
    async handleMusicianSelection(musicianId) {
        if (!musicianId) {
            this.currentMusicianId = null;
            this.hideMusicianDetails();
            this.showEmptyState();
            return;
        }
        
        // Performance optimization: Prevent duplicate requests
        if (this.currentMusicianId === musicianId) {
            return;
        }
        
        // Performance optimization: Debounce rapid selections
        if (this.selectionTimeout) {
            clearTimeout(this.selectionTimeout);
        }
        
        this.selectionTimeout = setTimeout(async () => {
            await this._loadMusicianDetails(musicianId);
        }, 100); // 100ms debounce
    }
    
    async _loadMusicianDetails(musicianId) {
        this.currentMusicianId = musicianId;
        
        // Performance optimization: Check cache first
        if (this.musicianDetailsCache.has(musicianId)) {
            const cachedData = this.musicianDetailsCache.get(musicianId);
            this.displayMusicianDetails(cachedData);
            return;
        }
        
        this.showLoadingIndicator(this.getTranslation('data_loading', 'Cargando datos...'));
        
        try {
            const response = await fetch(`/api/musician/${encodeURIComponent(musicianId)}`);
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error(this.getTranslation('musician_not_found', 'Músico no encontrado'));
                } else {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data && data.id) {
                // Performance optimization: Cache the response
                this.musicianDetailsCache.set(musicianId, data);
                this.displayMusicianDetails(data);
            } else {
                throw new Error(this.getTranslation('invalid_data_format', 'Formato de datos inválido'));
            }
        } catch (error) {
            console.error('Error loading musician details:', error);
            this.hideLoadingIndicator();
            this.showError(error.message || this.getTranslation('failed_to_load_musician_details', 'Error al cargar los detalles del músico'));
            
            // Reset dropdown selection on error
            this.musicianSelect.value = '';
            this.currentMusicianId = null;
        }
    }
    
    displayMusicianDetails(musicianData) {
        // Performance optimization: Skip re-rendering if same musician
        if (this.lastRenderedMusicianId === musicianData.id) {
            this.hideLoadingIndicator();
            this.hideError();
            this.hideEmptyState();
            this.musicianDetails.classList.remove('d-none');
            return;
        }
        
        this.hideLoadingIndicator();
        this.hideError();
        this.hideEmptyState();
        
        // Performance optimization: Batch DOM updates
        this.updateMusicianInfo(musicianData);
        this.updateMusicianSongs(musicianData.songs);
        
        // Show musician details with smooth transition
        this.musicianDetails.classList.remove('d-none');
        
        // Cache the last rendered musician ID
        this.lastRenderedMusicianId = musicianData.id;
        
        // Announce to screen readers
        this.announceToScreenReader(`Loaded details for musician ${musicianData.name}`);
    }
    
    updateMusicianInfo(musicianData) {
        /**
         * Performance optimization: Update musician info elements efficiently
         */
        // Use textContent for better performance than innerHTML
        this.musicianName.textContent = musicianData.name;
        
        const songCount = musicianData.songs.length;
        const songText = songCount === 1 ? 'canción' : 'canciones';
        this.musicianSongCount.textContent = `${songCount} ${songText}`;
    }
    
    updateMusicianSongs(songs) {
        /**
         * Performance optimization: Efficient DOM manipulation for songs with Spanish translations and enhanced accessibility
         * Enhanced with better order display - Requirements: 2.2, 5.1, 5.2
         */
        // Performance optimization: Use document fragment for batch updates
        const fragment = document.createDocumentFragment();
        
        songs.forEach((song, index) => {
            // Clone the template for better performance
            const col = this.songCardTemplate.cloneNode(true);
            
            // Update the cloned elements
            const card = col.querySelector('.song-card-small');
            const songTitle = col.querySelector('.song-title');
            const songArtist = col.querySelector('.song-artist');
            const songDuration = col.querySelector('.song-duration');
            const songInstruments = col.querySelector('.song-instruments');
            const forwardLink = col.querySelector('.forward-link');
            
            // Enhanced content with order information and Spanish formatting
            if (song.order) {
                songTitle.innerHTML = `
                    <span class="badge bg-warning text-dark me-2" aria-label="${this.getTranslation('order_label', 'Orden')} ${song.order}">
                        ${song.order}
                    </span>
                    ${song.song}
                `;
            } else {
                songTitle.textContent = song.song;
            }
            
            songArtist.textContent = `${this.getTranslation('by_artist', 'por')} ${song.artist}`;
            songDuration.textContent = `${this.getTranslation('duration_label', 'Duración')}: ${song.duration}`;
            
            // Display instruments in Spanish with enhanced formatting
            const instrumentsSpanish = song.instruments_spanish || song.instruments || [];
            if (instrumentsSpanish.length > 0) {
                songInstruments.innerHTML = `
                    <strong>${this.getTranslation('instruments_label', 'Instrumentos')}:</strong> 
                    ${instrumentsSpanish.join(', ')}
                `;
            } else {
                songInstruments.textContent = `${this.getTranslation('instruments_label', 'Instrumentos')}: ${this.getTranslation('no_instruments', 'Ninguno')}`;
            }
            
            // Enhanced accessibility attributes with order information
            card.setAttribute('role', 'listitem');
            card.setAttribute('tabindex', '0');
            const orderInfo = song.order ? `, ${this.getTranslation('order_label', 'orden')} ${song.order}` : '';
            card.setAttribute('aria-label', 
                `${song.song} ${this.getTranslation('by_artist', 'por')} ${song.artist}${orderInfo}, ${this.getTranslation('duration_label', 'duración')} ${song.duration}`
            );
            
            // Enhanced forward link with Spanish text and accessibility
            forwardLink.innerHTML = `
                <i class="bi bi-arrow-right-circle me-1" aria-hidden="true"></i>
                ${this.getTranslation('view_in_song_selector', 'Ver en Selector de Canciones')}
            `;
            forwardLink.setAttribute('aria-label', 
                `${this.getTranslation('view_song_in_selector', 'Ver')} ${song.song} ${this.getTranslation('in_song_selector', 'en el selector de canciones')}`
            );
            forwardLink.setAttribute('role', 'button');
            forwardLink.setAttribute('tabindex', '0');
            
            // Add keyboard navigation support for the card
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.navigateToSongSelector(song.id);
                }
            });
            
            // Add keyboard navigation support for the forward link
            forwardLink.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.navigateToSongSelector(song.id);
                }
            });
            
            forwardLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToSongSelector(song.id);
            });
            
            // Add hover effects for better UX
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-2px)';
                card.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.15)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
                card.style.boxShadow = '';
            });
            
            fragment.appendChild(col);
        });
        
        // Single DOM update
        this.musicianSongs.innerHTML = '';
        this.musicianSongs.appendChild(fragment);
        
        // If no songs, show a message with proper accessibility and Spanish text
        if (songs.length === 0) {
            const message = document.createElement('div');
            message.className = 'col-12 text-center py-4';
            message.setAttribute('role', 'status');
            message.innerHTML = `
                <i class="bi bi-music-note display-4 text-muted" aria-hidden="true"></i>
                <p class="mt-3 text-muted">${this.getTranslation('no_songs_assigned', 'Este músico no tiene canciones asignadas')}</p>
            `;
            this.musicianSongs.appendChild(message);
        }
    }
    
    navigateToSongSelector(songId) {
        /**
         * Navigate to song selector section and pre-select the song
         * Enhanced with NavigationStateManager for better reliability
         */
        if (window.NavigationStateManager) {
            window.NavigationStateManager.navigateToSongFromMusician(songId);
        } else {
            // Fallback to original implementation
            if (window.hamburgerMenu) {
                window.hamburgerMenu.goToSection('song-selector');
                sessionStorage.setItem('preselectedSong', songId);
                this.announceToScreenReader('Navegando al selector de canciones');
                
                // Pre-select the song in the song selector
                setTimeout(() => {
                    if (window.musicianSongSelector && window.musicianSongSelector.songSelect) {
                        window.musicianSongSelector.songSelect.value = songId;
                        window.musicianSongSelector.handleSongSelection(songId);
                    }
                }, 300);
            }
        }
    }
    
    selectMusicianByName(musicianName) {
        /**
         * Programmatically select a musician by name
         */
        const musician = this.musicians.find(m => m.name === musicianName);
        if (musician) {
            this.musicianSelect.value = musician.id;
            this.handleMusicianSelection(musician.id);
        }
    }
    
    showLoadingIndicator(message = null) {
        this.hideError();
        this.hideMusicianDetails();
        this.hideEmptyState();
        
        // Update loading message with Spanish translation
        const loadingText = this.musicianLoadingState.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message || this.getTranslation('loading', 'Cargando...');
        }
        
        this.musicianLoadingState.classList.remove('d-none');
        
        // Disable dropdown during loading
        this.musicianSelect.disabled = true;
    }
    
    hideLoadingIndicator() {
        this.musicianLoadingState.classList.add('d-none');
        this.musicianSelect.disabled = false;
    }
    
    showError(message) {
        this.hideLoadingIndicator();
        this.hideMusicianDetails();
        this.hideEmptyState();
        
        this.musicianErrorMessage.textContent = message;
        this.musicianErrorState.classList.remove('d-none');
        
        // Announce error to screen readers
        this.announceToScreenReader(`Error: ${message}`);
    }
    
    hideError() {
        this.musicianErrorState.classList.add('d-none');
    }
    
    showEmptyState() {
        this.hideError();
        this.hideMusicianDetails();
        this.hideLoadingIndicator();
        this.musicianEmptyState.classList.remove('d-none');
    }
    
    hideEmptyState() {
        this.musicianEmptyState.classList.add('d-none');
    }
    
    hideMusicianDetails() {
        this.musicianDetails.classList.add('d-none');
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
            if (document.body.contains(announcement)) {
                document.body.removeChild(announcement);
            }
        }, 1000);
    }
    
    // Public method to get current musician data
    getCurrentMusician() {
        return this.musicians.find(musician => musician.id === this.currentMusicianId) || null;
    }
    
    // Public method to refresh data
    async refresh() {
        this.currentMusicianId = null;
        this.lastRenderedMusicianId = null;
        this.musicianSelect.value = '';
        
        // Performance optimization: Clear caches on refresh
        this.musiciansById.clear();
        this.musicianDetailsCache.clear();
        
        await this.loadMusicians();
    }
    
    // Performance optimization: Clear caches when needed
    clearCache() {
        this.musicianDetailsCache.clear();
        this.lastRenderedMusicianId = null;
    }
    
    // Performance optimization: Preload popular musicians
    async preloadPopularMusicians() {
        // Preload first 3 musicians for better perceived performance
        const musiciansToPreload = this.musicians.slice(0, 3);
        
        for (const musician of musiciansToPreload) {
            if (!this.musicianDetailsCache.has(musician.id)) {
                try {
                    const response = await fetch(`/api/musician/${encodeURIComponent(musician.id)}`);
                    if (response.ok) {
                        const data = await response.json();
                        this.musicianDetailsCache.set(musician.id, data);
                    }
                } catch (error) {
                    // Silently fail preloading - not critical
                    console.debug('Preload failed for musician:', musician.id);
                }
            }
        }
    }
    
    // Handle viewport changes for responsive behavior
    handleViewportChange() {
        const viewportWidth = window.innerWidth;
        
        // Adjust musician songs grid layout based on viewport
        if (viewportWidth < 576) {
            // Ensure single column layout on very small screens
            const songCards = document.querySelectorAll('#musicianSongs .col-12');
            songCards.forEach(col => {
                col.className = 'col-12 mb-3';
            });
        } else if (viewportWidth < 768) {
            // Two columns for small screens
            const songCards = document.querySelectorAll('#musicianSongs .col-12');
            songCards.forEach(col => {
                col.className = 'col-12 col-sm-6 mb-3';
            });
        } else if (viewportWidth < 992) {
            // Three columns for medium screens
            const songCards = document.querySelectorAll('#musicianSongs .col-12');
            songCards.forEach(col => {
                col.className = 'col-12 col-sm-6 col-lg-4 mb-3';
            });
        } else {
            // Four columns for large screens
            const songCards = document.querySelectorAll('#musicianSongs .col-12');
            songCards.forEach(col => {
                col.className = 'col-12 col-sm-6 col-lg-4 col-xl-3 mb-3';
            });
        }
        
        // Adjust musician card layout
        const musicianCard = document.querySelector('.musician-card');
        if (musicianCard && viewportWidth < 576) {
            musicianCard.style.margin = '0.5rem 0';
        } else if (musicianCard) {
            musicianCard.style.margin = '';
        }
    }
}


// Add Socket.IO integration styles
const socketIOStyles = document.createElement('style');
socketIOStyles.textContent = `
/* Real-time connection indicators */
.realtime-active {
    position: relative;
}

.realtime-active::after {
    content: '';
    position: absolute;
    top: -2px;
    right: -2px;
    width: 8px;
    height: 8px;
    background-color: #28a745;
    border-radius: 50%;
    border: 2px solid white;
    animation: pulse-realtime 2s infinite;
}

@keyframes pulse-realtime {
    0%, 100% { 
        opacity: 1; 
        transform: scale(1);
    }
    50% { 
        opacity: 0.7; 
        transform: scale(1.2);
    }
}

/* Connection status styles */
.connection-status-container.connected {
    border-color: #28a745;
    background: rgba(40, 167, 69, 0.1);
}

.connection-status-container.disconnected {
    border-color: #dc3545;
    background: rgba(220, 53, 69, 0.1);
}

.connection-status-container.reconnecting {
    border-color: #ffc107;
    background: rgba(255, 193, 7, 0.1);
}

/* Global selector specific styles */
.global-song-card {
    transition: all 0.3s ease;
}

.global-song-card.updating {
    opacity: 0.7;
    transform: scale(0.98);
}

/* Notification styles */
.notification-enter {
    animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Socket.IO integration styles */
.socket-connected .connection-indicator {
    color: #28a745;
}

.socket-disconnected .connection-indicator {
    color: #dc3545;
}

.socket-reconnecting .connection-indicator {
    color: #ffc107;
    animation: spin 1s linear infinite;
}

/* Manual reconnect button */
.manual-reconnect-btn {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Session count badge */
.session-count-badge {
    transition: all 0.3s ease;
}

.session-count-badge.updated {
    animation: bounce 0.6s ease-in-out;
}

@keyframes bounce {
    0%, 20%, 60%, 100% {
        transform: translateY(0);
    }
    40% {
        transform: translateY(-10px);
    }
    80% {
        transform: translateY(-5px);
    }
}

/* Real-time sync indicator */
.sync-indicator {
    display: inline-flex;
    align-items: center;
    transition: all 0.3s ease;
}

.sync-indicator.syncing {
    color: #ffc107;
}

.sync-indicator.synced {
    color: #28a745;
}

.sync-indicator.error {
    color: #dc3545;
}

/* Loading states for real-time updates */
.realtime-loading {
    position: relative;
    overflow: hidden;
}

.realtime-loading::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #007bff, transparent);
    animation: loading-sweep 1.5s infinite;
}

@keyframes loading-sweep {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* Mobile responsive adjustments */
@media (max-width: 576px) {
    .connection-status-container {
        font-size: 0.875rem;
    }
    
    .realtime-active::after {
        width: 6px;
        height: 6px;
    }
}
`;
document.head.appendChild(socketIOStyles);