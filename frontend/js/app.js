class ChatApp {
    constructor() {
        // DOM Elements
        this.chatContainer = document.getElementById('chat-container');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.connectionStatus = document.getElementById('connection-status');
        this.loadingOverlay = document.getElementById('loading-overlay');

        // WebSocket connection
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;

        // Initialize
        this.setupEventListeners();
        this.connectWebSocket();
    }

    setupEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Send message on Enter key
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Focus input on load
        this.messageInput.focus();
    }

    connectWebSocket() {
        this.showLoading(true);
        this.updateConnectionStatus('connecting');

        // Create WebSocket connection
        const wsUrl = `ws://${window.location.host}/ws/chat`;
        console.log('Connecting to WebSocket:', wsUrl);
        
        this.ws = new WebSocket(wsUrl);

        // WebSocket event handlers
        this.ws.onopen = () => {
            console.log('WebSocket connection established');
            this.showLoading(false);
            this.updateConnectionStatus('connected');
            this.reconnectAttempts = 0;
            this.enableInterface();
        };

        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
            this.updateConnectionStatus('disconnected');
            this.disableInterface();
            this.handleReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showError('Connection error. Please try again later.');
        };

        this.ws.onmessage = (event) => {
            console.log('Received message:', event.data);
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'error') {
                    this.showError(data.content);
                } else {
                    this.addMessage('ai', data.content);
                }
            } catch (error) {
                console.error('Message parsing error:', error);
                this.showError('Error processing message');
            }
        };
    }

    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
            console.log(`Attempting to reconnect in ${delay}ms...`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, delay);
        } else {
            this.showError('Unable to connect. Please refresh the page.');
        }
    }

    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Clear input and disable interface
        this.messageInput.value = '';
        this.disableInterface();

        // Add user message to chat
        this.addMessage('user', message);

        // Send message through WebSocket
        try {
            const data = JSON.stringify({
                type: 'message',
                content: message
            });
            console.log('Sending message:', data);
            this.ws.send(data);
        } catch (error) {
            console.error('Send error:', error);
            this.showError('Failed to send message');
            this.enableInterface();
        }
    }

    addMessage(type, content) {
        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        this.chatContainer.appendChild(messageDiv);

        // Scroll to bottom
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;

        // Enable interface after AI response
        if (type === 'ai') {
            this.enableInterface();
        }
    }

    showError(message) {
        console.error('Error:', message);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message error-message';
        errorDiv.textContent = message;
        this.chatContainer.appendChild(errorDiv);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    updateConnectionStatus(status) {
        this.connectionStatus.className = status;
        switch (status) {
            case 'connecting':
                this.connectionStatus.textContent = 'Connecting...';
                break;
            case 'connected':
                this.connectionStatus.textContent = 'Connected';
                break;
            case 'disconnected':
                this.connectionStatus.textContent = 'Disconnected - Attempting to reconnect...';
                break;
        }
    }

    enableInterface() {
        this.messageInput.disabled = false;
        this.sendButton.disabled = false;
        this.messageInput.focus();
    }

    disableInterface() {
        this.messageInput.disabled = true;
        this.sendButton.disabled = true;
    }

    showLoading(show) {
        this.loadingOverlay.className = show ? '' : 'hidden';
    }
}

// Initialize chat application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
});
