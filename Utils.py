def in_boundaries(x: int, y: int, GRID_X: int, GRID_Y: int):
    return 0 <= x < GRID_X and 0 <= y < GRID_Y

def get_pos_from_dir(dir: str, x, y, rows, cols):
    res = -1, -1
    if dir == "Upward":
        res = x+1, y
    elif dir == "Downward":
        res =  x-1, y
    elif dir == "Rightward":
        res =  x, y+1
    elif dir == "Leftward":
        res =  x, y-1

    if in_boundaries(res[0], res[1], rows, cols):
        return -1, -1

    return res

allowed_colors = []