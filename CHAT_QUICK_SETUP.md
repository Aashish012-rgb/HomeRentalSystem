# Chat System Quick Setup Guide

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r chat_requirements.txt
```

### 2. Run Database Migrations
The Chat and Message models are already defined. Create and apply migrations:

```bash
python manage.py makemigrations chat
python manage.py migrate chat
```

### 3. Update Requirements.txt
Add the following to your main `requirements.txt`:
```
channels==4.0.0
asgiref==3.8.1
djangorestframework==3.14.0
django-cors-headers==4.3.0
daphne==4.0.0
```

### 4. Start Development Server

**Option A: Using Daphne (Recommended for WebSocket testing)**
```bash
daphne -b 0.0.0.0 -p 8000 HomeRental.asgi:application
```

**Option B: Using Django Development Server**
```bash
python manage.py runserver
```

## Verify Installation

### 1. Check Chat App Loaded
```bash
python manage.py shell
>>> from chat.models import Chat, Message
>>> print("Chat app loaded successfully!")
```

### 2. Test REST API
```bash
# Get your session ID from browser devtools
curl http://localhost:8000/api/chat/chats/ \
  -H "Cookie: sessionid=<your_session_id>"
```

### 3. Test WebSocket (requires wscat)
```bash
npm install -g wscat
wscat -c ws://localhost:8000/ws/chat/1/
# Should connect successfully
```

## Key Features Enabled

### ✓ Chat Models
- `Chat` - Conversation between owner and tenant
- `Message` - Individual messages in conversation

### ✓ REST API Endpoints
- `GET /api/chat/chats/` - List all chats
- `GET /api/chat/chats/{id}/` - Get specific chat with messages
- `POST /api/chat/chats/create_or_get/` - Create/get chat for booking
- `POST /api/chat/messages/` - Send message
- `DELETE /api/chat/messages/{id}/` - Delete message

### ✓ WebSocket
- `ws://localhost:8000/ws/chat/{chat_id}/` - Real-time messaging

### ✓ Chat Availability
- Chat only available after booking is accepted (is_accepted=True)
- Automatically created when booking is accepted
- Access limited to booking participants

### ✓ WhatsApp Integration Removed
- Removed all WhatsApp URL generation
- Removed WhatsApp buttons from templates
- Removed WhatsApp options from forms

## Admin Interface

Access Django admin at: http://localhost:8000/admin/

View and manage:
- Chats
- Messages
- Participants

## Testing Chat Workflow

### 1. Create a Booking
- Login as owner
- List properties
- Add a booking from different user

### 2. Accept Booking
- Login as property owner
- Accept the booking
- Chat is automatically created

### 3. Access Chat via API
```bash
curl http://localhost:8000/api/chat/chats/ \
  -H "Cookie: sessionid=<owner_session_id>"

# Returns list of chats for owner
```

### 4. Send Message
```bash
curl -X POST http://localhost:8000/api/chat/messages/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=<your_session_id>" \
  -d '{"chat": 1, "content": "Hello!"}'
```

### 5. Connect WebSocket
```bash
wscat -c ws://localhost:8000/ws/chat/1/ \
  -H "Cookie: sessionid=<your_session_id>"

# Send: {"type": "chat_message", "message": "Hello from WebSocket!"}
```

## Common Issues & Solutions

### Issue: `channels` module not found
**Solution:** Run `pip install -r chat_requirements.txt`

### Issue: WebSocket connection refused
**Solution:** Make sure Daphne is running, not Django's runserver

### Issue: Chat not created when booking accepted
**Solution:** Verify migration ran: `python manage.py migrate chat`

### Issue: Permission denied accessing chat
**Solution:** Ensure you're logged in as booking participant (owner or tenant)

### Issue: CORS errors when accessing from frontend
**Solution:** Update `CORS_ALLOWED_ORIGINS` in settings.py

## Frontend Integration TODO

Create a chat UI component that:
1. Fetches chat list via API
2. Connects to WebSocket
3. Displays messages real-time
4. Marks messages as read
5. Shows user online status

## Documentation

Detailed documentation: See `CHAT_SYSTEM_GUIDE.md`

This includes:
- Complete API documentation
- WebSocket message formats
- Permission details
- Production deployment
- Advanced features

## Next Steps

1. ✓ Install dependencies
2. ✓ Run migrations
3. ✓ Start development server
4. ⧗ Create frontend chat component
5. ⧗ Add chat UI to booking details
6. ⧗ Implement message notifications

## Support Files

- `chat_requirements.txt` - Python dependencies
- `CHAT_SYSTEM_GUIDE.md` - Complete documentation
- `chat/` - Chat app source code
  - `models.py` - Chat and Message models
  - `views.py` - REST API ViewSets
  - `consumers.py` - WebSocket consumer
  - `serializers.py` - JSON serializers
  - `permissions.py` - Access control
  - `routing.py` - WebSocket URLs
  - `urls.py` - REST API URLs

