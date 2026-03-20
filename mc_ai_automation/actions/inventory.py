"""
Inventory Management Actions Module
===================================

This module provides inventory management functions for Minecraft automation.
Handles crafting, equipping, organizing, and checking inventory.

Classes:
--------
- Inventory: Main class for inventory actions
"""

import time
from typing import List, Tuple, Optional, Dict, Any

from core.input_simulator import (
    open_inventory as input_open_inventory,
    close_inventory as input_close_inventory,
    select_slot as input_select_slot,
    drop_item as input_drop_item,
    move_item as input_move_item,
    use_item as input_use_item
)


class Inventory:
    """
    Inventory management actions for Minecraft automation.
    
    This class provides methods for managing the player's inventory,
    including crafting items, equipping gear, and organizing items.
    """
    
    # Crafting recipes (simplified)
    CRAFTING_RECIPES = {
        "minecraft:wooden_planks": {
            "ingredients": {"minecraft:oak_log": 1},
            "result_count": 4
        },
        "minecraft:stick": {
            "ingredients": {"minecraft:wooden_planks": 2},
            "result_count": 4
        },
        "minecraft:crafting_table": {
            "ingredients": {"minecraft:wooden_planks": 4},
            "result_count": 1
        },
        "minecraft:wooden_pickaxe": {
            "ingredients": {"minecraft:wooden_planks": 3, "minecraft:stick": 2},
            "result_count": 1
        },
        "minecraft:wooden_sword": {
            "ingredients": {"minecraft:wooden_planks": 2, "minecraft:stick": 1},
            "result_count": 1
        },
        "minecraft:wooden_axe": {
            "ingredients": {"minecraft:wooden_planks": 3, "minecraft:stick": 2},
            "result_count": 1
        },
        "minecraft:stone_pickaxe": {
            "ingredients": {"minecraft:cobblestone": 3, "minecraft:stick": 2},
            "result_count": 1
        },
        "minecraft:stone_sword": {
            "ingredients": {"minecraft:cobblestone": 2, "minecraft:stick": 1},
            "result_count": 1
        },
        "minecraft:iron_pickaxe": {
            "ingredients": {"minecraft:iron_ingot": 3, "minecraft:stick": 2},
            "result_count": 1
        },
        "minecraft:iron_sword": {
            "ingredients": {"minecraft:iron_ingot": 2, "minecraft:stick": 1},
            "result_count": 1
        },
        "minecraft:iron_helmet": {
            "ingredients": {"minecraft:iron_ingot": 5},
            "result_count": 1
        },
        "minecraft:iron_chestplate": {
            "ingredients": {"minecraft:iron_ingot": 8},
            "result_count": 1
        },
        "minecraft:iron_leggings": {
            "ingredients": {"minecraft:iron_ingot": 7},
            "result_count": 1
        },
        "minecraft:iron_boots": {
            "ingredients": {"minecraft:iron_ingot": 4},
            "result_count": 1
        },
        "minecraft:diamond_pickaxe": {
            "ingredients": {"minecraft:diamond": 3, "minecraft:stick": 2},
            "result_count": 1
        },
        "minecraft:diamond_sword": {
            "ingredients": {"minecraft:diamond": 2, "minecraft:stick": 1},
            "result_count": 1
        },
        "minecraft:torch": {
            "ingredients": {"minecraft:coal": 1, "minecraft:stick": 1},
            "result_count": 4
        },
        "minecraft:furnace": {
            "ingredients": {"minecraft:cobblestone": 8},
            "result_count": 1
        },
        "minecraft:chest": {
            "ingredients": {"minecraft:wooden_planks": 8},
            "result_count": 1
        },
        "minecraft:shield": {
            "ingredients": {"minecraft:iron_ingot": 1, "minecraft:wooden_planks": 6},
            "result_count": 1
        },
        "minecraft:bow": {
            "ingredients": {"minecraft:stick": 3, "minecraft:string": 3},
            "result_count": 1
        },
        "minecraft:arrow": {
            "ingredients": {"minecraft:flint": 1, "minecraft:stick": 1, "minecraft:feather": 1},
            "result_count": 4
        },
    }
    
    # Item categories
    TOOLS = ["pickaxe", "sword", "axe", "shovel", "hoe"]
    ARMOR = ["helmet", "chestplate", "leggings", "boots"]
    FOOD = ["bread", "steak", "cooked_porkchop", "golden_apple", "apple", "carrot", "potato"]
    
    def __init__(self):
        """Initialize the Inventory module."""
        self.inventory_open = False
        
    def open_inventory(self) -> None:
        """Open the player's inventory."""
        if not self.inventory_open:
            input_open_inventory()
            self.inventory_open = True
            time.sleep(0.1)
            
    def close_inventory(self) -> None:
        """Close the player's inventory."""
        if self.inventory_open:
            input_close_inventory()
            self.inventory_open = False
            time.sleep(0.1)
            
    def select_slot(self, slot: int) -> None:
        """
        Select a hotbar slot.
        
        Args:
            slot: Slot number (0-8 for hotbar)
        """
        input_select_slot(slot)
        
    def craft_item(self, item_id: str, count: int = 1, 
                   inventory: List[Dict] = None) -> bool:
        """
        Craft an item.
        
        Args:
            item_id: Item ID to craft (e.g., "minecraft:wooden_pickaxe")
            count: Number of items to craft
            inventory: Current inventory items
            
        Returns:
            True if crafting succeeded, False otherwise
        """
        recipe = self.CRAFTING_RECIPES.get(item_id)
        if recipe is None:
            return False
            
        # Check if we have ingredients
        if inventory:
            if not self._has_ingredients(recipe["ingredients"], inventory):
                return False
        
        # Open inventory for crafting
        self.open_inventory()
        
        # Simulate crafting (in a real implementation, this would
        # interact with the crafting interface)
        time.sleep(0.5 * count)  # Simulate crafting time
        
        # Close inventory
        self.close_inventory()
        
        return True
        
    def _has_ingredients(self, ingredients: Dict[str, int], 
                        inventory: List[Dict]) -> bool:
        """
        Check if we have all required ingredients.
        
        Args:
            ingredients: Dict of item_id to required count
            inventory: Current inventory items
            
        Returns:
            True if all ingredients are available
        """
        # Count items in inventory
        item_counts = {}
        for item in inventory:
            item_id = item.get("item_id", "")
            count = item.get("count", 0)
            item_counts[item_id] = item_counts.get(item_id, 0) + count
            
        # Check each ingredient
        for item_id, required_count in ingredients.items():
            available = item_counts.get(item_id, 0)
            if available < required_count:
                return False
                
        return True
        
    def equip_item(self, item_id: str, inventory: List[Dict] = None) -> bool:
        """
        Equip an item (tool or armor).
        
        Args:
            item_id: Item ID to equip
            inventory: Current inventory items
            
        Returns:
            True if equipping succeeded, False otherwise
        """
        if inventory is None:
            return False
            
        # Find the item in inventory
        item_slot = None
        for item in inventory:
            if item.get("item_id") == item_id:
                item_slot = item.get("slot")
                break
                
        if item_slot is None:
            return False
            
        # Select the item's slot
        self.select_slot(item_slot)
        
        # Use the item to equip it (for armor) or just hold it (for tools)
        input_use_item(10)
        
        return True
        
    def organize_inventory(self, inventory: List[Dict] = None) -> None:
        """
        Organize inventory items by category.
        
        Args:
            inventory: Current inventory items
        """
        if inventory is None:
            return
            
        self.open_inventory()
        
        # Sort items into categories
        tools = []
        armor = []
        food = []
        blocks = []
        other = []
        
        for item in inventory:
            item_id = item.get("item_id", "")
            
            if any(tool in item_id for tool in self.TOOLS):
                tools.append(item)
            elif any(arm in item_id for arm in self.ARMOR):
                armor.append(item)
            elif any(f in item_id for f in self.FOOD):
                food.append(item)
            elif "planks" in item_id or "log" in item_id or "cobblestone" in item_id:
                blocks.append(item)
            else:
                other.append(item)
        
        # Reorganize by moving items
        # This is a simplified version - full implementation would
        # actually move items to specific slots
        time.sleep(0.5)
        
        self.close_inventory()
        
    def has_item(self, item_id: str, inventory: List[Dict] = None,
                 min_count: int = 1) -> bool:
        """
        Check if we have a specific item.
        
        Args:
            item_id: Item ID to check for
            inventory: Current inventory items
            min_count: Minimum count required
            
        Returns:
            True if item is available in sufficient quantity
        """
        if inventory is None:
            return False
            
        total_count = 0
        for item in inventory:
            if item.get("item_id") == item_id:
                total_count += item.get("count", 0)
                
        return total_count >= min_count
        
    def get_item_count(self, item_id: str, inventory: List[Dict] = None) -> int:
        """
        Get the count of a specific item.
        
        Args:
            item_id: Item ID to count
            inventory: Current inventory items
            
        Returns:
            Total count of the item
        """
        if inventory is None:
            return 0
            
        total_count = 0
        for item in inventory:
            if item.get("item_id") == item_id:
                total_count += item.get("count", 0)
                
        return total_count
        
    def get_best_tool(self, task: str, inventory: List[Dict] = None) -> Optional[str]:
        """
        Get the best tool for a specific task.
        
        Args:
            task: Task type (e.g., "mining", "fighting", "chopping")
            inventory: Current inventory items
            
        Returns:
            Item ID of the best tool, or None if no tool available
        """
        if inventory is None:
            return None
            
        # Tool preference by material (best to worst)
        materials = ["netherite", "diamond", "iron", "stone", "wooden"]
        
        tool_types = {
            "mining": "pickaxe",
            "fighting": "sword",
            "chopping": "axe",
            "digging": "shovel"
        }
        
        tool_type = tool_types.get(task, "pickaxe")
        
        # Find best tool
        for material in materials:
            tool_id = f"minecraft:{material}_{tool_type}"
            if self.has_item(tool_id, inventory):
                return tool_id
                
        return None
        
    def get_best_armor(self, inventory: List[Dict] = None) -> Dict[str, Optional[str]]:
        """
        Get the best armor pieces available.
        
        Args:
            inventory: Current inventory items
            
        Returns:
            Dict mapping armor slots to best item IDs
        """
        if inventory is None:
            return {"head": None, "chest": None, "legs": None, "feet": None}
            
        # Armor preference by material (best to worst)
        materials = ["netherite", "diamond", "iron", "chainmail", "leather"]
        
        armor_types = {
            "head": "helmet",
            "chest": "chestplate",
            "legs": "leggings",
            "feet": "boots"
        }
        
        best_armor = {}
        
        for slot, armor_type in armor_types.items():
            best_armor[slot] = None
            for material in materials:
                armor_id = f"minecraft:{material}_{armor_type}"
                if self.has_item(armor_id, inventory):
                    best_armor[slot] = armor_id
                    break
                    
        return best_armor
        
    def drop_item(self, item_id: str, all: bool = False,
                  inventory: List[Dict] = None) -> bool:
        """
        Drop an item from inventory.
        
        Args:
            item_id: Item ID to drop
            all: If True, drop entire stack
            inventory: Current inventory items
            
        Returns:
            True if item was dropped, False otherwise
        """
        if inventory is None:
            return False
            
        # Find the item
        for item in inventory:
            if item.get("item_id") == item_id:
                slot = item.get("slot")
                self.select_slot(slot)
                input_drop_item(all)
                return True
                
        return False
        
    def get_food_items(self, inventory: List[Dict] = None) -> List[Dict]:
        """
        Get all food items in inventory.
        
        Args:
            inventory: Current inventory items
            
        Returns:
            List of food items
        """
        if inventory is None:
            return []
            
        food_items = []
        for item in inventory:
            item_id = item.get("item_id", "")
            if any(f in item_id for f in self.FOOD):
                food_items.append(item)
                
        return food_items
        
    def get_tool_durability(self, item_id: str, inventory: List[Dict] = None) -> Optional[int]:
        """
        Get the durability of a tool.
        
        Args:
            item_id: Item ID to check
            inventory: Current inventory items
            
        Returns:
            Remaining durability, or None if not found
        """
        if inventory is None:
            return None
            
        for item in inventory:
            if item.get("item_id") == item_id:
                # In Minecraft, damage value represents durability used
                damage = item.get("damage", 0)
                # This is simplified - actual max durability varies by tool
                max_durability = 1561  # Diamond tool durability
                return max_durability - damage
                
        return None