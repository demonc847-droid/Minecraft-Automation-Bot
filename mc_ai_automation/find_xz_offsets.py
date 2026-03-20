#!/usr/bin/env python3
"""
Find X and Z coordinate addresses around the stable Y address.
Run with: sudo python3 find_xz_offsets.py
"""

import struct
import subprocess

def main():
    # Get Minecraft PID
    pid_output = subprocess.check_output(['pgrep', '-f', 'java.*minecraft']).decode().strip()
    pid = int(pid_output.split('\n')[0])
    print(f'Using PID: {pid}')
    
    # New Y address found (updated after Minecraft restart)
    y_addr = 0x100b6f580
    print(f'\nScanning memory around Y address: 0x{y_addr:x}')
    print('=' * 50)
    
    with open(f'/proc/{pid}/mem', 'rb') as f:
        # Read values around Y
        for offset in range(-32, 33, 4):
            try:
                f.seek(y_addr + offset)
                val = struct.unpack('<f', f.read(4))[0]
                if -1000 < val < 1000:  # plausible coordinate
                    print(f'offset {offset:+4}: {val:.3f}')
            except:
                pass
    
    print('=' * 50)
    print('\nCompare these values with your F3 coordinates in Minecraft.')
    print('The Y value should be at offset 0.')
    print('Find which offsets match your X and Z coordinates.')

if __name__ == '__main__':
    main()