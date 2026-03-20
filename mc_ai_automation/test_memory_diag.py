#!/usr/bin/env python3
"""
Diagnostic script to test memory reading with detailed error reporting.
"""

import sys
sys.path.insert(0, '.')

from core.memory_reader import MemoryReader
import ctypes

def check_permissions():
    """Check if we have permission to read process memory."""
    print("Checking memory access permissions...")
    
    try:
        with open('/proc/sys/kernel/yama/ptrace_scope', 'r') as f:
            scope = f.read().strip()
            print(f"Yama ptrace_scope: {scope}")
            
            if scope == '0':
                print("✅ Permission level: Full access (no restrictions)")
                return True
            elif scope == '1':
                print("⚠️  Permission level: Restricted (child processes only)")
                print("   To fix: sudo sysctl kernel.yama.ptrace_scope=0")
                return False
            elif scope == '2':
                print("⚠️  Permission level: Admin only")
                print("   To fix: sudo sysctl kernel.yama.ptrace_scope=0")
                return False
            elif scope == '3':
                print("❌ Permission level: No access (ptrace disabled)")
                print("   To fix: sudo sysctl kernel.yama.ptrace_scope=0")
                return False
            else:
                print(f"Unknown ptrace_scope value: {scope}")
                return False
    except FileNotFoundError:
        print("ℹ️  Yama ptrace_scope not found (may not be applicable on this system)")
        return True
    except Exception as e:
        print(f"Error checking permissions: {e}")
        return False

def test_syscall():
    """Test if syscall works at all."""
    print("\nTesting syscall functionality...")
    
    reader = MemoryReader(offsets_file="data/memory/offsets.json")
    
    if not reader.attach():
        print("Failed to attach to Minecraft")
        return
    
    print(f"Attached to Minecraft (PID: {reader.pid})")
    
    # Test reading from a known valid address (base address)
    print(f"\nTesting read from base address: 0x{reader.base_address:x}")
    data = reader.read_memory(reader.base_address, 4)
    print(f"Result: {data}")
    
    if data:
        print(f"Successfully read {len(data)} bytes")
        print(f"Bytes: {data.hex()}")
    else:
        print("Failed to read from base address")
        
        # Check if it's a permission issue
        print("\nChecking /proc/pid/mem access...")
        try:
            with open(f"/proc/{reader.pid}/mem", 'rb') as f:
                f.seek(reader.base_address)
                test_data = f.read(4)
                print(f"Direct /proc/pid/mem read: {test_data.hex()}")
        except PermissionError:
            print("Permission denied - need sudo!")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test the specific X coordinate address
    x_addr = 0x76a722f30c54
    print(f"\nTesting X coordinate address: 0x{x_addr:x}")
    data = reader.read_memory(x_addr, 4)
    print(f"Result: {data}")
    
    if data:
        import struct
        val = struct.unpack('<f', data)[0]
        print(f"Float value: {val}")

if __name__ == '__main__':
    # Check permissions first
    has_permissions = check_permissions()
    
    if not has_permissions:
        print("\n⚠️  Warning: Limited permissions detected")
        print("   Memory reading may fail. Run with sudo or fix Yama settings.")
    
    # Run the test
    test_syscall()
