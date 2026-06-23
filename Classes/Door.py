from typing import List
from GameObject import Object
from Utils import in_boundaries

class Door(Object):
    def __init__(self, x: int, y: int) -> None:
        self.color = "red"
        self.symbol = "#"
        self.state = True
        self.type = "Door"
        super().__init__(x, y, self.type, self.symbol, self.color)

    def trigger_door(self):
        if self.state:
            self.symbol = " "
            self.state = False
            return True, "Door opened"
        else:
            self.state = True
            self.symbol = "#"
            return True, "Door closed"
        
    def add_to_grid(self, grid: List[List], GRID_X: int, GRID_Y: int):
        if not in_boundaries(self.x, self.y, GRID_X, GRID_Y):
            return False, "Out of boundaries"
 
        if grid[self.x][self.y] != -1:
            return False, "Something is already in that position"
 
        grid[self.x][self.y] = [self]
        return True, f"{self.type} placed at ({self.x}, {self.y})"

    def remove_from_grid(self, grid: List[List], GRID_X: int, GRID_Y: int):
        if not in_boundaries(self.x, self.y, GRID_X, GRID_Y):
            return False, "Out of boundaries"
        
        ls = grid[self.x][self.y]

        if len(ls) == 2:
            plr = ls[1]

            if not plr.type == "Player":
                return False, "Unexpected occurred, Second list element should be a Player"
            
            grid[self.x][self.y] = plr
        else:
            grid[self.x][self.y] = -1
        
        return True, "Door got removed from the grid"