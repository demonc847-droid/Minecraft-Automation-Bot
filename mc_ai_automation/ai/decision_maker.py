"""
AI Decision Maker for Minecraft Automation
==========================================

This module provides the main interface for AI-powered decision-making.
Supports multiple AI providers with caching, rate limiting, and fallback logic.
"""

import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, Tuple
from functools import lru_cache
from threading import Lock

# Import prompts and fallback modules
from .prompts import Prompts
from .fallback import FallbackStrategy, get_fallback_action

# Configure logging
logger = logging.getLogger(__name__)

# Global configuration
_current_provider = "gemini"
_api_keys = {}
_provider_config = {}
_config_lock = Lock()

# Cache configuration
_cache_max_size = 100
_cache_ttl = 300  # 5 minutes
_action_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
_cache_lock = Lock()

# Rate limiting
_rate_limit_calls = 10  # Max calls per minute
_rate_limit_window = 60  # Seconds
_call_timestamps: list = []
_rate_lock = Lock()


class DecisionMaker:
    """
    Main AI decision-making interface.
    
    This class manages AI provider connections, prompt formatting,
    response parsing, and fallback handling.
    
    Usage:
        dm = DecisionMaker(provider="gemini", api_key="your-key")
        action = dm.decide_action(game_state)
    """
    
    def __init__(self, provider: str = "gemini", api_key: Optional[str] = None, 
                 model: Optional[str] = None, **kwargs):
        """
        Initialize the DecisionMaker.
        
        Args:
            provider: AI provider to use ("gemini", "groq", "ollama")
            api_key: API key for the provider (not required for ollama)
            model: Specific model to use (provider-dependent)
            **kwargs: Additional provider-specific configuration
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.provider_kwargs = kwargs
        
        # Initialize fallback handler
        self.fallback = FallbackStrategy(default_strategy="safe")
        
        # Track recent actions to provide context
        self.recent_actions: list = []
        self.max_recent_actions = 5
        
        # Initialize provider client
        self._client = None
        self._initialize_provider()
    
    def _initialize_provider(self) -> None:
        """Initialize the AI provider client."""
        try:
            if self.provider == "gemini":
                self._init_gemini()
            elif self.provider == "groq":
                self._init_groq()
            elif self.provider == "ollama":
                self._init_ollama()
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            logger.info(f"Initialized {self.provider} provider successfully")
        except ImportError as e:
            logger.warning(f"Failed to import {self.provider} library: {e}")
            logger.warning("AI provider will not be available - will use fallback")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider}: {e}")
            self._client = None
    
    def _init_gemini(self) -> None:
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            
            api_key = self.api_key or _api_keys.get("gemini")
            if not api_key:
                raise ValueError("Gemini API key not provided")
            
            genai.configure(api_key=api_key)
            
            model_name = self.model or "gemini-pro"
            self._client = genai.GenerativeModel(model_name)
            logger.info(f"Gemini initialized with model: {model_name}")
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    def _init_groq(self) -> None:
        """Initialize Groq client."""
        try:
            from groq import Groq
            
            api_key = self.api_key or _api_keys.get("groq")
            if not api_key:
                raise ValueError("Groq API key not provided")
            
            self._client = Groq(api_key=api_key)
            
            self.model = self.model or "llama3-8b-8192"
            logger.info(f"Groq initialized with model: {self.model}")
        except ImportError:
            raise ImportError("groq package not installed. Run: pip install groq")
    
    def _init_ollama(self) -> None:
        """Initialize Ollama client (uses HTTP requests)."""
        import requests
        
        ollama_url = self.provider_kwargs.get("url", "http://localhost:11434")
        self._client = ollama_url
        self.model = self.model or "llama2"
        
        # Test connection
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Ollama connected at {ollama_url}")
            else:
                logger.warning(f"Ollama returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to Ollama: {e}")
    
    def decide_action(self, game_state: Dict[str, Any], phase: str = "foundation",
                     focus: str = "General progression") -> Dict[str, Any]:
        """
        Decide on an action based on the current game state.
        
        Args:
            game_state: Complete game state dictionary
            phase: Current game phase
            focus: Current focus within the phase
            
        Returns:
            Action dictionary with action, target, params, reasoning, priority, timeout
        """
        # Check cache first
        cache_key = self._generate_cache_key(game_state, phase, focus)
        cached_action = self._get_cached_action(cache_key)
        if cached_action:
            logger.debug("Using cached action")
            return cached_action
        
        # Check rate limiting
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded, using fallback")
            return self.get_action_with_fallback(game_state, "safe")
        
        try:
            # Build prompt
            recent_actions_str = self._format_recent_actions()
            prompt = Prompts.build_full_prompt(
                phase=phase,
                game_state=game_state,
                recent_actions=recent_actions_str,
                focus=focus
            )
            
            # Call AI provider
            system_prompt = Prompts.get_system_prompt()
            response = self._call_ai(system_prompt, prompt)
            
            # Parse response
            action = self._parse_response(response)
            
            # Validate action
            action = self._validate_action(action, game_state)
            
            # Add to recent actions
            self._add_recent_action(action)
            
            # Cache the result
            self._cache_action(cache_key, action)
            
            return action
            
        except Exception as e:
            logger.error(f"AI decision failed: {e}")
            return self.get_action_with_fallback(game_state, "safe")
    
    def _call_ai(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the configured AI provider.
        
        Args:
            system_prompt: System/instruction prompt
            user_prompt: User/query prompt
            
        Returns:
            AI response text
            
        Raises:
            Exception: If AI call fails
        """
        self._record_call()  # For rate limiting
        
        if self.provider == "gemini":
            return self._call_gemini(system_prompt, user_prompt)
        elif self.provider == "groq":
            return self._call_groq(system_prompt, user_prompt)
        elif self.provider == "ollama":
            return self._call_ollama(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Google Gemini API.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            
        Returns:
            Response text
        """
        if not self._client:
            raise RuntimeError("Gemini client not initialized")
        
        # Combine prompts for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = self._client.generate_content(full_prompt)
        
        if response.text:
            return response.text
        else:
            raise RuntimeError("Empty response from Gemini")
    
    def _call_groq(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Groq API.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            
        Returns:
            Response text
        """
        if not self._client:
            raise RuntimeError("Groq client not initialized")
        
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        
        if response.choices and response.choices[0].message:
            return response.choices[0].message.content
        else:
            raise RuntimeError("Empty response from Groq")
    
    def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Ollama API via HTTP.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            
        Returns:
            Response text
        """
        import requests
        
        if not self._client:
            raise RuntimeError("Ollama client not initialized")
        
        response = requests.post(
            f"{self._client}/api/generate",
            json={
                "model": self.model,
                "system": system_prompt,
                "prompt": user_prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "")
        else:
            raise RuntimeError(f"Ollama returned status {response.status_code}")
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI response into an action dictionary.
        
        Args:
            response: Raw AI response text
            
        Returns:
            Action dictionary
            
        Raises:
            ValueError: If response cannot be parsed
        """
        # Try to extract JSON from response
        response = response.strip()
        
        # Handle markdown code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end > start:
                response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                response = response[start:end].strip()
        
        # Try to find JSON object in response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            try:
                action = json.loads(json_str)
                return action
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                raise ValueError(f"Invalid JSON in response: {e}")
        
        raise ValueError("No JSON object found in response")
    
    def _validate_action(self, action: Dict[str, Any], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize an action dictionary.
        
        Args:
            action: Raw action from AI
            game_state: Current game state
            
        Returns:
            Validated action dictionary
        """
        # Ensure required fields
        if "action" not in action:
            action["action"] = "none"
        
        # Set defaults for optional fields
        action.setdefault("target", None)
        action.setdefault("params", {})
        action.setdefault("reasoning", "No reasoning provided")
        action.setdefault("priority", 5)
        action.setdefault("timeout", 10.0)
        
        # Validate action type
        valid_actions = [
            "move_to", "look_at", "jump", "sneak",
            "attack", "attack_entity", "defend",
            "use_item", "place_block", "break_block", "interact",
            "select_slot", "open_inventory", "close_inventory", "craft_item", "equip_item", "drop_item",
            "wait", "explore", "flee", "none"
        ]
        
        if action["action"] not in valid_actions:
            logger.warning(f"Invalid action type: {action['action']}, using 'none'")
            action["action"] = "none"
        
        # Validate priority range
        if not (1 <= action["priority"] <= 10):
            action["priority"] = max(1, min(10, action["priority"]))
        
        # Validate timeout
        if action["timeout"] <= 0:
            action["timeout"] = 10.0
        
        return action
    
    def get_action_with_fallback(self, game_state: Dict[str, Any], 
                                fallback_strategy: str = "safe") -> Dict[str, Any]:
        """
        Get an action with automatic fallback if AI fails.
        
        Args:
            game_state: Current game state
            fallback_strategy: Fallback strategy to use
            
        Returns:
            Action dictionary
        """
        try:
            return self.decide_action(game_state)
        except Exception as e:
            logger.warning(f"AI decision failed, using fallback: {e}")
            return self.fallback.get_fallback_action(game_state, fallback_strategy)
    
    def _generate_cache_key(self, game_state: Dict[str, Any], 
                           phase: str, focus: str) -> str:
        """
        Generate a cache key for the game state.
        
        Args:
            game_state: Game state dictionary
            phase: Current phase
            focus: Current focus
            
        Returns:
            Cache key string
        """
        # Create a simplified version of game state for caching
        cache_data = {
            "phase": phase,
            "focus": focus,
            "health": game_state.get("player", {}).get("health"),
            "hunger": game_state.get("player", {}).get("hunger"),
            "position": game_state.get("player", {}).get("position"),
            "nearby_entities": len(game_state.get("world", {}).get("nearby_entities", [])),
            "time": game_state.get("world", {}).get("time_of_day")
        }
        
        # Generate hash
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_cached_action(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get an action from cache if available and not expired.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached action or None
        """
        with _cache_lock:
            if cache_key in _action_cache:
                action, timestamp = _action_cache[cache_key]
                if time.time() - timestamp < _cache_ttl:
                    return action
                else:
                    # Expired
                    del _action_cache[cache_key]
        return None
    
    def _cache_action(self, cache_key: str, action: Dict[str, Any]) -> None:
        """
        Cache an action.
        
        Args:
            cache_key: Cache key
            action: Action to cache
        """
        with _cache_lock:
            # Clean old entries if cache is full
            if len(_action_cache) >= _cache_max_size:
                oldest_key = min(_action_cache.keys(), 
                                key=lambda k: _action_cache[k][1])
                del _action_cache[oldest_key]
            
            _action_cache[cache_key] = (action, time.time())
    
    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.
        
        Returns:
            True if within limits, False otherwise
        """
        with _rate_lock:
            current_time = time.time()
            
            # Remove old timestamps
            global _call_timestamps
            _call_timestamps = [t for t in _call_timestamps 
                               if current_time - t < _rate_limit_window]
            
            # Check limit
            if len(_call_timestamps) >= _rate_limit_calls:
                return False
            
            return True
    
    def _record_call(self) -> None:
        """Record a call timestamp for rate limiting."""
        with _rate_lock:
            _call_timestamps.append(time.time())
    
    def _format_recent_actions(self) -> str:
        """
        Format recent actions for context.
        
        Returns:
            Formatted string of recent actions
        """
        if not self.recent_actions:
            return "None"
        
        formatted = []
        for i, action in enumerate(self.recent_actions[-3:], 1):
            action_type = action.get("action", "unknown")
            reasoning = action.get("reasoning", "No reasoning")
            formatted.append(f"{i}. {action_type}: {reasoning}")
        
        return "\n".join(formatted)
    
    def _add_recent_action(self, action: Dict[str, Any]) -> None:
        """
        Add an action to recent history.
        
        Args:
            action: Action to add
        """
        self.recent_actions.append(action)
        if len(self.recent_actions) > self.max_recent_actions:
            self.recent_actions.pop(0)
    
    def clear_cache(self) -> None:
        """Clear the action cache."""
        with _cache_lock:
            _action_cache.clear()
        logger.info("Action cache cleared")
    
    def clear_recent_actions(self) -> None:
        """Clear recent action history."""
        self.recent_actions.clear()


# Module-level functions for easy access
_default_maker: Optional[DecisionMaker] = None
_maker_lock = Lock()


def configure_ai_provider(provider: str, api_key: Optional[str] = None, **kwargs) -> None:
    """
    Configure the default AI provider.
    
    Args:
        provider: Provider name ("gemini", "groq", "ollama")
        api_key: API key for the provider
        **kwargs: Additional provider configuration
    """
    global _current_provider, _api_keys, _provider_config
    
    with _config_lock:
        _current_provider = provider.lower()
        if api_key:
            _api_keys[provider.lower()] = api_key
        _provider_config.update(kwargs)
    
    # Reset default maker to use new configuration
    global _default_maker
    with _maker_lock:
        _default_maker = None
    
    logger.info(f"Configured AI provider: {provider}")


def get_current_provider() -> str:
    """
    Get the currently configured AI provider.
    
    Returns:
        Provider name string
    """
    return _current_provider


def switch_provider(provider: str) -> None:
    """
    Switch to a different AI provider.
    
    Args:
        provider: Provider name to switch to
    """
    global _current_provider, _default_maker
    
    with _config_lock:
        _current_provider = provider.lower()
    
    with _maker_lock:
        _default_maker = None
    
    logger.info(f"Switched to provider: {provider}")


def _get_default_maker() -> DecisionMaker:
    """
    Get or create the default DecisionMaker instance.
    
    Returns:
        Default DecisionMaker instance
    """
    global _default_maker
    
    with _maker_lock:
        if _default_maker is None:
            api_key = _api_keys.get(_current_provider)
            _default_maker = DecisionMaker(
                provider=_current_provider,
                api_key=api_key,
                **_provider_config
            )
    
    return _default_maker


def decide_action(game_state: Dict[str, Any], phase: str = "foundation",
                 focus: str = "General progression") -> Dict[str, Any]:
    """
    Decide on an action using the default AI provider.
    
    Args:
        game_state: Complete game state dictionary
        phase: Current game phase
        focus: Current focus within the phase
        
    Returns:
        Action dictionary
    """
    maker = _get_default_maker()
    return maker.decide_action(game_state, phase, focus)


def get_action_with_fallback(game_state: Dict[str, Any], 
                            fallback_strategy: str = "safe") -> Dict[str, Any]:
    """
    Get an action with automatic fallback if AI fails.
    
    Args:
        game_state: Current game state
        fallback_strategy: Fallback strategy ("safe", "explore", "random")
        
    Returns:
        Action dictionary
    """
    maker = _get_default_maker()
    return maker.get_action_with_fallback(game_state, fallback_strategy)