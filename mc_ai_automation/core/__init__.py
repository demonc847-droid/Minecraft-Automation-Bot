"""
Core Systems Module
==================

This module contains the core systems for Minecraft AI automation:
- Memory reading from the Minecraft process
- Game state representation (Player, Inventory, World)
- Input simulation (mouse and keyboard control)

Components:
-----------
- MemoryReader: Attach to Minecraft process and read game state
- PlayerState: Player position, health, status
- InventoryState: Inventory contents and management
- WorldState: World/chunk data and nearby entities
- InputSimulator: Mouse and keyboard input control

Usage:
------
    from core import MemoryReader, InputSimulator
    
    reader = MemoryReader()
    state = reader.get_game_state()
    
    simulator = InputSimulator()
    simulator.move_to(100, 200)
"""

from .memory_reader import MemoryReader, GameState
from .player_state import PlayerState
from .inventory_state import InventoryState, ItemStack
from .world_state import WorldState, Position, Entity, Block, LookingAt
from .input_simulator import InputSimulator

__all__ = [
    'MemoryReader',
    'GameState',
    'PlayerState',
    'InventoryState',
    'ItemStack',
    'WorldState',
    'Position',
    'Entity',
    'Block',
    'LookingAt',
    'InputSimulator',
]
