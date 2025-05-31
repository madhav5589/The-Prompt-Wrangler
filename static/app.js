// Global state
let appState = {
    config: null,
    conversations: [],
    currentExtraction: null,
    selectedConversation: null,
    viewMode: 'input'
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        // Load configuration
        appState.config = await fetchConfig();
        
        // Set up event listeners
        setupEventListeners();
        
        // Initialize UI
        initializeUI();
        
        // Load conversations
        await loadConversations();
        
        console.log('App initialized successfully');
    } catch (error) {
        console.error('Failed to initialize app:', error);
        showError('Failed to initialize application. Please refresh the page.');
    }
}

function setupEventListeners() {
    // Provider selection
    document.getElementById('providerSelect').addEventListener('change', onProviderChange);
    
    // Temperature slider
    const tempSlider = document.getElementById('temperatureSlider');
    tempSlider.addEventListener('input', function() {
        document.getElementById('tempValue').textContent = parseFloat(this.value).toFixed(2);
    });
    
    // Show conversations toggle
    document.getElementById('showConversations').addEventListener('change', onShowConversationsToggle);
    
    // New session button
    document.getElementById('newSessionBtn').addEventListener('click', onNewSession);
    
    // Extract button
    document.getElementById('extractBtn').addEventListener('click', onExtractData);
    
    // Clear button
    document.getElementById('clearBtn').addEventListener('click', onClearNote);
    
    // Close button
    document.getElementById('closeBtn').addEventListener('click', onCloseResults);
    
    // Example notes button
    document.getElementById('exampleNotesBtn').addEventListener('click', onShowExamples);
    
    // Modal close
    document.querySelector('.modal .close').addEventListener('click', function() {
        document.getElementById('exampleModal').style.display = 'none';
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('exampleModal');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Close view button
    document.getElementById('closeViewBtn').addEventListener('click', function() {
        showMainView();
    });
    
    // Clinical note input validation
    document.getElementById('clinicalNote').addEventListener('input', validateForm);
    document.getElementById('sessionName').addEventListener('input', validateForm);
    
    // Max Tokens input validation
    const maxTokensInput = document.getElementById('maxTokens');
    if (maxTokensInput) {
        maxTokensInput.addEventListener('input', function() {
            if (parseInt(this.value) < 0) {
                this.value = 0;
            }
        });
    }
}

function initializeUI() {
    // Set system prompt
    document.getElementById('systemPrompt').value = appState.config.system_prompt;
    
    // Initialize provider dropdown
    updateModelOptions();
    
    // Check initial API key status
    checkApiKeyStatus();
    
    // Initial form validation
    validateForm();
}

async function fetchConfig() {
    const response = await fetch('/api/config');
    if (!response.ok) {
        throw new Error('Failed to fetch configuration');
    }
    return await response.json();
}

async function loadConversations() {
    try {
        const response = await fetch('/api/conversations');
        if (response.ok) {
            appState.conversations = await response.json();
            updateConversationHistory();
        }
    } catch (error) {
        console.error('Failed to load conversations:', error);
    }
}

function onProviderChange() {
    updateModelOptions();
    checkApiKeyStatus();
    updateExtractButton();
}

function updateModelOptions() {
    const provider = document.getElementById('providerSelect').value;
    const modelSelect = document.getElementById('modelSelect');
    
    // Clear existing options
    modelSelect.innerHTML = '';
    
    // Add new options
    const models = appState.config.providers[provider].models;
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });
    
    updateExtractButton();
}

async function checkApiKeyStatus() {
    const provider = document.getElementById('providerSelect').value;
    const statusDiv = document.getElementById('apiKeyStatus');
    
    try {
        const response = await fetch('/api/check-api-key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ provider })
        });
        
        const result = await response.json();
        
        if (result.has_key) {
            statusDiv.className = 'api-status success';
            statusDiv.textContent = `✅ ${provider} API key configured`;
        } else {
            statusDiv.className = 'api-status error';
            statusDiv.textContent = `❌ ${provider} API key missing`;
            // const infoDiv = document.createElement('div');
            // infoDiv.className = 'api-status info';
            // infoDiv.textContent = `Add ${result.env_key} to your .env file`;
            // statusDiv.appendChild(infoDiv);
        }
    } catch (error) {
        statusDiv.className = 'api-status error';
        statusDiv.textContent = 'Error checking API key status';
    }
    
    validateForm();
}

function onShowConversationsToggle() {
    const checked = document.getElementById('showConversations').checked;
    const historyDiv = document.getElementById('conversationHistory');
    historyDiv.style.display = checked ? 'block' : 'none';
    
    if (checked) {
        updateConversationHistory();
    }
}

function updateConversationHistory() {
    const listDiv = document.getElementById('conversationList');
    listDiv.innerHTML = '';
    
    if (appState.conversations.length === 0) {
        listDiv.innerHTML = '<p style="color: #6b7280; font-size: 0.875rem;">No conversations yet</p>';
        return;
    }
    
    // Show last 10 conversations in reverse order
    const recentConversations = appState.conversations.slice(-10).reverse();
    
    recentConversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'conversation-item';
        item.textContent = `${conv.project_name}`;
        item.addEventListener('click', () => showConversation(conv));
        listDiv.appendChild(item);
    });
}

function showConversation(conversation) {
    appState.selectedConversation = conversation;
    appState.viewMode = 'view';
    
    // Populate conversation view
    document.getElementById('viewSessionName').value = conversation.project_name;
    
    // Format timestamp
    const timestamp = new Date(conversation.timestamp);
    const formattedTime = timestamp.toLocaleString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    // Update metrics
    document.getElementById('viewMetricProvider').textContent = `${conversation.provider} ${conversation.model}`;
    document.getElementById('viewMetricTime').textContent = formattedTime;
    document.getElementById('viewMetricResponseTime').textContent = `${conversation.response_time.toFixed(2)}s`;
    
    const usage = conversation.token_usage;
    const totalTokens = usage.total_tokens || (usage.input_tokens || 0) + (usage.output_tokens || 0);
    document.getElementById('viewMetricTokens').textContent = totalTokens || 'N/A';
    
    // Display structured data
    displayStructuredData(conversation.structured_data, 'view');
    
    // Show conversation view
    showConversationView();
}

async function onNewSession() {
    try {
        const response = await fetch('/api/session', {
            method: 'POST'
        });
        
        if (response.ok) {
            // Clear form
            document.getElementById('sessionName').value = 'Clinical Data Extraction';
            document.getElementById('clinicalNote').value = '';
            
            // Hide results
            hideResults();
            
            // Reset state
            appState.currentExtraction = null;
            appState.selectedConversation = null;
            appState.viewMode = 'input';
            
            // Show main view
            showMainView();
            
            // Reload conversations
            await loadConversations();
        }
    } catch (error) {
        console.error('Failed to start new session:', error);
        showError('Failed to start new session');
    }
}

async function onExtractData() {
    const provider = document.getElementById('providerSelect').value;
    const model = document.getElementById('modelSelect').value;
    const clinicalNote = document.getElementById('clinicalNote').value;
    const projectName = document.getElementById('sessionName').value;
    const temperature = parseFloat(document.getElementById('temperatureSlider').value);
    const maxTokens = parseInt(document.getElementById('maxTokens').value);
    
    // Show loading
    showLoading(provider);
    hideError();
    
    try {
        const response = await fetch('/api/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                provider,
                model,
                clinical_note: clinicalNote,
                project_name: projectName,
                temperature,
                max_tokens: maxTokens
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Extraction failed');
        }
        
        // Store current extraction
        appState.currentExtraction = result;
        
        // Display results
        displayExtractionResults(result);
        
        // Show close button instead of clear button
        document.getElementById('clearBtn').style.display = 'none';
        document.getElementById('closeBtn').style.display = 'inline-block';
        
        // Show success message
        showSuccess('Extraction completed and saved!');
        
        // Reload conversations
        await loadConversations();
        
        // Enable show conversations
        document.getElementById('showConversations').checked = true;
        onShowConversationsToggle();
        
    } catch (error) {
        console.error('Extraction failed:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function showLoading(provider) {
    document.getElementById('loadingProvider').textContent = provider;
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('extractBtn').disabled = true;
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
    validateForm(); // Re-enable extract button if form is valid
}

function displayExtractionResults(result) {
    // Update metrics
    const timestamp = new Date(result.timestamp);
    const formattedTime = timestamp.toLocaleString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    document.getElementById('metricProvider').textContent = `${result.provider} ${result.model}`;
    document.getElementById('metricTime').textContent = formattedTime;
    document.getElementById('metricResponseTime').textContent = `${result.elapsed.toFixed(2)}s`;
    
    const usage = result.usage;
    const totalTokens = usage.total_tokens || (usage.input_tokens || 0) + (usage.output_tokens || 0);
    document.getElementById('metricTokens').textContent = totalTokens || 'N/A';
    
    // Display structured data
    displayStructuredData(result.structured_data, 'main');
    
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
}

function displayStructuredData(data, prefix) {
    const fieldsContainer = document.getElementById(prefix === 'main' ? 'extractedFields' : 'viewExtractedFields');
    const jsonContainer = document.getElementById(prefix === 'main' ? 'rawJson' : 'viewRawJson');
    
    // Clear existing content
    fieldsContainer.innerHTML = '';
    
    if (data.raw_response) {
        // Show raw response if JSON parsing failed
        fieldsContainer.innerHTML = '<div class="error-display">Could not parse as JSON. Check raw response below.</div>';
        jsonContainer.textContent = data.raw_response;
        return;
    }
    
    // Display extracted fields
    Object.entries(data).forEach(([key, value]) => {
        const fieldGroup = document.createElement('div');
        fieldGroup.className = 'field-group';
        
        const label = document.createElement('div');
        label.className = 'field-label';
        label.textContent = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'field-value';
        input.readOnly = true;
        
        if (Array.isArray(value)) {
            input.value = value.join(', ');
        } else {
            input.value = String(value);
        }
        
        fieldGroup.appendChild(label);
        fieldGroup.appendChild(input);
        fieldsContainer.appendChild(fieldGroup);
    });
    
    // Display raw JSON
    jsonContainer.textContent = JSON.stringify(data, null, 2);
}

function onClearNote() {
    document.getElementById('clinicalNote').value = '';
    validateForm();
}

function onCloseResults() {
    hideResults();
    appState.currentExtraction = null;
    
    // Show clear button instead of close button
    document.getElementById('closeBtn').style.display = 'none';
    document.getElementById('clearBtn').style.display = 'inline-block';
}

function hideResults() {
    document.getElementById('resultsSection').style.display = 'none';
    hideError();
    hideSuccess();
}

async function onShowExamples() {
    try {
        const response = await fetch('/api/examples');
        const examples = await response.json();
        
        const listDiv = document.getElementById('exampleList');
        listDiv.innerHTML = '';
        
        examples.forEach(example => {
            const item = document.createElement('div');
            item.className = 'example-item';
            
            const title = document.createElement('h4');
            title.textContent = example.name;
            
            const preview = document.createElement('p');
            preview.textContent = example.content.substring(0, 100) + '...';
            preview.style.color = '#6b7280';
            preview.style.fontSize = '0.875rem';
            
            item.appendChild(title);
            item.appendChild(preview);
            
            item.addEventListener('click', () => {
                document.getElementById('clinicalNote').value = example.content;
                document.getElementById('exampleModal').style.display = 'none';
                validateForm();
            });
            
            listDiv.appendChild(item);
        });
        
        document.getElementById('exampleModal').style.display = 'block';
        
    } catch (error) {
        console.error('Failed to load examples:', error);
        showError('Failed to load example notes');
    }
}

function validateForm() {
    const clinicalNote = document.getElementById('clinicalNote').value.trim();
    const extractBtn = document.getElementById('extractBtn');
    const provider = document.getElementById('providerSelect').value;
    
    // Check if we have API key
    const apiStatus = document.getElementById('apiKeyStatus');
    const hasApiKey = apiStatus.classList.contains('success');
    
    // Enable extract button if we have text and API key
    const canExtract = clinicalNote.length > 0 && hasApiKey;
    extractBtn.disabled = !canExtract;
}

function updateExtractButton() {
    const provider = document.getElementById('providerSelect').value;
    const extractBtn = document.getElementById('extractBtn');
    extractBtn.textContent = `🚀 Extract Data with ${provider}`;
}

function showMainView() {
    document.getElementById('mainView').style.display = 'block';
    document.getElementById('conversationView').style.display = 'none';
    appState.viewMode = 'input';
}

function showConversationView() {
    document.getElementById('mainView').style.display = 'none';
    document.getElementById('conversationView').style.display = 'block';
    appState.viewMode = 'view';
}

function showError(message) {
    const errorDiv = document.getElementById('errorDisplay');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function hideError() {
    document.getElementById('errorDisplay').style.display = 'none';
}

function showSuccess(message) {
    // Create success message if it doesn't exist
    let successDiv = document.getElementById('successMessage');
    if (!successDiv) {
        successDiv = document.createElement('div');
        successDiv.id = 'successMessage';
        successDiv.className = 'success-message';
        document.getElementById('resultsSection').parentNode.insertBefore(successDiv, document.getElementById('resultsSection'));
    }
    
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(hideSuccess, 5000);
}

function hideSuccess() {
    const successDiv = document.getElementById('successMessage');
    if (successDiv) {
        successDiv.style.display = 'none';
    }
}