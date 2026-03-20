#!/usr/bin/env python3
# auto_find_coords.py

import struct
import subprocess
import json

def get_minecraft_pid():
    return int(subprocess.check_output(['pgrep', '-f', 'java.*minecraft']).decode().strip())

def find_coordinates():
    pid = get_minecraft_pid()
    y_addr = 0x100b667e8
    
    print(f"Reading memory around Y address {hex(y_addr)}...")
    
    with open(f'/proc/{pid}/mem', 'rb') as f:
        offsets = [-8, 0, 4]  # Try common offsets for X, Y, Z
        results = {}
        
        for offset in offsets:
            addr = y_addr + offset
            try:
                f.seek(addr)
                val = struct.unpack('<f', f.read(4))[0]
                results[offset] = val
                print(f"  Offset {offset:+3}: {hex(addr)} -> {val:.2f}")
            except:
                print(f"  Offset {offset:+3}: Failed")
        
        return results

if __name__ == "__main__":
    print("\nLooking for coordinates...")
    coords = find_coordinates()
    
    if coords.get(-8) and coords.get(4):
        print("\n✅ Found likely X and Z!")
        print(f"   X at Y-8: {hex(0x100b667e8 - 8)}")
        print(f"   Z at Y+4: {hex(0x100b667e8 + 4)}")
        print("\nUpdate offsets.json with these addresses.")
    else:
        print("\n⚠️  Could not find coordinates. Use Cheat Engine method.")