# 🎮 Minecraft AI Automation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](#license)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)](#status)

> **An intelligent AI-powered automation system that plays Minecraft autonomously, from punching trees to defeating the Ender Dragon.**

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd mc_ai_automation
pip install -r requirements.txt

# Set your AI API key
export GEMINI_API_KEY="your-api-key"

# Run the automation
python main.py
```

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Game Phases](#game-phases)
- [Testing](#testing)
- [Safety Features](#safety-features)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [FAQ](#faq)

## 🎯 Overview

This project implements a sophisticated AI-driven automation system for Minecraft that:

- 🧠 **AI-Powered Decision Making**: Uses Gemini, Groq, or local Ollama models
- 🎮 **Human-Like Input**: Simulates natural keyboard and mouse movements
- 📊 **Memory Reading**: Extracts game state directly from Minecraft's process
- 🔄 **Phase Progression**: Automatically advances through 7 game phases
- 🛡️ **Safety First**: Emergency pauses, fallback strategies, threat detection
- 📝 **Comprehensive Logging**: Detailed logs for debugging and monitoring

## ✨ Features

### 🧠 AI-Powered Intelligence
- **Multiple AI Providers**: Support for Google Gemini, Groq, and local Ollama models
- **Context-Aware Prompts**: Dynamically generated prompts based on game state
- **Intelligent Fallbacks**: Safe default actions when AI is unavailable
- **Learning from Context**: AI considers phase objectives, inventory, and threats

### 🎮 Human-Like Gameplay
- **Bézier Mouse Curves**: Natural, curved mouse movements instead of instant snaps
- **Random Timing Variations**: Unpredictable delays between actions
- **Variable Movement Speed**: Walk, sprint, and sneak modes
- **Natural Look Patterns**: Realistic camera movements

### 📊 Real-Time Game State
- **Direct Memory Reading**: Extracts data from Minecraft's process memory
- **Player Tracking**: Position, health, hunger, experience, velocity
- **Inventory Monitoring**: All items, slots, armor, and offhand
- **World Awareness**: Time, weather, nearby entities, visible blocks

### 🔄 Automated Phase Progression
- **7 Complete Phases**: From wood punching to dragon defeat
- **Smart Phase Transitions**: Automatic advancement when objectives complete
- **Phase-Specific Strategies**: Different tactics for each game stage
- **Resume Capability**: Start from any phase

### 🛡️ Safety & Reliability
- **Emergency Pause**: Automatic pause on critical health/hunger
- **Threat Detection**: Responds to hostile mobs within range
- **Graceful Shutdown**: Clean exit on Ctrl+C or SIGTERM
- **Error Recovery**: Continues after non-fatal errors
- **Simulation Mode**: Test without actual input

### 📝 Comprehensive Logging
- **Dual Output**: Console and file logging simultaneously
- **Configurable Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Session Statistics**: Running time, ticks, actions, errors
- **State Snapshots**: Optional periodic game state saves

## 🏗️ Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌────────────────────────────────────────────────────────────────────┐
│                      MinecraftAutomation                           │
│                          (main.py)                                 │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    Main Game Loop                            │  │
│  │  1. Read Game State → 2. AI Decision → 3. Execute Action    │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────┬───────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│      Core       │ │       AI        │ │     Actions     │
│     Module      │ │     Module      │ │     Module      │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ • MemoryReader  │ │ • DecisionMaker │ │ • Movement      │
│ • PlayerState   │ │ • Prompts       │ │ • Combat        │
│ • InventoryState│ │ • Fallback      │ │ • Gathering     │
│ • WorldState    │ │                 │ │ • Inventory     │
│ • InputSimulator│ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │      Phases         │
              │      Module         │
              ├─────────────────────┤
              │ • Phase 1: Foundation│
              │ • Phase 2: Resources │
              │ • Phase 3: Tools     │
              │ • Phase 4: Mining    │
              │ • Phase 5: Nether    │
              │ • Phase 6: Stronghold│
              │ • Phase 7: Dragon    │
              └─────────────────────┘
```

### Data Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Minecraft  │───▶│    Memory    │───▶│  Game State  │───▶│      AI      │
│    Process   │    │    Reader    │    │   (dict)     │    │   Provider   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                                   │
                                                                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Complete   │◀───│    Input     │◀───│    Action    │◀───│   AI         │
│    Loop      │    │   Simulator  │    │   Router     │    │  Response    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

## 🎮 Game Phases

The automation progresses through 7 phases:

| Phase | Name | Description |
|-------|------|-------------|
| 1 | Foundation | Collect wood, craft wooden tools, build shelter, find food |
| 2 | Resources | Mine stone, craft stone tools, find coal, make torches |
| 3 | Tools | Mine iron, smelt ingots, craft iron tools and armor |
| 4 | Mining | Mine diamonds at Y=-59, collect obsidian |
| 5 | Nether | Build portal, find fortress, get blaze rods and ender pearls |
| 6 | Stronghold | Craft Eyes of Ender, locate stronghold, activate End portal |
| 7 | Dragon | Destroy End crystals, defeat Ender Dragon |

## 📦 Installation

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.8+ | Python 3.10+ recommended |
| Minecraft | Java Edition | 1.16+ recommended |
| OS | Windows/Linux/macOS | Admin/root may be required for input simulation |
| AI Provider | API Key or Local | Gemini, Groq, or Ollama |

### Step-by-Step Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd mc_ai_automation
```

#### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `pynput` - Keyboard and mouse simulation
- `pymem` - Process memory reading
- `pyyaml` - Configuration file parsing
- `requests` - API communication
- `pytest` - Testing framework

#### 4. Configure AI Provider

Choose one of the following options:

**Option A: Google Gemini (Recommended)**
1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set environment variable:
   ```bash
   # Linux/macOS
   export GEMINI_API_KEY="your-api-key-here"
   
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your-api-key-here"
   
   # Windows (CMD)
   set GEMINI_API_KEY=your-api-key-here
   ```
3. Or add to `~/.bashrc` / `~/.zshrc` for persistence

**Option B: Groq**
1. Get API key from [Groq Console](https://console.groq.com/)
2. Set environment variable:
   ```bash
   export GROQ_API_KEY="your-api-key-here"
   ```

**Option C: Ollama (Local, No API Key Needed)**
1. Install Ollama from https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama2
   # Or try other models:
   ollama pull mistral
   ollama pull codellama
   ```
3. Verify Ollama is running:
   ```bash
   ollama list
   ```

#### 5. Configure the System

Edit `config.yaml` to match your setup:

```yaml
# Choose your AI provider
ai_provider: "gemini"  # Options: gemini, groq, ollama

# API key reference (uses environment variable)
api_key: "${GEMINI_API_KEY}"

# Ollama settings (only if using Ollama)
ollama:
  host: "localhost"
  port: 11434
  model: "llama2"
```

#### 6. Start Minecraft

1. Launch Minecraft Java Edition
2. Create or load a single-player world
3. Ensure the game is running at 20 TPS (default)
4. **Important**: Keep Minecraft as the focused window

#### 7. Run the Automation

```bash
python main.py
```

### Verification

To verify everything is working:

```bash
# Run in simulation mode first
python main.py --simulation --debug

# Run tests
pytest tests/ -v
```

## Usage

### Basic Usage

Run with default settings:
```bash
python main.py
```

### Command-Line Options

```bash
python main.py [OPTIONS]

Options:
  --config PATH       Path to configuration file (default: config.yaml)
  --provider NAME     AI provider to use: gemini, groq, ollama
  --phase NAME        Starting phase: foundation, resources, tools, mining, nether, stronghold, dragon
  --debug             Enable debug logging
  --simulation        Run in simulation mode (no actual input)
```

### Examples

```bash
# Run with Groq AI provider
python main.py --provider groq

# Start from the mining phase
python main.py --phase mining

# Use custom config file
python main.py --config my_config.yaml

# Enable debug mode
python main.py --debug

# Run in simulation mode (for testing)
python main.py --simulation
```

## Configuration

The `config.yaml` file contains all configuration options:

### AI Provider Settings
```yaml
ai_provider: "gemini"  # gemini, groq, or ollama
api_key: "${GEMINI_API_KEY}"
```

### Game Settings
```yaml
tick_rate: 20  # Ticks per second
phase_order:
  - foundation
  - resources
  - tools
  - mining
  - nether
  - stronghold
  - dragon
```

### Safety Settings
```yaml
safety:
  min_health_threshold: 6.0
  min_hunger_threshold: 4.0
  auto_eat_threshold: 10.0
  threat_distance_threshold: 5.0
```

### Movement Settings
```yaml
movement:
  default_speed: "walk"
  human_like_movement: true
  movement_variance: 0.1
```

See `config.yaml` for all available options.

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_core.py -v
pytest tests/test_ai.py -v
pytest tests/test_actions.py -v
pytest tests/test_integration.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Project Structure

```
mc_ai_automation/
├── main.py                 # Main entry point
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── offsets.json          # Memory offsets for Minecraft
├── README.md             # This file
│
├── core/                 # Core systems
│   ├── __init__.py
│   ├── memory_reader.py  # Process memory reading
│   ├── player_state.py   # Player state dataclass
│   ├── inventory_state.py# Inventory management
│   ├── world_state.py    # World state tracking
│   └── input_simulator.py# Keyboard/mouse simulation
│
├── ai/                   # AI decision making
│   ├── __init__.py
│   ├── decision_maker.py # Main AI interface
│   ├── prompts.py        # Prompt templates
│   └── fallback.py       # Fallback strategies
│
├── actions/              # Action implementations
│   ├── __init__.py
│   ├── movement.py       # Movement actions
│   ├── combat.py         # Combat actions
│   ├── gathering.py      # Resource gathering
│   └── inventory.py      # Inventory management
│
├── phases/               # Game phase scripts
│   ├── __init__.py
│   ├── phase1_foundation.py
│   ├── phase2_resources.py
│   ├── phase3_tools.py
│   ├── phase4_mining.py
│   ├── phase5_nether.py
│   ├── phase6_stronghold.py
│   └── phase7_dragon.py
│
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_core.py      # Core module tests
│   ├── test_ai.py        # AI module tests
│   ├── test_actions.py   # Action module tests
│   └── test_integration.py # Integration tests
│
└── agents/               # Agent documentation
    ├── agent1_core.md
    ├── agent2_ai.md
    ├── agent3_actions.md
    ├── agent4_integration.md
    └── *_task.md files
```

## How It Works

### 1. Game State Reading
The system reads Minecraft's process memory to extract:
- Player position, health, hunger, experience
- Inventory contents
- World time, weather, nearby entities
- What the player is looking at

### 2. AI Decision Making
The game state is sent to an AI provider (Gemini/Groq/Ollama) with carefully crafted prompts that include:
- Current game state
- Current phase objectives
- Recent action history
- Safety considerations

The AI returns an action decision with reasoning.

### 3. Action Execution
Actions are executed through simulated keyboard and mouse input:
- Human-like movement patterns (Bézier curves for mouse)
- Random delays to avoid detection
- Natural timing variations

### 4. Phase Progression
The system tracks progress through each phase and advances when objectives are met.

## Safety Features

- **Emergency Pause**: Automatically pauses when health is critically low
- **Fallback Strategies**: Uses safe fallback actions when AI fails
- **Threat Detection**: Automatically responds to hostile entities
- **Graceful Shutdown**: Handles Ctrl+C and SIGTERM signals
- **Error Recovery**: Continues operation after non-fatal errors

## Logging

Logs are written to both console and `minecraft_ai.log`:

```
2026-03-20 08:15:02 - MinecraftAI - INFO - MinecraftAutomation initialized
2026-03-20 08:15:02 - MinecraftAI - INFO - Configuration validated successfully
2026-03-20 08:15:03 - MinecraftAI - INFO - Initializing components...
2026-03-20 08:15:03 - MinecraftAI - INFO - MemoryReader initialized
2026-03-20 08:15:03 - MinecraftAI - INFO - InputSimulator initialized
```

## Troubleshooting

### Minecraft Process Not Found
- Ensure Minecraft is running before starting the automation
- Check that the process name in `config.yaml` matches your Minecraft installation

### AI Provider Errors
- Verify your API key is set correctly
- Check your internet connection
- Try a different AI provider

### Input Not Working
- Ensure Minecraft is the focused window
- Check that no other applications are capturing input
- Run with administrator/root privileges if needed

### High CPU Usage
- Reduce `tick_rate` in config.yaml
- Enable `throttle_on_high_cpu` in performance settings

## Contributing

This project is organized into 4 agents:

1. **Agent 1 (Core)**: Memory reading, game state, input simulation
2. **Agent 2 (AI)**: Decision making, prompts, fallback strategies
3. **Agent 3 (Actions)**: Movement, combat, gathering, inventory
4. **Agent 4 (Integration)**: Main loop, testing, configuration

Each agent works on separate branches and coordinates via pull requests.

## License

This project is for educational purposes. Use responsibly and in accordance with Minecraft's terms of service.

## Disclaimer

This automation system is designed for single-player use. Using automation in multiplayer servers may violate server rules and result in bans. Always respect server policies and other players.

## ❓ FAQ

### General Questions

**Q: Is this safe to use?**
A: The system includes multiple safety features including emergency pauses, threat detection, and graceful error handling. However, use at your own risk and only in single-player worlds.

**Q: Will this work on multiplayer servers?**
A: No. This is designed for single-player use only. Using automation on multiplayer servers typically violates server rules and may result in bans.

**Q: Which AI provider should I use?**
A: **Gemini** is recommended for best performance. **Groq** offers fast inference. **Ollama** is great for offline/private use but requires more local resources.

**Q: Can I run this on a Raspberry Pi?**
A: Yes, with Ollama and a smaller model. Performance will vary based on your Pi's specs.

### Technical Questions

**Q: Why is Minecraft not being detected?**
A: Ensure Minecraft is running before starting the automation. The system looks for the Java process. Check `config.yaml` for the correct process name.

**Q: The automation is moving the mouse too fast/slow**
A: Adjust `movement.movement_variance` and `movement.human_like_movement` in `config.yaml`. Enable human-like movement for more natural behavior.

**Q: How do I change the tick rate?**
A: Edit `tick_rate` in `config.yaml`. Default is 20 (Minecraft's native rate). Lower values reduce CPU usage but slow down automation.

**Q: Can I pause the automation?**
A: Yes! Press `Ctrl+C` to gracefully shutdown. The system also auto-pauses on critical health or when threats are detected.

**Q: Where are the logs stored?**
A: Logs are written to `minecraft_ai.log` in the project directory and also displayed in the console.

**Q: How do I start from a specific phase?**
A: Use `python main.py --phase <phase_name>` where phase_name is one of: foundation, resources, tools, mining, nether, stronghold, dragon.

### AI & Decision Making

**Q: What happens if the AI provider is down?**
A: The system automatically falls back to safe default actions. You can also use `--simulation` mode to test without AI.

**Q: Can I customize the AI prompts?**
A: Yes. Edit `ai/prompts.py` to customize how the AI makes decisions. The prompts include phase objectives and safety considerations.

**Q: How does the AI know what to do?**
A: The AI receives a comprehensive game state including position, health, inventory, nearby entities, current phase objectives, and recent actions. It returns an action with reasoning.

### Performance & Optimization

**Q: The automation uses too much CPU**
A: 
1. Reduce `tick_rate` in config.yaml
2. Enable `performance.throttle_on_high_cpu`
3. Lower `performance.max_cpu_usage`

**Q: Can I run multiple instances?**
A: Not recommended. Each instance needs a focused Minecraft window and would compete for input control.

**Q: How much RAM does this need?**
A: Typically under 200MB. Ollama models require additional RAM depending on model size.

## 🤝 Contributing

We welcome contributions! This project is organized into 4 specialized agents:

### Agent Responsibilities

| Agent | Focus | Responsibilities |
|-------|-------|------------------|
| Agent 1 | Core | Memory reading, game state, input simulation |
| Agent 2 | AI | Decision making, prompts, fallback strategies |
| Agent 3 | Actions | Movement, combat, gathering, inventory |
| Agent 4 | Integration | Main loop, testing, configuration, documentation |

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes
4. **Test** thoroughly: `pytest tests/ -v`
5. **Commit** with descriptive messages: `git commit -m "feat: add amazing feature"`
6. **Push** to your branch: `git push origin feature/amazing-feature`
7. **Create** a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for all public methods
- Include unit tests for new features
- Update documentation as needed

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_core.py -v
```

## 📜 License

This project is for **educational purposes only**. 

- ✅ Allowed: Learning, research, personal single-player use
- ❌ Not Allowed: Multiplayer automation, commercial use, rule violations

Use responsibly and in accordance with Minecraft's terms of service.

## ⚠️ Disclaimer

This automation system is designed for **single-player use only**. 

- Using automation in multiplayer servers may violate server rules
- Always respect server policies and other players
- The developers are not responsible for any consequences of misuse
- Use at your own risk

## 🙏 Acknowledgments

- **Minecraft memory offsets community** - For reverse engineering documentation
- **Google, Groq, Ollama** - For AI model access
- **pynput developers** - For input simulation library
- **pytest team** - For the excellent testing framework
- **All contributors** - For making this project better

## 📞 Support

- 📖 **Documentation**: Read this README thoroughly
- 🐛 **Bug Reports**: Open an issue with reproduction steps
- 💡 **Feature Requests**: Open an issue describing your idea
- 💬 **Questions**: Check the FAQ above first

---

<div align="center">

**Status**: 🚧 In Development

**Current Phase**: Integration & Testing (Agent 4)

**Last Updated**: 2026-03-20

**Made with ❤️ for the Minecraft community**

</div>
