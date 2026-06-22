def in_boundaries(x: int, y: int, GRID_X: int, GRID_Y: int):
    return 0 <= x < GRID_X and 0 <= y < GRID_Y

def get_pos_from_dir(dir: str, x: int, y: int, rows: int, cols: int):
    if dir == "Upward":
        n_x, n_y = x - 1, y
    elif dir == "Downward":
        n_x, n_y = x + 1, y
    elif dir == "Rightward":
        n_x, n_y = x, y + 1
    elif dir == "Leftward":
        n_x, n_y = x, y - 1
    else:
        return -1, -1
 
    if not in_boundaries(n_x, n_y, rows, cols):
        return -1, -1
 
    return n_x, n_y
 
 
ALLOWED_COLORS = ["red", "green", "blue", "yellow", "light_grey", "white", "black", "magenta", "cyan"]
DIRECTION_ENUM = ["Upward", "Downward", "Leftward", "Rightward"]
OBJECT_TYPES = ["Block", "Door"]
VALID_TYPES = {
    "block": "Block",
    "door": "Door"
}