/**
 * Prompt Makeover Chrome Extension - Side Panel
 * Side panel version with persistent display and no health checks
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const ENDPOINTS = {
    MAKEUP: `${API_BASE_URL}/makeup_prompt`
};

// DOM Elements
const elements = {
    inputPrompt: null,
    outputPrompt: null,
    optimizeBtn: null,
    clearBtn: null,
    copyBtn: null,
    messageArea: null,
    metadataSection: null,
    skillUsed: null,
    iterations: null,
    btnText: null,
    btnSpinner: null
};

// Application State
const state = {
    isLoading: false,
    inputValue: ''
};

/**
 * Initialize the application
 */
function init() {
    // Cache DOM elements
    cacheElements();

    // Attach event listeners
    attachEventListeners();

    // Listen for messages from background script
    chrome.runtime.onMessage.addListener(handleBackgroundMessage);

    // Focus on input field
    elements.inputPrompt.focus();
}

/**
 * Handle messages from background script
 */
function handleBackgroundMessage(message, sender, sendResponse) {
    if (message.action === 'autoOptimize' && message.prompt) {
        // Fill the input with the selected text
        elements.inputPrompt.value = message.prompt;
        handleInputChange();

        // Auto-trigger optimization
        setTimeout(() => {
            optimizePrompt();
        }, 300);
    }
}

/**
 * Cache all DOM elements for better performance
 */
function cacheElements() {
    elements.inputPrompt = document.getElementById('inputPrompt');
    elements.outputPrompt = document.getElementById('outputPrompt');
    elements.optimizeBtn = document.getElementById('optimizeBtn');
    elements.clearBtn = document.getElementById('clearBtn');
    elements.copyBtn = document.getElementById('copyBtn');
    elements.messageArea = document.getElementById('messageArea');
    elements.metadataSection = document.getElementById('metadataSection');
    elements.skillUsed = document.getElementById('skillUsed');
    elements.iterations = document.getElementById('iterations');
    elements.btnText = elements.optimizeBtn.querySelector('.btn-text');
    elements.btnSpinner = elements.optimizeBtn.querySelector('.btn-spinner');
}

/**
 * Attach all event listeners
 */
function attachEventListeners() {
    // Input change handler for validation
    elements.inputPrompt.addEventListener('input', handleInputChange);

    // Optimize button click
    elements.optimizeBtn.addEventListener('click', optimizePrompt);

    // Clear button click
    elements.clearBtn.addEventListener('click', clearAll);

    // Copy button click
    elements.copyBtn.addEventListener('click', copyToClipboard);

    // Keyboard shortcut: Ctrl/Cmd + Enter to optimize
    elements.inputPrompt.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (!elements.optimizeBtn.disabled) {
                optimizePrompt();
            }
        }
    });
}

/**
 * Handle input changes for validation
 */
function handleInputChange() {
    state.inputValue = elements.inputPrompt.value.trim();
    elements.optimizeBtn.disabled = state.inputValue === '' || state.isLoading;
}

/**
 * Fetch with timeout wrapper
 */
async function fetchWithTimeout(url, options = {}) {
    const { timeout = 30000 } = options;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error('Request timeout. Server may be slow or unresponsive.');
        }
        throw error;
    }
}

/**
 * Optimize the user's prompt
 */
async function optimizePrompt() {
    const inputPrompt = elements.inputPrompt.value.trim();

    if (!inputPrompt) {
        showMessage('Please enter a prompt to optimize.', 'error');
        return;
    }

    setLoading(true);
    hideMessage();
    hideMetadata();

    try {
        const response = await fetchWithTimeout(ENDPOINTS.MAKEUP, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input_prompt: inputPrompt }),
            timeout: 60000 // 60 second timeout for optimization
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();

        // Update UI with results
        elements.outputPrompt.value = data.output_prompt || 'No output received';
        showMetadata(data.skill_used, data.iterations);
        showMessage('Prompt optimized successfully!', 'success');

    } catch (error) {
        console.error('Optimization error:', error);
        let errorMessage = 'Failed to optimize prompt.';

        if (error.message.includes('timeout')) {
            errorMessage = 'Request timeout. The optimization took too long.';
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage = 'Network error. Please check if the server is running at http://localhost:8000';
        } else if (error.message) {
            errorMessage = error.message;
        }

        showMessage(errorMessage, 'error');
        elements.outputPrompt.value = '';
    } finally {
        setLoading(false);
    }
}

/**
 * Copy the output to clipboard
 */
async function copyToClipboard() {
    const outputText = elements.outputPrompt.value;

    if (!outputText) {
        showMessage('Nothing to copy.', 'warning');
        return;
    }

    try {
        await navigator.clipboard.writeText(outputText);

        // Visual feedback
        const originalText = elements.copyBtn.querySelector('.copy-text').textContent;
        elements.copyBtn.querySelector('.copy-text').textContent = 'Copied!';
        elements.copyBtn.classList.add('copied');

        setTimeout(() => {
            elements.copyBtn.querySelector('.copy-text').textContent = originalText;
            elements.copyBtn.classList.remove('copied');
        }, 2000);

        showMessage('Copied to clipboard!', 'success');
    } catch (error) {
        console.error('Copy error:', error);
        showMessage('Failed to copy to clipboard.', 'error');
    }
}

/**
 * Clear all input and output
 */
function clearAll() {
    elements.inputPrompt.value = '';
    elements.outputPrompt.value = '';
    hideMessage();
    hideMetadata();
    handleInputChange();
    elements.inputPrompt.focus();
}

/**
 * Set loading state
 */
function setLoading(loading) {
    state.isLoading = loading;

    if (loading) {
        elements.optimizeBtn.disabled = true;
        elements.btnText.classList.add('hidden');
        elements.btnSpinner.classList.remove('hidden');
    } else {
        elements.optimizeBtn.disabled = state.inputValue === '';
        elements.btnText.classList.remove('hidden');
        elements.btnSpinner.classList.add('hidden');
    }
}

/**
 * Show a message to the user
 */
function showMessage(message, type = 'info') {
    elements.messageArea.textContent = message;
    elements.messageArea.className = 'message-area';

    if (type === 'success') {
        elements.messageArea.classList.add('message-success');
    } else if (type === 'error') {
        elements.messageArea.classList.add('message-error');
    } else if (type === 'warning') {
        elements.messageArea.classList.add('message-warning');
    } else {
        elements.messageArea.classList.add('message-info');
    }

    elements.messageArea.classList.remove('hidden');

    // Auto-hide success and info messages after 5 seconds
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            hideMessage();
        }, 5000);
    }
}

/**
 * Hide the message area
 */
function hideMessage() {
    elements.messageArea.classList.add('hidden');
}

/**
 * Show metadata section
 */
function showMetadata(skillUsed, iterations) {
    elements.skillUsed.textContent = skillUsed || 'Unknown';
    elements.iterations.textContent = iterations !== undefined ? iterations : '-';
    elements.metadataSection.classList.remove('hidden');
}

/**
 * Hide metadata section
 */
function hideMetadata() {
    elements.metadataSection.classList.add('hidden');
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', init);
