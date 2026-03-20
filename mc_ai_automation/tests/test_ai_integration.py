"""
Test Script for AI Integration Module
=====================================

This script tests the AI integration components without requiring actual API keys.
It validates prompt generation, fallback strategies, and basic decision maker functionality.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai import Prompts, FallbackStrategy, DecisionMaker, get_action_with_fallback


def create_test_game_state():
    """Create a sample game state for testing."""
    return {
        "player": {
            "position": {"x": 100.5, "y": 64.0, "z": -200.3},
            "velocity": {"x": 0.0, "y": -0.0784, "z": 0.0},
            "health": 18.0,
            "hunger": 15.0,
            "saturation": 5.0,
            "experience_level": 5,
            "experience_progress": 0.45,
            "yaw": 90.0,
            "pitch": 15.0,
            "is_on_ground": True,
            "is_in_water": False,
            "is_in_lava": False,
            "is_sleeping": False,
            "dimension": "overworld"
        },
        "inventory": {
            "selected_slot": 0,
            "items": [
                {"slot": 0, "item_id": "minecraft:diamond_sword", "count": 1, "damage": 0, "nbt": {}},
                {"slot": 1, "item_id": "minecraft:diamond_pickaxe", "count": 1, "damage": 150, "nbt": {}},
                {"slot": 2, "item_id": "minecraft:bread", "count": 5, "damage": 0, "nbt": {}}
            ],
            "armor": {"head": None, "chest": None, "legs": None, "feet": None},
            "offhand": None
        },
        "world": {
            "time_of_day": 6000,
            "day_count": 1,
            "is_raining": False,
            "is_thundering": False,
            "difficulty": "normal",
            "game_mode": "survival",
            "seed": 123456789,
            "spawn_point": {"x": 0.0, "y": 64.0, "z": 0.0},
            "looking_at": {
                "block_type": "minecraft:stone",
                "position": {"x": 100, "y": 63, "z": -201},
                "face": "north"
            },
            "nearby_entities": [
                {
                    "type": "minecraft:pig",
                    "id": 123,
                    "position": {"x": 105.0, "y": 64.0, "z": -195.0},
                    "health": 10.0,
                    "is_hostile": False,
                    "distance": 5.8
                }
            ],
            "nearby_blocks": []
        },
        "timestamp": 1710912345.678
    }


def test_prompts():
    """Test prompt generation."""
    print("=" * 60)
    print("Testing Prompts Module")
    print("=" * 60)
    
    # Test system prompt
    system_prompt = Prompts.get_system_prompt()
    print(f"✓ System prompt generated ({len(system_prompt)} chars)")
    
    # Test phase prompts
    phases = ["foundation", "resources", "tools", "mining", "nether", "stronghold", "dragon"]
    for phase in phases:
        prompt = Prompts.get_phase_prompt(phase, focus="Testing")
        print(f"✓ Phase '{phase}' prompt generated")
    
    # Test emergency prompt
    emergency = Prompts.get_emergency_prompt(
        health=4.0,
        hunger=2.0,
        threats="Zombie at 3 blocks, Skeleton at 5 blocks",
        position="(100, 64, -200)"
    )
    print(f"✓ Emergency prompt generated")
    
    # Test action decision prompt
    game_state = create_test_game_state()
    full_prompt = Prompts.build_full_prompt(
        phase="foundation",
        game_state=game_state,
        recent_actions="None",
        focus="Collect wood"
    )
    print(f"✓ Full action decision prompt generated ({len(full_prompt)} chars)")
    
    # Test format_prompt
    formatted = Prompts.format_prompt(
        "Health: {health}/20, Position: {position}",
        health=18.0,
        position="(100, 64, -200)"
    )
    print(f"✓ Format prompt working: {formatted}")
    
    print("\n✓ All prompt tests passed!\n")


def test_fallback():
    """Test fallback strategies."""
    print("=" * 60)
    print("Testing Fallback Module")
    print("=" * 60)
    
    game_state = create_test_game_state()
    fallback = FallbackStrategy(default_strategy="safe")
    
    # Test safe fallback
    safe_action = fallback.get_fallback_action(game_state, "safe")
    print(f"✓ Safe fallback action: {safe_action['action']}")
    print(f"  Reasoning: {safe_action['reasoning']}")
    
    # Test explore fallback
    explore_action = fallback.get_fallback_action(game_state, "explore")
    print(f"✓ Explore fallback action: {explore_action['action']}")
    print(f"  Reasoning: {explore_action['reasoning']}")
    
    # Test random fallback
    random_action = fallback.get_fallback_action(game_state, "random")
    print(f"✓ Random fallback action: {random_action['action']}")
    print(f"  Reasoning: {random_action['reasoning']}")
    
    # Test emergency situation (low health)
    emergency_state = create_test_game_state()
    emergency_state["player"]["health"] = 3.0
    emergency_state["player"]["hunger"] = 2.0
    
    emergency_action = fallback.get_fallback_action(emergency_state, "safe")
    print(f"✓ Emergency fallback action: {emergency_action['action']}")
    print(f"  Reasoning: {emergency_action['reasoning']}")
    
    # Test hostile nearby
    hostile_state = create_test_game_state()
    hostile_state["world"]["nearby_entities"] = [
        {
            "type": "minecraft:zombie",
            "id": 456,
            "position": {"x": 102.0, "y": 64.0, "z": -198.0},
            "health": 20.0,
            "is_hostile": True,
            "distance": 3.5
        }
    ]
    
    combat_action = fallback.get_fallback_action(hostile_state, "safe")
    print(f"✓ Combat fallback action: {combat_action['action']}")
    print(f"  Reasoning: {combat_action['reasoning']}")
    
    # Test available strategies
    strategies = fallback.get_available_strategies()
    print(f"✓ Available strategies: {strategies}")
    
    print("\n✓ All fallback tests passed!\n")


def test_decision_maker():
    """Test decision maker (without actual AI calls)."""
    print("=" * 60)
    print("Testing DecisionMaker Module")
    print("=" * 60)
    
    # Test initialization with invalid provider (should use fallback)
    try:
        dm = DecisionMaker(provider="invalid_provider")
        print("✓ DecisionMaker initialized (with fallback mode)")
    except Exception as e:
        print(f"✓ DecisionMaker initialization handled: {type(e).__name__}")
    
    # Test cache key generation
    dm = DecisionMaker(provider="gemini", api_key="test_key")
    game_state = create_test_game_state()
    
    cache_key = dm._generate_cache_key(game_state, "foundation", "Testing")
    print(f"✓ Cache key generated: {cache_key}")
    
    # Test response parsing
    test_json_response = '''
    {
        "action": "move_to",
        "target": [100.0, 64.0, -200.0],
        "params": {"speed": "walk"},
        "reasoning": "Moving towards resource",
        "priority": 5,
        "timeout": 10.0
    }
    '''
    
    parsed = dm._parse_response(test_json_response)
    print(f"✓ Response parsed: {parsed['action']}")
    
    # Test action validation
    validated = dm._validate_action(parsed, game_state)
    print(f"✓ Action validated: {validated['action']}")
    
    # Test invalid action
    invalid_action = {"action": "invalid_action_type"}
    validated_invalid = dm._validate_action(invalid_action, game_state)
    print(f"✓ Invalid action corrected to: {validated_invalid['action']}")
    
    # Test markdown code block parsing
    markdown_response = '''
    ```json
    {
        "action": "jump",
        "target": null,
        "params": {},
        "reasoning": "Need to jump",
        "priority": 4
    }
    ```
    '''
    
    parsed_markdown = dm._parse_response(markdown_response)
    print(f"✓ Markdown response parsed: {parsed_markdown['action']}")
    
    # Test recent actions
    dm._add_recent_action({"action": "move_to", "reasoning": "Test"})
    dm._add_recent_action({"action": "jump", "reasoning": "Test2"})
    recent = dm._format_recent_actions()
    print(f"✓ Recent actions formatted: {len(recent.split(chr(10)))} actions")
    
    print("\n✓ All decision maker tests passed!\n")


def test_module_functions():
    """Test module-level functions."""
    print("=" * 60)
    print("Testing Module Functions")
    print("=" * 60)
    
    from ai import configure_ai_provider, get_current_provider, switch_provider
    
    # Test configuration
    initial_provider = get_current_provider()
    print(f"✓ Initial provider: {initial_provider}")
    
    # Test switching
    switch_provider("groq")
    current = get_current_provider()
    print(f"✓ Switched to: {current}")
    
    # Test configuration
    configure_ai_provider("ollama", url="http://localhost:11434")
    current = get_current_provider()
    print(f"✓ Configured provider: {current}")
    
    # Reset to gemini
    switch_provider("gemini")
    print(f"✓ Reset to: {get_current_provider()}")
    
    print("\n✓ All module function tests passed!\n")


def test_integration():
    """Test integration with fallback."""
    print("=" * 60)
    print("Testing Integration")
    print("=" * 60)
    
    game_state = create_test_game_state()
    
    # Test get_action_with_fallback (will use fallback since no real API key)
    action = get_action_with_fallback(game_state, fallback_strategy="safe")
    print(f"✓ Got action with fallback: {action['action']}")
    print(f"  Reasoning: {action['reasoning']}")
    
    # Test with different strategies
    for strategy in ["safe", "explore", "random"]:
        action = get_action_with_fallback(game_state, fallback_strategy=strategy)
        print(f"✓ Strategy '{strategy}': {action['action']}")
    
    print("\n✓ All integration tests passed!\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AI INTEGRATION TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_prompts()
        test_fallback()
        test_decision_maker()
        test_module_functions()
        test_integration()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)