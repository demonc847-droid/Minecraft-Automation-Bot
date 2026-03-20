# Minecraft AI Automation - Interfaces Definition

This document defines the interfaces between all components of the Minecraft AI Automation system. All agents must adhere to these interface definitions to ensure compatibility.

## Table of Contents
1. [GameState Dictionary](#gamestate-dictionary)
2. [Action Dictionary](#action-dictionary)
3. [Core Input Functions](#core-input-functions)
4. [AI Decision Functions](#ai-decision-functions)
5. [Phase Interface](#phase-interface)

---

## GameState Dictionary

The `GameState` object represents the current state of the Minecraft game as read from memory.

```python
GameState = {
    "player": {
        "position": {
            "x": float,          # Player X coordinate
            "y": float,          # Player Y coordinate (feet level)
            "z": float           # Player Z coordinate
        },
        "velocity": {
            "x": float,
            "y": float,
            "z": float
        },
        "health": float,         # 0.0 to 20.0
        "hunger": float,         # 0.0 to 20.0
        "saturation": float,     # 0.0 to 20.0
        "experience_level": int,
        "experience_progress": float,  # 0.0 to 1.0
        "yaw": float,            # Horizontal rotation in degrees
        "pitch": float,          # Vertical rotation in degrees
        "is_on_ground": bool,
        "is_in_water": bool,
        "is_in_lava": bool,
        "is_sleeping": bool,
        "dimension": str         # "overworld", "nether", "end"
    },
    "inventory": {
        "selected_slot": int,    # 0-8 (hotbar)
        "items": [
            {
                "slot": int,     # 0-35 (inventory slots)
                "item_id": str,  # e.g., "minecraft:diamond_sword"
                "count": int,
                "damage": int,   # For tools/weapons
                "nbt": dict      # Additional item data
            }
        ],
        "armor": {
            "head": dict,        # Item dict or None
            "chest": dict,
            "legs": dict,
            "feet": dict
        },
        "offhand": dict          # Item dict or None
    },
    "world": {
        "time_of_day": int,      # 0-24000 (ticks)
        "day_count": int,
        "is_raining": bool,
        "is_thundering": bool,
        "difficulty": str,       # "peaceful", "easy", "normal", "hard"
        "game_mode": str,        # "survival", "creative", "adventure", "spectator"
        "seed": int,
        "spawn_point": {
            "x": float,
            "y": float,
            "z": float
        },
        "looking_at": {
            "block_type": str,   # e.g., "minecraft:stone"
            "position": {
                "x": int,
                "y": int,
                "z": int
            },
            "face": str          # "north", "south", "east", "west", "up", "down"
        },
        "nearby_entities": [
            {
                "type": str,     # e.g., "minecraft:zombie", "minecraft:pig"
                "id": int,       # Entity ID
                "position": {
                    "x": float,
                    "y": float,
                    "z": float
                },
                "health": float,
                "is_hostile": bool,
                "distance": float  # Distance from player
            }
        ],
        "nearby_blocks": [
            {
                "type": str,
                "position": {
                    "x": int,
                    "y": int,
                    "z": int
                }
            }
        ]
    },
    "timestamp": float           # Unix timestamp when state was read
}
```

### Example GameState:
```python
{
    "player": {
        "position": {"x": 100.5, "y": 64.0, "z": -200.3},
        "velocity": {"x": 0.0, "y": -0.0784, "z": 0.0},
        "health": 20.0,
        "hunger": 18.0,
        "saturation": 5.0,
        "experience_level": 5,
        "experience_progress": 0.45,
        "yaw": 90.0,
        "pitch": 15.0,
        "is_on_ground": True,
        "is_in_water": False,
        "is_in_lava": False,
        "is_sleeping": False,
        "dimension": "overworld"
    },
    "inventory": {
        "selected_slot": 0,
        "items": [
            {"slot": 0, "item_id": "minecraft:diamond_sword", "count": 1, "damage": 0, "nbt": {}},
            {"slot": 1, "item_id": "minecraft:diamond_pickaxe", "count": 1, "damage": 150, "nbt": {}}
        ],
        "armor": {"head": None, "chest": None, "legs": None, "feet": None},
        "offhand": None
    },
    "world": {
        "time_of_day": 6000,
        "day_count": 1,
        "is_raining": False,
        "is_thundering": False,
        "difficulty": "normal",
        "game_mode": "survival",
        "seed": 123456789,
        "spawn_point": {"x": 0.0, "y": 64.0, "z": 0.0},
        "looking_at": {
            "block_type": "minecraft:stone",
            "position": {"x": 100, "y": 63, "z": -201},
            "face": "north"
        },
        "nearby_entities": [
            {
                "type": "minecraft:pig",
                "id": 123,
                "position": {"x": 105.0, "y": 64.0, "z": -195.0},
                "health": 10.0,
                "is_hostile": False,
                "distance": 5.8
            }
        ],
        "nearby_blocks": []
    },
    "timestamp": 1710912345.678
}
```

---

## Action Dictionary

The `Action` dictionary represents a decision made by the AI to be executed by the action system.

```python
Action = {
    "action": str,               # Action name (see list below)
    "target": [float, float, float] | None,  # Target coordinates [x, y, z]
    "params": {                  # Action-specific parameters
        # Varies by action type
    },
    "reasoning": str,            # AI's explanation for choosing this action
    "priority": int,             # 1-10, higher = more important
    "timeout": float             # Maximum time in seconds to complete action
}
```

### Supported Actions:

#### Movement Actions:
```python
{"action": "move_to", "target": [x, y, z], "params": {"speed": "walk"|"sprint"}}
{"action": "look_at", "target": [x, y, z], "params": {}}
{"action": "jump", "target": None, "params": {}}
{"action": "sneak", "target": None, "params": {"duration": float}}
```

#### Combat Actions:
```python
{"action": "attack", "target": None, "params": {"hold_ticks": int}}
{"action": "attack_entity", "target": [x, y, z], "params": {"entity_type": str}}
{"action": "defend", "target": None, "params": {"duration": float}}
```

#### Interaction Actions:
```python
{"action": "use_item", "target": None, "params": {"hold_ticks": int}}
{"action": "place_block", "target": [x, y, z], "params": {"block_type": str}}
{"action": "break_block", "target": [x, y, z], "params": {"hold_ticks": int}}
{"action": "interact", "target": [x, y, z], "params": {}}
```

#### Inventory Actions:
```python
{"action": "select_slot", "target": None, "params": {"slot": int}}
{"action": "open_inventory", "target": None, "params": {}}
{"action": "close_inventory", "target": None, "params": {}}
{"action": "craft_item", "target": None, "params": {"item_id": str, "count": int}}
{"action": "equip_item", "target": None, "params": {"item_id": str}}
{"action": "drop_item", "target": None, "params": {"slot": int, "all": bool}}
```

#### Special Actions:
```python
{"action": "wait", "target": None, "params": {"duration": float}}
{"action": "explore", "target": None, "params": {"direction": str, "distance": float}}
{"action": "flee", "target": [x, y, z], "params": {"speed": "sprint"}}
{"action": "none", "target": None, "params": {}}  # Do nothing this tick
```

### Example Actions:
```python
# Move to coordinates
{
    "action": "move_to",
    "target": [100.0, 64.0, -200.0],
    "params": {"speed": "sprint"},
    "reasoning": "Moving towards village to trade",
    "priority": 5,
    "timeout": 30.0
}

# Attack nearby enemy
{
    "action": "attack",
    "target": None,
    "params": {"hold_ticks": 10},
    "reasoning": "Zombie detected within attack range",
    "priority": 8,
    "timeout": 2.0
}

# Craft pickaxe
{
    "action": "craft_item",
    "target": None,
    "params": {"item_id": "minecraft:iron_pickaxe", "count": 1},
    "reasoning": "Current pickaxe durability is low",
    "priority": 6,
    "timeout": 10.0
}
```

---

## Core Input Functions

These functions are implemented by Agent 1 in the `core.input_simulator` module and are used by all other agents.

### Movement Functions:

```python
def move_to(x: float, z: float) -> None:
    """
    Move the player to the specified X, Z coordinates.
    Uses pathfinding if obstacles are detected.
    
    Args:
        x: Target X coordinate
        z: Target Z coordinate
    """
    pass

def look_at(yaw: float, pitch: float) -> None:
    """
    Rotate the player's view to the specified angles.
    
    Args:
        yaw: Horizontal rotation in degrees (-180 to 180)
        pitch: Vertical rotation in degrees (-90 to 90)
    """
    pass

def look_at_position(x: float, y: float, z: float) -> None:
    """
    Rotate the player's view to look at a specific position.
    
    Args:
        x: Target X coordinate
        y: Target Y coordinate
        z: Target Z coordinate
    """
    pass

def jump() -> None:
    """
    Make the player jump.
    """
    pass

def sneak(duration: float = 0.5) -> None:
    """
    Toggle sneak mode.
    
    Args:
        duration: How long to hold sneak (0 for toggle)
    """
    pass
```

### Combat Functions:

```python
def attack(hold_ticks: int = 10) -> None:
    """
    Perform an attack action.
    
    Args:
        hold_ticks: Number of ticks to hold the attack button (1 tick = 50ms)
    """
    pass

def block_with_shield(duration: float = 1.0) -> None:
    """
    Block with shield if equipped.
    
    Args:
        duration: How long to hold block
    """
    pass
```

### Interaction Functions:

```python
def use_item(hold_ticks: int = 10) -> None:
    """
    Use the item in the main hand (right click).
    
    Args:
        hold_ticks: Number of ticks to hold use button
    """
    pass

def place_block() -> None:
    """
    Place a block from the selected slot.
    """
    pass

def break_block(hold_ticks: int = 20) -> None:
    """
    Break the block being looked at.
    
    Args:
        hold_ticks: Number of ticks to hold break button
    """
    pass

def interact() -> None:
    """
    Interact with block/entity being looked at (right click without item).
    """
    pass
```

### Inventory Functions:

```python
def open_inventory() -> None:
    """
    Open the player's inventory.
    """
    pass

def close_inventory() -> None:
    """
    Close the player's inventory.
    """
    pass

def select_slot(slot: int) -> None:
    """
    Select a hotbar slot.
    
    Args:
        slot: Slot number (0-8)
    """
    pass

def drop_item(all: bool = False) -> None:
    """
    Drop the item in the selected slot.
    
    Args:
        all: If True, drop entire stack
    """
    pass

def move_item(from_slot: int, to_slot: int) -> None:
    """
    Move an item between inventory slots.
    Must have inventory open.
    
    Args:
        from_slot: Source slot number
        to_slot: Destination slot number
    """
    pass
```

---

## AI Decision Functions

These functions are implemented by Agent 2 in the `ai.decision_maker` module.

```python
def decide_action(game_state: dict) -> dict:
    """
    Given the current game state, decide on an action to take.
    
    Args:
        game_state: GameState dictionary (see above)
    
    Returns:
        Action dictionary (see above)
    """
    pass

def configure_ai_provider(provider: str, api_key: str = None, **kwargs) -> None:
    """
    Configure which AI provider to use.
    
    Args:
        provider: One of "gemini", "groq", "ollama"
        api_key: API key (not required for ollama)
        **kwargs: Additional provider-specific options
    """
    pass

def get_current_provider() -> str:
    """
    Get the currently configured AI provider.
    
    Returns:
        Provider name string
    """
    pass

def switch_provider(provider: str) -> None:
    """
    Switch to a different AI provider.
    
    Args:
        provider: Provider name to switch to
    """
    pass

def get_action_with_fallback(game_state: dict, fallback_strategy: str = "safe") -> dict:
    """
    Get an action decision with automatic fallback if AI fails.
    
    Args:
        game_state: GameState dictionary
        fallback_strategy: "safe", "explore", or "random"
    
    Returns:
        Action dictionary
    """
    pass
```

---

## Phase Interface

All phase scripts must implement this interface.

```python
from abc import ABC, abstractmethod

class Phase(ABC):
    """Base class for all game phases."""
    
    def __init__(self, game_state_provider, action_decider):
        """
        Initialize the phase.
        
        Args:
            game_state_provider: Callable that returns GameState dict
            action_decider: Callable (game_state) -> Action dict
        """
        self.get_state = game_state_provider
        self.decide = action_decider
    
    @abstractmethod
    def is_complete(self) -> bool:
        """
        Check if this phase's objectives have been met.
        
        Returns:
            True if phase is complete, False otherwise
        """
        pass
    
    @abstractmethod
    def get_objectives(self) -> list:
        """
        Get list of objectives for this phase.
        
        Returns:
            List of objective strings
        """
        pass
    
    def execute(self) -> dict:
        """
        Execute one tick of this phase.
        
        Returns:
            Action to perform
        """
        state = self.get_state()
        action = self.decide(state)
        return action
    
    def perform_action(self, action: dict) -> None:
        """
        Execute the specified action.
        
        Args:
            action: Action dictionary
        """
        # Route to appropriate action module based on action["action"]
        pass
```

### Phase Implementations:

```python
# Phase 1: Foundation - Basic survival
class Phase1_Foundation(Phase):
    def is_complete(self) -> bool:
        # Complete when: have wooden tools, basic shelter, food source
        pass

# Phase 2: Resources - Gather materials
class Phase2_Resources(Phase):
    def is_complete(self) -> bool:
        # Complete when: have stone tools, enough wood, coal torches
        pass

# Phase 3: Tools - Craft better equipment
class Phase3_Tools(Phase):
    def is_complete(self) -> bool:
        # Complete when: have iron tools and armor
        pass

# Phase 4: Mining - Deep underground
class Phase4_Mining(Phase):
    def is_complete(self) -> bool:
        # Complete when: have diamonds, obsidian
        pass

# Phase 5: Nether - Enter and progress
class Phase5_Nether(Phase):
    def is_complete(self) -> bool:
        # Complete when: have blaze rods, ender pearls
        pass

# Phase 6: Stronghold - Find and enter End
class Phase6_Stronghold(Phase):
    def is_complete(self) -> bool:
        # Complete when: entered End portal
        pass

# Phase 7: Dragon - Defeat Ender Dragon
class Phase7_Dragon(Phase):
    def is_complete(self) -> bool:
        # Complete when: dragon defeated
        pass
```

---

## Module Import Structure

For reference, here is how modules should import from each other:

```python
# Agent 1 (Core) - No dependencies on other agents
# core/memory_reader.py
# core/player_state.py
# core/inventory_state.py
# core/world_state.py
# core/input_simulator.py

# Agent 2 (AI) - Depends on: Core (for state types)
# ai/decision_maker.py
# ai/prompts.py
# ai/fallback.py

# Agent 3 (Actions) - Depends on: Core, AI
# actions/movement.py
# actions/combat.py
# actions/gathering.py
# actions/inventory.py
# phases/phase1_foundation.py
# phases/phase2_resources.py
# phases/phase3_tools.py
# phases/phase4_mining.py
# phases/phase5_nether.py
# phases/phase6_stronghold.py
# phases/phase7_dragon.py

# Agent 4 (Integration) - Depends on: All
# main.py
# tests/
```

---

## Notes

- All coordinates are in Minecraft's coordinate system
- All angles are in degrees
- Time is measured in ticks (1 second = 20 ticks)
- Memory offsets in `offsets.json` must be updated with actual values from the Minecraft version being used
- All agents should work on separate Git branches and coordinate via pull requests