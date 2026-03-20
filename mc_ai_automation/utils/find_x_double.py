#!/usr/bin/env python3
"""
Find X coordinate address - try both float and double formats.
"""

import sys
import struct
import psutil
import json

def find_minecraft_process():
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
    try:
        mem_file = f"/proc/{pid}/mem"
        with open(mem_file, 'rb') as f:
            f.seek(address)
            return f.read(size)
    except Exception as e:
        return None

def scan_for_value(pid, target_value, value_type='double'):
    print(f"Scanning for {value_type} value: {target_value}")
    
    maps_file = f"/proc/{pid}/maps"
    try:
        with open(maps_file, 'r') as f:
            maps = f.readlines()
    except PermissionError:
        print("Permission denied! Run with sudo.")
        return []
    
    found_addresses = []
    
    if value_type == 'double':
        value_bytes = struct.pack('<d', float(target_value))
    else:
        value_bytes = struct.pack('<f', float(target_value))
    
    print(f"Looking for bytes: {value_bytes.hex()}")
    
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
        
        if size > 100 * 1024 * 1024:
            continue
        
        try:
            memory = read_memory(pid, start_addr, size)
            if memory:
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
    print("Finding X Coordinate Address (Double Format)")
    print("=" * 60)
    
    process = find_minecraft_process()
    if not process:
        print("Minecraft process not found!")
        return 1
    
    pid = process.pid
    print(f"Found Minecraft! PID: {pid}")
    
    x_coord = 175.265
    print(f"Searching for X coordinate: {x_coord}")
    
    # Try double first
    print("\n--- Trying DOUBLE format (8 bytes) ---")
    x_addresses_double = scan_for_value(pid, x_coord, 'double')
    
    print(f"\nFound {len(x_addresses_double)} potential X addresses (double)")
    
    if x_addresses_double:
        print("\nFirst 20 addresses:")
        for i, addr in enumerate(x_addresses_double[:20]):
            print(f"  0x{addr:x}")
        
        results = {
            "x_coordinate": x_coord,
            "format": "double",
            "addresses": [f"0x{addr:x}" for addr in x_addresses_double[:50]]
        }
        
        with open('x_addresses.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nSaved to x_addresses.json")
    else:
        print("\nNo addresses found with double format either.")
        print("\nPossible reasons:")
        print("1. X coordinate might be accessed via pointer chain")
        print("2. Value might be transformed/offset in memory")
        print("3. Need to use pointer scan method")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())