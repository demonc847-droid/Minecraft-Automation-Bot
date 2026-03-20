#!/usr/bin/env python3
"""
Minecraft AI Automation Runner Script

This script provides convenient ways to run the automation with
different configurations, modes, and debugging options.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"   ✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error running {description}: {e}")
        return False


def check_requirements():
    """Check if main.py exists and is executable."""
    main_file = Path("main.py")
    if not main_file.exists():
        print("❌ main.py not found in current directory")
        return False
    return True


def get_config_path(config_name):
    """Get the path to a configuration file."""
    config_dir = Path("data/configs")
    
    if config_name == "default":
        return config_dir / "config.yaml"
    elif config_name == "sample":
        return config_dir / "config.sample.yaml"
    else:
        return config_dir / f"{config_name}.yaml"


def main():
    """Main runner function."""
    parser = argparse.ArgumentParser(
        description="Run Minecraft AI Automation with various options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_automation.py                    # Run with default config
  python scripts/run_automation.py --simulation       # Run in simulation mode
  python scripts/run_automation.py --debug            # Enable debug mode
  python scripts/run_automation.py --phase resources  # Start from resources phase
  python scripts/run_automation.py --config custom    # Use custom config
        """
    )
    
    # Mode options
    parser.add_argument("--simulation", action="store_true", 
                       help="Run in simulation mode (no actual input)")
    parser.add_argument("--debug", action="store_true", 
                       help="Enable debug logging")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output")
    
    # Configuration options
    parser.add_argument("--config", type=str, default="default",
                       help="Configuration file to use (default, sample, or custom name)")
    parser.add_argument("--provider", type=str, choices=["gemini", "groq", "ollama"],
                       help="Override AI provider")
    parser.add_argument("--phase", type=str, 
                       choices=["foundation", "resources", "tools", "mining", "nether", "stronghold", "dragon"],
                       help="Override starting phase")
    
    # Development options
    parser.add_argument("--test", action="store_true",
                       help="Run tests instead of automation")
    parser.add_argument("--lint", action="store_true",
                       help="Run code linting")
    parser.add_argument("--format", action="store_true",
                       help="Format code with black")
    parser.add_argument("--clean", action="store_true",
                       help="Clean up temporary files")
    
    # Advanced options
    parser.add_argument("--no-prompt", action="store_true",
                       help="Skip confirmation prompts")
    parser.add_argument("--log-level", type=str, default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                       help="Set log level")
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not check_requirements():
        sys.exit(1)
    
    # Handle development tasks
    if args.test:
        print("🧪 Running test suite...")
        cmd = "python -m pytest tests/ -v"
        if args.verbose:
            cmd += " -s"
        run_command(cmd, "Running tests")
        return
    
    if args.lint:
        print("📝 Running code linting...")
        cmd = "python -m flake8 core/ ai/ actions/ phases/ scripts/ --max-line-length=100"
        run_command(cmd, "Linting code")
        return
    
    if args.format:
        print("🖤 Formatting code...")
        cmd = "python -m black core/ ai/ actions/ phases/ scripts/"
        run_command(cmd, "Formatting code")
        return
    
    if args.clean:
        print("🧹 Cleaning up temporary files...")
        # Clean Python cache
        run_command("find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true", "Removing __pycache__ directories")
        run_command("find . -name '*.pyc' -delete", "Removing .pyc files")
        # Clean test cache
        run_command("rm -rf .pytest_cache/", "Removing pytest cache")
        # Clean coverage reports
        run_command("rm -rf htmlcov/ .coverage", "Removing coverage reports")
        print("   ✅ Cleanup completed")
        return
    
    # Build main command
    cmd_parts = ["python main.py"]
    
    # Add configuration
    config_path = get_config_path(args.config)
    if config_path.exists():
        cmd_parts.append(f"--config {config_path}")
    elif args.config != "default":
        print(f"⚠️  Configuration file {config_path} not found, using default")
    
    # Add AI provider
    if args.provider:
        cmd_parts.append(f"--provider {args.provider}")
    
    # Add starting phase
    if args.phase:
        cmd_parts.append(f"--phase {args.phase}")
    
    # Add debug mode
    if args.debug:
        cmd_parts.append("--debug")
    
    # Add simulation mode
    if args.simulation:
        cmd_parts.append("--simulation")
    
    # Add log level
    if args.log_level != "INFO":
        # This would need to be handled in main.py config override
        print(f"⚠️  Log level override not implemented in main.py yet")
    
    # Build final command
    cmd = " ".join(cmd_parts)
    
    # Show what will be run
    print("🎮 Minecraft AI Automation Runner")
    print("=" * 50)
    print(f"Command: {cmd}")
    print("=" * 50)
    
    # Confirmation prompt (unless skipped)
    if not args.no_prompt:
        response = input("Continue? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Cancelled.")
            return
    
    # Run the automation
    print("\n🚀 Starting automation...")
    print("Press Ctrl+C to stop\n")
    
    try:
        subprocess.run(cmd, shell=True, check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Automation stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Automation failed with exit code {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()