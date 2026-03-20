#!/usr/bin/env python3
"""
Test if memory_reader loads offsets correctly.
"""

import sys
sys.path.insert(0, '.')

from core.memory_reader import MemoryReader

def main():
    print("Testing MemoryReader initialization...")
    
    # Test with config path
    reader = MemoryReader(offsets_file="data/memory/offsets.json")
    
    print(f"Offsets loaded: {bool(reader.offsets)}")
    print(f"Player position config: {reader.offsets.get('player', {}).get('position', {})}")
    
    # Try to read coordinates
    if reader.attach():
        print("Attached to Minecraft successfully")
        state = reader.get_game_state()
        if state:
            print(f"Game state: {state}")
        else:
            print("Failed to get game state")
    else:
        print("Failed to attach to Minecraft")

if __name__ == '__main__':
    main()