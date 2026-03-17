"""
Django Admin Configuration for Chat Models
"""

from django.contrib import admin
from .models import Chat, Message


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """Admin configuration for Chat model"""
    list_display = ('id', 'booking', 'participant_count', 'message_count', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('booking__property__title', 'participants__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def participant_count(self, obj):
        """Display participant count"""
        return obj.participants.count()
    participant_count.short_description = 'Participants'
    
    def message_count(self, obj):
        """Display message count"""
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin configuration for Message model"""
    list_display = ('id', 'chat', 'sender_username', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read', 'sender')
    search_fields = ('sender__username', 'content', 'chat__booking__property__title')
    readonly_fields = ('timestamp', 'chat', 'sender')
    
    def sender_username(self, obj):
        """Display sender username"""
        return obj.sender.username
    sender_username.short_description = 'Sender'
