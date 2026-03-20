#!/usr/bin/env python3
"""
Cheat Engine-style Memory Analyzer for Minecraft
This script mimics Cheat Engine's pointer scan functionality to find stable pointer chains.
"""

import struct
import os
import sys
import mmap
from typing import List, Tuple, Dict, Optional, Set
import psutil

class CheatEngineAnalyzer:
    def __init__(self, pid: int, dump_file: str):
        self.pid = pid
        self.dump_file = dump_file
        self.memory_regions = []
        self.process = None
        
        try:
            self.process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            print(f"Process with PID {pid} not found")
            sys.exit(1)
    
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
                            regions.append((int(start_addr, 16), int(end_addr, 16)))
        except Exception as e:
            print(f"Error reading memory maps: {e}")
        return regions
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """Read memory from the target process"""
        try:
            with open(f'/proc/{self.pid}/mem', 'rb') as f:
                f.seek(address)
                return f.read(size)
        except Exception as e:
            print(f"Error reading memory at {hex(address)}: {e}")
            return None
    
    def find_pointers_to_address(self, target_addr: int, regions: List[Tuple[int, int]], 
                               max_depth: int = 5, offset_range: int = 0x2000) -> List[List[int]]:
        """Find pointer chains that point to the target address"""
        print(f"Searching for pointer chains to {hex(target_addr)}...")
        
        # Level 1: Find direct pointers
        level1_candidates = []
        for start, end in regions:
            current = start
            while current < end:
                try:
                    data = self.read_memory(current, 8)
                    if data and len(data) == 8:
                        ptr_value = struct.unpack('<Q', data)[0]
                        # Check if this pointer points near our target
                        if abs(ptr_value - target_addr) < offset_range:
                            level1_candidates.append([current])
                            if len(level1_candidates) >= 20:  # Limit candidates
                                break
                    current += 8
                except:
                    current += 8
            
            if len(level1_candidates) >= 20:
                break
        
        print(f"Found {len(level1_candidates)} level 1 candidates")
        
        if not level1_candidates:
            return []
        
        # Multi-level pointer search
        current_chains = level1_candidates
        
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
                    
                    # Find pointers to this chain target
                    for start, end in regions:
                        current = start
                        while current < end and len(next_chains) < 20:
                            try:
                                check_data = self.read_memory(current, 8)
                                if check_data and len(check_data) == 8:
                                    check_ptr = struct.unpack('<Q', check_data)[0]
                                    if abs(check_ptr - chain_target) < offset_range:
                                        next_chains.append(chain + [current])
                                current += 8
                            except:
                                current += 8
                except:
                    continue
            
            if next_chains:
                current_chains = next_chains
                print(f"Found {len(current_chains)} chains at depth {depth}")
            else:
                break
        
        return current_chains
    
    def validate_pointer_chain(self, chain: List[int], expected_value: float) -> bool:
        """Validate that a pointer chain points to the expected coordinate value"""
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
    
    def find_stable_pointer_chains(self, target_addr: int, expected_value: float, 
                                 max_depth: int = 5) -> List[List[int]]:
        """Find stable pointer chains for the target address"""
        regions = self.get_memory_regions()
        print(f"Found {len(regions)} memory regions")
        
        candidates = self.find_pointers_to_address(target_addr, regions, max_depth)
        
        stable_chains = []
        for chain in candidates:
            if self.validate_pointer_chain(chain, expected_value):
                stable_chains.append(chain)
                print(f"Valid chain: {[hex(addr) for addr in chain]}")
        
        return stable_chains
    
    def analyze_coordinate_structure(self, x_addr: int, z_addr: int) -> Dict[str, any]:
        """Analyze the memory structure around coordinates"""
        structure = {
            'x_address': hex(x_addr),
            'z_address': hex(z_addr),
            'distance': abs(z_addr - x_addr),
            'potential_structures': []
        }
        
        # Check if X and Z are close together (likely in same structure)
        if abs(z_addr - x_addr) < 0x100:
            structure['potential_structures'].append("X and Z likely in same memory structure")
            
            # Try to find the base of this structure
            base_addr = min(x_addr, z_addr)
            # Round down to page boundary
            base_addr = (base_addr // 0x1000) * 0x1000
            
            structure['structure_base'] = hex(base_addr)
            structure['structure_size'] = abs(z_addr - x_addr) + 0x20
        
        return structure

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 cheat_engine_analyzer.py <pid> <x_address> <expected_x_value> [z_address] [expected_z_value]")
        print("Example: python3 cheat_engine_analyzer.py 7539 0x8659cf94 500.5 0x8659cf9c 600.5")
        sys.exit(1)
    
    pid = int(sys.argv[1])
    x_addr = int(sys.argv[2], 16)
    x_value = float(sys.argv[3])
    
    z_addr = None
    z_value = None
    
    if len(sys.argv) >= 6:
        z_addr = int(sys.argv[4], 16)
        z_value = float(sys.argv[5])
    
    print(f"Cheat Engine-style Memory Analyzer")
    print(f"PID: {pid}")
    print(f"X Address: {hex(x_addr)}, Expected: {x_value}")
    if z_addr:
        print(f"Z Address: {hex(z_addr)}, Expected: {z_value}")
    
    analyzer = CheatEngineAnalyzer(pid, "")
    
    # Analyze coordinate structure
    if z_addr:
        structure = analyzer.analyze_coordinate_structure(x_addr, z_addr)
        print(f"\nCoordinate Structure Analysis:")
        for key, value in structure.items():
            print(f"  {key}: {value}")
    
    # Find X coordinate pointer chains
    print(f"\n=== Finding X Coordinate Pointer Chains ===")
    x_chains = analyzer.find_stable_pointer_chains(x_addr, x_value)
    
    if x_chains:
        print(f"\nFound {len(x_chains)} stable X coordinate pointer chains:")
        for i, chain in enumerate(x_chains):
            print(f"{i+1}. {[hex(addr) for addr in chain]}")
    else:
        print("No stable X coordinate pointer chains found")
    
    # Find Z coordinate pointer chains if provided
    if z_addr and z_value:
        print(f"\n=== Finding Z Coordinate Pointer Chains ===")
        z_chains = analyzer.find_stable_pointer_chains(z_addr, z_value)
        
        if z_chains:
            print(f"\nFound {len(z_chains)} stable Z coordinate pointer chains:")
            for i, chain in enumerate(z_chains):
                print(f"{i+1}. {[hex(addr) for addr in chain]}")
        else:
            print("No stable Z coordinate pointer chains found")
    
    # Try to find shared base addresses
    if x_chains and z_chains:
        print(f"\n=== Analyzing Shared Base Addresses ===")
        x_bases = {chain[0] for chain in x_chains}
        z_bases = {chain[0] for chain in z_chains}
        shared_bases = x_bases.intersection(z_bases)
        
        if shared_bases:
            print(f"Found {len(shared_bases)} shared base addresses:")
            for base in shared_bases:
                print(f"  Base: {hex(base)}")
        else:
            print("No shared base addresses found")

if __name__ == "__main__":
    main()