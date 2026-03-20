#!/usr/bin/env python3
"""
Verify X and Z addresses by checking nearby memory.
Run with: sudo python3 verify_xz.py
"""

import struct
import subprocess

def main():
    pid_output = subprocess.check_output(['pgrep', '-f', 'java.*minecraft']).decode().strip()
    pid = int(pid_output.split('\n')[0])
    print(f'Using PID: {pid}')
    
    # Candidate address found
    base_addr = 0x76a722f30c54
    
    print(f'\nChecking memory around: 0x{base_addr:x}')
    print('=' * 50)
    
    with open(f'/proc/{pid}/mem', 'rb') as f:
        for offset in range(-16, 20, 4):
            addr = base_addr + offset
            try:
                f.seek(addr)
                val = struct.unpack('<f', f.read(4))[0]
                # Show all values, mark plausible coordinates
                marker = " <-- plausible" if -1000 < val < 1000 else ""
                print(f'offset {offset:+4}: 0x{addr:x} = {val:.3f}{marker}')
            except Exception as e:
                print(f'offset {offset:+4}: Error reading - {e}')
    
    print('=' * 50)
    print('\nIf X and Z are stored together:')
    print('  X should be at offset 0')
    print('  Z should be at offset +4 (if stored as X,Y,Z triplet)')

if __name__ == '__main__':
    main()