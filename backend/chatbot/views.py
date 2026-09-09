import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ai.service import ai_service, AIServiceError
from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer, ChatSessionListSerializer,
    ChatMessageSerializer, SendMessageSerializer,
)

logger = logging.getLogger(__name__)


def generate_ai_reply(user, message_text, session=None):
    """Fallback / compatibility helper delegating to real AIService."""
    return ai_service.generate_reply(user=user, session=session, new_message=message_text)


class ChatSessionViewSet(viewsets.ModelViewSet):
    """A student's own chat sessions with the AI assistant."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(student=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatSessionListSerializer
        return ChatSessionSerializer

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        POST /api/chatbot/sessions/{id}/send_message/
        Body: {"message": "..."}
        Stores the user's message, generates an AI reply, stores it too,
        and returns both messages.
        """
        session = self.get_object()
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data['message'].strip()

        if not text:
            return Response(
                {'error': 'Message content cannot be empty.', 'code': 'empty_input'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Store the user's message once
        user_message = ChatMessage.objects.create(
            session=session, sender=ChatMessage.Sender.USER, message=text,
        )

        try:
            ai_reply_text = ai_service.generate_reply(
                user=request.user,
                session=session,
                new_message=text,
                exclude_message_id=user_message.id,
            )

            # Validate non-empty plain text response
            if not isinstance(ai_reply_text, str) or not ai_reply_text.strip():
                logger.error("AI provider returned empty or invalid text response for session_id=%s", session.id)
                return Response(
                    {
                        'error': 'The AI assistant generated an empty response. Please try again.',
                        'code': 'empty_response',
                        'user_message': ChatMessageSerializer(user_message).data,
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            clean_reply = ai_reply_text.strip()
            ai_message = ChatMessage.objects.create(
                session=session, sender=ChatMessage.Sender.ASSISTANT, message=clean_reply,
            )
            session.save(update_fields=['updated_at'])  # bump updated_at via auto_now

            return Response(
                {
                    'user_message': ChatMessageSerializer(user_message).data,
                    'assistant_message': ChatMessageSerializer(ai_message).data,
                },
                status=status.HTTP_201_CREATED,
            )

        except AIServiceError as exc:
            logger.warning(
                "AI service failed for user_id=%s session_id=%s error=%s code=%s status=%d",
                request.user.id, session.id, exc.message, exc.code, exc.status_code
            )
            return Response(
                {
                    'error': exc.message,
                    'code': exc.code,
                    'user_message': ChatMessageSerializer(user_message).data,
                },
                status=exc.status_code,
            )
        except Exception as exc:
            logger.exception("Unexpected error generating AI reply for session_id=%s: %s", session.id, exc)
            return Response(
                {
                    'error': 'An unexpected server error occurred while contacting the AI assistant.',
                    'code': 'server_error',
                    'user_message': ChatMessageSerializer(user_message).data,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to individual messages (mainly for filtering/debugging)."""
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(session__student=self.request.user)
