#!/usr/bin/env python3
"""
Convert file offsets to memory addresses and test pointer chains.
"""

import struct
import os
import sys
from typing import Optional

def convert_file_offset_to_memory_address(dump_file: str, file_offset: int) -> Optional[int]:
    """Convert a file offset to a memory address by analyzing ELF program headers."""
    try:
        with open(dump_file, 'rb') as f:
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
        print("Usage: python3 convert_offsets.py <dump_file> <file_offset1> [file_offset2] ...")
        print("Example: python3 convert_offsets.py minecraft_dump.7539 0x85100038 0x851000e0")
        sys.exit(1)
    
    dump_file = sys.argv[1]
    file_offsets = [int(offset, 16) for offset in sys.argv[2:]]
    
    print(f"Converting file offsets to memory addresses:")
    print(f"Dump file: {dump_file}")
    
    for i, offset in enumerate(file_offsets):
        addr = convert_file_offset_to_memory_address(dump_file, offset)
        if addr:
            print(f"{i+1}. File offset 0x{offset:x} -> Memory address 0x{addr:x}")
        else:
            print(f"{i+1}. File offset 0x{offset:x} -> Could not convert")

if __name__ == "__main__":
    main()