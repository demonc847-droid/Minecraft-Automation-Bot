#!/usr/bin/env python3
"""
Scan memory around the stable Y address to find X and Z coordinates.
Run with: sudo python3 scan_coords.py
"""
import struct
import subprocess

# Find Minecraft PID
try:
    pid = int(subprocess.check_output(['pgrep', '-f', 'java.*minecraft']).decode().strip())
    print(f"Found Minecraft PID: {pid}")
except Exception as e:
    print(f"Error finding Minecraft process: {e}")
    exit(1)

# Stable Y address
y_addr = 0x100b667e8

try:
    with open(f'/proc/{pid}/mem', 'rb') as f:
        print(f"\nScanning memory around Y address (0x{y_addr:x}):\n")
        print("Offset  | Address      | Value")
        print("-" * 40)
        
        for offset in range(-32, 33, 4):
            addr = y_addr + offset
            f.seek(addr)
            data = f.read(4)
            if len(data) == 4:
                val = struct.unpack('<f', data)[0]
                if -1000 < val < 1000:  # plausible coordinate
                    print(f"{offset:+4}    | 0x{addr:010x} | {val:.2f}")
        
        print("\nMatch these values with your current X and Z from Minecraft F3 screen.")
        
except Exception as e:
    print(f"Error reading memory: {e}")
    print("Make sure you're running with sudo!")