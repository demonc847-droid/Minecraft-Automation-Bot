"""
AI Integration Module
====================

This module handles AI decision-making for Minecraft automation:
- Connect to multiple AI providers (Gemini, Groq, Ollama)
- Process game state and generate action decisions
- Prompt engineering for optimal AI responses
- Fallback logic when AI is unavailable

Components:
-----------
- DecisionMaker: Main interface for AI decisions
- Prompts: Prompt templates for various scenarios
- Fallback: Fallback strategies when AI fails

Usage:
------
    from ai import DecisionMaker
    
    dm = DecisionMaker(provider="gemini")
    action = dm.decide_action(game_state)
"""

from .decision_maker import (
    DecisionMaker,
    decide_action,
    configure_ai_provider,
    get_current_provider,
    switch_provider,
    get_action_with_fallback,
)
from .prompts import Prompts
from .fallback import FallbackStrategy

__all__ = [
    'DecisionMaker',
    'decide_action',
    'configure_ai_provider',
    'get_current_provider',
    'switch_provider',
    'get_action_with_fallback',
    'Prompts',
    'FallbackStrategy',
]