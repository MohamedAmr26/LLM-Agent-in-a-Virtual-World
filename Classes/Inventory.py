class Inventory:
    def __init__(self, max_size):
        self.max_size = max_size
        self.actual_size = 0
    
    def is_full(self):
        return self.actual_size == self.max_size
    def is_empty(self):
        return self.actual_size == 0

    def Add_to_Inventory(self, objType: str, amount: int):
        if self.is_full():
            return False, "Inventory is full"
        # Check whether an attribute with this name exists and is an integer counter
        if not hasattr(self, objType) or not isinstance(getattr(self, objType), int):
            setattr(self, objType, 0)
 
        current_count = getattr(self, objType)
 
        # Calculate how many items we can actually add
        space_left = self.max_size - self.actual_size
        if space_left <= 0:
            return False, "Inventory is full"
 
        to_add = min(amount, space_left)
 
        # Update the attribute (integer counter) and the overall actual size
        setattr(self, objType, current_count + to_add)
        self.actual_size += to_add
 
        if to_add < amount:
            return False, f"Only added {to_add} items; inventory reached capacity"
        return True, f"Added {to_add} items to {objType}"
            
    def DecreaseFromType(self, objType: str, amount: int):
        # Validate amount
        if amount <= 0:
            return False, "Amount must be positive"
 
        # Check whether an attribute with this name exists and is an integer counter
        if not hasattr(self, objType) or not isinstance(getattr(self, objType), int):
            return False, f"No integer named '{objType}' in inventory"
 
        current_count = getattr(self, objType)
 
        if current_count <= 0:
            return False, f"No {objType} items to remove"
 
        to_remove = min(amount, current_count)
 
        # Update counters
        setattr(self, objType, current_count - to_remove)
 
        # Decrease overall actual_size but never below 0
        self.actual_size = max(0, self.actual_size - to_remove)
 
        if to_remove < amount:
            return False, f"Only removed {to_remove} items; only {current_count} were available"
        return True, f"Removed {to_remove} items from {objType}"

    def get_data(self):
        return vars(self)
    
    def get_inventory_list(self):
        """Returns a list like ['wood: 3', 'stone: 5'] for tool-result reporting."""
        return [f"{k}: {v}" for k, v in vars(self).items()
                if k not in ("max_size", "actual_size") and isinstance(v, int)]
 
