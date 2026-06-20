from typing import List
from termcolor import colored
from Utils import in_boundaries

class Object:
    registry = {}
    
    def __init__(self, x: int, y: int, type: str, symbol: str, color: str) -> None:
        self.x = x
        self.y = y
        self.type = type
        self.symbol = symbol
        self.color = color

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Object.registry[cls.__name__] = cls

    def add_to_grid(self, grid: List[List], GRID_X: int, GRID_Y: int):
        if not in_boundaries(self.x, self.y, GRID_X, GRID_Y):
            return False, "Out of boundaries"
 
        if grid[self.x][self.y] != -1:
            return False, "Something is already in that position"
 
        grid[self.x][self.y] = self
        return True, f"{self.type} placed at ({self.x}, {self.y})"

    @classmethod
    def create(cls, type_name: str, *args, **kwargs):
        target_cls = cls.registry.get(type_name)
        if target_cls is None:
            raise ValueError(f"Unknown GameObject type: {type_name}")
        return target_cls(*args, **kwargs)

    def getInfo(self):
        return f"Game object with type: {self.type}, color: {self.color}, and symbol: {self.symbol}"