#!/usr/bin/env python3
"""
Test memory addresses to see if they contain valid pointers.
"""

import struct
import os
import sys
import psutil
from typing import Optional

def read_memory(pid: int, address: int, size: int) -> Optional[bytes]:
    """Read memory from the target process."""
    try:
        with open(f'/proc/{pid}/mem', 'rb') as f:
            f.seek(address)
            return f.read(size)
    except Exception as e:
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 test_memory_addresses.py <pid> <address1> [address2] ...")
        print("Example: python3 test_memory_addresses.py 3418 0x1050f42f8 0x1050f43a0")
        sys.exit(1)
    
    pid = int(sys.argv[1])
    addresses = [int(addr, 16) for addr in sys.argv[2:]]
    
    print(f"Testing memory addresses for PID {pid}")
    
    for i, addr in enumerate(addresses):
        data = read_memory(pid, addr, 8)
        if data and len(data) == 8:
            ptr_value = struct.unpack('<Q', data)[0]
            print(f"{i+1}. Address {hex(addr)}: {hex(ptr_value)} (decimal: {ptr_value})")
            
            # Check if it looks like a valid pointer (not null, not too small, not too large)
            if ptr_value != 0 and 0x100000 < ptr_value < 0x7fffffffffff:
                print(f"   ✓ Valid pointer range")
                
                # Try to read what this pointer points to
                target_data = read_memory(pid, ptr_value, 8)
                if target_data and len(target_data) == 8:
                    target_value = struct.unpack('<Q', target_data)[0]
                    print(f"   → Points to: {hex(target_value)} (decimal: {target_value})")
                    
                    # Check if it points to our target coordinate addresses
                    if ptr_value == 0x8659cf94:
                        print(f"   ✓ Points directly to X coordinate!")
                    elif ptr_value == 0x8659cf9c:
                        print(f"   ✓ Points directly to Z coordinate!")
                    elif abs(ptr_value - 0x8659cf94) < 0x100:
                        print(f"   ✓ Points near X coordinate (offset {hex(ptr_value - 0x8659cf94)})")
                    elif abs(ptr_value - 0x8659cf9c) < 0x100:
                        print(f"   ✓ Points near Z coordinate (offset {hex(ptr_value - 0x8659cf9c)})")
                else:
                    print(f"   ✗ Cannot read target memory")
            else:
                print(f"   ✗ Invalid pointer range")
        else:
            print(f"{i+1}. Address {hex(addr)}: Cannot read memory")
        print()

if __name__ == "__main__":
    main()