# Agent 3: Actions & Phases Engineer - TASK LIST

## Your Mission
Implement action modules and phase scripts for Minecraft automation.

## Prerequisites
1. Read the Obsidian vault notes at `/media/cyber-demon/Projects/Minecraft_Automation_Vault/`
   - Focus on: [[26_Phase4_Movement]], [[27_Phase5_Resource]], [[28_Phase6_Mining]]
   - Focus on: [[29_Phase7_Strategy]], [[30_Phase8_Combat]], [[31_Phase9_Stronghold]], [[32_Phase10_Dragon]]

2. You are on branch: `actions-phases`
3. Your working directory: `mc_ai_automation/`

## Tasks (In Order)

### Task 1: Create actions/movement.py
Create a class `Movement` with methods:
- walk_to(x, z, speed="walk")
- sprint_to(x, z)
- navigate_path(waypoints)
- turn_to_yaw(yaw)
- Use pynput for keyboard/mouse control

### Task 2: Create actions/combat.py
Create a class `Combat` with methods:
- attack_entity(entity_type)
- defend() - Block with shield
- flee_from(danger_position)
- attack_nearest_hostile()

### Task 3: Create actions/gathering.py
Create a class `Gathering` with methods:
- mine_block(block_type)
- collect_drops()
- chop_tree(base_position)

### Task 4: Create actions/inventory.py
Create a class `Inventory` with methods:
- craft_item(item_id, count)
- equip_item(item_id)
- organize_inventory()
- has_item(item_id)

### Task 5: Create phase scripts
Create phases/phase1_foundation.py through phases/phase7_dragon.py
Each phase should:
- Inherit from base Phase class
- Implement is_complete() method
- Implement get_objectives() method
- Use AI to decide actions

### Task 6: Update phases/__init__.py
Ensure all phases are properly exported.

## Git Workflow
```bash
git checkout actions-phases
# Make your changes
git add .
git commit -m "feat(actions): implement [component name]"
git push origin actions-phases
```

## Status: START NOW
Begin with Task 1 (movement.py) and work through sequentially.