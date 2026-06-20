"""

Main tools for LLM

get_player_position() -> (x, y)
move_player(dir: str) -> (bool, str)
take_from_chest(dir: str, amount: int) -> (bool, str)
build_object(objType: str, dir: str) -> (bool, str)
color_block(dir: str, new_color: str) -> (bool, str)
trigger_door(dir: str) -> (bool, str)

whats_in_position(x: int, y: int) -> (bool, str)
get_all_grid_data() -> str

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
import asyncio
import json
import os
import sys
from datetime import datetime
 
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_THIS_DIR, "Classes"))
 
from termcolor import colored
from Utils import in_boundaries, allowed_colors
from google import genai
from google.genai import types
 
from Classes.Player import Player
from Classes.Chest import Chest
from Classes.Door import Door
from Classes.Block import Block
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

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
# Game setup
##########################

GRID_SIZE = input("Enter Grid size (e.g. 5*5): ").split("*")
GRID_X, GRID_Y = int(GRID_SIZE[0]), int(GRID_SIZE[1])
grid = [[-1] * GRID_Y for _ in range(GRID_X)]

inventorySize = int(input("Enter inventory size: "))

Chests = []
Chests_size = int(input("Enter number of chests: "))

for i in range(Chests_size):
    print(f"\n--- Chest {i + 1} ---")
    x = int(input("Enter x position: "))
    y = int(input("Enter y position: "))
    heldType = input("Enter held item type: ")
    amount = int(input("Enter amount: "))

    chest = Chest(x, y, heldType, amount)
    ok, msg = chest.add_to_grid(grid, GRID_X, GRID_Y)
    if not ok:
        print(colored(f"Could not place chest: {msg}", "red"))
        continue
    Chests.append(chest)

plr = Player(0, 0, inventorySize)
ok, msg = plr.add_to_grid(grid, GRID_X, GRID_Y)
if not ok:
    print(colored(f"Could not place player: {msg}", "red"))
    sys.exit(1)


def render():
    """Prints the grid to stdout using each object's symbol/color."""
    for x in range(GRID_X):
        row_parts = []
        for y in range(GRID_Y):
            obj = grid[x][y]
            if obj == -1:
                row_parts.append("~")
            else:
                row_parts.append(colored(obj.symbol, obj.color))
        print(" ".join(row_parts))
    print()


render()

##########################
# Tool implementations
# Every tool returns (bool, str) so the model gets explicit
# success/failure plus a human-readable reason it can act on.
##########################


def get_player_position():
    x, y = plr.get_current_position()
    return True, f"Player is at ({x}, {y})"


def move_player(dir: str):
    ok, msg = plr.move(dir, grid)
    log(f"move_player(dir={dir!r}) -> {ok}, {msg}")
    return ok, msg


def take_from_chest(dir: str, amount: int):
    ok, msg = plr.take_from_chest(grid, dir, amount)
    log(f"take_from_chest(dir={dir!r}, amount={amount}) -> {ok}, {msg}")
    return ok, msg


def build_object(objType: str, dir: str):
    ok, msg = plr.build_object(grid, objType, dir)
    log(f"build_object(objType={objType!r}, dir={dir!r}) -> {ok}, {msg}")
    return ok, msg


def color_block(dir: str, new_color: str):
    ok, msg = plr.color_block(grid, dir, new_color)
    log(f"color_block(dir={dir!r}, new_color={new_color!r}) -> {ok}, {msg}")
    return ok, msg


def trigger_door(dir: str):
    ok, msg = plr.trigger_door(grid, dir)
    log(f"trigger_door(dir={dir!r}) -> {ok}, {msg}")
    return ok, msg


def whats_in_position(x: int, y: int):
    if not in_boundaries(x, y, GRID_X, GRID_Y):
        return False, "Out of boundaries"

    obj = grid[x][y]

    if obj == -1:
        return True, "empty"
    return True, obj.getInfo()


def get_all_grid_data():
    res = ""
    for x in range(GRID_X):
        row = []
        for y in range(GRID_Y):
            obj = grid[x][y]
            row.append("~" if obj == -1 else obj.type)
        res += " ".join(row) + "\n"
    return True, res


def get_inventory_data():
    return True, plr.Inventory.get_inventory_list()


##########################
# Tool dispatch table
##########################

TOOL_FUNCTIONS = {
    "get_player_position": lambda args: get_player_position(),
    "move_player": lambda args: move_player(args["dir"]),
    "take_from_chest": lambda args: take_from_chest(args["dir"], int(args["amount"])),
    "build_object": lambda args: build_object(args["objType"], args["dir"]),
    "color_block": lambda args: color_block(args["dir"], args["new_color"]),
    "trigger_door": lambda args: trigger_door(args["dir"]),
    "whats_in_position": lambda args: whats_in_position(int(args["x"]), int(args["y"])),
    "get_all_grid_data": lambda args: get_all_grid_data(),
    "get_inventory_data": lambda args: get_inventory_data(),
}


def dispatch_tool_call(name: str, args: dict):
    """
    Executes a tool by name with the given args dict.
    Always returns a (bool, payload) tuple -- payload may be a string or a list.
    Never raises: malformed args or unknown tool names come back as a
    clean (False, "...") result so the model can self-correct.
    """
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return False, f"Unknown tool: {name}"
    try:
        return fn(args)
    except KeyError as e:
        return False, f"Missing required argument: {e}"
    except (TypeError, ValueError) as e:
        return False, f"Invalid argument: {e}"
    except Exception as e:  # last-resort guard so a bad call can't crash the session
        return False, f"Tool execution error: {e}"


##########################
# Function declarations (schemas) for Gemini
##########################

DIRECTION_ENUM = ["Upward", "Downward", "Leftward", "Rightward"]

get_player_position_decl = {
    "name": "get_player_position",
    "description": "Get the player's current (x, y) grid position.",
    "parameters": {"type": "object", "properties": {}},
}

move_player_decl = {
    "name": "move_player",
    "description": "Move the player one cell in the given direction, if that cell is in bounds and empty.",
    "parameters": {
        "type": "object",
        "properties": {
            "dir": {
                "type": "string",
                "enum": DIRECTION_ENUM,
                "description": "Direction to move the player.",
            }
        },
        "required": ["dir"],
    },
}

take_from_chest_decl = {
    "name": "take_from_chest",
    "description": (
        "Take items from a Chest adjacent to the player in the given direction, "
        "moving them into the player's inventory. Fails if there's no chest there, "
        "the chest doesn't have enough items, or the inventory is full."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "dir": {
                "type": "string",
                "enum": DIRECTION_ENUM,
                "description": "Direction of the chest relative to the player.",
            },
            "amount": {
                "type": "integer",
                "description": "Number of items to take from the chest.",
            },
        },
        "required": ["dir", "amount"],
    },
}

build_object_decl = {
    "name": "build_object",
    "description": (
        "Build/place an object from the player's inventory into the empty cell "
        "adjacent to the player in the given direction. Consumes one item of "
        "objType from the inventory."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "objType": {
                "type": "string",
                "description": "The inventory item type to build, e.g. 'Block' or 'Door'.",
            },
            "dir": {
                "type": "string",
                "enum": DIRECTION_ENUM,
                "description": "Direction relative to the player to build into.",
            },
        },
        "required": ["objType", "dir"],
    },
}

color_block_decl = {
    "name": "color_block",
    "description": "Change the color of a Block adjacent to the player in the given direction.",
    "parameters": {
        "type": "object",
        "properties": {
            "dir": {
                "type": "string",
                "enum": DIRECTION_ENUM,
                "description": "Direction of the block relative to the player.",
            },
            "new_color": {
                "type": "string",
                "enum": allowed_colors,
                "description": "The new color to apply to the block.",
            },
        },
        "required": ["dir", "new_color"],
    },
}

trigger_door_decl = {
    "name": "trigger_door",
    "description": "Open or close a Door adjacent to the player in the given direction (toggles its state).",
    "parameters": {
        "type": "object",
        "properties": {
            "dir": {
                "type": "string",
                "enum": DIRECTION_ENUM,
                "description": "Direction of the door relative to the player.",
            }
        },
        "required": ["dir"],
    },
}

whats_in_position_decl = {
    "name": "whats_in_position",
    "description": "Inspect a specific grid cell by absolute (x, y) coordinates and describe what's there.",
    "parameters": {
        "type": "object",
        "properties": {
            "x": {"type": "integer", "description": "Row index (0-based)."},
            "y": {"type": "integer", "description": "Column index (0-based)."},
        },
        "required": ["x", "y"],
    },
}

get_all_grid_data_decl = {
    "name": "get_all_grid_data",
    "description": "Get a text rendering of the entire grid, row by row, showing each cell's object type or '~' for empty.",
    "parameters": {"type": "object", "properties": {}},
}

get_inventory_data_decl = {
    "name": "get_inventory_data",
    "description": "Get the player's current inventory contents as a list of 'itemType: count' strings.",
    "parameters": {"type": "object", "properties": {}},
}

ALL_FUNCTION_DECLARATIONS = [
    get_player_position_decl,
    move_player_decl,
    take_from_chest_decl,
    build_object_decl,
    color_block_decl,
    trigger_door_decl,
    whats_in_position_decl,
    get_all_grid_data_decl,
    get_inventory_data_decl,
]

tools = [{"function_declarations": ALL_FUNCTION_DECLARATIONS}]

SYSTEM_INSTRUCTION = (
    "You are an agent controlling a player inside a 2D grid simulation. "
    "You may ONLY interact with the world by calling the provided tools -- "
    "never claim an action happened unless the matching tool call returned "
    "success. Every tool returns a boolean success flag and a message: "
    "if success is false, read the message, adjust your approach, and try "
    "again or pick a different action. Use get_all_grid_data or "
    "whats_in_position to understand your surroundings before acting, and "
    "get_inventory_data to check what you're carrying before building."
)

config = {
    "response_modalities": ["TEXT"],
    "tools": tools,
    "system_instruction": SYSTEM_INSTRUCTION,
}

client = genai.Client(api_key=api_key)
MODEL = "gemini-2.5-flash-live-preview"


##########################
# Live session loop
##########################

async def handle_tool_call(session, tool_call):
    """Executes every function call in a tool_call message and sends results back."""
    function_responses = []
    for fc in tool_call.function_calls:
        args = dict(fc.args or {})
        ok, payload = dispatch_tool_call(fc.name, args)
        response_dict = {"success": ok, "message": payload if isinstance(payload, str) else None}
        if isinstance(payload, list):
            response_dict["data"] = payload
            response_dict["message"] = None
        function_responses.append(
            types.FunctionResponse(id=fc.id, name=fc.name, response=response_dict)
        )
    await session.send_tool_response(function_responses=function_responses)
    render()


async def run_session(initial_prompt: str):
    async with client.aio.live.connect(model=MODEL, config=config) as session:
        await session.send_client_content(turns={"parts": [{"text": initial_prompt}]})

        async for response in session.receive():
            if response.text is not None:
                print(colored(response.text, "cyan"), end="")
            if response.tool_call:
                await handle_tool_call(session, response.tool_call)


def main():
    print(colored("Simulation ready. (Ctrl+C to quit).", "yellow"))
    try:
        while True:
            prompt = input("\n> ")
            if not prompt.strip():
                continue
            asyncio.run(run_session(prompt))
    except KeyboardInterrupt:
        print("\nExiting.")


if __name__ == "__main__":
    main()