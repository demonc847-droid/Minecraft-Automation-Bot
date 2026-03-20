#!/usr/bin/env python3
"""
Find X coordinate address using scanmem.
Following the guide in hello44009.md
"""

import subprocess
import sys
import time

def run_scanmem(pid, commands, timeout=30):
    """Run scanmem with given commands."""
    proc = subprocess.Popen(
        ['scanmem', '-p', str(pid)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = proc.communicate(input=commands, timeout=timeout)
    return stdout, stderr

def main():
    print("=" * 60)
    print("Finding X Coordinate Address with scanmem")
    print("=" * 60)
    
    pid = 41082
    x_coord = 175.265
    
    print(f"Minecraft PID: {pid}")
    print(f"Current X coordinate: {x_coord}")
    print()
    
    # Step 1: Search for X coordinate
    print("Step 1: Searching for X coordinate value...")
    commands = f"""
search {x_coord}
list
"""
    
    try:
        stdout, stderr = run_scanmem(pid, commands, timeout=30)
        print("scanmem output:")
        print(stdout)
        
        if stderr:
            print("Errors:")
            print(stderr)
    except Exception as e:
        print(f"Error running scanmem: {e}")
        return 1
    
    # Step 2: Instructions for narrowing down
    print("\n" + "=" * 60)
    print("NEXT STEPS (Manual):")
    print("=" * 60)
    print("1. Move your character in Minecraft (change X significantly)")
    print("2. Run scanmem again with the new X value:")
    print("   sudo scanmem -p 41082")
    print("3. In scanmem prompt:")
    print("   > search (new X value)")
    print("   > list")
    print("4. Repeat until you have 1-2 addresses left")
    print("5. Note down the dynamic address (e.g., 0x7f8c4a2b5678)")
    print()
    print("Then run pointer scan:")
    print("   > pointer scan (address) 5 0x1000")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())