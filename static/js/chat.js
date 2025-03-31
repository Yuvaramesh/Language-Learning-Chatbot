document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('message-form');
    const userInput = document.getElementById('user-input');
    const chatContainer = document.getElementById('chat-container');
    
    // Scroll to bottom of chat
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Add message to chat
    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerText = content;
        
        messageDiv.appendChild(messageContent);
        chatContainer.appendChild(messageDiv);
        
        // Clear any loading indicators
        document.querySelectorAll('.loading-message').forEach(el => el.remove());
        
        scrollToBottom();
    }
    
    // Add loading indicator
    function addLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant-message loading-message';
        
        const loadingContent = document.createElement('div');
        loadingContent.className = 'message-content';
        
        const loadingDots = document.createElement('span');
        loadingDots.className = 'loading-dots';
        loadingDots.innerText = 'Thinking';
        
        loadingContent.appendChild(loadingDots);
        loadingDiv.appendChild(loadingContent);
        chatContainer.appendChild(loadingDiv);
        
        scrollToBottom();
    }
    
    // Handle form submission
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, true);
        
        // Clear input
        userInput.value = '';
        
        // Show loading indicator
        addLoadingIndicator();
        
        // Send message to server
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Add assistant response to chat
            addMessage(data.response, false);
            
            // Process corrections if any
            if (data.corrections && data.corrections.length > 0) {
                displayFeedback(data.corrections);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your message. Please try again.', false);
        });
    });
    
    // Initial scroll to bottom
    scrollToBottom();
    
    // Focus input on page load
    userInput.focus();
    
    // Press Shift+Enter for new line, Enter to submit
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            messageForm.dispatchEvent(new Event('submit'));
        }
    });
});
