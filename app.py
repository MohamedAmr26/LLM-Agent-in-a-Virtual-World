"""

Main tools for LLM

get_player_position() -> (x, y)
move_player(dir: str) -> (bool, str)
take_from_chest(dir: str, amount: int) -> (bool, str)
whats_inside_chest(dir: str) -> (bool, str)
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
import json
import os
import sys
import time
from datetime import datetime

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_THIS_DIR, "Classes"))

from termcolor import colored
from openai import OpenAI, RateLimitError
from Utils import ALLOWED_COLORS, DIRECTION_ENUM, OBJECT_TYPES
from Classes.Player import Player
from Classes.Chest import Chest
from Classes.Door import Door
from Classes.Block import Block
from Classes.Inventory import Inventory

import tools
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

##########################
# Simulation setup
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

def build_state_prompt(history_lines: int = 15) -> str:
    _, grid_text = tools.get_all_grid_data(grid, GRID_X, GRID_Y)
    _, inv_list = tools.get_inventory_data(plr)
    inv_text = ", ".join(inv_list) if inv_list else "empty"

    if os.path.exists(tools.LOG_PATH):
        with open(tools.LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()[-history_lines:]
        recent_history = "".join(lines).strip() or "(no actions yet)"
    else:
        recent_history = "(no actions yet)"

    return (
        "Current grid (row by row, '~' = empty):\n"
        f"{grid_text}\n"
        f"Current inventory: {inv_text}\n\n"
        f"Recent action history (most recent last):\n{recent_history}\n\n"
        "Decide and take your next action by calling one of your tools."
    )


##########################
# Tool dispatch table
##########################

TOOL_FUNCTIONS = {
    "get_player_position": lambda args: tools.get_player_position(plr),
    "move_player": lambda args: tools.move_player(plr, args["dir"], grid),
    "take_from_chest": lambda args: tools.take_from_chest(plr, args["dir"], int(args["amount"]), grid),
    "build_object": lambda args: tools.build_object(plr, args["objType"], args["dir"], grid),
    "color_block": lambda args: tools.color_block(plr, args["dir"], args["new_color"], grid),
    "trigger_door": lambda args: tools.trigger_door(plr, args["dir"], grid),
    "whats_in_position": lambda args: tools.whats_in_position(plr, int(args["x"]), int(args["y"]), grid, GRID_X, GRID_Y),
    "get_all_grid_data": lambda args: tools.get_all_grid_data(grid, GRID_X, GRID_Y),
    "get_inventory_data": lambda args: tools.get_inventory_data(plr),
    "whats_inside_chest": lambda args: tools.whats_inside_chest(plr, grid, args["dir"], GRID_X, GRID_Y)
}


def dispatch_tool_call(name: str, args: dict):
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return False, f"Unknown tool: {name}"
    try:
        return fn(args)
    except KeyError as e:
        return False, f"Missing required argument: {e}"
    except (TypeError, ValueError) as e:
        return False, f"Invalid argument: {e}"
    except Exception as e:
        return False, f"Tool execution error: {e}"


##########################
# Tool schemas (OpenAI format)
##########################

ALL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_player_position",
            "description": "Get the player's current (x, y) grid position.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "move_player",
            "description": (
                "Move the player one cell in the given direction, "
                "if that cell is in bounds and empty."
            ),
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
        },
    },
    {
        "type": "function",
        "function": {
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
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_object",
            "description": (
                "Build/place an object from the player's inventory into the empty cell "
                "adjacent to the player in the given direction. Consumes one item of "
                "objType from the inventory."
                "objType MUST be exactly one of: Block, Door. Case sensitive."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "objType": {
                        "type": "string",
                        "enum": OBJECT_TYPES,
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
        },
    },
    {
        "type": "function",
        "function": {
            "name": "color_block",
            "description": (
                "Change the color of a Block adjacent to the player in the given direction."
            ),
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
                        "enum": ALLOWED_COLORS,
                        "description": "The new color to apply to the block.",
                    },
                },
                "required": ["dir", "new_color"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_door",
            "description": (
                "Open or close a Door adjacent to the player in the given direction "
                "(toggles its state)."
            ),
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
        },
    },
    {
        "type": "function",
        "function": {
            "name": "whats_in_position",
            "description": (
                "Inspect a specific grid cell by absolute (x, y) coordinates "
                "and describe what's there."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Row index (0-based)."},
                    "y": {"type": "integer", "description": "Column index (0-based)."},
                },
                "required": ["x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_grid_data",
            "description": (
                "Get a text rendering of the entire grid, row by row, showing each "
                "cell's object type or '~' for empty."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_inventory_data",
            "description": (
                "Get the player's current inventory contents as a list of "
                "'itemType: count' strings."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "whats_inside_chest",
            "description": (
                "Finds out what is the held material inside a chest and it's amount "
                "adjacent to the player in the given direction."
            ),
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
        },
    },
]

##########################
# OpenRouter client setup
##########################

SYSTEM_INSTRUCTION = (
    "You are a player inside a 2D grid simulation. "
    "You MUST interact with the world by calling the provided tools"
    "never claim an action happened unless the matching tool call returned success."
    "Every tool returns a boolean success flag and a message."
    "if success is false, read the message, find the issue and try again or pick a different action."
    "Use get_all_grid_data or whats_in_position to understand your surroundings before acting."
    "Use get_inventory_data to check what you're carrying before building."
    "Use whats_inside_chest to know what is inside the chest that is a neighbour to you"
    "You must do an action on your prompt."
)

MODEL = "openai/gpt-oss-120b:free"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

##########################
# Agent turn loop
##########################

def run_turn(prompt: str, max_tool_rounds: int = 8):
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": prompt},
    ]

    for _ in range(max_tool_rounds):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=ALL_TOOLS,
                tool_choice="auto",
            )
        except RateLimitError:
            retry_after = 45
            print(colored(f"Rate limited, waiting {retry_after}s...", "yellow"))
            time.sleep(retry_after)
            continue
        except Exception as e:
            print(colored(e, "red"))
            break

        message = response.choices[0].message

        if message.content:
            print(colored(message.content, "cyan"))

        if not message.tool_calls:
            #print(colored(f"[DEBUG] No tool calls returned. Message: {message.content}", "magenta"))
            break

        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]
        })

        # Execute each tool call and feed results back as "tool" messages.
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            ok, payload = dispatch_tool_call(tc.function.name, args)

            result = {"success": ok}
            if isinstance(payload, list):
                result["data"] = payload
            else:
                result["message"] = payload

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result),
            })

        render()


def main():
    print(colored("Simulation running autonomously. (Ctrl+C to quit).", "yellow"))
    try:
        while True:
            prompt = build_state_prompt()
            run_turn(prompt)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nExiting.")


if __name__ == "__main__":
    main()