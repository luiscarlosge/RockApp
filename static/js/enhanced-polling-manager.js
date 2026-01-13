/**
 * Enhanced Polling Manager for Real-Time Refresh System
 * Implements 5-second refresh intervals with countdown timer and error handling
 * 
 * Requirements addressed:
 * - 2.1: Reduce refresh interval from 30 seconds to 5 seconds
 * - 2.2: Add countdown timer component showing time until next refresh
 * - 2.3: Add error handling with automatic retry
 * - 2.4: Implement loading indicators during refresh
 * - 2.5: Update display immediately without page reload
 */

class EnhancedPollingManager {
    constructor(endpoint, options = {}) {
        this.endpoint = endpoint;
        this.interval = options.interval || 5000; // 5 seconds (Requirements 2.1)
        this.maxRetries = options.maxRetries || 3;
        this.retryDelay = options.retryDelay || 1000;
        
        // State management
        this.isPolling = false;
        this.isPaused = false;
        this.currentRetryCount = 0;
        this.lastSuccessfulFetch = null;
        this.consecutiveErrors = 0;
        
        // Timer management
        this.pollingTimer = null;
        this.countdownTimer = null;
        this.remainingTime = this.interval / 1000; // Convert to seconds
        
        // DOM elements for UI feedback
        this.countdownElement = null;
        this.loadingElement = null;
        this.errorElement = null;
        
        // Callbacks
        this.onDataReceived = options.onDataReceived || (() => {});
        this.onError = options.onError || (() => {});
        this.onCountdownUpdate = options.onCountdownUpdate || (() => {});
        this.onLoadingStateChange = options.onLoadingStateChange || (() => {});
        
        // Initialize UI elements
        this.initializeUI();
        
        // Bind methods to preserve context
        this.poll = this.poll.bind(this);
        this.updateCountdown = this.updateCountdown.bind(this);
        this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
        
        // Handle page visibility changes to pause/resume polling
        document.addEventListener('visibilitychange', this.handleVisibilityChange);
    }
    
    /**
     * Initialize UI elements for countdown timer and loading indicators
     * Requirements 2.2, 2.4
     */
    initializeUI() {
        // Create countdown timer element if it doesn't exist
        this.countdownElement = document.getElementById('refresh-countdown');
        if (!this.countdownElement) {
            this.countdownElement = document.createElement('div');
            this.countdownElement.id = 'refresh-countdown';
            this.countdownElement.className = 'refresh-countdown';
            this.countdownElement.setAttribute('aria-live', 'polite');
            this.countdownElement.setAttribute('aria-label', 'Tiempo hasta próxima actualización');
            
            // Add to live performance section if it exists
            const liveSection = document.getElementById('live-performance');
            if (liveSection) {
                liveSection.appendChild(this.countdownElement);
            } else {
                document.body.appendChild(this.countdownElement);
            }
        }
        
        // Create loading indicator element if it doesn't exist
        this.loadingElement = document.getElementById('refresh-loading');
        if (!this.loadingElement) {
            this.loadingElement = document.createElement('div');
            this.loadingElement.id = 'refresh-loading';
            this.loadingElement.className = 'refresh-loading d-none';
            this.loadingElement.setAttribute('role', 'status');
            this.loadingElement.setAttribute('aria-live', 'polite');
            this.loadingElement.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Actualizando...</span>
                    </div>
                    <span>Actualizando datos...</span>
                </div>
            `;
            
            // Add to live performance section if it exists
            const liveSection = document.getElementById('live-performance');
            if (liveSection) {
                liveSection.appendChild(this.loadingElement);
            } else {
                document.body.appendChild(this.loadingElement);
            }
        }
        
        // Create error display element if it doesn't exist
        this.errorElement = document.getElementById('refresh-error');
        if (!this.errorElement) {
            this.errorElement = document.createElement('div');
            this.errorElement.id = 'refresh-error';
            this.errorElement.className = 'refresh-error alert alert-warning d-none';
            this.errorElement.setAttribute('role', 'alert');
            this.errorElement.setAttribute('aria-live', 'assertive');
            
            // Add to live performance section if it exists
            const liveSection = document.getElementById('live-performance');
            if (liveSection) {
                liveSection.appendChild(this.errorElement);
            } else {
                document.body.appendChild(this.errorElement);
            }
        }
    }
    
    /**
     * Start the polling process
     * Requirements 2.1, 2.2
     */
    startPolling() {
        if (this.isPolling) {
            return;
        }
        
        this.isPolling = true;
        this.isPaused = false;
        this.remainingTime = this.interval / 1000;
        
        // Start with immediate poll
        this.poll();
        
        // Start countdown timer
        this.startCountdown();
        
        console.log(`Enhanced polling started with ${this.interval}ms interval`);
    }
    
    /**
     * Stop the polling process
     */
    stopPolling() {
        this.isPolling = false;
        this.isPaused = false;
        
        if (this.pollingTimer) {
            clearTimeout(this.pollingTimer);
            this.pollingTimer = null;
        }
        
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
            this.countdownTimer = null;
        }
        
        this.hideLoadingIndicator();
        this.hideError();
        this.updateCountdownDisplay(0);
        
        console.log('Enhanced polling stopped');
    }
    
    /**
     * Pause polling (useful when page is not visible)
     */
    pausePolling() {
        if (!this.isPolling || this.isPaused) {
            return;
        }
        
        this.isPaused = true;
        
        if (this.pollingTimer) {
            clearTimeout(this.pollingTimer);
            this.pollingTimer = null;
        }
        
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
            this.countdownTimer = null;
        }
        
        console.log('Enhanced polling paused');
    }
    
    /**
     * Resume polling after pause
     */
    resumePolling() {
        if (!this.isPolling || !this.isPaused) {
            return;
        }
        
        this.isPaused = false;
        this.remainingTime = this.interval / 1000;
        
        // Resume with immediate poll
        this.poll();
        this.startCountdown();
        
        console.log('Enhanced polling resumed');
    }
    
    /**
     * Start the countdown timer
     * Requirements 2.2, 2.5
     */
    startCountdown() {
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
        }
        
        this.countdownTimer = setInterval(() => {
            if (this.isPaused) {
                return;
            }
            
            this.remainingTime--;
            this.updateCountdownDisplay(this.remainingTime);
            this.onCountdownUpdate(this.remainingTime);
            
            if (this.remainingTime <= 0) {
                this.remainingTime = this.interval / 1000;
            }
        }, 1000);
    }
    
    /**
     * Update countdown display in the UI
     * Requirements 2.2, 2.5
     */
    updateCountdownDisplay(seconds) {
        if (!this.countdownElement) {
            return;
        }
        
        if (seconds <= 0) {
            this.countdownElement.innerHTML = `
                <div class="countdown-display">
                    <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>
                    <span>Actualizando...</span>
                </div>
            `;
        } else {
            this.countdownElement.innerHTML = `
                <div class="countdown-display">
                    <i class="bi bi-clock me-1" aria-hidden="true"></i>
                    <span>Próxima actualización en <strong>${seconds}s</strong></span>
                </div>
            `;
        }
        
        // Update aria-label for screen readers
        this.countdownElement.setAttribute('aria-label', 
            seconds <= 0 ? 'Actualizando datos' : `Próxima actualización en ${seconds} segundos`
        );
    }
    
    /**
     * Perform the actual polling request
     * Requirements 2.1, 2.3, 2.4, 2.5
     */
    async poll() {
        if (!this.isPolling || this.isPaused) {
            return;
        }
        
        try {
            // Show loading indicator (Requirements 2.4)
            this.showLoadingIndicator();
            this.hideError();
            
            // Make the fetch request
            const response = await fetch(this.endpoint, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Success - reset error counters
            this.currentRetryCount = 0;
            this.consecutiveErrors = 0;
            this.lastSuccessfulFetch = Date.now();
            
            // Hide loading indicator
            this.hideLoadingIndicator();
            
            // Call success callback (Requirements 2.5)
            this.onDataReceived(data);
            
            // Schedule next poll (Requirements 2.1)
            this.scheduleNextPoll();
            
        } catch (error) {
            console.error('Polling error:', error);
            
            // Hide loading indicator
            this.hideLoadingIndicator();
            
            // Handle error with retry logic (Requirements 2.3)
            await this.handleError(error);
        }
    }
    
    /**
     * Handle errors with automatic retry logic
     * Requirements 2.3
     */
    async handleError(error) {
        this.consecutiveErrors++;
        this.currentRetryCount++;
        
        // Show error message
        this.showError(error.message, this.currentRetryCount, this.maxRetries);
        
        // Call error callback
        this.onError(error, this.currentRetryCount);
        
        if (this.currentRetryCount < this.maxRetries) {
            // Retry with exponential backoff
            const retryDelay = this.retryDelay * Math.pow(2, this.currentRetryCount - 1);
            
            console.log(`Retrying in ${retryDelay}ms (attempt ${this.currentRetryCount}/${this.maxRetries})`);
            
            setTimeout(() => {
                if (this.isPolling && !this.isPaused) {
                    this.poll();
                }
            }, retryDelay);
        } else {
            // Max retries reached, schedule next regular poll
            console.log('Max retries reached, scheduling next regular poll');
            this.currentRetryCount = 0;
            this.scheduleNextPoll();
        }
    }
    
    /**
     * Schedule the next polling attempt
     * Requirements 2.1
     */
    scheduleNextPoll() {
        if (!this.isPolling || this.isPaused) {
            return;
        }
        
        this.pollingTimer = setTimeout(() => {
            this.poll();
        }, this.interval);
    }
    
    /**
     * Show loading indicator
     * Requirements 2.4
     */
    showLoadingIndicator() {
        if (this.loadingElement) {
            this.loadingElement.classList.remove('d-none');
        }
        this.onLoadingStateChange(true);
    }
    
    /**
     * Hide loading indicator
     * Requirements 2.4
     */
    hideLoadingIndicator() {
        if (this.loadingElement) {
            this.loadingElement.classList.add('d-none');
        }
        this.onLoadingStateChange(false);
    }
    
    /**
     * Show error message
     * Requirements 2.3
     */
    showError(message, retryCount = 0, maxRetries = 0) {
        if (!this.errorElement) {
            return;
        }
        
        let errorHtml = `
            <div class="d-flex align-items-center">
                <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>
                <div>
                    <strong>Error de conexión:</strong> ${message}
        `;
        
        if (retryCount > 0 && retryCount < maxRetries) {
            errorHtml += `<br><small>Reintentando... (${retryCount}/${maxRetries})</small>`;
        } else if (retryCount >= maxRetries) {
            errorHtml += `<br><small>Se reintentará en la próxima actualización programada.</small>`;
        }
        
        errorHtml += `
                </div>
            </div>
        `;
        
        this.errorElement.innerHTML = errorHtml;
        this.errorElement.classList.remove('d-none');
        
        // Auto-hide error after 10 seconds if no more errors
        setTimeout(() => {
            if (this.consecutiveErrors === 0) {
                this.hideError();
            }
        }, 10000);
    }
    
    /**
     * Hide error message
     */
    hideError() {
        if (this.errorElement) {
            this.errorElement.classList.add('d-none');
        }
    }
    
    /**
     * Handle page visibility changes to optimize polling
     */
    handleVisibilityChange() {
        if (document.hidden) {
            this.pausePolling();
        } else {
            this.resumePolling();
        }
    }
    
    /**
     * Get current polling status
     */
    getStatus() {
        return {
            isPolling: this.isPolling,
            isPaused: this.isPaused,
            remainingTime: this.remainingTime,
            consecutiveErrors: this.consecutiveErrors,
            lastSuccessfulFetch: this.lastSuccessfulFetch,
            interval: this.interval
        };
    }
    
    /**
     * Update polling interval
     * Requirements 2.1
     */
    setInterval(newInterval) {
        const wasPolling = this.isPolling;
        
        if (wasPolling) {
            this.stopPolling();
        }
        
        this.interval = newInterval;
        this.remainingTime = newInterval / 1000;
        
        if (wasPolling) {
            this.startPolling();
        }
        
        console.log(`Polling interval updated to ${newInterval}ms`);
    }
    
    /**
     * Force an immediate poll
     */
    forcePoll() {
        if (!this.isPolling) {
            return;
        }
        
        // Reset countdown
        this.remainingTime = this.interval / 1000;
        this.updateCountdownDisplay(this.remainingTime);
        
        // Cancel current timer and poll immediately
        if (this.pollingTimer) {
            clearTimeout(this.pollingTimer);
            this.pollingTimer = null;
        }
        
        this.poll();
    }
    
    /**
     * Cleanup method
     */
    destroy() {
        this.stopPolling();
        
        // Remove event listeners
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
        
        // Remove UI elements
        if (this.countdownElement && this.countdownElement.parentNode) {
            this.countdownElement.parentNode.removeChild(this.countdownElement);
        }
        if (this.loadingElement && this.loadingElement.parentNode) {
            this.loadingElement.parentNode.removeChild(this.loadingElement);
        }
        if (this.errorElement && this.errorElement.parentNode) {
            this.errorElement.parentNode.removeChild(this.errorElement);
        }
        
        console.log('Enhanced polling manager destroyed');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedPollingManager;
} else {
    window.EnhancedPollingManager = EnhancedPollingManager;
}