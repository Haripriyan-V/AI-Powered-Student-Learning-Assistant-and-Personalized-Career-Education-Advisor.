from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('id', 'session', 'sender', 'message', 'created_at')
        read_only_fields = ('sender', 'created_at')


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ('id', 'student', 'title', 'messages', 'last_message', 'created_at', 'updated_at')
        read_only_fields = ('student', 'created_at', 'updated_at')

    def get_last_message(self, obj):
        last = obj.messages.last()
        return ChatMessageSerializer(last).data if last else None


class ChatSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the session list (no nested messages)."""
    class Meta:
        model = ChatSession
        fields = ('id', 'title', 'created_at', 'updated_at')


class SendMessageSerializer(serializers.Serializer):
    message = serializers.CharField(allow_blank=False)
