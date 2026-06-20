"""

Main tools for LLM

get_player_position() -> (x, y)
move_player(dir: str) -> (x, y)
take_from_chest(chest_id: int, amount: int) -> bool
build_item(slot_number: int, dir: str) -> bool
color_block(dir: str, new_color: str) -> bool

whats_in_position(x: int, y: int) -> str
get_all_grid_data() -> List[List]

get_inventory_data() -> List[str]

"""

"""

Main objects in the simulation

* Door
* Block
* Chest
* Inventory

"""

"""
Inputs

* Grid Size
* Inventory Slots number
* Number of chests and their content

"""

"""
Outputs

* Log of the behaviour in an external file
* Looping view while the behaviour is happening

"""
from termcolor import colored
from Utils import in_boundaries
from google import genai
from google.genai import types
from Classes.Player import Player
from Classes.Chest import Chest

##########################

# Game setup
GRID_SIZE = input("Enter Grid size: ").split("*")
GRID_X, GRID_Y = int(GRID_SIZE[0]), int(GRID_SIZE[1])
grid = [[-1]*GRID_Y for _ in range(GRID_X)]

inventorySize = int(input("Enter inventory size: "))

Chests_size = 0
Chests = []

Chests_size = int(input("Enter number of chests: "))

for i in range(Chests_size):
    print(f"\n--- Chest {i + 1} ---")
    x = int(input("Enter x position: "))
    y = int(input("Enter y position: "))
    heldType = input("Enter held item type: ")
    amount = int(input("Enter amount: "))

    chest = Chest(x, y, heldType, amount)
    chest.add_to_grid(grid, GRID_X, GRID_Y)
    Chests.append(chest)

plr = Player(0, 0, inventorySize)
plr.add_to_grid(grid, GRID_X, GRID_Y)

def render():
    pass

render()

##########################

def whats_in_position(x: int, y: int):
    if not in_boundaries(x, y, GRID_X, GRID_Y):
        return False, "Out of boundaries"
    
    obj = grid[x][y]

    if obj == -1:
        return True, "empty"
    elif not isinstance(obj, int):
        return True, obj.getInfo()
    return False, "something wrong has happened"

def get_all_grid():
    res = ""
    for x in range(GRID_X):
        row = []
        for y in range(GRID_Y):
            obj = grid[x][y]
            if obj == -1:
                row.append("~")
            elif not isinstance(obj, int):
                try:
                    info = obj.type
                except Exception:
                    info = "obj"
                row.append(info)
            else:
                row.append("?")
        res += " ".join(row) + "\n"
    return res


client = genai.Client()

model = "gemini-2.5-flash-live-preview"

# function definitions
move = {"name": "move"}
take_from_chest = {"name": "take_from_chest"}
build_object = {"name": "build_object"}
color_block = {"name": "color_block"}
get_inventory_data = {"name": "get_data"}
trigger_door = {"name": "trigger_door"}
whats_in_position_f = {"name": "whats_in_position"}
get_all_grid_f = {"name": "get_all_grid"}


