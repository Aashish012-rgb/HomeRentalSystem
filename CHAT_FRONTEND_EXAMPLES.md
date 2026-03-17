# Chat System Frontend Integration Examples

## JavaScript WebSocket Client

### Basic WebSocket Connection

```javascript
class ChatClient {
    constructor(chatId, userId) {
        this.chatId = chatId;
        this.userId = userId;
        this.ws = null;
        this.messageHandlers = [];
        this.statusHandlers = [];
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.chatId}/`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('Connected to chat');
            this.onConnected();
        };
        
        this.ws.onmessage = (event) => {
            this.handleMessage(JSON.parse(event.data));
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.onError(error);
        };
        
        this.ws.onclose = () => {
            console.log('Disconnected from chat');
            this.onDisconnected();
        };
    }

    handleMessage(data) {
        if (data.type === 'chat_message') {
            this.messageHandlers.forEach(handler => handler(data));
        } else if (data.type === 'user_status') {
            this.statusHandlers.forEach(handler => handler(data));
        } else if (data.type === 'error') {
            console.error('Chat error:', data.message);
        }
    }

    sendMessage(content) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'chat_message',
                message: content
            }));
        }
    }

    markAsRead(messageIds) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'mark_as_read',
                message_ids: messageIds
            }));
        }
    }

    onConnected() {
        // Override in subclass
    }

    onDisconnected() {
        // Override in subclass
    }

    onError(error) {
        // Override in subclass
    }

    addMessageHandler(handler) {
        this.messageHandlers.push(handler);
    }

    addStatusHandler(handler) {
        this.statusHandlers.push(handler);
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}
```

### Using the Chat Client

```javascript
// Initialize
const chat = new ChatClient(1, currentUserId);
chat.connect();

// Handle incoming messages
chat.addMessageHandler((message) => {
    console.log(`${message.sender_username}: ${message.content}`);
    displayMessage(message);
});

// Handle status updates
chat.addStatusHandler((status) => {
    console.log(`${status.username} is ${status.status}`);
    updateUserStatus(status);
});

// Send message
document.getElementById('sendBtn').addEventListener('click', () => {
    const content = document.getElementById('messageInput').value;
    chat.sendMessage(content);
    document.getElementById('messageInput').value = '';
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    chat.disconnect();
});
```

## React Component Example

### Chat Container Component

```jsx
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

function ChatContainer({ chatId, currentUser }) {
    const [messages, setMessages] = useState([]);
    const [currentMessage, setCurrentMessage] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [onlineUsers, setOnlineUsers] = useState({});
    const wsRef = useRef(null);
    const messagesEndRef = useRef(null);

    // Fetch initial messages
    useEffect(() => {
        const fetchMessages = async () => {
            try {
                const response = await axios.get(
                    `/api/chat/chats/${chatId}/messages/`
                );
                setMessages(response.data.results || []);
                setIsLoading(false);
            } catch (err) {
                setError('Failed to load messages');
                setIsLoading(false);
            }
        };

        fetchMessages();
    }, [chatId]);

    // Connect to WebSocket
    useEffect(() => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${chatId}/`;
        
        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'chat_message') {
                setMessages(prev => [...prev, data]);
                // Mark as read if from other user
                if (data.sender_id !== currentUser.id) {
                    markAsRead([data.id]);
                }
            } else if (data.type === 'user_status') {
                setOnlineUsers(prev => ({
                    ...prev,
                    [data.user_id]: data.status === 'online'
                }));
            }
        };

        wsRef.current.onerror = (error) => {
            setError('WebSocket connection failed');
        };

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [chatId, currentUser.id]);

    // Auto-scroll to latest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = async (e) => {
        e.preventDefault();
        
        if (!currentMessage.trim()) return;

        try {
            // Send via WebSocket for real-time update
            wsRef.current.send(JSON.stringify({
                type: 'chat_message',
                message: currentMessage
            }));
            setCurrentMessage('');
        } catch (err) {
            setError('Failed to send message');
        }
    };

    const markAsRead = (messageIds) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'mark_as_read',
                message_ids: messageIds
            }));
        }
    };

    if (isLoading) {
        return <div className="text-center">Loading chat...</div>;
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

    return (
        <div className="chat-container">
            <div className="messages-list">
                {messages.map(msg => (
                    <div
                        key={msg.id}
                        className={`message ${
                            msg.sender_id === currentUser.id ? 'sent' : 'received'
                        }`}
                    >
                        <div className="message-sender">
                            <strong>{msg.sender_username}</strong>
                            {onlineUsers[msg.sender_id] && (
                                <span className="online-indicator">●</span>
                            )}
                        </div>
                        <div className="message-content">{msg.content}</div>
                        <div className="message-time">
                            {new Date(msg.timestamp).toLocaleTimeString()}
                            {msg.is_read && <span className="read-receipt">✓✓</span>}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={sendMessage} className="message-form">
                <input
                    type="text"
                    value={currentMessage}
                    onChange={e => setCurrentMessage(e.target.value)}
                    placeholder="Type a message..."
                    disabled={!wsRef.current?.readyState === WebSocket.OPEN}
                />
                <button type="submit" disabled={!currentMessage.trim()}>
                    Send
                </button>
            </form>
        </div>
    );
}

export default ChatContainer;
```

### Chat List Component

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ChatList({ onSelectChat }) {
    const [chats, setChats] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchChats = async () => {
            try {
                const response = await axios.get('/api/chat/chats/');
                setChats(response.data.results || []);
                setIsLoading(false);
            } catch (err) {
                console.error('Failed to load chats', err);
                setIsLoading(false);
            }
        };

        fetchChats();
    }, []);

    if (isLoading) {
        return <div>Loading chats...</div>;
    }

    if (chats.length === 0) {
        return <div className="alert alert-info">No chats yet. Accept a booking to start chatting!</div>;
    }

    return (
        <div className="chat-list">
            {chats.map(chat => (
                <div
                    key={chat.id}
                    className="chat-item"
                    onClick={() => onSelectChat(chat)}
                >
                    <div className="chat-header">
                        <h3>{chat.property_title}</h3>
                        {chat.unread_count > 0 && (
                            <span className="badge bg-primary">
                                {chat.unread_count}
                            </span>
                        )}
                    </div>
                    <div className="chat-preview">
                        {chat.last_message ? (
                            <>
                                <strong>{chat.last_message.sender}:</strong>
                                <p>{chat.last_message.content}</p>
                            </>
                        ) : (
                            <p className="text-muted">No messages yet</p>
                        )}
                    </div>
                    <div className="chat-time">
                        {new Date(chat.updated_at).toLocaleDateString()}
                    </div>
                </div>
            ))}
        </div>
    );
}

export default ChatList;
```

## Vue.js Component Example

### Vue Chat Component

```vue
<template>
    <div class="chat-container">
        <div class="messages-list">
            <div
                v-for="message in messages"
                :key="message.id"
                :class="['message', message.sender_id === currentUser.id ? 'sent' : 'received']"
            >
                <div class="message-sender">
                    <strong>{{ message.sender_username }}</strong>
                    <span v-if="onlineUsers[message.sender_id]" class="online-indicator">●</span>
                </div>
                <div class="message-content">{{ message.content }}</div>
                <div class="message-time">
                    {{ formatTime(message.timestamp) }}
                    <span v-if="message.is_read" class="read-receipt">✓✓</span>
                </div>
            </div>
        </div>

        <form @submit.prevent="sendMessage" class="message-form">
            <input
                v-model="currentMessage"
                type="text"
                placeholder="Type a message..."
                @keyup.enter="sendMessage"
            />
            <button type="submit" :disabled="!currentMessage.trim()">Send</button>
        </form>
    </div>
</template>

<script>
export default {
    props: {
        chatId: {
            type: Number,
            required: true
        },
        currentUser: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            messages: [],
            currentMessage: '',
            ws: null,
            onlineUsers: {},
            isLoading: true
        };
    },
    mounted() {
        this.fetchMessages();
        this.connectWebSocket();
    },
    beforeUnmount() {
        if (this.ws) {
            this.ws.close();
        }
    },
    methods: {
        async fetchMessages() {
            try {
                const response = await fetch(`/api/chat/chats/${this.chatId}/messages/`);
                const data = await response.json();
                this.messages = data.results || [];
                this.isLoading = false;
            } catch (error) {
                console.error('Failed to fetch messages:', error);
                this.isLoading = false;
            }
        },
        connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.chatId}/`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'chat_message') {
                    this.messages.push(data);
                    if (data.sender_id !== this.currentUser.id) {
                        this.markAsRead([data.id]);
                    }
                } else if (data.type === 'user_status') {
                    this.$set(this.onlineUsers, data.user_id, data.status === 'online');
                }
            };
        },
        sendMessage() {
            if (!this.currentMessage.trim() || !this.ws) return;
            
            this.ws.send(JSON.stringify({
                type: 'chat_message',
                message: this.currentMessage
            }));
            
            this.currentMessage = '';
        },
        markAsRead(messageIds) {
            if (this.ws?.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'mark_as_read',
                    message_ids: messageIds
                }));
            }
        },
        formatTime(timestamp) {
            return new Date(timestamp).toLocaleTimeString();
        }
    }
};
</script>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.messages-list {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
}

.message {
    margin-bottom: 15px;
    display: flex;
    flex-direction: column;
}

.message.sent {
    align-items: flex-end;
}

.message.received {
    align-items: flex-start;
}

.message-content {
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 70%;
    word-wrap: break-word;
}

.message.sent .message-content {
    background-color: #007bff;
    color: white;
}

.message.received .message-content {
    background-color: #e9ecef;
    color: black;
}

.message-form {
    display: flex;
    gap: 10px;
    padding: 15px;
    border-top: 1px solid #dee2e6;
}

.message-form input {
    flex: 1;
    padding: 10px;
    border: 1px solid #dee2e6;
    border-radius: 5px;
}

.message-form button {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.message-form button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.online-indicator {
    color: green;
    margin-left: 5px;
}

.read-receipt {
    font-size: 0.8em;
    color: blue;
}
</style>
```

## CSS Styling

### Basic Chat Styling

```css
/* Chat Container */
.chat-container {
    display: flex;
    flex-direction: column;
    height: 500px;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    overflow: hidden;
}

/* Messages List */
.messages-list {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background-color: #f8f9fa;
}

/* Message Styles */
.message {
    margin-bottom: 15px;
    display: flex;
    flex-direction: column;
    animation: messageSlideIn 0.3s ease-out;
}

@keyframes messageSlideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message.sent {
    align-items: flex-end;
}

.message.received {
    align-items: flex-start;
}

.message-sender {
    font-weight: 600;
    margin-bottom: 5px;
    font-size: 0.9em;
    color: #495057;
}

.message-content {
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 70%;
    word-wrap: break-word;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message.sent .message-content {
    background-color: #007bff;
    color: white;
    border-bottom-right-radius: 0;
}

.message.received .message-content {
    background-color: #e9ecef;
    color: #212529;
    border-bottom-left-radius: 0;
}

.message-time {
    font-size: 0.75em;
    color: #6c757d;
    margin-top: 5px;
}

.read-receipt {
    margin-left: 5px;
    color: #007bff;
}

/* Message Form */
.message-form {
    display: flex;
    gap: 10px;
    padding: 15px;
    background-color: white;
    border-top: 1px solid #dee2e6;
}

.message-form input[type="text"] {
    flex: 1;
    padding: 10px 15px;
    border: 1px solid #dee2e6;
    border-radius: 25px;
    font-size: 0.95em;
    outline: none;
    transition: all 0.3s ease;
}

.message-form input[type="text"]:focus {
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.message-form button {
    padding: 10px 25px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
}

.message-form button:hover {
    background-color: #0056b3;
    transform: scale(1.02);
}

.message-form button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: scale(1);
}

/* Chat List */
.chat-list {
    list-style: none;
    padding: 0;
}

.chat-item {
    padding: 15px;
    border-bottom: 1px solid #dee2e6;
    cursor: pointer;
    transition: all 0.2s ease;
}

.chat-item:hover {
    background-color: #f8f9fa;
}

.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.chat-header h3 {
    margin: 0;
    font-size: 1em;
}

.chat-preview {
    color: #6c757d;
    font-size: 0.9em;
    margin-bottom: 5px;
}

.chat-time {
    font-size: 0.8em;
    color: #adb5bd;
}

/* Online Indicator */
.online-indicator {
    color: #28a745;
    margin-left: 5px;
    font-size: 0.8em;
}

/* Responsive */
@media (max-width: 768px) {
    .message-content {
        max-width: 85%;
    }
    
    .message-form {
        padding: 10px;
    }
}
```

## Integration Checklist

- [ ] Install required dependencies (channels, djangorestframework)
- [ ] Run migrations for chat app
- [ ] Update Django settings for Channels
- [ ] Update ASGI configuration
- [ ] Test WebSocket connection
- [ ] Create chat UI component
- [ ] Connect to REST API for initial messages
- [ ] Connect WebSocket for real-time updates
- [ ] Test sending and receiving messages
- [ ] Add chat button to booking detail view
- [ ] Test permission controls
- [ ] Add read receipts and typing indicators
- [ ] Style chat UI matching design system
- [ ] Deploy with proper WebSocket server (Daphne)

## Troubleshooting

**WebSocket connection fails:**
- Ensure Daphne server is running
- Check browser console for error details
- Verify chat ID is valid

**Messages not updating in real-time:**
- Check WebSocket connection status
- Verify message payload format
- Check browser console for errors

**Permission errors:**
- Ensure user is authenticated
- Verify user is a chat participant
- Check booking is accepted

