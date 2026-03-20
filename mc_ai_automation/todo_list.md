# Todo List: Implement Stable Pointer Chains

## Overview
Implement dynamic base address discovery mechanism to turn unstable direct addresses into stable pointer chains that survive Minecraft restarts.

## Tasks

### 1. Analyze Current Structure
- [ ] Review existing memory_reader.py implementation
- [ ] Examine current offsets.json structure
- [ ] Understand existing pointer chain functionality

### 2. Add Module Resolution to memory_reader.py
- [ ] Implement `_resolve_module_base()` method
- [ ] Modify `_get_pointer_chain()` to handle module names
- [ ] Test module base resolution functionality

### 3. Update offsets.json with Candidate Chain
- [ ] Analyze dump analysis results for candidate base addresses
- [ ] Determine which module base addresses belong to
- [ ] Compute constant offsets from module base
- [ ] Update offsets.json with module-relative chains

### 4. Create Test Script
- [ ] Create test_pointer.py script
- [ ] Implement coordinate reading with new pointer chains
- [ ] Test functionality with current Minecraft session

### 5. Implement Fallback Scanner (Optional)
- [ ] Create helper script for automatic offset finding
- [ ] Implement scanmem integration for session-specific offsets
- [ ] Add automatic offsets.json update functionality

### 6. Testing and Verification
- [ ] Test pointer chains across Minecraft restarts
- [ ] Verify coordinates are read correctly
- [ ] Ensure stability and reliability

## Implementation Priority
1. **High Priority**: Module resolution and pointer chain modification
2. **Medium Priority**: Test script creation and validation
3. **Low Priority**: Fallback scanner implementation