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
import os
import signal
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


# Configure logging
def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Set up logging based on configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured logger
    """
    log_level = config.get("log_level", "INFO")
    log_file = config.get("log_file", "minecraft_ai.log")
    log_to_console = config.get("log_to_console", True)
    log_to_file = config.get("log_to_file", True)
    
    # Create logger
    logger = logging.getLogger("MinecraftAI")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create log file {log_file}: {e}")
    
    return logger


class MinecraftAutomation:
    """
    Main automation controller that orchestrates all components.
    
    This class manages the game loop, component initialization,
    phase transitions, and error handling.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the automation system.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = setup_logging(self.config)
        self.running = False
        self.paused = False
        
        # Components (to be initialized)
        self.memory_reader = None
        self.ai_provider = None
        self.current_phase = None
        self.input_simulator = None
        self.fallback_strategy = None
        
        # Statistics
        self.start_time = None
        self.tick_count = 0
        self.actions_executed = 0
        self.errors_count = 0
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("MinecraftAutomation initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        config_file = Path(config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                print(f"Loaded config from {config_path}")
                return config
            except yaml.YAMLError as e:
                print(f"Error parsing config file: {e}")
                print("Using default configuration")
        else:
            print(f"Config file {config_path} not found, using defaults")
        
        # Default configuration
        return {
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
            ],
            "safety": {
                "min_health_threshold": 6.0,
                "min_hunger_threshold": 4.0
            }
        }
    
    def validate_config(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if configuration is valid
        """
        required_keys = ["ai_provider", "tick_rate", "phase_order"]
        
        for key in required_keys:
            if key not in self.config:
                self.logger.error(f"Missing required config key: {key}")
                return False
        
        # Validate tick rate
        tick_rate = self.config.get("tick_rate", 20)
        if not 1 <= tick_rate <= 100:
            self.logger.warning(f"Tick rate {tick_rate} outside recommended range (1-100)")
        
        # Validate AI provider
        valid_providers = ["gemini", "groq", "ollama"]
        provider = self.config.get("ai_provider", "gemini")
        if provider not in valid_providers:
            self.logger.error(f"Invalid AI provider: {provider}. Must be one of {valid_providers}")
            return False
        
        self.logger.info("Configuration validated successfully")
        return True
    
    def initialize_components(self) -> bool:
        """
        Initialize all system components.
        
        Returns:
            True if initialization successful
        """
        self.logger.info("Initializing components...")
        
        # Import components
        try:
            from core import MemoryReader, InputSimulator
            from ai import configure_ai_provider, FallbackStrategy
            from phases import Phase1_Foundation
            
            # Initialize memory reader
            try:
                offsets_file = self.config.get("memory", {}).get("offsets_file", "offsets.json")
                self.memory_reader = MemoryReader(offsets_file=offsets_file)
                self.logger.info("MemoryReader initialized")
            except Exception as e:
                self.logger.warning(f"MemoryReader initialization failed: {e}")
                self.memory_reader = None
            
            # Initialize input simulator
            try:
                self.input_simulator = InputSimulator()
                self.logger.info("InputSimulator initialized")
            except Exception as e:
                self.logger.warning(f"InputSimulator initialization failed: {e}")
                self.input_simulator = None
            
            # Configure AI provider
            try:
                api_key = self.config.get("api_key", "")
                # Expand environment variables in API key
                if api_key.startswith("${") and api_key.endswith("}"):
                    env_var = api_key[2:-1]
                    api_key = os.environ.get(env_var, "")
                
                configure_ai_provider(
                    self.config["ai_provider"],
                    api_key=api_key if api_key else None
                )
                self.logger.info(f"AI provider configured: {self.config['ai_provider']}")
            except Exception as e:
                self.logger.warning(f"AI provider configuration failed: {e}")
            
            # Initialize fallback strategy
            self.fallback_strategy = FallbackStrategy(default_strategy="safe")
            self.logger.info("FallbackStrategy initialized")
            
            # Initialize first phase
            try:
                starting_phase = self.config.get("starting_phase", "")
                if not starting_phase:
                    starting_phase = self.config.get("phase_order", ["foundation"])[0]
                
                if starting_phase == "foundation":
                    self.current_phase = Phase1_Foundation(
                        game_state_provider=self._get_game_state,
                        action_decider=self._get_action_decider()
                    )
                    self.logger.info("Phase1_Foundation initialized")
                else:
                    self.logger.info(f"Starting phase: {starting_phase}")
                    # TODO: Initialize other phases
            except Exception as e:
                self.logger.warning(f"Phase initialization failed: {e}")
            
            self.logger.info("Component initialization complete")
            return True
            
        except ImportError as e:
            self.logger.error(f"Failed to import component: {e}")
            self.logger.info("Running in simulation mode")
            return False
    
    def _get_game_state(self) -> Optional[Dict[str, Any]]:
        """
        Get the current game state.
        
        Returns:
            Game state dictionary or simulated state
        """
        if self.memory_reader:
            try:
                state = self.memory_reader.get_game_state()
                if state:
                    return state.to_dict() if hasattr(state, 'to_dict') else state
            except Exception as e:
                self.logger.debug(f"Error reading game state: {e}")
        
        # Return simulated state for testing
        return self._get_simulated_state()
    
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
            self.logger.warning("AI module not available, using fallback")
            return lambda state: self.fallback_strategy.get_fallback_action(state)
    
    def _get_simulated_state(self) -> Dict[str, Any]:
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
    
    def run(self):
        """
        Main automation loop.
        """
        self.logger.info("=" * 50)
        self.logger.info("Starting Minecraft AI Automation")
        self.logger.info("=" * 50)
        
        # Validate configuration
        if not self.validate_config():
            self.logger.error("Configuration validation failed")
            return
        
        # Initialize components
        if not self.initialize_components():
            self.logger.warning("Some components failed to initialize")
        
        self.running = True
        self.start_time = time.time()
        
        try:
            while self.running:
                # Handle pause
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                # 1. Get current game state
                state = self._get_game_state()
                
                if state is None:
                    self.logger.warning("Failed to get game state")
                    time.sleep(0.1)
                    continue
                
                # 2. Check if current phase is complete
                if self.current_phase and self.current_phase.is_complete():
                    self._advance_phase()
                
                # 3. Execute current phase
                action = None
                if self.current_phase:
                    try:
                        action = self.current_phase.execute()
                    except Exception as e:
                        self.logger.error(f"Error executing phase: {e}")
                        self.errors_count += 1
                        # Use fallback action
                        if self.fallback_strategy:
                            action = self.fallback_strategy.get_fallback_action(state)
                
                # 4. Execute action
                if action:
                    self._execute_action(action)
                    self.actions_executed += 1
                
                # 5. Log state periodically
                self.tick_count += 1
                self._log_state(state)
                
                # 6. Sleep for tick rate
                tick_rate = self.config.get("tick_rate", 20)
                time.sleep(1 / tick_rate)
                
        except KeyboardInterrupt:
            self.logger.info("Automation stopped by user (Ctrl+C)")
        except Exception as e:
            self.logger.error(f"Fatal error in main loop: {e}")
            raise
        finally:
            self.cleanup()
    
    def _advance_phase(self):
        """Advance to the next phase."""
        phase_order = self.config.get("phase_order", [])
        
        if not self.current_phase:
            return
        
        # Get current phase name
        current_class = self.current_phase.__class__.__name__
        current_name = current_class.lower().replace("phase", "").split("_")[1] if "_" in current_class else "unknown"
        
        try:
            current_index = phase_order.index(current_name)
            if current_index < len(phase_order) - 1:
                next_phase_name = phase_order[current_index + 1]
                self.logger.info(f"Phase complete! Advancing to: {next_phase_name}")
                # TODO: Initialize next phase based on name
            else:
                self.logger.info("All phases complete! Automation finished.")
                self.running = False
        except ValueError:
            self.logger.warning(f"Current phase {current_name} not found in phase order")
    
    def _execute_action(self, action: Dict[str, Any]):
        """
        Execute an action.
        
        Args:
            action: Action dictionary
        """
        if not action:
            return
        
        action_type = action.get("action", "none")
        params = action.get("params", {})
        target = action.get("target")
        reasoning = action.get("reasoning", "")
        
        if reasoning:
            self.logger.debug(f"Action: {action_type} - {reasoning}")
        
        if not self.input_simulator:
            self.logger.debug(f"Would execute: {action_type}")
            return
        
        try:
            # Route to appropriate input function
            if action_type == "move_to" and target:
                self.input_simulator.move_to(target[0], target[2])
            elif action_type == "look_at" and target:
                self.input_simulator.look_at_position(target[0], target[1], target[2])
            elif action_type == "attack":
                self.input_simulator.attack(params.get("hold_ticks", 10))
            elif action_type == "jump":
                self.input_simulator.jump()
            elif action_type == "sneak":
                self.input_simulator.sneak(params.get("duration", 0.5))
            elif action_type == "use_item":
                self.input_simulator.use_item(params.get("hold_ticks", 10))
            elif action_type == "place_block":
                self.input_simulator.place_block()
            elif action_type == "break_block":
                self.input_simulator.break_block(params.get("hold_ticks", 20))
            elif action_type == "select_slot":
                self.input_simulator.select_slot(params.get("slot", 0))
            elif action_type == "open_inventory":
                self.input_simulator.open_inventory()
            elif action_type == "close_inventory":
                self.input_simulator.close_inventory()
            elif action_type == "drop_item":
                self.input_simulator.drop_item(params.get("all", False))
            elif action_type == "defend":
                self.input_simulator.block_with_shield(params.get("duration", 1.0))
            elif action_type == "flee" and target:
                self.input_simulator.sprint_forward(params.get("duration", 2.0))
            elif action_type == "wait":
                time.sleep(params.get("duration", 1.0))
            elif action_type == "none":
                pass  # Do nothing
            else:
                self.logger.debug(f"Unknown action type: {action_type}")
                
        except Exception as e:
            self.logger.error(f"Error executing action {action_type}: {e}")
            self.errors_count += 1
    
    def _log_state(self, state: Dict[str, Any]):
        """
        Log the current game state.
        
        Args:
            state: GameState dictionary
        """
        # Log every 100 ticks
        if self.tick_count % 100 == 0:
            player = state.get("player", {})
            position = player.get("position", {})
            self.logger.info(
                f"Tick {self.tick_count}: "
                f"Pos=({position.get('x', 0):.1f}, "
                f"{position.get('y', 0):.1f}, "
                f"{position.get('z', 0):.1f}), "
                f"HP={player.get('health', 0):.1f}, "
                f"Hunger={player.get('hunger', 0):.1f}"
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get automation statistics.
        
        Returns:
            Statistics dictionary
        """
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        return {
            "running_time": elapsed,
            "tick_count": self.tick_count,
            "actions_executed": self.actions_executed,
            "errors_count": self.errors_count,
            "ticks_per_second": self.tick_count / elapsed if elapsed > 0 else 0,
            "actions_per_second": self.actions_executed / elapsed if elapsed > 0 else 0
        }
    
    def cleanup(self):
        """Clean up resources before exit."""
        self.logger.info("Cleaning up...")
        self.running = False
        
        # Print statistics
        stats = self.get_statistics()
        self.logger.info("=" * 50)
        self.logger.info("Session Statistics:")
        self.logger.info(f"  Running time: {stats['running_time']:.1f} seconds")
        self.logger.info(f"  Ticks processed: {stats['tick_count']}")
        self.logger.info(f"  Actions executed: {stats['actions_executed']}")
        self.logger.info(f"  Errors encountered: {stats['errors_count']}")
        self.logger.info("=" * 50)
        
        # Close any open resources
        if self.input_simulator:
            try:
                # Release any held keys
                pass
            except Exception as e:
                self.logger.debug(f"Error during cleanup: {e}")
        
        self.logger.info("Cleanup complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Minecraft AI Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Run with default settings
  python main.py --provider gemini        # Use Gemini AI provider
  python main.py --config custom.yaml     # Use custom config file
  python main.py --phase resources        # Start from resources phase
  python main.py --debug                  # Enable debug logging
        """
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["gemini", "groq", "ollama"],
        help="AI provider to use (overrides config)"
    )
    parser.add_argument(
        "--phase",
        type=str,
        choices=["foundation", "resources", "tools", "mining", "nether", "stronghold", "dragon"],
        help="Starting phase (overrides config)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--simulation",
        action="store_true",
        help="Run in simulation mode (no actual input)"
    )
    
    args = parser.parse_args()
    
    # Create automation instance
    automation = MinecraftAutomation(config_path=args.config)
    
    # Apply command-line overrides
    if args.provider:
        automation.config["ai_provider"] = args.provider
        automation.logger.info(f"AI provider overridden to: {args.provider}")
    
    if args.phase:
        automation.config["starting_phase"] = args.phase
        automation.logger.info(f"Starting phase overridden to: {args.phase}")
    
    if args.debug:
        automation.config["log_level"] = "DEBUG"
        automation.logger.setLevel(logging.DEBUG)
        automation.logger.info("Debug logging enabled")
    
    if args.simulation:
        automation.config["simulation_mode"] = True
        automation.logger.info("Simulation mode enabled")
    
    # Run automation
    try:
        automation.run()
    except Exception as e:
        automation.logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()