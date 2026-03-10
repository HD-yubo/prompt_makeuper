/**
 * prompt makeuper Chrome Extension - Side Panel
 * Side panel version with persistent display and no health checks
 */

// API Configuration - Read from manifest.json, fallback to localhost
const manifest = chrome.runtime.getManifest();
const API_BASE_URL = manifest.api_base_url || 'http://localhost:8000';
const MAKEUP_REQUEST_TIMEOUT_MS = 90000;
const ENDPOINTS = {
    MAKEUP: `${API_BASE_URL}/makeup_prompt`
};
const PENDING_AUTO_OPTIMIZE_KEY = 'pendingAutoOptimize';

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
    btnSpinner: null,
    formatSelector: null,
    formatInputs: null
};

// Application State
const state = {
    isLoading: false,
    inputValue: '',
    outputType: 'markdown',
    latestRequestToken: 0,
    lastHandledAutoOptimizeId: null,
    autoOptimizeTimerId: null
};

function getPendingStorageArea() {
    return chrome.storage.session || chrome.storage.local;
}

function getPendingStorageAreaName() {
    return chrome.storage.session ? 'session' : 'local';
}

/**
 * Initialize the application
 */
function init() {
    // Cache DOM elements
    cacheElements();

    // Load saved output type preference
    loadOutputTypePreference();

    // Attach event listeners
    attachEventListeners();

    // Handle auto-optimize requests persisted by the background worker
    chrome.storage.onChanged.addListener(handleStorageChange);
    consumePendingAutoOptimize().catch((error) => {
        console.error('Failed to consume pending auto-optimize request:', error);
    });

    // Focus on input field
    elements.inputPrompt.focus();
}

/**
 * Handle storage changes from the background worker.
 */
function handleStorageChange(changes, areaName) {
    if (areaName !== getPendingStorageAreaName()) {
        return;
    }

    const change = changes[PENDING_AUTO_OPTIMIZE_KEY];
    if (!change || !change.newValue) {
        return;
    }

    processAutoOptimizeRequest(change.newValue);
}

async function consumePendingAutoOptimize() {
    const storageArea = getPendingStorageArea();
    const result = await storageArea.get(PENDING_AUTO_OPTIMIZE_KEY);
    const pendingRequest = result[PENDING_AUTO_OPTIMIZE_KEY];

    if (!pendingRequest) {
        return;
    }

    processAutoOptimizeRequest(pendingRequest);
}

async function clearPendingAutoOptimize() {
    const storageArea = getPendingStorageArea();
    await storageArea.remove(PENDING_AUTO_OPTIMIZE_KEY);
}

function scheduleAutoOptimize() {
    if (state.autoOptimizeTimerId) {
        clearTimeout(state.autoOptimizeTimerId);
    }

    state.autoOptimizeTimerId = setTimeout(() => {
        state.autoOptimizeTimerId = null;
        optimizePrompt();
    }, 0);
}

function processAutoOptimizeRequest(request) {
    if (!request || !request.prompt || !request.requestId) {
        return;
    }

    if (request.requestId === state.lastHandledAutoOptimizeId) {
        return;
    }

    state.lastHandledAutoOptimizeId = request.requestId;
    elements.inputPrompt.value = request.prompt;
    handleInputChange();
    clearPendingAutoOptimize().catch((error) => {
        console.error('Failed to clear pending auto-optimize request:', error);
    });
    scheduleAutoOptimize();
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
    elements.formatSelector = document.getElementById('formatSelector');
    elements.formatInputs = elements.formatSelector.querySelectorAll('input[type="radio"]');
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

    // Output format change listeners
    elements.formatInputs.forEach(input => {
        input.addEventListener('change', handleFormatChange);
    });

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
 * Handle output format selection changes
 */
function handleFormatChange(e) {
    state.outputType = e.target.value;
    localStorage.setItem('outputType', state.outputType);
}

/**
 * Load saved output type preference from localStorage
 */
function loadOutputTypePreference() {
    const savedType = localStorage.getItem('outputType');
    if (savedType && (savedType === 'markdown' || savedType === 'xml')) {
        state.outputType = savedType;
        // Update radio buttons to match saved preference
        elements.formatInputs.forEach(input => {
            input.checked = (input.value === savedType);
        });
    }
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
    const requestToken = ++state.latestRequestToken;

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
            body: JSON.stringify({
                input_prompt: inputPrompt,
                output_type: state.outputType
            }),
            timeout: MAKEUP_REQUEST_TIMEOUT_MS
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();

        if (requestToken !== state.latestRequestToken) {
            return;
        }

        // Update UI with results
        elements.outputPrompt.value = data.output_prompt || 'No output received';
        showMetadata(data.skill_used, data.iterations);

        // Show format-specific success message
        const formatLabel = state.outputType === 'xml' ? 'XML' : 'Markdown';
        showMessage(`Prompt optimized successfully (${formatLabel} format)!`, 'success');

    } catch (error) {
        if (requestToken !== state.latestRequestToken) {
            return;
        }

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
        if (requestToken === state.latestRequestToken) {
            setLoading(false);
        }
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
