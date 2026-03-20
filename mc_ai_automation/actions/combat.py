"""
Combat Actions Module
====================

This module provides combat and defense functions for Minecraft automation.
Handles attacking, defending, fleeing, and combat tactics.

Classes:
--------
- Combat: Main class for combat actions
"""

import time
from typing import List, Tuple, Optional, Dict, Any

from core.input_simulator import (
    attack as input_attack,
    block_with_shield,
    use_item as input_use_item,
    look_at_position,
    jump as input_jump,
    sneak as input_sneak,
    select_slot
)


class Combat:
    """
    Combat and defense actions for Minecraft automation.
    
    This class provides methods for engaging in combat,
    including attacking enemies, defending with shields,
    and tactical retreats.
    """
    
    # Common hostile entity types
    HOSTILE_ENTITIES = [
        "minecraft:zombie", "minecraft:skeleton", "minecraft:creeper",
        "minecraft:spider", "minecraft:enderman", "minecraft:witch",
        "minecraft:blaze", "minecraft:ghast", "minecraft:wither_skeleton",
        "minecraft:piglin_brute", "minecraft:piglin", "minecraft:hoglin",
        "minecraft:magma_cube", "minecraft:slime"
    ]
    
    def __init__(self):
        """Initialize the Combat module."""
        self.is_blocking = False
        self.last_attack_time = 0
        self.attack_cooldown = 0.625  # Minecraft attack cooldown in seconds
        
    def attack_entity(self, entity_type: str = None, hold_ticks: int = 10) -> None:
        """
        Attack an entity of the specified type.
        
        Args:
            entity_type: Type of entity to attack (e.g., "minecraft:zombie")
            hold_ticks: Number of ticks to hold the attack button
        """
        # Check attack cooldown
        current_time = time.time()
        if current_time - self.last_attack_time < self.attack_cooldown:
            time.sleep(self.attack_cooldown - (current_time - self.last_attack_time))
        
        # Perform attack
        input_attack(hold_ticks)
        self.last_attack_time = time.time()
        
    def attack_nearest_hostile(self, game_state: Dict[str, Any] = None) -> bool:
        """
        Attack the nearest hostile entity.
        
        Args:
            game_state: Current game state with nearby entities
            
        Returns:
            True if an attack was performed, False otherwise
        """
        if game_state is None:
            return False
            
        nearby_entities = game_state.get("world", {}).get("nearby_entities", [])
        
        # Find nearest hostile entity
        nearest_hostile = None
        nearest_distance = float('inf')
        
        for entity in nearby_entities:
            if entity.get("is_hostile", False):
                distance = entity.get("distance", float('inf'))
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_hostile = entity
        
        if nearest_hostile is None:
            return False
            
        # Look at the entity
        pos = nearest_hostile.get("position", {})
        if pos:
            look_at_position(pos.get("x", 0), pos.get("y", 0), pos.get("z", 0))
            time.sleep(0.05)  # Small delay to aim
            
            # Attack
            self.attack_entity(nearest_hostile.get("type"))
            return True
            
        return False
        
    def defend(self, duration: float = 1.0) -> None:
        """
        Block with shield for a specified duration.
        
        Args:
            duration: How long to hold the block in seconds
        """
        if not self.is_blocking:
            block_with_shield(duration)
            self.is_blocking = True
            time.sleep(duration)
            # Shield blocking is held, not toggled in Minecraft
            # We'll need to release it manually or by performing another action
            
    def stop_defending(self) -> None:
        """Stop blocking with shield."""
        if self.is_blocking:
            # Release the block by doing a quick action
            input_attack(1)  # Quick attack to release block
            self.is_blocking = False
            
    def flee_from(self, danger_position: Tuple[float, float, float], 
                  player_position: Tuple[float, float, float] = None) -> None:
        """
        Flee from a dangerous position.
        
        Args:
            danger_position: Position of the danger (x, y, z)
            player_position: Current player position (x, y, z)
        """
        if player_position is None:
            # If no player position given, just run opposite to danger
            # This is a simplified implementation
            input_jump()  # Jump for momentum
            time.sleep(0.1)
            return
            
        # Calculate opposite direction
        dx = player_position[0] - danger_position[0]
        dz = player_position[2] - danger_position[2]
        
        # Normalize and scale
        distance = (dx ** 2 + dz ** 2) ** 0.5
        if distance > 0:
            dx /= distance
            dz /= distance
            
        # Move away from danger
        flee_x = player_position[0] + dx * 10
        flee_z = player_position[2] + dz * 10
        
        # Sprint away (handled by movement module)
        # For now, just jump and move
        input_jump()
        time.sleep(0.1)
        
    def retreat_and_heal(self, health: float, food_items: List[Dict] = None) -> None:
        """
        Retreat from combat and heal if possible.
        
        Args:
            health: Current health level (0-20)
            food_items: List of food items in inventory
        """
        # Sneak to reduce damage
        input_sneak(0.5)
        
        # Try to eat food if health is low
        if health < 15 and food_items:
            # Find best food item
            best_food = None
            best_value = 0
            
            for item in food_items:
                item_id = item.get("item_id", "")
                # Simple food value estimation
                if "golden_apple" in item_id:
                    value = 20
                elif "steak" in item_id or "cooked_porkchop" in item_id:
                    value = 8
                elif "bread" in item_id:
                    value = 5
                else:
                    value = 3
                    
                if value > best_value:
                    best_value = value
                    best_food = item
            
            if best_food:
                # Select food slot and eat
                slot = best_food.get("slot", 0)
                select_slot(slot)
                input_use_item(40)  # Hold to eat
                
    def dodge_attack(self, direction: str = "left") -> None:
        """
        Perform a dodge move to avoid an attack.
        
        Args:
            direction: Direction to dodge - "left", "right", or "back"
        """
        # Jump and move in direction
        input_jump()
        time.sleep(0.05)
        
        # Direction is handled by movement module
        # This is a simplified version
        
    def circle_strafe(self, target_position: Tuple[float, float, float],
                      player_position: Tuple[float, float, float],
                      radius: float = 3.0) -> None:
        """
        Circle around a target while attacking.
        
        Args:
            target_position: Position of target (x, y, z)
            player_position: Current player position (x, y, z)
            radius: Desired distance from target
        """
        import math
        
        # Calculate angle to target
        dx = target_position[0] - player_position[0]
        dz = target_position[2] - player_position[2]
        angle = math.atan2(dx, dz)
        
        # Calculate perpendicular direction for circling
        circle_angle = angle + math.pi / 2
        circle_x = player_position[0] + math.sin(circle_angle) * 2
        circle_z = player_position[2] + math.cos(circle_angle) * 2
        
        # Look at target while moving
        look_at_position(target_position[0], target_position[1], target_position[2])
        
        # Attack periodically
        current_time = time.time()
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.attack_entity()
            
    def use_shield_block_timing(self, attack_interval: float = 2.0) -> None:
        """
        Time shield blocks to enemy attacks.
        
        Args:
            attack_interval: Expected interval between enemy attacks
        """
        # Block just before expected attack
        time.sleep(attack_interval * 0.8)
        self.defend(0.5)
        
    def critical_hit(self) -> None:
        """
        Perform a critical hit by attacking while falling.
        """
        input_jump()
        time.sleep(0.2)  # Wait for fall
        self.attack_entity()
        
    def sweep_attack(self) -> None:
        """
        Perform a sweep attack by attacking while moving.
        """
        # Attack while moving forward
        self.attack_entity(hold_ticks=5)
        
    def is_entity_hostile(self, entity_type: str) -> bool:
        """
        Check if an entity type is hostile.
        
        Args:
            entity_type: Type of entity to check
            
        Returns:
            True if entity is hostile, False otherwise
        """
        return entity_type in self.HOSTILE_ENTITIES
        
    def get_threat_level(self, game_state: Dict[str, Any]) -> int:
        """
        Assess the current threat level.
        
        Args:
            game_state: Current game state
            
        Returns:
            Threat level (0-10, higher = more dangerous)
        """
        threat_level = 0
        
        player = game_state.get("player", {})
        health = player.get("health", 20)
        nearby_entities = game_state.get("world", {}).get("nearby_entities", [])
        
        # Low health increases threat
        if health < 10:
            threat_level += 3
        elif health < 15:
            threat_level += 1
            
        # Count hostile entities
        for entity in nearby_entities:
            if entity.get("is_hostile", False):
                distance = entity.get("distance", 100)
                entity_type = entity.get("type", "")
                
                # Closer enemies are more threatening
                if distance < 3:
                    threat_level += 3
                elif distance < 8:
                    threat_level += 2
                else:
                    threat_level += 1
                    
                # Specific dangerous entities
                if "creeper" in entity_type:
                    threat_level += 2
                elif "enderman" in entity_type:
                    threat_level += 1
                    
        return min(threat_level, 10)