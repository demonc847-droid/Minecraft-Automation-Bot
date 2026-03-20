# Agent 4: Integration & Testing Engineer - TASK LIST

## Your Mission
Integrate all components, create tests, and ensure everything works together.

## Prerequisites
1. Read the Obsidian vault notes at `/media/cyber-demon/Projects/Minecraft_Automation_Vault/`
   - Focus on: [[34_Troubleshooting]], [[35_Useful_Commands]], [[36_Code_Snippets]], [[38_Cheat_Sheet]]
   - Read ALL notes to understand full system

2. You are on branch: `integration-test`
3. Your working directory: `mc_ai_automation/`

## Tasks (In Order)

### Task 1: Create config.yaml template
Create a configuration file template with:
- AI provider settings (gemini/groq/ollama)
- API key placeholders
- Tick rate settings
- Phase order configuration
- Logging settings

### Task 2: Create tests/test_core.py
Test the core module:
- Test MemoryReader initialization
- Test PlayerState dataclass
- Test InventoryState dataclass
- Test WorldState dataclass
- Test InputSimulator methods

### Task 3: Create tests/test_ai.py
Test the AI module:
- Test prompt formatting
- Test fallback strategies
- Test decision maker (mocked)
- Test provider switching

### Task 4: Create tests/test_actions.py
Test action modules:
- Test Movement class
- Test Combat class
- Test Gathering class
- Test Inventory class

### Task 5: Create tests/test_integration.py
Integration tests:
- Test full game loop (simulated)
- Test phase transitions
- Test AI to action pipeline

### Task 6: Update main.py
Enhance main.py with:
- Better error handling
- Configuration validation
- Logging improvements
- Graceful shutdown

### Task 7: Create README.md
Create project documentation:
- Project overview
- Installation instructions
- Usage guide
- Configuration reference
- Architecture diagram

## Git Workflow
```bash
git checkout integration-test
# Make your changes
git add .
git commit -m "feat(integration): implement [component name]"
git push origin integration-test
```

## Status: START NOW
Begin with Task 1 (config.yaml) and work through sequentially.