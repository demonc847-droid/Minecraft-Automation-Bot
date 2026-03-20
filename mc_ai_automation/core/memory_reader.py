"""
Memory Reader Module
===================

This module implements the MemoryReader class for attaching to the Minecraft
process and reading game state from memory using process_vm_readv syscall.
"""

import json
import os
import subprocess
import struct
import ctypes
import ctypes.util
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .player_state import PlayerState
from .inventory_state import InventoryState, ItemStack
from .world_state import WorldState, Position, Entity, Block, LookingAt


@dataclass
class GameState:
    """
    Complete game state containing player, inventory, and world data.
    
    Attributes:
        player: Player state
        inventory: Inventory state
        world: World state
        timestamp: Unix timestamp when state was read
    """
    player: PlayerState
    inventory: InventoryState
    world: WorldState
    timestamp: float
    
    def to_dict(self) -> dict:
        """Convert game state to dictionary."""
        return {
            "player": self.player.to_dict(),
            "inventory": self.inventory.to_dict(),
            "world": self.world.to_dict(),
            "timestamp": self.timestamp
        }


class MemoryReader:
    """
    Reads Minecraft game state from process memory using DMA.
    
    This class attaches to the Minecraft Java process and reads memory
    at configured offsets to extract player, inventory, and world data.
    """
    
    # Syscall number for process_vm_readv on x86_64
    SYS_process_vm_readv = 310
    
    def __init__(self, offsets_file: str = "offsets.json"):
        """
        Initialize MemoryReader.
        
        Args:
            offsets_file: Path to offsets configuration file
        """
        self.pid: Optional[int] = None
        self.base_address: Optional[int] = None
        self.offsets: Dict[str, Any] = {}
        self.libc = None
        
        self._load_libc()
        self._load_offsets(offsets_file)
    
    def _load_libc(self):
        """Load C library for syscall access."""
        try:
            libc_name = ctypes.util.find_library("c")
            if libc_name:
                self.libc = ctypes.CDLL(libc_name, use_errno=True)
            else:
                raise RuntimeError("Could not find C library")
        except Exception as e:
            raise RuntimeError(f"Failed to load C library: {e}")
    
    def _load_offsets(self, offsets_file: str):
        """
        Load memory offsets from configuration file.
        
        Args:
            offsets_file: Path to offsets JSON file
        """
        try:
            with open(offsets_file, 'r') as f:
                self.offsets = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Offsets file {offsets_file} not found, using defaults")
            self.offsets = self._get_default_offsets()
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {offsets_file}: {e}, using defaults")
            self.offsets = self._get_default_offsets()
    
    def _get_default_offsets(self) -> Dict[str, Any]:
        """
        Get default offset configuration.
        
        Returns:
            Default offsets dictionary
        """
        return {
            "player": {
                "base_offset": "0x00000000",
                "position": {"x": "0x00", "y": "0x08", "z": "0x10"},
                "velocity": {"x": "0x00", "y": "0x08", "z": "0x10"},
                "rotation": {"yaw": "0x00", "pitch": "0x04"},
                "health": "0x00",
                "hunger": "0x00",
                "saturation": "0x00",
                "experience": {"level": "0x00", "progress": "0x00"},
                "flags": {
                    "is_on_ground": "0x00",
                    "is_in_water": "0x00",
                    "is_in_lava": "0x00",
                    "is_sleeping": "0x00"
                }
            },
            "inventory": {
                "base_offset": "0x00000000",
                "selected_slot": "0x00",
                "slots": {
                    "hotbar_start": "0x00",
                    "inventory_start": "0x00",
                    "armor_start": "0x00",
                    "offhand": "0x00"
                },
                "item_structure": {
                    "item_id": "0x00",
                    "count": "0x00",
                    "damage": "0x00",
                    "nbt_data": "0x00"
                }
            },
            "world": {
                "base_offset": "0x00000000",
                "time_of_day": "0x00",
                "day_count": "0x00",
                "difficulty": "0x00",
                "game_mode": "0x00",
                "seed": "0x00",
                "spawn_point": {"x": "0x00", "y": "0x00", "z": "0x00"}
            },
            "pointers": {
                "game_instance": "0x00000000",
                "player_pointer": "0x00000000",
                "world_pointer": "0x00000000",
                "inventory_pointer": "0x00000000",
                "entity_list_pointer": "0x00000000"
            }
        }
    
    def _check_permissions(self) -> bool:
        """
        Check if we have permission to read memory.
        
        Returns:
            True if we have permission, False otherwise
        """
        if self.pid is None:
            return False
        
        try:
            # Try reading 1 byte at a known address
            test_addr = self.base_address or 0x1000
            self.read_memory(test_addr, 1)
            return True
        except PermissionError:
            # Check Yama setting
            try:
                with open('/proc/sys/kernel/yama/ptrace_scope', 'r') as f:
                    scope = f.read().strip()
                    if scope == '1':
                        print("\n⚠️  Yama ptrace_scope = 1 (restricted)")
                        print("   To fix permanently:")
                        print("   sudo sysctl kernel.yama.ptrace_scope=0")
                        print("   echo 'kernel.yama.ptrace_scope=0' | sudo tee -a /etc/sysctl.d/99-minecraft.conf")
                        print("   sudo sysctl --system")
                        return False
            except FileNotFoundError:
                pass
            return False
        except Exception:
            pass
        return False

    def attach(self) -> bool:
        """
        Attach to Minecraft process.
        
        Returns:
            True if successfully attached
        """
        try:
            self.pid = self._get_minecraft_pid()
            if self.pid is None:
                print("Error: Minecraft process not found")
                return False
            
            self.base_address = self._get_module_base(self.pid)
            if self.base_address is None:
                print("Error: Could not find Minecraft module base")
                return False
            
            print(f"Attached to Minecraft (PID: {self.pid}, Base: 0x{self.base_address:x})")
            
            # Check permissions after attaching
            if not self._check_permissions():
                print("⚠️  Warning: Limited memory access permissions detected")
            
            return True
            
        except Exception as e:
            print(f"Error attaching to Minecraft: {e}")
            return False
    
    def _get_minecraft_pid(self) -> Optional[int]:
        """
        Get PID of running Minecraft process.
        
        Returns:
            Process ID or None if not found
        """
        try:
            # Try to find Minecraft process
            result = subprocess.run(
                ["pgrep", "-f", "minecraft"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                if pids and pids[0]:
                    return int(pids[0])
            
            # Alternative: look for java processes with minecraft
            result = subprocess.run(
                ["pgrep", "-f", "java.*minecraft"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                if pids and pids[0]:
                    return int(pids[0])
            
            return None
            
        except Exception as e:
            print(f"Error finding Minecraft PID: {e}")
            return None
    
    def _get_module_base(self, pid: int) -> Optional[int]:
        """
        Get base address of Minecraft module.
        
        Args:
            pid: Process ID
            
        Returns:
            Base address or None if not found
        """
        try:
            # Read memory maps
            maps_file = f"/proc/{pid}/maps"
            with open(maps_file, 'r') as f:
                for line in f:
                    if "minecraft" in line.lower() or "java" in line.lower():
                        # Parse address range
                        addr_range = line.split()[0]
                        start_addr = int(addr_range.split('-')[0], 16)
                        return start_addr
            
            # Fallback: use first executable region
            with open(maps_file, 'r') as f:
                for line in f:
                    if 'r-xp' in line:  # Executable region
                        addr_range = line.split()[0]
                        start_addr = int(addr_range.split('-')[0], 16)
                        return start_addr
            
            return None
            
        except Exception as e:
            print(f"Error getting module base: {e}")
            return None
    
    def _resolve_module_base(self, module_name: str) -> Optional[int]:
        """
        Find base address of a loaded module by scanning /proc/pid/maps.
        
        Args:
            module_name: Name of the module (e.g., "libjvm.so", "libc.so")
            
        Returns:
            Base address of the module or None if not found
        """
        if self.pid is None:
            return None
        
        try:
            maps_file = f"/proc/{self.pid}/maps"
            with open(maps_file, 'r') as f:
                for line in f:
                    if module_name in line:
                        # Parse address range (format: "start-end perms offset dev inode pathname")
                        addr_range = line.split()[0]
                        base_addr = int(addr_range.split('-')[0], 16)
                        return base_addr
            return None
        except Exception as e:
            print(f"Error resolving module base for {module_name}: {e}")
            return None
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """
        Read memory from Minecraft process with automatic fallback.
        
        Tries process_vm_readv syscall first (faster), then falls back to
        /proc/pid/mem if the syscall fails with EPERM.
        
        Args:
            address: Memory address to read
            size: Number of bytes to read
            
        Returns:
            Bytes read or None if failed
        """
        if self.pid is None:
            return None
        
        # Try syscall first (faster)
        result = self._read_memory_syscall(address, size)
        if result is not None:
            return result
        
        # If syscall fails, try /proc/pid/mem fallback
        result = self._read_memory_proc(address, size)
        if result is not None:
            return result
        
        # Both methods failed
        return None
    
    def _read_memory_syscall(self, address: int, size: int) -> Optional[bytes]:
        """
        Read memory using process_vm_readv syscall.
        
        Args:
            address: Memory address to read
            size: Number of bytes to read
            
        Returns:
            Bytes read or None if failed
        """
        if self.pid is None:
            return None
        
        try:
            # Create buffers for process_vm_readv
            buf = ctypes.create_string_buffer(size)
            
            # Define iovec structure
            class IOVec(ctypes.Structure):
                _fields_ = [
                    ("iov_base", ctypes.c_void_p),
                    ("iov_len", ctypes.c_size_t)
                ]
            
            local_iov = IOVec()
            local_iov.iov_base = ctypes.addressof(buf)
            local_iov.iov_len = size
            
            remote_iov = IOVec()
            remote_iov.iov_base = address
            remote_iov.iov_len = size
            
            # Execute syscall
            result = self.libc.syscall(
                self.SYS_process_vm_readv,
                self.pid,
                ctypes.byref(local_iov), 1,
                ctypes.byref(remote_iov), 1,
                0
            )
            
            if result == -1:
                # Check errno for permission error
                errno = ctypes.get_errno()
                if errno == 1:  # EPERM - Permission denied
                    # This is expected with ptrace_scope=1
                    # Don't print error, just fall back silently
                    return None
                elif errno == 14:  # EFAULT - Bad address
                    print(f"Invalid memory address: 0x{address:x}")
                else:
                    print(f"Unexpected syscall error: errno {errno}")
                return None
            
            return buf.raw[:result]
            
        except Exception as e:
            print(f"Error reading memory via syscall: {e}")
            return None
    
    def _read_memory_proc(self, address: int, size: int) -> Optional[bytes]:
        """
        Read memory using /proc/pid/mem (fallback method).
        
        Args:
            address: Memory address to read
            size: Number of bytes to read
            
        Returns:
            Bytes read or None if failed
        """
        if self.pid is None:
            return None
        
        try:
            mem_file = f"/proc/{self.pid}/mem"
            with open(mem_file, 'rb') as f:
                f.seek(address)
                data = f.read(size)
                if len(data) == size:
                    return data
                return None
        except PermissionError:
            # Silently fail - permission checking is done separately
            return None
        except Exception as e:
            print(f"Error reading memory via /proc: {e}")
            return None
    
    def read_memory_proc(self, address: int, size: int) -> Optional[bytes]:
        """
        Read memory using /proc/pid/mem (requires sudo).
        
        Args:
            address: Memory address to read
            size: Number of bytes to read
            
        Returns:
            Bytes read or None if failed
        """
        if self.pid is None:
            return None
        
        try:
            mem_file = f"/proc/{self.pid}/mem"
            with open(mem_file, 'rb') as f:
                f.seek(address)
                data = f.read(size)
                if len(data) == size:
                    return data
                return None
        except PermissionError:
            print(f"Permission denied reading /proc/{self.pid}/mem. Run with sudo!")
            return None
        except Exception as e:
            print(f"Error reading memory via /proc: {e}")
            return None
    
    def read_float(self, address: int) -> Optional[float]:
        """
        Read a 4-byte float from memory.
        
        Args:
            address: Memory address
            
        Returns:
            Float value or None if failed
        """
        # Try syscall first
        data = self.read_memory(address, 4)
        if data and len(data) == 4:
            return struct.unpack('<f', data)[0]
        
        # Fallback to /proc/pid/mem if syscall fails
        data = self.read_memory_proc(address, 4)
        if data and len(data) == 4:
            return struct.unpack('<f', data)[0]
        
        return None
    
    def read_double(self, address: int) -> Optional[float]:
        """
        Read an 8-byte double from memory.
        
        Args:
            address: Memory address
            
        Returns:
            Double value or None if failed
        """
        data = self.read_memory(address, 8)
        if data and len(data) == 8:
            return struct.unpack('<d', data)[0]
        return None
    
    def read_int(self, address: int) -> Optional[int]:
        """
        Read a 4-byte integer from memory.
        
        Args:
            address: Memory address
            
        Returns:
            Integer value or None if failed
        """
        data = self.read_memory(address, 4)
        if data and len(data) == 4:
            return struct.unpack('<i', data)[0]
        return None
    
    def read_pointer_chain(self, base_address: int, offsets: List[int]) -> Optional[float]:
        """
        Follow a chain of 64-bit pointers to read a float value.
        
        This method properly handles 64-bit pointer dereferencing, which is
        required for reading X and Z coordinates that are stored behind
        pointer chains in Minecraft's memory structure.
        
        Args:
            base_address: Starting base address
            offsets: List of offsets to follow (intermediate are pointer offsets, last is value offset)
            
        Returns:
            Float value at the end of the pointer chain, or None if failed
        """
        if not offsets:
            return None
        
        addr = base_address
        
        # Follow all intermediate pointers (64-bit)
        for offset in offsets[:-1]:
            # Read 64-bit pointer (8 bytes)
            ptr_bytes = self.read_memory(addr + offset, 8)
            if not ptr_bytes or len(ptr_bytes) != 8:
                return None
            # Unpack as unsigned 64-bit integer (little-endian)
            addr = struct.unpack('<Q', ptr_bytes)[0]
            if addr == 0:
                return None
        
        # Read the final float value
        return self.read_float(addr + offsets[-1])

    def read_with_offsets(self, base: int, offsets: List[int]) -> Optional[float]:
        """
        Follow pointer chain to read final value.
        
        Args:
            base: Base address
            offsets: List of offsets to follow
            
        Returns:
            Float value or None if failed
        """
        if not offsets:
            return None
        
        addr = base
        # Follow all intermediate pointers (64-bit)
        for offset in offsets[:-1]:
            # Read 64-bit pointer (8 bytes) - FIX: use 8 bytes for 64-bit pointers
            ptr_bytes = self.read_memory(addr + offset, 8)
            if not ptr_bytes or len(ptr_bytes) != 8:
                return None
            addr = struct.unpack('<Q', ptr_bytes)[0]
            if addr == 0:
                return None
        
        return self.read_float(addr + offsets[-1])

    def _get_pointer_chain(self, base: int, offsets: List[int]) -> Optional[int]:
        """
        Follow pointer chain to get final address.

        Args:
            base: Base address or module name with offset (e.g., "libjvm.so+0x123456")
            offsets: Offset chain

        Returns:
            Final address or None if failed
        """
        # Handle module name with offset (e.g., "libjvm.so+0x123456")
        if isinstance(base, str) and "+" in base:
            try:
                module_name, offset_str = base.split("+")
                offset = int(offset_str, 16)
                base_addr = self._resolve_module_base(module_name)
                if base_addr is None:
                    return None
                base = base_addr + offset
            except ValueError:
                pass  # Not a valid module+offset format, treat as normal base

        addr = base
        for offset in offsets[:-1]:
            # Read 64-bit pointer (8 bytes)
            ptr_bytes = self.read_memory(addr + offset, 8)
            if not ptr_bytes or len(ptr_bytes) != 8:
                return None
            addr = struct.unpack('<Q', ptr_bytes)[0]
            if addr == 0:
                return None
        return addr + offsets[-1] if offsets else addr
    
    def _read_coordinate(self, player_base: int, coord_config: Any) -> Optional[float]:
        """
        Read a coordinate value, handling both direct addresses and pointer chains.
        
        Args:
            player_base: Player base address
            coord_config: Coordinate configuration (string offset or dict with type/chain)
            
        Returns:
            Coordinate value or None if failed
        """
        if isinstance(coord_config, str):
            # Legacy format: simple offset string
            return self.read_with_offsets(player_base, self._parse_offset_chain(coord_config))
        elif isinstance(coord_config, dict):
            coord_type = coord_config.get("type", "pointer_chain")
            
            if coord_type == "direct":
                # Direct address read
                address = int(coord_config.get("address", "0x0"), 16)
                return self.read_float(address)
            elif coord_type == "pointer_chain":
                # Pointer chain
                chain = coord_config.get("chain", [])
                if not chain:
                    return None
                # Convert hex strings to integers
                chain_ints = [int(c, 16) if isinstance(c, str) else c for c in chain]
                return self.read_pointer_chain(player_base, chain_ints)
        
        return None

    def get_player_state(self) -> Optional[PlayerState]:
        """
        Read player state from memory.
        
        Returns:
            PlayerState or None if failed
        """
        if self.base_address is None:
            return None
        
        try:
            # Get player base pointer
            player_offsets = self.offsets.get("player", {})
            player_base = self._get_pointer_chain(
                self.base_address,
                self._parse_offset_chain(player_offsets.get("base_offset", "0x0"))
            )
            
            if player_base is None:
                return None
            
            # Read position - handle both new pointer chain format and legacy format
            pos_offsets = player_offsets.get("position", {})
            x = self._read_coordinate(player_base, pos_offsets.get("x", "0x0"))
            y = self._read_coordinate(player_base, pos_offsets.get("y", "0x0"))
            z = self._read_coordinate(player_base, pos_offsets.get("z", "0x0"))
            
            # Read velocity
            vel_offsets = player_offsets.get("velocity", {})
            vx = self.read_with_offsets(player_base, self._parse_offset_chain(vel_offsets.get("x", "0x0")))
            vy = self.read_with_offsets(player_base, self._parse_offset_chain(vel_offsets.get("y", "0x0")))
            vz = self.read_with_offsets(player_base, self._parse_offset_chain(vel_offsets.get("z", "0x0")))
            
            # Read rotation
            rot_offsets = player_offsets.get("rotation", {})
            yaw = self.read_with_offsets(player_base, self._parse_offset_chain(rot_offsets.get("yaw", "0x0")))
            pitch = self.read_with_offsets(player_base, self._parse_offset_chain(rot_offsets.get("pitch", "0x0")))
            
            # Read health, hunger, saturation
            health = self.read_with_offsets(player_base, self._parse_offset_chain(player_offsets.get("health", "0x0")))
            hunger = self.read_with_offsets(player_base, self._parse_offset_chain(player_offsets.get("hunger", "0x0")))
            saturation = self.read_with_offsets(player_base, self._parse_offset_chain(player_offsets.get("saturation", "0x0")))
            
            # Read experience
            exp_offsets = player_offsets.get("experience", {})
            exp_level = self.read_with_offsets(player_base, self._parse_offset_chain(exp_offsets.get("level", "0x0")))
            exp_progress = self.read_with_offsets(player_base, self._parse_offset_chain(exp_offsets.get("progress", "0x0")))
            
            # Read flags
            flag_offsets = player_offsets.get("flags", {})
            is_on_ground = self._read_flag(player_base, flag_offsets.get("is_on_ground", "0x0"))
            is_in_water = self._read_flag(player_base, flag_offsets.get("is_in_water", "0x0"))
            is_in_lava = self._read_flag(player_base, flag_offsets.get("is_in_lava", "0x0"))
            is_sleeping = self._read_flag(player_base, flag_offsets.get("is_sleeping", "0x0"))
            
            # Create player state
            return PlayerState(
                position={"x": x or 0.0, "y": y or 0.0, "z": z or 0.0},
                velocity={"x": vx or 0.0, "y": vy or 0.0, "z": vz or 0.0},
                health=health or 20.0,
                hunger=hunger or 20.0,
                saturation=saturation or 5.0,
                experience_level=int(exp_level or 0),
                experience_progress=exp_progress or 0.0,
                yaw=yaw or 0.0,
                pitch=pitch or 0.0,
                is_on_ground=is_on_ground,
                is_in_water=is_in_water,
                is_in_lava=is_in_lava,
                is_sleeping=is_sleeping,
                dimension="overworld"  # TODO: Read dimension from memory
            )
            
        except Exception as e:
            print(f"Error reading player state: {e}")
            return None
    
    def get_inventory_state(self) -> Optional[InventoryState]:
        """
        Read inventory state from memory.
        
        Returns:
            InventoryState or None if failed
        """
        if self.base_address is None:
            return None
        
        try:
            # Get inventory base pointer
            inv_offsets = self.offsets.get("inventory", {})
            inv_base = self._get_pointer_chain(
                self.base_address,
                self._parse_offset_chain(inv_offsets.get("base_offset", "0x0"))
            )
            
            if inv_base is None:
                return None
            
            # Read selected slot
            selected_slot = self.read_with_offsets(inv_base, self._parse_offset_chain(inv_offsets.get("selected_slot", "0x0")))
            selected_slot = int(selected_slot or 0)
            
            # Read items
            items = []
            slot_offsets = inv_offsets.get("slots", {})
            item_struct = inv_offsets.get("item_structure", {})
            
            # Read hotbar (slots 0-8)
            hotbar_start = self._parse_offset_chain(slot_offsets.get("hotbar_start", "0x0"))
            for i in range(9):
                item = self._read_item(inv_base, hotbar_start, i, item_struct)
                if item:
                    items.append(item)
            
            # Read main inventory (slots 9-35)
            inv_start = self._parse_offset_chain(slot_offsets.get("inventory_start", "0x0"))
            for i in range(27):
                item = self._read_item(inv_base, inv_start, 9 + i, item_struct)
                if item:
                    items.append(item)
            
            # Create inventory state
            return InventoryState(
                selected_slot=selected_slot,
                items=items,
                armor={"head": None, "chest": None, "legs": None, "feet": None},
                offhand=None
            )
            
        except Exception as e:
            print(f"Error reading inventory state: {e}")
            return None
    
    def get_world_state(self) -> Optional[WorldState]:
        """
        Read world state from memory.
        
        Returns:
            WorldState or None if failed
        """
        if self.base_address is None:
            return None
        
        try:
            # Get world base pointer
            world_offsets = self.offsets.get("world", {})
            world_base = self._get_pointer_chain(
                self.base_address,
                self._parse_offset_chain(world_offsets.get("base_offset", "0x0"))
            )
            
            if world_base is None:
                return None
            
            # Read time of day
            time_of_day = self.read_with_offsets(world_base, self._parse_offset_chain(world_offsets.get("time_of_day", "0x0")))
            
            # Read difficulty
            difficulty_val = self.read_with_offsets(world_base, self._parse_offset_chain(world_offsets.get("difficulty", "0x0")))
            difficulty_map = {0: "peaceful", 1: "easy", 2: "normal", 3: "hard"}
            difficulty = difficulty_map.get(int(difficulty_val or 2), "normal")
            
            # Read game mode
            game_mode_val = self.read_with_offsets(world_base, self._parse_offset_chain(world_offsets.get("game_mode", "0x0")))
            game_mode_map = {0: "survival", 1: "creative", 2: "adventure", 3: "spectator"}
            game_mode = game_mode_map.get(int(game_mode_val or 0), "survival")
            
            # Read spawn point
            spawn_offsets = world_offsets.get("spawn_point", {})
            spawn_x = self.read_with_offsets(world_base, self._parse_offset_chain(spawn_offsets.get("x", "0x0")))
            spawn_y = self.read_with_offsets(world_base, self._parse_offset_chain(spawn_offsets.get("y", "0x0")))
            spawn_z = self.read_with_offsets(world_base, self._parse_offset_chain(spawn_offsets.get("z", "0x0")))
            
            # Create world state
            return WorldState(
                time_of_day=int(time_of_day or 0) % 24000,
                day_count=0,  # TODO: Read day count
                is_raining=False,  # TODO: Read rain state
                is_thundering=False,  # TODO: Read thunder state
                difficulty=difficulty,
                game_mode=game_mode,
                seed=0,  # TODO: Read seed
                spawn_point=Position(x=spawn_x or 0.0, y=spawn_y or 64.0, z=spawn_z or 0.0),
                looking_at=None,  # TODO: Read looking at
                nearby_entities=[],  # TODO: Read entities
                nearby_blocks=[]  # TODO: Read blocks
            )
            
        except Exception as e:
            print(f"Error reading world state: {e}")
            return None
    
    def get_game_state(self) -> Optional[GameState]:
        """
        Read complete game state from memory.
        
        Returns:
            GameState or None if failed
        """
        import time
        
        player = self.get_player_state()
        inventory = self.get_inventory_state()
        world = self.get_world_state()
        
        if player is None or inventory is None or world is None:
            return None
        
        return GameState(
            player=player,
            inventory=inventory,
            world=world,
            timestamp=time.time()
        )
    
    
    def _parse_offset_chain(self, offset_str: str) -> List[int]:
        """
        Parse offset string into list of integers.
        
        Args:
            offset_str: Offset string (e.g., "0x28, 0x08" or "0x28")
            
        Returns:
            List of offset integers
        """
        if isinstance(offset_str, str):
            # Handle comma-separated offsets
            if "," in offset_str:
                return [int(x.strip(), 16) for x in offset_str.split(",")]
            # Handle single offset
            return [int(offset_str, 16)]
        return [0]
    
    def _read_flag(self, base: int, offset_str: str) -> bool:
        """
        Read a boolean flag from memory.
        
        Args:
            base: Base address
            offset_str: Offset string
            
        Returns:
            Boolean value
        """
        offsets = self._parse_offset_chain(offset_str)
        value = self.read_with_offsets(base, offsets)
        return bool(value and value != 0.0)
    
    def _read_item(self, inv_base: int, slot_offsets: List[int], slot: int, item_struct: Dict) -> Optional[Dict[str, Any]]:
        """
        Read item data from inventory slot.
        
        Args:
            inv_base: Inventory base address
            slot_offsets: Slot offset chain
            slot: Slot number
            item_struct: Item structure offsets
            
        Returns:
            Item dictionary or None if failed
        """
        try:
            # Calculate slot address
            slot_addr = self._get_pointer_chain(inv_base, slot_offsets)
            if slot_addr is None:
                return None
            
            # Read item ID
            item_id_offset = int(item_struct.get("item_id", "0x0"), 16)
            item_id = self.read_int(slot_addr + item_id_offset)
            
            # Read count
            count_offset = int(item_struct.get("count", "0x0"), 16)
            count = self.read_int(slot_addr + count_offset)
            
            # Read damage
            damage_offset = int(item_struct.get("damage", "0x0"), 16)
            damage = self.read_int(slot_addr + damage_offset)
            
            if item_id is None or count is None:
                return None
            
            return {
                "slot": slot,
                "item_id": f"minecraft:item_{item_id}",  # TODO: Map ID to name
                "count": count,
                "damage": damage or 0,
                "nbt": {}
            }
            
        except Exception as e:
            print(f"Error reading item at slot {slot}: {e}")
            return None
