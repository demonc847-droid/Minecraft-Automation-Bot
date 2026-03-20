#!/usr/bin/env python3
"""
Pointer Chain Scanner for Minecraft Memory
Scans memory for pointer chains leading to a target address.
"""

import sys
import struct
import psutil
import argparse
import json
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass

@dataclass
class PointerChain:
    base_module: str
    base_offset: int
    offsets: List[int]
    chain_str: str

def find_minecraft_process():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'].lower() if proc.info['name'] else ''
            cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
            if 'java' in name and 'minecraft' in cmdline:
                return proc
        except:
            continue
    return None

def read_memory(pid, address, size):
    try:
        with open(f"/proc/{pid}/mem", 'rb') as f:
            f.seek(address)
            return f.read(size)
    except:
        return None

def get_memory_maps(pid):
    maps = []
    try:
        with open(f"/proc/{pid}/maps", 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 6:
                    addr_range = parts[0].split('-')
                    start = int(addr_range[0], 16)
                    end = int(addr_range[1], 16)
                    perms = parts[1]
                    pathname = parts[5] if len(parts) > 5 else ''
                    maps.append((pathname, start, end, perms))
    except Exception as e:
        print(f"Error: {e}")
    return maps

def scan_for_pointers(pid, target_addr, maps, max_pointers=1000):
    pointers = []
    target_bytes = struct.pack('<Q', target_addr)
    print(f"Scanning for pointers to 0x{target_addr:x}...")
    
    for pathname, start, end, perms in maps:
        if 'r' not in perms:
            continue
        size = end - start
        if size > 500 * 1024 * 1024:
            continue
        try:
            memory = read_memory(pid, start, size)
            if not memory:
                continue
            offset = 0
            while len(pointers) < max_pointers:
                idx = memory.find(target_bytes, offset)
                if idx == -1:
                    break
                ptr_addr = start + idx
                pointers.append((ptr_addr, pathname))
                offset = idx + 8
        except:
            continue
    return pointers

def find_pointer_chains(pid, target_addr, maps, max_depth=3):
    chains = []
    pointers = scan_for_pointers(pid, target_addr, maps, max_pointers=50)
    
    for ptr_addr, pathname in pointers:
        module_name = pathname.split('/')[-1] if '/' in pathname else pathname
        if module_name and not pathname.startswith('['):
            for map_path, map_start, map_end, _ in maps:
                if map_path == pathname and map_start <= ptr_addr < map_end:
                    module_offset = ptr_addr - map_start
                    chain_str = f"[{module_name}+0x{module_offset:x}]"
                    chains.append(PointerChain(
                        base_module=module_name,
                        base_offset=module_offset,
                        offsets=[module_offset],
                        chain_str=chain_str
                    ))
                    print(f"  Found: {chain_str}")
                    break
    return chains

def test_pointer_chain(pid, chain, expected_value, maps):
    try:
        module_base = None
        for pathname, start, end, perms in maps:
            if chain.base_module in pathname and 'r' in perms:
                module_base = start
                break
        if module_base is None:
            return False
        
        addr = module_base + chain.base_offset
        for offset in chain.offsets[:-1]:
            ptr_bytes = read_memory(pid, addr + offset, 8)
            if not ptr_bytes or len(ptr_bytes) != 8:
                return False
            addr = struct.unpack('<Q', ptr_bytes)[0]
            if addr == 0:
                return False
        
        value_bytes = read_memory(pid, addr + chain.offsets[-1], 8)
        if not value_bytes or len(value_bytes) != 8:
            return False
        value = struct.unpack('<d', value_bytes)[0]
        print(f"  Reads: {value:.3f} (expected: {expected_value:.3f})")
        return abs(value - expected_value) < 0.1
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Scan for pointer chains')
    parser.add_argument('--target', required=True, help='Target address (hex)')
    parser.add_argument('--depth', type=int, default=3, help='Max depth')
    parser.add_argument('--test-value', type=float, help='Expected value')
    parser.add_argument('--output', default='pointer_chains.json', help='Output file')
    
    args = parser.parse_args()
    target_addr = int(args.target, 16)
    
    print("=" * 60)
    print("Pointer Chain Scanner")
    print("=" * 60)
    print(f"Target: 0x{target_addr:x}")
    print()
    
    proc = find_minecraft_process()
    if not proc:
        print("ERROR: Minecraft not found!")
        return 1
    
    pid = proc.pid
    print(f"Found Minecraft! PID: {pid}")
    
    maps = get_memory_maps(pid)
    print(f"Found {len(maps)} memory regions")
    print()
    
    print("Searching for pointer chains...")
    chains = find_pointer_chains(pid, target_addr, maps, args.depth)
    
    print()
    print(f"Found {len(chains)} potential chains")
    
    if args.test_value is not None and chains:
        print()
        print("Testing chains...")
        valid = []
        for i, chain in enumerate(chains):
            print(f"Testing {i+1}: {chain.chain_str}")
            if test_pointer_chain(pid, chain, args.test_value, maps):
                print(f"  ✓ VALID!")
                valid.append(chain)
            else:
                print(f"  ✗ Invalid")
        chains = valid
        print(f"\nValid chains: {len(chains)}")
    
    if chains:
        results = {
            "target_address": f"0x{target_addr:x}",
            "chains": [{"base_module": c.base_module, "base_offset": f"0x{c.base_offset:x}", "chain_str": c.chain_str} for c in chains]
        }
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved to {args.output}")
        print("\nRecommended chains:")
        for i, chain in enumerate(chains[:3]):
            print(f"  {i+1}. {chain.chain_str}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
