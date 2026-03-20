"""
Phases Module
=============

This module contains phase-specific scripts for Minecraft speedrun automation:
Each phase represents a stage of progression toward defeating the Ender Dragon.

Phases:
-------
1. Foundation: Basic survival, wooden tools, shelter
2. Resources: Stone tools, wood, coal, torches
3. Tools: Iron tools and armor
4. Mining: Diamonds, obsidian, deep mining
5. Nether: Nether progression, blaze rods, ender pearls
6. Stronghold: Finding and entering the End portal
7. Dragon: Defeating the Ender Dragon

Usage:
------
    from phases import Phase1_Foundation
    
    phase = Phase1_Foundation(game_state_provider, action_decider)
    while not phase.is_complete():
        action = phase.execute()
"""

from .phase1_foundation import Phase1_Foundation
from .phase2_resources import Phase2_Resources
from .phase3_tools import Phase3_Tools
from .phase4_mining import Phase4_Mining
from .phase5_nether import Phase5_Nether
from .phase6_stronghold import Phase6_Stronghold
from .phase7_dragon import Phase7_Dragon

__all__ = [
    'Phase1_Foundation',
    'Phase2_Resources',
    'Phase3_Tools',
    'Phase4_Mining',
    'Phase5_Nether',
    'Phase6_Stronghold',
    'Phase7_Dragon',
]