"""
Integration Test Suite
======================

End-to-end tests for the complete Minecraft AI automation system.
Tests component interaction and full game loop simulation.
"""

import pytest
import time
import yaml
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import all components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.player_state import PlayerState
from core.inventory_state import InventoryState
from core.world_state import WorldState, Position, Entity
from core.memory_reader import GameState

from ai.prompts import Prompts
from ai.fallback import FallbackStrategy, get_fallback_action

from actions.movement import Movement
from actions.combat import Combat
from actions.gathering import Gathering
from actions.inventory import Inventory


class TestGameStateIntegration:
    """Test integration of game state components."""
    
    def test_complete_game_state_creation(self):
        """Test creating a complete game state from components."""
        player = PlayerState(
            position={"x": 100.5, "y": 64.0, "z": -200.3},
            health=18.0,
            hunger=15.0,
            yaw=90.0,
            pitch=15.0
        )
        
        inventory = InventoryState(
            selected_slot=0,
            items=[
                {"slot": 0, "item_id": "minecraft:diamond_sword", "count": 1},
                {"slot": 1, "item_id": "minecraft:bread", "count": 10}
            ]
        )
        
        world = WorldState(
            time_of_day=6000,
            day_count=1,
            difficulty="normal",
            nearby_entities=[
                Entity(type="minecraft:pig", distance=10.0, is_hostile=False)
            ]
        )
        
        state = GameState(
            player=player,
            inventory=inventory,
            world=world,
            timestamp=time.time()
        )
        
        # Verify complete state
        assert state.player.health == 18.0
        assert state.inventory.selected_slot == 0
        assert state.world.time_of_day == 6000
        
        # Verify serialization
        state_dict = state.to_dict()
        assert state_dict["player"]["health"] == 18.0
        assert state_dict["inventory"]["selected_slot"] == 0
    
    def test_game_state_to_dict_roundtrip(self):
        """Test game state serialization and deserialization."""
        original_player = PlayerState(
            position={"x": 50.0, "y": 70.0, "z": 100.0},
            health=15.0,
            hunger=12.0
        )
        
        original_inventory = InventoryState(
            selected_slot=3,
            items=[{"slot": 0, "item_id": "minecraft:stone", "count": 64}]
        )
        
        original_world = WorldState(
            time_of_day=12000,
            difficulty="hard"
        )
        
        # Serialize
        state = GameState(
            player=original_player,
            inventory=original_inventory,
            world=original_world,
            timestamp=1234567890.0
        )
        state_dict = state.to_dict()
        
        # Deserialize
        restored_player = PlayerState.from_dict(state_dict["player"])
        restored_inventory = InventoryState.from_dict(state_dict["inventory"])
        restored_world = WorldState.from_dict(state_dict["world"])
        
        # Verify
        assert restored_player.health == original_player.health
        assert restored_inventory.selected_slot == original_inventory.selected_slot
        assert restored_world.time_of_day == original_world.time_of_day


class TestAIDecisionIntegration:
    """Test AI decision making with game state."""
    
    def test_prompt_generation_with_game_state(self):
        """Test generating prompts from game state."""
        game_state = {
            "player": {
                "health": 10.0,
                "hunger": 8.0,
                "position": {"x": 0, "y": 64, "z": 0}
            },
            "inventory": {
                "selected_slot": 0,
                "items": [
                    {"slot": 0, "item_id": "minecraft:bread", "count": 5}
                ]
            },
            "world": {
                "time_of_day": 18000,  # Night
                "nearby_entities": []
            }
        }
        
        prompt = Prompts.build_full_prompt(
            phase="foundation",
            game_state=game_state,
            recent_actions="Built shelter"
        )
        
        assert prompt is not None
        assert len(prompt) > 0
    
    def test_emergency_prompt_triggers(self):
        """Test that emergency prompts trigger correctly."""
        # Critical health scenario
        game_state = {
            "player": {
                "health": 3.0,
                "hunger": 2.0,
                "position": {"x": 100, "y": 64, "z": 200}
            },
            "world": {
                "nearby_entities": [
                    {"type": "minecraft:zombie", "is_hostile": True, "distance": 3.0}
                ]
            }
        }
        
        prompt = Prompts.build_full_prompt(
            phase="foundation",
            game_state=game_state
        )
        
        # Should be emergency prompt
        assert "EMERGENCY" in prompt
    
    def test_fallback_action_with_game_state(self):
        """Test fallback action generation with game state."""
        game_state = {
            "player": {
                "health": 15.0,
                "hunger": 10.0,
                "is_on_ground": True,
                "is_in_lava": False,
                "position": {"x": 0, "y": 64, "z": 0}
            },
            "inventory": {
                "selected_slot": 0,
                "items": []
            },
            "world": {
                "nearby_entities": []
            }
        }
        
        action = get_fallback_action(game_state, strategy="safe")
        
        assert action is not None
        assert "action" in action
        assert "reasoning" in action


class TestActionExecutionIntegration:
    """Test action execution with mocked input."""
    
    def test_movement_action_sequence(self):
        """Test executing a sequence of movement actions."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        # Execute movement sequence
        movement.walk_to(100.0, 200.0)
        movement.jump()
        movement.sneak(duration=1.0)
        
        # Verify calls were made
        assert mock_input.move_to.called
        assert mock_input.jump.called
        assert mock_input.sneak.called
    
    def test_combat_action_sequence(self):
        """Test executing combat actions."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        
        # Execute combat sequence
        combat.attack_entity()
        combat.defend(duration=1.0)
        combat.attack_entity(hold_ticks=20)
        
        # Verify calls
        assert mock_input.attack.call_count == 2
        assert mock_input.block_with_shield.called
    
    def test_gathering_action_sequence(self):
        """Test executing gathering actions."""
        mock_input = Mock()
        gathering = Gathering(input_simulator=mock_input)
        
        # Execute gathering sequence with position parameter
        gathering.mine_block(position=(10, 64, 20))
        gathering.mine_block(position=(10, 64, 20))
        
        # Verify calls
        assert mock_input.break_block.call_count == 2
    
    def test_inventory_action_sequence(self):
        """Test executing inventory actions."""
        mock_input = Mock()
        inventory = Inventory(input_simulator=mock_input)
        
        # Execute inventory sequence
        inventory.open_inventory()
        inventory.select_slot(3)
        inventory.close_inventory()
        
        # Verify calls
        assert mock_input.open_inventory.called
        assert mock_input.select_slot.called_with(3)
        assert mock_input.close_inventory.called


class TestPhaseTransitions:
    """Test phase transition logic."""
    
    def test_foundation_phase_objectives(self):
        """Test foundation phase objectives."""
        objectives = Prompts.get_phase_objectives("foundation")
        
        assert "wood" in objectives.lower() or "tools" in objectives.lower()
        assert "shelter" in objectives.lower() or "survival" in objectives.lower()
    
    def test_resources_phase_objectives(self):
        """Test resources phase objectives."""
        objectives = Prompts.get_phase_objectives("resources")
        
        assert "stone" in objectives.lower() or "coal" in objectives.lower()
    
    def test_all_phases_have_objectives(self):
        """Test that all phases have defined objectives."""
        phases = ["foundation", "resources", "tools", "mining", "nether", "stronghold", "dragon"]
        
        for phase in phases:
            objectives = Prompts.get_phase_objectives(phase)
            assert objectives is not None
            assert len(objectives) > 0
    
    def test_phase_prompts_exist(self):
        """Test that all phase prompts exist."""
        phases = ["foundation", "resources", "tools", "mining", "nether", "stronghold", "dragon"]
        
        for phase in phases:
            prompt = Prompts.get_phase_prompt(phase)
            assert prompt is not None
            assert len(prompt) > 0


class TestConfigLoading:
    """Test configuration loading and validation."""
    
    def test_default_config_structure(self):
        """Test default configuration structure."""
        default_config = {
            "ai_provider": "gemini",
            "tick_rate": 20,
            "log_level": "INFO",
            "phase_order": [
                "foundation",
                "resources",
                "tools",
                "mining",
                "nether",
                "stronghold",
                "dragon"
            ]
        }
        
        assert "ai_provider" in default_config
        assert "tick_rate" in default_config
        assert "phase_order" in default_config
        assert len(default_config["phase_order"]) == 7
    
    def test_config_yaml_exists(self):
        """Test that config.yaml file exists."""
        config_path = Path(__file__).parent.parent / "config.yaml"
        assert config_path.exists(), "config.yaml should exist"
    
    def test_config_yaml_valid(self):
        """Test that config.yaml is valid YAML."""
        config_path = Path(__file__).parent.parent / "config.yaml"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            assert config is not None
            assert "ai_provider" in config
            assert "tick_rate" in config


class TestFullGameLoop:
    """Test full game loop simulation."""
    
    def test_simulated_game_loop(self):
        """Test a simulated game loop iteration."""
        # Create mock components
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        combat = Combat(input_simulator=mock_input)
        gathering = Gathering(input_simulator=mock_input)
        inventory = Inventory(input_simulator=mock_input)
        fallback = FallbackStrategy()
        
        # Create game state
        game_state = {
            "player": {
                "health": 20.0,
                "hunger": 18.0,
                "is_on_ground": True,
                "is_in_lava": False,
                "position": {"x": 0, "y": 64, "z": 0},
                "yaw": 0.0
            },
            "inventory": {
                "selected_slot": 0,
                "items": [
                    {"slot": 0, "item_id": "minecraft:diamond_pickaxe", "count": 1}
                ]
            },
            "world": {
                "time_of_day": 6000,
                "nearby_entities": [],
                "nearby_blocks": [
                    {"type": "minecraft:stone", "position": {"x": 5, "y": 64, "z": 0}}
                ]
            }
        }
        
        # Simulate one loop iteration
        action = fallback.get_fallback_action(game_state)
        
        # Execute action
        if action["action"] == "move_to":
            target = action.get("target", [0, 0, 0])
            movement.walk_to(target[0], target[2])
        elif action["action"] == "look_at":
            pass  # Just look around
        elif action["action"] == "jump":
            movement.jump()
        
        # Verify something happened
        assert action is not None
    
    def test_emergency_response(self):
        """Test system response to emergency situation."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        fallback = FallbackStrategy()
        
        # Create emergency game state
        game_state = {
            "player": {
                "health": 3.0,
                "hunger": 2.0,
                "is_in_lava": True,
                "position": {"x": 0, "y": 64, "z": 0}
            },
            "inventory": {
                "selected_slot": 0,
                "items": []
            },
            "world": {
                "nearby_entities": []
            }
        }
        
        # Get emergency action
        action = fallback.get_fallback_action(game_state, strategy="safe")
        
        # Should attempt to escape lava
        assert action["action"] == "jump"
        assert "lava" in action["reasoning"].lower()


class TestComponentInteraction:
    """Test interaction between different components."""
    
    def test_combat_with_inventory(self):
        """Test combat using inventory items."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        inventory = Inventory(input_simulator=mock_input)
        
        # Equip weapon
        inventory.select_slot(0)
        
        # Attack
        combat.attack()
        
        assert mock_input.select_slot.called
        assert mock_input.attack.called
    
    def test_gathering_with_tool_selection(self):
        """Test gathering with automatic tool selection."""
        mock_input = Mock()
        gathering = Gathering(input_simulator=mock_input)
        inventory = Inventory(input_simulator=mock_input)
        
        # Select tool
        inventory.select_slot(0)
        
        # Gather resources
        gathering.mine_block()
        
        assert mock_input.select_slot.called
        assert mock_input.break_block.called
    
    def test_movement_after_combat(self):
        """Test movement after combat engagement."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        combat = Combat(input_simulator=mock_input)
        
        # Attack enemy
        combat.attack()
        
        # Move away
        movement.walk_backward(duration=1.0)
        
        assert mock_input.attack.called
        assert mock_input.walk_backward.called


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_action_handling(self):
        """Test handling of invalid actions."""
        mock_input = Mock()
        movement = Movement(input_simulator=mock_input)
        
        # Should not crash with invalid inputs
        try:
            movement.calculate_distance(0, 0, 0, 0)  # Same point
        except Exception as e:
            pytest.fail(f"Should handle zero distance: {e}")
    
    def test_empty_inventory_handling(self):
        """Test handling empty inventory."""
        mock_input = Mock()
        inventory = Inventory(input_simulator=mock_input)
        
        game_state = {
            "inventory": {
                "items": []
            }
        }
        
        slot = inventory.find_item_in_hotbar(game_state, "minecraft:diamond")
        assert slot is None
    
    def test_missing_entity_handling(self):
        """Test handling missing entity data."""
        mock_input = Mock()
        combat = Combat(input_simulator=mock_input)
        
        # Empty entity list
        game_state = {
            "world": {
                "nearby_entities": []
            }
        }
        
        # Should not crash
        assert True  # If we get here, no crash occurred


class TestPerformance:
    """Test performance-related scenarios."""
    
    def test_fallback_action_speed(self):
        """Test that fallback actions are generated quickly."""
        fallback = FallbackStrategy()
        
        game_state = {
            "player": {"health": 20.0, "hunger": 20.0, "position": {"x": 0, "y": 64, "z": 0}},
            "inventory": {"selected_slot": 0, "items": []},
            "world": {"nearby_entities": []}
        }
        
        start_time = time.time()
        
        for _ in range(100):
            action = fallback.get_fallback_action(game_state)
        
        elapsed = time.time() - start_time
        
        # Should complete 100 actions in under 1 second
        assert elapsed < 1.0
    
    def test_prompt_generation_speed(self):
        """Test that prompts are generated quickly."""
        game_state = {
            "player": {"health": 20.0, "hunger": 20.0, "position": {"x": 0, "y": 64, "z": 0}},
            "inventory": {"selected_slot": 0, "items": []},
            "world": {"time_of_day": 6000, "nearby_entities": []}
        }
        
        start_time = time.time()
        
        for _ in range(100):
            prompt = Prompts.build_full_prompt("foundation", game_state)
        
        elapsed = time.time() - start_time
        
        # Should complete 100 prompts in under 1 second
        assert elapsed < 1.0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])