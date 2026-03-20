#!/usr/bin/env python3
"""
Test if read_float works correctly.
"""

import sys
sys.path.insert(0, '.')

from core.memory_reader import MemoryReader

def main():
    print("Testing read_float...")
    
    reader = MemoryReader(offsets_file="data/memory/offsets.json")
    
    if reader.attach():
        print(f"Attached to Minecraft (PID: {reader.pid})")
        
        # Test reading X coordinate directly
        x_addr = 0x76a722f30c54
        print(f"Reading X from address: 0x{x_addr:x}")
        
        # Try reading with read_float
        x_val = reader.read_float(x_addr)
        print(f"read_float result: {x_val}")
        
        # Try reading with read_memory directly
        data = reader.read_memory(x_addr, 4)
        print(f"read_memory result: {data}")
        
        if data:
            import struct
            val = struct.unpack('<f', data)[0]
            print(f"struct.unpack result: {val}")
    else:
        print("Failed to attach to Minecraft")

if __name__ == '__main__':
    main()