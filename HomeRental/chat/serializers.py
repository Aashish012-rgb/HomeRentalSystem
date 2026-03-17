"""
Chat System Serializers
Serializers for Chat and Message models used in REST API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Chat, Message
from home.models import Booking


class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple user serializer for chat participants"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserSimpleSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'sender_id', 'content', 'timestamp', 'is_read']
        read_only_fields = ['id', 'timestamp', 'is_read']
    
    def create(self, validated_data):
        """Create a new message"""
        validated_data.pop('sender_id', None)  # Remove sender_id if present
        return Message.objects.create(**validated_data)


class ChatSerializer(serializers.ModelSerializer):
    """Serializer for Chat model with nested messages and participants"""
    participants = UserSimpleSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    booking_id = serializers.IntegerField(source='booking.id', read_only=True)
    property_title = serializers.CharField(source='booking.property.title', read_only=True)
    tenant = serializers.SerializerMethodField(read_only=True)
    owner = serializers.SerializerMethodField(read_only=True)
    message_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = [
            'id', 'booking_id', 'property_title', 'participants', 
            'tenant', 'owner', 'messages', 'message_count', 'unread_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_tenant(self, obj):
        """Get tenant information from booking"""
        return UserSimpleSerializer(obj.booking.booked_by).data
    
    def get_owner(self, obj):
        """Get owner information from booking"""
        return UserSimpleSerializer(obj.booking.owner).data
    
    def get_message_count(self, obj):
        """Get total message count in chat"""
        return obj.messages.count()
    
    def get_unread_count(self, obj):
        """Get unread message count for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class ChatListSerializer(serializers.ModelSerializer):
    """Simplified serializer for chat list view"""
    property_title = serializers.CharField(source='booking.property.title', read_only=True)
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = [
            'id', 'booking_id', 'property_title', 'other_participant', 
            'last_message', 'unread_count', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']
    
    def get_booking_id(self, obj):
        """Get booking ID"""
        return obj.booking.id
    
    def get_other_participant(self, obj):
        """Get the other participant in the chat"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other = obj.get_other_participant(request.user)
            if other:
                return UserSimpleSerializer(other).data
        return None
    
    def get_last_message(self, obj):
        """Get the last message in the chat"""
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content,
                'sender': last_message.sender.username,
                'timestamp': last_message.timestamp,
                'is_read': last_message.is_read
            }
        return None
    
    def get_unread_count(self, obj):
        """Get unread message count for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
