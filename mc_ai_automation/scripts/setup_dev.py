#!/usr/bin/env python3
"""
Development Setup Script for Minecraft AI Automation

This script helps set up the development environment with proper
configuration, dependencies, and initial setup.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("   ❌ Python 3.8+ required")
        return False
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("   ❌ requirements.txt not found")
        return False
    
    # Try to install in virtual environment first
    venv_path = Path("venv")
    if venv_path.exists():
        print("   🏠 Virtual environment detected")
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix/Linux/macOS
            pip_path = venv_path / "bin" / "pip"
        
        if pip_path.exists():
            cmd = f"{pip_path} install -r requirements.txt"
        else:
            print("   ⚠️  Virtual environment pip not found, using system pip")
            cmd = "pip install -r requirements.txt"
    else:
        print("   ⚠️  No virtual environment found, using system pip")
        cmd = "pip install -r requirements.txt"
    
    return run_command(cmd, "Installing dependencies")


def create_sample_config():
    """Create a sample configuration file."""
    print("⚙️  Creating sample configuration...")
    
    config_dir = Path("data/configs")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    sample_config = config_dir / "config.sample.yaml"
    
    if sample_config.exists():
        print("   ⚠️  Sample config already exists")
        return True
    
    config_content = """# Sample Configuration for Minecraft AI Automation
# Copy this to config.yaml and customize as needed

# AI Provider Settings
ai_provider: "gemini"  # Options: gemini, groq, ollama

# API Keys (set these in environment variables)
api_key: "${GEMINI_API_KEY}"

# Ollama settings (only if using local Ollama)
ollama:
  host: "localhost"
  port: 11434
  model: "llama2"

# Game Settings
tick_rate: 20  # Ticks per second

# Logging Configuration
log_level: "INFO"
log_file: "data/logs/minecraft_ai.log"
log_to_console: true
log_to_file: true

# Phase Order Configuration
phase_order:
  - foundation
  - resources
  - tools
  - mining
  - nether
  - stronghold
  - dragon

# Safety Settings
safety:
  min_health_threshold: 6.0
  min_hunger_threshold: 4.0
  auto_eat_threshold: 10.0
  threat_distance_threshold: 5.0

# Movement Settings
movement:
  default_speed: "walk"
  human_like_movement: true
  movement_variance: 0.1

# Debug Settings
debug:
  enabled: false
  show_game_state: false
  simulation_mode: false
"""
    
    try:
        with open(sample_config, 'w') as f:
            f.write(config_content)
        print(f"   ✅ Created {sample_config}")
        return True
    except Exception as e:
        print(f"   ❌ Error creating config: {e}")
        return False


def setup_git_hooks():
    """Set up Git hooks for code quality."""
    print("🪝 Setting up Git hooks...")
    
    hooks_dir = Path(".git/hooks")
    if not hooks_dir.exists():
        print("   ⚠️  Git repository not found, skipping hooks")
        return True
    
    # Pre-commit hook for code formatting
    pre_commit_content = """#!/bin/bash
# Pre-commit hook for code quality

echo "🔍 Running pre-commit checks..."

# Check if black is installed and format code
if command -v black &> /dev/null; then
    echo "   🖤 Formatting code with black..."
    black --check --diff core/ ai/ actions/ phases/ scripts/ || {
        echo "   ❌ Code formatting required. Run 'black .' to fix."
        exit 1
    }
fi

# Check if flake8 is installed and lint code
if command -v flake8 &> /dev/null; then
    echo "   📝 Linting code with flake8..."
    flake8 core/ ai/ actions/ phases/ scripts/ || {
        echo "   ❌ Linting failed. Please fix the issues."
        exit 1
    }
fi

echo "   ✅ Pre-commit checks passed!"
"""
    
    pre_commit_file = hooks_dir / "pre-commit"
    try:
        with open(pre_commit_file, 'w') as f:
            f.write(pre_commit_content)
        os.chmod(pre_commit_file, 0o755)
        print("   ✅ Git hooks configured")
        return True
    except Exception as e:
        print(f"   ❌ Error setting up hooks: {e}")
        return False


def create_dev_environment():
    """Create development environment files."""
    print("🏗️  Creating development environment...")
    
    # Create .env file template
    env_content = """# Environment Variables for Minecraft AI Automation
# Copy this to .env and fill in your API keys

# Google Gemini API Key
# GEMINI_API_KEY=your-api-key-here

# Groq API Key (alternative)
# GROQ_API_KEY=your-api-key-here

# Debug mode
# DEBUG=true

# Simulation mode (no actual input)
# SIMULATION=true
"""
    
    env_file = Path(".env.example")
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"   ✅ Created {env_file}")
    except Exception as e:
        print(f"   ❌ Error creating .env.example: {e}")
    
    # Create .gitignore if it doesn't exist
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
data/logs/*.log

# Environment variables
.env
.env.local

# Temporary files
*.tmp
*.temp
*.bak

# OS
.DS_Store
Thumbs.db

# Memory dumps and analysis files
data/memory/*.json
!data/memory/offsets.json

# Test coverage
htmlcov/
.coverage
.pytest_cache/
"""
    
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        try:
            with open(gitignore_file, 'w') as f:
                f.write(gitignore_content)
            print(f"   ✅ Created {gitignore_file}")
        except Exception as e:
            print(f"   ❌ Error creating .gitignore: {e}")
    
    return True


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    
    if not Path("tests").exists():
        print("   ⚠️  No tests directory found")
        return True
    
    cmd = "python -m pytest tests/ -v"
    return run_command(cmd, "Running tests")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup development environment")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-git-hooks", action="store_true", help="Skip setting up Git hooks")
    
    args = parser.parse_args()
    
    print("🚀 Setting up Minecraft AI Automation Development Environment")
    print("=" * 60)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Create sample configuration
    if not create_sample_config():
        success = False
    
    # Set up Git hooks (optional)
    if not args.skip_git_hooks:
        if not setup_git_hooks():
            success = False
    
    # Create development environment files
    if not create_dev_environment():
        success = False
    
    # Run tests (optional)
    if not args.skip_tests:
        if not run_tests():
            success = False
    
    print("=" * 60)
    if success:
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Copy data/configs/config.sample.yaml to config.yaml")
        print("2. Set your API keys in environment variables")
        print("3. Run: python main.py --simulation --debug")
    else:
        print("❌ Setup completed with errors. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()