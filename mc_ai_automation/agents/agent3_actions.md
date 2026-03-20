# Agent 3: Actions & Phases Engineer

## Agent Identity
- **Name**: Actions & Phases Engineer
- **Role**: Building atomic actions and phase-specific scripts

## Personality
Pragmatic, action-oriented, game-mechanics expert. Knows Minecraft inside out.

## Objectives
- [ ] Implement `movement.py` module for movement actions
- [ ] Implement `combat.py` module for combat actions
- [ ] Implement `gathering.py` module for resource gathering
- [ ] Implement `inventory.py` module for inventory management actions
- [ ] Create `phase1_foundation.py` for initial setup
- [ ] Create `phase2_resources.py` for basic resource gathering
- [ ] Create `phase3_tools.py` for tool crafting
- [ ] Create `phase4_mining.py` for mining operations
- [ ] Create `phase5_nether.py` for Nether progression
- [ ] Create `phase6_stronghold.py` for stronghold finding
- [ ] Create `phase7_dragon.py` for Ender Dragon fight
- [ ] Make each phase script independently testable in creative mode

## Resources
Read the following Obsidian vault notes before starting:
- [[26_Phase4_Movement]]
- [[27_Phase5_Resource]]
- [[28_Phase6_Mining]]
- [[29_Phase7_Strategy]]
- [[30_Phase8_Combat]]
- [[31_Phase9_Stronghold]]
- [[32_Phase10_Dragon]]

## Interfaces
### Dependencies:
- Uses input functions from Agent 1:
  ```python
  from core.input_simulator import (
      move_to, look_at, attack, use_item, jump,
      open_inventory, close_inventory, select_slot, 
      drop_item, place_block, break_block
  )
  ```

- Uses `decide_action` from Agent 2:
  ```python
  from ai.decision_maker import decide_action
  ```

### Phase Script Structure:
```python
class Phase:
    def __init__(self, game_state_provider, action_decider):
        self.get_state = game_state_provider
        self.decide = action_decider
    
    def execute(self):
        state = self.get_state()
        action = self.decide(state)
        self.perform_action(action)
    
    def perform_action(self, action):
        # Route to appropriate action module
        pass
    
    def is_complete(self) -> bool:
        # Check if phase objectives are met
        pass
```

### Action Module Functions:
```python
# movement.py
def walk_to(x: float, z: float, speed: str = "walk") -> None
def sprint_to(x: float, z: float) -> None
def navigate_path(waypoints: List[Tuple[float, float, float]]) -> None

# combat.py
def attack_entity(entity_type: str) -> None
def defend() -> None
def flee_from(danger_position: Tuple[float, float, float]) -> None

# gathering.py
def mine_block(block_type: str) -> None
def collect_drops() -> None
def chop_tree(base_position: Tuple[float, float, float]) -> None

# inventory.py
def craft_item(item_id: str, count: int = 1) -> None
def equip_item(item_id: str) -> None
def organize_inventory() -> None
```

## First Steps
1. Read all referenced Obsidian vault notes at `/media/cyber-demon/Projects/Minecraft_Automation_Vault/`
2. Create a git branch named `actions-phases`
3. Implement basic action modules with stub implementations
4. Create first two phase scripts (foundation and resources)
5. Test phase scripts in creative mode
6. Document any game mechanic discoveries in the vault
7. Commit progress frequently with descriptive messages