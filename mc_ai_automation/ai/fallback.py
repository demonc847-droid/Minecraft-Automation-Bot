"""
Fallback Strategies for Minecraft AI
====================================

This module provides fallback actions when AI decision-making fails
or is unavailable. Implements multiple strategies for different situations.
"""

import random
from typing import Dict, Any, List, Optional
from enum import Enum


class FallbackType(Enum):
    """Types of fallback strategies available."""
    SAFE = "safe"           # Prioritize survival
    EXPLORE = "explore"     # Explore surroundings
    RANDOM = "random"       # Random valid actions


class FallbackStrategy:
    """
    Provides fallback actions when AI decision-making fails.
    
    Strategies:
    - safe: Prioritize survival - defend, retreat, eat food
    - explore: Move randomly, look around to gather information
    - random: Pick a random valid action from available options
    """
    
    def __init__(self, default_strategy: str = "safe"):
        """
        Initialize fallback strategy handler.
        
        Args:
            default_strategy: Default strategy to use ("safe", "explore", or "random")
        """
        self.default_strategy = default_strategy
        self._action_history: List[Dict[str, Any]] = []
        self._max_history = 10
    
    def get_fallback_action(self, game_state: Dict[str, Any], 
                           strategy: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a fallback action based on the current game state.
        
        Args:
            game_state: Current game state dictionary
            strategy: Override strategy for this action ("safe", "explore", "random")
            
        Returns:
            Action dictionary compatible with the action interface
        """
        if strategy is None:
            strategy = self.default_strategy
        
        # Validate strategy
        valid_strategies = ["safe", "explore", "random"]
        if strategy not in valid_strategies:
            strategy = self.default_strategy
        
        # Choose fallback strategy
        if strategy == "safe":
            action = self._safe_fallback(game_state)
        elif strategy == "explore":
            action = self._explore_fallback(game_state)
        else:  # random
            action = self._random_fallback(game_state)
        
        # Add metadata
        action["reasoning"] = f"Fallback action using {strategy} strategy"
        action["priority"] = 3  # Lower priority than AI decisions
        action["timeout"] = 5.0
        
        # Track action history
        self._track_action(action)
        
        return action
    
    def _safe_fallback(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safe fallback strategy - prioritize survival.
        
        Actions in priority order:
        1. Eat food if health/hunger is low
        2. Defend if hostile nearby
        3. Retreat from danger
        4. Wait safely
        
        Args:
            game_state: Current game state
            
        Returns:
            Safe action dictionary
        """
        player = game_state.get("player", {})
        world = game_state.get("world", {})
        inventory = game_state.get("inventory", {})
        
        health = player.get("health", 20)
        hunger = player.get("hunger", 20)
        is_in_water = player.get("is_in_water", False)
        is_in_lava = player.get("is_in_lava", False)
        
        # Priority 1: Escape immediate danger
        if is_in_lava:
            return {
                "action": "jump",
                "target": None,
                "params": {},
                "reasoning": "In lava - attempting to escape"
            }
        
        if is_in_water and health < 10:
            return {
                "action": "jump",
                "target": None,
                "params": {},
                "reasoning": "Low health in water - trying to get to surface"
            }
        
        # Priority 2: Eat food if available and needed
        if hunger < 10 or health < 15:
            food_slot = self._find_food_slot(inventory)
            if food_slot is not None:
                return {
                    "action": "select_slot",
                    "target": None,
                    "params": {"slot": food_slot},
                    "reasoning": "Selecting food to eat"
                }
        
        # Priority 3: Defend if hostile nearby
        nearby_entities = world.get("nearby_entities", [])
        hostile_nearby = [e for e in nearby_entities if e.get("is_hostile", False)]
        
        if hostile_nearby:
            nearest_threat = min(hostile_nearby, key=lambda e: e.get("distance", float('inf')))
            threat_distance = nearest_threat.get("distance", 0)
            
            if threat_distance < 5:  # Very close
                # Check if we have a weapon
                selected_slot = inventory.get("selected_slot", 0)
                items = inventory.get("items", [])
                has_weapon = any(
                    item.get("slot") == selected_slot and 
                    any(w in item.get("item_id", "") for w in ["sword", "axe", "trident"])
                    for item in items
                )
                
                if has_weapon:
                    return {
                        "action": "attack",
                        "target": None,
                        "params": {"hold_ticks": 10},
                        "reasoning": f"Attacking {nearest_threat['type']} at close range"
                    }
                else:
                    # No weapon - retreat
                    return {
                        "action": "flee",
                        "target": self._get_retreat_target(player, nearest_threat),
                        "params": {"speed": "sprint"},
                        "reasoning": f"Retreating from {nearest_threat['type']} - no weapon"
                    }
        
        # Priority 4: Look around to assess situation
        return {
            "action": "look_at",
            "target": self._get_look_around_target(player),
            "params": {},
            "reasoning": "Looking around to assess situation safely"
        }
    
    def _explore_fallback(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explore fallback strategy - gather information.
        
        Actions:
        1. Look around in different directions
        2. Move to explore new areas
        3. Jump to get better view
        
        Args:
            game_state: Current game state
            
        Returns:
            Exploration action dictionary
        """
        player = game_state.get("player", {})
        position = player.get("position", {})
        yaw = player.get("yaw", 0)
        
        # Random exploration actions
        explore_actions = [
            {
                "action": "look_at",
                "target": [
                    position.get("x", 0) + random.uniform(-10, 10),
                    position.get("y", 0) + random.uniform(-5, 5),
                    position.get("z", 0) + random.uniform(-10, 10)
                ],
                "params": {},
                "reasoning": "Scanning surroundings"
            },
            {
                "action": "jump",
                "target": None,
                "params": {},
                "reasoning": "Jumping to get better view"
            },
            {
                "action": "move_to",
                "target": [
                    position.get("x", 0) + random.uniform(-5, 5),
                    position.get("y", 0),
                    position.get("z", 0) + random.uniform(-5, 5)
                ],
                "params": {"speed": "walk"},
                "reasoning": "Walking to explore nearby area"
            },
            {
                "action": "look_at",
                "target": [
                    position.get("x", 0) + 10 * random.choice([-1, 1]),
                    position.get("y", 0),
                    position.get("z", 0) + 10 * random.choice([-1, 1])
                ],
                "params": {},
                "reasoning": "Looking at horizon"
            }
        ]
        
        # Choose random exploration action
        return random.choice(explore_actions)
    
    def _random_fallback(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Random fallback strategy - pick random valid action.
        
        Args:
            game_state: Current game state
            
        Returns:
            Random action dictionary
        """
        player = game_state.get("player", {})
        position = player.get("position", {})
        inventory = game_state.get("inventory", {})
        
        # Build list of possible actions
        possible_actions = [
            {
                "action": "wait",
                "target": None,
                "params": {"duration": random.uniform(0.5, 2.0)},
                "reasoning": "Waiting randomly"
            },
            {
                "action": "jump",
                "target": None,
                "params": {},
                "reasoning": "Random jump"
            },
            {
                "action": "look_at",
                "target": [
                    position.get("x", 0) + random.uniform(-10, 10),
                    position.get("y", 0) + random.uniform(-5, 5),
                    position.get("z", 0) + random.uniform(-10, 10)
                ],
                "params": {},
                "reasoning": "Looking at random direction"
            }
        ]
        
        # Add movement action if on ground
        if player.get("is_on_ground", True):
            possible_actions.append({
                "action": "move_to",
                "target": [
                    position.get("x", 0) + random.uniform(-3, 3),
                    position.get("y", 0),
                    position.get("z", 0) + random.uniform(-3, 3)
                ],
                "params": {"speed": "walk"},
                "reasoning": "Random movement"
            })
        
        # Add slot selection if has multiple hotbar items
        items = inventory.get("items", [])
        hotbar_items = [item for item in items if 0 <= item.get("slot", -1) <= 8]
        if len(hotbar_items) > 1:
            possible_actions.append({
                "action": "select_slot",
                "target": None,
                "params": {"slot": random.randint(0, 8)},
                "reasoning": "Random slot selection"
            })
        
        return random.choice(possible_actions)
    
    def _find_food_slot(self, inventory: Dict[str, Any]) -> Optional[int]:
        """
        Find a slot containing food in the inventory.
        
        Args:
            inventory: Inventory section of game state
            
        Returns:
            Slot number with food, or None if no food found
        """
        food_items = [
            "bread", "cooked_beef", "cooked_porkchop", "cooked_chicken",
            "cooked_salmon", "cooked_cod", "baked_potato", "carrot",
            "apple", "golden_apple", "melon_slice", "sweet_berries",
            "beef", "porkchop", "chicken", "salmon", "cod", "potato",
            "beetroot", "cake", "cookie", "pumpkin_pie"
        ]
        
        items = inventory.get("items", [])
        for item in items:
            item_id = item.get("item_id", "").lower()
            # Remove "minecraft:" prefix if present
            item_name = item_id.replace("minecraft:", "")
            
            if item_name in food_items and item.get("count", 0) > 0:
                slot = item.get("slot")
                if slot is not None and 0 <= slot <= 8:  # Hotbar only
                    return slot
        
        return None
    
    def _get_retreat_target(self, player: Dict[str, Any], 
                           threat: Dict[str, Any]) -> List[float]:
        """
        Calculate a retreat position away from a threat.
        
        Args:
            player: Player section of game state
            threat: Threatening entity data
            
        Returns:
            Target coordinates to retreat to
        """
        player_pos = player.get("position", {})
        threat_pos = threat.get("position", {})
        
        px = player_pos.get("x", 0)
        py = player_pos.get("y", 0)
        pz = player_pos.get("z", 0)
        
        tx = threat_pos.get("x", 0)
        tz = threat_pos.get("z", 0)
        
        # Calculate direction away from threat
        dx = px - tx
        dz = pz - tz
        
        # Normalize and scale retreat distance
        distance = (dx**2 + dz**2) ** 0.5
        if distance > 0:
            dx = (dx / distance) * 10  # Retreat 10 blocks
            dz = (dz / distance) * 10
        else:
            dx = random.uniform(-10, 10)
            dz = random.uniform(-10, 10)
        
        return [px + dx, py, pz + dz]
    
    def _get_look_around_target(self, player: Dict[str, Any]) -> List[float]:
        """
        Calculate a target to look at for assessing surroundings.
        
        Args:
            player: Player section of game state
            
        Returns:
            Target coordinates to look at
        """
        position = player.get("position", {})
        yaw = player.get("yaw", 0)
        
        # Look in the direction player is facing
        import math
        yaw_rad = math.radians(yaw)
        
        x = position.get("x", 0) + math.sin(yaw_rad) * 10
        y = position.get("y", 0) + 1  # Slightly above eye level
        z = position.get("z", 0) + math.cos(yaw_rad) * 10
        
        return [x, y, z]
    
    def _track_action(self, action: Dict[str, Any]) -> None:
        """
        Track action in history to avoid repetition.
        
        Args:
            action: Action to track
        """
        self._action_history.append(action)
        if len(self._action_history) > self._max_history:
            self._action_history.pop(0)
    
    def get_last_action(self) -> Optional[Dict[str, Any]]:
        """
        Get the last fallback action taken.
        
        Returns:
            Last action or None if history is empty
        """
        if self._action_history:
            return self._action_history[-1]
        return None
    
    def clear_history(self) -> None:
        """Clear the action history."""
        self._action_history.clear()
    
    def set_default_strategy(self, strategy: str) -> None:
        """
        Set the default fallback strategy.
        
        Args:
            strategy: Strategy name ("safe", "explore", or "random")
        """
        valid_strategies = ["safe", "explore", "random"]
        if strategy in valid_strategies:
            self.default_strategy = strategy
    
    def get_available_strategies(self) -> List[str]:
        """
        Get list of available fallback strategies.
        
        Returns:
            List of strategy names
        """
        return ["safe", "explore", "random"]


# Convenience function for quick fallback action retrieval
def get_fallback_action(game_state: Dict[str, Any], 
                       strategy: str = "safe") -> Dict[str, Any]:
    """
    Get a fallback action without creating a FallbackStrategy instance.
    
    Args:
        game_state: Current game state dictionary
        strategy: Fallback strategy to use ("safe", "explore", "random")
        
    Returns:
        Action dictionary
    """
    fallback = FallbackStrategy(default_strategy=strategy)
    return fallback.get_fallback_action(game_state, strategy)