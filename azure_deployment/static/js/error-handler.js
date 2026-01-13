/**
 * Enhanced Error Handling and Retry Mechanisms for Rock and Roll Forum Jam en Español
 * Provides comprehensive error handling, retry logic, and data consistency validation
 */

class ErrorHandler {
    constructor() {
        this.maxRetries = 3;
        this.retryDelay = 1000; // 1 second
        this.backoffFactor = 2;
        this.circuitBreakerThreshold = 5;
        this.circuitBreakerTimeout = 60000; // 1 minute
        
        // Error tracking
        this.errorCounts = new Map();
        this.circuitBreakers = new Map();
        this.lastDataHash = null;
        
        // Spanish translations
        this.translations = window.translations || {};
        
        this.init();
    }
    
    init() {
        // Set up global error handlers
        window.addEventListener('unhandledrejection', (event) => {
            this.handleUnhandledError(event.reason, 'unhandled_promise_rejection');
        });
        
        window.addEventListener('error', (event) => {
            this.handleUnhandledError(event.error, 'unhandled_error');
        });
        
        // Set up periodic data consistency checks
        setInterval(() => {
            this.checkDataConsistency();
        }, 300000); // 5 minutes
    }
    
    getTranslation(key, defaultValue = key) {
        return this.translations[key] || defaultValue;
    }
    
    async retryWithBackoff(operation, operationName, maxRetries = this.maxRetries) {
        /**
         * Execute an operation with exponential backoff retry logic and enhanced real-time support.
         * 
         * @param {Function} operation - The async operation to retry
         * @param {string} operationName - Name for logging and circuit breaker
         * @param {number} maxRetries - Maximum number of retry attempts
         * @returns {Promise} - Result of the operation
         */
        
        // Check circuit breaker
        if (this.isCircuitBreakerOpen(operationName)) {
            throw new Error(this.getTranslation('server_unavailable', 'Servidor no disponible'));
        }
        
        let lastError;
        let delay = this.retryDelay;
        
        // Adjust retry parameters for real-time operations
        const isRealTimeOperation = operationName.includes('realtime') || 
                                   operationName.includes('websocket') || 
                                   operationName.includes('global') ||
                                   operationName.includes('session');
        
        if (isRealTimeOperation) {
            maxRetries = Math.min(maxRetries, 5); // Limit retries for real-time ops
            delay = Math.max(delay, 500); // Minimum delay for real-time ops
        }
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const result = await operation();
                
                // Reset error count on success
                this.errorCounts.set(operationName, 0);
                
                // Show success notification for recovered real-time operations
                if (isRealTimeOperation && attempt > 1) {
                    this.showRealTimeRecoveryNotification(operationName);
                }
                
                return result;
                
            } catch (error) {
                lastError = error;
                
                // Increment error count
                const errorCount = (this.errorCounts.get(operationName) || 0) + 1;
                this.errorCounts.set(operationName, errorCount);
                
                // Check if circuit breaker should be triggered
                if (errorCount >= this.circuitBreakerThreshold) {
                    this.openCircuitBreaker(operationName);
                }
                
                console.warn(`Attempt ${attempt} failed for ${operationName}:`, error.message);
                
                // Don't retry on certain error types
                if (this.isNonRetryableError(error)) {
                    break;
                }
                
                // Special handling for real-time errors
                if (isRealTimeOperation) {
                    this.handleRealTimeRetryError(error, operationName, attempt, maxRetries);
                }
                
                // Wait before retrying (except on last attempt)
                if (attempt < maxRetries) {
                    // Show retry notification for real-time operations
                    if (isRealTimeOperation) {
                        this.showRealTimeRetryNotification(operationName, attempt, maxRetries, delay);
                    }
                    
                    await this.sleep(delay);
                    delay *= this.backoffFactor;
                    
                    // Cap delay for real-time operations
                    if (isRealTimeOperation) {
                        delay = Math.min(delay, 10000); // Max 10 seconds for real-time
                    }
                }
            }
        }
        
        console.error(`All ${maxRetries} attempts failed for ${operationName}:`, lastError);
        
        // Show failure notification for real-time operations
        if (isRealTimeOperation) {
            this.showRealTimeFailureNotification(operationName, lastError);
        }
        
        throw lastError;
    }
    
    handleRealTimeRetryError(error, operationName, attempt, maxRetries) {
        /**
         * Handle real-time specific retry errors
         */
        // Classify error severity for real-time operations
        let errorSeverity = 'medium';
        
        if (error.code) {
            switch (error.code) {
                case 4000: // Authentication
                case 4001: // Authorization
                    errorSeverity = 'critical'; // Don't retry auth errors
                    break;
                case 1012: // Service restart
                case 1013: // Try again later
                    errorSeverity = 'high'; // Longer delays
                    break;
                case 1006: // Network issues
                    errorSeverity = 'medium'; // Normal retry
                    break;
                default:
                    errorSeverity = 'low'; // Quick retry
            }
        }
        
        // Adjust retry behavior based on severity
        if (errorSeverity === 'critical') {
            throw error; // Don't retry critical errors
        }
        
        // Log real-time specific error context
        console.warn(`Real-time operation ${operationName} failed (attempt ${attempt}/${maxRetries}), severity: ${errorSeverity}`);
    }
    
    showRealTimeRetryNotification(operationName, attempt, maxRetries, delay) {
        /**
         * Show retry notification for real-time operations
         */
        const message = this.getTranslation('network_retry_in_progress', 'Reintentando conexión de red') + 
                       ` (${attempt}/${maxRetries}) - ${Math.round(delay/1000)}s`;
        
        // Only show notification for later attempts to avoid spam
        if (attempt >= 2) {
            this.showTemporaryNotification(message, 'info', 3000);
        }
    }
    
    showRealTimeRecoveryNotification(operationName) {
        /**
         * Show recovery notification for real-time operations
         */
        const message = this.getTranslation('realtime_update_successful_notification', 'Actualización en tiempo real exitosa');
        this.showTemporaryNotification(message, 'success', 3000);
    }
    
    showRealTimeFailureNotification(operationName, error) {
        /**
         * Show failure notification for real-time operations
         */
        const message = this.getTranslation('realtime_update_failed_notification', 'Error al actualizar en tiempo real. Reintentando...');
        this.showTemporaryNotification(message, 'warning', 5000);
    }
    
    showTemporaryNotification(message, type = 'info', duration = 4000) {
        /**
         * Show temporary notification to user
         */
        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'warning' ? 'alert-warning' : 
                          type === 'error' ? 'alert-danger' : 'alert-info';
        const iconClass = type === 'success' ? 'bi-check-circle' : 
                         type === 'warning' ? 'bi-exclamation-triangle' : 
                         type === 'error' ? 'bi-x-circle' : 'bi-info-circle';
        
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 260px;
            right: 20px;
            z-index: 9993;
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
        
        // Auto-dismiss after specified duration
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }
    
    isNonRetryableError(error) {
        /**
         * Check if an error should not be retried.
         * 
         * @param {Error} error - The error to check
         * @returns {boolean} - True if error should not be retried
         */
        if (error.status) {
            // Don't retry client errors (4xx) except for 408 (timeout) and 429 (rate limit)
            return error.status >= 400 && error.status < 500 && 
                   error.status !== 408 && error.status !== 429;
        }
        
        return false;
    }
    
    isCircuitBreakerOpen(operationName) {
        /**
         * Check if circuit breaker is open for an operation.
         * 
         * @param {string} operationName - Name of the operation
         * @returns {boolean} - True if circuit breaker is open
         */
        const breaker = this.circuitBreakers.get(operationName);
        if (!breaker) return false;
        
        const now = Date.now();
        if (now - breaker.openedAt > this.circuitBreakerTimeout) {
            // Reset circuit breaker after timeout
            this.circuitBreakers.delete(operationName);
            this.errorCounts.set(operationName, 0);
            console.info(`Circuit breaker reset for ${operationName}`);
            return false;
        }
        
        return true;
    }
    
    openCircuitBreaker(operationName) {
        /**
         * Open circuit breaker for an operation.
         * 
         * @param {string} operationName - Name of the operation
         */
        this.circuitBreakers.set(operationName, {
            openedAt: Date.now(),
            errorCount: this.errorCounts.get(operationName) || 0
        });
        
        console.warn(`Circuit breaker opened for ${operationName}`);
    }
    
    async enhancedFetch(url, options = {}, operationName = 'fetch') {
        /**
         * Enhanced fetch with retry logic and error handling.
         * 
         * @param {string} url - URL to fetch
         * @param {Object} options - Fetch options
         * @param {string} operationName - Operation name for tracking
         * @returns {Promise<Response>} - Fetch response
         */
        return this.retryWithBackoff(async () => {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
            
            try {
                const response = await fetch(url, {
                    ...options,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
                    error.status = response.status;
                    error.response = response;
                    throw error;
                }
                
                return response;
                
            } catch (error) {
                clearTimeout(timeoutId);
                
                if (error.name === 'AbortError') {
                    const timeoutError = new Error(this.getTranslation('timeout_error', 'Tiempo de espera agotado'));
                    timeoutError.status = 504;
                    throw timeoutError;
                }
                
                throw error;
            }
        }, operationName);
    }
    
    async handleApiError(error, context = '') {
        /**
         * Handle API errors with appropriate user messaging and enhanced real-time error support.
         * 
         * @param {Error} error - The error to handle
         * @param {string} context - Additional context for the error
         * @returns {string} - User-friendly error message in Spanish
         */
        console.error(`API Error${context ? ` in ${context}` : ''}:`, error);
        
        // Network errors
        if (!navigator.onLine) {
            return this.getTranslation('network_error', 'Error de conexión de red');
        }
        
        if (error.name === 'AbortError' || error.message.includes('timeout')) {
            return this.getTranslation('timeout_error', 'Tiempo de espera agotado');
        }
        
        // WebSocket specific errors
        if (error.type === 'websocket' || context.includes('websocket') || context.includes('socketio')) {
            return this.handleWebSocketError(error, context);
        }
        
        // Session synchronization errors
        if (error.type === 'session_sync' || context.includes('session') || context.includes('sync')) {
            return this.handleSessionSyncError(error, context);
        }
        
        // Real-time specific errors
        if (error.type === 'realtime' || context.includes('realtime') || context.includes('global')) {
            return this.handleRealTimeError(error, context);
        }
        
        // HTTP status errors
        if (error.status) {
            switch (error.status) {
                case 404:
                    return this.getTranslation('not_found', 'No encontrado');
                case 500:
                    return this.getTranslation('server_error', 'Error del servidor');
                case 503:
                    return this.getTranslation('server_unavailable', 'Servidor no disponible');
                case 504:
                    return this.getTranslation('timeout_error', 'Tiempo de espera agotado');
                default:
                    return this.getTranslation('api_error', 'Error en la API');
            }
        }
        
        // Parse JSON error responses
        if (error.response) {
            try {
                const errorData = await error.response.json();
                if (errorData.error) {
                    return errorData.error;
                }
            } catch (parseError) {
                // Ignore JSON parsing errors
            }
        }
        
        // Generic error
        return this.getTranslation('server_error', 'Error del servidor');
    }
    
    handleWebSocketError(error, context) {
        /**
         * Handle WebSocket-specific errors with detailed classification
         */
        console.error('WebSocket error:', error, 'Context:', context);
        
        // Classify WebSocket error type
        if (error.code) {
            switch (error.code) {
                case 1006: // Abnormal closure
                    return this.getTranslation('websocket_network_error', 'Error de red WebSocket');
                case 1011: // Server error
                    return this.getTranslation('websocket_server_error', 'Error del servidor WebSocket');
                case 1012: // Service restart
                    return this.getTranslation('websocket_maintenance_mode', 'WebSocket en modo de mantenimiento');
                case 1013: // Try again later
                    return this.getTranslation('websocket_service_overloaded', 'Servicio WebSocket sobrecargado');
                case 4000: // Custom authentication error
                    return this.getTranslation('websocket_authentication_failed', 'Error de autenticación WebSocket');
                case 4001: // Custom authorization error
                    return this.getTranslation('websocket_authorization_failed', 'Error de autorización WebSocket');
                case 4029: // Rate limit
                    return this.getTranslation('websocket_rate_limit_exceeded', 'Límite de velocidad WebSocket excedido');
                default:
                    return this.getTranslation('websocket_protocol_error', 'Error de protocolo WebSocket');
            }
        }
        
        // Check error message for additional context
        if (error.message) {
            const message = error.message.toLowerCase();
            if (message.includes('handshake')) {
                return this.getTranslation('websocket_handshake_failed', 'Error en el protocolo de conexión WebSocket');
            } else if (message.includes('security') || message.includes('ssl') || message.includes('tls')) {
                return this.getTranslation('websocket_security_error', 'Error de seguridad WebSocket');
            } else if (message.includes('quota') || message.includes('limit')) {
                return this.getTranslation('websocket_quota_exceeded', 'Cuota WebSocket excedida');
            } else if (message.includes('transport')) {
                return this.getTranslation('websocket_transport_error', 'Error de transporte WebSocket');
            }
        }
        
        // Default WebSocket error
        return this.getTranslation('websocket_connection_failed', 'Error de conexión WebSocket');
    }
    
    handleSessionSyncError(error, context) {
        /**
         * Handle session synchronization errors
         */
        console.error('Session sync error:', error, 'Context:', context);
        
        // Classify session sync error type
        if (error.type) {
            switch (error.type) {
                case 'conflict':
                    return this.getTranslation('session_conflict_detected', 'Conflicto de sesión detectado');
                case 'state_mismatch':
                    return this.getTranslation('session_state_mismatch', 'Desajuste de estado de sesión');
                case 'data_corrupted':
                    return this.getTranslation('session_data_corrupted', 'Datos de sesión corruptos');
                case 'timeout':
                    return this.getTranslation('session_timeout_exceeded', 'Tiempo de sesión excedido');
                case 'invalid_state':
                    return this.getTranslation('session_invalid_state', 'Estado de sesión inválido');
                case 'recovery_failed':
                    return this.getTranslation('session_recovery_failed', 'Error en recuperación de sesión');
                case 'cleanup_failed':
                    return this.getTranslation('session_cleanup_failed', 'Error en limpieza de sesión');
                case 'broadcast_failed':
                    return this.getTranslation('session_broadcast_failed', 'Error en difusión de sesión');
                case 'update_rejected':
                    return this.getTranslation('session_update_rejected', 'Actualización de sesión rechazada');
                case 'version_mismatch':
                    return this.getTranslation('session_version_mismatch', 'Desajuste de versión de sesión');
                case 'lock_timeout':
                    return this.getTranslation('session_lock_timeout', 'Tiempo de bloqueo de sesión agotado');
                case 'concurrent_modification':
                    return this.getTranslation('session_concurrent_modification', 'Modificación concurrente de sesión');
                case 'rollback_failed':
                    return this.getTranslation('session_rollback_failed', 'Error en reversión de sesión');
                case 'persistence_failed':
                    return this.getTranslation('session_persistence_failed', 'Error en persistencia de sesión');
                default:
                    return this.getTranslation('session_sync_failed', 'Error de sincronización de sesión');
            }
        }
        
        // Default session sync error
        return this.getTranslation('session_sync_failed', 'Error de sincronización de sesión');
    }
    
    handleRealTimeError(error, context) {
        /**
         * Handle real-time specific errors
         */
        console.error('Real-time error:', error, 'Context:', context);
        
        // Check for specific real-time error patterns
        if (error.message) {
            const message = error.message.toLowerCase();
            if (message.includes('global') && message.includes('state')) {
                return this.getTranslation('global_state_error', 'Error de estado global');
            } else if (message.includes('global') && message.includes('update')) {
                return this.getTranslation('global_update_error', 'Error de actualización global');
            } else if (message.includes('global') && message.includes('sync')) {
                return this.getTranslation('global_sync_error', 'Error de sincronización global');
            } else if (message.includes('global') && message.includes('session')) {
                return this.getTranslation('global_session_error', 'Error de sesión global');
            } else if (message.includes('global') && message.includes('broadcast')) {
                return this.getTranslation('global_broadcast_error', 'Error de difusión global');
            } else if (message.includes('global') && message.includes('connection')) {
                return this.getTranslation('global_connection_error', 'Error de conexión global');
            }
        }
        
        // Default real-time error
        return this.getTranslation('realtime_update_failed_notification', 'Error al actualizar en tiempo real. Reintentando...');
    }
    
    handleUnhandledError(error, type) {
        /**
         * Handle unhandled errors globally.
         * 
         * @param {Error} error - The unhandled error
         * @param {string} type - Type of unhandled error
         */
        console.error(`Unhandled ${type}:`, error);
        
        // Show user-friendly error message
        this.showGlobalErrorMessage(
            this.getTranslation('server_error', 'Ha ocurrido un error inesperado. Por favor, actualiza la página.')
        );
    }
    
    showGlobalErrorMessage(message) {
        /**
         * Show a global error message to the user.
         * 
         * @param {string} message - Error message to display
         */
        // Create or update global error banner
        let errorBanner = document.getElementById('global-error-banner');
        
        if (!errorBanner) {
            errorBanner = document.createElement('div');
            errorBanner.id = 'global-error-banner';
            errorBanner.className = 'alert alert-danger alert-dismissible fade show position-fixed';
            errorBanner.style.cssText = `
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            `;
            
            document.body.appendChild(errorBanner);
        }
        
        errorBanner.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-exclamation-triangle-fill me-2" aria-hidden="true"></i>
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()" aria-label="Cerrar"></button>
            </div>
        `;
        
        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            if (errorBanner && errorBanner.parentNode) {
                errorBanner.remove();
            }
        }, 10000);
    }
    
    async checkDataConsistency() {
        /**
         * Check data consistency across all sections.
         */
        try {
            const response = await fetch('/api/data-consistency');
            if (response.ok) {
                const consistencyData = await response.json();
                
                // Handle consistency issues
                if (consistencyData.overall_status !== 'healthy') {
                    console.warn('Data consistency issues detected:', consistencyData);
                }
            }
        } catch (error) {
            console.debug('Data consistency check failed:', error.message);
            // Don't show user errors for background consistency checks
        }
    }
    
    notifyDataChange() {
        /**
         * Notify all sections that data has changed.
         */
        // Dispatch custom event for data change
        const event = new CustomEvent('dataConsistencyChange', {
            detail: { timestamp: Date.now() }
        });
        
        window.dispatchEvent(event);
        
        // Clear caches in all section managers
        if (window.musicianSongSelector && window.musicianSongSelector.clearCache) {
            window.musicianSongSelector.clearCache();
        }
        
        if (window.musicianSelector && window.musicianSelector.clearCache) {
            window.musicianSelector.clearCache();
        }
    }
    
    sleep(ms) {
        /**
         * Sleep for specified milliseconds.
         * 
         * @param {number} ms - Milliseconds to sleep
         * @returns {Promise} - Promise that resolves after delay
         */
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    getErrorStats() {
        /**
         * Get error statistics for monitoring.
         * 
         * @returns {Object} - Error statistics
         */
        return {
            errorCounts: Object.fromEntries(this.errorCounts),
            circuitBreakers: Object.fromEntries(
                Array.from(this.circuitBreakers.entries()).map(([name, breaker]) => [
                    name, 
                    { 
                        openedAt: breaker.openedAt, 
                        errorCount: breaker.errorCount,
                        isOpen: this.isCircuitBreakerOpen(name)
                    }
                ])
            ),
            lastDataHash: this.lastDataHash
        };
    }
    
    clearErrorStats() {
        /**
         * Clear all error statistics and reset circuit breakers.
         */
        this.errorCounts.clear();
        this.circuitBreakers.clear();
        console.info('Error statistics cleared');
    }
}

// Initialize global error handler
window.errorHandler = new ErrorHandler();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorHandler;
}