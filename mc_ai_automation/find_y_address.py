#!/usr/bin/env python3
"""
Find the Y coordinate address by searching for the known value.
Run with: sudo python3 find_y_address.py
"""

import struct
import subprocess

def main():
    # Get Minecraft PID
    pid_output = subprocess.check_output(['pgrep', '-f', 'java.*minecraft']).decode().strip()
    pid = int(pid_output.split('\n')[0])
    print(f'Using PID: {pid}')
    
    # Your current Y coordinate from F3
    target_y = 80.0
    tolerance = 0.1
    
    print(f'\nSearching for Y coordinate: {target_y}')
    print(f'Tolerance: ±{tolerance}')
    print('=' * 60)
    
    found_addresses = []
    
    with open(f'/proc/{pid}/mem', 'rb') as f:
        # Read memory maps to find readable regions
        with open(f'/proc/{pid}/maps', 'r') as maps:
            for line in maps:
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                # Check if region is readable
                perms = parts[1]
                if 'r' not in perms:
                    continue
                
                # Parse address range
                addr_range = parts[0]
                try:
                    start_str, end_str = addr_range.split('-')
                    start_addr = int(start_str, 16)
                    end_addr = int(end_str, 16)
                    
                    # Skip very large regions (over 100MB) to save time
                    region_size = end_addr - start_addr
                    if region_size > 100 * 1024 * 1024:
                        continue
                    
                    # Read the region in chunks
                    chunk_size = 4096
                    for addr in range(start_addr, end_addr, chunk_size):
                        try:
                            f.seek(addr)
                            data = f.read(min(chunk_size, end_addr - addr))
                            
                            # Search for float value
                            for i in range(0, len(data) - 4, 4):
                                val = struct.unpack('<f', data[i:i+4])[0]
                                if abs(val - target_y) < tolerance:
                                    found_addr = addr + i
                                    found_addresses.append(found_addr)
                                    print(f'Found Y at: 0x{found_addr:x} = {val:.3f}')
                                    
                                    # Stop after finding several candidates
                                    if len(found_addresses) >= 20:
                                        break
                        except:
                            pass
                    
                    if len(found_addresses) >= 20:
                        break
                        
                except:
                    pass
    
    print('=' * 60)
    print(f'\nFound {len(found_addresses)} potential Y addresses')
    
    if found_addresses:
        print('\nMost likely candidates (check which is stable):')
        for i, addr in enumerate(found_addresses[:5]):
            print(f'  {i+1}. 0x{addr:x}')

if __name__ == '__main__':
    main()