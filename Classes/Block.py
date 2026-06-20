from GameObject import Object

class Block(Object):
    def __init__(self, x: int, y: int) -> None:
        self.color = "light_grey"
        self.symbol = "."
        self.type = "Block"
        super().__init__(x, y, self.type, self.symbol, self.color)
