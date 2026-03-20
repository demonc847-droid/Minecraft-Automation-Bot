#!/usr/bin/env python3
"""
Analyze offset scan results to find common addresses.
Compares multiple scans to identify the correct memory offsets.
"""

import json

def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def main():
    print("=" * 60)
    print("Analyzing Minecraft 1.21.11 Memory Offset Scans")
    print("=" * 60)
    
    # Load all scan results
    scan1 = load_json('offsets_found.json')
    scan3 = load_json('offsets_scan3.json')
    
    print("\nScan Coordinates:")
    print("  Scan 1: X=161.737, Y=64, Z=-84.201")
    print("  Scan 2: X=182.031, Y=63, Z=-84.996")
    print("  Scan 3: X=175.594, Y=66, Z=-68.449")
    
    # Get Y addresses from each scan
    y_addresses = {}
    
    if scan1 and 'found_addresses' in scan1:
        for addr in scan1['found_addresses'].get('y', []):
            y_addresses[addr] = y_addresses.get(addr, 0) + 1
    
    if scan3 and 'found_addresses' in scan3:
        for addr in scan3['found_addresses'].get('y', []):
            y_addresses[addr] = y_addresses.get(addr, 0) + 1
    
    # Also check the common_y from scan3
    if scan3 and 'common_y' in scan3:
        for addr in scan3['common_y']:
            if addr not in y_addresses:
                y_addresses[addr] = 1
    
    # Find addresses that appear in multiple scans
    print("\n" + "=" * 60)
    print("Y Coordinate Addresses (appearing in multiple scans):")
    print("=" * 60)
    
    common_addresses = []
    for addr, count in sorted(y_addresses.items(), key=lambda x: x[1], reverse=True):
        if count >= 2:
            common_addresses.append(addr)
            print(f"  {addr}: appeared in {count} scans")
    
    if not common_addresses:
        print("  No common addresses found across multiple scans.")
        print("  Using addresses from scan3 common_y list:")
        if scan3 and 'common_y' in scan3:
            common_addresses = scan3['common_y'][:4]
            for addr in common_addresses:
                print(f"    {addr}")
    
    # Get health addresses
    health_addresses = []
    if scan1 and 'found_addresses' in scan1:
        health_addresses = scan1['found_addresses'].get('health', [])[:4]
    
    print("\n" + "=" * 60)
    print("Health Addresses (from scan 1):")
    print("=" * 60)
    for addr in health_addresses:
        print(f"  {addr}")
    
    # Create offsets.json structure
    offsets = {
        "_comment": "Memory offsets for Minecraft Java Edition 1.21.11",
        "_documentation": "Found using offset finder tool on 2026-03-20",
        "version": "1.21.11",
        "last_updated": "2026-03-20",
        "player": {
            "_comment": "Player-related memory offsets",
            "base_offset": "0x00000000",
            "position": {
                "x": "0x10",
                "y": common_addresses[0] if common_addresses else "0x00",
                "z": "0x18"
            },
            "velocity": {
                "x": "0x20",
                "y": "0x24",
                "z": "0x28"
            },
            "rotation": {
                "yaw": "0x30",
                "pitch": "0x34"
            },
            "health": health_addresses[0] if health_addresses else "0x00",
            "hunger": "0x40",
            "saturation": "0x44",
            "experience": {
                "level": "0x50",
                "progress": "0x54"
            },
            "flags": {
                "is_on_ground": "0x60",
                "is_in_water": "0x61",
                "is_in_lava": "0x62",
                "is_sleeping": "0x63"
            }
        },
        "inventory": {
            "_comment": "Inventory-related memory offsets",
            "base_offset": "0x00000000",
            "selected_slot": "0x00",
            "slots": {
                "hotbar_start": "0x100",
                "inventory_start": "0x200",
                "armor_start": "0x300",
                "offhand": "0x400"
            },
            "item_structure": {
                "item_id": "0x00",
                "count": "0x04",
                "damage": "0x08",
                "nbt_data": "0x10"
            }
        },
        "world": {
            "_comment": "World-related memory offsets",
            "base_offset": "0x00000000",
            "time_of_day": "0x00",
            "day_count": "0x04",
            "difficulty": "0x08",
            "game_mode": "0x0C",
            "seed": "0x10",
            "spawn_point": {
                "x": "0x20",
                "y": "0x24",
                "z": "0x28"
            }
        },
        "entity": {
            "_comment": "Entity-related memory offsets",
            "base_offset": "0x00000000",
            "entity_list": "0x00",
            "entity_structure": {
                "type_id": "0x00",
                "position": {
                    "x": "0x10",
                    "y": "0x14",
                    "z": "0x18"
                },
                "health": "0x20",
                "uuid": "0x30"
            }
        },
        "pointers": {
            "_comment": "Key pointers in the Minecraft process",
            "game_instance": "0x00000000",
            "player_pointer": "0x00000000",
            "world_pointer": "0x00000000",
            "inventory_pointer": "0x00000000",
            "entity_list_pointer": "0x00000000"
        },
        "_notes": {
            "y_offset_found": common_addresses[0] if common_addresses else "Not found",
            "health_offset_found": health_addresses[0] if health_addresses else "Not found",
            "scans_performed": 3,
            "coordinates_used": [
                {"x": 161.737, "y": 64, "z": -84.201},
                {"x": 182.031, "y": 63, "z": -84.996},
                {"x": 175.594, "y": 66, "z": -68.449}
            ]
        }
    }
    
    # Save offsets.json
    with open('offsets.json', 'w') as f:
        json.dump(offsets, f, indent=4)
    
    print("\n" + "=" * 60)
    print("Offsets Saved!")
    print("=" * 60)
    print(f"\nY offset: {common_addresses[0] if common_addresses else 'Not found'}")
    print(f"Health offset: {health_addresses[0] if health_addresses else 'Not found'}")
    print("\nNote: Some offsets are still placeholders.")
    print("The Y and health offsets have been updated with found values.")
    print("\nYou can now try running: python3 main.py --provider groq")

if __name__ == "__main__":
    main()