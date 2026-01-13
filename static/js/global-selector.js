/**
 * Global Song Selector for Real-time Synchronization
 * Handles global song selection interface and real-time updates
 * Requirements: 4.1, 4.3, 4.4, 4.5, 6.1, 6.2, 6.3
 */

class GlobalSongSelector {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentGlobalSong = null;
        this.connectedSessions = 0;
        this.lastUpdateTime = null;
        
        // DOM elements
        this.songSelect = null;
        this.currentSongDisplay = null;
        this.nextSongDisplay = null;
        this.sessionCountDisplay = null;
        this.lastUpdateDisplay = null;
        this.loadingIndicator = null;
        this.errorDisplay = null;
        
        // Spanish translations
        this.translations = window.translations || {};
        
        // Cache for song data
        this.songsCache = new Map();
        this.songDetailsCache = new Map();
        
        this.init();
    }
    
    getTranslation(key, defaultValue = key) {
        return this.translations[key] || defaultValue;
    }
    
    init() {
        this.initializeDOM();
        this.setupSocketConnection();
        this.loadSongs();
        this.setupEventListeners();
    }
    
    initializeDOM() {
        /**
         * Initialize DOM elements and create interface
         */
        // Get or create main container
        let container = document.getElementById('global-selector-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'global-selector-container';
            container.className = 'container-fluid py-4';
            document.body.appendChild(container);
        }
        
        // Create interface HTML
        container.innerHTML = `
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-warning text-dark">
                            <h2 class="card-title mb-0">
                                <i class="bi bi-broadcast me-2" aria-hidden="true"></i>
                                ${this.getTranslation('global_selector_title', 'Selector Global de Canciones')}
                            </h2>
                        </div>
                        <div class="card-body">
                            <!-- Connection Status -->
                            <div class="row mb-4">
                                <div class="col-12">
                                    <div class="alert alert-info d-flex align-items-center" id="connection-status-alert">
                                        <i class="bi bi-info-circle me-2" aria-hidden="true"></i>
                                        <div>
                                            <strong>${this.getTranslation('connection_status', 'Estado de conexión')}:</strong>
                                            <span id="connection-status-text">${this.getTranslation('disconnected', 'Desconectado')}</span>
                                            <br>
                                            <small class="text-muted">
                                                <span id="session-count-display">0</span> ${this.getTranslation('connected_users', 'usuarios conectados')}
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Song Selection -->
                            <div class="row mb-4">
                                <div class="col-12 col-md-6">
                                    <label for="global-song-select" class="form-label">
                                        <i class="bi bi-music-note-beamed me-1" aria-hidden="true"></i>
                                        ${this.getTranslation('select_global_song', 'Seleccionar canción global')}
                                    </label>
                                    <select class="form-select" id="global-song-select" disabled>
                                        <option value="">${this.getTranslation('loading', 'Cargando...')}</option>
                                    </select>
                                </div>
                                <div class="col-12 col-md-6 d-flex align-items-end">
                                    <button type="button" class="btn btn-warning" id="refresh-songs-btn" disabled>
                                        <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>
                                        ${this.getTranslation('refresh', 'Actualizar')}
                                    </button>
                                </div>
                            </div>
                            
                            <!-- Loading Indicator -->
                            <div class="row mb-4 d-none" id="loading-indicator">
                                <div class="col-12">
                                    <div class="d-flex align-items-center">
                                        <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
                                        <span>${this.getTranslation('loading', 'Cargando...')}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Error Display -->
                            <div class="row mb-4 d-none" id="error-display">
                                <div class="col-12">
                                    <div class="alert alert-danger" role="alert">
                                        <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>
                                        <span id="error-message"></span>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Current Song Display -->
                            <div class="row">
                                <div class="col-12">
                                    <div class="card border-warning">
                                        <div class="card-header bg-light">
                                            <h3 class="card-title mb-0">
                                                <i class="bi bi-play-circle me-2" aria-hidden="true"></i>
                                                ${this.getTranslation('current_selection', 'Selección actual')}
                                            </h3>
                                        </div>
                                        <div class="card-body" id="current-song-display">
                                            <div class="text-center text-muted py-4">
                                                <i class="bi bi-music-note display-4" aria-hidden="true"></i>
                                                <p class="mt-3">${this.getTranslation('no_current_song', 'No hay canción actual seleccionada')}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Last Update Info -->
                            <div class="row mt-3">
                                <div class="col-12">
                                    <small class="text-muted" id="last-update-display">
                                        ${this.getTranslation('no_updates', 'Sin actualizaciones')}
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Store DOM element references
        this.songSelect = document.getElementById('global-song-select');
        this.currentSongDisplay = document.getElementById('current-song-display');
        this.sessionCountDisplay = document.getElementById('session-count-display');
        this.lastUpdateDisplay = document.getElementById('last-update-display');
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.errorDisplay = document.getElementById('error-display');
        this.connectionStatusText = document.getElementById('connection-status-text');
        this.connectionStatusAlert = document.getElementById('connection-status-alert');
        this.refreshBtn = document.getElementById('refresh-songs-btn');
    }
    
    setupSocketConnection() {
        /**
         * Set up SocketIO connection for real-time features
         * Requirements: 4.5, 6.1, 6.2, 6.3
         */
        // Wait for connection manager to be available
        if (window.connectionManager) {
            this.socket = window.connectionManager.getSocket();
            this.setupSocketEventHandlers();
            
            // Listen for connection manager events
            window.connectionManager.on('connected', (data) => {
                this.handleSocketConnect(data);
            });
            
            window.connectionManager.on('disconnected', (data) => {
                this.handleSocketDisconnect(data);
            });
            
            window.connectionManager.on('reconnected', (data) => {
                this.handleSocketReconnect(data);
            });
            
            window.connectionManager.on('connection_error', (data) => {
                this.handleConnectionError(data);
            });
            
            window.connectionManager.on('reconnect_attempt', (data) => {
                this.handleReconnectAttempt(data);
            });
            
            window.connectionManager.on('reconnect_failed', (data) => {
                this.handleReconnectFailed(data);
            });
            
            // Check if already connected
            if (window.connectionManager.isSocketConnected()) {
                this.handleSocketConnect({ sessionId: this.socket.id });
            } else {
                this.updateConnectionStatus('disconnected', this.getTranslation('disconnected', 'Desconectado'));
            }
        } else {
            // Fallback: wait for connection manager to be initialized
            console.warn('Connection manager not available, retrying...');
            setTimeout(() => {
                this.setupSocketConnection();
            }, 1000);
        }
    }
    
    setupSocketEventHandlers() {
        /**
         * Set up SocketIO event handlers for global selector
         */
        if (!this.socket) return;
        
        // Global session events
        this.socket.on('global_session_joined', (data) => {
            this.handleGlobalSessionJoined(data);
        });
        
        this.socket.on('global_song_selected', (data) => {
            this.handleGlobalSongSelected(data);
        });
        
        this.socket.on('song_changed', (data) => {
            this.handleSongChanged(data);
        });
        
        this.socket.on('session_count_updated', (data) => {
            this.handleSessionCountUpdated(data);
        });
        
        this.socket.on('current_song_state', (data) => {
            this.handleCurrentSongState(data);
        });
        
        // Error handling
        this.socket.on('error', (error) => {
            this.handleSocketError(error);
        });
    }
    
    setupEventListeners() {
        /**
         * Set up DOM event listeners
         */
        // Song selection
        if (this.songSelect) {
            this.songSelect.addEventListener('change', (e) => {
                this.handleSongSelection(e.target.value);
            });
        }
        
        // Refresh button
        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.altKey && e.key === 'r') {
                e.preventDefault();
                this.refreshData();
            }
        });
    }
    
    async loadSongs() {
        /**
         * Load songs for selection dropdown
         */
        try {
            this.showLoading();
            
            const response = await fetch('/api/songs');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data.songs && Array.isArray(data.songs)) {
                this.populateSongDropdown(data.songs);
                this.songsCache.clear();
                data.songs.forEach(song => {
                    this.songsCache.set(song.song_id, song);
                });
            } else {
                throw new Error(this.getTranslation('invalid_data_format', 'Formato de datos inválido'));
            }
            
            this.hideLoading();
            
        } catch (error) {
            console.error('Error loading songs:', error);
            this.hideLoading();
            this.showError(error.message || this.getTranslation('failed_to_load_songs', 'Error al cargar las canciones'));
        }
    }
    
    populateSongDropdown(songs) {
        /**
         * Populate song selection dropdown with order information
         */
        if (!this.songSelect) return;
        
        // Create document fragment for performance
        const fragment = document.createDocumentFragment();
        
        // Default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = this.getTranslation('select_song', 'Seleccionar una canción...');
        fragment.appendChild(defaultOption);
        
        // Song options (already sorted by order from server)
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
        
        // Update dropdown
        this.songSelect.innerHTML = '';
        this.songSelect.appendChild(fragment);
        this.songSelect.disabled = false;
        
        if (this.refreshBtn) {
            this.refreshBtn.disabled = false;
        }
    }
    
    async handleSongSelection(songId) {
        /**
         * Handle song selection from dropdown
         */
        if (!songId) {
            return;
        }
        
        try {
            this.showLoading();
            
            // Get detailed song information
            const songDetails = await this.getSongDetails(songId);
            
            // Send selection to server via SocketIO
            if (this.socket && this.isConnected) {
                this.socket.emit('select_global_song', {
                    song_id: songId,
                    song_data: songDetails
                });
            } else {
                // Fallback to REST API
                const response = await fetch('/api/global/set-song', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        song_id: songId,
                        session_id: this.socket?.id || 'web_client'
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                if (result.error) {
                    throw new Error(result.error);
                }
                
                // Update display with result
                this.updateCurrentSongDisplay(result.song_details);
            }
            
            this.hideLoading();
            
        } catch (error) {
            console.error('Error selecting song:', error);
            this.hideLoading();
            this.showError(error.message || this.getTranslation('update_failed', 'Error al actualizar'));
            
            // Reset dropdown selection
            this.songSelect.value = '';
        }
    }
    
    async getSongDetails(songId) {
        /**
         * Get detailed song information with caching
         */
        // Check cache first
        if (this.songDetailsCache.has(songId)) {
            return this.songDetailsCache.get(songId);
        }
        
        // Fetch from server
        const response = await fetch(`/api/song/${encodeURIComponent(songId)}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Cache the result
        this.songDetailsCache.set(songId, data);
        
        return data;
    }
    
    updateCurrentSongDisplay(songData) {
        /**
         * Update the current song display with detailed information including order and next song
         */
        if (!this.currentSongDisplay || !songData) {
            return;
        }
        
        // Update header elements
        const globalSongTitle = document.getElementById('globalSongTitle');
        const globalSongArtist = document.getElementById('globalSongArtist');
        const globalSongOrder = document.getElementById('globalSongOrder');
        const globalSongDuration = document.getElementById('globalSongDuration');
        
        if (globalSongTitle) {
            globalSongTitle.innerHTML = `
                <i class="bi bi-broadcast me-2" aria-hidden="true"></i>
                ${songData.song}
            `;
        }
        
        if (globalSongArtist) {
            globalSongArtist.textContent = `por ${songData.artist}`;
        }
        
        if (globalSongOrder && songData.order) {
            globalSongOrder.textContent = `${this.getTranslation('order_label', 'Orden')}: ${songData.order}`;
            globalSongOrder.classList.remove('d-none');
        } else if (globalSongOrder) {
            globalSongOrder.classList.add('d-none');
        }
        
        if (globalSongDuration) {
            globalSongDuration.textContent = songData.time;
        }
        
        // Create detailed song display
        const html = `
            <!-- Musician Assignments -->
            <h4 class="mb-3">
                <i class="bi bi-people me-2" aria-hidden="true"></i>
                ${this.getTranslation('musician_assignments', 'Asignaciones de Músicos')}
            </h4>
            <div id="globalMusicianAssignments" class="row g-3 mb-4">
                ${songData.assignments ? Object.entries(songData.assignments).map(([instrument, musician]) => `
                    <div class="col-12 col-sm-6 col-lg-4">
                        <div class="card h-100 ${musician ? 'border-success' : 'border-secondary'}">
                            <div class="card-body text-center">
                                <i class="bi bi-music-note-beamed display-6 ${musician ? 'text-success' : 'text-muted'}" aria-hidden="true"></i>
                                <h6 class="card-title mt-2">${instrument}</h6>
                                <p class="card-text ${musician ? 'text-success fw-bold' : 'text-muted'}">
                                    ${musician || this.getTranslation('unassigned', 'Sin asignar')}
                                </p>
                            </div>
                        </div>
                    </div>
                `).join('') : ''}
            </div>
        `;
        
        this.currentSongDisplay.innerHTML = html;
        
        // Update next song section
        this.updateNextSongSection(songData);
        
        this.currentGlobalSong = songData;
        
        // Update last update time
        this.updateLastUpdateTime();
        
        // Announce to screen readers
        this.announceToScreenReader(`${this.getTranslation('song_selected', 'Canción seleccionada')}: ${songData.artist} - ${songData.song}`);
    }
    
    updateNextSongSection(songData) {
        /**
         * Update next song section with detailed information
         */
        const nextSongSection = document.getElementById('nextSongSection');
        const noNextSongSection = document.getElementById('noNextSongSection');
        
        if (songData.next_song) {
            // Update next song information
            const nextSongTitle = document.getElementById('nextSongTitle');
            const nextSongArtist = document.getElementById('nextSongArtist');
            const nextSongOrder = document.getElementById('nextSongOrder');
            const nextSongDuration = document.getElementById('nextSongDuration');
            const selectNextSongBtn = document.getElementById('selectNextSongBtn');
            const nextSongMusiciansList = document.getElementById('nextSongMusiciansList');
            
            if (nextSongTitle) {
                nextSongTitle.textContent = songData.next_song.title || songData.next_song.song;
            }
            
            if (nextSongArtist) {
                nextSongArtist.textContent = `por ${songData.next_song.artist || 'Artista desconocido'}`;
            }
            
            if (nextSongOrder) {
                nextSongOrder.textContent = `${this.getTranslation('order_label', 'Orden')}: ${songData.next_song.order}`;
            }
            
            if (nextSongDuration && songData.next_song.time) {
                nextSongDuration.textContent = songData.next_song.time;
            }
            
            // Set up next song selection button
            if (selectNextSongBtn) {
                selectNextSongBtn.onclick = () => {
                    if (this.songSelect) {
                        this.songSelect.value = songData.next_song.song_id;
                        this.handleSongSelection(songData.next_song.song_id);
                    }
                };
            }
            
            // Update next song musicians if available
            if (nextSongMusiciansList && songData.next_song.assignments) {
                const musiciansHtml = Object.entries(songData.next_song.assignments)
                    .filter(([instrument, musician]) => musician && musician.trim() !== '')
                    .map(([instrument, musician]) => `
                        <span class="badge bg-light text-dark me-1 mb-1">
                            <i class="bi bi-person-fill me-1" aria-hidden="true"></i>
                            ${musician}
                        </span>
                    `).join('');
                
                nextSongMusiciansList.innerHTML = musiciansHtml || `
                    <small class="text-muted">${this.getTranslation('no_musicians_assigned', 'No hay músicos asignados')}</small>
                `;
            }
            
            // Show next song section
            if (nextSongSection) {
                nextSongSection.classList.remove('d-none');
            }
            if (noNextSongSection) {
                noNextSongSection.classList.add('d-none');
            }
        } else {
            // Show no next song section
            if (nextSongSection) {
                nextSongSection.classList.add('d-none');
            }
            if (noNextSongSection) {
                noNextSongSection.classList.remove('d-none');
            }
        }
    }
    
    updateLastUpdateTime() {
        /**
         * Update last update time display
         */
        if (!this.lastUpdateDisplay) return;
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('es-ES');
        
        this.lastUpdateDisplay.textContent = `${this.getTranslation('last_updated', 'Última actualización')}: ${timeString}`;
        this.lastUpdateTime = now;
    }
    
    updateSessionCount(count) {
        /**
         * Update connected sessions count
         */
        if (this.sessionCountDisplay) {
            this.sessionCountDisplay.textContent = count || 0;
        }
        this.connectedSessions = count || 0;
    }
    
    updateConnectionStatus(status, message = '') {
        /**
         * Update connection status display
         */
        if (!this.connectionStatusText || !this.connectionStatusAlert) return;
        
        this.connectionStatusText.textContent = message || this.getConnectionStatusText(status);
        
        // Update alert class
        this.connectionStatusAlert.className = 'alert d-flex align-items-center';
        switch (status) {
            case 'connected':
                this.connectionStatusAlert.classList.add('alert-success');
                break;
            case 'connecting':
            case 'reconnecting':
                this.connectionStatusAlert.classList.add('alert-warning');
                break;
            case 'disconnected':
                this.connectionStatusAlert.classList.add('alert-danger');
                break;
            default:
                this.connectionStatusAlert.classList.add('alert-info');
        }
    }
    
    getConnectionStatusText(status) {
        /**
         * Get localized connection status text
         */
        const statusTexts = {
            connected: this.getTranslation('connected', 'Conectado'),
            connecting: this.getTranslation('reconnecting', 'Conectando'),
            reconnecting: this.getTranslation('reconnecting', 'Reconectando'),
            disconnected: this.getTranslation('disconnected', 'Desconectado')
        };
        
        return statusTexts[status] || status;
    }
    
    // Socket event handlers
    handleSocketConnect(data) {
        /**
         * Handle socket connection
         */
        console.info('Global selector connected:', data);
        
        this.isConnected = true;
        this.updateConnectionStatus('connected');
        
        // Join global session
        if (this.socket) {
            this.socket.emit('join_global_session', {
                client_info: {
                    page: 'global-selector',
                    userAgent: navigator.userAgent.substring(0, 100)
                }
            });
        }
        
        // Request current state
        this.requestCurrentState();
    }
    
    handleSocketDisconnect(data) {
        /**
         * Handle socket disconnection
         */
        console.warn('Global selector disconnected:', data);
        
        this.isConnected = false;
        this.updateConnectionStatus('disconnected', data.reason);
    }
    
    handleSocketReconnect(data) {
        /**
         * Handle socket reconnection
         */
        console.info('Global selector reconnected:', data);
        
        this.isConnected = true;
        this.updateConnectionStatus('connected');
        
        // Rejoin global session and refresh state
        if (this.socket) {
            this.socket.emit('join_global_session');
        }
        this.requestCurrentState();
    }
    
    handleGlobalSessionJoined(data) {
        /**
         * Handle successful global session join
         */
        console.info('Joined global session:', data);
        
        if (data.current_state) {
            this.updateSessionCount(data.current_state.connected_sessions);
            
            // Update current song if available
            if (data.current_song_details) {
                this.updateCurrentSongDisplay(data.current_song_details);
                
                // Update dropdown selection
                if (this.songSelect && data.current_song_details.song_id) {
                    this.songSelect.value = data.current_song_details.song_id;
                }
            }
        }
    }
    
    handleGlobalSongSelected(data) {
        /**
         * Handle confirmation of song selection
         */
        console.info('Global song selected:', data);
        
        if (data.status === 'success' && data.song_data) {
            this.updateCurrentSongDisplay(data.song_data);
            
            // Show success message briefly
            this.showSuccessMessage(data.message || this.getTranslation('song_selected', 'Canción seleccionada'));
        }
    }
    
    handleSongChanged(data) {
        /**
         * Handle song change from other sessions
         */
        console.info('Song changed by another session:', data);
        
        if (data.song_data) {
            this.updateCurrentSongDisplay(data.song_data);
            
            // Update dropdown selection
            if (this.songSelect && data.song_id) {
                this.songSelect.value = data.song_id;
            }
            
            // Show notification
            this.showInfoMessage(data.message || this.getTranslation('song_changed', 'Canción cambiada'));
        }
    }
    
    handleSessionCountUpdated(data) {
        /**
         * Handle session count updates
         */
        if (typeof data.connected_sessions === 'number') {
            this.updateSessionCount(data.connected_sessions);
        }
    }
    
    handleCurrentSongState(data) {
        /**
         * Handle current song state response
         */
        console.info('Current song state:', data);
        
        if (data.current_song_data) {
            this.updateCurrentSongDisplay(data.current_song_data);
            
            // Update dropdown selection
            if (this.songSelect && data.current_song_id) {
                this.songSelect.value = data.current_song_id;
            }
        }
        
        if (typeof data.connected_sessions === 'number') {
            this.updateSessionCount(data.connected_sessions);
        }
    }
    
    handleSocketError(error) {
        /**
         * Handle socket errors
         */
        console.error('Global selector socket error:', error);
        
        let errorMessage = error.message || this.getTranslation('connection_error', 'Error de conexión');
        if (error.code) {
            errorMessage += ` (${error.code})`;
        }
        
        this.showError(errorMessage);
    }
    
    /**
     * Handle connection errors
     * Requirements: 6.3
     */
    handleConnectionError(data) {
        console.warn('Connection error:', data);
        
        let message = this.getTranslation('connection_error', 'Error de conexión');
        if (data.attempts) {
            message += ` (Intento ${data.attempts})`;
        }
        
        this.updateConnectionStatus('disconnected', message);
    }
    
    /**
     * Handle reconnection attempts
     * Requirements: 6.3
     */
    handleReconnectAttempt(data) {
        console.info('Reconnection attempt:', data.attempt);
        
        const message = `${this.getTranslation('reconnect_attempt', 'Intento de reconexión')} ${data.attempt}`;
        this.updateConnectionStatus('reconnecting', message);
    }
    
    /**
     * Handle failed reconnection
     * Requirements: 6.3
     */
    handleReconnectFailed(data) {
        console.error('Reconnection failed after maximum attempts');
        
        const message = this.getTranslation('max_reconnect_attempts', 'Máximo de intentos de reconexión alcanzado');
        this.updateConnectionStatus('disconnected', message);
        
        // Show manual reconnect option
        this.showManualReconnectOption();
    }
    
    /**
     * Show manual reconnect option
     * Requirements: 6.3
     */
    showManualReconnectOption() {
        if (!this.connectionStatusAlert) return;
        
        // Check if manual reconnect button already exists
        if (this.connectionStatusAlert.querySelector('.manual-reconnect-btn')) {
            return;
        }
        
        const reconnectBtn = document.createElement('button');
        reconnectBtn.className = 'btn btn-sm btn-outline-primary ms-2 manual-reconnect-btn';
        reconnectBtn.innerHTML = `<i class="bi bi-arrow-clockwise me-1"></i>${this.getTranslation('manual_reconnect', 'Reconectar')}`;
        reconnectBtn.onclick = () => {
            if (window.connectionManager) {
                window.connectionManager.reconnect();
                reconnectBtn.remove();
            }
        };
        
        this.connectionStatusAlert.appendChild(reconnectBtn);
    }
    
    // Utility methods
    requestCurrentState() {
        /**
         * Request current global state from server
         */
        if (this.socket && this.isConnected) {
            this.socket.emit('request_current_song');
        }
    }
    
    async refreshData() {
        /**
         * Refresh all data
         */
        try {
            this.showLoading();
            
            // Reload songs
            await this.loadSongs();
            
            // Request current state
            this.requestCurrentState();
            
            this.hideLoading();
            this.showSuccessMessage(this.getTranslation('refresh_complete', 'Actualización completa'));
            
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.hideLoading();
            this.showError(error.message || this.getTranslation('refresh_failed', 'Error al actualizar'));
        }
    }
    
    // UI state methods
    showLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.remove('d-none');
        }
        this.hideError();
    }
    
    hideLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.add('d-none');
        }
    }
    
    showError(message) {
        if (this.errorDisplay) {
            const errorMessage = this.errorDisplay.querySelector('#error-message');
            if (errorMessage) {
                errorMessage.textContent = message;
            }
            this.errorDisplay.classList.remove('d-none');
        }
        
        this.hideLoading();
        
        // Announce to screen readers
        this.announceToScreenReader(`${this.getTranslation('error', 'Error')}: ${message}`);
    }
    
    hideError() {
        if (this.errorDisplay) {
            this.errorDisplay.classList.add('d-none');
        }
    }
    
    showSuccessMessage(message) {
        /**
         * Show temporary success message
         */
        this.showTemporaryMessage(message, 'success');
    }
    
    showInfoMessage(message) {
        /**
         * Show temporary info message
         */
        this.showTemporaryMessage(message, 'info');
    }
    
    showTemporaryMessage(message, type = 'info') {
        /**
         * Show temporary message that auto-dismisses
         */
        const alertClass = type === 'success' ? 'alert-success' : 'alert-info';
        const iconClass = type === 'success' ? 'bi-check-circle' : 'bi-info-circle';
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        messageDiv.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        messageDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${iconClass} me-2" aria-hidden="true"></i>
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()" aria-label="Cerrar"></button>
            </div>
        `;
        
        document.body.appendChild(messageDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (messageDiv && messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
        
        // Announce to screen readers
        this.announceToScreenReader(message);
    }
    
    announceToScreenReader(message) {
        /**
         * Announce message to screen readers
         */
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
}

// Initialize global selector when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're on the global selector page
    if (window.location.pathname.includes('global-selector') || 
        document.getElementById('global-selector-container')) {
        window.globalSongSelector = new GlobalSongSelector();
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GlobalSongSelector;
}