/**
 * Connection Manager for Real-time SocketIO Features
 * Handles connection status, reconnection logic, and visual feedback
 * Requirements: 6.3, 6.5
 */

class ConnectionManager {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.connectionAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000; // Start with 1 second
        this.maxReconnectDelay = 30000; // Max 30 seconds
        this.backoffFactor = 1.5;
        this.reconnectTimer = null;
        this.pingInterval = null;
        this.lastPingTime = null;
        this.connectionQuality = 'unknown';
        
        // Connection status elements
        this.statusIndicator = null;
        this.statusText = null;
        this.connectionDetails = null;
        
        // Spanish translations
        this.translations = window.translations || {};
        
        // Event listeners
        this.eventListeners = new Map();
        
        this.init();
    }
    
    getTranslation(key, defaultValue = key) {
        return this.translations[key] || defaultValue;
    }
    
    init() {
        this.createStatusIndicator();
        this.initializeSocketIO();
        this.setupEventListeners();
        this.startConnectionMonitoring();
    }
    
    createStatusIndicator() {
        /**
         * Create visual connection status indicator
         */
        // Create status indicator container
        const statusContainer = document.createElement('div');
        statusContainer.id = 'connection-status-container';
        statusContainer.className = 'connection-status-container';
        statusContainer.innerHTML = `
            <div class="connection-status-indicator" id="connection-status-indicator">
                <div class="status-icon" id="status-icon">
                    <i class="bi bi-wifi" aria-hidden="true"></i>
                </div>
                <div class="status-text" id="status-text">
                    ${this.getTranslation('connection_status', 'Estado de conexión')}
                </div>
                <div class="connection-details" id="connection-details">
                    <small class="text-muted">${this.getTranslation('disconnected', 'Desconectado')}</small>
                </div>
            </div>
        `;
        
        // Add CSS styles
        const style = document.createElement('style');
        style.textContent = `
            .connection-status-container {
                position: fixed;
                top: 10px;
                left: 10px;
                z-index: 1000;
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 8px 12px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(5px);
                transition: all 0.3s ease;
                max-width: 200px;
            }
            
            .connection-status-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 0.875rem;
            }
            
            .status-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                transition: all 0.3s ease;
            }
            
            .status-icon.connected {
                background-color: #28a745;
                color: white;
            }
            
            .status-icon.connecting {
                background-color: #ffc107;
                color: white;
                animation: pulse 1.5s infinite;
            }
            
            .status-icon.disconnected {
                background-color: #dc3545;
                color: white;
            }
            
            .status-icon.reconnecting {
                background-color: #fd7e14;
                color: white;
                animation: spin 2s linear infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
            .status-text {
                font-weight: 500;
                color: #495057;
            }
            
            .connection-details {
                margin-top: 2px;
            }
            
            .connection-status-container.hidden {
                opacity: 0;
                transform: translateY(-10px);
                pointer-events: none;
            }
            
            @media (max-width: 576px) {
                .connection-status-container {
                    top: 5px;
                    left: 5px;
                    right: 5px;
                    max-width: none;
                    padding: 6px 10px;
                }
                
                .connection-status-indicator {
                    font-size: 0.8rem;
                }
            }
        `;
        document.head.appendChild(style);
        
        // Add to page
        document.body.appendChild(statusContainer);
        
        // Store references
        this.statusIndicator = document.getElementById('connection-status-indicator');
        this.statusIcon = document.getElementById('status-icon');
        this.statusText = document.getElementById('status-text');
        this.connectionDetails = document.getElementById('connection-details');
        
        // Add click handler for details
        statusContainer.addEventListener('click', () => {
            this.showConnectionDetails();
        });
        
        // Hide initially
        this.updateConnectionStatus('disconnected', this.getTranslation('disconnected', 'Desconectado'));
    }
    
    initializeSocketIO() {
        /**
         * Initialize SocketIO connection with proper configuration
         */
        try {
            // Initialize Socket.IO with configuration for Azure App Service
            this.socket = io({
                transports: ['websocket', 'polling'], // WebSocket with polling fallback
                upgrade: true,
                rememberUpgrade: true,
                timeout: 20000,
                forceNew: false,
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: this.reconnectDelay,
                reconnectionDelayMax: this.maxReconnectDelay,
                maxReconnectionAttempts: this.maxReconnectAttempts,
                randomizationFactor: 0.5
            });
            
            this.setupSocketEventHandlers();
            
        } catch (error) {
            console.error('Failed to initialize SocketIO:', error);
            this.updateConnectionStatus('disconnected', this.getTranslation('connection_error', 'Error de conexión'));
        }
    }
    
    setupSocketEventHandlers() {
        /**
         * Set up SocketIO event handlers
         */
        // Connection events
        this.socket.on('connect', () => {
            this.handleConnect();
        });
        
        this.socket.on('disconnect', (reason) => {
            this.handleDisconnect(reason);
        });
        
        this.socket.on('connect_error', (error) => {
            this.handleConnectionError(error);
        });
        
        this.socket.on('reconnect', (attemptNumber) => {
            this.handleReconnect(attemptNumber);
        });
        
        this.socket.on('reconnect_attempt', (attemptNumber) => {
            this.handleReconnectAttempt(attemptNumber);
        });
        
        this.socket.on('reconnect_error', (error) => {
            this.handleReconnectError(error);
        });
        
        this.socket.on('reconnect_failed', () => {
            this.handleReconnectFailed();
        });
        
        // Application-specific events
        this.socket.on('connection_status', (data) => {
            this.handleConnectionStatusUpdate(data);
        });
        
        this.socket.on('error', (error) => {
            this.handleSocketError(error);
        });
        
        // Ping/pong for connection quality monitoring
        this.socket.on('pong', (data) => {
            this.handlePong(data);
        });
        
        // Enhanced real-time error handling events
        this.socket.on('session_sync_conflict', (data) => {
            this.handleSessionSyncConflict(data);
        });
        
        this.socket.on('network_quality_update', (data) => {
            this.handleNetworkQualityChange(data.quality);
        });
        
        this.socket.on('service_degraded', (data) => {
            this.handleServiceDegradation(data);
        });
        
        this.socket.on('service_restored', (data) => {
            this.handleServiceRestoration(data);
        });
        
        this.socket.on('conflict_resolved', (data) => {
            this.handleConflictResolution(data);
        });
        
        this.socket.on('session_cleanup', (data) => {
            this.handleSessionCleanup(data);
        });
        
        this.socket.on('broadcast_failed', (data) => {
            this.handleBroadcastFailure(data);
        });
    }
    
    setupEventListeners() {
        /**
         * Set up browser event listeners
         */
        // Network status monitoring
        window.addEventListener('online', () => {
            this.handleNetworkOnline();
        });
        
        window.addEventListener('offline', () => {
            this.handleNetworkOffline();
        });
        
        // Page visibility for connection management
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });
        
        // Beforeunload for cleanup
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }
    
    startConnectionMonitoring(intervalMs = 30000) {
        /**
         * Start periodic connection quality monitoring with configurable interval
         */
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
        }
        
        this.pingInterval = setInterval(() => {
            if (this.isConnected && this.socket) {
                this.lastPingTime = Date.now();
                this.socket.emit('ping');
            }
        }, intervalMs);
    }
    
    handleConnect() {
        /**
         * Handle successful connection
         */
        console.info('SocketIO connected:', this.socket.id);
        
        this.isConnected = true;
        this.connectionAttempts = 0;
        this.reconnectDelay = 1000; // Reset delay
        
        // Clear reconnection timer
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        // Update UI
        this.updateConnectionStatus('connected', this.getTranslation('connected', 'Conectado'));
        
        // Emit custom event for application
        this.emitEvent('connected', {
            sessionId: this.socket.id,
            transport: this.socket.io.engine.transport.name
        });
        
        // Join global session if needed
        this.joinGlobalSession();
        
        // Announce to screen readers
        this.announceToScreenReader(this.getTranslation('connection_established', 'Conexión establecida'));
    }
    
    handleDisconnect(reason) {
        /**
         * Handle disconnection
         */
        console.warn('SocketIO disconnected:', reason);
        
        this.isConnected = false;
        
        // Update UI based on reason
        let statusMessage;
        let shouldReconnect = true;
        
        switch (reason) {
            case 'io server disconnect':
                statusMessage = this.getTranslation('server_maintenance', 'Servidor en mantenimiento');
                shouldReconnect = false; // Server initiated disconnect
                break;
            case 'io client disconnect':
                statusMessage = this.getTranslation('disconnected', 'Desconectado');
                shouldReconnect = false; // Client initiated disconnect
                break;
            case 'ping timeout':
                statusMessage = this.getTranslation('connection_timeout', 'Tiempo de conexión agotado');
                break;
            case 'transport close':
                statusMessage = this.getTranslation('connection_lost', 'Conexión perdida');
                break;
            case 'transport error':
                statusMessage = this.getTranslation('connection_error', 'Error de conexión');
                break;
            default:
                statusMessage = this.getTranslation('disconnected', 'Desconectado');
        }
        
        this.updateConnectionStatus('disconnected', statusMessage);
        
        // Emit custom event for application
        this.emitEvent('disconnected', { reason, shouldReconnect });
        
        // Start manual reconnection if needed
        if (shouldReconnect && navigator.onLine) {
            this.startReconnection();
        }
        
        // Announce to screen readers
        this.announceToScreenReader(this.getTranslation('connection_lost', 'Conexión perdida'));
    }
    
    handleConnectionError(error) {
        /**
         * Handle connection errors with enhanced error classification and recovery
         */
        console.error('SocketIO connection error:', error);
        
        this.connectionAttempts++;
        
        let errorMessage;
        let errorType = 'connection_error';
        let shouldRetry = true;
        let retryDelay = this.reconnectDelay;
        
        // Enhanced error classification
        if (!navigator.onLine) {
            errorMessage = this.getTranslation('network_unavailable', 'Red no disponible');
            errorType = 'network_unavailable';
            shouldRetry = false; // Don't retry when offline
        } else if (error.type === 'TransportError') {
            if (error.description && error.description.includes('websocket')) {
                errorMessage = this.getTranslation('websocket_connection_failed', 'Error de conexión WebSocket');
                errorType = 'websocket_connection_failed';
            } else if (error.description && error.description.includes('polling')) {
                errorMessage = this.getTranslation('websocket_upgrade_failed', 'Error al actualizar a WebSocket');
                errorType = 'websocket_upgrade_failed';
            } else {
                errorMessage = this.getTranslation('websocket_transport_error', 'Error de transporte WebSocket');
                errorType = 'websocket_transport_error';
            }
        } else if (error.type === 'TimeoutError') {
            if (this.connectionAttempts <= 3) {
                errorMessage = this.getTranslation('network_timeout_short', 'Tiempo de red agotado (corto)');
                errorType = 'network_timeout_short';
                retryDelay = 2000; // Short retry delay for timeouts
            } else if (this.connectionAttempts <= 6) {
                errorMessage = this.getTranslation('network_timeout_medium', 'Tiempo de red agotado (medio)');
                errorType = 'network_timeout_medium';
                retryDelay = 5000; // Medium retry delay
            } else {
                errorMessage = this.getTranslation('network_timeout_long', 'Tiempo de red agotado (largo)');
                errorType = 'network_timeout_long';
                retryDelay = 10000; // Long retry delay
            }
        } else if (error.code) {
            // Handle specific error codes
            switch (error.code) {
                case 1006: // Abnormal closure
                    errorMessage = this.getTranslation('websocket_network_error', 'Error de red WebSocket');
                    errorType = 'websocket_network_error';
                    break;
                case 1011: // Server error
                    errorMessage = this.getTranslation('websocket_server_error', 'Error del servidor WebSocket');
                    errorType = 'websocket_server_error';
                    break;
                case 1012: // Service restart
                    errorMessage = this.getTranslation('websocket_maintenance_mode', 'WebSocket en modo de mantenimiento');
                    errorType = 'websocket_maintenance_mode';
                    retryDelay = 30000; // Longer delay for maintenance
                    break;
                case 1013: // Try again later
                    errorMessage = this.getTranslation('websocket_service_overloaded', 'Servicio WebSocket sobrecargado');
                    errorType = 'websocket_service_overloaded';
                    retryDelay = 15000; // Longer delay for overload
                    break;
                case 4000: // Custom authentication error
                    errorMessage = this.getTranslation('websocket_authentication_failed', 'Error de autenticación WebSocket');
                    errorType = 'websocket_authentication_failed';
                    shouldRetry = false; // Don't retry auth errors
                    break;
                case 4001: // Custom authorization error
                    errorMessage = this.getTranslation('websocket_authorization_failed', 'Error de autorización WebSocket');
                    errorType = 'websocket_authorization_failed';
                    shouldRetry = false; // Don't retry auth errors
                    break;
                case 4029: // Rate limit
                    errorMessage = this.getTranslation('websocket_rate_limit_exceeded', 'Límite de velocidad WebSocket excedido');
                    errorType = 'websocket_rate_limit_exceeded';
                    retryDelay = 60000; // Long delay for rate limits
                    break;
                default:
                    errorMessage = this.getTranslation('websocket_protocol_error', 'Error de protocolo WebSocket');
                    errorType = 'websocket_protocol_error';
            }
        } else if (error.message) {
            // Parse error message for additional context
            const message = error.message.toLowerCase();
            if (message.includes('handshake')) {
                errorMessage = this.getTranslation('websocket_handshake_failed', 'Error en el protocolo de conexión WebSocket');
                errorType = 'websocket_handshake_failed';
            } else if (message.includes('security') || message.includes('ssl') || message.includes('tls')) {
                errorMessage = this.getTranslation('websocket_security_error', 'Error de seguridad WebSocket');
                errorType = 'websocket_security_error';
                shouldRetry = false; // Don't retry security errors
            } else if (message.includes('quota') || message.includes('limit')) {
                errorMessage = this.getTranslation('websocket_quota_exceeded', 'Cuota WebSocket excedida');
                errorType = 'websocket_quota_exceeded';
                retryDelay = 30000; // Long delay for quota issues
            } else {
                errorMessage = this.getTranslation('websocket_client_error', 'Error del cliente WebSocket');
                errorType = 'websocket_client_error';
            }
        } else {
            errorMessage = this.getTranslation('connection_error', 'Error de conexión');
            errorType = 'connection_error';
        }
        
        // Update connection status with specific error type
        this.updateConnectionStatus('disconnected', errorMessage);
        
        // Implement circuit breaker logic
        if (this.connectionAttempts >= 5) {
            this.updateConnectionStatus('disconnected', this.getTranslation('network_circuit_breaker_open', 'Cortacircuitos de red abierto'));
            shouldRetry = false;
            
            // Show manual reconnect option after circuit breaker opens
            setTimeout(() => {
                this.showManualReconnectOption();
            }, 5000);
        }
        
        // Emit custom event for application with enhanced error info
        this.emitEvent('connection_error', { 
            error, 
            attempts: this.connectionAttempts,
            errorType,
            errorMessage,
            shouldRetry,
            retryDelay
        });
        
        // Show user notification for critical errors
        if (!shouldRetry || this.connectionAttempts >= 3) {
            this.showConnectionErrorNotification(errorMessage, errorType);
        }
        
        // Schedule retry if appropriate
        if (shouldRetry && navigator.onLine && this.connectionAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnection(retryDelay);
        }
    }
    
    handleReconnect(attemptNumber) {
        /**
         * Handle successful reconnection
         */
        console.info('SocketIO reconnected after', attemptNumber, 'attempts');
        
        this.connectionAttempts = 0;
        this.reconnectDelay = 1000; // Reset delay
        
        this.updateConnectionStatus('connected', this.getTranslation('reconnect_success', 'Reconexión exitosa'));
        
        // Emit custom event for application
        this.emitEvent('reconnected', { attempts: attemptNumber });
        
        // Announce to screen readers
        this.announceToScreenReader(this.getTranslation('connection_restored', 'Conexión restaurada'));
    }
    
    handleReconnectAttempt(attemptNumber) {
        /**
         * Handle reconnection attempts
         */
        console.info('SocketIO reconnection attempt:', attemptNumber);
        
        this.connectionAttempts = attemptNumber;
        
        const message = `${this.getTranslation('reconnect_attempt', 'Intento de reconexión')} ${attemptNumber}/${this.maxReconnectAttempts}`;
        this.updateConnectionStatus('reconnecting', message);
        
        // Emit custom event for application
        this.emitEvent('reconnect_attempt', { attempt: attemptNumber });
    }
    
    handleReconnectError(error) {
        /**
         * Handle reconnection errors
         */
        console.error('SocketIO reconnection error:', error);
        
        // Emit custom event for application
        this.emitEvent('reconnect_error', { error, attempts: this.connectionAttempts });
    }
    
    handleReconnectFailed() {
        /**
         * Handle failed reconnection
         */
        console.error('SocketIO reconnection failed after', this.maxReconnectAttempts, 'attempts');
        
        this.updateConnectionStatus('disconnected', this.getTranslation('max_reconnect_attempts', 'Máximo de intentos de reconexión alcanzado'));
        
        // Emit custom event for application
        this.emitEvent('reconnect_failed', { maxAttempts: this.maxReconnectAttempts });
        
        // Show manual reconnect option
        this.showManualReconnectOption();
        
        // Announce to screen readers
        this.announceToScreenReader(this.getTranslation('reconnect_failed', 'Reconexión fallida'));
    }
    
    handleConnectionStatusUpdate(data) {
        /**
         * Handle connection status updates from server
         */
        console.info('Connection status update:', data);
        
        if (data.status === 'connected') {
            this.updateConnectionDetails(data);
        }
        
        // Emit custom event for application
        this.emitEvent('status_update', data);
    }
    
    handleSocketError(error) {
        /**
         * Handle general socket errors
         */
        console.error('SocketIO error:', error);
        
        // Emit custom event for application
        this.emitEvent('socket_error', { error });
    }
    
    handlePong(data) {
        /**
         * Handle pong response for connection quality monitoring
         */
        if (this.lastPingTime) {
            const latency = Date.now() - this.lastPingTime;
            this.updateConnectionQuality(latency);
            
            // Determine network quality based on latency
            let quality;
            if (latency < 100) {
                quality = 'excellent';
            } else if (latency < 300) {
                quality = 'good';
            } else if (latency < 1000) {
                quality = 'fair';
            } else if (latency < 3000) {
                quality = 'poor';
            } else {
                quality = 'unstable';
            }
            
            // Update quality if it changed significantly
            if (quality !== this.connectionQuality) {
                this.handleNetworkQualityChange(quality);
            }
        }
    }
    
    handleServiceDegradation(data) {
        /**
         * Handle service degradation notifications
         */
        console.warn('Service degradation detected:', data);
        
        const degradationType = data.type || 'general';
        const message = data.message || this.getTranslation('realtime_service_degraded_notification', 'Servicio en tiempo real funcionando con limitaciones');
        
        // Show degraded service notification
        this.showServiceStatusNotification(message, 'degraded');
        
        // Emit event for application
        this.emitEvent('service_degraded', { degradationType, message, data });
    }
    
    handleServiceRestoration(data) {
        /**
         * Handle service restoration notifications
         */
        console.info('Service restoration detected:', data);
        
        const message = data.message || this.getTranslation('realtime_service_restored_notification', 'Servicio en tiempo real completamente restaurado');
        
        // Show service restored notification
        this.showServiceStatusNotification(message, 'restored');
        
        // Reset connection quality monitoring to normal interval
        this.startConnectionMonitoring(30000);
        
        // Emit event for application
        this.emitEvent('service_restored', { message, data });
    }
    
    handleConflictResolution(data) {
        /**
         * Handle conflict resolution notifications
         */
        console.info('Conflict resolution completed:', data);
        
        const resolutionType = data.resolution_type || 'unknown';
        const success = data.success !== false;
        
        this.showConflictResolutionNotification(resolutionType, success);
        
        // Emit event for application
        this.emitEvent('conflict_resolved', { resolutionType, success, data });
    }
    
    handleSessionCleanup(data) {
        /**
         * Handle session cleanup notifications
         */
        console.info('Session cleanup performed:', data);
        
        // Update session count if provided
        if (data.remaining_sessions !== undefined) {
            this.emitEvent('session_count_updated', { 
                connected_sessions: data.remaining_sessions,
                cleaned_sessions: data.cleaned_sessions || 0
            });
        }
    }
    
    handleBroadcastFailure(data) {
        /**
         * Handle broadcast failure notifications
         */
        console.warn('Broadcast failure detected:', data);
        
        const failureType = data.type || 'general';
        const affectedSessions = data.affected_sessions || 0;
        
        // Show notification for significant broadcast failures
        if (affectedSessions > 1) {
            const message = this.getTranslation('session_broadcast_failed', 'Error en difusión de sesión') + 
                          ` (${affectedSessions} sesiones afectadas)`;
            this.showServiceStatusNotification(message, 'warning');
        }
        
        // Emit event for application
        this.emitEvent('broadcast_failed', { failureType, affectedSessions, data });
    }
    
    showServiceStatusNotification(message, type) {
        /**
         * Show service status notification
         */
        const alertClass = type === 'restored' ? 'alert-success' : 
                          type === 'degraded' ? 'alert-warning' : 'alert-info';
        const iconClass = type === 'restored' ? 'bi-check-circle' : 
                         type === 'degraded' ? 'bi-exclamation-triangle' : 'bi-info-circle';
        
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 220px;
            right: 20px;
            z-index: 9994;
            max-width: 350px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${iconClass} me-2" aria-hidden="true"></i>
                <div class="flex-grow-1">
                    <small>${message}</small>
                </div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()" aria-label="Cerrar"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    handleNetworkOnline() {
        /**
         * Handle network coming online
         */
        console.info('Network is online');
        
        if (!this.isConnected && this.socket) {
            this.socket.connect();
        }
        
        // Emit custom event for application
        this.emitEvent('network_online');
    }
    
    handleNetworkOffline() {
        /**
         * Handle network going offline
         */
        console.warn('Network is offline');
        
        this.updateConnectionStatus('disconnected', this.getTranslation('network_unavailable', 'Red no disponible'));
        
        // Emit custom event for application
        this.emitEvent('network_offline');
    }
    
    handleVisibilityChange() {
        /**
         * Handle page visibility changes
         */
        if (document.hidden) {
            // Page is hidden - reduce connection activity
            if (this.pingInterval) {
                clearInterval(this.pingInterval);
                this.pingInterval = null;
            }
        } else {
            // Page is visible - resume connection activity
            if (!this.pingInterval && this.isConnected) {
                this.startConnectionMonitoring();
            }
            
            // Check connection status
            if (!this.isConnected && navigator.onLine) {
                this.reconnect();
            }
        }
    }
    
    scheduleReconnection(delay) {
        /**
         * Schedule reconnection with enhanced retry logic
         */
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        
        this.updateConnectionStatus('reconnecting', 
            this.getTranslation('network_retry_scheduled', 'Reintento de red programado') + ` (${Math.round(delay/1000)}s)`);
        
        this.reconnectTimer = setTimeout(() => {
            if (!this.isConnected && navigator.onLine) {
                console.info('Attempting scheduled reconnection...');
                this.updateConnectionStatus('reconnecting', this.getTranslation('network_retry_in_progress', 'Reintentando conexión de red'));
                this.socket.connect();
            }
        }, delay);
    }
    
    showConnectionErrorNotification(message, errorType) {
        /**
         * Show connection error notification to user
         */
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show position-fixed';
        notification.style.cssText = `
            top: 60px;
            right: 20px;
            z-index: 9998;
            max-width: 350px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        const iconClass = errorType.includes('websocket') ? 'bi-wifi-off' : 
                         errorType.includes('network') ? 'bi-exclamation-triangle' : 'bi-x-circle';
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${iconClass} me-2" aria-hidden="true"></i>
                <div class="flex-grow-1">
                    <strong>${this.getTranslation('connection_error', 'Error de conexión')}</strong><br>
                    <small>${message}</small>
                </div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()" aria-label="Cerrar"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-dismiss after 8 seconds
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.remove();
            }
        }, 8000);
    }
    
    handleSessionSyncConflict(conflictData) {
        /**
         * Handle session synchronization conflicts with resolution strategies
         */
        console.warn('Session sync conflict detected:', conflictData);
        
        const conflictType = conflictData.type || 'unknown';
        const conflictResolution = conflictData.resolution || 'last_write_wins';
        
        // Show conflict notification to user
        this.showSyncConflictNotification(conflictType, conflictResolution);
        
        // Apply conflict resolution strategy
        switch (conflictResolution) {
            case 'last_write_wins':
                this.applyLastWriteWins(conflictData);
                break;
            case 'first_write_wins':
                this.applyFirstWriteWins(conflictData);
                break;
            case 'merge':
                this.attemptMergeResolution(conflictData);
                break;
            case 'manual':
                this.requestManualResolution(conflictData);
                break;
            default:
                this.applyLastWriteWins(conflictData); // Default strategy
        }
        
        // Emit event for application handling
        this.emitEvent('session_sync_conflict', {
            conflictType,
            conflictResolution,
            conflictData,
            timestamp: Date.now()
        });
    }
    
    applyLastWriteWins(conflictData) {
        /**
         * Apply last-write-wins conflict resolution
         */
        console.info('Applying last-write-wins conflict resolution');
        
        // The server should have already applied this strategy
        // Just update local state and notify user
        this.showConflictResolutionNotification('last_write_wins', true);
        
        // Request current state to ensure synchronization
        if (this.socket && this.isConnected) {
            this.socket.emit('request_current_song');
        }
    }
    
    applyFirstWriteWins(conflictData) {
        /**
         * Apply first-write-wins conflict resolution
         */
        console.info('Applying first-write-wins conflict resolution');
        
        // Similar to last-write-wins, server handles the logic
        this.showConflictResolutionNotification('first_write_wins', true);
        
        // Request current state to ensure synchronization
        if (this.socket && this.isConnected) {
            this.socket.emit('request_current_song');
        }
    }
    
    attemptMergeResolution(conflictData) {
        /**
         * Attempt to merge conflicting changes
         */
        console.info('Attempting merge conflict resolution');
        
        try {
            // For song selection conflicts, merging might not be applicable
            // Fall back to last-write-wins
            this.applyLastWriteWins(conflictData);
            this.showConflictResolutionNotification('merge_successful', true);
        } catch (error) {
            console.error('Merge resolution failed:', error);
            this.showConflictResolutionNotification('merge_failed', false);
            // Fall back to last-write-wins
            this.applyLastWriteWins(conflictData);
        }
    }
    
    requestManualResolution(conflictData) {
        /**
         * Request manual conflict resolution from user
         */
        console.info('Requesting manual conflict resolution');
        
        // Show modal or notification for manual resolution
        this.showManualResolutionDialog(conflictData);
    }
    
    showSyncConflictNotification(conflictType, resolutionStrategy) {
        /**
         * Show sync conflict notification to user
         */
        const message = this.getTranslation('realtime_sync_conflict_notification', 'Conflicto de sincronización detectado. Resolviendo automáticamente...');
        
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show position-fixed';
        notification.style.cssText = `
            top: 100px;
            right: 20px;
            z-index: 9997;
            max-width: 350px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-arrow-repeat me-2" aria-hidden="true"></i>
                <div class="flex-grow-1">
                    <strong>${this.getTranslation('sync_conflict', 'Conflicto de sincronización')}</strong><br>
                    <small>${message}</small>
                </div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()" aria-label="Cerrar"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    showConflictResolutionNotification(resolutionType, success) {
        /**
         * Show conflict resolution result notification
         */
        const message = success ? 
            this.getTranslation('realtime_sync_conflict_resolved_notification', 'Conflicto de sincronización resuelto') :
            this.getTranslation('conflict_resolution_failed', 'Error en resolución de conflicto');
        
        const alertClass = success ? 'alert-success' : 'alert-warning';
        const iconClass = success ? 'bi-check-circle' : 'bi-exclamation-triangle';
        
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 140px;
            right: 20px;
            z-index: 9996;
            max-width: 350px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${iconClass} me-2" aria-hidden="true"></i>
                <div class="flex-grow-1">
                    <small>${message}</small>
                </div>
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
    
    showManualResolutionDialog(conflictData) {
        /**
         * Show manual resolution dialog for complex conflicts
         */
        // This would typically show a modal dialog
        // For now, just show a notification and fall back to automatic resolution
        const message = this.getTranslation('conflict_manual_resolution_required', 'Resolución manual de conflicto requerida');
        
        console.warn('Manual resolution required but not implemented, falling back to automatic resolution');
        this.applyLastWriteWins(conflictData);
    }
    
    handleNetworkQualityChange(quality) {
        /**
         * Handle network quality changes and adapt behavior
         */
        this.connectionQuality = quality;
        
        let qualityMessage;
        let shouldAdjustBehavior = false;
        
        switch (quality) {
            case 'excellent':
                qualityMessage = this.getTranslation('connected', 'Conectado');
                break;
            case 'good':
                qualityMessage = this.getTranslation('connected', 'Conectado');
                break;
            case 'fair':
                qualityMessage = this.getTranslation('network_quality_degraded', 'Calidad de red degradada');
                shouldAdjustBehavior = true;
                break;
            case 'poor':
                qualityMessage = this.getTranslation('network_quality_poor', 'Calidad de red pobre');
                shouldAdjustBehavior = true;
                break;
            case 'unstable':
                qualityMessage = this.getTranslation('network_quality_unstable', 'Calidad de red inestable');
                shouldAdjustBehavior = true;
                break;
            default:
                qualityMessage = this.getTranslation('connection_status', 'Estado de conexión');
        }
        
        // Update connection status display
        if (this.isConnected) {
            this.updateConnectionStatus('connected', qualityMessage);
        }
        
        // Adjust behavior for poor network quality
        if (shouldAdjustBehavior) {
            this.adjustForPoorNetworkQuality(quality);
        }
        
        // Emit event for application
        this.emitEvent('network_quality_change', { quality, qualityMessage });
    }
    
    adjustForPoorNetworkQuality(quality) {
        /**
         * Adjust connection behavior for poor network quality
         */
        console.info(`Adjusting behavior for ${quality} network quality`);
        
        // Increase ping interval for poor connections
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
        }
        
        const pingIntervalMs = quality === 'poor' ? 60000 : 45000; // 60s for poor, 45s for fair/unstable
        this.startConnectionMonitoring(pingIntervalMs);
        
        // Show degraded service notification
        if (quality === 'poor' || quality === 'unstable') {
            this.showDegradedServiceNotification();
        }
    }
    
    showDegradedServiceNotification() {
        /**
         * Show degraded service notification
         */
        const message = this.getTranslation('realtime_service_degraded_notification', 'Servicio en tiempo real funcionando con limitaciones');
        
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show position-fixed';
        notification.style.cssText = `
            top: 180px;
            right: 20px;
            z-index: 9995;
            max-width: 350px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>
                <div class="flex-grow-1">
                    <strong>${this.getTranslation('service_degraded', 'Servicio degradado')}</strong><br>
                    <small>${message}</small>
                </div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()" aria-label="Cerrar"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-dismiss after 6 seconds
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.remove();
            }
        }, 6000);
    }
    
    updateConnectionStatus(status, message) {
        /**
         * Update visual connection status
         */
        if (!this.statusIcon || !this.statusText || !this.connectionDetails) {
            return;
        }
        
        // Update icon
        this.statusIcon.className = `status-icon ${status}`;
        
        // Update icon based on status
        const iconElement = this.statusIcon.querySelector('i');
        if (iconElement) {
            switch (status) {
                case 'connected':
                    iconElement.className = 'bi bi-wifi';
                    break;
                case 'connecting':
                case 'reconnecting':
                    iconElement.className = 'bi bi-arrow-clockwise';
                    break;
                case 'disconnected':
                    iconElement.className = 'bi bi-wifi-off';
                    break;
                default:
                    iconElement.className = 'bi bi-question-circle';
            }
        }
        
        // Update text
        this.statusText.textContent = this.getConnectionStatusText(status);
        
        // Update details
        this.connectionDetails.innerHTML = `<small class="text-muted">${message}</small>`;
        
        // Update accessibility
        this.statusIndicator.setAttribute('aria-label', `${this.getConnectionStatusText(status)}: ${message}`);
    }
    
    updateConnectionDetails(data) {
        /**
         * Update connection details with server information
         */
        if (data.session_id && this.connectionDetails) {
            const details = [
                `ID: ${data.session_id.substring(0, 8)}...`,
                data.current_state ? `${data.current_state.connected_sessions} sesiones` : ''
            ].filter(Boolean).join(' • ');
            
            this.connectionDetails.innerHTML = `<small class="text-muted">${details}</small>`;
        }
    }
    
    updateConnectionQuality(latency) {
        /**
         * Update connection quality based on latency
         */
        let quality;
        if (latency < 100) {
            quality = 'excellent';
        } else if (latency < 300) {
            quality = 'good';
        } else if (latency < 1000) {
            quality = 'fair';
        } else {
            quality = 'poor';
        }
        
        this.connectionQuality = quality;
        
        // Update UI if needed
        if (this.connectionDetails) {
            const currentText = this.connectionDetails.textContent;
            if (!currentText.includes('ms')) {
                this.connectionDetails.innerHTML += ` <small class="text-muted">(${latency}ms)</small>`;
            }
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
    
    showConnectionDetails() {
        /**
         * Show detailed connection information
         */
        const details = {
            status: this.isConnected ? 'connected' : 'disconnected',
            sessionId: this.socket?.id || 'N/A',
            transport: this.socket?.io?.engine?.transport?.name || 'N/A',
            quality: this.connectionQuality,
            attempts: this.connectionAttempts,
            online: navigator.onLine
        };
        
        console.info('Connection Details:', details);
        
        // Could show a modal or tooltip with details
        // For now, just log to console
    }
    
    showManualReconnectOption() {
        /**
         * Show manual reconnect button
         */
        if (this.connectionDetails) {
            const reconnectBtn = document.createElement('button');
            reconnectBtn.className = 'btn btn-sm btn-outline-primary mt-1';
            reconnectBtn.textContent = this.getTranslation('manual_reconnect', 'Reconectar');
            reconnectBtn.onclick = () => {
                this.reconnect();
                reconnectBtn.remove();
            };
            
            this.connectionDetails.appendChild(reconnectBtn);
        }
    }
    
    joinGlobalSession() {
        /**
         * Join global session for real-time features
         */
        if (this.socket && this.isConnected) {
            this.socket.emit('join_global_session', {
                client_info: {
                    userAgent: navigator.userAgent.substring(0, 100),
                    language: navigator.language,
                    platform: navigator.platform
                },
                connection_type: this.socket.io.engine.transport.name
            });
        }
    }
    
    reconnect() {
        /**
         * Manually trigger reconnection
         */
        if (this.socket) {
            this.updateConnectionStatus('connecting', this.getTranslation('reconnecting', 'Reconectando...'));
            this.socket.connect();
        }
    }
    
    disconnect() {
        /**
         * Manually disconnect
         */
        if (this.socket) {
            this.socket.disconnect();
        }
    }
    
    // Event system for application integration
    on(event, callback) {
        /**
         * Register event listener
         */
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }
    
    off(event, callback) {
        /**
         * Remove event listener
         */
        if (this.eventListeners.has(event)) {
            const listeners = this.eventListeners.get(event);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }
    
    emitEvent(event, data = {}) {
        /**
         * Emit custom event to registered listeners
         */
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in event listener:', error);
                }
            });
        }
    }
    
    // Utility methods
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
    
    cleanup() {
        /**
         * Clean up resources
         */
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
        }
        
        if (this.socket) {
            this.socket.disconnect();
        }
        
        this.eventListeners.clear();
    }
    
    // Public API
    getSocket() {
        return this.socket;
    }
    
    isSocketConnected() {
        return this.isConnected;
    }
    
    getConnectionQuality() {
        return this.connectionQuality;
    }
    
    getConnectionAttempts() {
        return this.connectionAttempts;
    }
}

// Initialize connection manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.connectionManager = new ConnectionManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConnectionManager;
}