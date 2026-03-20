#!/usr/bin/env python3
"""
Test memory reading with sudo to verify the fix.
Run this with: sudo python3 test_with_sudo.py
"""

import sys
sys.path.insert(0, '.')

from core.memory_reader import MemoryReader
import struct

def main():
    print("Testing memory reading with sudo...")
    print("=" * 50)
    
    reader = MemoryReader(offsets_file="data/memory/offsets.json")
    
    if not reader.attach():
        print("Failed to attach to Minecraft")
        return
    
    print(f"Attached to Minecraft (PID: {reader.pid})")
    print(f"Base address: 0x{reader.base_address:x}")
    
    # Test addresses from offsets.json
    test_addresses = {
        "X": 0x76a722f30c54,
        "Y": 0x100b6f580,
        "Z": 0x76a722f30c5c,  # Fixed: Z is 8 bytes after X
    }
    
    print("\nTesting coordinate addresses:")
    print("-" * 50)
    
    for coord_name, addr in test_addresses.items():
        print(f"\n{coord_name} coordinate (0x{addr:x}):")
        
        # Test syscall method
        print("  Trying syscall method...")
        data_syscall = reader.read_memory(addr, 4)
        if data_syscall:
            val = struct.unpack('<f', data_syscall)[0]
            print(f"    ✓ Syscall success: {val:.3f}")
        else:
            print("    ✗ Syscall failed")
        
        # Test /proc method
        print("  Trying /proc/pid/mem method...")
        data_proc = reader.read_memory_proc(addr, 4)
        if data_proc:
            val = struct.unpack('<f', data_proc)[0]
            print(f"    ✓ /proc success: {val:.3f}")
        else:
            print("    ✗ /proc failed")
    
    # Test read_float method (which tries both)
    print("\n" + "=" * 50)
    print("Testing read_float method (tries both syscall and /proc):")
    print("-" * 50)
    
    for coord_name, addr in test_addresses.items():
        val = reader.read_float(addr)
        if val is not None:
            print(f"{coord_name}: {val:.3f}")
        else:
            print(f"{coord_name}: FAILED")
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == '__main__':
    main()