#!/usr/bin/env python3
"""
Test pointer chain reading using the MemoryReader class.
"""

import sys
sys.path.insert(0, '.')

from core.memory_reader import MemoryReader

def main():
    print("Testing pointer chain reading...")
    print("=" * 60)
    
    reader = MemoryReader(offsets_file="data/memory/offsets.json")
    
    if not reader.attach():
        print("Failed to attach to Minecraft")
        return
    
    print(f"Attached to Minecraft (PID: {reader.pid})")
    print(f"Base address: 0x{reader.base_address:x}")
    
    # Test reading player state using pointer chains
    print("\nReading player state using pointer chains...")
    print("-" * 60)
    
    player_state = reader.get_player_state()
    
    if player_state:
        print("✓ Successfully read player state!")
        print(f"\nPlayer Position:")
        print(f"  X: {player_state.position['x']:.3f}")
        print(f"  Y: {player_state.position['y']:.3f}")
        print(f"  Z: {player_state.position['z']:.3f}")
        print(f"\nPlayer Stats:")
        print(f"  Health: {player_state.health:.1f}")
        print(f"  Hunger: {player_state.hunger:.1f}")
        print(f"  Saturation: {player_state.saturation:.1f}")
        print(f"\nPlayer Rotation:")
        print(f"  Yaw: {player_state.yaw:.1f}")
        print(f"  Pitch: {player_state.pitch:.1f}")
        print(f"\nPlayer Flags:")
        print(f"  On Ground: {player_state.is_on_ground}")
        print(f"  In Water: {player_state.is_in_water}")
        print(f"  In Lava: {player_state.is_in_lava}")
        print(f"  Sleeping: {player_state.is_sleeping}")
    else:
        print("✗ Failed to read player state")
    
    # Test reading inventory
    print("\n" + "=" * 60)
    print("Reading inventory state...")
    print("-" * 60)
    
    inv_state = reader.get_inventory_state()
    
    if inv_state:
        print("✓ Successfully read inventory state!")
        print(f"\nSelected Slot: {inv_state.selected_slot}")
        print(f"Items in inventory: {len(inv_state.items)}")
        
        if inv_state.items:
            print("\nFirst 5 items:")
            for i, item in enumerate(inv_state.items[:5]):
                print(f"  Slot {item['slot']}: {item['item_id']} x{item['count']}")
    else:
        print("✗ Failed to read inventory state")
    
    # Test reading world state
    print("\n" + "=" * 60)
    print("Reading world state...")
    print("-" * 60)
    
    world_state = reader.get_world_state()
    
    if world_state:
        print("✓ Successfully read world state!")
        print(f"\nTime of Day: {world_state.time_of_day}")
        print(f"Difficulty: {world_state.difficulty}")
        print(f"Game Mode: {world_state.game_mode}")
        print(f"Spawn Point: ({world_state.spawn_point.x:.1f}, {world_state.spawn_point.y:.1f}, {world_state.spawn_point.z:.1f})")
    else:
        print("✗ Failed to read world state")
    
    print("\n" + "=" * 60)
    print("Test complete!")

if __name__ == '__main__':
    main()