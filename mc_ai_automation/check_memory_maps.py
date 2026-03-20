#!/usr/bin/env python3
"""
Check memory maps to see if the addresses are in readable regions.
"""

import sys
sys.path.insert(0, '.')

from core.memory_reader import MemoryReader

def main():
    reader = MemoryReader(offsets_file="data/memory/offsets.json")
    
    if not reader.attach():
        print("Failed to attach to Minecraft")
        return
    
    print(f"Attached to Minecraft (PID: {reader.pid})")
    print(f"Base address: 0x{reader.base_address:x}")
    
    # Test addresses
    test_addresses = {
        "X": 0x76a722f30c54,
        "Y": 0x100b6f580,
        "Z": 0x76a722f30c5c,
    }
    
    print("\nChecking memory maps...")
    print("=" * 80)
    
    try:
        maps_file = f"/proc/{reader.pid}/maps"
        with open(maps_file, 'r') as f:
            maps = f.readlines()
        
        print(f"Total memory regions: {len(maps)}")
        print("\nLooking for readable regions containing our addresses...")
        print("-" * 80)
        
        for name, addr in test_addresses.items():
            print(f"\n{name} address: 0x{addr:x}")
            found = False
            
            for line in maps:
                parts = line.strip().split()
                if len(parts) >= 2:
                    addr_range = parts[0]
                    perms = parts[1]
                    
                    start_str, end_str = addr_range.split('-')
                    start = int(start_str, 16)
                    end = int(end_str, 16)
                    
                    if start <= addr < end:
                        print(f"  Found in region: {addr_range} ({perms})")
                        if 'r' in perms:
                            print(f"    ✓ Region is readable")
                        else:
                            print(f"    ✗ Region is NOT readable")
                        found = True
                        break
            
            if not found:
                print(f"  ✗ Address not found in any memory region!")
        
        print("\n" + "=" * 80)
        print("\nAll readable memory regions:")
        print("-" * 80)
        
        for line in maps:
            parts = line.strip().split()
            if len(parts) >= 2:
                addr_range = parts[0]
                perms = parts[1]
                
                if 'r' in perms:  # Readable
                    print(f"{addr_range} ({perms})")
        
    except Exception as e:
        print(f"Error reading memory maps: {e}")

if __name__ == '__main__':
    main()