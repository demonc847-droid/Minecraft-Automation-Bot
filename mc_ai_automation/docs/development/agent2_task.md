# Agent 2: AI Integration Engineer - TASK LIST

## Your Mission
Implement AI decision-making: connect to AI providers, create prompts, and build decision loops.

## Prerequisites
1. Read the Obsidian vault notes at `/media/cyber-demon/Projects/Minecraft_Automation_Vault/`
   - Focus on: [[42_AI_Setup_Gemini]], [[43_AI_Setup_Groq]], [[44_AI_Setup_Ollama]]
   - Focus on: [[45_Prompt_Engineering]], [[46_AI_Decision_Loop]], [[48_Fallback_Logic]]

2. You are on branch: `ai-integration`
3. Your working directory: `mc_ai_automation/`

## Tasks (In Order)

### Task 1: Create ai/prompts.py
Create a class `Prompts` with prompt templates:
- SYSTEM_PROMPT - Base system prompt for Minecraft AI
- ACTION_DECISION_PROMPT - Template for deciding actions
- PHASE_PROMPTS - Prompts for each phase
- EMERGENCY_PROMPT - For critical situations (low health, etc.)
- Method: format_prompt(template, **kwargs)

### Task 2: Create ai/fallback.py
Create a class `FallbackStrategy` with:
- Strategies: "safe", "explore", "random"
- safe: defend, retreat, eat food
- explore: move randomly, look around
- random: pick random valid action
- Method: get_fallback_action(game_state, strategy="safe")

### Task 3: Create ai/decision_maker.py
Create the main AI integration:
- Class `DecisionMaker`:
  - __init__(provider, api_key)
  - decide_action(game_state) -> action dict
  - _call_gemini(prompt) -> response
  - _call_groq(prompt) -> response
  - _call_ollama(prompt) -> response
  - _parse_response(response) -> action dict
- Module functions:
  - configure_ai_provider(provider, api_key)
  - decide_action(game_state)
  - get_action_with_fallback(game_state, strategy)

### Task 4: Update ai/__init__.py
Ensure all functions and classes are properly exported.

## Git Workflow
```bash
git checkout ai-integration
# Make your changes
git add .
git commit -m "feat(ai): implement [component name]"
git push origin ai-integration
```

## Status: START NOW
Begin with Task 1 (prompts.py) and work through sequentially.