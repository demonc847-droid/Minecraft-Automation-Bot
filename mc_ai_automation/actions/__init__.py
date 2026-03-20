"""
Actions Module
==============

This module contains atomic action implementations for Minecraft automation:
- Movement actions (walking, sprinting, navigating)
- Combat actions (attacking, defending, fleeing)
- Gathering actions (mining, chopping, collecting)
- Inventory actions (crafting, equipping, organizing)

Components:
-----------
- Movement: Movement and navigation functions
- Combat: Combat and defense functions
- Gathering: Resource gathering functions
- Inventory: Inventory management functions

Usage:
------
    from actions import Movement, Combat
    
    movement = Movement()
    movement.walk_to(100, 200)
    
    combat = Combat()
    combat.attack_entity("zombie")
"""

from .movement import Movement
from .combat import Combat
from .gathering import Gathering
from .inventory import Inventory

__all__ = [
    'Movement',
    'Combat',
    'Gathering',
    'Inventory',
]