from GameObject import Object

class Chest(Object):
    def __init__(self, x: int, y: int, heldType: str, amount: int) -> None:
        self.color = "red"
        self.symbol = "*"
        self.type = "Chest"
        self.amount = amount
        self.heldType = heldType
        super().__init__(x, y, self.type, self.symbol, self.color)
    
    def decreaseAmount(self, amt):
        if self.amount - amt < 0:
            return False, "Given amount is higher than the total amount"
        self.amount -= amt
        return True
    def addAmount(self, amt):
        self.amount += amt
        return True
    def changeHeldType(self, heldType: str):
        self.heldType = heldType
        return True
    
    def getInfo(self):
        return f"Chest holds {self.heldType} with an amount of {self.amount}"


