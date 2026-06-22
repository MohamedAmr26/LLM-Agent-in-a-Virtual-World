from typing import List
from GameObject import Object
from Inventory import Inventory
from Utils import get_pos_from_dir, allowed_colors

class Player(Object):
    def __init__(self, x: int, y: int, inventorySize: int) -> None:
        self.color = "green"
        self.symbol = "&"
        self.type = "Player"
        self.Inventory = Inventory(inventorySize)
        super().__init__(x, y, self.type, self.symbol, self.color)
        
    def get_current_position(self):
        return self.x, self.y
    
    def move(self, dir: str, grid: List[List]):
        GRID_X = len(grid)
        GRID_Y = len(grid[0])
        n_x, n_y = get_pos_from_dir(dir, self.x, self.y, GRID_X, GRID_Y)
 
        if (n_x, n_y) == (-1, -1):
            return False, "Out of boundaries"
 
        if grid[n_x][n_y] != -1:
            return False, "Something is blocking that direction"
 
        # Only vacate the old cell once we know the move will succeed
        old_x, old_y = self.x, self.y
        grid[old_x][old_y] = -1
 
        self.x = n_x
        self.y = n_y
 
        ok, msg = self.add_to_grid(grid, GRID_X, GRID_Y)
        if not ok:
            # Roll back -- shouldn't normally happen since we just checked
            # the cell was empty, but keep state consistent if it ever does.
            self.x, self.y = old_x, old_y
            grid[old_x][old_y] = self
            return ok, msg
 
        return True, f"Moved {dir} to ({self.x}, {self.y})"
    
    def take_from_chest(self, grid: List[List], dir: str, amount: int):
        GRID_X = len(grid)
        GRID_Y = len(grid[0])
 
        c_x, c_y = get_pos_from_dir(dir, self.x, self.y, GRID_X, GRID_Y)
 
        if (c_x, c_y) == (-1, -1):
            return False, "Out of boundaries"
 
        obj = grid[c_x][c_y]
 
        if obj == -1 or obj.type != "Chest":
            return False, "Nothing there or it's not a Chest"
 
        if amount <= 0:
            return False, "Amount must be positive"
 
        if obj.amount < amount:
            return False, "Chest doesn't have that amount of your desired object"
 
        added_ok, added_msg = self.Inventory.Add_to_Inventory(obj.heldObjectType if hasattr(obj, "heldObjectType") else obj.heldType, amount)
 
        if not added_ok:
            return False, added_msg
 
        return obj.decreaseAmount(amount)
 
    def build_object(self, grid: List[List], objType: str, dir: str) -> tuple[bool, str]:
        GRID_X = len(grid)
        GRID_Y = len(grid[0])
        n_x, n_y = get_pos_from_dir(dir, self.x, self.y, GRID_X, GRID_Y)
 
        if (n_x, n_y) == (-1, -1):
            return False, "Out of boundaries"
 
        if grid[n_x][n_y] != -1:
            return False, "There's something already there"
 
        res, msg = self.Inventory.DecreaseFromType(objType, 1)
 
        if not res:
            return res, msg
 
        obj = Object.create(objType, n_x, n_y)
        return obj.add_to_grid(grid, GRID_X, GRID_Y)
        
    def color_block(self, grid: List[List], dir: str, color: str):
        GRID_X = len(grid)
        GRID_Y = len(grid[0])
        n_x, n_y = get_pos_from_dir(dir, self.x, self.y, GRID_X, GRID_Y)
 
        if (n_x, n_y) == (-1, -1):
            return False, "Out of boundaries"
 
        obj = grid[n_x][n_y]
 
        if obj == -1 or obj.type != "Block":
            return False, "Empty place or isn't a Block"
 
        if color not in allowed_colors:
            return False, f"Given color isn't in the allowed colors: {allowed_colors}"
 
        obj.color = color
 
        return True, f"Block at ({n_x}, {n_y}) colored {color}"
    def trigger_door(self, grid: List[List], dir: str):
        GRID_X = len(grid)
        GRID_Y = len(grid[0])
        n_x, n_y = get_pos_from_dir(dir, self.x, self.y, GRID_X, GRID_Y)
 
        if (n_x, n_y) == (-1, -1):
            return False, "Out of boundaries"
 
        obj = grid[n_x][n_y]
 
        if obj == -1 or obj.type != "Door":
            return False, "Empty place or isn't a Door"
 
        return obj.trigger_door()


        








