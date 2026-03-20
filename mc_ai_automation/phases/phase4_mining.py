"""
Phase 4: Mining
==============

This module implements Phase 4 of the Minecraft speedrun automation.
Goal: Find diamonds and obsidian.

Objectives:
-----------
1. Mine at Y level -59 for diamonds
2. Collect at least 5 diamonds
3. Craft diamond pickaxe
4. Find and mine obsidian
5. Mine ancient debris (optional)
"""

from typing import Dict, Any, List
from actions.movement import Movement
from actions.combat import Combat
from actions.gathering import Gathering
from actions.inventory import Inventory


class Phase4_Mining:
    """
    Phase 4: Mining
    
    Goal: Find diamonds and obsidian.
    
    Objectives:
    1. Mine at Y level -59 for diamonds
    2. Collect at least 5 diamonds
    3. Craft diamond pickaxe
    4. Find and mine obsidian
    5. Mine ancient debris (optional)
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
            "reached_mining_level": False,
            "diamonds_collected": False,
            "diamond_pickaxe_crafted": False,
            "obsidian_collected": False
        }
        self.diamond_count = 0
        self.target_diamonds = 5
        self.obsidian_count = 0
        self.target_obsidian = 10  # Need 10 for nether portal
        
    def is_complete(self) -> bool:
        """
        Check if Phase 4 objectives are met.
        
        Returns:
            True if all objectives are complete
        """
        # Core objectives (obsidian is optional for speedrun)
        return (self.objectives_completed["diamonds_collected"] and
                self.objectives_completed["diamond_pickaxe_crafted"])
    
    def get_objectives(self) -> list:
        """
        Get list of objectives for this phase.
        
        Returns:
            List of objective strings
        """
        return [
            "Mine down to Y level -59",
            "Collect 5 diamonds",
            "Craft diamond pickaxe",
            "Collect 10 obsidian for Nether portal"
        ]
    
    def execute(self) -> dict:
        """
        Execute one tick of Phase 4.
        
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
        
        # Check if we're at the right mining level
        y_level = player.get("position", {}).get("y", 64)
        if y_level <= -50:  # Close to -59
            self.objectives_completed["reached_mining_level"] = True
            
        # Check diamonds
        diamond_items = [item for item in inventory 
                        if "diamond" in item.get("item_id", "") and
                           "pickaxe" not in item.get("item_id", "")]
        self.diamond_count = sum(item.get("count", 0) for item in diamond_items)
        
        if self.diamond_count >= self.target_diamonds:
            self.objectives_completed["diamonds_collected"] = True
            
        # Check diamond pickaxe
        if self.inventory.has_item("minecraft:diamond_pickaxe", inventory):
            self.objectives_completed["diamond_pickaxe_crafted"] = True
            
        # Check obsidian
        obsidian_items = [item for item in inventory 
                         if "obsidian" in item.get("item_id", "")]
        self.obsidian_count = sum(item.get("count", 0) for item in obsidian_items)
        
        if self.obsidian_count >= self.target_obsidian:
            self.objectives_completed["obsidian_collected"] = True
    
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
        
        # Priority 3: Mine down to diamond level
        if not self.objectives_completed["reached_mining_level"]:
            y_level = player.get("position", {}).get("y", 64)
            if y_level > -50:
                # Need to mine down
                return {
                    "action": "break_block",
                    "target": None,
                    "params": {"hold_ticks": 20},
                    "reasoning": f"Mining down to Y -59 (currently at Y {int(y_level)})",
                    "priority": 7,
                    "timeout": 5.0
                }
            else:
                self.objectives_completed["reached_mining_level"] = True
        
        # Priority 4: Mine diamonds
        if not self.objectives_completed["diamonds_collected"]:
            nearby_blocks = world.get("nearby_blocks", [])
            diamond_blocks = [b for b in nearby_blocks 
                             if "diamond_ore" in b.get("type", "")]
            
            if diamond_blocks:
                nearest_diamond = diamond_blocks[0]
                pos = nearest_diamond.get("position", {})
                return {
                    "action": "break_block",
                    "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                    "params": {"hold_ticks": 20},
                    "reasoning": f"Mining diamonds ({self.diamond_count}/{self.target_diamonds})",
                    "priority": 8,
                    "timeout": 5.0
                }
            else:
                # Strip mine to find diamonds
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 10},
                    "reasoning": "Strip mining for diamonds",
                    "priority": 6,
                    "timeout": 10.0
                }
        
        # Priority 5: Craft diamond pickaxe
        if not self.objectives_completed["diamond_pickaxe_crafted"]:
            if self.diamond_count >= 3:
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:diamond_pickaxe", "count": 1},
                    "reasoning": "Crafting diamond pickaxe",
                    "priority": 7,
                    "timeout": 3.0
                }
        
        # Priority 6: Mine obsidian
        if not self.objectives_completed["obsidian_collected"]:
            nearby_blocks = world.get("nearby_blocks", [])
            obsidian_blocks = [b for b in nearby_blocks 
                              if "obsidian" in b.get("type", "")]
            
            if obsidian_blocks:
                nearest_obsidian = obsidian_blocks[0]
                pos = nearest_obsidian.get("position", {})
                return {
                    "action": "break_block",
                    "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                    "params": {"hold_ticks": 20},
                    "reasoning": f"Mining obsidian ({self.obsidian_count}/{self.target_obsidian})",
                    "priority": 6,
                    "timeout": 10.0  # Obsidian takes longer to mine
                }
            else:
                # Look for lava + water to create obsidian
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 15},
                    "reasoning": "Searching for obsidian or lava",
                    "priority": 5,
                    "timeout": 10.0
                }
        
        # Default: Explore or prepare for next phase
        return {
            "action": "explore",
            "target": None,
            "params": {"direction": "forward", "distance": 10},
            "reasoning": "Phase 4 complete - preparing for Nether",
            "priority": 2,
            "timeout": 10.0
        }