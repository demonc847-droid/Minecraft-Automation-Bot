#!/usr/bin/env python3
"""
Find X coordinate address using memory scanning.
Uses the same approach as find_offsets.py but specifically for X coordinate.
"""

import sys
import struct
import psutil
import json

def find_minecraft_process():
    """Find the Minecraft Java process."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'].lower() if proc.info['name'] else ''
            cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
            
            if 'java' in name and 'minecraft' in cmdline:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def read_memory(pid, address, size):
    """Read memory from process."""
    try:
        mem_file = f"/proc/{pid}/mem"
        with open(mem_file, 'rb') as f:
            f.seek(address)
            return f.read(size)
    except Exception as e:
        return None

def scan_for_float(pid, target_value, tolerance=0.01):
    """Scan memory for a float value."""
    print(f"Scanning for float value: {target_value}")
    
    # Read memory maps
    maps_file = f"/proc/{pid}/maps"
    try:
        with open(maps_file, 'r') as f:
            maps = f.readlines()
    except PermissionError:
        print("Permission denied! Run with sudo.")
        return []
    
    found_addresses = []
    value_bytes = struct.pack('<f', float(target_value))
    
    for line in maps:
        parts = line.split()
        if len(parts) < 5:
            continue
        
        perms = parts[1]
        if 'r' not in perms:
            continue
        
        addr_range = parts[0].split('-')
        start_addr = int(addr_range[0], 16)
        end_addr = int(addr_range[1], 16)
        size = end_addr - start_addr
        
        # Skip very large regions
        if size > 100 * 1024 * 1024:
            continue
        
        try:
            memory = read_memory(pid, start_addr, size)
            if memory:
                # Search for value
                offset = 0
                while True:
                    idx = memory.find(value_bytes, offset)
                    if idx == -1:
                        break
                    found_addresses.append(start_addr + idx)
                    offset = idx + 1
        except Exception:
            continue
    
    return found_addresses

def main():
    print("=" * 60)
    print("Finding X Coordinate Address")
    print("=" * 60)
    
    # Find Minecraft process
    process = find_minecraft_process()
    if not process:
        print("Minecraft process not found!")
        return 1
    
    pid = process.pid
    print(f"Found Minecraft! PID: {pid}")
    
    # Current X coordinate
    x_coord = 175.265
    print(f"Searching for X coordinate: {x_coord}")
    
    # Scan for X coordinate
    x_addresses = scan_for_float(pid, x_coord)
    
    print(f"\nFound {len(x_addresses)} potential X addresses")
    
    if x_addresses:
        print("\nFirst 20 addresses:")
        for i, addr in enumerate(x_addresses[:20]):
            print(f"  0x{addr:x}")
        
        # Save results
        results = {
            "x_coordinate": x_coord,
            "addresses": [f"0x{addr:x}" for addr in x_addresses[:50]]
        }
        
        with open('x_addresses.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nSaved to x_addresses.json")
        print("\nNext steps:")
        print("1. Move your character in Minecraft (change X)")
        print("2. Run this script again with new X value")
        print("3. Addresses that appear in both scans are likely correct")
    else:
        print("\nNo addresses found. Try:")
        print("1. Make sure Minecraft is running")
        print("2. Check the X coordinate value is correct")
        print("3. Try a different X value")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())