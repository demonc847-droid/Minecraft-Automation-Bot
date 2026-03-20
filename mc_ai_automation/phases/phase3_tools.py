"""
Phase 3: Tools
=============

This module implements Phase 3 of the Minecraft speedrun automation.
Goal: Obtain iron tools and armor.

Objectives:
-----------
1. Mine iron ore (Y level 16-64)
2. Build and fuel a furnace
3. Smelt iron ingots
4. Craft iron tools and armor
5. Build a more permanent base
"""

from typing import Dict, Any, List
from actions.movement import Movement
from actions.combat import Combat
from actions.gathering import Gathering
from actions.inventory import Inventory


class Phase3_Tools:
    """
    Phase 3: Tools
    
    Goal: Obtain iron tools and armor.
    
    Objectives:
    1. Mine iron ore (Y level 16-64)
    2. Build and fuel a furnace
    3. Smelt iron ingots
    4. Craft iron tools and armor
    5. Build a more permanent base
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
            "iron_ore_mined": False,
            "furnace_built": False,
            "iron_smelted": False,
            "iron_tools_crafted": False,
            "iron_armor_crafted": False
        }
        self.iron_ore_count = 0
        self.target_iron_ore = 30  # Need enough for tools and armor
        self.iron_ingot_count = 0
        
    def is_complete(self) -> bool:
        """
        Check if Phase 3 objectives are met.
        
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
            "Mine 30 iron ore",
            "Build a furnace",
            "Smelt iron ingots",
            "Craft iron tools (pickaxe, sword, axe)",
            "Craft iron armor (helmet, chestplate, leggings, boots)"
        ]
    
    def execute(self) -> dict:
        """
        Execute one tick of Phase 3.
        
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
        
        # Check iron ore
        iron_ore_items = [item for item in inventory 
                         if "iron_ore" in item.get("item_id", "")]
        self.iron_ore_count = sum(item.get("count", 0) for item in iron_ore_items)
        
        if self.iron_ore_count >= self.target_iron_ore:
            self.objectives_completed["iron_ore_mined"] = True
            
        # Check furnace
        if self.inventory.has_item("minecraft:furnace", inventory):
            self.objectives_completed["furnace_built"] = True
            
        # Check iron ingots
        iron_ingot_items = [item for item in inventory 
                           if "iron_ingot" in item.get("item_id", "")]
        self.iron_ingot_count = sum(item.get("count", 0) for item in iron_ingot_items)
        
        if self.iron_ingot_count >= 5:  # At least some smelted
            self.objectives_completed["iron_smelted"] = True
            
        # Check iron tools
        has_pickaxe = self.inventory.has_item("minecraft:iron_pickaxe", inventory)
        has_sword = self.inventory.has_item("minecraft:iron_sword", inventory)
        has_axe = self.inventory.has_item("minecraft:iron_axe", inventory)
        
        if has_pickaxe and has_sword and has_axe:
            self.objectives_completed["iron_tools_crafted"] = True
            
        # Check iron armor
        has_helmet = self.inventory.has_item("minecraft:iron_helmet", inventory)
        has_chestplate = self.inventory.has_item("minecraft:iron_chestplate", inventory)
        has_leggings = self.inventory.has_item("minecraft:iron_leggings", inventory)
        has_boots = self.inventory.has_item("minecraft:iron_boots", inventory)
        
        if has_helmet and has_chestplate and has_leggings and has_boots:
            self.objectives_completed["iron_armor_crafted"] = True
    
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
        
        # Priority 3: Mine iron ore if needed
        if not self.objectives_completed["iron_ore_mined"]:
            nearby_blocks = world.get("nearby_blocks", [])
            iron_blocks = [b for b in nearby_blocks 
                          if "iron_ore" in b.get("type", "")]
            
            if iron_blocks:
                nearest_iron = iron_blocks[0]
                pos = nearest_iron.get("position", {})
                return {
                    "action": "break_block",
                    "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                    "params": {"hold_ticks": 20},
                    "reasoning": f"Mining iron ore ({self.iron_ore_count}/{self.target_iron_ore})",
                    "priority": 7,
                    "timeout": 5.0
                }
            else:
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 15},
                    "reasoning": "Searching for iron ore",
                    "priority": 5,
                    "timeout": 10.0
                }
        
        # Priority 4: Build furnace
        if not self.objectives_completed["furnace_built"]:
            cobblestone_count = self.inventory.get_item_count("minecraft:cobblestone", inventory)
            if cobblestone_count >= 8:
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:furnace", "count": 1},
                    "reasoning": "Crafting furnace",
                    "priority": 6,
                    "timeout": 3.0
                }
            else:
                # Mine more cobblestone
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
                        "reasoning": f"Mining cobblestone for furnace ({cobblestone_count}/8)",
                        "priority": 6,
                        "timeout": 5.0
                    }
        
        # Priority 5: Smelt iron (simplified - just assume it happens)
        if not self.objectives_completed["iron_smelted"] and self.iron_ore_count > 0:
            # In a real implementation, this would place furnace, add fuel and ore
            # For now, we just wait for smelting
            return {
                "action": "wait",
                "target": None,
                "params": {"duration": 5.0},
                "reasoning": "Smelting iron ingots",
                "priority": 5,
                "timeout": 10.0
            }
        
        # Priority 6: Craft iron tools
        if not self.objectives_completed["iron_tools_crafted"]:
            if self.iron_ingot_count >= 3 and not self.inventory.has_item("minecraft:iron_pickaxe", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:iron_pickaxe", "count": 1},
                    "reasoning": "Crafting iron pickaxe",
                    "priority": 6,
                    "timeout": 3.0
                }
            elif self.iron_ingot_count >= 2 and not self.inventory.has_item("minecraft:iron_sword", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:iron_sword", "count": 1},
                    "reasoning": "Crafting iron sword",
                    "priority": 6,
                    "timeout": 3.0
                }
            elif self.iron_ingot_count >= 3 and not self.inventory.has_item("minecraft:iron_axe", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:iron_axe", "count": 1},
                    "reasoning": "Crafting iron axe",
                    "priority": 6,
                    "timeout": 3.0
                }
        
        # Priority 7: Craft iron armor
        if not self.objectives_completed["iron_armor_crafted"]:
            if self.iron_ingot_count >= 5 and not self.inventory.has_item("minecraft:iron_helmet", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:iron_helmet", "count": 1},
                    "reasoning": "Crafting iron helmet",
                    "priority": 5,
                    "timeout": 3.0
                }
            elif self.iron_ingot_count >= 8 and not self.inventory.has_item("minecraft:iron_chestplate", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:iron_chestplate", "count": 1},
                    "reasoning": "Crafting iron chestplate",
                    "priority": 5,
                    "timeout": 3.0
                }
            elif self.iron_ingot_count >= 7 and not self.inventory.has_item("minecraft:iron_leggings", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:iron_leggings", "count": 1},
                    "reasoning": "Crafting iron leggings",
                    "priority": 5,
                    "timeout": 3.0
                }
            elif self.iron_ingot_count >= 4 and not self.inventory.has_item("minecraft:iron_boots", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:iron_boots", "count": 1},
                    "reasoning": "Crafting iron boots",
                    "priority": 5,
                    "timeout": 3.0
                }
        
        # Default: Explore
        return {
            "action": "explore",
            "target": None,
            "params": {"direction": "forward", "distance": 10},
            "reasoning": "Phase 3 complete - exploring",
            "priority": 2,
            "timeout": 10.0
        }