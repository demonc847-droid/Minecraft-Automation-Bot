# 🏗️ Minecraft AI Automation - Project Structure

This document describes the organized structure of the Minecraft AI Automation project, designed to make it easier for agents to navigate, understand, and work with the codebase.

## 📁 Directory Structure

```
mc_ai_automation/
├── 📋 README.md                    # Main project documentation
├── 📋 PROJECT_STRUCTURE.md         # This file
├── 📋 requirements.txt            # Python dependencies
├── 📋 LICENSE                     # Project license
├── 📋 .gitignore                  # Git ignore rules
├── 📋 .env.example                # Environment variables template
│
├── 🎮 main.py                     # Main entry point and automation loop
│
├── 📁 core/                       # Core system components
│   ├── __init__.py
│   ├── memory_reader.py          # Process memory reading
│   ├── player_state.py           # Player state dataclass
│   ├── inventory_state.py        # Inventory management
│   ├── world_state.py            # World state tracking
│   └── input_simulator.py        # Keyboard/mouse simulation
│
├── 🤖 ai/                         # AI decision making
│   ├── __init__.py
│   ├── decision_maker.py         # Main AI interface
│   ├── prompts.py                # Prompt templates
│   └── fallback.py               # Fallback strategies
│
├── ⚔️ actions/                     # Action implementations
│   ├── __init__.py
│   ├── movement.py               # Movement actions
│   ├── combat.py                 # Combat actions
│   ├── gathering.py              # Resource gathering
│   └── inventory.py              # Inventory management
│
├── 🎯 phases/                     # Game phase scripts
│   ├── __init__.py
│   ├── phase1_foundation.py      # Wood, shelter, food
│   ├── phase2_resources.py       # Stone, coal, torches
│   ├── phase3_tools.py           # Iron tools and armor
│   ├── phase4_mining.py          # Diamonds and obsidian
│   ├── phase5_nether.py          # Nether portal and resources
│   ├── phase6_stronghold.py      # Eyes of Ender, stronghold
│   └── phase7_dragon.py          # End crystals, dragon fight
│
├── 🧪 tests/                      # Test suite
│   ├── __init__.py
│   ├── test_core.py              # Core module tests
│   ├── test_ai.py                # AI module tests
│   ├── test_actions.py           # Action module tests
│   └── test_integration.py       # Integration tests
│
├── 📚 docs/                       # Comprehensive documentation
│   ├── README.md                 # Documentation overview
│   ├── architecture/             # System architecture
│   │   ├── overview.md          # High-level design
│   │   ├── components.md        # Component details
│   │   ├── data_flow.md         # Data flow diagrams
│   │   └── memory_structure.md  # Memory implementation
│   ├── development/             # Development guides
│   │   ├── setup.md            # Environment setup
│   │   ├── coding_standards.md # Code standards
│   │   ├── testing.md          # Testing guidelines
│   │   ├── debugging.md        # Debugging techniques
│   │   └── agent*.md           # Agent-specific docs
│   ├── api/                    # API documentation
│   │   ├── core_api.md         # Core APIs
│   │   ├── ai_api.md           # AI APIs
│   │   ├── actions_api.md      # Action APIs
│   │   └── phases_api.md       # Phase APIs
│   └── guides/                 # User guides
│       ├── quick_start.md      # Quick start
│       ├── configuration.md    # Config reference
│       ├── troubleshooting.md  # Troubleshooting
│       └── faq.md             # Frequently asked questions
│
├── 🛠️ scripts/                    # Utility scripts
│   ├── setup_dev.py            # Development environment setup
│   ├── run_automation.py       # Automation runner script
│   └── utils/                  # Additional utilities
│
├── 📊 data/                      # Data files and configurations
│   ├── configs/                 # Configuration files
│   │   ├── config.yaml         # Main configuration
│   │   └── config.sample.yaml  # Sample configuration
│   ├── memory/                  # Memory analysis files
│   │   ├── offsets.json        # Memory offsets
│   │   ├── offsets_found.json  # Found offsets
│   │   ├── offsets_scan3.json  # Scan results
│   │   ├── x_addresses_current.json
│   │   ├── x_addresses_new.json
│   │   └── x_addresses_old.json
│   └── logs/                    # Log files
│       └── minecraft_ai.log    # Main log file
│
└── 🔧 utils/                     # Utility scripts and tools
    ├── analyze_memory_dump.py  # Memory dump analysis
    ├── analyze_offsets.py      # Offset analysis
    ├── cheat_engine_analyzer.py # Cheat Engine integration
    ├── convert_offsets.py      # Offset conversion
    ├── find_offsets.py         # Offset discovery
    ├── find_pointer_chain.py   # Pointer chain finding
    ├── find_stable_pointers.py # Stable pointer analysis
    ├── find_x_address.py       # Address finding
    ├── find_x_direct.py        # Direct address finding
    ├── find_x_double.py        # Double pointer finding
    ├── scan_pointer_chains.py  # Pointer chain scanning
    ├── targeted_pointer_finder.py # Targeted pointer finding
    ├── test_memory_addresses.py # Memory address testing
    └── test_pointer_chains.py  # Pointer chain testing
```

## 🎯 Quick Navigation Guide

### For New Developers
1. **Start Here**: `README.md` - Project overview
2. **Setup**: `scripts/setup_dev.py` - Development environment
3. **Architecture**: `docs/architecture/overview.md` - System design
4. **Quick Start**: `docs/guides/quick_start.md` - Get running quickly

### For AI/Decision Making Work
1. **AI Module**: `ai/` - All AI-related code
2. **Prompts**: `ai/prompts.py` - Prompt templates
3. **Decision Making**: `ai/decision_maker.py` - Main AI logic
4. **Documentation**: `docs/ai_api.md` - AI API documentation

### For Action/Execution Work
1. **Actions Module**: `actions/` - All action implementations
2. **Movement**: `actions/movement.py` - Movement logic
3. **Combat**: `actions/combat.py` - Combat logic
4. **Documentation**: `docs/actions_api.md` - Actions API documentation

### For Core/System Work
1. **Core Module**: `core/` - Core system components
2. **Memory Reading**: `core/memory_reader.py` - Memory access
3. **Input Simulation**: `core/input_simulator.py` - Input control
4. **Documentation**: `docs/core_api.md` - Core API documentation

### For Game Logic/Phases
1. **Phases Module**: `phases/` - Game phase implementations
2. **Phase 1**: `phases/phase1_foundation.py` - Foundation phase
3. **Phase 2**: `phases/phase2_resources.py` - Resources phase
4. **Documentation**: `docs/phases_api.md` - Phases API documentation

### For Testing
1. **Test Suite**: `tests/` - All tests
2. **Run Tests**: `python -m pytest tests/ -v` - Execute tests
3. **Test Runner**: `scripts/run_automation.py --test` - Test with script
4. **Testing Guide**: `docs/development/testing.md` - Testing documentation

### For Configuration
1. **Main Config**: `data/configs/config.yaml` - Main configuration
2. **Sample Config**: `data/configs/config.sample.yaml` - Configuration template
3. **Configuration Guide**: `docs/guides/configuration.md` - Config documentation

### For Memory Analysis
1. **Memory Utils**: `utils/` - Memory analysis tools
2. **Offsets**: `data/memory/offsets.json` - Memory offsets
3. **Analysis Tools**: `utils/analyze_*.py` - Analysis scripts

## 🔄 Development Workflow

### 1. Setup Development Environment
```bash
# Run the setup script
python scripts/setup_dev.py

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Automation
```bash
# Basic run
python main.py

# With custom config
python main.py --config data/configs/config.yaml

# In simulation mode
python main.py --simulation --debug

# Using the runner script
python scripts/run_automation.py --simulation --debug
```

### 3. Development Tasks
```bash
# Run tests
python scripts/run_automation.py --test

# Format code
python scripts/run_automation.py --format

# Lint code
python scripts/run_automation.py --lint

# Clean temporary files
python scripts/run_automation.py --clean
```

### 4. Memory Analysis
```bash
# Analyze memory dumps
python utils/analyze_memory_dump.py

# Find offsets
python utils/find_offsets.py

# Test memory addresses
python utils/test_memory_addresses.py
```

## 📋 File Naming Conventions

### Python Files
- **Modules**: `snake_case.py` (e.g., `memory_reader.py`)
- **Classes**: `PascalCase` within files
- **Functions**: `snake_case()` within files

### Documentation Files
- **Markdown**: `kebab-case.md` (e.g., `quick-start.md`)
- **Structure**: Organized by purpose in `docs/` directory

### Data Files
- **JSON**: `snake_case.json` (e.g., `offsets.json`)
- **YAML**: `snake_case.yaml` (e.g., `config.yaml`)
- **Logs**: `snake_case.log` (e.g., `minecraft_ai.log`)

### Scripts
- **Python**: `snake_case.py` (e.g., `setup_dev.py`)
- **Executable**: Made executable with `chmod +x`

## 🎯 Agent-Specific Directories

### Agent 1 (Core) - Memory Reading & Input
- **Focus**: `core/` directory
- **Key Files**: `memory_reader.py`, `input_simulator.py`
- **Documentation**: `docs/development/agent1_core.md`

### Agent 2 (AI) - Decision Making
- **Focus**: `ai/` directory
- **Key Files**: `decision_maker.py`, `prompts.py`
- **Documentation**: `docs/development/agent2_ai.md`

### Agent 3 (Actions) - Action Execution
- **Focus**: `actions/` directory
- **Key Files**: `movement.py`, `combat.py`, `gathering.py`
- **Documentation**: `docs/development/agent3_actions.md`

### Agent 4 (Integration) - Testing & Integration
- **Focus**: `tests/` and `phases/` directories
- **Key Files**: All test files, phase implementations
- **Documentation**: `docs/development/agent4_integration.md`

## 🔍 Finding Files Quickly

### By Function
- **Memory Reading**: `core/memory_reader.py`
- **AI Decisions**: `ai/decision_maker.py`
- **Movement**: `actions/movement.py`
- **Combat**: `actions/combat.py`
- **Phase Logic**: `phases/phase*.py`

### By Type
- **Tests**: `tests/test_*.py`
- **Documentation**: `docs/**/*.md`
- **Configuration**: `data/configs/*.yaml`
- **Memory Data**: `data/memory/*.json`
- **Utilities**: `utils/*.py`

### By Agent
- **Agent 1**: `core/` + `docs/development/agent1_core.md`
- **Agent 2**: `ai/` + `docs/development/agent2_ai.md`
- **Agent 3**: `actions/` + `docs/development/agent3_actions.md`
- **Agent 4**: `tests/` + `docs/development/agent4_integration.md`

## 📚 Documentation Map

### Architecture & Design
- **Overview**: `docs/architecture/overview.md`
- **Components**: `docs/architecture/components.md`
- **Data Flow**: `docs/architecture/data_flow.md`

### Development
- **Setup**: `docs/development/setup.md`
- **Standards**: `docs/development/coding_standards.md`
- **Testing**: `docs/development/testing.md`
- **Debugging**: `docs/development/debugging.md`

### APIs
- **Core**: `docs/api/core_api.md`
- **AI**: `docs/api/ai_api.md`
- **Actions**: `docs/api/actions_api.md`
- **Phases**: `docs/api/phases_api.md`

### User Guides
- **Quick Start**: `docs/guides/quick_start.md`
- **Configuration**: `docs/guides/configuration.md`
- **Troubleshooting**: `docs/guides/troubleshooting.md`
- **FAQ**: `docs/guides/faq.md`

---

This structure is designed to be intuitive, scalable, and agent-friendly. Each directory has a clear purpose, and files are organized logically to make navigation and development as efficient as possible.