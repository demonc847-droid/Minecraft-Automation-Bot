"""
Phase 1: Foundation
==================

This module implements Phase 1 of the Minecraft speedrun automation.
Goal: Establish basic survival - wooden tools, shelter, and food source.

Objectives:
-----------
1. Find trees and collect wood
2. Craft wooden tools (pickaxe, sword)
3. Find or build basic shelter
4. Locate food source (animals, crops)
"""

from typing import Dict, Any, List, Tuple
from abc import ABC, abstractmethod

from actions.movement import Movement
from actions.combat import Combat
from actions.gathering import Gathering
from actions.inventory import Inventory


class Phase:
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
        self.movement = Movement()
        self.combat = Combat()
        self.gathering = Gathering()
        self.inventory = Inventory()
        
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
        action_type = action.get("action", "none")
        target = action.get("target")
        params = action.get("params", {})
        
        if action_type == "move_to":
            x, y, z = target if target else (0, 0, 0)
            speed = params.get("speed", "walk")
            self.movement.walk_to(x, z, speed)
        elif action_type == "look_at":
            x, y, z = target if target else (0, 0, 0)
            self.movement.look_at_target(x, y, z)
        elif action_type == "jump":
            self.movement.jump()
        elif action_type == "attack":
            hold_ticks = params.get("hold_ticks", 10)
            self.combat.attack_entity(hold_ticks=hold_ticks)
        elif action_type == "defend":
            duration = params.get("duration", 1.0)
            self.combat.defend(duration)
        elif action_type == "use_item":
            hold_ticks = params.get("hold_ticks", 10)
            # Use item via input simulator
        elif action_type == "place_block":
            # Place block via input simulator
            pass
        elif action_type == "break_block":
            hold_ticks = params.get("hold_ticks", 20)
            self.gathering.mine_block(hold_ticks=hold_ticks)
        elif action_type == "select_slot":
            slot = params.get("slot", 0)
            self.inventory.select_slot(slot)
        elif action_type == "craft_item":
            item_id = params.get("item_id", "")
            count = params.get("count", 1)
            self.inventory.craft_item(item_id, count)
        elif action_type == "equip_item":
            item_id = params.get("item_id", "")
            self.inventory.equip_item(item_id)
        elif action_type == "explore":
            direction = params.get("direction", "forward")
            distance = params.get("distance", 10)
            # Explore the area
        elif action_type == "flee":
            x, y, z = target if target else (0, 0, 0)
            self.combat.flee_from((x, y, z))
        elif action_type == "wait":
            import time
            duration = params.get("duration", 1.0)
            time.sleep(duration)
        # "none" action does nothing


class Phase1_Foundation(Phase):
    """
    Phase 1: Foundation
    
    Goal: Establish basic survival - wooden tools, shelter, and food source.
    
    Objectives:
    1. Find trees and collect wood
    2. Craft wooden tools (pickaxe, sword)
    3. Find or build basic shelter
    4. Locate food source (animals, crops)
    """
    
    def __init__(self, game_state_provider, action_decider):
        super().__init__(game_state_provider, action_decider)
        self.objectives_completed = {
            "wood_collected": False,
            "tools_crafted": False,
            "shelter_found": False,
            "food_located": False
        }
        self.wood_count = 0
        self.target_wood = 10  # Need at least 10 wood
        
    def is_complete(self) -> bool:
        """
        Check if Phase 1 objectives are met.
        
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
            "Collect 10 wood (logs)",
            "Craft wooden tools (pickaxe, sword)",
            "Find or build basic shelter",
            "Locate food source"
        ]
    
    def execute(self) -> dict:
        """
        Execute one tick of Phase 1.
        
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
        
        # Check wood collection
        wood_items = [item for item in inventory 
                     if "log" in item.get("item_id", "")]
        self.wood_count = sum(item.get("count", 0) for item in wood_items)
        
        if self.wood_count >= self.target_wood:
            self.objectives_completed["wood_collected"] = True
            
        # Check tools crafted
        has_pickaxe = self.inventory.has_item("minecraft:wooden_pickaxe", inventory)
        has_sword = self.inventory.has_item("minecraft:wooden_sword", inventory)
        if has_pickaxe and has_sword:
            self.objectives_completed["tools_crafted"] = True
            
        # Check shelter (simplified - just check if it's day or we're underground)
        player = state.get("player", {})
        time_of_day = state.get("world", {}).get("time_of_day", 0)
        y_level = player.get("position", {}).get("y", 64)
        
        # Consider "shelter" found if it's day or we're below surface
        if 1000 < time_of_day < 13000 or y_level < 60:
            self.objectives_completed["shelter_found"] = True
            
        # Check food source
        food_items = self.inventory.get_food_items(inventory)
        nearby_animals = [e for e in state.get("world", {}).get("nearby_entities", [])
                         if not e.get("is_hostile", False) and 
                         any(animal in e.get("type", "") 
                             for animal in ["pig", "cow", "chicken", "sheep"])]
        
        if len(food_items) > 0 or len(nearby_animals) > 0:
            self.objectives_completed["food_located"] = True
    
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
                "reasoning": "High threat level detected - fleeing",
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
        
        # Priority 2: Low health - eat or find food
        health = player.get("health", 20)
        hunger = player.get("hunger", 20)
        
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
        
        # Priority 3: Collect wood if needed
        if not self.objectives_completed["wood_collected"]:
            # Find nearest tree (log block)
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
                    "reasoning": f"Chopping tree for wood ({self.wood_count}/{self.target_wood})",
                    "priority": 7,
                    "timeout": 5.0
                }
            else:
                # Explore to find trees
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 20},
                    "reasoning": "Searching for trees",
                    "priority": 5,
                    "timeout": 10.0
                }
        
        # Priority 4: Craft tools if we have wood
        if self.objectives_completed["wood_collected"] and not self.objectives_completed["tools_crafted"]:
            # Convert logs to planks first
            if self.inventory.has_item("minecraft:oak_log", inventory):
                return {
                    "action": "craft_item",
                    "target": None,
                    "params": {"item_id": "minecraft:wooden_planks", "count": 1},
                    "reasoning": "Converting logs to planks",
                    "priority": 6,
                    "timeout": 3.0
                }
            elif self.inventory.has_item("minecraft:wooden_planks", inventory, min_count=5):
                # Craft pickaxe
                if not self.inventory.has_item("minecraft:wooden_pickaxe", inventory):
                    return {
                        "action": "craft_item",
                        "target": None,
                        "params": {"item_id": "minecraft:wooden_pickaxe", "count": 1},
                        "reasoning": "Crafting wooden pickaxe",
                        "priority": 6,
                        "timeout": 3.0
                    }
                # Craft sword
                elif not self.inventory.has_item("minecraft:wooden_sword", inventory):
                    return {
                        "action": "craft_item",
                        "target": None,
                        "params": {"item_id": "minecraft:wooden_sword", "count": 1},
                        "reasoning": "Crafting wooden sword",
                        "priority": 6,
                        "timeout": 3.0
                    }
        
        # Priority 5: Find shelter if it's getting dark
        time_of_day = world.get("time_of_day", 0)
        if not self.objectives_completed["shelter_found"]:
            if time_of_day > 12000:  # Getting dark
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 10},
                    "reasoning": "Looking for shelter before night",
                    "priority": 7,
                    "timeout": 10.0
                }
        
        # Priority 6: Find food source
        if not self.objectives_completed["food_located"]:
            nearby_entities = world.get("nearby_entities", [])
            animals = [e for e in nearby_entities 
                      if not e.get("is_hostile", False) and
                      any(animal in e.get("type", "") 
                          for animal in ["pig", "cow", "chicken", "sheep"])]
            
            if animals:
                nearest_animal = animals[0]
                pos = nearest_animal.get("position", {})
                return {
                    "action": "attack",
                    "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                    "params": {"hold_ticks": 15},
                    "reasoning": f"Hunting {nearest_animal.get('type')} for food",
                    "priority": 5,
                    "timeout": 5.0
                }
            else:
                return {
                    "action": "explore",
                    "target": None,
                    "params": {"direction": "forward", "distance": 15},
                    "reasoning": "Searching for animals to hunt",
                    "priority": 4,
                    "timeout": 10.0
                }
        
        # Default: Wait or explore
        return {
            "action": "explore",
            "target": None,
            "params": {"direction": "forward", "distance": 10},
            "reasoning": "Phase 1 objectives complete - exploring",
            "priority": 2,
            "timeout": 10.0
        }