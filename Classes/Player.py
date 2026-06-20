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
        
        grid[self.x][self.y] = -1

        self.x = n_x
        self.y = n_y

        return self.add_to_grid(grid, GRID_X, GRID_Y)
    
    def take_from_chest(self, grid: List[List], dir: str, amount: int):
        GRID_X = len(grid)
        GRID_Y = len(grid[0])

        c_x, c_y = get_pos_from_dir(dir, self.x, self.y, GRID_X, GRID_Y)
        obj = grid[c_x][c_y]

        if obj != -1 and obj.type == "Chest":
            pass
        else:
            return False, "Nothing there or it's not a Chest"
        
        if obj.filled_size < amount:
            return False, "Chest doesn't have that amount of your desired object"

        if obj.type == "Chest":
            return False, "Cannot color a Chest"

        if self.Inventory.Add_to_Inventory(obj.heldObjectType, amount):
            return obj.decreaseAmount(amount)
        else:
            return False, "amount is above your capacity"
        
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
            return False, "Given color isn't in the allowed colors"

        obj.color = color

        return True


        








