/**
 * Admin Control Panel JavaScript
 * Handles live performance state management for administrators
 */

class AdminControlPanel {
    constructor() {
        // DOM elements
        this.currentSongSelect = document.getElementById('currentSongSelect');
        this.nextSongSelect = document.getElementById('nextSongSelect');
        this.currentSongStatus = document.getElementById('currentSongStatus');
        this.nextSongStatus = document.getElementById('nextSongStatus');
        this.statusMessages = document.getElementById('statusMessages');
        
        // Buttons
        this.setCurrentSongBtn = document.getElementById('setCurrentSongBtn');
        this.clearCurrentSongBtn = document.getElementById('clearCurrentSongBtn');
        this.setNextSongBtn = document.getElementById('setNextSongBtn');
        this.clearNextSongBtn = document.getElementById('clearNextSongBtn');
        this.refreshStateBtn = document.getElementById('refreshStateBtn');
        this.clearAllBtn = document.getElementById('clearAllBtn');
        
        // Spanish translations from server
        this.translations = window.translations || {};
        
        // Data storage
        this.songs = [];
        this.currentState = null;
        
        this.init();
    }
    
    getTranslation(key, defaultValue = key) {
        return this.translations[key] || defaultValue;
    }
    
    init() {
        // Load initial data
        this.loadSongs();
        this.loadCurrentState();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Set up auto-refresh every 30 seconds
        setInterval(() => {
            this.loadCurrentState();
        }, 30000);
        
        console.log('Admin Control Panel initialized');
    }
    
    setupEventListeners() {
        // Set current song
        this.setCurrentSongBtn.addEventListener('click', () => {
            this.setCurrentSong();
        });
        
        // Clear current song
        this.clearCurrentSongBtn.addEventListener('click', () => {
            this.clearCurrentSong();
        });
        
        // Set next song
        this.setNextSongBtn.addEventListener('click', () => {
            this.setNextSong();
        });
        
        // Clear next song
        this.clearNextSongBtn.addEventListener('click', () => {
            this.clearNextSong();
        });
        
        // Refresh state
        this.refreshStateBtn.addEventListener('click', () => {
            this.refreshState();
        });
        
        // Clear all
        this.clearAllBtn.addEventListener('click', () => {
            this.clearAll();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'r':
                        e.preventDefault();
                        this.refreshState();
                        break;
                    case 'Enter':
                        if (e.target === this.currentSongSelect) {
                            e.preventDefault();
                            this.setCurrentSong();
                        } else if (e.target === this.nextSongSelect) {
                            e.preventDefault();
                            this.setNextSong();
                        }
                        break;
                }
            }
        });
    }
    
    async loadSongs() {
        try {
            const response = await fetch('/api/songs');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data.songs && Array.isArray(data.songs)) {
                this.songs = data.songs;
                this.populateDropdowns(data.songs);
            } else {
                throw new Error('Invalid songs data format');
            }
        } catch (error) {
            console.error('Error loading songs:', error);
            this.showError('Error al cargar las canciones: ' + error.message);
        }
    }
    
    populateDropdowns(songs) {
        // Clear existing options
        this.currentSongSelect.innerHTML = '';
        this.nextSongSelect.innerHTML = '';
        
        // Add default options
        const defaultOption1 = document.createElement('option');
        defaultOption1.value = '';
        defaultOption1.textContent = 'Seleccionar una canción...';
        this.currentSongSelect.appendChild(defaultOption1);
        
        const defaultOption2 = document.createElement('option');
        defaultOption2.value = '';
        defaultOption2.textContent = 'Seleccionar una canción...';
        this.nextSongSelect.appendChild(defaultOption2);
        
        // Add clear option
        const clearOption1 = document.createElement('option');
        clearOption1.value = 'null';
        clearOption1.textContent = '--- Limpiar selección ---';
        this.currentSongSelect.appendChild(clearOption1);
        
        const clearOption2 = document.createElement('option');
        clearOption2.value = 'null';
        clearOption2.textContent = '--- Limpiar selección ---';
        this.nextSongSelect.appendChild(clearOption2);
        
        // Add songs
        songs.forEach(song => {
            const option1 = document.createElement('option');
            option1.value = song.song_id;
            option1.textContent = song.display_name;
            this.currentSongSelect.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = song.song_id;
            option2.textContent = song.display_name;
            this.nextSongSelect.appendChild(option2);
        });
        
        // Enable dropdowns
        this.currentSongSelect.disabled = false;
        this.nextSongSelect.disabled = false;
    }
    
    async loadCurrentState() {
        try {
            const response = await fetch('/api/live-performance');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.currentState = data;
            this.updateStateDisplay(data);
            
        } catch (error) {
            console.error('Error loading current state:', error);
            this.showError('Error al cargar el estado actual: ' + error.message);
        }
    }
    
    updateStateDisplay(state) {
        // Update current song status
        if (state.current_song) {
            this.currentSongStatus.innerHTML = `
                <strong>${state.current_song.full_title}</strong><br>
                <small class="text-muted">Duración: ${state.current_song.duration}</small>
            `;
        } else {
            this.currentSongStatus.textContent = 'No hay canción actual seleccionada';
        }
        
        // Update next song status
        if (state.next_song) {
            this.nextSongStatus.innerHTML = `
                <strong>${state.next_song.full_title}</strong><br>
                <small class="text-muted">Duración: ${state.next_song.duration}</small>
            `;
        } else {
            this.nextSongStatus.textContent = 'No hay próxima canción seleccionada';
        }
        
        // Update dropdown selections to match current state
        if (state.current_song) {
            this.currentSongSelect.value = state.current_song.id;
        } else {
            this.currentSongSelect.value = '';
        }
        
        if (state.next_song) {
            this.nextSongSelect.value = state.next_song.id;
        } else {
            this.nextSongSelect.value = '';
        }
    }
    
    async setCurrentSong() {
        const songId = this.currentSongSelect.value;
        
        if (!songId || songId === '') {
            this.showWarning('Por favor selecciona una canción');
            return;
        }
        
        const finalSongId = songId === 'null' ? null : songId;
        
        try {
            this.setButtonLoading(this.setCurrentSongBtn, true);
            
            const response = await fetch('/api/admin/set-current-song', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ song_id: finalSongId })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            if (data.success) {
                this.showSuccess('Canción actual actualizada correctamente');
                await this.loadCurrentState(); // Refresh state
            } else {
                throw new Error(data.error || 'Unknown error');
            }
            
        } catch (error) {
            console.error('Error setting current song:', error);
            this.showError('Error al establecer la canción actual: ' + error.message);
        } finally {
            this.setButtonLoading(this.setCurrentSongBtn, false);
        }
    }
    
    async clearCurrentSong() {
        try {
            this.setButtonLoading(this.clearCurrentSongBtn, true);
            
            const response = await fetch('/api/admin/set-current-song', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ song_id: null })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            if (data.success) {
                this.showSuccess('Canción actual limpiada correctamente');
                await this.loadCurrentState(); // Refresh state
            } else {
                throw new Error(data.error || 'Unknown error');
            }
            
        } catch (error) {
            console.error('Error clearing current song:', error);
            this.showError('Error al limpiar la canción actual: ' + error.message);
        } finally {
            this.setButtonLoading(this.clearCurrentSongBtn, false);
        }
    }
    
    async setNextSong() {
        const songId = this.nextSongSelect.value;
        
        if (!songId || songId === '') {
            this.showWarning('Por favor selecciona una canción');
            return;
        }
        
        const finalSongId = songId === 'null' ? null : songId;
        
        try {
            this.setButtonLoading(this.setNextSongBtn, true);
            
            const response = await fetch('/api/admin/set-next-song', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ song_id: finalSongId })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            if (data.success) {
                this.showSuccess('Próxima canción actualizada correctamente');
                await this.loadCurrentState(); // Refresh state
            } else {
                throw new Error(data.error || 'Unknown error');
            }
            
        } catch (error) {
            console.error('Error setting next song:', error);
            this.showError('Error al establecer la próxima canción: ' + error.message);
        } finally {
            this.setButtonLoading(this.setNextSongBtn, false);
        }
    }
    
    async clearNextSong() {
        try {
            this.setButtonLoading(this.clearNextSongBtn, true);
            
            const response = await fetch('/api/admin/set-next-song', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ song_id: null })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            if (data.success) {
                this.showSuccess('Próxima canción limpiada correctamente');
                await this.loadCurrentState(); // Refresh state
            } else {
                throw new Error(data.error || 'Unknown error');
            }
            
        } catch (error) {
            console.error('Error clearing next song:', error);
            this.showError('Error al limpiar la próxima canción: ' + error.message);
        } finally {
            this.setButtonLoading(this.clearNextSongBtn, false);
        }
    }
    
    async refreshState() {
        try {
            this.setButtonLoading(this.refreshStateBtn, true);
            await this.loadCurrentState();
            this.showInfo('Estado actualizado correctamente');
        } catch (error) {
            console.error('Error refreshing state:', error);
            this.showError('Error al actualizar el estado: ' + error.message);
        } finally {
            this.setButtonLoading(this.refreshStateBtn, false);
        }
    }
    
    async clearAll() {
        if (!confirm('¿Estás seguro de que quieres limpiar todas las selecciones?')) {
            return;
        }
        
        try {
            this.setButtonLoading(this.clearAllBtn, true);
            
            // Clear both current and next songs
            await Promise.all([
                fetch('/api/admin/set-current-song', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ song_id: null })
                }),
                fetch('/api/admin/set-next-song', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ song_id: null })
                })
            ]);
            
            this.showSuccess('Todas las selecciones han sido limpiadas');
            await this.loadCurrentState(); // Refresh state
            
        } catch (error) {
            console.error('Error clearing all:', error);
            this.showError('Error al limpiar todas las selecciones: ' + error.message);
        } finally {
            this.setButtonLoading(this.clearAllBtn, false);
        }
    }
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.setAttribute('data-original-text', originalText);
            button.innerHTML = '<i class="bi bi-hourglass-split me-2" aria-hidden="true"></i>Procesando...';
        } else {
            button.disabled = false;
            const originalText = button.getAttribute('data-original-text');
            if (originalText) {
                button.innerHTML = originalText;
                button.removeAttribute('data-original-text');
            }
        }
    }
    
    showMessage(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const icon = {
            'success': 'bi-check-circle-fill',
            'error': 'bi-exclamation-triangle-fill',
            'warning': 'bi-exclamation-triangle-fill',
            'info': 'bi-info-circle-fill'
        }[type] || 'bi-info-circle-fill';
        
        const alert = document.createElement('div');
        alert.className = `alert ${alertClass} alert-dismissible fade show`;
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${icon} me-2" aria-hidden="true"></i>
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
            </div>
        `;
        
        // Clear existing messages
        this.statusMessages.innerHTML = '';
        this.statusMessages.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
        
        // Announce to screen readers
        this.announceToScreenReader(message);
    }
    
    showSuccess(message) {
        this.showMessage(message, 'success');
    }
    
    showError(message) {
        this.showMessage(message, 'error');
    }
    
    showWarning(message) {
        this.showMessage(message, 'warning');
    }
    
    showInfo(message) {
        this.showMessage(message, 'info');
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
}

// Initialize the admin control panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminControlPanel = new AdminControlPanel();
    
    // Add error handling for unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
        if (window.adminControlPanel) {
            window.adminControlPanel.showError('Ha ocurrido un error inesperado. Por favor, actualiza la página.');
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