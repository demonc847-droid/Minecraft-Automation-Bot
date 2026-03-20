"""
Tests Module
============

This module contains all tests for the Minecraft AI automation system:
- Unit tests for individual components
- Integration tests for component interaction
- End-to-end tests for full system operation

Test Categories:
----------------
- test_core: Tests for memory reading, game state, input simulation
- test_ai: Tests for AI decision making, prompt handling, fallbacks
- test_actions: Tests for movement, combat, gathering, inventory
- test_phases: Tests for phase progression and objectives
- test_integration: Tests for full system integration

Usage:
------
    # Run all tests
    pytest tests/

    # Run specific test category
    pytest tests/test_core/
    pytest tests/test_ai/

    # Run with verbose output
    pytest tests/ -v
"""

# Test configuration
PYTEST_CONFIG = {
    "testpaths": ["tests"],
    "python_files": ["test_*.py"],
    "python_functions": ["test_*"],
    "python_classes": ["Test*"],
}