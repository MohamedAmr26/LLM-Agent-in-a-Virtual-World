import os
import sys
from datetime import datetime

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_THIS_DIR, "Classes"))

from Utils import in_boundaries, ALLOWED_COLORS, get_pos_from_dir
from Classes.Player import Player
from Classes.Chest import Chest

##########################
# Logging
##########################

LOG_PATH = "behaviour_log.txt"

def log(line: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {line}"
    print(entry)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

##########################
# Tool implementations
##########################

def get_player_position(plr: Player, ):
    x, y = plr.get_current_position()
    ok, msg = True, f"Player is at ({x}, {y})"
    log(f"get_player_position() -> {ok}, {msg}")
    return ok, msg


def move_player(plr: Player, dir: str, grid):
    ok, msg = plr.move(dir, grid)
    log(f"move_player(dir={dir!r}) -> {ok}, {msg}")
    return ok, msg


def take_from_chest(plr: Player, dir: str, amount: int, grid):
    ok, msg = plr.take_from_chest(grid, dir, amount)
    log(f"take_from_chest(dir={dir!r}, amount={amount}) -> {ok}, {msg}")
    return ok, msg


def build_object(plr: Player, objType: str, dir: str, grid):
    ok, msg = plr.build_object(grid, objType, dir)
    log(f"build_object(objType={objType!r}, dir={dir!r}) -> {ok}, {msg}")
    return ok, msg


def color_block(plr: Player, dir: str, new_color: str, grid):
    ok, msg = plr.color_block(grid, dir, new_color)
    log(f"color_block(dir={dir!r}, new_color={new_color!r}) -> {ok}, {msg}")
    return ok, msg


def trigger_door(plr: Player, dir: str, grid):
    ok, msg = plr.trigger_door(grid, dir)
    log(f"trigger_door(dir={dir!r}) -> {ok}, {msg}")
    return ok, msg


def whats_in_position(plr: Player, x: int, y: int, grid, GRID_X, GRID_Y):
    if not in_boundaries(x, y, GRID_X, GRID_Y):
        ok, msg = False, "Out of boundaries"
        log(f"whats_in_position(x={x}, y={y}) -> {ok}, {msg}")
        return ok, msg
    obj = grid[x][y]
    if obj == -1:
        ok, msg = True, "empty"
        log(f"whats_in_position(x={x}, y={y}) -> {ok}, {msg}")
        return ok, msg
    ok, msg = True, obj.getInfo()
    log(f"whats_in_position(x={x}, y={y}) -> {ok}, {msg}")
    return ok, msg


def get_all_grid_data(grid, GRID_X, GRID_Y):
    res = ""
    for x in range(GRID_X):
        row = []
        for y in range(GRID_Y):
            obj = grid[x][y]
            row.append("~" if obj == -1 else obj.type)
        res += " ".join(row) + "\n"
    ok, msg = True, res
    log(f"get_all_grid_data() -> {ok}, grid={GRID_X}x{GRID_Y}")
    return ok, msg

def get_inventory_data(plr: Player):
    ok, msg = True, plr.Inventory.get_inventory_list()
    log(f"get_inventory_data() -> {ok}, {msg}")
    return ok, msg

def whats_inside_chest(plr: Player, grid, dir: str, GRID_X, GRID_Y):
    x, y = get_pos_from_dir(dir, plr.x, plr.y, GRID_X, GRID_Y)
 
    if (x, y) == (-1, -1) or not in_boundaries(x, y, GRID_X, GRID_Y):
        ok, msg = False, "Out of boundaries"
        log(f"whats_inside_chest(dir={dir!r}) -> {ok}, {msg}")
        return ok, msg
    
    if not isinstance(grid[x][y], Chest):
        ok, msg = False, "Not a chest"
        log(f"whats_inside_chest(dir={dir!r}) -> {ok}, {msg}")
        return ok, msg
    ok, msg = True, grid[x][y].getInfo()
    log(f"whats_inside_chest(dir={dir!r}) -> {ok}, {msg}")
    return ok, msg
