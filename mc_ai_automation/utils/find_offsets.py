#!/usr/bin/env python3
"""
Minecraft Offset Finder Tool
=============================

This tool helps you find memory offsets for Minecraft.
Run this while Minecraft is running to automatically find key offsets.

Usage:
    python find_offsets.py

Requirements:
    - Minecraft Java Edition running
    - A world loaded
    - Administrator/root privileges (for memory access)
"""

import sys
import struct
import json
from pathlib import Path

# Try to import memory reading libraries
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not installed. Install with: pip install psutil")

try:
    import pymem
    PYMEM_AVAILABLE = True
except ImportError:
    PYMEM_AVAILABLE = False
    print("Note: pymem only works on Windows. Using alternative method on Linux.")


def find_minecraft_process():
    """Find the Minecraft Java process."""
    if not PSUTIL_AVAILABLE:
        print("Error: psutil is required. Install with: pip install psutil")
        return None
    
    minecraft_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'].lower() if proc.info['name'] else ''
            cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
            
            # Look for Java processes running Minecraft
            if 'java' in name and ('minecraft' in cmdline or 'minecraft' in name):
                minecraft_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not minecraft_processes:
        print("Minecraft process not found!")
        print("Make sure Minecraft Java Edition is running.")
        return None
    
    if len(minecraft_processes) > 1:
        print(f"Found {len(minecraft_processes)} Minecraft processes:")
        for i, proc in enumerate(minecraft_processes):
            print(f"  {i}: PID {proc.pid}")
        choice = input("Select process number (default 0): ").strip()
        idx = int(choice) if choice.isdigit() else 0
        return minecraft_processes[idx]
    
    return minecraft_processes[0]


def read_memory_linux(pid, address, size):
    """Read memory from process on Linux."""
    try:
        mem_file = f"/proc/{pid}/mem"
        maps_file = f"/proc/{pid}/maps"
        
        # Check if we have permission
        with open(maps_file, 'r') as f:
            pass
        
        with open(mem_file, 'rb') as f:
            f.seek(address)
            return f.read(size)
    except PermissionError:
        print(f"Permission denied! Run with sudo.")
        return None
    except Exception as e:
        print(f"Error reading memory: {e}")
        return None


def read_memory_windows(pid, address, size):
    """Read memory from process on Windows."""
    if not PYMEM_AVAILABLE:
        print("Error: pymem is required on Windows. Install with: pip install pymem")
        return None
    
    try:
        pm = pymem.Pymem(pid)
        return pm.read_bytes(address, size)
    except Exception as e:
        print(f"Error reading memory: {e}")
        return None


def scan_for_value(process, value, value_type='float'):
    """Scan process memory for a specific value."""
    pid = process.pid
    
    print(f"Scanning for {value_type} value: {value}")
    print("This may take a moment...")
    
    # Read memory maps
    if sys.platform == 'linux':
        maps_file = f"/proc/{pid}/maps"
        try:
            with open(maps_file, 'r') as f:
                maps = f.readlines()
        except PermissionError:
            print("Permission denied! Run with sudo.")
            return []
    else:
        print("Windows scanning not yet implemented in this script.")
        print("Please use Cheat Engine for Windows.")
        return []
    
    # Convert value to bytes
    if value_type == 'float':
        value_bytes = struct.pack('<f', float(value))
    elif value_type == 'double':
        value_bytes = struct.pack('<d', float(value))
    elif value_type == 'int':
        value_bytes = struct.pack('<i', int(value))
    else:
        print(f"Unknown value type: {value_type}")
        return []
    
    found_addresses = []
    
    for line in maps:
        parts = line.split()
        if len(parts) < 5:
            continue
        
        # Check if it's readable memory
        perms = parts[1]
        if 'r' not in perms:
            continue
        
        addr_range = parts[0].split('-')
        start_addr = int(addr_range[0], 16)
        end_addr = int(addr_range[1], 16)
        size = end_addr - start_addr
        
        # Skip very large regions (likely not what we want)
        if size > 100 * 1024 * 1024:  # Skip > 100MB
            continue
        
        try:
            memory = read_memory_linux(pid, start_addr, size)
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


def get_user_input():
    """Get current values from user."""
    print("\n" + "="*50)
    print("Minecraft Offset Finder")
    print("="*50)
    print("\nPlease provide your current Minecraft values.")
    print("You can see these by pressing F3 in Minecraft.\n")
    
    values = {}
    
    # Get position
    print("Current Position (from F3 screen):")
    values['x'] = input("  X coordinate: ").strip()
    values['y'] = input("  Y coordinate: ").strip()
    values['z'] = input("  Z coordinate: ").strip()
    
    # Get health
    print("\nCurrent Health:")
    values['health'] = input("  Health (usually 20.0 when full): ").strip()
    
    # Get hunger
    print("\nCurrent Hunger:")
    values['hunger'] = input("  Hunger (usually 20 when full): ").strip()
    
    return values


def main():
    """Main function."""
    print("\n" + "="*60)
    print("Minecraft 1.21.11 Offset Finder")
    print("="*60)
    
    # Check dependencies
    if not PSUTIL_AVAILABLE:
        print("\nError: psutil is required!")
        print("Install with: pip install psutil")
        return 1
    
    # Find Minecraft process
    print("\nLooking for Minecraft process...")
    process = find_minecraft_process()
    
    if not process:
        return 1
    
    print(f"Found Minecraft! PID: {process.pid}")
    
    # Get user input
    values = get_user_input()
    
    print("\n" + "="*50)
    print("Scanning memory for values...")
    print("="*50)
    
    results = {}
    
    # Scan for X position
    print(f"\n[1/6] Scanning for X position ({values['x']})...")
    x_addresses = scan_for_value(process, values['x'], 'float')
    results['x'] = x_addresses
    print(f"Found {len(x_addresses)} potential addresses")
    
    # Scan for Y position
    print(f"\n[2/6] Scanning for Y position ({values['y']})...")
    y_addresses = scan_for_value(process, values['y'], 'float')
    results['y'] = y_addresses
    print(f"Found {len(y_addresses)} potential addresses")
    
    # Scan for Z position
    print(f"\n[3/6] Scanning for Z position ({values['z']})...")
    z_addresses = scan_for_value(process, values['z'], 'float')
    results['z'] = z_addresses
    print(f"Found {len(z_addresses)} potential addresses")
    
    # Scan for health
    print(f"\n[4/6] Scanning for health ({values['health']})...")
    health_addresses = scan_for_value(process, values['health'], 'float')
    results['health'] = health_addresses
    print(f"Found {len(health_addresses)} potential addresses")
    
    # Find common base address
    print("\n" + "="*50)
    print("Analyzing results...")
    print("="*50)
    
    # Look for addresses that are close together (likely same object)
    if results['x'] and results['y'] and results['z']:
        print("\nLooking for position addresses that are close together...")
        
        for x_addr in results['x'][:10]:  # Check first 10
            for y_addr in results['y'][:10]:
                for z_addr in results['z'][:10]:
                    # Check if addresses are within 0x20 of each other
                    if abs(x_addr - y_addr) < 0x20 and abs(y_addr - z_addr) < 0x20:
                        print(f"\nFound potential player object at:")
                        print(f"  X: 0x{x_addr:x}")
                        print(f"  Y: 0x{y_addr:x}")
                        print(f"  Z: 0x{z_addr:x}")
                        print(f"  Offset between X and Y: 0x{abs(y_addr - x_addr):x}")
                        print(f"  Offset between Y and Z: 0x{abs(z_addr - y_addr):x}")
    
    # Save results
    output_file = "offsets_found.json"
    output = {
        "version": "1.21.11",
        "process_id": process.pid,
        "values_provided": values,
        "found_addresses": {
            "x": [f"0x{addr:x}" for addr in results['x'][:20]],
            "y": [f"0x{addr:x}" for addr in results['y'][:20]],
            "z": [f"0x{addr:x}" for addr in results['z'][:20]],
            "health": [f"0x{addr:x}" for addr in results['health'][:20]]
        },
        "instructions": [
            "1. Move in Minecraft and note new coordinates",
            "2. Run this script again with new values to narrow down results",
            "3. Addresses that appear multiple times are likely correct",
            "4. Update offsets.json with the found addresses"
        ]
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    print("\n" + "="*50)
    print("Next Steps:")
    print("="*50)
    print("1. Move your character in Minecraft")
    print("2. Note your new coordinates (F3)")
    print("3. Run this script again with the new coordinates")
    print("4. Addresses that keep appearing are likely correct")
    print("5. Update mc_ai_automation/offsets.json with found values")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
