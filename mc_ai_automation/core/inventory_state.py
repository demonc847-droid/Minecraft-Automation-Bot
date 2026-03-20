"""
Inventory State Module
=====================

This module defines the InventoryState class for tracking inventory contents
including items, armor, and offhand equipment.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class ItemStack:
    """
    Represents a stack of items in a single inventory slot.
    
    Attributes:
        item_id: Item identifier (e.g., "minecraft:diamond_sword")
        count: Number of items in the stack
        damage: Damage value for tools/weapons
        nbt: Additional NBT data for the item
    """
    item_id: str = ""
    count: int = 0
    damage: int = 0
    nbt: Dict[str, Any] = field(default_factory=dict)
    
    def is_empty(self) -> bool:
        """Check if this item stack is empty."""
        return self.count <= 0 or self.item_id == ""
    
    def to_dict(self) -> dict:
        """Convert item stack to dictionary."""
        return {
            "item_id": self.item_id,
            "count": self.count,
            "damage": self.damage,
            "nbt": self.nbt.copy()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ItemStack':
        """Create ItemStack from dictionary."""
        return cls(
            item_id=data.get("item_id", ""),
            count=data.get("count", 0),
            damage=data.get("damage", 0),
            nbt=data.get("nbt", {})
        )


@dataclass
class InventoryState:
    """
    Represents the current state of the player's inventory.
    
    Attributes:
        selected_slot: Currently selected hotbar slot (0-8)
        items: List of all inventory items with their slot information
        armor: Armor slots (head, chest, legs, feet)
        offhand: Offhand item
    """
    
    selected_slot: int = 0
    items: List[Dict[str, Any]] = field(default_factory=list)
    armor: Dict[str, Optional[ItemStack]] = field(default_factory=lambda: {
        "head": None,
        "chest": None,
        "legs": None,
        "feet": None
    })
    offhand: Optional[ItemStack] = None
    
    def __post_init__(self):
        """Validate inventory state after initialization."""
        self._validate_selected_slot()
    
    def _validate_selected_slot(self):
        """Validate selected slot is within valid range."""
        if not 0 <= self.selected_slot <= 8:
            raise ValueError(f"Selected slot must be between 0 and 8, got {self.selected_slot}")
    
    def get_item(self, slot: int) -> Optional[Dict[str, Any]]:
        """
        Get item at specified slot.
        
        Args:
            slot: Slot number (0-35 for main inventory, 36-39 for armor, 40 for offhand)
            
        Returns:
            Item dictionary if found, None otherwise
        """
        for item in self.items:
            if item.get("slot") == slot:
                return item
        return None
    
    def set_item(self, slot: int, item: Optional[Dict[str, Any]]):
        """
        Set item at specified slot.
        
        Args:
            slot: Slot number
            item: Item dictionary or None to clear slot
        """
        # Remove existing item at slot
        self.items = [i for i in self.items if i.get("slot") != slot]
        
        # Add new item if provided
        if item is not None:
            item["slot"] = slot
            self.items.append(item)
    
    def find_item(self, item_id: str) -> Optional[int]:
        """
        Find first slot containing specified item.
        
        Args:
            item_id: Item identifier to search for
            
        Returns:
            Slot number if found, None otherwise
        """
        for item in self.items:
            if item.get("item_id") == item_id and item.get("count", 0) > 0:
                return item.get("slot")
        return None
    
    def count_item(self, item_id: str) -> int:
        """
        Count total number of specified item across all slots.
        
        Args:
            item_id: Item identifier to count
            
        Returns:
            Total count of item
        """
        total = 0
        for item in self.items:
            if item.get("item_id") == item_id:
                total += item.get("count", 0)
        return total
    
    def has_item(self, item_id: str) -> bool:
        """
        Check if inventory contains specified item.
        
        Args:
            item_id: Item identifier to check
            
        Returns:
            True if item is found
        """
        return self.count_item(item_id) > 0
    
    def get_hotbar_items(self) -> List[Dict[str, Any]]:
        """
        Get items in hotbar slots (0-8).
        
        Returns:
            List of hotbar items
        """
        return [item for item in self.items if 0 <= item.get("slot", -1) <= 8]
    
    def get_main_inventory_items(self) -> List[Dict[str, Any]]:
        """
        Get items in main inventory slots (9-35).
        
        Returns:
            List of main inventory items
        """
        return [item for item in self.items if 9 <= item.get("slot", -1) <= 35]
    
    def get_selected_item(self) -> Optional[Dict[str, Any]]:
        """
        Get currently selected item from hotbar.
        
        Returns:
            Selected item dictionary or None
        """
        return self.get_item(self.selected_slot)
    
    def is_slot_empty(self, slot: int) -> bool:
        """
        Check if specified slot is empty.
        
        Args:
            slot: Slot number to check
            
        Returns:
            True if slot is empty
        """
        item = self.get_item(slot)
        return item is None or item.get("count", 0) <= 0
    
    def get_armor_piece(self, slot: str) -> Optional[ItemStack]:
        """
        Get armor piece at specified slot.
        
        Args:
            slot: Armor slot ("head", "chest", "legs", "feet")
            
        Returns:
            ItemStack if found, None otherwise
        """
        return self.armor.get(slot)
    
    def set_armor_piece(self, slot: str, item: Optional[ItemStack]):
        """
        Set armor piece at specified slot.
        
        Args:
            slot: Armor slot
            item: ItemStack or None to clear slot
        """
        if slot not in self.armor:
            raise ValueError(f"Invalid armor slot: {slot}")
        self.armor[slot] = item
    
    def has_armor(self) -> bool:
        """
        Check if player is wearing any armor.
        
        Returns:
            True if at least one armor piece is equipped
        """
        return any(piece is not None for piece in self.armor.values())
    
    def get_empty_slots(self) -> List[int]:
        """
        Get list of empty inventory slots.
        
        Returns:
            List of empty slot numbers
        """
        occupied_slots = {item.get("slot") for item in self.items if item.get("count", 0) > 0}
        return [slot for slot in range(36) if slot not in occupied_slots]
    
    def get_first_empty_slot(self) -> Optional[int]:
        """
        Get first empty inventory slot.
        
        Returns:
            First empty slot number or None if inventory is full
        """
        empty_slots = self.get_empty_slots()
        return empty_slots[0] if empty_slots else None
    
    def is_inventory_full(self) -> bool:
        """
        Check if inventory is full.
        
        Returns:
            True if no empty slots available
        """
        return len(self.get_empty_slots()) == 0
    
    def to_dict(self) -> dict:
        """
        Convert inventory state to dictionary format.
        
        Returns:
            Dictionary representation of inventory state
        """
        return {
            "selected_slot": self.selected_slot,
            "items": [item.copy() for item in self.items],
            "armor": {
                slot: piece.to_dict() if piece else None 
                for slot, piece in self.armor.items()
            },
            "offhand": self.offhand.to_dict() if self.offhand else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InventoryState':
        """
        Create InventoryState from dictionary.
        
        Args:
            data: Dictionary containing inventory state data
            
        Returns:
            InventoryState instance
        """
        armor = {}
        for slot, piece in data.get("armor", {}).items():
            armor[slot] = ItemStack.from_dict(piece) if piece else None
        
        offhand_data = data.get("offhand")
        offhand = ItemStack.from_dict(offhand_data) if offhand_data else None
        
        return cls(
            selected_slot=data.get("selected_slot", 0),
            items=data.get("items", []),
            armor=armor,
            offhand=offhand
        )