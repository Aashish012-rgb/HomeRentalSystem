# Chat System API Examples

## Authentication
All endpoints require authentication via session cookies. To test, use:
```
-H "Cookie: sessionid=<your_session_id>"
```

Or use Django's built-in API browsing at the endpoint URL.

## REST API Examples

### 1. List All Chats for Current User

```bash
curl -X GET http://localhost:8000/api/chat/chats/ \
  -H "Cookie: sessionid=<your_session_id>"
```

**Example Response:**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "booking_id": 5,
            "property_title": "Beautiful Apartment in Downtown",
            "other_participant": {
                "id": 2,
                "username": "john_doe",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com"
            },
            "last_message": {
                "content": "When can I move in?",
                "sender": "john_doe",
                "timestamp": "2024-03-17T14:30:45.123456Z",
                "is_read": true
            },
            "unread_count": 0,
            "updated_at": "2024-03-17T14:30:45.123456Z"
        }
    ]
}
```

### 2. Get Specific Chat with All Messages

```bash
curl -X GET http://localhost:8000/api/chat/chats/1/ \
  -H "Cookie: sessionid=<your_session_id>"
```

**Example Response:**
```json
{
    "id": 1,
    "booking_id": 5,
    "property_title": "Beautiful Apartment in Downtown",
    "participants": [
        {
            "id": 1,
            "username": "jane_owner",
            "first_name": "Jane",
            "last_name": "Owner",
            "email": "jane@example.com"
        },
        {
            "id": 2,
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        }
    ],
    "tenant": {
        "id": 2,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    },
    "owner": {
        "id": 1,
        "username": "jane_owner",
        "first_name": "Jane",
        "last_name": "Owner",
        "email": "jane@example.com"
    },
    "messages": [
        {
            "id": 1,
            "chat": 1,
            "sender": {
                "id": 2,
                "username": "john_doe",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com"
            },
            "content": "Hi, I'm interested in this property",
            "timestamp": "2024-03-17T10:15:30.123456Z",
            "is_read": true
        },
        {
            "id": 2,
            "chat": 1,
            "sender": {
                "id": 1,
                "username": "jane_owner",
                "first_name": "Jane",
                "last_name": "Owner",
                "email": "jane@example.com"
            },
            "content": "Great! Let's discuss the details.",
            "timestamp": "2024-03-17T10:45:15.123456Z",
            "is_read": true
        }
    ],
    "message_count": 2,
    "unread_count": 0,
    "created_at": "2024-03-17T10:15:30.123456Z",
    "updated_at": "2024-03-17T14:30:45.123456Z"
}
```

### 3. Create or Get Chat for Booking

**Note:** Booking must be accepted (is_accepted=True)

```bash
curl -X POST http://localhost:8000/api/chat/chats/create_or_get/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=<your_session_id>" \
  -d '{
    "booking_id": 5
  }'
```

**Success Response (201 Created or 200 OK):**
```json
{
    "id": 1,
    "booking_id": 5,
    "property_title": "Beautiful Apartment in Downtown",
    "participants": [
        {
            "id": 1,
            "username": "jane_owner",
            "first_name": "Jane",
            "last_name": "Owner",
            "email": "jane@example.com"
        },
        {
            "id": 2,
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        }
    ],
    "messages": [],
    "message_count": 0,
    "unread_count": 0,
    "created_at": "2024-03-17T10:15:30.123456Z",
    "updated_at": "2024-03-17T10:15:30.123456Z"
}
```

**Error Response (400 Bad Request - Booking not accepted):**
```json
{
    "detail": "Chat is only available after booking acceptance."
}
```

**Error Response (403 Forbidden - User not involved in booking):**
```json
{
    "detail": "You don't have permission to access this booking."
}
```

### 4. Send Message

```bash
curl -X POST http://localhost:8000/api/chat/messages/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=<your_session_id>" \
  -d '{
    "chat": 1,
    "content": "When can I move in?"
  }'
```

**Success Response (201 Created):**
```json
{
    "id": 3,
    "chat": 1,
    "sender": {
        "id": 2,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    },
    "content": "When can I move in?",
    "timestamp": "2024-03-17T14:30:45.123456Z",
    "is_read": false
}
```

**Error Response (400 Bad Request - Empty content):**
```json
{
    "detail": "chat and content are required."
}
```

**Error Response (403 Forbidden - Not a participant):**
```json
{
    "detail": "You don't have permission to send messages in this chat."
}
```

### 5. Get Messages by Chat (Paginated)

```bash
curl -X GET "http://localhost:8000/api/chat/messages/by_chat/?chat_id=1&page=1&page_size=20" \
  -H "Cookie: sessionid=<your_session_id>"
```

**Response:**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "chat": 1,
            "sender": {
                "id": 2,
                "username": "john_doe",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com"
            },
            "content": "Hi, I'm interested in this property",
            "timestamp": "2024-03-17T10:15:30.123456Z",
            "is_read": true
        }
    ]
}
```

### 6. Mark Messages as Read

```bash
curl -X POST http://localhost:8000/api/chat/chats/1/mark_as_read/ \
  -H "Cookie: sessionid=<your_session_id>"
```

**Response:**
```json
{
    "detail": "Messages marked as read."
}
```

### 7. Delete Message (Only by sender)

```bash
curl -X DELETE http://localhost:8000/api/chat/messages/3/ \
  -H "Cookie: sessionid=<your_session_id>"
```

**Success Response (204 No Content)**
```
HTTP/1.1 204 No Content
```

**Error Response (403 Forbidden - Not sender):**
```json
{
    "detail": "You can only delete your own messages."
}
```

## WebSocket Examples

### Connect to Chat WebSocket

Using wscat:
```bash
wscat -c ws://localhost:8000/ws/chat/1/
```

### Send Message via WebSocket

```json
{
    "type": "chat_message",
    "message": "Hello! This is a real-time message"
}
```

### Receive Message via WebSocket

```json
{
    "type": "chat_message",
    "id": 4,
    "sender_id": 1,
    "sender_username": "jane_owner",
    "content": "Hello! This is a real-time message",
    "timestamp": "2024-03-17T14:35:20.123456Z",
    "is_read": false
}
```

### Mark Messages as Read via WebSocket

```json
{
    "type": "mark_as_read",
    "message_ids": [1, 2, 3]
}
```

### Receive User Status Update

When a user connects or disconnects:
```json
{
    "type": "user_status",
    "status": "online",
    "user_id": 1,
    "username": "jane_owner"
}
```

Or when disconnecting:
```json
{
    "type": "user_status",
    "status": "offline",
    "user_id": 1,
    "username": "jane_owner"
}
```

## cURL Testing Examples

### Using Shell Script to Test

```bash
#!/bin/bash

# Set these variables
SESSION_ID="your_session_id_here"
BASE_URL="http://localhost:8000"
CHAT_ID=1
BOOKING_ID=5

# List chats
echo "=== Listing chats ==="
curl -s "${BASE_URL}/api/chat/chats/" \
  -H "Cookie: sessionid=${SESSION_ID}" | jq .

# Get specific chat
echo "=== Getting chat details ==="
curl -s "${BASE_URL}/api/chat/chats/${CHAT_ID}/" \
  -H "Cookie: sessionid=${SESSION_ID}" | jq .

# Create or get chat
echo "=== Creating/getting chat ==="
curl -s -X POST "${BASE_URL}/api/chat/chats/create_or_get/" \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=${SESSION_ID}" \
  -d "{\"booking_id\": ${BOOKING_ID}}" | jq .

# Send message
echo "=== Sending message ==="
curl -s -X POST "${BASE_URL}/api/chat/messages/" \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=${SESSION_ID}" \
  -d "{\"chat\": ${CHAT_ID}, \"content\": \"Test message\"}" | jq .

# Get chat messages
echo "=== Getting messages ==="
curl -s "${BASE_URL}/api/chat/messages/by_chat/?chat_id=${CHAT_ID}" \
  -H "Cookie: sessionid=${SESSION_ID}" | jq .
```

## Error Codes Reference

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check required fields and booking acceptance status |
| 403 | Forbidden | Verify user is booking participant or message sender |
| 404 | Not Found | Verify chat_id, message_id, or booking_id exists |
| 401 | Unauthorized | Session expired, need to login again |

## Testing Workflow

1. **Setup:**
   - Create property as owner
   - Create booking as tenant
   - Accept booking as owner

2. **Test REST API:**
   - List chats
   - Get specific chat
   - Send message
   - Verify message appears in chat

3. **Test WebSocket:**
   - Connect to chat WebSocket
   - Send message via WebSocket
   - Verify broadcast to all participants
   - Test user status updates

4. **Test Permissions:**
   - Try accessing chat as non-participant (should fail)
   - Try deleting other user's message (should fail)
   - Try sending message before booking accepted (should fail)

