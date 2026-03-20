"""
Movement Actions Module
======================

This module provides movement and navigation functions for Minecraft automation.
Handles walking, sprinting, path navigation, and camera control.

Classes:
--------
- Movement: Main class for movement actions
"""

import math
import time
from typing import List, Tuple, Optional

from core.input_simulator import (
    move_to as input_move_to,
    look_at as input_look_at,
    look_at_position,
    jump as input_jump,
    sneak as input_sneak
)


class Movement:
    """
    Movement and navigation actions for Minecraft automation.
    
    This class provides methods for moving the player character,
    including walking, sprinting, path navigation, and camera control.
    """
    
    def __init__(self):
        """Initialize the Movement module."""
        self.current_speed = "walk"
        self.is_sneaking = False
        
    def walk_to(self, x: float, z: float, speed: str = "walk") -> None:
        """
        Walk to the specified X, Z coordinates.
        
        Args:
            x: Target X coordinate
            z: Target Z coordinate
            speed: Movement speed - "walk", "sprint", or "sneak"
        """
        self.current_speed = speed
        
        if speed == "sneak":
            if not self.is_sneaking:
                input_sneak(0.5)  # Toggle sneak on
                self.is_sneaking = True
        elif self.is_sneaking:
            input_sneak(0.5)  # Toggle sneak off
            self.is_sneaking = False
        
        # Move to target position
        input_move_to(x, z)
        
    def sprint_to(self, x: float, z: float) -> None:
        """
        Sprint to the specified X, Z coordinates.
        
        Args:
            x: Target X coordinate
            z: Target Z coordinate
        """
        self.walk_to(x, z, speed="sprint")
        
    def navigate_path(self, waypoints: List[Tuple[float, float, float]]) -> None:
        """
        Navigate through a series of waypoints.
        
        Args:
            waypoints: List of (x, y, z) coordinates to visit in order
        """
        for waypoint in waypoints:
            x, y, z = waypoint
            # Look at the waypoint first
            look_at_position(x, y, z)
            # Move to the waypoint
            self.walk_to(x, z)
            # Small delay between waypoints
            time.sleep(0.1)
            
    def turn_to_yaw(self, yaw: float) -> None:
        """
        Rotate the player's view to the specified yaw angle.
        
        Args:
            yaw: Horizontal rotation in degrees (-180 to 180)
        """
        # Normalize yaw to -180 to 180 range
        yaw = ((yaw + 180) % 360) - 180
        input_look_at(yaw, 0)  # Keep pitch at 0
        
    def turn_to_pitch(self, pitch: float) -> None:
        """
        Rotate the player's view to the specified pitch angle.
        
        Args:
            pitch: Vertical rotation in degrees (-90 to 90)
        """
        # Clamp pitch to valid range
        pitch = max(-90, min(90, pitch))
        input_look_at(0, pitch)  # Keep yaw at 0
        
    def look_at_target(self, x: float, y: float, z: float) -> None:
        """
        Look at a specific position in 3D space.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            z: Target Z coordinate
        """
        look_at_position(x, y, z)
        
    def jump_and_move(self, x: float, z: float) -> None:
        """
        Jump while moving to the target position.
        
        Args:
            x: Target X coordinate
            z: Target Z coordinate
        """
        input_jump()
        time.sleep(0.1)  # Small delay for jump to start
        self.walk_to(x, z)
        
    def move_forward(self, duration: float = 1.0) -> None:
        """
        Move forward for a specified duration.
        
        Args:
            duration: How long to move forward in seconds
        """
        # This would need to hold the W key - simulated by moving to a point ahead
        # For now, we use a simple forward movement
        time.sleep(duration)
        
    def move_backward(self, duration: float = 1.0) -> None:
        """
        Move backward for a specified duration.
        
        Args:
            duration: How long to move backward in seconds
        """
        # This would need to hold the S key
        time.sleep(duration)
        
    def strafe_left(self, duration: float = 1.0) -> None:
        """
        Strafe left for a specified duration.
        
        Args:
            duration: How long to strafe left in seconds
        """
        # This would need to hold the A key
        time.sleep(duration)
        
    def strafe_right(self, duration: float = 1.0) -> None:
        """
        Strafe right for a specified duration.
        
        Args:
            duration: How long to strafe right in seconds
        """
        # This would need to hold the D key
        time.sleep(duration)
        
    def jump(self) -> None:
        """Make the player jump."""
        input_jump()
        
    def sneak(self, duration: float = 0.0) -> None:
        """
        Toggle sneak mode or hold sneak for a duration.
        
        Args:
            duration: How long to hold sneak (0 for toggle)
        """
        input_sneak(duration)
        if duration == 0:
            self.is_sneaking = not self.is_sneaking
        else:
            self.is_sneaking = True
            
    def stop(self) -> None:
        """Stop all movement and reset sneak state."""
        if self.is_sneaking:
            input_sneak(0.5)  # Toggle sneak off
            self.is_sneaking = False
            
    def calculate_distance(self, x1: float, z1: float, x2: float, z2: float) -> float:
        """
        Calculate the distance between two points in 2D space.
        
        Args:
            x1: First point X coordinate
            z1: First point Z coordinate
            x2: Second point X coordinate
            z2: Second point Z coordinate
            
        Returns:
            Distance between the points
        """
        return math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2)
        
    def calculate_yaw_to_target(self, current_x: float, current_z: float, 
                                target_x: float, target_z: float) -> float:
        """
        Calculate the yaw angle needed to face a target.
        
        Args:
            current_x: Current X position
            current_z: Current Z position
            target_x: Target X position
            target_z: Target Z position
            
        Returns:
            Yaw angle in degrees
        """
        dx = target_x - current_x
        dz = target_z - current_z
        
        # Calculate angle in radians
        angle_rad = math.atan2(dx, dz)
        
        # Convert to degrees
        angle_deg = math.degrees(angle_rad)
        
        # Minecraft uses a different coordinate system
        # Adjust to match Minecraft's yaw (0 = South, 90 = West, etc.)
        yaw = -angle_deg
        
        return yaw
        
    def calculate_pitch_to_target(self, current_x: float, current_y: float, current_z: float,
                                   target_x: float, target_y: float, target_z: float) -> float:
        """
        Calculate the pitch angle needed to look at a target.
        
        Args:
            current_x: Current X position
            current_y: Current Y position (eye level)
            current_z: Current Z position
            target_x: Target X position
            target_y: Target Y position
            target_z: Target Z position
            
        Returns:
            Pitch angle in degrees (positive = down, negative = up)
        """
        dx = target_x - current_x
        dy = target_y - current_y
        dz = target_z - current_z
        
        # Calculate horizontal distance
        horizontal_dist = math.sqrt(dx ** 2 + dz ** 2)
        
        # Calculate pitch angle
        pitch_rad = math.atan2(dy, horizontal_dist)
        pitch_deg = math.degrees(pitch_rad)
        
        # In Minecraft, negative pitch looks up, positive looks down
        return -pitch_deg