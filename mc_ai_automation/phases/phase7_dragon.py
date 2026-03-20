"""
Phase 7: Dragon
==============

This module implements Phase 7 of the Minecraft speedrun automation.
Goal: Defeat the Ender Dragon.

Objectives:
-----------
1. Destroy End crystals (beds work well)
2. Attack dragon when it perches
3. Avoid dragon breath
4. Use beds for explosive damage
5. Collect dragon egg after victory
"""

from typing import Dict, Any, List
from actions.movement import Movement
from actions.combat import Combat
from actions.gathering import Gathering
from actions.inventory import Inventory


class Phase7_Dragon:
    """
    Phase 7: Dragon
    
    Goal: Defeat the Ender Dragon.
    
    Objectives:
    1. Destroy End crystals
    2. Attack dragon when it perches
    3. Avoid dragon breath
    4. Use beds for explosive damage
    5. Collect dragon egg
    """
    
    def __init__(self, game_state_provider, action_decider):
        """
        Initialize the phase.
        
        Args:
            game_state_provider: Callable that returns GameState dict
            action_decider: Callable (game_state) -> Action dict
        """
        self.get_state = game_state_provider
        self.decide = action_decider
        self.movement = Movement()
        self.combat = Combat()
        self.gathering = Gathering()
        self.inventory = Inventory()
        
        self.objectives_completed = {
            "crystals_destroyed": False,
            "dragon_defeated": False,
            "egg_collected": False
        }
        self.crystals_destroyed = 0
        self.target_crystals = 10  # Typical number of crystals
        self.has_beds = False
        
    def is_complete(self) -> bool:
        """
        Check if Phase 7 objectives are met.
        
        Returns:
            True if phase is complete
        """
        return self.objectives_completed["dragon_defeated"]
    
    def get_objectives(self) -> list:
        """
        Get list of objectives for this phase.
        
        Returns:
            List of objective strings
        """
        return [
            "Destroy all End crystals",
            "Defeat the Ender Dragon",
            "Collect the dragon egg"
        ]
    
    def execute(self) -> dict:
        """
        Execute one tick of Phase 7.
        
        Returns:
            Action to perform
        """
        state = self.get_state()
        
        # Update objective status
        self._update_objectives(state)
        
        # Get next action based on current state
        action = self._get_next_action(state)
        
        return action
    
    def _update_objectives(self, state: Dict[str, Any]) -> None:
        """
        Update objective completion status.
        
        Args:
            state: Current game state
        """
        inventory = state.get("inventory", {}).get("items", [])
        world = state.get("world", {})
        
        # Check for End crystals
        nearby_entities = world.get("nearby_entities", [])
        crystals = [e for e in nearby_entities 
                   if "end_crystal" in e.get("type", "").lower()]
        
        # Count destroyed crystals (simplified - just track if we've attacked)
        if len(crystals) == 0:
            self.objectives_completed["crystals_destroyed"] = True
            
        # Check for dragon
        dragons = [e for e in nearby_entities 
                  if "ender_dragon" in e.get("type", "").lower()]
        
        if len(dragons) == 0 and self.objectives_completed["crystals_destroyed"]:
            self.objectives_completed["dragon_defeated"] = True
            
        # Check for beds (for explosive damage)
        self.has_beds = self.inventory.has_item("minecraft:bed", inventory)
    
    def _get_next_action(self, state: Dict[str, Any]) -> dict:
        """
        Determine the next action based on current state.
        
        Args:
            state: Current game state
            
        Returns:
            Action dictionary
        """
        inventory = state.get("inventory", {}).get("items", [])
        player = state.get("player", {})
        world = state.get("world", {})
        
        # Priority 1: Avoid dragon breath
        nearby_entities = world.get("nearby_entities", [])
        dragon_breath = [e for e in nearby_entities 
                        if "dragon_breath" in e.get("type", "").lower()]
        
        if dragon_breath:
            return {
                "action": "flee",
                "target": None,
                "params": {"speed": "sprint"},
                "reasoning": "Avoiding dragon breath",
                "priority": 10,
                "timeout": 3.0
            }
        
        # Priority 2: Low health - eat
        health = player.get("health", 20)
        if health < 10:
            food_items = self.inventory.get_food_items(inventory)
            if food_items:
                return {
                    "action": "use_item",
                    "target": None,
                    "params": {"hold_ticks": 40},
                    "reasoning": f"Low health ({health}) - eating food",
                    "priority": 9,
                    "timeout": 3.0
                }
        
        # Priority 3: Destroy End crystals
        crystals = [e for e in nearby_entities 
                   if "end_crystal" in e.get("type", "").lower()]
        
        if crystals:
            nearest_crystal = crystals[0]
            pos = nearest_crystal.get("position", {})
            
            # Use beds for explosive damage if available
            if self.has_beds:
                return {
                    "action": "place_block",
                    "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                    "params": {"block_type": "bed"},
                    "reasoning": "Using bed to destroy crystal",
                    "priority": 8,
                    "timeout": 5.0
                }
            else:
                # Attack crystal with sword/bow
                return {
                    "action": "attack_entity",
                    "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                    "params": {"entity_type": "end_crystal"},
                    "reasoning": f"Destroying End crystals ({self.crystals_destroyed}/{self.target_crystals})",
                    "priority": 8,
                    "timeout": 5.0
                }
        
        # Priority 4: Attack dragon
        dragons = [e for e in nearby_entities 
                  if "ender_dragon" in e.get("type", "").lower()]
        
        if dragons:
            dragon = dragons[0]
            pos = dragon.get("position", {})
            
            # Check if dragon is perching (low Y position)
            if pos.get("y", 100) < 70:
                # Dragon is perching - use beds for max damage
                if self.has_beds:
                    return {
                        "action": "place_block",
                        "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                        "params": {"block_type": "bed"},
                        "reasoning": "Using bed explosion on perched dragon",
                        "priority": 9,
                        "timeout": 5.0
                    }
                else:
                    # Attack with sword
                    return {
                        "action": "attack_entity",
                        "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                        "params": {"entity_type": "ender_dragon"},
                        "reasoning": "Attacking perched dragon",
                        "priority": 8,
                        "timeout": 5.0
                    }
            else:
                # Dragon is flying - wait for it to perch or use bow
                return {
                    "action": "look_at",
                    "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                    "params": {},
                    "reasoning": "Tracking flying dragon",
                    "priority": 6,
                    "timeout": 3.0
                }
        
        # Priority 5: Check for dragon egg (victory!)
        if self.objectives_completed["dragon_defeated"]:
            nearby_blocks = world.get("nearby_blocks", [])
            egg_blocks = [b for b in nearby_blocks 
                         if "dragon_egg" in b.get("type", "")]
            
            if egg_blocks:
                egg_pos = egg_blocks[0].get("position", {})
                return {
                    "action": "break_block",
                    "target": [egg_pos.get("x", 0), egg_pos.get("y", 0), egg_pos.get("z", 0)],
                    "params": {"hold_ticks": 20},
                    "reasoning": "Collecting dragon egg",
                    "priority": 7,
                    "timeout": 5.0
                }
            else:
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 10},
                    "reasoning": "Searching for dragon egg",
                    "priority": 5,
                    "timeout": 10.0
                }
        
        # Default: Wait or explore
        return {
            "action": "wait",
            "target": None,
            "params": {"duration": 1.0},
            "reasoning": "Waiting for dragon to appear",
            "priority": 3,
            "timeout": 5.0
        }
