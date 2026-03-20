"""
Player State Module
==================

This module defines the PlayerState dataclass for tracking player data
including position, health, hunger, experience, rotation, and status flags.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlayerState:
    """
    Represents the current state of the player in Minecraft.
    
    Attributes:
        position: Player position as (x, y, z) coordinates
        velocity: Player velocity as (x, y, z) components
        health: Player health (0.0 to 20.0)
        hunger: Player hunger level (0.0 to 20.0)
        saturation: Player saturation level (0.0 to 20.0)
        experience_level: Player experience level
        experience_progress: Experience progress to next level (0.0 to 1.0)
        yaw: Horizontal rotation in degrees (-180 to 180)
        pitch: Vertical rotation in degrees (-90 to 90)
        is_on_ground: Whether the player is on the ground
        is_in_water: Whether the player is in water
        is_in_lava: Whether the player is in lava
        is_sleeping: Whether the player is sleeping
        dimension: Current dimension ("overworld", "nether", "end")
    """
    
    # Position coordinates
    position: dict = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0})
    
    # Velocity components
    velocity: dict = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0})
    
    # Health and hunger
    health: float = 20.0
    hunger: float = 20.0
    saturation: float = 5.0
    
    # Experience
    experience_level: int = 0
    experience_progress: float = 0.0
    
    # Rotation
    yaw: float = 0.0
    pitch: float = 0.0
    
    # Status flags
    is_on_ground: bool = True
    is_in_water: bool = False
    is_in_lava: bool = False
    is_sleeping: bool = False
    
    # Dimension
    dimension: str = "overworld"
    
    def __post_init__(self):
        """Validate player state after initialization."""
        self._validate_health()
        self._validate_hunger()
        self._validate_saturation()
        self._validate_rotation()
        self._validate_dimension()
    
    def _validate_health(self):
        """Validate health is within valid range."""
        if not 0.0 <= self.health <= 20.0:
            raise ValueError(f"Health must be between 0.0 and 20.0, got {self.health}")
    
    def _validate_hunger(self):
        """Validate hunger is within valid range."""
        if not 0.0 <= self.hunger <= 20.0:
            raise ValueError(f"Hunger must be between 0.0 and 20.0, got {self.hunger}")
    
    def _validate_saturation(self):
        """Validate saturation is within valid range."""
        if not 0.0 <= self.saturation <= 20.0:
            raise ValueError(f"Saturation must be between 0.0 and 20.0, got {self.saturation}")
    
    def _validate_rotation(self):
        """Validate rotation angles are within valid ranges."""
        if not -180.0 <= self.yaw <= 180.0:
            raise ValueError(f"Yaw must be between -180.0 and 180.0, got {self.yaw}")
        if not -90.0 <= self.pitch <= 90.0:
            raise ValueError(f"Pitch must be between -90.0 and 90.0, got {self.pitch}")
    
    def _validate_dimension(self):
        """Validate dimension is a valid value."""
        valid_dimensions = {"overworld", "nether", "end"}
        if self.dimension not in valid_dimensions:
            raise ValueError(f"Dimension must be one of {valid_dimensions}, got {self.dimension}")
    
    @property
    def x(self) -> float:
        """Get X coordinate."""
        return self.position["x"]
    
    @x.setter
    def x(self, value: float):
        """Set X coordinate."""
        self.position["x"] = value
    
    @property
    def y(self) -> float:
        """Get Y coordinate."""
        return self.position["y"]
    
    @y.setter
    def y(self, value: float):
        """Set Y coordinate."""
        self.position["y"] = value
    
    @property
    def z(self) -> float:
        """Get Z coordinate."""
        return self.position["z"]
    
    @z.setter
    def z(self, value: float):
        """Set Z coordinate."""
        self.position["z"] = value
    
    @property
    def velocity_x(self) -> float:
        """Get X velocity."""
        return self.velocity["x"]
    
    @velocity_x.setter
    def velocity_x(self, value: float):
        """Set X velocity."""
        self.velocity["x"] = value
    
    @property
    def velocity_y(self) -> float:
        """Get Y velocity."""
        return self.velocity["y"]
    
    @velocity_y.setter
    def velocity_y(self, value: float):
        """Set Y velocity."""
        self.velocity["y"] = value
    
    @property
    def velocity_z(self) -> float:
        """Get Z velocity."""
        return self.velocity["z"]
    
    @velocity_z.setter
    def velocity_z(self, value: float):
        """Set Z velocity."""
        self.velocity["z"] = value
    
    def is_low_health(self, threshold: float = 6.0) -> bool:
        """
        Check if player health is dangerously low.
        
        Args:
            threshold: Health threshold below which health is considered low
            
        Returns:
            True if health is below threshold
        """
        return self.health < threshold
    
    def is_hungry(self, threshold: float = 10.0) -> bool:
        """
        Check if player hunger is low.
        
        Args:
            threshold: Hunger threshold below which player is considered hungry
            
        Returns:
            True if hunger is below threshold
        """
        return self.hunger < threshold
    
    def should_heal(self) -> bool:
        """
        Determine if the player needs healing.
        
        Returns:
            True if healing is recommended
        """
        return self.is_low_health() or self.is_hungry()
    
    def is_in_danger(self) -> bool:
        """
        Check if the player is in immediate danger.
        
        Returns:
            True if player is in lava or has very low health
        """
        return self.is_in_lava or self.health < 4.0
    
    def to_dict(self) -> dict:
        """
        Convert player state to dictionary format.
        
        Returns:
            Dictionary representation of player state
        """
        return {
            "position": self.position.copy(),
            "velocity": self.velocity.copy(),
            "health": self.health,
            "hunger": self.hunger,
            "saturation": self.saturation,
            "experience_level": self.experience_level,
            "experience_progress": self.experience_progress,
            "yaw": self.yaw,
            "pitch": self.pitch,
            "is_on_ground": self.is_on_ground,
            "is_in_water": self.is_in_water,
            "is_in_lava": self.is_in_lava,
            "is_sleeping": self.is_sleeping,
            "dimension": self.dimension
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PlayerState':
        """
        Create PlayerState from dictionary.
        
        Args:
            data: Dictionary containing player state data
            
        Returns:
            PlayerState instance
        """
        return cls(
            position=data.get("position", {"x": 0.0, "y": 0.0, "z": 0.0}),
            velocity=data.get("velocity", {"x": 0.0, "y": 0.0, "z": 0.0}),
            health=data.get("health", 20.0),
            hunger=data.get("hunger", 20.0),
            saturation=data.get("saturation", 5.0),
            experience_level=data.get("experience_level", 0),
            experience_progress=data.get("experience_progress", 0.0),
            yaw=data.get("yaw", 0.0),
            pitch=data.get("pitch", 0.0),
            is_on_ground=data.get("is_on_ground", True),
            is_in_water=data.get("is_in_water", False),
            is_in_lava=data.get("is_in_lava", False),
            is_sleeping=data.get("is_sleeping", False),
            dimension=data.get("dimension", "overworld")
        )