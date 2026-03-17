"""
Chat System Permission Classes
Custom permission classes to control access to chat resources.
"""

from rest_framework import permissions


class IsChatParticipant(permissions.BasePermission):
    """
    Permission class to ensure only chat participants can access the chat.
    """
    message = "You don't have permission to access this chat."
    
    def has_object_permission(self, request, view, obj):
        """Check if user is a participant in the chat"""
        return obj.participants.filter(id=request.user.id).exists()


class IsBookingAccepted(permissions.BasePermission):
    """
    Permission class to ensure chat is only accessible for accepted bookings.
    """
    message = "Chat is only available after the booking is accepted."
    
    def has_object_permission(self, request, view, obj):
        """Check if booking is accepted"""
        return obj.booking.is_accepted


class IsMessageSenderOrRecipient(permissions.BasePermission):
    """
    Permission to allow message sender or recipient to access the message.
    """
    message = "You don't have permission to access this message."
    
    def has_object_permission(self, request, view, obj):
        """Check if user is sender or recipient of the message"""
        return obj.sender == request.user or obj.chat.participants.filter(id=request.user.id).exists()


class IsSender(permissions.BasePermission):
    """
    Permission to allow only the message sender to edit/delete the message.
    """
    message = "You can only edit or delete your own messages."
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the sender of the message"""
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.sender == request.user
