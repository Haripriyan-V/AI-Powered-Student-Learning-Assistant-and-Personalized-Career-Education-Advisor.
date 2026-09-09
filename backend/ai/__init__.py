"""
AI service package for DishaAI.
Provides clean LLM integration and prompt construction for DishaAI.
"""
from .service import AIService, ai_service, AIServiceError

__all__ = ['AIService', 'ai_service', 'AIServiceError']

