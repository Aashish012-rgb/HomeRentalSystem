# Chat System - Migration & Setup Instructions

## Overview

This guide walks you through the steps to set up the new Django Chat System in your Home Rental project.

## Prerequisites

- Django 6.0+ (already installed)
- Python 3.8+
- Your existing Home Rental project is working

## Step-by-Step Setup

### Step 1: Install Required Packages

```bash
# Install all required packages
pip install -r chat_requirements.txt
```

Or install individually:
```bash
pip install channels==4.0.0
pip install asgiref==3.8.1
pip install djangorestframework==3.14.0
pip install django-cors-headers==4.3.0
pip install daphne==4.0.0
pip install channels-redis==4.1.0  # For production only
```

### Step 2: Verify Django Settings Updated

The `HomeRental/settings.py` should already have:

```python
# Should contain:
INSTALLED_APPS = [
    'daphne',  # Must be first
    'django.contrib.admin',
    # ... other apps ...
    'rest_framework',
    'corsheaders',
    'chat',  # Our new chat app
    'home',
]

# Should contain:
ASGI_APPLICATION = 'HomeRental.asgi.application'

# Should contain:
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# Should contain:
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

If not, update `HomeRental/settings.py` manually.

### Step 3: Verify ASGI Configuration

Check `HomeRental/asgi.py`:

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeRental.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
```

If not, update it manually.

### Step 4: Create and Apply Migrations

```bash
# Create migrations for the chat app
python manage.py makemigrations chat

# Apply the migrations to the database
python manage.py migrate chat
```

**Expected output:**
```
Applying chat.0001_initial... OK
```

### Step 5: Verify Chat App Loaded

```bash
python manage.py shell
```

In the shell:
```python
from chat.models import Chat, Message
print("Chat models loaded successfully!")
# Should print: Chat models loaded successfully!

# Exit with Ctrl+D or type: exit()
```

### Step 6: Verify Database Tables Created

```bash
python manage.py shell
```

In the shell:
```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print([t[0] for t in tables])

# Should include: 'chat_chat', 'chat_message'
```

### Step 7: Start Development Server

**Option A: Using Daphne (Recommended for WebSocket)**
```bash
# Install Daphne if not already installed
pip install daphne

# Run Daphne server
daphne -b 0.0.0.0 -p 8000 HomeRental.asgi:application
```

**Option B: Using Django's Development Server**
```bash
# Note: WebSocket may not work properly with runserver
python manage.py runserver
```

### Step 8: Verify Installation

#### Test REST API Endpoints

Open browser or use curl:
```bash
# Get admin login page (should work)
curl http://localhost:8000/admin/
```

#### Access Django Admin

1. Go to http://localhost:8000/admin/
2. Login with superuser account
3. You should see new "Chat" and "Message" sections in admin

#### Test Chat API

```bash
# First, get your session ID
# 1. Go to http://localhost:8000/admin/ and login
# 2. Copy the sessionid cookie from browser DevTools

# Then test the endpoint:
curl http://localhost:8000/api/chat/chats/ \
  -H "Cookie: sessionid=<your_session_id>"

# Should return: {"count":0,"next":null,"previous":null,"results":[]}
```

## Testing the Chat System

### Step 1: Create a Test Booking

1. Create property as one user
2. Create booking as different user
3. Accept booking (this automatically creates a Chat)

### Step 2: Access Chat via Admin

1. Go to http://localhost:8000/admin/chat/chat/
2. You should see the chat created for the booking

### Step 3: Test REST API

```bash
# List all chats
curl http://localhost:8000/api/chat/chats/ \
  -H "Cookie: sessionid=<your_session_id>"

# Send a message
curl -X POST http://localhost:8000/api/chat/messages/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=<your_session_id>" \
  -d '{"chat": 1, "content": "Hello!"}'
```

### Step 4: Test WebSocket

Install wscat:
```bash
npm install -g wscat
```

Connect to WebSocket:
```bash
wscat -c ws://localhost:8000/ws/chat/1/
```

Send message:
```
Connected (press CTRL+C to quit)
> {"type": "chat_message", "message": "Hello WebSocket!"}
```

Should receive:
```
< {"type": "chat_message", "id": 1, "sender_id": 1, ...}
```

## Troubleshooting

### Issue: Module not found error

**Error:** `ModuleNotFoundError: No module named 'channels'`

**Solution:**
```bash
pip install channels==4.0.0
```

### Issue: Chat app won't migrate

**Error:** `django.core.management.CommandError: No changes detected in app 'chat'`

**Solution:**
```bash
# First migration might need explicit creation
python manage.py makemigrations chat --empty chat --name initial
# Edit the migration if needed
python manage.py migrate chat
```

### Issue: WebSocket connection refused

**Error:** `WebSocket connection failed`

**Solution 1:** Ensure Daphne is running (not Django's runserver)
```bash
daphne -b 0.0.0.0 -p 8000 HomeRental.asgi:application
```

**Solution 2:** Check if port 8000 is in use
```bash
# Linux/Mac
lsof -i :8000

# Windows (in PowerShell)
netstat -ano | findstr :8000

# Kill the process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

### Issue: Permission denied on chat access

**Error:** `You don't have permission to access this chat.`

**Solution:**
- Ensure you're logged in as a participant in the booking
- Use same session ID where you have permission
- Check booking actually exists and is accepted

### Issue: Settings not updated

**Error:** Different Channels errors (no ASGI_APPLICATION, etc.)

**Solution:**
- Manually update `HomeRental/settings.py`
- Ensure all settings from guide are in place
- Restart server after changes

### Issue: CORS errors

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:**
- Update `CORS_ALLOWED_ORIGINS` in settings.py
- Add your frontend URL to the list
- Restart server

## Verification Checklist

Go through this checklist to ensure everything is installed correctly:

- [ ] Channels and related packages installed (`pip list | grep channels`)
- [ ] Chat app in INSTALLED_APPS
- [ ] ASGI_APPLICATION configured
- [ ] CHANNEL_LAYERS configured
- [ ] Migrations created (`python manage.py makemigrations chat`)
- [ ] Migrations applied (`python manage.py migrate chat`)
- [ ] Chat tables in database
- [ ] Admin panel shows Chat/Message models
- [ ] REST API endpoints accessible
- [ ] WebSocket connects successfully
- [ ] Can create/access chats for accepted bookings

## Running Tests

```bash
# Run all chat app tests
python manage.py test chat

# Run specific test
python manage.py test chat.tests.ChatModelTest

# Run with verbose output
python manage.py test chat -v 2
```

## Development Commands

```bash
# Start Daphne server
daphne -b 0.0.0.0 -p 8000 HomeRental.asgi:application

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Create fresh database (WARNING: deletes all data)
python manage.py flush

# Show SQL migrations
python manage.py sqlmigrate chat 0001

# Clear migrations (advanced)
python manage.py migrate chat zero
```

## Next Steps After Setup

1. **Create Frontend Components**
   - See `CHAT_FRONTEND_EXAMPLES.md` for React/Vue/JavaScript examples

2. **Add Chat UI to Templates**
   - Create chat component in templates
   - Add chat button to booking detail view

3. **Test Complete Workflow**
   - Follow testing checklist above
   - Test all API endpoints
   - Test WebSocket functionality

4. **Deploy to Production**
   - See `CHAT_SYSTEM_GUIDE.md` for production setup
   - Use Redis for channel layers
   - Use production ASGI server

## Support & Help

- **Issues?** Check the Troubleshooting section
- **More info?** See `CHAT_SYSTEM_GUIDE.md`
- **API examples?** See `CHAT_API_EXAMPLES.md`
- **Frontend code?** See `CHAT_FRONTEND_EXAMPLES.md`

## Important Notes

1. **Use Daphne, not Django's runserver** - WebSocket requires proper ASGI server
2. **Run migrations before using** - Database tables must exist
3. **Chat only available after booking acceptance** - This is by design
4. **Authentication required** - Use session cookies to access endpoints

## Quick Command List

```bash
# Setup
pip install -r chat_requirements.txt
python manage.py makemigrations chat
python manage.py migrate chat

# Development
daphne -b 0.0.0.0 -p 8000 HomeRental.asgi:application

# Testing
curl http://localhost:8000/api/chat/chats/ \
  -H "Cookie: sessionid=<your_session>"

wscat -c ws://localhost:8000/ws/chat/1/
```

That's it! Your Django Chat System is ready to use. Proceed to `CHAT_FRONTEND_EXAMPLES.md` to add the frontend integration.

