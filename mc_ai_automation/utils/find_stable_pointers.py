#!/usr/bin/env python3
"""
Find stable pointer chains for Minecraft coordinates using memory analysis.
This script analyzes memory regions to find pointer chains that remain stable across restarts.
"""

import os
import struct
import sys
import time
from typing import List, Tuple, Optional
import psutil

class PointerChainFinder:
    def __init__(self, pid: int):
        self.pid = pid
        self.proc = None
        try:
            self.proc = psutil.Process(pid)
        except psutil.NoSuchProcess:
            print(f"Process with PID {pid} not found")
            sys.exit(1)
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """Read memory from the target process."""
        try:
            with open(f'/proc/{self.pid}/mem', 'rb') as f:
                f.seek(address)
                return f.read(size)
        except Exception as e:
            print(f"Error reading memory at {hex(address)}: {e}")
            return None
    
    def write_memory(self, address: int, data: bytes) -> bool:
        """Write memory to the target process."""
        try:
            with open(f'/proc/{self.pid}/mem', 'r+b') as f:
                f.seek(address)
                f.write(data)
            return True
        except Exception as e:
            print(f"Error writing memory at {hex(address)}: {e}")
            return False
    
    def get_memory_regions(self) -> List[Tuple[int, int]]:
        """Get all readable memory regions of the process."""
        regions = []
        try:
            with open(f'/proc/{self.pid}/maps', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        addr_range = parts[0]
                        perms = parts[1]
                        if 'r' in perms:  # Only readable regions
                            start_addr, end_addr = addr_range.split('-')
                            regions.append((int(start_addr, 16), int(end_addr, 16)))
        except Exception as e:
            print(f"Error reading memory maps: {e}")
        return regions
    
    def find_pointer_to_address(self, target_addr: int, regions: List[Tuple[int, int]], 
                              max_depth: int = 3, offset_range: int = 0x1000) -> List[List[int]]:
        """Find pointers that point to the target address."""
        candidates = []
        
        print(f"Searching for pointers to {hex(target_addr)}...")
        
        for depth in range(1, max_depth + 1):
            print(f"Searching depth {depth}...")
            
            if depth == 1:
                # First level: direct pointers
                for start, end in regions:
                    current = start
                    while current < end:
                        try:
                            data = self.read_memory(current, 8)
                            if data and len(data) == 8:
                                ptr_value = struct.unpack('<Q', data)[0]
                                if abs(ptr_value - target_addr) < offset_range:
                                    candidates.append([current])
                                    if len(candidates) >= 10:  # Limit candidates
                                        break
                            current += 8
                        except:
                            current += 8
            else:
                # Multi-level pointers
                new_candidates = []
                for chain in candidates:
                    last_addr = chain[-1]
                    try:
                        data = self.read_memory(last_addr, 8)
                        if data and len(data) == 8:
                            ptr_value = struct.unpack('<Q', data)[0]
                            
                            # Search for pointers to this address
                            for start, end in regions:
                                current = start
                                while current < end and len(new_candidates) < 10:
                                    try:
                                        check_data = self.read_memory(current, 8)
                                        if check_data and len(check_data) == 8:
                                            check_ptr = struct.unpack('<Q', check_data)[0]
                                            if abs(check_ptr - ptr_value) < offset_range:
                                                new_candidates.append(chain + [current])
                                        current += 8
                                    except:
                                        current += 8
                    except:
                        pass
                
                candidates = new_candidates
            
            if candidates:
                print(f"Found {len(candidates)} candidates at depth {depth}")
                break
        
        return candidates
    
    def test_pointer_chain(self, chain: List[int], expected_value: float) -> bool:
        """Test if a pointer chain points to the expected value."""
        try:
            # Follow the pointer chain
            current_value = 0
            for i, addr in enumerate(chain):
                data = self.read_memory(addr, 8)
                if not data or len(data) < 8:
                    return False
                
                if i == len(chain) - 1:
                    # Last address should contain the coordinate value
                    coord_data = self.read_memory(addr, 8)
                    if coord_data and len(coord_data) >= 8:
                        actual_value = struct.unpack('<d', coord_data[:8])[0]
                        return abs(actual_value - expected_value) < 0.1
                else:
                    current_value = struct.unpack('<Q', data)[0]
            
            return False
        except:
            return False
    
    def find_stable_pointers(self, target_addr: int, expected_value: float) -> List[List[int]]:
        """Find stable pointer chains for the target address."""
        regions = self.get_memory_regions()
        print(f"Found {len(regions)} memory regions")
        
        candidates = self.find_pointer_to_address(target_addr, regions)
        
        stable_chains = []
        for chain in candidates:
            if self.test_pointer_chain(chain, expected_value):
                stable_chains.append(chain)
                print(f"Valid chain: {[hex(addr) for addr in chain]}")
        
        return stable_chains

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 find_stable_pointers.py <pid> <target_address> <expected_value>")
        print("Example: python3 find_stable_pointers.py 7539 0x8659cf94 500.5")
        sys.exit(1)
    
    pid = int(sys.argv[1])
    target_addr = int(sys.argv[2], 16)
    expected_value = float(sys.argv[3])
    
    print(f"Finding stable pointers for PID {pid}")
    print(f"Target address: {hex(target_addr)}")
    print(f"Expected value: {expected_value}")
    
    finder = PointerChainFinder(pid)
    stable_chains = finder.find_stable_pointers(target_addr, expected_value)
    
    if stable_chains:
        print(f"\nFound {len(stable_chains)} stable pointer chains:")
        for i, chain in enumerate(stable_chains):
            print(f"{i+1}. {[hex(addr) for addr in chain]}")
    else:
        print("No stable pointer chains found")

if __name__ == "__main__":
    main()