#!/usr/bin/env python3
"""
Search for X,Y,Z coordinate triplet structure in memory.
Run with: sudo python3 find_xyz_structure.py
"""

import struct
import subprocess

def main():
    pid_output = subprocess.check_output(['pgrep', '-f', 'java.*minecraft']).decode().strip()
    pid = int(pid_output.split('\n')[0])
    print(f'Using PID: {pid}')
    
    # Current coordinates from F3
    target_x = 200.5
    target_y = 80.0
    target_z = 200.5
    tolerance = 0.2
    
    print(f'\nSearching for coordinate triplet:')
    print(f'  X = {target_x}')
    print(f'  Y = {target_y}')
    print(f'  Z = {target_z}')
    print('=' * 60)
    
    found_structures = []
    
    with open(f'/proc/{pid}/mem', 'rb') as f:
        with open(f'/proc/{pid}/maps', 'r') as maps:
            for line in maps:
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                perms = parts[1]
                if 'r' not in perms:
                    continue
                
                addr_range = parts[0]
                try:
                    start_str, end_str = addr_range.split('-')
                    start_addr = int(start_str, 16)
                    end_addr = int(end_str, 16)
                    
                    region_size = end_addr - start_addr
                    if region_size > 100 * 1024 * 1024:
                        continue
                    
                    chunk_size = 4096
                    for addr in range(start_addr, end_addr, chunk_size):
                        try:
                            f.seek(addr)
                            data = f.read(min(chunk_size, end_addr - addr))
                            
                            # Search for triplet pattern
                            for i in range(0, len(data) - 12, 4):
                                val1 = struct.unpack('<f', data[i:i+4])[0]
                                val2 = struct.unpack('<f', data[i+4:i+8])[0]
                                val3 = struct.unpack('<f', data[i+8:i+12])[0]
                                
                                # Check if this could be X, Y, Z
                                if (abs(val1 - target_x) < tolerance and 
                                    abs(val2 - target_y) < tolerance and 
                                    abs(val3 - target_z) < tolerance):
                                    base = addr + i
                                    found_structures.append(base)
                                    print(f'Found triplet at: 0x{base:x}')
                                    print(f'  X: {val1:.3f}')
                                    print(f'  Y: {val2:.3f}')
                                    print(f'  Z: {val3:.3f}')
                                    print()
                                    
                                    if len(found_structures) >= 10:
                                        break
                        except:
                            pass
                    
                    if len(found_structures) >= 10:
                        break
                        
                except:
                    pass
    
    print('=' * 60)
    print(f'Found {len(found_structures)} coordinate structures')
    
    if found_structures:
        print(f'\nBest candidate base: 0x{found_structures[0]:x}')
        print('Offsets:')
        print(f'  X: offset 0')
        print(f'  Y: offset +4')
        print(f'  Z: offset +8')

if __name__ == '__main__':
    main()