"""
Test Suite for AI Module
========================

Tests for DecisionMaker, Prompts, and FallbackStrategy.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

# Import AI components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.prompts import Prompts
from ai.fallback import FallbackStrategy, FallbackType, get_fallback_action


class TestPrompts:
    """Test cases for Prompts class."""
    
    def test_system_prompt_exists(self):
        """Test that system prompt is defined."""
        prompt = Prompts.get_system_prompt()
        assert prompt is not None
        assert len(prompt) > 0
        assert "Minecraft AI assistant" in prompt
    
    def test_format_prompt_basic(self):
        """Test basic prompt formatting."""
        template = "Hello {name}, you are at {location}."
        result = Prompts.format_prompt(template, name="Player", location="spawn")
        
        assert result == "Hello Player, you are at spawn."
    
    def test_format_prompt_missing_placeholder(self):
        """Test format_prompt with missing placeholder."""
        template = "Hello {name}, you are at {location}."
        
        with pytest.raises(KeyError):
            Prompts.format_prompt(template, name="Player")
    
    def test_format_prompt_extra_kwargs(self):
        """Test format_prompt with extra kwargs."""
        template = "Hello {name}."
        result = Prompts.format_prompt(template, name="Player", extra="ignored")
        
        assert result == "Hello Player."
    
    def test_get_phase_prompt_valid(self):
        """Test getting valid phase prompts."""
        valid_phases = ["foundation", "resources", "tools", "mining", "nether", "stronghold", "dragon"]
        
        for phase in valid_phases:
            prompt = Prompts.get_phase_prompt(phase)
            assert prompt is not None
            assert len(prompt) > 0
    
    def test_get_phase_prompt_invalid(self):
        """Test getting invalid phase prompt."""
        with pytest.raises(ValueError):
            Prompts.get_phase_prompt("invalid_phase")
    
    def test_get_phase_prompt_with_focus(self):
        """Test getting phase prompt with custom focus."""
        prompt = Prompts.get_phase_prompt("foundation", focus="Finding wood")
        assert "Finding wood" in prompt
    
    def test_get_emergency_prompt(self):
        """Test emergency prompt generation."""
        prompt = Prompts.get_emergency_prompt(
            health=3.0,
            hunger=5.0,
            threats="Zombie nearby",
            position="(100, 64, 200)"
        )
        
        assert "EMERGENCY" in prompt
        assert "3.0" in prompt
        assert "Zombie nearby" in prompt
    
    def test_get_exploration_prompt(self):
        """Test exploration prompt generation."""
        prompt = Prompts.get_exploration_prompt(
            position="(0, 64, 0)",
            inventory_summary="Basic tools",
            time_of_day=6000,
            weather="Clear"
        )
        
        assert "Exploration" in prompt
        assert "0, 64, 0" in prompt
    
    def test_get_phase_objectives(self):
        """Test getting phase objectives."""
        objectives = Prompts.get_phase_objectives("foundation")
        assert "wood" in objectives.lower() or "survival" in objectives.lower()
        
        objectives = Prompts.get_phase_objectives("dragon")
        assert "dragon" in objectives.lower()
    
    def test_build_full_prompt_normal(self):
        """Test building full prompt in normal conditions."""
        game_state = {
            "player": {
                "health": 20.0,
                "hunger": 18.0,
                "position": {"x": 0, "y": 64, "z": 0}
            },
            "world": {
                "nearby_entities": []
            }
        }
        
        prompt = Prompts.build_full_prompt(
            phase="foundation",
            game_state=game_state,
            recent_actions="Collected wood",
            focus="Crafting tools"
        )
        
        assert prompt is not None
        assert "foundation" in prompt.lower() or "Foundation" in prompt
    
    def test_build_full_prompt_emergency(self):
        """Test building prompt in emergency conditions."""
        game_state = {
            "player": {
                "health": 3.0,  # Critical health
                "hunger": 2.0,  # Critical hunger
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
        
        # Should use emergency prompt
        assert "EMERGENCY" in prompt or "emergency" in prompt.lower()


class TestFallbackStrategy:
    """Test cases for FallbackStrategy class."""
    
    def test_initialization_default(self):
        """Test default initialization."""
        strategy = FallbackStrategy()
        assert strategy.default_strategy == "safe"
        assert len(strategy._action_history) == 0
    
    def test_initialization_custom(self):
        """Test initialization with custom strategy."""
        strategy = FallbackStrategy(default_strategy="explore")
        assert strategy.default_strategy == "explore"
    
    def test_get_fallback_action_safe(self):
        """Test safe fallback strategy."""
        strategy = FallbackStrategy(default_strategy="safe")
        
        game_state = {
            "player": {
                "health": 20.0,
                "hunger": 20.0,
                "is_on_ground": True,
                "is_in_water": False,
                "is_in_lava": False,
                "position": {"x": 0, "y": 64, "z": 0},
                "yaw": 0.0
            },
            "inventory": {
                "selected_slot": 0,
                "items": []
            },
            "world": {
                "nearby_entities": []
            }
        }
        
        action = strategy.get_fallback_action(game_state, strategy="safe")
        
        assert action is not None
        assert "action" in action
        assert "reasoning" in action
        assert action["reasoning"].startswith("Fallback action")
    
    def test_get_fallback_action_explore(self):
        """Test explore fallback strategy."""
        strategy = FallbackStrategy(default_strategy="explore")
        
        game_state = {
            "player": {
                "health": 20.0,
                "hunger": 20.0,
                "is_on_ground": True,
                "position": {"x": 0, "y": 64, "z": 0},
                "yaw": 0.0
            },
            "inventory": {"selected_slot": 0, "items": []},
            "world": {"nearby_entities": []}
        }
        
        action = strategy.get_fallback_action(game_state, strategy="explore")
        
        assert action is not None
        assert "action" in action
        # Explore actions should be look_at, jump, or move_to
        assert action["action"] in ["look_at", "jump", "move_to"]
    
    def test_get_fallback_action_random(self):
        """Test random fallback strategy."""
        strategy = FallbackStrategy(default_strategy="random")
        
        game_state = {
            "player": {
                "health": 20.0,
                "hunger": 20.0,
                "is_on_ground": True,
                "position": {"x": 0, "y": 64, "z": 0}
            },
            "inventory": {"selected_slot": 0, "items": []},
            "world": {"nearby_entities": []}
        }
        
        action = strategy.get_fallback_action(game_state, strategy="random")
        
        assert action is not None
        assert "action" in action
    
    def test_safe_fallback_in_lava(self):
        """Test safe fallback when in lava."""
        strategy = FallbackStrategy()
        
        game_state = {
            "player": {
                "health": 15.0,
                "hunger": 20.0,
                "is_in_lava": True,
                "position": {"x": 0, "y": 64, "z": 0}
            },
            "inventory": {"selected_slot": 0, "items": []},
            "world": {"nearby_entities": []}
        }
        
        action = strategy._safe_fallback(game_state)
        
        assert action["action"] == "jump"
        assert "lava" in action["reasoning"].lower()
    
    def test_safe_fallback_low_health_with_food(self):
        """Test safe fallback with low health and food available."""
        strategy = FallbackStrategy()
        
        game_state = {
            "player": {
                "health": 5.0,
                "hunger": 5.0,
                "is_in_lava": False,
                "position": {"x": 0, "y": 64, "z": 0}
            },
            "inventory": {
                "selected_slot": 0,
                "items": [
                    {"slot": 1, "item_id": "minecraft:cooked_beef", "count": 5}
                ]
            },
            "world": {"nearby_entities": []}
        }
        
        action = strategy._safe_fallback(game_state)
        
        # Should select food to eat
        assert action["action"] == "select_slot"
    
    def test_safe_fallback_hostile_nearby(self):
        """Test safe fallback with hostile entity nearby."""
        strategy = FallbackStrategy()
        
        game_state = {
            "player": {
                "health": 15.0,
                "hunger": 15.0,
                "is_in_lava": False,
                "position": {"x": 0, "y": 64, "z": 0}
            },
            "inventory": {
                "selected_slot": 0,
                "items": [
                    {"slot": 0, "item_id": "minecraft:diamond_sword", "count": 1}
                ]
            },
            "world": {
                "nearby_entities": [
                    {"type": "minecraft:zombie", "is_hostile": True, "distance": 3.0, "position": {"x": 3, "y": 64, "z": 0}}
                ]
            }
        }
        
        action = strategy._safe_fallback(game_state)
        
        # Should attack or flee
        assert action["action"] in ["attack", "flee"]
    
    def test_find_food_slot(self):
        """Test finding food in inventory."""
        strategy = FallbackStrategy()
        
        inventory = {
            "items": [
                {"slot": 0, "item_id": "minecraft:diamond_sword", "count": 1},
                {"slot": 3, "item_id": "minecraft:bread", "count": 10},
                {"slot": 5, "item_id": "minecraft:stone", "count": 64}
            ]
        }
        
        food_slot = strategy._find_food_slot(inventory)
        assert food_slot == 3
    
    def test_find_food_slot_no_food(self):
        """Test finding food when none available."""
        strategy = FallbackStrategy()
        
        inventory = {
            "items": [
                {"slot": 0, "item_id": "minecraft:diamond_sword", "count": 1},
                {"slot": 5, "item_id": "minecraft:stone", "count": 64}
            ]
        }
        
        food_slot = strategy._find_food_slot(inventory)
        assert food_slot is None
    
    def test_get_retreat_target(self):
        """Test calculating retreat target."""
        strategy = FallbackStrategy()
        
        player = {"position": {"x": 100.0, "y": 64.0, "z": 200.0}}
        threat = {"position": {"x": 105.0, "y": 64.0, "z": 200.0}}
        
        target = strategy._get_retreat_target(player, threat)
        
        # Should move away from threat
        assert target[0] < 100.0  # Moving in negative X direction
        assert target[2] == 200.0  # Z stays same
    
    def test_action_history_tracking(self):
        """Test action history tracking."""
        strategy = FallbackStrategy()
        
        game_state = {
            "player": {"health": 20.0, "hunger": 20.0, "position": {"x": 0, "y": 64, "z": 0}},
            "inventory": {"selected_slot": 0, "items": []},
            "world": {"nearby_entities": []}
        }
        
        # Get multiple actions
        for _ in range(5):
            strategy.get_fallback_action(game_state)
        
        assert len(strategy._action_history) == 5
    
    def test_clear_history(self):
        """Test clearing action history."""
        strategy = FallbackStrategy()
        
        game_state = {
            "player": {"health": 20.0, "hunger": 20.0, "position": {"x": 0, "y": 64, "z": 0}},
            "inventory": {"selected_slot": 0, "items": []},
            "world": {"nearby_entities": []}
        }
        
        strategy.get_fallback_action(game_state)
        assert len(strategy._action_history) == 1
        
        strategy.clear_history()
        assert len(strategy._action_history) == 0
    
    def test_get_last_action(self):
        """Test getting last action."""
        strategy = FallbackStrategy()
        
        assert strategy.get_last_action() is None
        
        game_state = {
            "player": {"health": 20.0, "hunger": 20.0, "position": {"x": 0, "y": 64, "z": 0}},
            "inventory": {"selected_slot": 0, "items": []},
            "world": {"nearby_entities": []}
        }
        
        action = strategy.get_fallback_action(game_state)
        last_action = strategy.get_last_action()
        
        assert last_action == action
    
    def test_set_default_strategy(self):
        """Test setting default strategy."""
        strategy = FallbackStrategy()
        
        strategy.set_default_strategy("explore")
        assert strategy.default_strategy == "explore"
        
        strategy.set_default_strategy("random")
        assert strategy.default_strategy == "random"
        
        # Invalid strategy should not change
        strategy.set_default_strategy("invalid")
        assert strategy.default_strategy == "random"
    
    def test_get_available_strategies(self):
        """Test getting available strategies."""
        strategy = FallbackStrategy()
        strategies = strategy.get_available_strategies()
        
        assert "safe" in strategies
        assert "explore" in strategies
        assert "random" in strategies
        assert len(strategies) == 3
    
    def test_max_history_limit(self):
        """Test that history respects max limit."""
        strategy = FallbackStrategy()
        
        game_state = {
            "player": {"health": 20.0, "hunger": 20.0, "position": {"x": 0, "y": 64, "z": 0}},
            "inventory": {"selected_slot": 0, "items": []},
            "world": {"nearby_entities": []}
        }
        
        # Get more actions than max history
        for _ in range(15):
            strategy.get_fallback_action(game_state)
        
        # Should be limited to max_history (10)
        assert len(strategy._action_history) == 10


class TestGetFallbackActionFunction:
    """Test the convenience function get_fallback_action."""
    
    def test_get_fallback_action_basic(self):
        """Test basic fallback action retrieval."""
        game_state = {
            "player": {
                "health": 20.0,
                "hunger": 20.0,
                "position": {"x": 0, "y": 64, "z": 0}
            },
            "inventory": {"selected_slot": 0, "items": []},
            "world": {"nearby_entities": []}
        }
        
        action = get_fallback_action(game_state)
        
        assert action is not None
        assert "action" in action
    
    def test_get_fallback_action_with_strategy(self):
        """Test fallback action with specific strategy."""
        game_state = {
            "player": {
                "health": 20.0,
                "hunger": 20.0,
                "position": {"x": 0, "y": 64, "z": 0}
            },
            "inventory": {"selected_slot": 0, "items": []},
            "world": {"nearby_entities": []}
        }
        
        for strategy in ["safe", "explore", "random"]:
            action = get_fallback_action(game_state, strategy=strategy)
            assert action is not None
            assert "action" in action


class TestFallbackType:
    """Test FallbackType enum."""
    
    def test_fallback_types(self):
        """Test that all fallback types are defined."""
        assert FallbackType.SAFE.value == "safe"
        assert FallbackType.EXPLORE.value == "explore"
        assert FallbackType.RANDOM.value == "random"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])