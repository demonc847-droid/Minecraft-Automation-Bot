# 🎮 Minecraft AI Automation Bot

<div align="center">

![Minecraft Version](https://img.shields.io/badge/Minecraft-1.21.11-green?style=for-the-badge&logo=minecraft)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge)

**🤖 An intelligent AI-powered automation bot for Minecraft Java Edition 1.21.11**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🌟 Overview

Minecraft AI Automation Bot is a sophisticated AI system that can autonomously play Minecraft. It uses memory reading to understand the game state, AI decision-making to plan actions, and human-like input simulation to execute those actions.

The bot can:
- 🧭 Navigate the world intelligently
- ⚔️ Fight monsters and defend itself
- ⛏️ Mine resources and gather materials
- 🏠 Build structures and craft items
- 🐉 Complete the game by defeating the Ender Dragon

---

## ✨ Features

### 🧠 AI-Powered Decision Making
- **Multi-Provider Support**: Google Gemini, Groq, and Ollama
- **Context-Aware**: Understands game state, inventory, and threats
- **Phase-Based Progression**: 7 distinct game phases from foundation to dragon fight

### 🔍 Advanced Memory Reading
- **Real-Time State**: Reads player position, health, inventory, world data
- **Pointer Chain Support**: Robust memory access across game sessions
- **Fallback Mechanisms**: Multiple reading methods for reliability

### 🎯 Intelligent Actions
- **Smooth Movement**: Human-like mouse and keyboard control
- **Combat System**: Attack, defend, flee based on threat assessment
- **Resource Gathering**: Automated mining, tree chopping, farming
- **Inventory Management**: Smart item organization and crafting

### 📊 7 Game Phases
1. **🏗️ Foundation**: Basic survival, shelter, food
2. **🪵 Resources**: Wood, stone, coal gathering
3. **⚔️ Tools**: Iron equipment, weapons, armor
4. **⛏️ Mining**: Diamond hunting, advanced resources
5. **🔥 Nether**: Blaze rods, ender pearls
6. **🏰 Stronghold**: Locate and prepare for the End
7. **🐉 Dragon**: Defeat the Ender Dragon

---

## 🚀 Installation

### Prerequisites
- Linux (Ubuntu/Debian recommended)
- Python 3.12+
- Minecraft Java Edition 1.21.11
- AI API Key (Groq or Google Gemini)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/demonc847-droid/Minecraft-Automation-Bot.git
cd Minecraft-Automation-Bot/mc_ai_automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up memory access permissions (one-time)
sudo sysctl kernel.yama.ptrace_scope=0
echo 'kernel.yama.ptrace_scope=0' | sudo tee -a /etc/sysctl.d/99-minecraft.conf
sudo sysctl --system

# Configure your API key
nano config.yaml
```

### Configuration

Edit `config.yaml` to set your AI provider:

```yaml
ai:
  provider: groq  # Options: gemini, groq, ollama
  api_key: your_groq_api_key_here
```

---

## 🎮 Usage

### Start the Bot

```bash
cd mc_ai_automation
source venv/bin/activate
python3 main.py --provider groq
```

### Run Diagnostics

```bash
# Test memory reading
python3 test_memory_diag.py

# Check pointer chains
python3 test_pointer_chains.py

# Verify coordinate reading
python3 utils/auto_find_coords.py
```

### Expected Output

```
🎮 Minecraft AI Automation Bot
================================
✅ Memory Reader initialized
✅ AI Provider: Groq
✅ Input Simulator ready
✅ Attached to Minecraft (PID: 12345)

📊 Game State:
  Position: (125.5, 64.0, -89.3)
  Health: 20.0/20.0
  Hunger: 18/20
  Phase: 1 - Foundation

🤖 AI Decision: Collecting wood from nearby trees
```

---

## 🏗️ Architecture

```
mc_ai_automation/
├── 🧠 core/              # Memory reading & game state
│   ├── memory_reader.py  # Process memory access
│   ├── player_state.py   # Player position, health, etc.
│   ├── inventory_state.py# Inventory management
│   ├── world_state.py    # World time, entities
│   └── input_simulator.py# Mouse & keyboard control
│
├── 🤖 ai/                # AI decision making
│   ├── decision_maker.py # Multi-provider AI integration
│   ├── prompts.py        # Context-aware prompts
│   └── fallback.py       # Fallback strategies
│
├── 🎯 actions/           # Game actions
│   ├── movement.py       # Walking, sprinting, navigation
│   ├── combat.py         # Attacking, defending, fleeing
│   ├── gathering.py      # Mining, chopping, farming
│   └── inventory.py      # Crafting, organizing
│
├── 📈 phases/            # Game progression phases
│   ├── phase1_foundation.py
│   ├── phase2_resources.py
│   └── ... phase7_dragon.py
│
├── 🛠️ utils/             # Helper tools
│   ├── find_offsets.py   # Memory offset discovery
│   ├── analyze_*.py      # Analysis tools
│   └── test_*.py         # Diagnostic scripts
│
├── 📚 docs/              # Documentation
│   ├── architecture/     # System design docs
│   ├── development/      # Development guides
│   └── guides/           # User guides
│
└── ⚙️ config.yaml        # Configuration file
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [PROJECT_STATUS_REPORT.md](PROJECT_STATUS_REPORT.md) | Current project status and progress |
| [MEMORY_READING_FIX.md](mc_ai_automation/MEMORY_READING_FIX.md) | Memory reading implementation details |
| [INTERFACES.md](mc_ai_automation/docs/architecture/INTERFACES.md) | API and interface documentation |
| [STABLE_POINTER_ANALYSIS.md](mc_ai_automation/docs/architecture/STABLE_POINTER_ANALYSIS.md) | Memory pointer analysis |

---

## 🧪 Testing

```bash
cd mc_ai_automation
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_core.py -v

# Run diagnostics
python3 test_memory_diag.py
```

---

## 🔧 Troubleshooting

### Permission Issues
```bash
# Check ptrace permission
cat /proc/sys/kernel/yama/ptrace_scope

# Should return 0 for unrestricted access
# If not, run:
sudo sysctl kernel.yama.ptrace_scope=0
```

### Memory Reading Fails
```bash
# Test memory access
python3 test_memory_diag.py

# Check if Minecraft is running
pgrep -f "java.*minecraft"
```

### AI Provider Issues
```bash
# Test AI connection
python3 -c "from ai.decision_maker import DecisionMaker; dm = DecisionMaker(); print('AI OK')"
```

---

## 📊 Project Status

| Component | Status | Progress |
|-----------|--------|----------|
| Core Systems | ✅ Complete | 100% |
| AI Integration | ✅ Complete | 100% |
| Actions & Phases | ✅ Complete | 100% |
| Memory Reading | ✅ Working | 100% |
| Testing | ✅ Passing | 100% |
| Documentation | ✅ Complete | 100% |

**Overall Status: 🎉 Production Ready**

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Minecraft Community** - For reverse engineering resources
- **Google, Groq, Ollama** - For AI model access
- **Python Community** - For amazing libraries
- **Linux Community** - For memory access tools

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/demonc847-droid/Minecraft-Automation-Bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/demonc847-droid/Minecraft-Automation-Bot/discussions)

---

<div align="center">

**⭐ Star this repository if you find it useful! ⭐**

Made with ❤️ by [demonc847-droid](https://github.com/demonc847-droid)

</div>
