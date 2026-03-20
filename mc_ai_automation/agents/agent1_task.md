# Agent 1: Core Systems Engineer - TASK LIST

## Your Mission
Implement the core systems for Minecraft AI automation: memory reading, game state, and input simulation.

## Prerequisites
1. Read the Obsidian vault notes at `/media/cyber-demon/Projects/Minecraft_Automation_Vault/`
   - Focus on: [[09_Process_Attachment]], [[10_Reading_Memory]], [[11_Finding_Offsets]], [[12_Coordinate_Offsets]]
   - Focus on: [[19_Player_State]], [[20_Inventory_State]], [[21_World_State]], [[22_Polling_Loop]]
   - Focus on: [[16_Smooth_Mouse]], [[17_Keyboard_Control]], [[18_Anti_Pattern]]

2. You are on branch: `core-engineer`
3. Your working directory: `mc_ai_automation/`

## Tasks (In Order)

### Task 1: Create core/player_state.py
Create a class `PlayerState` that represents player data:
- position (x, y, z)
- velocity (x, y, z)  
- health, hunger, saturation
- experience level and progress
- yaw, pitch (rotation)
- status flags: is_on_ground, is_in_water, is_in_lava, is_sleeping
- dimension (overworld, nether, end)

### Task 2: Create core/inventory_state.py
Create a class `InventoryState` that represents inventory:
- selected_slot (0-8)
- items list (slot, item_id, count, damage, nbt)
- armor (head, chest, legs, feet)
- offhand item
- Methods: get_item(slot), set_item(slot, item), find_item(item_id)

### Task 3: Create core/world_state.py
Create a class `WorldState` that represents world data:
- time_of_day, day_count
- weather (is_raining, is_thundering)
- difficulty, game_mode
- seed, spawn_point
- looking_at (block_type, position, face)
- nearby_entities list
- nearby_blocks list

### Task 4: Create core/memory_reader.py
Create a class `MemoryReader` that:
- Attaches to Minecraft Java process
- Reads memory at configured offsets (from offsets.json)
- Returns GameState dictionary with player, inventory, world
- Has method: get_game_state() -> dict
- Loads offsets from offsets.json

### Task 5: Create core/input_simulator.py
Create a class `InputSimulator` with methods:
- move_to(x, z) - Move to coordinates
- look_at(yaw, pitch) - Rotate view
- look_at_position(x, y, z) - Look at 3D position
- jump() - Jump
- attack(hold_ticks) - Attack
- use_item(hold_ticks) - Use item
- place_block() - Place block
- break_block(hold_ticks) - Break block
- open_inventory() / close_inventory()
- select_slot(slot)
- drop_item(all=False)
- sneak(duration)

### Task 6: Update core/__init__.py
Ensure all classes are properly exported.

## Git Workflow
```bash
git checkout core-engineer
# Make your changes
git add .
git commit -m "feat(core): implement [component name]"
git push origin core-engineer
```

## Status: START NOW
Begin with Task 1 (player_state.py) and work through sequentially.