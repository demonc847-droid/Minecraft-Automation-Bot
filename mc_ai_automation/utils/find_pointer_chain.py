#!/usr/bin/env python3
"""
Find Pointer Chains for X/Z Coordinates
========================================

This script implements the methodology from hello44009.md to find pointer
chains for X and Z coordinates in Minecraft's memory.

Usage:
    1. Launch Minecraft 1.21.11 and note your coordinates (F3)
    2. Run: sudo python3 find_pointer_chain.py
    3. Follow the interactive prompts to narrow down addresses
    4. The script will generate pointer chain candidates

Requirements:
    - scanmem installed
    - sudo privileges
    - Minecraft running
"""

import subprocess
import sys
import json
import re
from typing import List, Optional

def get_minecraft_pid() -> Optional[int]:
    """Find Minecraft process ID."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "java.*minecraft"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            if pids and pids[0]:
                return int(pids[0])
    except Exception as e:
        print(f"Error finding Minecraft PID: {e}")
    return None

def run_scanmem_interactive(pid: int):
    """Run scanmem in interactive mode."""
    print("\n" + "=" * 60)
    print("Starting scanmem interactive mode")
    print("=" * 60)
    print(f"Minecraft PID: {pid}")
    print()
    print("Commands to use:")
    print("  search <value>  - Search for a value")
    print("  list            - Show current matches")
    print("  delete <id>     - Remove a match")
    print("  reset           - Clear all matches")
    print("  quit            - Exit scanmem")
    print()
    print("To find X coordinate:")
    print("  1. Note your X coordinate from F3")
    print("  2. Type: search <x_value>")
    print("  3. Move in game (change X significantly)")
    print("  4. Type: search <new_x_value>")
    print("  5. Repeat until 1-2 addresses remain")
    print()
    print("After finding the dynamic address, run pointer scan:")
    print("  pointer scan <address> <depth> <offset_range>")
    print("  Example: pointer scan 0x7f8c4a2b5678 5 0x1000")
    print()
    
    # Launch scanmem
    subprocess.run(["scanmem", "-p", str(pid)])

def parse_pointer_scan_output(output: str) -> List[dict]:
    """Parse pointer scan results."""
    chains = []
    # Pattern: [base] + offset1 + offset2 + ...
    pattern = r'\[(0x[0-9a-fA-F]+)\]((?:\s*\+\s*0x[0-9a-fA-F]+)+)'
    
    for match in re.finditer(pattern, output):
        base = match.group(1)
        offsets_str = match.group(2)
        # Extract all offsets
        offsets = re.findall(r'0x[0-9a-fA-F]+', offsets_str)
        
        chains.append({
            "base": base,
            "offsets": offsets
        })
    
    return chains

def save_results(x_chain: Optional[dict], z_chain: Optional[dict]):
    """Save found pointer chains to offsets.json."""
    try:
        with open('offsets.json', 'r') as f:
            offsets = json.load(f)
        
        if x_chain:
            offsets["player"]["position"]["x"] = {
                "type": "pointer_chain",
                "chain": x_chain["offsets"]
            }
            print(f"Updated X chain: {x_chain['offsets']}")
        
        if z_chain:
            offsets["player"]["position"]["z"] = {
                "type": "pointer_chain",
                "chain": z_chain["offsets"]
            }
            print(f"Updated Z chain: {z_chain['offsets']}")
        
        with open('offsets.json', 'w') as f:
            json.dump(offsets, f, indent=4)
        
        print("\nOffsets saved to offsets.json")
        
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    print("=" * 60)
    print("Minecraft X/Z Pointer Chain Finder")
    print("=" * 60)
    print()
    print("This tool helps find pointer chains for X and Z coordinates.")
    print("See hello44009.md for detailed methodology.")
    print()
    
    # Check if Minecraft is running
    pid = get_minecraft_pid()
    if not pid:
        print("ERROR: Minecraft process not found!")
        print("Please launch Minecraft 1.21.11 and try again.")
        return 1
    
    print(f"Found Minecraft! PID: {pid}")
    print()
    
    # Interactive mode
    print("OPTIONS:")
    print("1. Launch scanmem (interactive)")
    print("2. Manual pointer chain entry")
    print("3. View current offsets")
    print("4. Exit")
    print()
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == "1":
        run_scanmem_interactive(pid)
        
    elif choice == "2":
        print("\nManual Pointer Chain Entry")
        print("Format: base_offset, offset1, offset2, ...")
        print("Example: 0x1000, 0x28, 0x10")
        print()
        
        x_input = input("X pointer chain (comma-separated hex offsets): ").strip()
        z_input = input("Z pointer chain (comma-separated hex offsets): ").strip()
        
        x_chain = None
        z_chain = None
        
        if x_input:
            x_offsets = [o.strip() for o in x_input.split(',')]
            x_chain = {"offsets": x_offsets}
        
        if z_input:
            z_offsets = [o.strip() for o in z_input.split(',')]
            z_chain = {"offsets": z_offsets}
        
        if x_chain or z_chain:
            save_results(x_chain, z_chain)
        
    elif choice == "3":
        try:
            with open('offsets.json', 'r') as f:
                offsets = json.load(f)
            
            print("\nCurrent Position Offsets:")
            print(json.dumps(offsets.get("player", {}).get("position", {}), indent=2))
        except Exception as e:
            print(f"Error reading offsets: {e}")
    
    elif choice == "4":
        print("Exiting...")
        return 0
    
    else:
        print("Invalid option")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())