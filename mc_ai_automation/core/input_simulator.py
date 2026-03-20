"""
Input Simulator Module
======================

This module implements the InputSimulator class for simulating keyboard
and mouse input using pynput with human-like behavior.
"""

import time
import math
import random
from typing import Optional, Tuple, List
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import numpy as np


class InputSimulator:
    """
    Simulates keyboard and mouse input for Minecraft control.
    
    This class provides methods for human-like input simulation including
    smooth mouse movement, keyboard control, and anti-detection patterns.
    """
    
    def __init__(self, mouse_sensitivity: float = 5.0):
        """
        Initialize InputSimulator.
        
        Args:
            mouse_sensitivity: Pixels per degree of rotation (default: 5.0)
        """
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.mouse_sensitivity = mouse_sensitivity
        
        # Timing parameters (in seconds)
        self.min_action_delay = 0.05
        self.max_action_delay = 0.2
        self.min_key_duration = 0.05
        self.max_key_duration = 0.15
        
        # Mouse movement parameters
        self.min_move_duration = 0.1
        self.max_move_duration = 0.5
        self.move_points = 20
    
    def _human_delay(self, min_ms: float = 50, max_ms: float = 200):
        """
        Add human-like random delay.
        
        Args:
            min_ms: Minimum delay in milliseconds
            max_ms: Maximum delay in milliseconds
        """
        delay = random.uniform(min_ms, max_ms) / 1000.0
        time.sleep(delay)
    
    def _think_pause(self):
        """Simulate player thinking (1-3 seconds)."""
        time.sleep(random.uniform(1.0, 3.0))
    
    def _jitter_offset(self, range_px: int = 3) -> int:
        """
        Get random pixel offset for movement.
        
        Args:
            range_px: Range of offset in pixels
            
        Returns:
            Random offset value
        """
        return random.randint(-range_px, range_px)
    
    def _bezier_points(self, start: Tuple[int, int], end: Tuple[int, int], 
                       control: Tuple[int, int], num_points: int = 20) -> List[Tuple[int, int]]:
        """
        Generate smooth curve points using Bézier curve.
        
        Args:
            start: Starting position (x, y)
            end: Ending position (x, y)
            control: Control point for curve (x, y)
            num_points: Number of points to generate
            
        Returns:
            List of points along the curve
        """
        t = np.linspace(0, 1, num_points)
        points = []
        
        for i in t:
            x = (1-i)**2 * start[0] + 2*(1-i)*i * control[0] + i**2 * end[0]
            y = (1-i)**2 * start[1] + 2*(1-i)*i * control[1] + i**2 * end[1]
            points.append((int(x), int(y)))
        
        return points
    
    def smooth_move(self, target_x: int, target_y: int, duration: float = 0.3):
        """
        Move mouse smoothly to target position.
        
        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            duration: Movement duration in seconds
        """
        start = self.mouse.position
        end = (target_x, target_y)
        
        # Random control point for curve
        mid_x = (start[0] + end[0]) / 2 + random.randint(-50, 50)
        mid_y = (start[1] + end[1]) / 2 + random.randint(-50, 50)
        
        points = self._bezier_points(start, end, (mid_x, mid_y), self.move_points)
        delay = duration / len(points)
        
        for p in points:
            self.mouse.position = p
            time.sleep(delay + random.uniform(-0.01, 0.01))
    
    def move_to(self, x: float, z: float) -> None:
        """
        Move the player to the specified X, Z coordinates.
        
        Note: This is a placeholder. Actual movement requires pathfinding.
        
        Args:
            x: Target X coordinate
            z: Target Z coordinate
        """
        # TODO: Implement pathfinding and movement
        # For now, just walk forward
        self.keyboard.press('w')
        time.sleep(1.0)
        self.keyboard.release('w')
    
    def look_at(self, yaw: float, pitch: float) -> None:
        """
        Rotate the player's view to the specified angles.
        
        Args:
            yaw: Horizontal rotation in degrees (-180 to 180)
            pitch: Vertical rotation in degrees (-90 to 90)
        """
        # Convert yaw/pitch to pixel movement
        # Minecraft yaw: 0 = South, 90 = West, ±180 = North, -90 = East
        yaw_pixels = int(yaw * self.mouse_sensitivity)
        pitch_pixels = int(pitch * self.mouse_sensitivity)
        
        # Calculate movement duration based on distance
        distance = math.sqrt(yaw_pixels**2 + pitch_pixels**2)
        duration = min(self.max_move_duration, max(self.min_move_duration, distance / 1000))
        
        # Get current position
        current_x, current_y = self.mouse.position
        
        # Calculate target position
        target_x = current_x + yaw_pixels
        target_y = current_y + pitch_pixels
        
        # Smooth move to target
        self.smooth_move(target_x, target_y, duration)
        
        # Add small random delay
        self._human_delay(10, 50)
    
    def look_at_position(self, x: float, y: float, z: float) -> None:
        """
        Rotate the player's view to look at a specific position.
        
        Note: This is a placeholder. Requires player position for calculation.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            z: Target Z coordinate
        """
        # TODO: Implement position-based look calculation
        # This requires knowing the player's current position
        pass
    
    def jump(self) -> None:
        """Make the player jump."""
        self.keyboard.press(Key.space)
        time.sleep(random.uniform(0.05, 0.1))
        self.keyboard.release(Key.space)
        self._human_delay(50, 150)
    
    def attack(self, hold_ticks: int = 10) -> None:
        """
        Perform an attack action.
        
        Args:
            hold_ticks: Number of ticks to hold attack button (1 tick = 50ms)
        """
        duration = hold_ticks * 0.05  # Convert ticks to seconds
        self.mouse.press(Button.left)
        time.sleep(duration + random.uniform(-0.02, 0.02))
        self.mouse.release(Button.left)
        self._human_delay(50, 150)
    
    def block_with_shield(self, duration: float = 1.0) -> None:
        """
        Block with shield if equipped.
        
        Args:
            duration: How long to hold block
        """
        self.mouse.press(Button.right)
        time.sleep(duration + random.uniform(-0.1, 0.1))
        self.mouse.release(Button.right)
        self._human_delay(50, 150)
    
    def use_item(self, hold_ticks: int = 10) -> None:
        """
        Use the item in the main hand (right click).
        
        Args:
            hold_ticks: Number of ticks to hold use button
        """
        duration = hold_ticks * 0.05
        self.mouse.press(Button.right)
        time.sleep(duration + random.uniform(-0.02, 0.02))
        self.mouse.release(Button.right)
        self._human_delay(50, 150)
    
    def place_block(self) -> None:
        """Place a block from the selected slot."""
        self.mouse.click(Button.right, 1)
        self._human_delay(50, 150)
    
    def break_block(self, hold_ticks: int = 20) -> None:
        """
        Break the block being looked at.
        
        Args:
            hold_ticks: Number of ticks to hold break button
        """
        duration = hold_ticks * 0.05
        self.mouse.press(Button.left)
        time.sleep(duration + random.uniform(-0.02, 0.02))
        self.mouse.release(Button.left)
        self._human_delay(50, 150)
    
    def interact(self) -> None:
        """Interact with block/entity being looked at (right click without item)."""
        self.mouse.click(Button.right, 1)
        self._human_delay(50, 150)
    
    def open_inventory(self) -> None:
        """Open the player's inventory."""
        self.keyboard.press('e')
        time.sleep(random.uniform(0.05, 0.15))
        self.keyboard.release('e')
        time.sleep(0.3)  # Wait for GUI
        self._human_delay(50, 150)
    
    def close_inventory(self) -> None:
        """Close the player's inventory."""
        self.keyboard.press(Key.esc)
        time.sleep(random.uniform(0.05, 0.15))
        self.keyboard.release(Key.esc)
        self._human_delay(50, 150)
    
    def select_slot(self, slot: int) -> None:
        """
        Select a hotbar slot.
        
        Args:
            slot: Slot number (0-8)
        """
        if not 0 <= slot <= 8:
            raise ValueError(f"Slot must be between 0 and 8, got {slot}")
        
        # Convert to 1-9 key
        key = str(slot + 1)
        self.keyboard.press(key)
        time.sleep(random.uniform(0.05, 0.1))
        self.keyboard.release(key)
        self._human_delay(20, 80)
    
    def drop_item(self, all: bool = False) -> None:
        """
        Drop the item in the selected slot.
        
        Args:
            all: If True, drop entire stack
        """
        if all:
            # Hold Ctrl + Q to drop stack
            self.keyboard.press(Key.ctrl_l)
            self.keyboard.press('q')
            time.sleep(random.uniform(0.05, 0.15))
            self.keyboard.release('q')
            self.keyboard.release(Key.ctrl_l)
        else:
            # Single Q to drop one item
            self.keyboard.press('q')
            time.sleep(random.uniform(0.05, 0.15))
            self.keyboard.release('q')
        
        self._human_delay(50, 150)
    
    def move_item(self, from_slot: int, to_slot: int) -> None:
        """
        Move an item between inventory slots.
        
        Note: Must have inventory open.
        
        Args:
            from_slot: Source slot number
            to_slot: Destination slot number
        """
        # TODO: Implement inventory slot clicking
        # This requires knowing slot positions in the GUI
        pass
    
    def sneak(self, duration: float = 0.5) -> None:
        """
        Toggle sneak mode.
        
        Args:
            duration: How long to hold sneak (0 for toggle)
        """
        if duration > 0:
            self.keyboard.press(Key.shift_l)
            time.sleep(duration + random.uniform(-0.1, 0.1))
            self.keyboard.release(Key.shift_l)
        else:
            # Toggle
            self.keyboard.press(Key.shift_l)
            time.sleep(random.uniform(0.05, 0.15))
            self.keyboard.release(Key.shift_l)
        
        self._human_delay(50, 150)
    
    def walk_forward(self, duration: float = 1.0) -> None:
        """
        Walk forward for specified duration.
        
        Args:
            duration: Walking duration in seconds
        """
        self.keyboard.press('w')
        time.sleep(duration + random.uniform(-0.1, 0.1))
        self.keyboard.release('w')
        self._human_delay(50, 150)
    
    def sprint_forward(self, duration: float = 2.0) -> None:
        """
        Sprint forward for specified duration.
        
        Args:
            duration: Sprinting duration in seconds
        """
        self.keyboard.press(Key.ctrl_l)
        self.keyboard.press('w')
        time.sleep(duration + random.uniform(-0.1, 0.1))
        self.keyboard.release('w')
        self.keyboard.release(Key.ctrl_l)
        self._human_delay(50, 150)
    
    def walk_backward(self, duration: float = 1.0) -> None:
        """
        Walk backward for specified duration.
        
        Args:
            duration: Walking duration in seconds
        """
        self.keyboard.press('s')
        time.sleep(duration + random.uniform(-0.1, 0.1))
        self.keyboard.release('s')
        self._human_delay(50, 150)
    
    def strafe_left(self, duration: float = 1.0) -> None:
        """
        Strafe left for specified duration.
        
        Args:
            duration: Strafing duration in seconds
        """
        self.keyboard.press('a')
        time.sleep(duration + random.uniform(-0.1, 0.1))
        self.keyboard.release('a')
        self._human_delay(50, 150)
    
    def strafe_right(self, duration: float = 1.0) -> None:
        """
        Strafe right for specified duration.
        
        Args:
            duration: Strafing duration in seconds
        """
        self.keyboard.press('d')
        time.sleep(duration + random.uniform(-0.1, 0.1))
        self.keyboard.release('d')
        self._human_delay(50, 150)
    
    def press_key(self, key: str, duration: float = 0.1) -> None:
        """
        Press and release a key with variable timing.
        
        Args:
            key: Key to press
            duration: Key hold duration in seconds
        """
        self.keyboard.press(key)
        time.sleep(duration + random.uniform(-0.02, 0.02))
        self.keyboard.release(key)
        self._human_delay(20, 80)
    
    def maybe_pause(self, chance: float = 0.05) -> None:
        """
        Sometimes pause like a distracted player.
        
        Args:
            chance: Probability of pausing (0.0 to 1.0)
        """
        if random.random() < chance:
            self._think_pause()
    
    def afk_moment(self) -> None:
        """Rare longer pause (bathroom, phone, etc.)."""
        if random.random() < 0.01:
            time.sleep(random.uniform(10, 30))