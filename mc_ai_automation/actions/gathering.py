"""
Gathering Actions Module
=======================

This module provides resource gathering functions for Minecraft automation.
Handles mining, chopping trees, and collecting drops.

Classes:
--------
- Gathering: Main class for gathering actions
"""

import time
from typing import List, Tuple, Optional, Dict, Any

from core.input_simulator import (
    break_block as input_break_block,
    use_item as input_use_item,
    look_at_position,
    select_slot,
    move_to
)


class Gathering:
    """
    Resource gathering actions for Minecraft automation.
    
    This class provides methods for gathering resources,
    including mining blocks, chopping trees, and collecting drops.
    """
    
    # Block types that require specific tools
    TOOL_REQUIREMENTS = {
        "minecraft:stone": "pickaxe",
        "minecraft:iron_ore": "pickaxe",
        "minecraft:gold_ore": "pickaxe",
        "minecraft:diamond_ore": "pickaxe",
        "minecraft:deepslate_diamond_ore": "pickaxe",
        "minecraft:obsidian": "diamond_pickaxe",
        "minecraft:ancient_debris": "diamond_pickaxe",
        "minecraft:coal_ore": "pickaxe",
        "minecraft:lapis_ore": "pickaxe",
        "minecraft:redstone_ore": "pickaxe",
        "minecraft:emerald_ore": "pickaxe",
        "minecraft:oak_log": "axe",
        "minecraft:birch_log": "axe",
        "minecraft:spruce_log": "axe",
        "minecraft:jungle_log": "axe",
        "minecraft:acacia_log": "axe",
        "minecraft:dark_oak_log": "axe",
        "minecraft:mangrove_log": "axe",
        "minecraft:dirt": "shovel",
        "minecraft:grass_block": "shovel",
        "minecraft:gravel": "shovel",
        "minecraft:sand": "shovel",
        "minecraft:clay": "shovel",
    }
    
    # Blocks that drop items when broken
    VALUABLE_DROPS = [
        "minecraft:diamond_ore", "minecraft:deepslate_diamond_ore",
        "minecraft:iron_ore", "minecraft:gold_ore", "minecraft:lapis_ore",
        "minecraft:redstone_ore", "minecraft:emerald_ore", "minecraft:coal_ore",
        "minecraft:ancient_debris"
    ]
    
    def __init__(self):
        """Initialize the Gathering module."""
        self.is_mining = False
        self.last_mine_time = 0
        
    def mine_block(self, block_type: str = None, position: Tuple[int, int, int] = None,
                   hold_ticks: int = 20) -> None:
        """
        Mine a block at the specified position.
        
        Args:
            block_type: Type of block to mine (e.g., "minecraft:stone")
            position: Position of the block (x, y, z)
            hold_ticks: Number of ticks to hold the break button
        """
        if position:
            # Look at the block first
            look_at_position(position[0], position[1], position[2])
            time.sleep(0.05)
        
        # Check for tool requirements
        if block_type and block_type in self.TOOL_REQUIREMENTS:
            required_tool = self.TOOL_REQUIREMENTS[block_type]
            # Note: In a full implementation, we'd check if we have the right tool equipped
        
        # Mine the block
        self.is_mining = True
        input_break_block(hold_ticks)
        self.last_mine_time = time.time()
        self.is_mining = False
        
    def collect_drops(self, game_state: Dict[str, Any] = None) -> None:
        """
        Collect dropped items nearby.
        
        Args:
            game_state: Current game state with item drop information
        """
        # Move around to pick up items
        # Items are picked up automatically when close enough
        # We just need to move around the area
        time.sleep(0.5)  # Wait for items to be picked up
        
    def chop_tree(self, base_position: Tuple[float, float, float]) -> None:
        """
        Chop down a tree starting from the base.
        
        Args:
            base_position: Position of the tree base (x, y, z)
        """
        x, y, z = base_position
        
        # Chop each log block going up
        for i in range(10):  # Max tree height
            block_y = y + i
            
            # Look at the log block
            look_at_position(x, block_y, z)
            time.sleep(0.05)
            
            # Chop the block
            self.mine_block("minecraft:oak_log", (x, block_y, z), hold_ticks=20)
            time.sleep(0.1)
            
            # Collect drops (move around to pick up items)
            self.collect_drops()
        
    def mine_vein(self, block_type: str, start_position: Tuple[int, int, int],
                  max_blocks: int = 20) -> int:
        """
        Mine an entire vein of blocks.
        
        Args:
            block_type: Type of block to mine
            start_position: Starting position (x, y, z)
            max_blocks: Maximum number of blocks to mine
            
        Returns:
            Number of blocks mined
        """
        mined_count = 0
        positions_to_mine = [start_position]
        mined_positions = set()
        
        while positions_to_mine and mined_count < max_blocks:
            pos = positions_to_mine.pop(0)
            
            if pos in mined_positions:
                continue
                
            # Mine the block
            self.mine_block(block_type, pos)
            mined_positions.add(pos)
            mined_count += 1
            
            # Collect drops periodically
            if mined_count % 5 == 0:
                self.collect_drops()
            
            # Small delay between blocks
            time.sleep(0.1)
        
        return mined_count
        
    def strip_mine(self, direction: str = "north", length: int = 100,
                   height: int = 2) -> None:
        """
        Strip mine in a direction.
        
        Args:
            direction: Direction to mine - "north", "south", "east", "west"
            length: How far to mine
            height: Height of the tunnel
        """
        # This is a simplified implementation
        # A full version would handle movement and mining simultaneously
        for i in range(length):
            # Mine forward
            self.mine_block("minecraft:stone", hold_ticks=20)
            time.sleep(0.1)
            
            # Collect drops
            if i % 10 == 0:
                self.collect_drops()
                
    def mine_at_level(self, y_level: int = -59, area_size: int = 10) -> None:
        """
        Mine at a specific Y level (for diamonds, etc.).
        
        Args:
            y_level: Y coordinate to mine at
            area_size: Size of the area to mine (x and z)
        """
        # Mine in a grid pattern
        for x in range(-area_size // 2, area_size // 2):
            for z in range(-area_size // 2, area_size // 2):
                self.mine_block("minecraft:deepslate", hold_ticks=20)
                time.sleep(0.1)
                
    def is_valuable_block(self, block_type: str) -> bool:
        """
        Check if a block type is valuable.
        
        Args:
            block_type: Type of block to check
            
        Returns:
            True if the block is valuable, False otherwise
        """
        return block_type in self.VALUABLE_DROPS
        
    def get_required_tool(self, block_type: str) -> Optional[str]:
        """
        Get the tool required to mine a block.
        
        Args:
            block_type: Type of block
            
        Returns:
            Required tool type, or None if no tool required
        """
        return self.TOOL_REQUIREMENTS.get(block_type)
        
    def can_mine_block(self, block_type: str, inventory: List[Dict] = None) -> bool:
        """
        Check if we can mine a block with our current tools.
        
        Args:
            block_type: Type of block to mine
            inventory: Current inventory items
            
        Returns:
            True if we can mine the block, False otherwise
        """
        if block_type not in self.TOOL_REQUIREMENTS:
            return True  # No tool required
            
        required_tool = self.TOOL_REQUIREMENTS[block_type]
        
        if inventory is None:
            return True  # Assume we have tools if inventory not provided
            
        # Check if we have the required tool
        for item in inventory:
            item_id = item.get("item_id", "")
            if required_tool in item_id:
                return True
                
        return False
        
    def find_nearest_block(self, block_type: str, game_state: Dict[str, Any]) -> Optional[Tuple[int, int, int]]:
        """
        Find the nearest block of a specific type.
        
        Args:
            block_type: Type of block to find
            game_state: Current game state
            
        Returns:
            Position of the nearest block, or None if not found
        """
        nearby_blocks = game_state.get("world", {}).get("nearby_blocks", [])
        
        nearest_block = None
        nearest_distance = float('inf')
        
        for block in nearby_blocks:
            if block.get("type") == block_type:
                pos = block.get("position", {})
                # Calculate distance (simplified)
                distance = abs(pos.get("x", 0)) + abs(pos.get("y", 0)) + abs(pos.get("z", 0))
                
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_block = (pos.get("x", 0), pos.get("y", 0), pos.get("z", 0))
                    
        return nearest_block
        
    def gather_resource(self, resource_type: str, game_state: Dict[str, Any],
                       count: int = 1) -> int:
        """
        Gather a specific resource.
        
        Args:
            resource_type: Type of resource to gather (e.g., "wood", "stone", "iron")
            game_state: Current game state
            count: Number of items to gather
            
        Returns:
            Number of items gathered
        """
        gathered = 0
        
        # Map resource types to block types
        resource_to_blocks = {
            "wood": ["minecraft:oak_log", "minecraft:birch_log", "minecraft:spruce_log"],
            "stone": ["minecraft:stone", "minecraft:cobblestone"],
            "iron": ["minecraft:iron_ore", "minecraft:deepslate_iron_ore"],
            "diamond": ["minecraft:diamond_ore", "minecraft:deepslate_diamond_ore"],
            "coal": ["minecraft:coal_ore"],
        }
        
        block_types = resource_to_blocks.get(resource_type, [])
        
        for block_type in block_types:
            while gathered < count:
                position = self.find_nearest_block(block_type, game_state)
                if position is None:
                    break
                    
                self.mine_block(block_type, position)
                gathered += 1
                time.sleep(0.1)
                
        return gathered