# Django Chat System Implementation Guide

## Overview
This document provides a comprehensive guide to the newly implemented real-time chat system for the Home Rental application. The system replaces WhatsApp integration with a built-in Django chat functionality using Django REST Framework and Django Channels for real-time messaging.

## Architecture

### Components
1. **Chat App** - Django app handling chat models, serializers, views, and consumers
2. **Chat Model** - Represents a conversation thread between owner and tenant
3. **Message Model** - Individual messages within a chat
4. **ViewSets** - REST API endpoints for chat operations
5. **Consumers** - WebSocket handlers for real-time messaging
6. **Permissions** - Custom permission classes for access control

## Database Models

### Chat Model
```python
- booking: OneToOneField(Booking)
- participants: ManyToManyField(User)
- created_at: DateTimeField
- updated_at: DateTimeField
```

**Features:**
- One chat per booking
- Multiple participants (owner + tenant)
- Automatic timestamps
- Database indexes for performance

### Message Model
```python
- chat: ForeignKey(Chat)
- sender: ForeignKey(User)
- content: TextField
- timestamp: DateTimeField
- is_read: BooleanField
```

**Features:**
- Tracks sender identity
- Message read status
- Ordered by timestamp
- Database indexes for fast queries

## REST API Endpoints

### Chat Endpoints

#### 1. List All Chats
```
GET /api/chat/chats/
Authentication: Required
Response: List of chats with last message and unread count
```

#### 2. Get Specific Chat
```
GET /api/chat/chats/{id}/
Authentication: Required
Response: Chat with all messages and participants
```

**Behavior:**
- Returns full chat details with message history
- Automatically marks all unread messages as read
- Checks user is a participant

#### 3. Create or Get Chat for Booking
```
POST /api/chat/chats/create_or_get/
Content-Type: application/json

{
    "booking_id": <int>
}

Response: Chat object (201 if created, 200 if exists)
```

**Validation:**
- Booking must be accepted (is_accepted=True)
- Only booking owner or tenant can create/access chat
- Returns 400 if booking not accepted
- Returns 403 if user is not involved in booking

#### 4. Mark Messages as Read
```
POST /api/chat/chats/{id}/mark_as_read/
Authentication: Required
Response: {"detail": "Messages marked as read."}
```

#### 5. Get Paginated Messages for Chat
```
GET /api/chat/chats/{id}/messages/?page=1&page_size=20
Authentication: Required
Response: Paginated message list
```

### Message Endpoints

#### 1. Send Message
```
POST /api/chat/messages/
Content-Type: application/json

{
    "chat": <chat_id>,
    "content": "<message_content>"
}

Response: Created message object
```

**Validation:**
- User must be chat participant
- Booking must be accepted
- Content cannot be empty
- Updates chat's updated_at timestamp

#### 2. Get Messages by Chat
```
GET /api/chat/messages/by_chat/?chat_id=<int>
Authentication: Required
Response: Paginated messages for the chat
```

#### 3. Delete Message
```
DELETE /api/chat/messages/{id}/
Authentication: Required
Response: 204 No Content
```

**Validation:**
- Only message sender can delete
- Returns 403 if user is not sender

## WebSocket Real-Time Messaging

### Connection
```
WebSocket URL: ws://localhost:8000/ws/chat/<chat_id>/
Authentication: Session-based
```

### Message Format - Send Message
```json
{
    "type": "chat_message",
    "message": "Your message content here"
}
```

### Message Format - Receive Message
```json
{
    "type": "chat_message",
    "id": <message_id>,
    "sender_id": <user_id>,
    "sender_username": "username",
    "content": "message content",
    "timestamp": "2024-03-17T12:30:45.123456Z",
    "is_read": false
}
```

### Message Format - Mark as Read
```json
{
    "type": "mark_as_read",
    "message_ids": [1, 2, 3]
}
```

### Message Format - User Status
```json
{
    "type": "user_status",
    "status": "online|offline",
    "user_id": <user_id>,
    "username": "username"
}
```

## Chat Availability Rules

1. **Before Booking Acceptance**
   - Chat NOT available
   - API returns 400 Bad Request if creation attempted
   - Frontend should disable chat button

2. **After Booking Acceptance**
   - Chat automatically created
   - Both owner and tenant can access
   - Real-time messaging enabled
   - Message history available

3. **Access Control**
   - Only chat participants can access
   - Non-participants receive 403 Forbidden
   - Owner and tenant are automatic participants

## Implementation Details

### Booking Acceptance Flow
When a booking is accepted:
1. `accept_booking()` view sets `booking.is_accepted = True`
2. Chat instance is automatically created
3. Participants are set to owner and tenant
4. Chat is ready for messaging

### Chat Consumer (WebSocket)
**Authentication:** Requires authenticated user

**Features:**
- Session-based authentication via `AuthMiddlewareStack`
- Validates user is chat participant on connection
- Broadcasts messages to all participants
- Tracks online/offline status
- Auto-saves messages to database
- Handles message read status

**Database Operations:**
```python
@database_sync_to_async
def save_message(content)
    # Save message to database

@database_sync_to_async
def check_chat_access()
    # Verify user has access

@database_sync_to_async
def mark_messages_as_read(message_ids)
    # Update is_read status
```

## Settings Configuration

### Essential Settings
```python
# INSTALLED_APPS
INSTALLED_APPS = [
    'daphne',  # Must be first
    'chat',
    'rest_framework',
    'corsheaders',
    # ... other apps
]

# ASGI Application
ASGI_APPLICATION = 'HomeRental.asgi.application'

# Channels Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install channels==4.0.0
pip install channels-redis==4.1.0  # For production
pip install djangorestframework==3.14.0
pip install django-cors-headers==4.3.0
```

### 2. Run Migrations
```bash
python manage.py makemigrations chat
python manage.py migrate chat
```

### 3. Create Superuser (if needed)
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
**Option 1: Using Daphne (preferred)**
```bash
daphne -b 0.0.0.0 -p 8000 HomeRental.asgi:application
```

**Option 2: Using runserver (Django's development server)**
```bash
python manage.py runserver
```

## Permission Classes

### IsChatParticipant
- Ensures user is a participant in the chat
- Used for chat operations
- Returns 403 if not participant

### IsBookingAccepted
- Ensures booking is accepted
- Used for chat access
- Returns 400 if booking not accepted

### IsMessageSenderOrRecipient
- Allows message access to sender or recipient
- Used for message operations

### IsSender
- Allows only sender to edit/delete
- Used for message delete operations

## Frontend Integration

### JavaScript WebSocket Client
```javascript
const chatId = <chat_id>;
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${chatId}/`);

// Connect event
ws.onopen = (event) => {
    console.log('Connected to chat');
};

// Receive messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'chat_message') {
        // Handle incoming message
        displayMessage(data);
    } else if (data.type === 'user_status') {
        // Handle user status
        updateUserStatus(data);
    }
};

// Send message
function sendMessage(content) {
    ws.send(JSON.stringify({
        type: 'chat_message',
        message: content
    }));
}

// Mark messages as read
function markAsRead(messageIds) {
    ws.send(JSON.stringify({
        type: 'mark_as_read',
        message_ids: messageIds
    }));
}
```

### React Component Example
```javascript
import React, { useState, useEffect } from 'react';

function ChatComponent({ chatId, userId }) {
    const [messages, setMessages] = useState([]);
    const [ws, setWs] = useState(null);
    
    useEffect(() => {
        // Fetch initial messages
        fetch(`/api/chat/chats/${chatId}/messages/`)
            .then(r => r.json())
            .then(data => setMessages(data.results));
        
        // Connect WebSocket
        const websocket = new WebSocket(
            `ws://localhost:8000/ws/chat/${chatId}/`
        );
        
        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'chat_message') {
                setMessages([...messages, data]);
            }
        };
        
        setWs(websocket);
        
        return () => websocket.close();
    }, [chatId]);
    
    return (
        <div className="chat-container">
            {/* Chat UI */}
        </div>
    );
}
```

## Testing

### Test Creating Chat
```bash
curl -X POST http://localhost:8000/api/chat/chats/create_or_get/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=<your_session_id>" \
  -d '{"booking_id": 1}'
```

### Test Sending Message
```bash
curl -X POST http://localhost:8000/api/chat/messages/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=<your_session_id>" \
  -d '{"chat": 1, "content": "Hello!"}'
```

### Test WebSocket
```bash
# Using wscat (npm install -g wscat)
wscat -c ws://localhost:8000/ws/chat/1/
# Then send: {"type": "chat_message", "message": "Hello"}
```

## Database Performance

### Indexes
The Chat and Message models have database indexes on frequently queried fields:

**Chat Model:**
- Index on `updated_at` (for sorting by recent)
- Index on `created_at`

**Message Model:**
- Composite index on `chat` and `timestamp`
- Index on `sender`
- Index on `is_read`

### Query Optimization
- Messages are ordered by timestamp
- Chat participants are cached
- Use `select_related` for foreign keys

## Production Deployment

### Redis Channel Layer
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis.example.com', 6379)],
        },
    }
}
```

### Running with Supervisor (Daphne)
```ini
[program:daphne]
command=daphne -b 0.0.0.0 -p 8000 HomeRental.asgi:application
directory=/path/to/project
autostart=true
autorestart=true
```

### Nginx Configuration
```nginx
upstream daphne {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name example.com;
    
    location /ws/ {
        proxy_pass http://daphne;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    location /api/ {
        proxy_pass http://daphne;
        proxy_set_header Host $host;
    }
}
```

## Troubleshooting

### Issue: WebSocket Connection Refused
**Solution:** Ensure Daphne is running with ASGI application configured correctly

### Issue: Messages Not Persisting
**Solution:** Verify database migrations ran successfully: `python manage.py migrate`

### Issue: Permission Denied Accessing Chat
**Solution:** Verify user is a chat participant and booking is accepted

### Issue: Channel Layer Connection Failed
**Solution:** Ensure Redis is running (for production) or verify in-memory layer is configured

## Migration Path from WhatsApp

1. **Disable WhatsApp Links** ✓ (Completed)
   - Removed WhatsApp URL generation from views
   - Removed WhatsApp buttons from templates
   - Removed WhatsApp options from forms

2. **Enable Chat for Accepted Bookings** ✓ (Completed)
   - Chat auto-created on booking acceptance
   - Chat accessible only after acceptance
   - Permission-based access control

3. **Frontend Integration** (TODO)
   - Create chat UI component
   - Add WebSocket connection logic
   - Display chat button in booking details
   - Create chat list view

4. **User Notifications** (TODO)
   - Notify users when chat available
   - Real-time message notifications
   - Unread message badges

## File Structure
```
chat/
├── __init__.py
├── apps.py
├── models.py              # Chat and Message models
├── serializers.py         # DRF serializers
├── views.py              # ViewSets and API views
├── consumers.py          # WebSocket consumer
├── permissions.py        # Custom permissions
├── routing.py            # WebSocket URL routing
├── urls.py              # REST API URL routing
├── admin.py             # Django admin config
├── migrations/
│   └── __init__.py
```

## Next Steps

1. **Create Frontend Components**
   - Chat UI with message list
   - Message input form
   - WebSocket integration

2. **Add Chat UI to Booking Detail**
   - Show chat button for accepted bookings
   - Disable chat for pending bookings

3. **Implement Message Notifications**
   - Browser notifications
   - Email notifications for offline users
   - Read receipts

4. **Add Advanced Features**
   - Typing indicators
   - Message search
   - Chat export/archive
   - User presence indicators
   - Message reactions/emojis

## Support

For issues or questions about the chat system implementation, refer to:
- Chat app documentation
- Django Channels documentation: https://channels.readthedocs.io/
- Django REST Framework documentation: https://www.django-rest-framework.org/

