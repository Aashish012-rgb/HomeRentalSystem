"""
Chat System Models
This module defines models for real-time messaging between property owners and tenants.
Models include Chat (conversation thread) and Message (individual messages).
"""

from django.db import models
from django.contrib.auth.models import User
from home.models import Booking


class Chat(models.Model):
    """
    Chat model represents a conversation thread between owner and tenant.
    Only created after booking is accepted.
    
    Attributes:
        booking: ForeignKey to Booking (one-to-one relationship)
        participants: ManyToMany to User (owner and tenant)
        created_at: Timestamp when chat was created
        updated_at: Timestamp of last message
    """
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='chat')
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['-updated_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Chat for {self.booking.property.title}"
    
    def get_other_participant(self, user):
        """Get the other participant in the chat"""
        return self.participants.exclude(id=user.id).first()


class Message(models.Model):
    """
    Message model represents individual messages in a chat conversation.
    
    Attributes:
        chat: ForeignKey to Chat
        sender: ForeignKey to User (who sent the message)
        content: TextField for message content
        timestamp: Timestamp when message was sent
        is_read: Boolean to track if message has been read by recipient
    """
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['chat', '-timestamp']),
            models.Index(fields=['sender']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.save()
