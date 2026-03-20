"""
Test Suite for Core Module
==========================

Tests for MemoryReader, PlayerState, InventoryState, WorldState, and InputSimulator.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

# Import core components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.player_state import PlayerState
from core.inventory_state import InventoryState, ItemStack
from core.world_state import WorldState, Position, Entity, Block, LookingAt
from core.memory_reader import MemoryReader, GameState


class TestPlayerState:
    """Test cases for PlayerState dataclass."""
    
    def test_default_initialization(self):
        """Test default PlayerState initialization."""
        player = PlayerState()
        
        assert player.position == {"x": 0.0, "y": 0.0, "z": 0.0}
        assert player.velocity == {"x": 0.0, "y": 0.0, "z": 0.0}
        assert player.health == 20.0
        assert player.hunger == 20.0
        assert player.saturation == 5.0
        assert player.experience_level == 0
        assert player.experience_progress == 0.0
        assert player.yaw == 0.0
        assert player.pitch == 0.0
        assert player.is_on_ground is True
        assert player.is_in_water is False
        assert player.is_in_lava is False
        assert player.is_sleeping is False
        assert player.dimension == "overworld"
    
    def test_custom_initialization(self):
        """Test PlayerState with custom values."""
        player = PlayerState(
            position={"x": 100.5, "y": 64.0, "z": -200.3},
            health=15.0,
            hunger=18.0,
            yaw=90.0,
            pitch=15.0,
            dimension="nether"
        )
        
        assert player.position["x"] == 100.5
        assert player.position["y"] == 64.0
        assert player.position["z"] == -200.3
        assert player.health == 15.0
        assert player.hunger == 18.0
        assert player.yaw == 90.0
        assert player.pitch == 15.0
        assert player.dimension == "nether"
    
    def test_health_validation(self):
        """Test health validation."""
        # Valid health
        player = PlayerState(health=10.0)
        assert player.health == 10.0
        
        # Invalid health - too low
        with pytest.raises(ValueError):
            PlayerState(health=-1.0)
        
        # Invalid health - too high
        with pytest.raises(ValueError):
            PlayerState(health=25.0)
    
    def test_hunger_validation(self):
        """Test hunger validation."""
        # Valid hunger
        player = PlayerState(hunger=15.0)
        assert player.hunger == 15.0
        
        # Invalid hunger
        with pytest.raises(ValueError):
            PlayerState(hunger=-5.0)
        
        with pytest.raises(ValueError):
            PlayerState(hunger=30.0)
    
    def test_rotation_validation(self):
        """Test yaw and pitch validation."""
        # Valid rotation
        player = PlayerState(yaw=180.0, pitch=45.0)
        assert player.yaw == 180.0
        assert player.pitch == 45.0
        
        # Invalid yaw
        with pytest.raises(ValueError):
            PlayerState(yaw=200.0)
        
        # Invalid pitch
        with pytest.raises(ValueError):
            PlayerState(pitch=100.0)
    
    def test_dimension_validation(self):
        """Test dimension validation."""
        # Valid dimensions
        for dim in ["overworld", "nether", "end"]:
            player = PlayerState(dimension=dim)
            assert player.dimension == dim
        
        # Invalid dimension
        with pytest.raises(ValueError):
            PlayerState(dimension="invalid")
    
    def test_property_accessors(self):
        """Test position and velocity property accessors."""
        player = PlayerState(
            position={"x": 10.0, "y": 20.0, "z": 30.0},
            velocity={"x": 1.0, "y": 2.0, "z": 3.0}
        )
        
        # Position properties
        assert player.x == 10.0
        assert player.y == 20.0
        assert player.z == 30.0
        
        # Velocity properties
        assert player.velocity_x == 1.0
        assert player.velocity_y == 2.0
        assert player.velocity_z == 3.0
        
        # Setters
        player.x = 100.0
        assert player.x == 100.0
    
    def test_health_checks(self):
        """Test health-related methods."""
        player = PlayerState(health=5.0, hunger=8.0)
        
        assert player.is_low_health(threshold=6.0) is True
        assert player.is_low_health(threshold=4.0) is False
        assert player.is_hungry(threshold=10.0) is True
        assert player.is_hungry(threshold=5.0) is False
        assert player.should_heal() is True
    
    def test_danger_check(self):
        """Test is_in_danger method."""
        # Player in lava
        player = PlayerState(is_in_lava=True, health=15.0)
        assert player.is_in_danger() is True
        
        # Player with very low health
        player = PlayerState(health=3.0)
        assert player.is_in_danger() is True
        
        # Safe player
        player = PlayerState(health=20.0, is_in_lava=False)
        assert player.is_in_danger() is False
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        player = PlayerState(
            position={"x": 10.0, "y": 20.0, "z": 30.0},
            health=15.0
        )
        
        data = player.to_dict()
        assert isinstance(data, dict)
        assert data["position"]["x"] == 10.0
        assert data["health"] == 15.0
    
    def test_from_dict(self):
        """Test from_dict creation."""
        data = {
            "position": {"x": 10.0, "y": 20.0, "z": 30.0},
            "health": 15.0,
            "hunger": 18.0,
            "dimension": "nether"
        }
        
        player = PlayerState.from_dict(data)
        assert player.position["x"] == 10.0
        assert player.health == 15.0
        assert player.hunger == 18.0
        assert player.dimension == "nether"


class TestItemStack:
    """Test cases for ItemStack dataclass."""
    
    def test_default_initialization(self):
        """Test default ItemStack initialization."""
        item = ItemStack()
        assert item.item_id == ""
        assert item.count == 0
        assert item.damage == 0
        assert item.nbt == {}
    
    def test_custom_initialization(self):
        """Test ItemStack with custom values."""
        item = ItemStack(
            item_id="minecraft:diamond_sword",
            count=1,
            damage=100,
            nbt={"ench": []}
        )
        
        assert item.item_id == "minecraft:diamond_sword"
        assert item.count == 1
        assert item.damage == 100
        assert item.nbt == {"ench": []}
    
    def test_is_empty(self):
        """Test is_empty method."""
        empty_item = ItemStack()
        assert empty_item.is_empty() is True
        
        empty_item = ItemStack(item_id="minecraft:stone", count=0)
        assert empty_item.is_empty() is True
        
        valid_item = ItemStack(item_id="minecraft:stone", count=5)
        assert valid_item.is_empty() is False
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        item = ItemStack(item_id="minecraft:diamond", count=64)
        data = item.to_dict()
        
        assert data["item_id"] == "minecraft:diamond"
        assert data["count"] == 64
    
    def test_from_dict(self):
        """Test from_dict creation."""
        data = {
            "item_id": "minecraft:iron_ingot",
            "count": 32,
            "damage": 0,
            "nbt": {}
        }
        
        item = ItemStack.from_dict(data)
        assert item.item_id == "minecraft:iron_ingot"
        assert item.count == 32


class TestInventoryState:
    """Test cases for InventoryState dataclass."""
    
    def test_default_initialization(self):
        """Test default InventoryState initialization."""
        inventory = InventoryState()
        
        assert inventory.selected_slot == 0
        assert inventory.items == []
        assert inventory.armor == {"head": None, "chest": None, "legs": None, "feet": None}
        assert inventory.offhand is None
    
    def test_selected_slot_validation(self):
        """Test selected slot validation."""
        # Valid slot
        inventory = InventoryState(selected_slot=5)
        assert inventory.selected_slot == 5
        
        # Invalid slot
        with pytest.raises(ValueError):
            InventoryState(selected_slot=10)
    
    def test_get_item(self):
        """Test get_item method."""
        inventory = InventoryState(
            items=[
                {"slot": 0, "item_id": "minecraft:diamond_sword", "count": 1},
                {"slot": 1, "item_id": "minecraft:stone", "count": 64}
            ]
        )
        
        item = inventory.get_item(0)
        assert item is not None
        assert item["item_id"] == "minecraft:diamond_sword"
        
        item = inventory.get_item(5)
        assert item is None
    
    def test_set_item(self):
        """Test set_item method."""
        inventory = InventoryState()
        
        # Set new item
        inventory.set_item(0, {"item_id": "minecraft:diamond", "count": 10})
        item = inventory.get_item(0)
        assert item["item_id"] == "minecraft:diamond"
        
        # Clear slot
        inventory.set_item(0, None)
        item = inventory.get_item(0)
        assert item is None
    
    def test_find_item(self):
        """Test find_item method."""
        inventory = InventoryState(
            items=[
                {"slot": 0, "item_id": "minecraft:diamond_sword", "count": 1},
                {"slot": 5, "item_id": "minecraft:stone", "count": 64},
                {"slot": 10, "item_id": "minecraft:stone", "count": 32}
            ]
        )
        
        slot = inventory.find_item("minecraft:stone")
        assert slot == 5  # First occurrence
        
        slot = inventory.find_item("minecraft:emerald")
        assert slot is None
    
    def test_count_item(self):
        """Test count_item method."""
        inventory = InventoryState(
            items=[
                {"slot": 0, "item_id": "minecraft:stone", "count": 64},
                {"slot": 1, "item_id": "minecraft:stone", "count": 32},
                {"slot": 2, "item_id": "minecraft:dirt", "count": 16}
            ]
        )
        
        count = inventory.count_item("minecraft:stone")
        assert count == 96
        
        count = inventory.count_item("minecraft:emerald")
        assert count == 0
    
    def test_has_item(self):
        """Test has_item method."""
        inventory = InventoryState(
            items=[{"slot": 0, "item_id": "minecraft:diamond", "count": 5}]
        )
        
        assert inventory.has_item("minecraft:diamond") is True
        assert inventory.has_item("minecraft:emerald") is False
    
    def test_hotbar_items(self):
        """Test get_hotbar_items method."""
        inventory = InventoryState(
            items=[
                {"slot": 0, "item_id": "minecraft:sword", "count": 1},
                {"slot": 5, "item_id": "minecraft:pickaxe", "count": 1},
                {"slot": 10, "item_id": "minecraft:stone", "count": 64}
            ]
        )
        
        hotbar = inventory.get_hotbar_items()
        assert len(hotbar) == 2
        assert all(0 <= item["slot"] <= 8 for item in hotbar)
    
    def test_selected_item(self):
        """Test get_selected_item method."""
        inventory = InventoryState(
            selected_slot=2,
            items=[{"slot": 2, "item_id": "minecraft:diamond_sword", "count": 1}]
        )
        
        item = inventory.get_selected_item()
        assert item is not None
        assert item["item_id"] == "minecraft:diamond_sword"
    
    def test_empty_slots(self):
        """Test get_empty_slots and is_inventory_full methods."""
        inventory = InventoryState(
            items=[
                {"slot": 0, "item_id": "minecraft:stone", "count": 1},
                {"slot": 5, "item_id": "minecraft:dirt", "count": 1}
            ]
        )
        
        empty_slots = inventory.get_empty_slots()
        assert len(empty_slots) == 34  # 36 total - 2 occupied
        assert 0 not in empty_slots
        assert 5 not in empty_slots
        
        assert inventory.is_inventory_full() is False
    
    def test_armor(self):
        """Test armor methods."""
        inventory = InventoryState()
        
        # Set armor piece
        armor_piece = ItemStack(item_id="minecraft:diamond_helmet", count=1)
        inventory.set_armor_piece("head", armor_piece)
        
        retrieved = inventory.get_armor_piece("head")
        assert retrieved is not None
        assert retrieved.item_id == "minecraft:diamond_helmet"
        
        assert inventory.has_armor() is True
        
        # Invalid slot
        with pytest.raises(ValueError):
            inventory.set_armor_piece("invalid", armor_piece)
    
    def test_to_dict_from_dict(self):
        """Test to_dict and from_dict conversion."""
        inventory = InventoryState(
            selected_slot=3,
            items=[{"slot": 0, "item_id": "minecraft:diamond", "count": 10}]
        )
        
        data = inventory.to_dict()
        assert data["selected_slot"] == 3
        assert len(data["items"]) == 1
        
        restored = InventoryState.from_dict(data)
        assert restored.selected_slot == 3
        assert len(restored.items) == 1


class TestWorldState:
    """Test cases for WorldState and related classes."""
    
    def test_position(self):
        """Test Position dataclass."""
        pos = Position(x=100.5, y=64.0, z=-200.3)
        assert pos.x == 100.5
        assert pos.y == 64.0
        assert pos.z == -200.3
        
        data = pos.to_dict()
        assert data == {"x": 100.5, "y": 64.0, "z": -200.3}
        
        restored = Position.from_dict(data)
        assert restored.x == 100.5
    
    def test_entity(self):
        """Test Entity dataclass."""
        entity = Entity(
            type="minecraft:zombie",
            id=123,
            position=Position(x=10.0, y=64.0, z=20.0),
            health=20.0,
            is_hostile=True,
            distance=5.0
        )
        
        assert entity.type == "minecraft:zombie"
        assert entity.is_hostile is True
        
        data = entity.to_dict()
        assert data["type"] == "minecraft:zombie"
        
        restored = Entity.from_dict(data)
        assert restored.type == "minecraft:zombie"
    
    def test_block(self):
        """Test Block dataclass."""
        block = Block(
            type="minecraft:stone",
            position=Position(x=10, y=64, z=20)
        )
        
        assert block.type == "minecraft:stone"
        
        data = block.to_dict()
        assert data["type"] == "minecraft:stone"
    
    def test_looking_at(self):
        """Test LookingAt dataclass."""
        looking = LookingAt(
            block_type="minecraft:diamond_ore",
            position=Position(x=10, y=-59, z=20),
            face="north"
        )
        
        assert looking.block_type == "minecraft:diamond_ore"
        assert looking.face == "north"
    
    def test_world_state_initialization(self):
        """Test WorldState default initialization."""
        world = WorldState()
        
        assert world.time_of_day == 0
        assert world.day_count == 0
        assert world.is_raining is False
        assert world.difficulty == "normal"
        assert world.game_mode == "survival"
    
    def test_time_validation(self):
        """Test time_of_day validation."""
        world = WorldState(time_of_day=12000)
        assert world.time_of_day == 12000
        
        with pytest.raises(ValueError):
            WorldState(time_of_day=30000)
    
    def test_day_night_check(self):
        """Test is_day and is_night methods."""
        # Day time
        world = WorldState(time_of_day=6000)
        assert world.is_day() is True
        assert world.is_night() is False
        
        # Night time
        world = WorldState(time_of_day=18000)
        assert world.is_day() is False
        assert world.is_night() is True
    
    def test_get_hostile_entities(self):
        """Test get_hostile_entities method."""
        world = WorldState(
            nearby_entities=[
                Entity(type="minecraft:zombie", is_hostile=True),
                Entity(type="minecraft:pig", is_hostile=False),
                Entity(type="minecraft:skeleton", is_hostile=True)
            ]
        )
        
        hostile = world.get_hostile_entities()
        assert len(hostile) == 2
        assert all(e.is_hostile for e in hostile)
    
    def test_get_closest_entity(self):
        """Test get_closest_entity method."""
        world = WorldState(
            nearby_entities=[
                Entity(type="minecraft:pig", distance=10.0),
                Entity(type="minecraft:cow", distance=5.0),
                Entity(type="minecraft:sheep", distance=15.0)
            ]
        )
        
        closest = world.get_closest_entity()
        assert closest is not None
        assert closest.type == "minecraft:cow"
        assert closest.distance == 5.0
    
    def test_is_dangerous(self):
        """Test is_dangerous method."""
        # Night time
        world = WorldState(time_of_day=18000)
        assert world.is_dangerous() is True
        
        # Hostile entities
        world = WorldState(
            time_of_day=6000,
            nearby_entities=[Entity(type="minecraft:zombie", is_hostile=True)]
        )
        assert world.is_dangerous() is True
        
        # Safe
        world = WorldState(
            time_of_day=6000,
            nearby_entities=[Entity(type="minecraft:pig", is_hostile=False)]
        )
        assert world.is_dangerous() is False
    
    def test_to_dict_from_dict(self):
        """Test WorldState to_dict and from_dict."""
        world = WorldState(
            time_of_day=12000,
            difficulty="hard",
            nearby_entities=[Entity(type="minecraft:zombie", is_hostile=True)]
        )
        
        data = world.to_dict()
        assert data["time_of_day"] == 12000
        assert data["difficulty"] == "hard"
        
        restored = WorldState.from_dict(data)
        assert restored.time_of_day == 12000
        assert restored.difficulty == "hard"


class TestMemoryReader:
    """Test cases for MemoryReader class."""
    
    def test_initialization_without_file(self):
        """Test MemoryReader initialization without offsets file."""
        reader = MemoryReader(offsets_file="nonexistent.json")
        
        assert reader.pid is None
        assert reader.base_address is None
        assert reader.offsets is not None  # Should use defaults
    
    def test_default_offsets(self):
        """Test default offsets generation."""
        reader = MemoryReader(offsets_file="nonexistent.json")
        
        assert "player" in reader.offsets
        assert "inventory" in reader.offsets
        assert "world" in reader.offsets
    
    def test_parse_offset_chain(self):
        """Test offset chain parsing."""
        reader = MemoryReader(offsets_file="nonexistent.json")
        
        # Single offset
        offsets = reader._parse_offset_chain("0x28")
        assert offsets == [0x28]
        
        # Multiple offsets
        offsets = reader._parse_offset_chain("0x28, 0x08, 0x10")
        assert offsets == [0x28, 0x08, 0x10]
    
    @patch('core.memory_reader.subprocess.run')
    def test_get_minecraft_pid_not_found(self, mock_run):
        """Test _get_minecraft_pid when process not found."""
        mock_run.return_value = Mock(returncode=1, stdout="")
        
        reader = MemoryReader(offsets_file="nonexistent.json")
        pid = reader._get_minecraft_pid()
        
        assert pid is None
    
    def test_get_game_state_without_attach(self):
        """Test get_game_state without attaching."""
        reader = MemoryReader(offsets_file="nonexistent.json")
        
        state = reader.get_game_state()
        assert state is None


class TestGameState:
    """Test cases for GameState dataclass."""
    
    def test_initialization(self):
        """Test GameState initialization."""
        player = PlayerState()
        inventory = InventoryState()
        world = WorldState()
        timestamp = time.time()
        
        state = GameState(
            player=player,
            inventory=inventory,
            world=world,
            timestamp=timestamp
        )
        
        assert state.player == player
        assert state.inventory == inventory
        assert state.world == world
        assert state.timestamp == timestamp
    
    def test_to_dict(self):
        """Test GameState to_dict conversion."""
        player = PlayerState(health=15.0)
        inventory = InventoryState(selected_slot=2)
        world = WorldState(time_of_day=6000)
        
        state = GameState(
            player=player,
            inventory=inventory,
            world=world,
            timestamp=1234567890.0
        )
        
        data = state.to_dict()
        assert data["player"]["health"] == 15.0
        assert data["inventory"]["selected_slot"] == 2
        assert data["world"]["time_of_day"] == 6000
        assert data["timestamp"] == 1234567890.0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])