"""
Phase 5: Nether
==============

This module implements Phase 5 of the Minecraft speedrun automation.
Goal: Progress through the Nether.

Objectives:
-----------
1. Build Nether portal (obsidian)
2. Enter the Nether safely
3. Find a Nether fortress
4. Kill Blazes for blaze rods
5. Collect ender pearls (bartering or hunting)
"""

from typing import Dict, Any, List
from actions.movement import Movement
from actions.combat import Combat
from actions.gathering import Gathering
from actions.inventory import Inventory


class Phase5_Nether:
    """
    Phase 5: Nether
    
    Goal: Progress through the Nether.
    
    Objectives:
    1. Build Nether portal (obsidian)
    2. Enter the Nether safely
    3. Find a Nether fortress
    4. Kill Blazes for blaze rods
    5. Collect ender pearls (bartering or hunting)
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
            "portal_built": False,
            "entered_nether": False,
            "fortress_found": False,
            "blaze_rods_collected": False,
            "ender_pearls_collected": False
        }
        self.blaze_rod_count = 0
        self.target_blaze_rods = 7  # Need 7 for eyes of ender
        self.ender_pearl_count = 0
        self.target_ender_pearls = 12  # Need 12 for portal
        
    def is_complete(self) -> bool:
        """
        Check if Phase 5 objectives are met.
        
        Returns:
            True if all objectives are complete
        """
        return (self.objectives_completed["blaze_rods_collected"] and
                self.objectives_completed["ender_pearls_collected"])
    
    def get_objectives(self) -> list:
        """
        Get list of objectives for this phase.
        
        Returns:
            List of objective strings
        """
        return [
            "Build Nether portal with obsidian",
            "Enter the Nether",
            "Find a Nether fortress",
            "Kill Blazes for 7 blaze rods",
            "Collect 12 ender pearls"
        ]
    
    def execute(self) -> dict:
        """
        Execute one tick of Phase 5.
        
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
        
        # Check obsidian for portal
        obsidian_count = self.inventory.get_item_count("minecraft:obsidian", inventory)
        if obsidian_count >= 10:
            self.objectives_completed["portal_built"] = True
            
        # Check if in Nether
        dimension = player.get("dimension", "overworld")
        if dimension == "nether":
            self.objectives_completed["entered_nether"] = True
            
        # Check blaze rods
        blaze_items = [item for item in inventory 
                      if "blaze_rod" in item.get("item_id", "")]
        self.blaze_rod_count = sum(item.get("count", 0) for item in blaze_items)
        
        if self.blaze_rod_count >= self.target_blaze_rods:
            self.objectives_completed["blaze_rods_collected"] = True
            
        # Check ender pearls
        pearl_items = [item for item in inventory 
                      if "ender_pearl" in item.get("item_id", "")]
        self.ender_pearl_count = sum(item.get("count", 0) for item in pearl_items)
        
        if self.ender_pearl_count >= self.target_ender_pearls:
            self.objectives_completed["ender_pearls_collected"] = True
    
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
        
        # Check if we're in the overworld
        if dimension == "overworld":
            # Priority 3: Build portal if we have obsidian
            if not self.objectives_completed["portal_built"]:
                obsidian_count = self.inventory.get_item_count("minecraft:obsidian", inventory)
                if obsidian_count >= 10:
                    return {
                        "action": "place_block",
                        "target": None,
                        "params": {"block_type": "obsidian"},
                        "reasoning": "Building Nether portal",
                        "priority": 7,
                        "timeout": 10.0
                    }
                else:
                    return {
                        "action": "explore",
                        "target": None,
                        "params": {"direction": "forward", "distance": 15},
                        "reasoning": f"Searching for obsidian ({obsidian_count}/10)",
                        "priority": 5,
                        "timeout": 10.0
                    }
            
            # If portal built, try to enter
            if self.objectives_completed["portal_built"]:
                return {
                    "action": "interact",
                    "target": None,
                    "params": {},
                    "reasoning": "Entering Nether portal",
                    "priority": 7,
                    "timeout": 5.0
                }
        
        # We're in the Nether
        elif dimension == "nether":
            # Priority 4: Find fortress
            if not self.objectives_completed["fortress_found"]:
                # Look for fortress structures (simplified)
                nearby_blocks = world.get("nearby_blocks", [])
                nether_bricks = [b for b in nearby_blocks 
                               if "nether_brick" in b.get("type", "")]
                
                if nether_bricks:
                    self.objectives_completed["fortress_found"] = True
                else:
                    return {
                        "action": "explore",
                        "target": None,
                        "params": {"direction": "forward", "distance": 50},
                        "reasoning": "Searching for Nether fortress",
                        "priority": 6,
                        "timeout": 30.0
                    }
            
            # Priority 5: Kill Blazes for blaze rods
            if not self.objectives_completed["blaze_rods_collected"]:
                nearby_entities = world.get("nearby_entities", [])
                blazes = [e for e in nearby_entities 
                         if "blaze" in e.get("type", "").lower()]
                
                if blazes:
                    nearest_blaze = blazes[0]
                    pos = nearest_blaze.get("position", {})
                    return {
                        "action": "attack_entity",
                        "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                        "params": {"entity_type": "blaze"},
                        "reasoning": f"Fighting Blazes ({self.blaze_rod_count}/{self.target_blaze_rods})",
                        "priority": 7,
                        "timeout": 10.0
                    }
                else:
                    return {
                        "action": "explore",
                        "target": None,
                        "params": {"direction": "forward", "distance": 20},
                        "reasoning": "Searching for Blazes",
                        "priority": 5,
                        "timeout": 15.0
                    }
            
            # Priority 6: Get ender pearls (from Piglins or Endermen)
            if not self.objectives_completed["ender_pearls_collected"]:
                nearby_entities = world.get("nearby_entities", [])
                piglins = [e for e in nearby_entities 
                          if "piglin" in e.get("type", "").lower() and
                             "brute" not in e.get("type", "").lower()]
                endermen = [e for e in nearby_entities 
                           if "enderman" in e.get("type", "").lower()]
                
                # Prefer bartering with Piglins (safer)
                if piglins:
                    # Need gold to barter
                    if self.inventory.has_item("minecraft:gold_ingot", inventory):
                        nearest_piglin = piglins[0]
                        pos = nearest_piglin.get("position", {})
                        return {
                            "action": "interact",
                            "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                            "params": {},
                            "reasoning": f"Bartering with Piglins ({self.ender_pearl_count}/{self.target_ender_pearls})",
                            "priority": 6,
                            "timeout": 10.0
                        }
                    else:
                        # Mine gold
                        return {
                            "action": "explore",
                            "target": None,
                            "params": {"direction": "forward", "distance": 15},
                            "reasoning": "Searching for gold to barter",
                            "priority": 5,
                            "timeout": 10.0
                        }
                # Hunt Endermen as backup
                elif endermen:
                    nearest_enderman = endermen[0]
                    pos = nearest_enderman.get("position", {})
                    return {
                        "action": "attack_entity",
                        "target": [pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)],
                        "params": {"entity_type": "enderman"},
                        "reasoning": f"Hunting Endermen ({self.ender_pearl_count}/{self.target_ender_pearls})",
                        "priority": 6,
                        "timeout": 10.0
                    }
                else:
                    return {
                        "action": "explore",
                        "target": None,
                        "params": {"direction": "forward", "distance": 20},
                        "reasoning": "Searching for Piglins or Endermen",
                        "priority": 5,
                        "timeout": 15.0
                    }
        
        # Default: Explore
        return {
            "action": "explore",
            "target": None,
            "params": {"direction": "forward", "distance": 10},
            "reasoning": "Phase 5 complete - returning to Overworld",
            "priority": 2,
            "timeout": 10.0
        }