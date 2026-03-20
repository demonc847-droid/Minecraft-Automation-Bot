"""
Phase 6: Stronghold
==================

This module implements Phase 6 of the Minecraft speedrun automation.
Goal: Find and enter the End portal.

Objectives:
-----------
1. Craft Eyes of Ender (blaze powder + ender pearl)
2. Throw Eyes of Ender to locate stronghold
3. Dig down to find stronghold
4. Navigate to End portal room
5. Activate portal with 12 Eyes of Ender
"""

from typing import Dict, Any, List
from actions.movement import Movement
from actions.combat import Combat
from actions.gathering import Gathering
from actions.inventory import Inventory


class Phase6_Stronghold:
    """
    Phase 6: Stronghold
    
    Goal: Find and enter the End portal.
    
    Objectives:
    1. Craft Eyes of Ender (blaze powder + ender pearl)
    2. Throw Eyes of Ender to locate stronghold
    3. Dig down to find stronghold
    4. Navigate to End portal room
    5. Activate portal with 12 Eyes of Ender
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
            "eyes_crafted": False,
            "stronghold_located": False,
            "stronghold_found": False,
            "portal_activated": False,
            "entered_end": False
        }
        self.eye_count = 0
        self.target_eyes = 12
        self.stronghold_position = None
        
    def is_complete(self) -> bool:
        """
        Check if Phase 6 objectives are met.
        
        Returns:
            True if phase is complete
        """
        return self.objectives_completed["entered_end"]
    
    def get_objectives(self) -> list:
        """
        Get list of objectives for this phase.
        
        Returns:
            List of objective strings
        """
        return [
            "Craft 12 Eyes of Ender",
            "Locate stronghold with Eyes of Ender",
            "Find the stronghold structure",
            "Navigate to End portal room",
            "Activate End portal"
        ]
    
    def execute(self) -> dict:
        """
        Execute one tick of Phase 6.
        
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
        player = state.get("player", {})
        
        # Check Eyes of Ender
        eye_items = [item for item in inventory 
                    if "eye_of_ender" in item.get("item_id", "")]
        self.eye_count = sum(item.get("count", 0) for item in eye_items)
        
        if self.eye_count >= self.target_eyes:
            self.objectives_completed["eyes_crafted"] = True
            
        # Check dimension
        dimension = player.get("dimension", "overworld")
        if dimension == "end":
            self.objectives_completed["entered_end"] = True
    
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
        dimension = player.get("dimension", "overworld")
        
        # Priority 1: Handle immediate threats
        threat_level = self.combat.get_threat_level(state)
        if threat_level >= 7:
            return {
                "action": "flee",
                "target": None,
                "params": {"speed": "sprint"},
                "reasoning": "High threat level - fleeing",
                "priority": 10,
                "timeout": 5.0
            }
        elif threat_level >= 4:
            return {
                "action": "defend",
                "target": None,
                "params": {"duration": 2.0},
                "reasoning": "Moderate threat - defending",
                "priority": 8,
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
        
        # If in the End, we're done
        if dimension == "end":
            return {
                "action": "none",
                "target": None,
                "params": {},
                "reasoning": "Successfully entered the End!",
                "priority": 1,
                "timeout": 1.0
            }
        
        # Priority 3: Craft Eyes of Ender
        if not self.objectives_completed["eyes_crafted"]:
            blaze_rod_count = self.inventory.get_item_count("minecraft:blaze_rod", inventory)
            ender_pearl_count = self.inventory.get_item_count("minecraft:ender_pearl", inventory)
            
            # Convert blaze rods to blaze powder
            if blaze_rod_count > 0:
                blaze_powder_count = self.inventory.get_item_count("minecraft:blaze_powder", inventory)
                if blaze_powder_count < ender_pearl_count:
                    return {
                        "action": "craft_item",
                        "target": None,
                        "params": {"item_id": "minecraft:blaze_powder", "count": 1},
                        "reasoning": "Converting blaze rods to powder",
                        "priority": 7,
                        "timeout": 3.0
                    }
            
            # Craft Eyes of Ender
            blaze_powder_count = self.inventory.get_item_count("minecraft:blaze_powder", inventory)
            if blaze_powder_count > 0 and ender_pearl_count > 0:
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:eye_of_ender", "count": 1},
                    "reasoning": f"Crafting Eyes of Ender ({self.eye_count}/{self.target_eyes})",
                    "priority": 7,
                    "timeout": 3.0
                }
            else:
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 15},
                    "reasoning": "Need blaze powder and ender pearls",
                    "priority": 5,
                    "timeout": 10.0
                }
        
        # Priority 4: Locate stronghold
        if not self.objectives_completed["stronghold_located"] and self.eye_count > 0:
            # Throw Eye of Ender
            return {
                "action": "use_item",
                "target": None,
                "params": {"hold_ticks": 10},
                "reasoning": "Throwing Eye of Ender to locate stronghold",
                "priority": 7,
                "timeout": 5.0
            }
        
        # Priority 5: Find stronghold
        if not self.objectives_completed["stronghold_found"]:
            # Look for stone brick blocks (stronghold material)
            nearby_blocks = world.get("nearby_blocks", [])
            stronghold_blocks = [b for b in nearby_blocks 
                               if "stone_brick" in b.get("type", "") or
                                  "mossy_stone_brick" in b.get("type", "")]
            
            if stronghold_blocks:
                self.objectives_completed["stronghold_found"] = True
            else:
                # Move towards stronghold position
                if self.stronghold_position:
                    return {
                        "action": "move_to",
                        "target": self.stronghold_position,
                        "params": {"speed": "sprint"},
                        "reasoning": "Moving towards stronghold",
                        "priority": 6,
                        "timeout": 30.0
                    }
                else:
                    return {
                        "action": "explore",
                        "target": None,
                        "params": {"direction": "forward", "distance": 20},
                        "reasoning": "Searching for stronghold entrance",
                        "priority": 5,
                        "timeout": 15.0
                    }
        
        # Priority 6: Find End portal room
        if not self.objectives_completed["portal_activated"]:
            # Look for portal frame blocks
            nearby_blocks = world.get("nearby_blocks", [])
            portal_blocks = [b for b in nearby_blocks 
                           if "end_portal_frame" in b.get("type", "") or
                              "end_portal" in b.get("type", "")]
            
            if portal_blocks:
                # Check if portal is already active
                active_portal = [b for b in portal_blocks 
                               if "end_portal" in b.get("type", "")]
                
                if active_portal:
                    self.objectives_completed["portal_activated"] = True
                    # Move to portal
                    return {
                        "action": "move_to",
                        "target": [active_portal[0].get("position", {}).get("x", 0),
                                  active_portal[0].get("position", {}).get("y", 0),
                                  active_portal[0].get("position", {}).get("z", 0)],
                        "params": {"speed": "walk"},
                        "reasoning": "Entering End portal",
                        "priority": 8,
                        "timeout": 10.0
                    }
                else:
                    # Activate portal with Eyes of Ender
                    return {
                        "action": "interact",
                        "target": None,
                        "params": {},
                        "reasoning": "Placing Eye of Ender in portal frame",
                        "priority": 7,
                        "timeout": 5.0
                    }
            else:
                # Navigate stronghold corridors
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 15},
                    "reasoning": "Navigating stronghold to find portal room",
                    "priority": 5,
                    "timeout": 15.0
                }
        
        # Default: Explore
        return {
            "action": "explore",
            "target": None,
            "params": {"direction": "forward", "distance": 10},
            "reasoning": "Phase 6 complete",
            "priority": 2,
            "timeout": 10.0
        }