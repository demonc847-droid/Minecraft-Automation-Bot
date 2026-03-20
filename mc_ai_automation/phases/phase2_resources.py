"""
Phase 2: Resources
=================

This module implements Phase 2 of the Minecraft speedrun automation.
Goal: Gather materials for progression - stone tools, coal, torches.

Objectives:
-----------
1. Mine stone for better tools
2. Craft stone tools (pickaxe, sword, axe)
3. Find coal for torches
4. Build torches for lighting
5. Continue gathering wood
"""

from typing import Dict, Any, List
from actions.movement import Movement
from actions.combat import Combat
from actions.gathering import Gathering
from actions.inventory import Inventory


class Phase2_Resources:
    """
    Phase 2: Resources
    
    Goal: Gather materials for progression - stone tools, coal, torches.
    
    Objectives:
    1. Mine stone for better tools
    2. Craft stone tools (pickaxe, sword, axe)
    3. Find coal for torches
    4. Build torches for lighting
    5. Continue gathering wood
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
            "stone_mined": False,
            "stone_tools_crafted": False,
            "coal_found": False,
            "torches_crafted": False,
            "wood_stocked": False
        }
        self.stone_count = 0
        self.target_stone = 20
        self.coal_count = 0
        self.target_coal = 10
        self.wood_count = 0
        self.target_wood = 20
        
    def is_complete(self) -> bool:
        """
        Check if Phase 2 objectives are met.
        
        Returns:
            True if all objectives are complete
        """
        return all(self.objectives_completed.values())
    
    def get_objectives(self) -> list:
        """
        Get list of objectives for this phase.
        
        Returns:
            List of objective strings
        """
        return [
            "Mine 20 stone (cobblestone)",
            "Craft stone tools (pickaxe, sword, axe)",
            "Find and mine 10 coal",
            "Craft torches for lighting",
            "Stock up 20 wood"
        ]
    
    def execute(self) -> dict:
        """
        Execute one tick of Phase 2.
        
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
        
        # Check stone collection
        stone_items = [item for item in inventory 
                      if "cobblestone" in item.get("item_id", "") or
                         "stone" in item.get("item_id", "")]
        self.stone_count = sum(item.get("count", 0) for item in stone_items)
        
        if self.stone_count >= self.target_stone:
            self.objectives_completed["stone_mined"] = True
            
        # Check stone tools
        has_pickaxe = self.inventory.has_item("minecraft:stone_pickaxe", inventory)
        has_sword = self.inventory.has_item("minecraft:stone_sword", inventory)
        has_axe = self.inventory.has_item("minecraft:stone_axe", inventory)
        
        if has_pickaxe and has_sword and has_axe:
            self.objectives_completed["stone_tools_crafted"] = True
            
        # Check coal
        coal_items = [item for item in inventory 
                     if "coal" in item.get("item_id", "")]
        self.coal_count = sum(item.get("count", 0) for item in coal_items)
        
        if self.coal_count >= self.target_coal:
            self.objectives_completed["coal_found"] = True
            
        # Check torches
        torch_count = self.inventory.get_item_count("minecraft:torch", inventory)
        if torch_count >= 10:
            self.objectives_completed["torches_crafted"] = True
            
        # Check wood stock
        wood_items = [item for item in inventory 
                     if "log" in item.get("item_id", "") or
                        "planks" in item.get("item_id", "")]
        self.wood_count = sum(item.get("count", 0) for item in wood_items)
        
        if self.wood_count >= self.target_wood:
            self.objectives_completed["wood_stocked"] = True
    
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
        
        # Priority 3: Mine stone if needed
        if not self.objectives_completed["stone_mined"]:
            nearby_blocks = world.get("nearby_blocks", [])
            stone_blocks = [b for b in nearby_blocks 
                           if "stone" in b.get("type", "") or
                              "cobblestone" in b.get("type", "")]
            
            if stone_blocks:
                nearest_stone = stone_blocks[0]
                pos = nearest_stone.get("position", {})
                return {
                    "action": "break_block",
                    "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                    "params": {"hold_ticks": 20},
                    "reasoning": f"Mining stone ({self.stone_count}/{self.target_stone})",
                    "priority": 7,
                    "timeout": 5.0
                }
            else:
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 15},
                    "reasoning": "Searching for stone",
                    "priority": 5,
                    "timeout": 10.0
                }
        
        # Priority 4: Mine coal if needed
        if not self.objectives_completed["coal_found"]:
            nearby_blocks = world.get("nearby_blocks", [])
            coal_blocks = [b for b in nearby_blocks 
                          if "coal_ore" in b.get("type", "")]
            
            if coal_blocks:
                nearest_coal = coal_blocks[0]
                pos = nearest_coal.get("position", {})
                return {
                    "action": "break_block",
                    "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                    "params": {"hold_ticks": 20},
                    "reasoning": f"Mining coal ({self.coal_count}/{self.target_coal})",
                    "priority": 6,
                    "timeout": 5.0
                }
            else:
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 15},
                    "reasoning": "Searching for coal",
                    "priority": 5,
                    "timeout": 10.0
                }
        
        # Priority 5: Craft stone tools
        if not self.objectives_completed["stone_tools_crafted"]:
            if self.stone_count >= 3 and not self.inventory.has_item("minecraft:stone_pickaxe", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:stone_pickaxe", "count": 1},
                    "reasoning": "Crafting stone pickaxe",
                    "priority": 6,
                    "timeout": 3.0
                }
            elif self.stone_count >= 2 and not self.inventory.has_item("minecraft:stone_sword", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:stone_sword", "count": 1},
                    "reasoning": "Crafting stone sword",
                    "priority": 6,
                    "timeout": 3.0
                }
            elif self.stone_count >= 3 and not self.inventory.has_item("minecraft:stone_axe", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:stone_axe", "count": 1},
                    "reasoning": "Crafting stone axe",
                    "priority": 6,
                    "timeout": 3.0
                }
        
        # Priority 6: Craft torches
        if not self.objectives_completed["torches_crafted"] and self.coal_count > 0:
            if self.inventory.has_item("minecraft:stick", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:torch", "count": 4},
                    "reasoning": "Crafting torches",
                    "priority": 5,
                    "timeout": 3.0
                }
            elif self.inventory.has_item("minecraft:wooden_planks", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:stick", "count": 4},
                    "reasoning": "Crafting sticks for torches",
                    "priority": 5,
                    "timeout": 3.0
                }
        
        # Priority 7: Stock up on wood
        if not self.objectives_completed["wood_stocked"]:
            nearby_blocks = world.get("nearby_blocks", [])
            tree_blocks = [b for b in nearby_blocks 
                          if "log" in b.get("type", "")]
            
            if tree_blocks:
                nearest_tree = tree_blocks[0]
                pos = nearest_tree.get("position", {})
                return {
                    "action": "break_block",
                    "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                    "params": {"hold_ticks": 20},
                    "reasoning": f"Chopping wood ({self.wood_count}/{self.target_wood})",
                    "priority": 5,
                    "timeout": 5.0
                }
            else:
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 20},
                    "reasoning": "Searching for trees",
                    "priority": 4,
                    "timeout": 10.0
                }
        
        # Default: Explore
        return {
            "action": "explore",
            "target": None,
            "params": {"direction": "forward", "distance": 10},
            "reasoning": "Phase 2 complete - exploring",
            "priority": 2,
            "timeout": 10.0
        }