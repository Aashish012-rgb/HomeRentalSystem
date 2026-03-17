"""
Chat System Views and ViewSets
REST API views for chat operations including listing chats, retrieving messages, and sending messages.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Chat, Message
from .serializers import ChatSerializer, ChatListSerializer, MessageSerializer
from .permissions import IsChatParticipant, IsBookingAccepted, IsMessageSenderOrRecipient
from home.models import Booking


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for chat messages"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Chat operations.
    
    - list: Get all chats for current user
    - retrieve: Get specific chat with all messages
    - create_or_get: Create or get chat for a booking
    - mark_messages_as_read: Mark all unread messages as read
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get chats where user is a participant"""
        user = self.request.user
        return Chat.objects.filter(participants=user).distinct()
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'list':
            return ChatListSerializer
        return ChatSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get specific chat with all messages"""
        chat = self.get_object()
        
        # Check permissions
        if not chat.participants.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You don\'t have permission to access this chat.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mark all unread messages from other participant as read
        other_user = chat.get_other_participant(request.user)
        if other_user:
            chat.messages.filter(
                sender=other_user,
                is_read=False
            ).update(is_read=True)
        
        serializer = self.get_serializer(chat)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def create_or_get(self, request):
        """
        Create or get a chat for a booking.
        Only works if booking is accepted.
        
        Expected POST data:
        {
            "booking_id": <int>
        }
        """
        booking_id = request.data.get('booking_id')
        
        if not booking_id:
            return Response(
                {'detail': 'booking_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Check if user is owner or tenant
        if request.user not in [booking.owner, booking.booked_by]:
            return Response(
                {'detail': 'You don\'t have permission to access this booking.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if booking is accepted
        if not booking.is_accepted:
            return Response(
                {'detail': 'Chat is only available after booking acceptance.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create chat
        chat, created = Chat.objects.get_or_create(booking=booking)
        
        # Ensure participants are set
        if not chat.participants.exists():
            chat.participants.set([booking.owner, booking.booked_by])
        
        serializer = self.get_serializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request):
        """Mark all unread messages in this chat as read"""
        chat = self.get_object()
        
        # Check permissions
        if not chat.participants.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You don\'t have permission to access this chat.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mark messages as read
        chat.messages.filter(
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        return Response({'detail': 'Messages marked as read.'})
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def messages(self, request, pk=None):
        """Get paginated messages for a specific chat"""
        chat = self.get_object()
        
        # Check permissions
        if not chat.participants.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You don\'t have permission to access this chat.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = chat.messages.all()
        page = self.paginate_queryset(messages)
        
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message operations.
    
    - list: Get messages (filtered by chat)
    - create: Send a new message
    - retrieve: Get specific message
    - destroy: Delete a message (only by sender)
    """
    permission_classes = [permissions.IsAuthenticated, IsChatParticipant]
    pagination_class = StandardResultsSetPagination
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """Get messages from chats where user is a participant"""
        user = self.request.user
        return Message.objects.filter(chat__participants=user).distinct()
    
    def create(self, request, *args, **kwargs):
        """Send a new message"""
        chat_id = request.data.get('chat')
        content = request.data.get('content', '').strip()
        
        if not chat_id or not content:
            return Response(
                {'detail': 'chat and content are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chat = get_object_or_404(Chat, id=chat_id)
        
        # Check if user is participant
        if not chat.participants.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You don\'t have permission to send messages in this chat.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if booking is accepted
        if not chat.booking.is_accepted:
            return Response(
                {'detail': 'Chat is not available for this booking.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create message
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            content=content
        )
        
        # Update chat's updated_at
        chat.save(update_fields=['updated_at'])
        
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a message (only by sender)"""
        message = self.get_object()
        
        if message.sender != request.user:
            return Response(
                {'detail': 'You can only delete your own messages.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def by_chat(self, request):
        """Get messages filtered by chat_id"""
        chat_id = request.query_params.get('chat_id')
        
        if not chat_id:
            return Response(
                {'detail': 'chat_id query parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chat = get_object_or_404(Chat, id=chat_id)
        
        # Check permissions
        if not chat.participants.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You don\'t have permission to access this chat.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = chat.messages.all()
        page = self.paginate_queryset(messages)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
