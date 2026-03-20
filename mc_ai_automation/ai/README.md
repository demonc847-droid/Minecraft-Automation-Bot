# AI Integration Module

This module provides AI-powered decision-making for Minecraft automation. It supports multiple AI providers and includes fallback strategies for when AI is unavailable.

## Features

- **Multiple AI Providers**: Support for Google Gemini, Groq, and Ollama
- **Prompt Engineering**: Pre-built prompts for various game scenarios
- **Fallback Strategies**: Safe, explore, and random strategies when AI fails
- **Caching**: Action caching to reduce API calls
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Action Validation**: Validates and normalizes AI responses

## Installation

```bash
# Install required dependencies
pip install google-generativeai  # For Gemini
pip install groq                 # For Groq
pip install requests             # For Ollama (HTTP API)

# Or install all at once
pip install -r requirements.txt
```

## Quick Start

```python
from ai import DecisionMaker, configure_ai_provider

# Configure AI provider
configure_ai_provider("gemini", api_key="your-api-key")

# Create decision maker
dm = DecisionMaker(provider="gemini", api_key="your-api-key")

# Define game state (see INTERFACES.md for full specification)
game_state = {
    "player": {
        "position": {"x": 100.5, "y": 64.0, "z": -200.3},
        "health": 18.0,
        "hunger": 15.0,
        "is_on_ground": True
    },
    "inventory": {
        "selected_slot": 0,
        "items": [
            {"slot": 0, "item_id": "minecraft:diamond_sword", "count": 1}
        ]
    },
    "world": {
        "time_of_day": 6000,
        "nearby_entities": []
    }
}

# Get action decision
action = dm.decide_action(game_state, phase="foundation", focus="Collect wood")
print(action)
# Output: {"action": "move_to", "target": [...], "params": {...}, "reasoning": "..."}
```

## Usage

### Basic Usage

```python
from ai import decide_action, configure_ai_provider

# Configure provider
configure_ai_provider("gemini", api_key="your-key")

# Get action (uses default provider)
action = decide_action(game_state, phase="foundation")
```

### With Fallback

```python
from ai import get_action_with_fallback

# Get action with automatic fallback if AI fails
action = get_action_with_fallback(game_state, fallback_strategy="safe")
```

### Switching Providers

```python
from ai import switch_provider, get_current_provider

# Switch to Groq
switch_provider("groq")
print(get_current_provider())  # Output: "groq"

# Switch to Ollama (local)
switch_provider("ollama")
```

### Using Fallback Directly

```python
from ai import FallbackStrategy

fallback = FallbackStrategy(default_strategy="safe")
action = fallback.get_fallback_action(game_state, strategy="explore")
```

### Using Prompts

```python
from ai import Prompts

# Get system prompt
system_prompt = Prompts.get_system_prompt()

# Get phase-specific prompt
phase_prompt = Prompts.get_phase_prompt("foundation", focus="Find wood")

# Build complete prompt
full_prompt = Prompts.build_full_prompt(
    phase="foundation",
    game_state=game_state,
    recent_actions="None",
    focus="Collect wood"
)
```

## AI Providers

### Google Gemini

```python
from ai import DecisionMaker

dm = DecisionMaker(
    provider="gemini",
    api_key="your-gemini-api-key",
    model="gemini-pro"  # Optional, defaults to gemini-pro
)
```

**Get API Key**: https://makersuite.google.com/app/apikey

### Groq

```python
from ai import DecisionMaker

dm = DecisionMaker(
    provider="groq",
    api_key="your-groq-api-key",
    model="llama3-8b-8192"  # Optional
)
```

**Get API Key**: https://console.groq.com/keys

### Ollama (Local)

```python
from ai import DecisionMaker

dm = DecisionMaker(
    provider="ollama",
    url="http://localhost:11434",  # Optional, defaults to localhost
    model="llama2"  # Optional
)
```

**Install Ollama**: https://ollama.ai

## Fallback Strategies

When AI is unavailable or fails, the module uses fallback strategies:

### Safe Strategy (Default)
Prioritizes survival:
1. Eat food if health/hunger is low
2. Defend if hostile nearby
3. Retreat from danger
4. Look around safely

### Explore Strategy
Gathers information:
1. Look around in different directions
2. Move to explore new areas
3. Jump to get better view

### Random Strategy
Picks random valid actions:
1. Wait randomly
2. Jump
3. Look at random direction
4. Move randomly

## Prompt Templates

The module includes prompts for various scenarios:

- **SYSTEM_PROMPT**: Base system prompt for Minecraft AI
- **ACTION_DECISION_PROMPT**: Template for deciding actions
- **PHASE_PROMPTS**: Prompts for each game phase (foundation, resources, tools, mining, nether, stronghold, dragon)
- **EMERGENCY_PROMPT**: For critical situations (low health, threats)
- **EXPLORATION_PROMPT**: When unsure what to do
- **CRAFTING_PROMPT**: For item creation decisions
- **COMBAT_PROMPT**: For combat situations
- **GATHERING_PROMPT**: For resource gathering

## Caching

Actions are cached for 5 minutes to reduce API calls:

```python
# Cache is automatic, but you can clear it:
dm.clear_cache()
```

## Rate Limiting

Built-in rate limiting prevents API abuse:
- Max 10 calls per minute
- Automatic fallback when rate limit is exceeded

## Testing

Run the test suite to verify functionality:

```bash
python3 tests/test_ai_integration.py
```

## Troubleshooting

### AI Provider Not Available

If you see "AI provider will not be available - will use fallback":
1. Install the required package: `pip install google-generativeai` or `pip install groq`
2. Verify your API key is correct
3. Check your internet connection

### Rate Limit Exceeded

If you see "Rate limit exceeded":
1. Wait 60 seconds for the rate limit window to reset
2. Reduce the frequency of `decide_action()` calls
3. Use caching (enabled by default)

### Invalid Action Type

If AI returns an invalid action type, it will be corrected to "none" automatically.

## Module Structure

```
ai/
├── __init__.py          # Module exports
├── prompts.py           # Prompt templates
├── fallback.py          # Fallback strategies
├── decision_maker.py    # Main AI integration
└── README.md           # This file
```

## API Reference

### DecisionMaker Class

```python
class DecisionMaker:
    def __init__(provider: str, api_key: str = None, model: str = None, **kwargs)
    def decide_action(game_state: dict, phase: str = "foundation", focus: str = "General progression") -> dict
    def get_action_with_fallback(game_state: dict, fallback_strategy: str = "safe") -> dict
    def clear_cache() -> None
    def clear_recent_actions() -> None
```

### Module Functions

```python
def configure_ai_provider(provider: str, api_key: str = None, **kwargs) -> None
def get_current_provider() -> str
def switch_provider(provider: str) -> None
def decide_action(game_state: dict, phase: str = "foundation", focus: str = "General progression") -> dict
def get_action_with_fallback(game_state: dict, fallback_strategy: str = "safe") -> dict
```

### Prompts Class

```python
class Prompts:
    @staticmethod
    def format_prompt(template: str, **kwargs) -> str
    @staticmethod
    def get_system_prompt() -> str
    @staticmethod
    def get_phase_prompt(phase: str, focus: str = "General progression") -> str
    @staticmethod
    def get_emergency_prompt(health: float, hunger: float, threats: str, position: str) -> str
    @staticmethod
    def build_full_prompt(phase: str, game_state: dict, recent_actions: str = "None", focus: str = "General progression") -> str
```

### FallbackStrategy Class

```python
class FallbackStrategy:
    def __init__(default_strategy: str = "safe")
    def get_fallback_action(game_state: dict, strategy: str = None) -> dict
    def get_available_strategies() -> list
```

## License

Part of the Minecraft AI Automation project.