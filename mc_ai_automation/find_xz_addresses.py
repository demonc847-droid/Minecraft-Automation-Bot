#!/usr/bin/env python3
"""
Find X and Z coordinate addresses by searching for known values.
Run with: sudo python3 find_xz_addresses.py
"""

import struct
import subprocess

def search_value(pid, target_val, val_name, tolerance=0.1):
    """Search for a float value in memory."""
    print(f'\nSearching for {val_name}: {target_val}')
    print('=' * 60)
    
    found_addresses = []
    
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
                            
                            for i in range(0, len(data) - 4, 4):
                                val = struct.unpack('<f', data[i:i+4])[0]
                                if abs(val - target_val) < tolerance:
                                    found_addr = addr + i
                                    found_addresses.append(found_addr)
                                    print(f'Found {val_name} at: 0x{found_addr:x} = {val:.3f}')
                                    
                                    if len(found_addresses) >= 15:
                                        break
                        except:
                            pass
                    
                    if len(found_addresses) >= 15:
                        break
                        
                except:
                    pass
    
    print(f'\nFound {len(found_addresses)} potential {val_name} addresses')
    return found_addresses

def main():
    pid_output = subprocess.check_output(['pgrep', '-f', 'java.*minecraft']).decode().strip()
    pid = int(pid_output.split('\n')[0])
    print(f'Using PID: {pid}')
    
    # Current coordinates from F3
    target_x = 200.5
    target_z = 200.5
    
    # Search for X
    x_addresses = search_value(pid, target_x, 'X')
    
    # Search for Z
    z_addresses = search_value(pid, target_z, 'Z')
    
    print('\n' + '=' * 60)
    print('SUMMARY')
    print('=' * 60)
    
    if x_addresses:
        print(f'\nBest X candidate: 0x{x_addresses[0]:x}')
    
    if z_addresses:
        print(f'Best Z candidate: 0x{z_addresses[0]:x}')
    
    print(f'\nBest Y candidate: 0x100b6f580 (confirmed)')

if __name__ == '__main__':
    main()