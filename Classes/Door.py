from GameObject import Object

class Door(Object):
    def __init__(self, x: int, y: int) -> None:
        self.color = "red"
        self.symbol = "#"
        self.state = True
        self.type = "Door"
        super().__init__(x, y, self.type, self.symbol, self.color)

    def trigger_door(self):
        if self.state == True:
            self.symbol = " "
            self.state = False
        else:
            self.state = True
            self.symbol = "#"