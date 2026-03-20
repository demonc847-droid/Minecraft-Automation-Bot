"""
Minecraft AI Automation - Main Entry Point
==========================================

This is the main entry point for the Minecraft AI automation system.
It initializes all components and runs the main automation loop.

Usage:
    python main.py [--config CONFIG_PATH] [--provider AI_PROVIDER] [--phase PHASE]

Examples:
    # Run with default settings
    python main.py

    # Run with specific AI provider
    python main.py --provider gemini

    # Run with custom config
    python main.py --config config.yaml

    # Start from specific phase
    python main.py --phase resources
"""

import argparse
import logging
import sys
import time
import yaml
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('minecraft_ai.log')
    ]
)
logger = logging.getLogger(__name__)


class MinecraftAutomation:
    """
    Main automation controller that orchestrates all components.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the automation system.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.running = False
        
        # Components (to be initialized)
        self.memory_reader = None
        self.ai_provider = None
        self.current_phase = None
        self.input_simulator = None
        
        logger.info("MinecraftAutomation initialized")
    
    def _load_config(self, config_path: str) -> dict:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        config_file = Path(config_path)
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded config from {config_path}")
        else:
            # Default configuration
            config = {
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
            logger.info("Using default configuration")
        
        return config
    
    def initialize_components(self):
        """
        Initialize all system components.
        """
        logger.info("Initializing components...")
        
        # Import components
        try:
            from core import MemoryReader, InputSimulator
            from ai import configure_ai_provider
            from phases import Phase1_Foundation
            
            # Initialize memory reader
            self.memory_reader = MemoryReader()
            logger.info("MemoryReader initialized")
            
            # Initialize input simulator
            self.input_simulator = InputSimulator()
            logger.info("InputSimulator initialized")
            
            # Configure AI provider
            configure_ai_provider(
                self.config["ai_provider"],
                api_key=self.config.get("api_key")
            )
            logger.info(f"AI provider configured: {self.config['ai_provider']}")
            
            # Initialize first phase
            self.current_phase = Phase1_Foundation(
                game_state_provider=self.memory_reader.get_game_state,
                action_decider=self._get_action_decider()
            )
            logger.info("Phase1_Foundation initialized")
            
        except ImportError as e:
            logger.error(f"Failed to import component: {e}")
            logger.info("Running in simulation mode (no actual components)")
    
    def _get_action_decider(self):
        """
        Get the action decision function.
        
        Returns:
            Callable that takes game_state and returns action
        """
        try:
            from ai import decide_action
            return decide_action
        except ImportError:
            logger.warning("AI module not available, using placeholder")
            return lambda state: {"action": "none", "params": {}}
    
    def run(self):
        """
        Main automation loop.
        """
        logger.info("Starting Minecraft AI Automation...")
        self.running = True
        
        try:
            while self.running:
                # 1. Get current game state
                if self.memory_reader:
                    state = self.memory_reader.get_game_state()
                else:
                    state = self._get_simulated_state()
                
                # 2. Check if current phase is complete
                if self.current_phase and self.current_phase.is_complete():
                    self._advance_phase()
                
                # 3. Execute current phase
                if self.current_phase:
                    action = self.current_phase.execute(state)
                    self._execute_action(action)
                
                # 4. Log state
                self._log_state(state)
                
                # 5. Sleep for tick rate
                tick_rate = self.config.get("tick_rate", 20)
                time.sleep(1 / tick_rate)
                
        except KeyboardInterrupt:
            logger.info("Automation stopped by user")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            raise
        finally:
            self.cleanup()
    
    def _get_simulated_state(self) -> dict:
        """
        Get a simulated game state for testing.
        
        Returns:
            Simulated GameState dictionary
        """
        return {
            "player": {
                "position": {"x": 0.0, "y": 64.0, "z": 0.0},
                "velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
                "health": 20.0,
                "hunger": 20.0,
                "saturation": 5.0,
                "experience_level": 0,
                "experience_progress": 0.0,
                "yaw": 0.0,
                "pitch": 0.0,
                "is_on_ground": True,
                "is_in_water": False,
                "is_in_lava": False,
                "is_sleeping": False,
                "dimension": "overworld"
            },
            "inventory": {
                "selected_slot": 0,
                "items": [],
                "armor": {"head": None, "chest": None, "legs": None, "feet": None},
                "offhand": None
            },
            "world": {
                "time_of_day": 0,
                "day_count": 0,
                "is_raining": False,
                "is_thundering": False,
                "difficulty": "normal",
                "game_mode": "survival",
                "seed": 0,
                "spawn_point": {"x": 0.0, "y": 64.0, "z": 0.0},
                "looking_at": None,
                "nearby_entities": [],
                "nearby_blocks": []
            },
            "timestamp": time.time()
        }
    
    def _advance_phase(self):
        """
        Advance to the next phase.
        """
        phase_order = self.config.get("phase_order", [])
        current_name = self.current_phase.__class__.__name__.lower().replace("phase", "").split("_")[1]
        
        try:
            current_index = phase_order.index(current_name)
            if current_index < len(phase_order) - 1:
                next_phase_name = phase_order[current_index + 1]
                logger.info(f"Advancing to phase: {next_phase_name}")
                # TODO: Initialize next phase
        except ValueError:
            logger.warning(f"Current phase {current_name} not in phase order")
    
    def _execute_action(self, action: dict):
        """
        Execute an action.
        
        Args:
            action: Action dictionary
        """
        if not action:
            return
        
        action_type = action.get("action", "none")
        params = action.get("params", {})
        
        logger.debug(f"Executing action: {action_type} with params: {params}")
        
        if self.input_simulator:
            # Route to appropriate input function
            if action_type == "move_to":
                target = action.get("target", [0, 0, 0])
                self.input_simulator.move_to(target[0], target[2])
            elif action_type == "look_at":
                target = action.get("target", [0, 0, 0])
                self.input_simulator.look_at_position(target[0], target[1], target[2])
            elif action_type == "attack":
                self.input_simulator.attack(params.get("hold_ticks", 10))
            elif action_type == "jump":
                self.input_simulator.jump()
            # ... handle other actions
    
    def _log_state(self, state: dict):
        """
        Log the current game state.
        
        Args:
            state: GameState dictionary
        """
        # Only log occasionally to avoid spam
        if hasattr(self, '_tick_count'):
            self._tick_count += 1
        else:
            self._tick_count = 0
        
        if self._tick_count % 100 == 0:  # Log every 100 ticks
            player = state.get("player", {})
            logger.info(
                f"Tick {self._tick_count}: "
                f"Pos=({player.get('position', {}).get('x', 0):.1f}, "
                f"{player.get('position', {}).get('y', 0):.1f}, "
                f"{player.get('position', {}).get('z', 0):.1f}), "
                f"HP={player.get('health', 0)}, "
                f"Hunger={player.get('hunger', 0)}"
            )
    
    def cleanup(self):
        """
        Clean up resources before exit.
        """
        logger.info("Cleaning up...")
        self.running = False
        # TODO: Close any open resources


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(
        description="Minecraft AI Automation System"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["gemini", "groq", "ollama"],
        help="AI provider to use"
    )
    parser.add_argument(
        "--phase",
        type=str,
        choices=["foundation", "resources", "tools", "mining", "nether", "stronghold", "dragon"],
        help="Starting phase"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run automation
    automation = MinecraftAutomation(config_path=args.config)
    
    # Override provider if specified
    if args.provider:
        automation.config["ai_provider"] = args.provider
    
    # Initialize and run
    automation.initialize_components()
    automation.run()


if __name__ == "__main__":
    main()