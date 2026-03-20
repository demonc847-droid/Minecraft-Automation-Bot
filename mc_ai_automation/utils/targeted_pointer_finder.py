#!/usr/bin/env python3
"""
Targeted Pointer Finder for Minecraft Coordinates
This script focuses on finding pointer chains in specific memory regions.
"""

import struct
import os
import sys
import psutil
from typing import List, Tuple, Optional

class TargetedPointerFinder:
    def __init__(self, pid: int):
        self.pid = pid
        self.process = None
        try:
            self.process = psutil.Process(pid)
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
            return None
    
    def get_memory_regions(self) -> List[Tuple[int, int]]:
        """Get all readable memory regions from /proc/pid/maps"""
        regions = []
        try:
            with open(f'/proc/{self.pid}/maps', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        addr_range = parts[0]
                        perms = parts[1]
                        if 'r' in perms and 'p' not in perms:  # Readable and not private
                            start_addr, end_addr = addr_range.split('-')
                            start = int(start_addr, 16)
                            end = int(end_addr, 16)
                            # Filter for reasonable memory ranges
                            if 0x100000 < start < 0x7fffffffffff and end - start > 0x1000:
                                regions.append((start, end))
        except Exception as e:
            print(f"Error reading memory maps: {e}")
        return regions
    
    def find_pointers_in_region(self, target_addr: int, region_start: int, region_end: int, 
                              max_candidates: int = 100) -> List[int]:
        """Find pointers to target address within a specific memory region."""
        candidates = []
        current = region_start
        
        print(f"Searching region {hex(region_start)} - {hex(region_end)} for pointers to {hex(target_addr)}")
        
        while current < region_end and len(candidates) < max_candidates:
            try:
                data = self.read_memory(current, 8)
                if data and len(data) == 8:
                    ptr_value = struct.unpack('<Q', data)[0]
                    # Check if this pointer points near our target (within 0x1000 bytes)
                    if abs(ptr_value - target_addr) < 0x1000:
                        candidates.append(current)
                        if len(candidates) % 10 == 0:
                            print(f"  Found {len(candidates)} candidates so far...")
                current += 8
            except:
                current += 8
        
        return candidates
    
    def find_pointer_chains(self, target_addr: int, expected_value: float, 
                          max_depth: int = 3) -> List[List[int]]:
        """Find pointer chains leading to the target address."""
        regions = self.get_memory_regions()
        print(f"Found {len(regions)} memory regions to search")
        
        # Level 1: Find direct pointers
        level1_candidates = []
        for start, end in regions:
            candidates = self.find_pointers_in_region(target_addr, start, end, 50)
            level1_candidates.extend(candidates)
            if len(level1_candidates) >= 100:
                break
        
        print(f"Found {len(level1_candidates)} level 1 candidates")
        
        if not level1_candidates:
            return []
        
        # Multi-level search
        current_chains = [[addr] for addr in level1_candidates[:20]]  # Limit to first 20
        
        for depth in range(2, max_depth + 1):
            print(f"Searching depth {depth}...")
            next_chains = []
            
            for chain in current_chains:
                last_addr = chain[-1]
                
                # Read the value at the end of this chain
                try:
                    data = self.read_memory(last_addr, 8)
                    if not data or len(data) < 8:
                        continue
                    
                    chain_target = struct.unpack('<Q', data)[0]
                    
                    # Find pointers to this chain target in all regions
                    for start, end in regions:
                        candidates = self.find_pointers_in_region(chain_target, start, end, 10)
                        for candidate in candidates:
                            next_chains.append(chain + [candidate])
                            if len(next_chains) >= 20:
                                break
                        if len(next_chains) >= 20:
                            break
                    if len(next_chains) >= 20:
                        break
                except:
                    continue
            
            if next_chains:
                current_chains = next_chains
                print(f"Found {len(current_chains)} chains at depth {depth}")
            else:
                break
        
        return current_chains
    
    def validate_chain(self, chain: List[int], expected_value: float) -> bool:
        """Validate that a pointer chain points to the expected coordinate value."""
        try:
            # Follow the pointer chain
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
                    # Follow the pointer
                    pass
            
            return False
        except:
            return False

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 targeted_pointer_finder.py <pid> <target_address> <expected_value>")
        print("Example: python3 targeted_pointer_finder.py 7539 0x8659cf94 500.5")
        sys.exit(1)
    
    pid = int(sys.argv[1])
    target_addr = int(sys.argv[2], 16)
    expected_value = float(sys.argv[3])
    
    print(f"Targeted Pointer Finder")
    print(f"PID: {pid}")
    print(f"Target Address: {hex(target_addr)}")
    print(f"Expected Value: {expected_value}")
    
    finder = TargetedPointerFinder(pid)
    
    # Find pointer chains
    chains = finder.find_pointer_chains(target_addr, expected_value)
    
    if chains:
        print(f"\nFound {len(chains)} potential pointer chains:")
        valid_chains = []
        for i, chain in enumerate(chains):
            if finder.validate_chain(chain, expected_value):
                valid_chains.append(chain)
                print(f"{i+1}. VALID: {[hex(addr) for addr in chain]}")
            else:
                print(f"{i+1}. INVALID: {[hex(addr) for addr in chain]}")
        
        if valid_chains:
            print(f"\nValid chains found: {len(valid_chains)}")
            return valid_chains
        else:
            print("No valid chains found")
            return []
    else:
        print("No pointer chains found")
        return []

if __name__ == "__main__":
    main()