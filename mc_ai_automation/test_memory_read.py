#!/usr/bin/env python3
"""
Test if memory addresses are still valid.
Run with: sudo python3 test_memory_read.py
"""

import struct
import subprocess

def main():
    # Get Minecraft PID
    pid_output = subprocess.check_output(['pgrep', '-f', 'java.*minecraft']).decode().strip()
    pid = int(pid_output.split('\n')[0])
    print(f'Using PID: {pid}')
    
    # Test addresses from offsets.json
    addresses = {
        'X': 0x76a722f30c54,
        'Y': 0x100b6f580,
        'Z': 0x76a722f30c54
    }
    
    print('\nTesting memory addresses:')
    print('=' * 50)
    
    with open(f'/proc/{pid}/mem', 'rb') as f:
        for name, addr in addresses.items():
            try:
                f.seek(addr)
                data = f.read(4)
                val = struct.unpack('<f', data)[0]
                print(f'{name} (0x{addr:x}): {val:.3f}')
            except Exception as e:
                print(f'{name} (0x{addr:x}): ERROR - {e}')
    
    print('=' * 50)
    print('\nIf all show ERROR, the addresses are invalid.')
    print('If values are wrong, we need to find new addresses.')

if __name__ == '__main__':
    main()