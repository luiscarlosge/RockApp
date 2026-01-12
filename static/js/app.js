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
                    case '3':
                        e.preventDefault();
                        this.navigateToSection('live-performance');
                        this.announceToScreenReader('Navegando a la presentación en vivo');
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
        
        if (window.livePerformanceManager && window.livePerformanceManager.handleViewportChange) {
            window.livePerformanceManager.handleViewportChange();
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
            'musician-selector': 'Selector de Músicos',
            'live-performance': 'Presentación en Vivo'
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
            case 'live-performance':
                if (window.livePerformanceManager && !window.livePerformanceManager.isInitialized) {
                    window.livePerformanceManager.init();
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
        
        // Listen for data consistency changes
        window.addEventListener('dataConsistencyChange', () => {
            this.handleDataConsistencyChange();
        });
        
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
         * Performance optimization: Update song info elements efficiently
         */
        // Use textContent for better performance than innerHTML
        this.songTitle.textContent = songData.song;
        this.songArtist.textContent = `by ${songData.artist}`;
        this.songDuration.textContent = songData.time;
    }
    
    updateMusicianAssignments(assignments) {
        /**
         * Performance optimization: Efficient DOM manipulation for assignments with Spanish translations and enhanced accessibility
         */
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
         */
        // Use the hamburger menu system to navigate
        if (window.hamburgerMenu) {
            window.hamburgerMenu.goToSection('musician-selector');
            
            // Store the musician name to pre-select when the section loads
            sessionStorage.setItem('preselectedMusician', musicianName);
            
            // Announce navigation to screen readers
            this.announceToScreenReader(`Navegando al selector de músicos para ${musicianName}`);
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
    
    // Initialize live performance manager (will be lazy-loaded when section is accessed)
    window.livePerformanceManager = new LivePerformanceManager();
    
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
            
            // Set content
            songTitle.textContent = song.song;
            songArtist.textContent = `por ${song.artist}`;
            songDuration.textContent = `Duración: ${song.duration}`;
            songInstruments.textContent = `Instrumentos: ${song.instruments.join(', ')}`;
            
            // Enhanced accessibility attributes
            card.setAttribute('role', 'listitem');
            card.setAttribute('tabindex', '0');
            card.setAttribute('aria-label', `${song.song} por ${song.artist}, duración ${song.duration}`);
            
            // Set up forward link with enhanced accessibility
            forwardLink.setAttribute('aria-label', `Ver ${song.song} en el selector de canciones`);
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
            
            fragment.appendChild(col);
        });
        
        // Single DOM update
        this.musicianSongs.innerHTML = '';
        this.musicianSongs.appendChild(fragment);
        
        // If no songs, show a message with proper accessibility
        if (songs.length === 0) {
            const message = document.createElement('div');
            message.className = 'col-12 text-center py-4';
            message.setAttribute('role', 'status');
            message.innerHTML = `
                <i class="bi bi-music-note display-4 text-muted" aria-hidden="true"></i>
                <p class="mt-3 text-muted">Este músico no tiene canciones asignadas</p>
            `;
            this.musicianSongs.appendChild(message);
        }
    }
    
    navigateToSongSelector(songId) {
        /**
         * Navigate to song selector section and pre-select the song
         */
        // Use the hamburger menu system to navigate
        if (window.hamburgerMenu) {
            window.hamburgerMenu.goToSection('song-selector');
            
            // Store the song ID to pre-select when the section loads
            sessionStorage.setItem('preselectedSong', songId);
            
            // Announce navigation to screen readers
            this.announceToScreenReader(`Navegando al selector de canciones`);
            
            // Pre-select the song in the song selector
            setTimeout(() => {
                if (window.musicianSongSelector && window.musicianSongSelector.songSelect) {
                    window.musicianSongSelector.songSelect.value = songId;
                    window.musicianSongSelector.handleSongSelection(songId);
                }
            }, 300);
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

class LivePerformanceManager {
    constructor() {
        this.currentSongDisplay = document.getElementById('currentSongDisplay');
        this.nextSongDisplay = document.getElementById('nextSongDisplay');
        
        // Spanish translations from server
        this.translations = window.translations || {};
        
        // Performance optimization: Cache data and DOM elements
        this.performanceState = null;
        this.lastRenderedState = null;
        this.refreshInterval = null;
        
        // Performance optimization: Reusable DOM elements
        this.songDisplayTemplate = null;
        this.createSongDisplayTemplate();
        
        this.isInitialized = false;
    }
    
    getTranslation(key, defaultValue = key) {
        return this.translations[key] || defaultValue;
    }
    
    createSongDisplayTemplate() {
        /**
         * Create a reusable template for song display to avoid repeated DOM creation
         */
        this.songDisplayTemplate = document.createElement('div');
        this.songDisplayTemplate.innerHTML = `
            <div class="song-info mb-3">
                <h4 class="song-title mb-1"></h4>
                <p class="song-artist text-muted mb-2"></p>
                <div class="song-duration badge mb-3"></div>
            </div>
            <div class="musicians-list">
                <h5 class="mb-3">Músicos Asignados</h5>
                <div class="musicians-grid row g-2">
                    <!-- Musicians will be populated here -->
                </div>
            </div>
        `;
    }
    
    init() {
        if (this.isInitialized) {
            return;
        }
        
        // Load initial performance state
        this.loadPerformanceState();
        
        // Set up auto-refresh every 30 seconds for real-time updates
        this.refreshInterval = setInterval(() => {
            this.loadPerformanceState();
        }, 30000); // 30 seconds
        
        this.isInitialized = true;
        console.log('Live Performance Manager initialized');
    }
    
    async loadPerformanceState() {
        try {
            const response = await fetch('/api/live-performance');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.performanceState = data;
            this.displayPerformanceState(data);
            
        } catch (error) {
            console.error('Error loading live performance state:', error);
            this.showError(error.message || this.getTranslation('failed_to_load_performance', 'Error al cargar el estado de la presentación'));
        }
    }
    
    displayPerformanceState(state) {
        // Performance optimization: Skip re-rendering if same state
        const stateHash = JSON.stringify(state);
        if (this.lastRenderedState === stateHash) {
            return;
        }
        
        // Update current song display
        this.updateSongDisplay(this.currentSongDisplay, state.current_song, 'current');
        
        // Update next song display
        this.updateSongDisplay(this.nextSongDisplay, state.next_song, 'next');
        
        // Cache the last rendered state
        this.lastRenderedState = stateHash;
        
        // Announce changes to screen readers
        if (state.current_song) {
            this.announceToScreenReader(`Canción actual: ${state.current_song.full_title}`);
        }
        if (state.next_song) {
            this.announceToScreenReader(`Próxima canción: ${state.next_song.full_title}`);
        }
    }
    
    updateSongDisplay(container, songData, type) {
        /**
         * Update song display container with song information
         */
        if (!songData) {
            // Show empty state
            const emptyMessage = type === 'current' 
                ? 'No hay canción actual seleccionada'
                : 'No hay próxima canción seleccionada';
            
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-music-note display-4 text-muted" aria-hidden="true"></i>
                    <p class="mt-3 text-muted">${emptyMessage}</p>
                </div>
            `;
            return;
        }
        
        // Clone the template for better performance
        const songDisplay = this.songDisplayTemplate.cloneNode(true);
        
        // Update song information
        const songTitle = songDisplay.querySelector('.song-title');
        const songArtist = songDisplay.querySelector('.song-artist');
        const songDuration = songDisplay.querySelector('.song-duration');
        const musiciansGrid = songDisplay.querySelector('.musicians-grid');
        
        songTitle.textContent = songData.title;
        songArtist.textContent = `por ${songData.artist}`;
        songDuration.textContent = `Duración: ${songData.duration}`;
        
        // Update musicians list
        this.updateMusiciansGrid(musiciansGrid, songData.musicians);
        
        // Replace container content
        container.innerHTML = '';
        container.appendChild(songDisplay);
    }
    
    updateMusiciansGrid(container, musicians) {
        /**
         * Update musicians grid with musician assignments
         */
        if (!musicians || musicians.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-3">
                    <p class="text-muted mb-0">No hay músicos asignados</p>
                </div>
            `;
            return;
        }
        
        // Performance optimization: Use document fragment for batch updates
        const fragment = document.createDocumentFragment();
        
        musicians.forEach(musician => {
            const col = document.createElement('div');
            col.className = 'col-12 col-sm-6 col-lg-4 mb-2';
            
            col.innerHTML = `
                <div class="musician-assignment">
                    <div class="musician-name">${musician.name}</div>
                    <div class="instrument-name">${musician.instrument}</div>
                </div>
            `;
            
            fragment.appendChild(col);
        });
        
        // Single DOM update
        container.innerHTML = '';
        container.appendChild(fragment);
    }
    
    showError(message) {
        // Show error in both displays
        const errorHtml = `
            <div class="alert alert-danger" role="alert">
                <div class="d-flex align-items-center">
                    <i class="bi bi-exclamation-triangle-fill me-2" aria-hidden="true"></i>
                    <div>
                        <h5 class="alert-heading mb-1">Error</h5>
                        <p class="mb-0">${message}</p>
                    </div>
                </div>
            </div>
        `;
        
        this.currentSongDisplay.innerHTML = errorHtml;
        this.nextSongDisplay.innerHTML = errorHtml;
        
        // Announce error to screen readers
        this.announceToScreenReader(`Error: ${message}`);
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
    
    // Public method to refresh performance state
    async refresh() {
        await this.loadPerformanceState();
    }
    
    // Public method to get current performance state
    getPerformanceState() {
        return this.performanceState;
    }
    
    // Cleanup method
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
        this.isInitialized = false;
    }
    
    // Handle viewport changes for responsive behavior
    handleViewportChange() {
        const viewportWidth = window.innerWidth;
        
        // Adjust musicians grid layout based on viewport
        const musiciansGrids = document.querySelectorAll('.musicians-grid');
        musiciansGrids.forEach(grid => {
            const musicianCols = grid.querySelectorAll('.col-12');
            
            if (viewportWidth < 576) {
                // Single column for very small screens
                musicianCols.forEach(col => {
                    col.className = 'col-12 mb-2';
                });
            } else if (viewportWidth < 768) {
                // Two columns for small screens
                musicianCols.forEach(col => {
                    col.className = 'col-12 col-sm-6 mb-2';
                });
            } else if (viewportWidth < 992) {
                // Three columns for medium screens
                musicianCols.forEach(col => {
                    col.className = 'col-12 col-sm-6 col-lg-4 mb-2';
                });
            } else {
                // Four columns for large screens
                musicianCols.forEach(col => {
                    col.className = 'col-12 col-sm-6 col-lg-4 col-xl-3 mb-2';
                });
            }
        });
        
        // Adjust performance cards layout
        const performanceCards = document.querySelectorAll('.performance-card');
        performanceCards.forEach(card => {
            if (viewportWidth < 576) {
                card.style.marginBottom = '1rem';
            } else {
                card.style.marginBottom = '';
            }
        });
        
        // Adjust song info layout for small screens
        const songInfos = document.querySelectorAll('.song-info');
        songInfos.forEach(info => {
            const title = info.querySelector('.song-title');
            const artist = info.querySelector('.song-artist');
            const duration = info.querySelector('.song-duration');
            
            if (viewportWidth < 576) {
                if (title) title.style.fontSize = '1.1rem';
                if (artist) artist.style.fontSize = '0.9rem';
                if (duration) {
                    duration.style.fontSize = '0.8rem';
                    duration.style.padding = '0.4rem 0.8rem';
                }
            } else {
                if (title) title.style.fontSize = '';
                if (artist) artist.style.fontSize = '';
                if (duration) {
                    duration.style.fontSize = '';
                    duration.style.padding = '';
                }
            }
        });
    }
}