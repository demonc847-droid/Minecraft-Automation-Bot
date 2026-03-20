#!/usr/bin/env python3
"""
Analyze Minecraft memory dump to find stable pointer chains.
This script analyzes the core dump file to find pointer chains that remain stable across restarts.
"""

import struct
import os
import sys
from typing import List, Tuple, Dict, Optional

class MemoryDumpAnalyzer:
    def __init__(self, dump_file: str):
        self.dump_file = dump_file
        self.dump_size = 0
        self.memory_regions = []
        
    def parse_elf_header(self) -> bool:
        """Parse the ELF header to understand the dump structure."""
        try:
            with open(self.dump_file, 'rb') as f:
                # Read ELF header
                elf_header = f.read(64)
                if len(elf_header) < 64:
                    print("Invalid core dump file")
                    return False
                
                # Check if it's an ELF file
                if elf_header[:4] != b'\x7fELF':
                    print("Not an ELF core dump")
                    return False
                
                # Get file size
                self.dump_size = os.path.getsize(self.dump_file)
                print(f"Memory dump size: {self.dump_size / (1024*1024*1024):.2f} GB")
                
                return True
        except Exception as e:
            print(f"Error reading core dump: {e}")
            return False
    
    def find_pointers_to_address(self, target_addr: int, max_candidates: int = 1000) -> List[int]:
        """Find pointers that point to the target address in the memory dump."""
        candidates = []
        
        print(f"Searching for pointers to {hex(target_addr)} in memory dump...")
        
        try:
            with open(self.dump_file, 'rb') as f:
                # Read the dump in chunks to avoid memory issues
                chunk_size = 1024 * 1024  # 1MB chunks
                current_pos = 0
                
                while current_pos < self.dump_size - 8:
                    # Read a chunk
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Search for potential pointers in this chunk
                    for i in range(0, len(chunk) - 8, 8):
                        try:
                            ptr_value = struct.unpack('<Q', chunk[i:i+8])[0]
                            
                            # Check if this pointer points near our target
                            if abs(ptr_value - target_addr) < 0x10000:  # Within 64KB range
                                # Calculate the actual file offset
                                file_offset = current_pos + i
                                candidates.append(file_offset)
                                
                                if len(candidates) >= max_candidates:
                                    print(f"Found {len(candidates)} candidates")
                                    return candidates
                        except:
                            continue
                    
                    current_pos += len(chunk)
                    
                    # Progress indicator
                    if current_pos % (100 * 1024 * 1024) == 0:  # Every 100MB
                        progress = (current_pos / self.dump_size) * 100
                        print(f"Progress: {progress:.1f}%")
                
        except Exception as e:
            print(f"Error reading memory dump: {e}")
        
        print(f"Found {len(candidates)} candidates")
        return candidates
    
    def find_pointer_chains(self, target_addr: int, max_depth: int = 3, max_candidates: int = 100) -> List[List[int]]:
        """Find pointer chains that lead to the target address."""
        print(f"Finding pointer chains to {hex(target_addr)}...")
        
        # Level 1: Find direct pointers
        level1_candidates = self.find_pointers_to_address(target_addr, max_candidates)
        
        if not level1_candidates:
            print("No level 1 candidates found")
            return []
        
        print(f"Found {len(level1_candidates)} level 1 candidates")
        
        # Multi-level pointer search
        current_chains = [[offset] for offset in level1_candidates[:20]]  # Limit to first 20
        
        for depth in range(2, max_depth + 1):
            print(f"Searching depth {depth}...")
            next_chains = []
            
            for chain in current_chains:
                last_offset = chain[-1]
                
                # Read the value at the end of this chain
                try:
                    with open(self.dump_file, 'rb') as f:
                        f.seek(last_offset)
                        data = f.read(8)
                        if not data or len(data) < 8:
                            continue
                        
                        chain_target = struct.unpack('<Q', data)[0]
                        
                        # Find pointers to this chain target
                        candidates = self.find_pointers_to_address(chain_target, 10)
                        for candidate in candidates:
                            next_chains.append(chain + [candidate])
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
    
    def convert_file_offset_to_memory_address(self, file_offset: int) -> Optional[int]:
        """Convert a file offset to a memory address by analyzing ELF program headers."""
        try:
            with open(self.dump_file, 'rb') as f:
                # Read ELF header to get program header info
                f.seek(0)
                elf_header = f.read(64)
                
                # Parse ELF header (simplified)
                # e_phoff (offset to program headers) is at offset 32, 8 bytes
                # e_phnum (number of program headers) is at offset 56, 2 bytes
                phoff = struct.unpack('<Q', elf_header[32:40])[0]
                phnum = struct.unpack('<H', elf_header[56:58])[0]
                
                # Read program headers
                f.seek(phoff)
                for i in range(phnum):
                    phdr = f.read(56)  # 64-bit program header is 56 bytes
                    if len(phdr) < 56:
                        break
                    
                    # Parse program header
                    p_type = struct.unpack('<I', phdr[0:4])[0]
                    p_flags = struct.unpack('<I', phdr[4:8])[0]
                    p_offset = struct.unpack('<Q', phdr[8:16])[0]
                    p_vaddr = struct.unpack('<Q', phdr[16:24])[0]
                    p_filesz = struct.unpack('<Q', phdr[32:40])[0]
                    
                    # Check if file offset falls within this segment
                    if p_offset <= file_offset < p_offset + p_filesz:
                        # Calculate memory address
                        addr = p_vaddr + (file_offset - p_offset)
                        return addr
                
        except Exception as e:
            print(f"Error converting file offset to memory address: {e}")
        
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 analyze_memory_dump.py <dump_file> <target_address> [max_depth]")
        print("Example: python3 analyze_memory_dump.py minecraft_dump.7539 0x8659cf94 3")
        sys.exit(1)
    
    dump_file = sys.argv[1]
    target_addr = int(sys.argv[2], 16)
    max_depth = 3
    
    if len(sys.argv) >= 4:
        max_depth = int(sys.argv[3])
    
    print(f"Memory Dump Analyzer")
    print(f"Dump file: {dump_file}")
    print(f"Target address: {hex(target_addr)}")
    print(f"Max depth: {max_depth}")
    
    analyzer = MemoryDumpAnalyzer(dump_file)
    
    if not analyzer.parse_elf_header():
        print("Failed to parse memory dump")
        sys.exit(1)
    
    # Find pointer chains
    chains = analyzer.find_pointer_chains(target_addr, max_depth)
    
    if chains:
        print(f"\nFound {len(chains)} potential pointer chains:")
        for i, chain in enumerate(chains):
            # Convert file offsets to memory addresses
            memory_chain = []
            for offset in chain:
                addr = analyzer.convert_file_offset_to_memory_address(offset)
                if addr:
                    memory_chain.append(hex(addr))
                else:
                    memory_chain.append(f"0x{offset:x} (unknown)")
            
            print(f"{i+1}. {[addr for addr in memory_chain]}")
    else:
        print("No pointer chains found")

if __name__ == "__main__":
    main()