"""
World State Module
==================

This module defines the WorldState class for tracking world data
including time, weather, difficulty, nearby entities, and blocks.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple


@dataclass
class Position:
    """
    Represents a 3D position in the world.
    
    Attributes:
        x: X coordinate
        y: Y coordinate
        z: Z coordinate
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert position to dictionary."""
        return {"x": self.x, "y": self.y, "z": self.z}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        """Create Position from dictionary."""
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            z=data.get("z", 0.0)
        )


@dataclass
class LookingAt:
    """
    Represents what the player is currently looking at.
    
    Attributes:
        block_type: Type of block being looked at (e.g., "minecraft:stone")
        position: Position of the block
        face: Face of the block being looked at
    """
    block_type: str = ""
    position: Position = field(default_factory=Position)
    face: str = ""  # "north", "south", "east", "west", "up", "down"
    
    def to_dict(self) -> dict:
        """Convert looking_at to dictionary."""
        return {
            "block_type": self.block_type,
            "position": self.position.to_dict(),
            "face": self.face
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LookingAt':
        """Create LookingAt from dictionary."""
        return cls(
            block_type=data.get("block_type", ""),
            position=Position.from_dict(data.get("position", {})),
            face=data.get("face", "")
        )


@dataclass
class Entity:
    """
    Represents a nearby entity.
    
    Attributes:
        type: Entity type (e.g., "minecraft:zombie", "minecraft:pig")
        id: Entity ID
        position: Entity position
        health: Entity health
        is_hostile: Whether the entity is hostile
        distance: Distance from player
    """
    type: str = ""
    id: int = 0
    position: Position = field(default_factory=Position)
    health: float = 0.0
    is_hostile: bool = False
    distance: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert entity to dictionary."""
        return {
            "type": self.type,
            "id": self.id,
            "position": self.position.to_dict(),
            "health": self.health,
            "is_hostile": self.is_hostile,
            "distance": self.distance
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Entity':
        """Create Entity from dictionary."""
        return cls(
            type=data.get("type", ""),
            id=data.get("id", 0),
            position=Position.from_dict(data.get("position", {})),
            health=data.get("health", 0.0),
            is_hostile=data.get("is_hostile", False),
            distance=data.get("distance", 0.0)
        )


@dataclass
class Block:
    """
    Represents a nearby block.
    
    Attributes:
        type: Block type (e.g., "minecraft:stone")
        position: Block position
    """
    type: str = ""
    position: Position = field(default_factory=Position)
    
    def to_dict(self) -> dict:
        """Convert block to dictionary."""
        return {
            "type": self.type,
            "position": self.position.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Block':
        """Create Block from dictionary."""
        return cls(
            type=data.get("type", ""),
            position=Position.from_dict(data.get("position", {}))
        )


@dataclass
class WorldState:
    """
    Represents the current state of the Minecraft world.
    
    Attributes:
        time_of_day: Time of day in ticks (0-24000)
        day_count: Number of days elapsed
        is_raining: Whether it's currently raining
        is_thundering: Whether there's a thunderstorm
        difficulty: Game difficulty
        game_mode: Current game mode
        seed: World seed
        spawn_point: World spawn point
        looking_at: What the player is looking at
        nearby_entities: List of nearby entities
        nearby_blocks: List of nearby blocks
    """
    
    time_of_day: int = 0
    day_count: int = 0
    is_raining: bool = False
    is_thundering: bool = False
    difficulty: str = "normal"
    game_mode: str = "survival"
    seed: int = 0
    spawn_point: Position = field(default_factory=Position)
    looking_at: Optional[LookingAt] = None
    nearby_entities: List[Entity] = field(default_factory=list)
    nearby_blocks: List[Block] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate world state after initialization."""
        self._validate_time_of_day()
        self._validate_difficulty()
        self._validate_game_mode()
    
    def _validate_time_of_day(self):
        """Validate time of day is within valid range."""
        if not 0 <= self.time_of_day <= 24000:
            raise ValueError(f"Time of day must be between 0 and 24000, got {self.time_of_day}")
    
    def _validate_difficulty(self):
        """Validate difficulty is a valid value."""
        valid_difficulties = {"peaceful", "easy", "normal", "hard"}
        if self.difficulty not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of {valid_difficulties}, got {self.difficulty}")
    
    def _validate_game_mode(self):
        """Validate game mode is a valid value."""
        valid_modes = {"survival", "creative", "adventure", "spectator"}
        if self.game_mode not in valid_modes:
            raise ValueError(f"Game mode must be one of {valid_modes}, got {self.game_mode}")
    
    def is_night(self) -> bool:
        """
        Check if it's nighttime (dangerous mobs can spawn).
        
        Returns:
            True if it's night (time < 1000 or > 13000)
        """
        return self.time_of_day < 1000 or self.time_of_day > 13000
    
    def is_day(self) -> bool:
        """
        Check if it's daytime (safe for exploration).
        
        Returns:
            True if it's day (1000 <= time <= 13000)
        """
        return 1000 <= self.time_of_day <= 13000
    
    def get_time_percentage(self) -> float:
        """
        Get time of day as percentage.
        
        Returns:
            Time as percentage (0.0 to 1.0)
        """
        return self.time_of_day / 24000.0
    
    def get_hostile_entities(self) -> List[Entity]:
        """
        Get list of nearby hostile entities.
        
        Returns:
            List of hostile entities
        """
        return [entity for entity in self.nearby_entities if entity.is_hostile]
    
    def get_passive_entities(self) -> List[Entity]:
        """
        Get list of nearby passive entities.
        
        Returns:
            List of passive entities
        """
        return [entity for entity in self.nearby_entities if not entity.is_hostile]
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """
        Get entities of specified type.
        
        Args:
            entity_type: Entity type to filter by
            
        Returns:
            List of entities of specified type
        """
        return [entity for entity in self.nearby_entities if entity.type == entity_type]
    
    def get_closest_entity(self, max_distance: float = 100.0) -> Optional[Entity]:
        """
        Get closest entity within distance.
        
        Args:
            max_distance: Maximum distance to consider
            
        Returns:
            Closest entity or None
        """
        if not self.nearby_entities:
            return None
        
        closest = None
        min_distance = max_distance
        
        for entity in self.nearby_entities:
            if entity.distance < min_distance:
                min_distance = entity.distance
                closest = entity
        
        return closest
    
    def get_closest_hostile_entity(self, max_distance: float = 100.0) -> Optional[Entity]:
        """
        Get closest hostile entity within distance.
        
        Args:
            max_distance: Maximum distance to consider
            
        Returns:
            Closest hostile entity or None
        """
        hostile_entities = self.get_hostile_entities()
        if not hostile_entities:
            return None
        
        closest = None
        min_distance = max_distance
        
        for entity in hostile_entities:
            if entity.distance < min_distance:
                min_distance = entity.distance
                closest = entity
        
        return closest
    
    def get_blocks_by_type(self, block_type: str) -> List[Block]:
        """
        Get blocks of specified type.
        
        Args:
            block_type: Block type to filter by
            
        Returns:
            List of blocks of specified type
        """
        return [block for block in self.nearby_blocks if block.type == block_type]
    
    def is_block_nearby(self, block_type: str, radius: float = 5.0) -> bool:
        """
        Check if block type exists within radius.
        
        Args:
            block_type: Block type to check
            radius: Search radius
            
        Returns:
            True if block is found within radius
        """
        for block in self.nearby_blocks:
            if block.type == block_type:
                # Calculate distance (simplified)
                distance = abs(block.position.x) + abs(block.position.y) + abs(block.position.z)
                if distance <= radius:
                    return True
        return False
    
    def is_dangerous(self) -> bool:
        """
        Check if world state indicates danger.
        
        Returns:
            True if there are hostile entities or it's nighttime
        """
        return len(self.get_hostile_entities()) > 0 or self.is_night()
    
    def to_dict(self) -> dict:
        """
        Convert world state to dictionary format.
        
        Returns:
            Dictionary representation of world state
        """
        return {
            "time_of_day": self.time_of_day,
            "day_count": self.day_count,
            "is_raining": self.is_raining,
            "is_thundering": self.is_thundering,
            "difficulty": self.difficulty,
            "game_mode": self.game_mode,
            "seed": self.seed,
            "spawn_point": self.spawn_point.to_dict(),
            "looking_at": self.looking_at.to_dict() if self.looking_at else None,
            "nearby_entities": [entity.to_dict() for entity in self.nearby_entities],
            "nearby_blocks": [block.to_dict() for block in self.nearby_blocks]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WorldState':
        """
        Create WorldState from dictionary.
        
        Args:
            data: Dictionary containing world state data
            
        Returns:
            WorldState instance
        """
        looking_at_data = data.get("looking_at")
        looking_at = LookingAt.from_dict(looking_at_data) if looking_at_data else None
        
        return cls(
            time_of_day=data.get("time_of_day", 0),
            day_count=data.get("day_count", 0),
            is_raining=data.get("is_raining", False),
            is_thundering=data.get("is_thundering", False),
            difficulty=data.get("difficulty", "normal"),
            game_mode=data.get("game_mode", "survival"),
            seed=data.get("seed", 0),
            spawn_point=Position.from_dict(data.get("spawn_point", {})),
            looking_at=looking_at,
            nearby_entities=[Entity.from_dict(e) for e in data.get("nearby_entities", [])],
            nearby_blocks=[Block.from_dict(b) for b in data.get("nearby_blocks", [])]
        )