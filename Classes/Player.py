from typing import List
from GameObject import Object
from Inventory import Inventory
from Utils import get_pos_from_dir, ALLOWED_COLORS, VALID_TYPES, DIRECTION_ENUM, in_boundaries

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
 
        if dir not in DIRECTION_ENUM:
            return False, "Directions are [Upward, Downward, Leftward, Rightward], Case Sensitive"

        if (n_x, n_y) == (-1, -1):
            return False, "Out of boundaries"

        if grid[n_x][n_y] != -1 and isinstance(grid[n_x][n_y], list):
            for obj in grid[n_x][n_y]:
                if obj.type == "Door" and obj.state == True:
                    return False, "There's a closed door here"
    
        if grid[n_x][n_y] != -1 and not isinstance(grid[n_x][n_y], list):
            return False, "Something is blocking that direction"
 
        old_x, old_y = self.x, self.y
        self.remove_from_grid(grid, GRID_X, GRID_Y)
 
        self.x = n_x
        self.y = n_y
 
        ok, msg = self.add_to_grid(grid, GRID_X, GRID_Y)
        if not ok:
            self.x, self.y = old_x, old_y

            try:
                self.add_to_grid(grid, GRID_X, GRID_Y)
            except Exception as e:
                msg = f"{msg}, {e}"

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
 
        if obj.type != "Chest":
            return False, "That's not a chest"
    
        added_ok, added_msg = self.Inventory.Add_to_Inventory(obj.heldType, amount)
 
        if not added_ok:
            return False, added_msg
 
        ok, msg = obj.decreaseAmount(added_msg)
        if not ok:
            return False, msg
        return True, f"Took {amount} {obj.heldType}(s) from chest" 

    def build_object(self, grid: List[List], objType: str, dir: str) -> tuple[bool, str]:
        objType = VALID_TYPES.get(
            objType.lower(),
            objType
        )
        GRID_X = len(grid)
        GRID_Y = len(grid[0])
        n_x, n_y = get_pos_from_dir(dir, self.x, self.y, GRID_X, GRID_Y)
 
        if (n_x, n_y) == (-1, -1):
            return False, "Out of boundaries"
 
        if grid[n_x][n_y] != -1:
            return False, "There's something already there"
 
        if self.Inventory.check_inventory_obj_amount(objType) < 1:
            return False, f"Not enough {objType} for building, You have zero of it"

        res, msg = False, "Unknown happened"

        try:
            res, msg = self.Inventory.DecreaseFromType(objType, 1)
            
            if not res:
                return res, msg
            
            obj = Object.create(objType, n_x, n_y)
            res, msg = obj.add_to_grid(grid, GRID_X, GRID_Y)
        except Exception as e:
            return False, f"an issue occurred {e}"
        return res, f"Object successfully built at {n_x},{n_y}"
                
    def color_block(self, grid: List[List], dir: str, color: str):
        GRID_X = len(grid)
        GRID_Y = len(grid[0])
        n_x, n_y = get_pos_from_dir(dir, self.x, self.y, GRID_X, GRID_Y)
 
        if (n_x, n_y) == (-1, -1):
            return False, "Out of boundaries"
 
        obj = grid[n_x][n_y]
 
        if obj == -1 or obj.type != "Block":
            return False, "Empty place or isn't a Block"
 
        if color not in ALLOWED_COLORS:
            return False, f"Given color isn't in the allowed colors: {ALLOWED_COLORS}"
 
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

    def add_to_grid(self, grid: List[List], GRID_X: int, GRID_Y: int):
        if not in_boundaries(self.x, self.y, GRID_X, GRID_Y):
            return False, "Out of boundaries"

        if grid[self.x][self.y] != -1 and not isinstance(grid[self.x][self.y], list):
            return False, "Something is already in that position"

        if not isinstance(grid[self.x][self.y], list):
            grid[self.x][self.y] = self
        else:
            grid[self.x][self.y].append(self)
        
        return True, f"{self.type} placed at ({self.x}, {self.y})"
    
    def remove_from_grid(self, grid: List[List], GRID_X: int, GRID_Y: int):
        if not in_boundaries(self.x, self.y, GRID_X, GRID_Y):
            return False, "Out of boundaries"
        
        if isinstance(grid[self.x][self.y], list):
            grid[self.x][self.y].pop()
        else:
            grid[self.x][self.y] = -1
        
        return True, f"{self.type} got removed from the grid"


        








