"""
Prompt Templates for Minecraft AI Automation
============================================

This module provides prompt templates for various game scenarios.
Templates use Python string formatting with placeholders for dynamic content.
"""

from typing import Dict, Any


class Prompts:
    """
    Prompt templates for AI decision-making in Minecraft.
    
    Templates use {placeholder} syntax for dynamic content injection.
    Use format_prompt() method to fill in placeholders.
    """
    
    # Base system prompt that sets the AI's role and behavior
    SYSTEM_PROMPT = """You are an expert Minecraft AI assistant controlling a player in survival mode. Your goal is to help the player progress through the game efficiently.

You will receive a game state dictionary containing information about the player's position, health, inventory, and surroundings.

You must respond with a JSON object containing:
- "action": The action to take (see list below)
- "target": [x, y, z] coordinates if applicable, or null
- "params": Additional parameters for the action
- "reasoning": Brief explanation of why you chose this action
- "priority": 1-10 scale (higher = more urgent)

Available actions:
- move_to: Move to coordinates
- look_at: Look at coordinates
- jump: Jump
- attack: Attack with weapon
- defend: Block with shield
- use_item: Use item in hand
- place_block: Place a block
- break_block: Break the block being looked at
- select_slot: Select a hotbar slot
- craft_item: Craft an item
- equip_item: Equip an item
- explore: Explore the area
- flee: Run away from danger
- wait: Do nothing for a duration
- none: Do nothing this tick

Always choose actions that help progress the game. Prioritize survival when health is low."""
    
    # Template for general action decisions
    ACTION_DECISION_PROMPT = """## Current Game State:
{game_state}

## Current Phase: {phase}
## Phase Objectives: {objectives}

## Recent Actions:
{recent_actions}

Based on this game state, what action should the player take next?

Remember:
- Check health and hunger levels
- Consider nearby threats
- Work towards phase objectives
- Use appropriate tools for the task

Respond with a JSON action object."""
    
    # Phase-specific prompts
    PHASE_PROMPTS = {
        "foundation": """## Phase 1: Foundation
**Goal**: Establish basic survival - wooden tools, shelter, and food source.

**Priorities**:
1. Find trees and collect wood
2. Craft wooden tools (pickaxe, sword)
3. Find or build basic shelter
4. Locate food source (animals, crops)

**Current Focus**: {focus}

Adapt your actions based on what has already been accomplished.""",
        
        "resources": """## Phase 2: Resources
**Goal**: Gather materials for progression - stone tools, coal, torches.

**Priorities**:
1. Mine stone for better tools
2. Craft stone tools (pickaxe, sword, axe)
3. Find coal for torches
4. Build torches for lighting
5. Continue gathering wood

**Current Focus**: {focus}

Balance mining with surface gathering.""",
        
        "tools": """## Phase 3: Tools
**Goal**: Obtain iron tools and armor.

**Priorities**:
1. Mine iron ore (Y level 16-64)
2. Build and fuel a furnace
3. Smelt iron ingots
4. Craft iron tools and armor
5. Build a more permanent base

**Current Focus**: {focus}

Iron is essential for mining diamonds later.""",
        
        "mining": """## Phase 4: Mining
**Goal**: Find diamonds and obsidian.

**Priorities**:
1. Mine at Y level -59 for diamonds
2. Collect at least 5 diamonds
3. Craft diamond pickaxe
4. Find and mine obsidian
5. Mine ancient debris (optional)

**Current Focus**: {focus}

Be careful of lava when mining deep!""",
        
        "nether": """## Phase 5: Nether
**Goal**: Progress through the Nether.

**Priorities**:
1. Build Nether portal (obsidian)
2. Enter the Nether safely
3. Find a Nether fortress
4. Kill Blazes for blaze rods
5. Collect ender pearls (bartering or hunting)

**Current Focus**: {focus}

The Nether is extremely dangerous - be prepared!""",
        
        "stronghold": """## Phase 6: Stronghold
**Goal**: Find and enter the End portal.

**Priorities**:
1. Craft Eyes of Ender (blaze powder + ender pearl)
2. Throw Eyes of Ender to locate stronghold
3. Dig down to find stronghold
4. Navigate to End portal room
5. Activate portal with 12 Eyes of Ender

**Current Focus**: {focus}

You're getting close to the final challenge!""",
        
        "dragon": """## Phase 7: Dragon
**Goal**: Defeat the Ender Dragon.

**Priorities**:
1. Destroy End crystals (beds work well)
2. Attack dragon when it perches
3. Avoid dragon breath
4. Use beds for explosive damage
5. Collect dragon egg after victory

**Current Focus**: {focus}

This is the final battle - give it everything you've got!"""
    }
    
    # Emergency prompt for critical situations
    EMERGENCY_PROMPT = """## ⚠️ EMERGENCY SITUATION ⚠️

**Health**: {health}/20
**Hunger**: {hunger}/20
**Threats**: {threats}
**Location**: {position}

IMMEDIATE ACTION REQUIRED!

**Survival Priority List**:
1. If health < 5: FLEE or EAT immediately
2. If hostile nearby: DEFEND or ATTACK
3. If in lava/water: ESCAPE immediately
4. If starving: Find food NOW
5. If night with no shelter: BUILD shelter

What is the BEST immediate survival action?"""
    
    # Exploration prompt for when unsure what to do
    EXPLORATION_PROMPT = """## Exploration Mode

**Current Location**: {position}
**Inventory Summary**: {inventory_summary}
**Time of Day**: {time_of_day}
**Weather**: {weather}

The player needs direction. Suggest an exploratory action to discover new opportunities:
- Scout nearby area
- Look for specific resources
- Head towards interesting landmarks
- Search for structures (villages, caves, etc.)

What exploration action would be most beneficial?"""
    
    # Crafting prompt for item creation decisions
    CRAFTING_PROMPT = """## Crafting Decision

**Available Resources**:
{available_items}

**Current Tools/Equipment**:
{current_equipment}

**Phase Objective**: {objective}

What should the player craft to best progress?
Consider:
- What tools are needed next?
- What's the most limiting factor?
- What provides the most value?

Recommend a specific crafting action."""
    
    # Combat prompt for combat situations
    COMBAT_PROMPT = """## Combat Situation

**Player Health**: {health}/20
**Player Armor**: {armor_status}
**Weapon**: {current_weapon}
**Enemies Nearby**:
{enemies}

**Distance to Nearest Threat**: {nearest_distance}

Analyze the combat situation and recommend the best combat action:
- Should we attack or retreat?
- Which enemy to target first?
- Should we switch weapons/items?
- Is there a tactical advantage nearby?"""
    
    # Resource gathering prompt
    GATHERING_PROMPT = """## Resource Gathering

**Need**: {needed_resource}
**Current Tool**: {current_tool}
**Nearby Blocks**:
{nearby_blocks}

**Inventory Space**: {inventory_space}/36 slots filled

Best approach to gather {needed_resource}:
1. Find the resource nearby
2. Use appropriate tool
3. Maximize gathering efficiency
4. Manage inventory space

What gathering action should be taken?"""
    
    @classmethod
    def format_prompt(cls, template: str, **kwargs) -> str:
        """
        Format a prompt template with the provided values.
        
        Args:
            template: The prompt template string with {placeholders}
            **kwargs: Keyword arguments to fill placeholders
            
        Returns:
            Formatted prompt string
            
        Raises:
            KeyError: If a required placeholder is missing
            ValueError: If template formatting fails
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"Missing required placeholder in prompt: {e}")
        except Exception as e:
            raise ValueError(f"Failed to format prompt: {e}")
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get the base system prompt."""
        return cls.SYSTEM_PROMPT
    
    @classmethod
    def get_phase_prompt(cls, phase: str, focus: str = "General progression") -> str:
        """
        Get a phase-specific prompt.
        
        Args:
            phase: Phase name (foundation, resources, tools, mining, nether, stronghold, dragon)
            focus: Current focus within the phase
            
        Returns:
            Formatted phase prompt
        """
        if phase not in cls.PHASE_PROMPTS:
            raise ValueError(f"Unknown phase: {phase}. Valid phases: {list(cls.PHASE_PROMPTS.keys())}")
        
        return cls.format_prompt(cls.PHASE_PROMPTS[phase], focus=focus)
    
    @classmethod
    def get_emergency_prompt(cls, health: float, hunger: float, threats: str, position: str) -> str:
        """
        Get an emergency situation prompt.
        
        Args:
            health: Current health (0-20)
            hunger: Current hunger (0-20)
            threats: Description of immediate threats
            position: Current position coordinates
            
        Returns:
            Formatted emergency prompt
        """
        return cls.format_prompt(
            cls.EMERGENCY_PROMPT,
            health=health,
            hunger=hunger,
            threats=threats,
            position=position
        )
    
    @classmethod
    def get_exploration_prompt(cls, position: str, inventory_summary: str, time_of_day: int, weather: str) -> str:
        """
        Get an exploration prompt.
        
        Args:
            position: Current position
            inventory_summary: Summary of inventory contents
            time_of_day: Time in ticks (0-24000)
            weather: Weather description
            
        Returns:
            Formatted exploration prompt
        """
        # Convert ticks to readable time
        hours = (time_of_day // 1000 + 6) % 24
        time_str = f"{hours}:00"
        
        return cls.format_prompt(
            cls.EXPLORATION_PROMPT,
            position=position,
            inventory_summary=inventory_summary,
            time_of_day=time_str,
            weather=weather
        )
    
    @classmethod
    def build_full_prompt(cls, phase: str, game_state: Dict[str, Any], 
                         recent_actions: str = "None", focus: str = "General progression") -> str:
        """
        Build a complete prompt for AI decision-making.
        
        Args:
            phase: Current game phase
            game_state: Complete game state dictionary
            recent_actions: Description of recent actions taken
            focus: Current focus within phase
            
        Returns:
            Complete formatted prompt
        """
        # Check for emergency situations
        player = game_state.get("player", {})
        health = player.get("health", 20)
        hunger = player.get("hunger", 20)
        
        # Use emergency prompt if health is critically low
        if health < 6 or hunger < 4:
            threats = []
            for entity in game_state.get("world", {}).get("nearby_entities", []):
                if entity.get("is_hostile", False):
                    threats.append(f"{entity['type']} at distance {entity.get('distance', '?')}")
            
            position = player.get("position", {})
            pos_str = f"({position.get('x', '?')}, {position.get('y', '?')}, {position.get('z', '?')})"
            
            return cls.get_emergency_prompt(
                health=health,
                hunger=hunger,
                threats=", ".join(threats) if threats else "None detected",
                position=pos_str
            )
        
        # Build standard action decision prompt
        phase_prompt = cls.get_phase_prompt(phase, focus)
        
        return cls.format_prompt(
            cls.ACTION_DECISION_PROMPT,
            game_state=str(game_state),
            phase=phase_prompt,
            objectives=cls.get_phase_objectives(phase),
            recent_actions=recent_actions
        )
    
    @staticmethod
    def get_phase_objectives(phase: str) -> str:
        """Get objectives for a specific phase."""
        objectives = {
            "foundation": "Collect wood, craft wooden tools, build shelter, find food",
            "resources": "Mine stone, craft stone tools, find coal, make torches",
            "tools": "Mine iron, smelt ingots, craft iron tools and armor",
            "mining": "Mine diamonds at Y=-59, collect obsidian",
            "nether": "Build portal, find fortress, get blaze rods and ender pearls",
            "stronghold": "Craft Eyes of Ender, locate stronghold, activate End portal",
            "dragon": "Destroy End crystals, defeat Ender Dragon"
        }
        return objectives.get(phase, "Progress through the game")