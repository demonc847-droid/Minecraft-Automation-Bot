"""
Test Suite for Actions Module
=============================

Tests for Movement, Combat, Gathering, and Inventory action classes.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

# Import action components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.movement import Movement
from actions.combat import Combat
from actions.gathering import Gathering
from actions.inventory import Inventory


class TestMovement:
    """Test cases for Movement class."""
    
    def test_initialization(self):
        """Test Movement class initialization."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        assert movement.input_simulator == mock_input
        assert movement.current_speed == "walk"
        assert movement.is_sneaking is False
    
    def test_initialization_without_input(self):
        """Test Movement initialization without input simulator."""
        movement = Movement()
        
        assert movement.input_simulator is None
        assert movement.current_speed == "walk"
    
    def test_walk_to(self):
        """Test walk_to method."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        movement.walk_to(100.0, 200.0)
        
        mock_input.move_to.assert_called_with(100.0, 200.0)
        assert movement.current_speed == "walk"
    
    def test_walk_to_with_sneak(self):
        """Test walk_to with sneak speed."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        movement.walk_to(100.0, 200.0, speed="sneak")
        
        mock_input.sneak.assert_called()
        mock_input.move_to.assert_called()
        assert movement.is_sneaking is True
    
    def test_sprint_to(self):
        """Test sprint_to method."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        movement.sprint_to(100.0, 200.0)
        
        mock_input.move_to.assert_called()
        assert movement.current_speed == "sprint"
    
    def test_jump(self):
        """Test jump method."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        movement.jump()
        
        mock_input.jump.assert_called_once()
    
    def test_jump_without_input(self):
        """Test jump without input simulator."""
        movement = Movement()
        
        # Should not raise error
        movement.jump()
    
    def test_sneak_toggle(self):
        """Test sneak toggle."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        movement.sneak(0)
        
        mock_input.sneak.assert_called_with(0)
        assert movement.is_sneaking is True
    
    def test_sneak_with_duration(self):
        """Test sneak with duration."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        movement.sneak(1.0)
        
        mock_input.sneak.assert_called_with(1.0)
        assert movement.is_sneaking is True
    
    def test_stop(self):
        """Test stop method."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        movement.is_sneaking = True
        
        movement.stop()
        
        mock_input.sneak.assert_called_with(0.5)
        assert movement.is_sneaking is False
    
    def test_look_at_target(self):
        """Test look_at_target method."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        movement.look_at_target(10.0, 20.0, 30.0)
        
        mock_input.look_at_position.assert_called_with(10.0, 20.0, 30.0)
    
    def test_turn_to_yaw(self):
        """Test turn_to_yaw method."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        movement.turn_to_yaw(90.0)
        
        mock_input.look_at.assert_called()
    
    def test_turn_to_pitch(self):
        """Test turn_to_pitch method."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        movement.turn_to_pitch(45.0)
        
        mock_input.look_at.assert_called()
    
    def test_calculate_distance(self):
        """Test distance calculation."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        distance = movement.calculate_distance(0, 0, 3, 4)
        assert distance == 5.0  # 3-4-5 triangle
    
    def test_calculate_distance_same_point(self):
        """Test distance calculation for same point."""
        movement = Movement()
        
        distance = movement.calculate_distance(0, 0, 0, 0)
        assert distance == 0.0
    
    def test_calculate_yaw_to_target(self):
        """Test yaw calculation."""
        movement = Movement()
        
        # Looking east (positive X)
        yaw = movement.calculate_yaw_to_target(0, 0, 10, 0)
        assert yaw != 0  # Should return some angle
    
    def test_calculate_pitch_to_target(self):
        """Test pitch calculation."""
        movement = Movement()
        
        # Looking up
        pitch = movement.calculate_pitch_to_target(0, 0, 0, 0, 10, 0)
        assert pitch < 0  # Negative pitch looks up
    
    def test_navigate_path(self):
        """Test navigate_path method."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        waypoints = [(0, 64, 0), (10, 64, 0), (20, 64, 0)]
        movement.navigate_path(waypoints)
        
        assert mock_input.look_at_position.call_count == 3
        assert mock_input.move_to.call_count == 3
    
    def test_jump_and_move(self):
        """Test jump_and_move method."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        movement.jump_and_move(10.0, 20.0)
        
        mock_input.jump.assert_called()
        mock_input.move_to.assert_called()


class TestCombat:
    """Test cases for Combat class."""
    
    def test_initialization(self):
        """Test Combat class initialization."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        
        assert combat.input_simulator == mock_input
        assert combat.is_blocking is False
        assert combat.attack_cooldown == 0.625
    
    def test_attack_entity(self):
        """Test attack_entity method."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        
        combat.attack_entity()
        
        mock_input.attack.assert_called()
    
    def test_attack_entity_with_hold(self):
        """Test attack with custom hold duration."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        
        combat.attack_entity(hold_ticks=20)
        
        mock_input.attack.assert_called_with(20)
    
    def test_attack_nearest_hostile(self):
        """Test attack_nearest_hostile method."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        
        game_state = {
            "world": {
                "nearby_entities": [
                    {"type": "minecraft:zombie", "is_hostile": True, "distance": 5.0, "position": {"x": 5, "y": 64, "z": 0}}
                ]
            }
        }
        
        result = combat.attack_nearest_hostile(game_state)
        
        assert result is True
        mock_input.look_at_position.assert_called()
        mock_input.attack.assert_called()
    
    def test_attack_nearest_hostile_no_enemies(self):
        """Test attack_nearest_hostile with no enemies."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        
        game_state = {
            "world": {
                "nearby_entities": []
            }
        }
        
        result = combat.attack_nearest_hostile(game_state)
        
        assert result is False
    
    def test_defend(self):
        """Test defend method."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        
        combat.defend(1.0)
        
        mock_input.block_with_shield.assert_called()
        assert combat.is_blocking is True
    
    def test_stop_defending(self):
        """Test stop_defending method."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        combat.is_blocking = True
        
        combat.stop_defending()
        
        mock_input.attack.assert_called_with(1)
        assert combat.is_blocking is False
    
    def test_is_entity_hostile(self):
        """Test is_entity_hostile method."""
        combat = Combat()
        
        assert combat.is_entity_hostile("minecraft:zombie") is True
        assert combat.is_entity_hostile("minecraft:pig") is False
    
    def test_get_threat_level_low(self):
        """Test get_threat_level with low threats."""
        combat = Combat()
        
        game_state = {
            "player": {"health": 20.0},
            "world": {"nearby_entities": []}
        }
        
        threat = combat.get_threat_level(game_state)
        assert threat == 0
    
    def test_get_threat_level_high(self):
        """Test get_threat_level with high threats."""
        combat = Combat()
        
        game_state = {
            "player": {"health": 5.0},
            "world": {
                "nearby_entities": [
                    {"type": "minecraft:creeper", "is_hostile": True, "distance": 2.0}
                ]
            }
        }
        
        threat = combat.get_threat_level(game_state)
        assert threat > 5
    
    def test_critical_hit(self):
        """Test critical_hit method."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        
        combat.critical_hit()
        
        mock_input.jump.assert_called()
        mock_input.attack.assert_called()
    
    def test_dodge_attack(self):
        """Test dodge_attack method."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        
        combat.dodge_attack()
        
        mock_input.jump.assert_called()


class TestGathering:
    """Test cases for Gathering class."""
    
    def test_initialization(self):
        """Test Gathering class initialization."""
        mock_input = Mock()
        gathering = Gathering(input_simulator=mock_input)
        
        assert gathering.input_simulator == mock_input
        assert gathering.is_mining is False
    
    def test_mine_block(self):
        """Test mine_block method."""
        mock_input = Mock()
        gathering = Gathering(input_simulator=mock_input)
        
        gathering.mine_block()
        
        mock_input.break_block.assert_called()
    
    def test_mine_block_with_position(self):
        """Test mine_block with position."""
        mock_input = Mock()
        gathering = Gathering(input_simulator=mock_input)
        
        gathering.mine_block(position=(10, 64, 20))
        
        mock_input.look_at_position.assert_called()
        mock_input.break_block.assert_called()
    
    def test_chop_tree(self):
        """Test chop_tree method."""
        mock_input = Mock()
        gathering = Gathering(input_simulator=mock_input)
        
        gathering.chop_tree((10.0, 64.0, 20.0))
        
        assert mock_input.break_block.call_count > 0
    
    def test_collect_drops(self):
        """Test collect_drops method."""
        mock_input = Mock()
        gathering = Gathering(input_simulator=mock_input)
        
        # Should not raise error
        gathering.collect_drops()
    
    def test_get_required_tool(self):
        """Test get_required_tool method."""
        gathering = Gathering()
        
        tool = gathering.get_required_tool("minecraft:stone")
        assert tool == "pickaxe"
        
        tool = gathering.get_required_tool("minecraft:oak_log")
        assert tool == "axe"
    
    def test_get_required_tool_unknown(self):
        """Test get_required_tool with unknown block."""
        gathering = Gathering()
        
        tool = gathering.get_required_tool("minecraft:unknown_block")
        assert tool is None
    
    def test_is_valuable_block(self):
        """Test is_valuable_block method."""
        gathering = Gathering()
        
        assert gathering.is_valuable_block("minecraft:diamond_ore") is True
        assert gathering.is_valuable_block("minecraft:stone") is False
    
    def test_can_mine_block(self):
        """Test can_mine_block method."""
        gathering = Gathering()
        
        # Without inventory, should return True
        assert gathering.can_mine_block("minecraft:stone") is True
    
    def test_can_mine_block_with_inventory(self):
        """Test can_mine_block with inventory."""
        gathering = Gathering()
        
        inventory = [
            {"item_id": "minecraft:diamond_pickaxe", "count": 1}
        ]
        
        assert gathering.can_mine_block("minecraft:stone", inventory) is True
    
    def test_can_mine_block_without_tool(self):
        """Test can_mine_block without required tool."""
        gathering = Gathering()
        
        inventory = [
            {"item_id": "minecraft:diamond_sword", "count": 1}
        ]
        
        assert gathering.can_mine_block("minecraft:stone", inventory) is False
    
    def test_find_nearest_block(self):
        """Test find_nearest_block method."""
        gathering = Gathering()
        
        game_state = {
            "world": {
                "nearby_blocks": [
                    {"type": "minecraft:stone", "position": {"x": 5, "y": 64, "z": 0}},
                    {"type": "minecraft:stone", "position": {"x": 10, "y": 64, "z": 0}}
                ]
            }
        }
        
        position = gathering.find_nearest_block("minecraft:stone", game_state)
        assert position == (5, 64, 0)
    
    def test_find_nearest_block_not_found(self):
        """Test find_nearest_block when block not found."""
        gathering = Gathering()
        
        game_state = {
            "world": {
                "nearby_blocks": []
            }
        }
        
        position = gathering.find_nearest_block("minecraft:diamond_ore", game_state)
        assert position is None
    
    def test_gather_resource(self):
        """Test gather_resource method."""
        mock_input = Mock()
        gathering = Gathering(input_simulator=mock_input)
        
        game_state = {
            "world": {
                "nearby_blocks": [
                    {"type": "minecraft:oak_log", "position": {"x": 5, "y": 64, "z": 0}}
                ]
            }
        }
        
        count = gathering.gather_resource("wood", game_state, count=1)
        
        assert count >= 0


class TestInventory:
    """Test cases for Inventory class."""
    
    def test_initialization(self):
        """Test Inventory class initialization."""
        mock_input = Mock()
        inventory = Inventory(input_simulator=mock_input)
        
        assert inventory.input_simulator == mock_input
        assert inventory.inventory_open is False
    
    def test_open_inventory(self):
        """Test open_inventory method."""
        mock_input = Mock()
        inventory = Inventory(input_simulator=mock_input)
        
        inventory.open_inventory()
        
        mock_input.open_inventory.assert_called_once()
        assert inventory.inventory_open is True
    
    def test_close_inventory(self):
        """Test close_inventory method."""
        mock_input = Mock()
        inventory = Inventory(input_simulator=mock_input)
        inventory.inventory_open = True
        
        inventory.close_inventory()
        
        mock_input.close_inventory.assert_called_once()
        assert inventory.inventory_open is False
    
    def test_select_slot(self):
        """Test select_slot method."""
        mock_input = Mock()
        inventory = Inventory(input_simulator=mock_input)
        
        inventory.select_slot(5)
        
        mock_input.select_slot.assert_called_with(5)
    
    def test_craft_item(self):
        """Test craft_item method."""
        mock_input = Mock()
        inventory = Inventory(input_simulator=mock_input)
        
        result = inventory.craft_item("minecraft:wooden_planks")
        
        assert result is True
        mock_input.open_inventory.assert_called()
        mock_input.close_inventory.assert_called()
    
    def test_craft_item_unknown_recipe(self):
        """Test craft_item with unknown recipe."""
        inventory = Inventory()
        
        result = inventory.craft_item("minecraft:unknown_item")
        
        assert result is False
    
    def test_has_item(self):
        """Test has_item method."""
        inventory = Inventory()
        
        inv_items = [
            {"item_id": "minecraft:diamond", "count": 5},
            {"item_id": "minecraft:stone", "count": 64}
        ]
        
        assert inventory.has_item("minecraft:diamond", inv_items) is True
        assert inventory.has_item("minecraft:emerald", inv_items) is False
    
    def test_has_item_min_count(self):
        """Test has_item with minimum count."""
        inventory = Inventory()
        
        inv_items = [
            {"item_id": "minecraft:diamond", "count": 2}
        ]
        
        assert inventory.has_item("minecraft:diamond", inv_items, min_count=1) is True
        assert inventory.has_item("minecraft:diamond", inv_items, min_count=5) is False
    
    def test_get_item_count(self):
        """Test get_item_count method."""
        inventory = Inventory()
        
        inv_items = [
            {"item_id": "minecraft:stone", "count": 64},
            {"item_id": "minecraft:stone", "count": 32}
        ]
        
        count = inventory.get_item_count("minecraft:stone", inv_items)
        assert count == 96
    
    def test_get_best_tool(self):
        """Test get_best_tool method."""
        inventory = Inventory()
        
        inv_items = [
            {"item_id": "minecraft:iron_pickaxe", "count": 1},
            {"item_id": "minecraft:stone_pickaxe", "count": 1}
        ]
        
        tool = inventory.get_best_tool("mining", inv_items)
        assert tool == "minecraft:iron_pickaxe"
    
    def test_get_best_tool_no_tools(self):
        """Test get_best_tool with no tools."""
        inventory = Inventory()
        
        tool = inventory.get_best_tool("mining", [])
        assert tool is None
    
    def test_get_best_armor(self):
        """Test get_best_armor method."""
        inventory = Inventory()
        
        inv_items = [
            {"item_id": "minecraft:iron_helmet", "count": 1},
            {"item_id": "minecraft:diamond_chestplate", "count": 1}
        ]
        
        armor = inventory.get_best_armor(inv_items)
        assert armor["head"] == "minecraft:iron_helmet"
        assert armor["chest"] == "minecraft:diamond_chestplate"
    
    def test_equip_item(self):
        """Test equip_item method."""
        mock_input = Mock()
        inventory = Inventory(input_simulator=mock_input)
        
        inv_items = [
            {"item_id": "minecraft:diamond_sword", "slot": 0, "count": 1}
        ]
        
        result = inventory.equip_item("minecraft:diamond_sword", inv_items)
        
        assert result is True
        mock_input.select_slot.assert_called_with(0)
        mock_input.use_item.assert_called()
    
    def test_equip_item_not_found(self):
        """Test equip_item with item not in inventory."""
        inventory = Inventory()
        
        result = inventory.equip_item("minecraft:diamond_sword", [])
        
        assert result is False
    
    def test_get_food_items(self):
        """Test get_food_items method."""
        inventory = Inventory()
        
        inv_items = [
            {"item_id": "minecraft:bread", "count": 10},
            {"item_id": "minecraft:stone", "count": 64},
            {"item_id": "minecraft:cooked_porkchop", "count": 5}
        ]
        
        food = inventory.get_food_items(inv_items)
        assert len(food) == 2
    
    def test_get_tool_durability(self):
        """Test get_tool_durability method."""
        inventory = Inventory()
        
        inv_items = [
            {"item_id": "minecraft:diamond_pickaxe", "damage": 100, "count": 1}
        ]
        
        durability = inventory.get_tool_durability("minecraft:diamond_pickaxe", inv_items)
        assert durability == 1461  # 1561 - 100
    
    def test_get_tool_durability_not_found(self):
        """Test get_tool_durability with item not found."""
        inventory = Inventory()
        
        durability = inventory.get_tool_durability("minecraft:diamond_pickaxe", [])
        assert durability is None


class TestActionIntegration:
    """Integration tests for action classes."""
    
    def test_movement_with_combat(self):
        """Test movement and combat working together."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        combat = Combat(input_simulator=mock_input)
        
        # Move to enemy
        movement.walk_to(10.0, 0.0)
        
        # Attack
        combat.attack_entity()
        
        assert mock_input.move_to.called
        assert mock_input.attack.called
    
    def test_gathering_with_inventory(self):
        """Test gathering and inventory management."""
        mock_input = Mock()
        gathering = Gathering(input_simulator=mock_input)
        inventory = Inventory(input_simulator=mock_input)
        
        # Mine a block
        gathering.mine_block()
        
        # Select different slot
        inventory.select_slot(1)
        
        assert mock_input.break_block.called
        assert mock_input.select_slot.called
    
    def test_combat_with_movement_flee(self):
        """Test fleeing from combat using movement."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        movement = Movement(input_simulator=mock_input)
        
        # Detect threat and dodge
        combat.dodge_attack()
        
        # Move away
        movement.sprint_to(0.0, 10.0)
        
        assert mock_input.jump.called
        assert mock_input.move_to.called


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])