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
         * Execute an operation with exponential backoff retry logic.
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
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const result = await operation();
                
                // Reset error count on success
                this.errorCounts.set(operationName, 0);
                
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
                
                // Wait before retrying (except on last attempt)
                if (attempt < maxRetries) {
                    await this.sleep(delay);
                    delay *= this.backoffFactor;
                }
            }
        }
        
        console.error(`All ${maxRetries} attempts failed for ${operationName}:`, lastError);
        throw lastError;
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
         * Handle API errors with appropriate user messaging.
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