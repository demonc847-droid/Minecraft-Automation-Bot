#!/usr/bin/env python3
"""
Test pointer chains found in memory dump to identify stable ones.
"""

import struct
import os
import sys
import psutil
from typing import List, Tuple, Optional

class PointerChainTester:
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
    
    def follow_pointer_chain(self, chain: List[int]) -> Optional[int]:
        """Follow a pointer chain and return the final address."""
        try:
            current_addr = chain[0]
            
            # Follow the chain
            for i in range(len(chain) - 1):
                data = self.read_memory(current_addr, 8)
                if not data or len(data) < 8:
                    return None
                
                current_addr = struct.unpack('<Q', data)[0]
            
            return current_addr
        except:
            return None
    
    def test_pointer_chain(self, chain: List[int], expected_target: int, expected_value: float) -> bool:
        """Test if a pointer chain points to the expected coordinate value."""
        try:
            # Follow the chain to get the final address
            final_addr = self.follow_pointer_chain(chain)
            if not final_addr:
                return False
            
            # Check if it points to the expected target address (within range)
            if abs(final_addr - expected_target) > 0x100:
                return False
            
            # Read the coordinate value at the final address
            coord_data = self.read_memory(final_addr, 8)
            if not coord_data or len(coord_data) < 8:
                return False
            
            actual_value = struct.unpack('<d', coord_data[:8])[0]
            return abs(actual_value - expected_value) < 0.1
            
        except:
            return False
    
    def test_chains(self, chains: List[List[int]], expected_target: int, expected_value: float) -> List[List[int]]:
        """Test multiple pointer chains and return the valid ones."""
        valid_chains = []
        
        print(f"Testing {len(chains)} pointer chains...")
        
        for i, chain in enumerate(chains):
            if self.test_pointer_chain(chain, expected_target, expected_value):
                valid_chains.append(chain)
                print(f"✓ Chain {i+1} VALID: {[hex(addr) for addr in chain]}")
            else:
                print(f"✗ Chain {i+1} INVALID: {[hex(addr) for addr in chain]}")
        
        return valid_chains

def main():
    if len(sys.argv) < 5:
        print("Usage: python3 test_pointer_chains.py <pid> <expected_x_value> <expected_z_value> <chain1_addr1> <chain1_addr2> ...")
        print("Example: python3 test_pointer_chains.py 7539 500.5 600.5 0x1050f42f8 0x1050f42f8 0x1050f42f8")
        sys.exit(1)
    
    pid = int(sys.argv[1])
    expected_x = float(sys.argv[2])
    expected_z = float(sys.argv[3])
    
    # Parse chains from arguments (assuming chains of 3 addresses each)
    chain_data = [int(addr, 16) for addr in sys.argv[4:]]
    
    # Group into chains of 3
    chains = []
    for i in range(0, len(chain_data), 3):
        if i + 2 < len(chain_data):
            chains.append([chain_data[i], chain_data[i+1], chain_data[i+2]])
    
    if not chains:
        print("No valid chains provided")
        sys.exit(1)
    
    print(f"Pointer Chain Tester")
    print(f"PID: {pid}")
    print(f"Expected X: {expected_x}, Expected Z: {expected_z}")
    print(f"Testing {len(chains)} chains")
    
    tester = PointerChainTester(pid)
    
    # Test X coordinate chains
    print(f"\n=== Testing X Coordinate Chains ===")
    x_chains = tester.test_chains(chains, 0x8659cf94, expected_x)
    
    # Test Z coordinate chains (Z is at 0x8659cf9c, which is 8 bytes after X)
    print(f"\n=== Testing Z Coordinate Chains ===")
    z_chains = tester.test_chains(chains, 0x8659cf9c, expected_z)
    
    # Report results
    print(f"\n=== Results ===")
    print(f"Valid X chains: {len(x_chains)}")
    print(f"Valid Z chains: {len(z_chains)}")
    
    if x_chains:
        print(f"\nValid X chains:")
        for i, chain in enumerate(x_chains):
            print(f"  {i+1}. {[hex(addr) for addr in chain]}")
    
    if z_chains:
        print(f"\nValid Z chains:")
        for i, chain in enumerate(z_chains):
            print(f"  {i+1}. {[hex(addr) for addr in chain]}")
    
    # Look for shared base addresses
    if x_chains and z_chains:
        print(f"\n=== Shared Base Analysis ===")
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