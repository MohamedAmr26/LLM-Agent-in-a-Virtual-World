# LLM AGENT, IN A 2D TERMINAL WORLD

The Agent has different objects (Door, Block) and an Inventory.
The Agent has several tools given so it can perform a certain goal (Move, Build and etc).
Agent can obtain objects from Chests that are already in the game given by the User.

* The Agent's goal here is to be a House

---

## Setup

- Of course you need Python installed on your device

- Dependencies
  - `json` → `pip3 install json`
  - `openai` → `pip3 install openai`
  - `termcolor` → `pip3 install termcolor`
  - `datetime` → `pip3 install datetime`
  - `dotenv` → `pip3 install dotenv`
  - `os` → `pip3 install os`
  - `time` → `pip3 install time`

- Create a file named `.env`
  - Inside of it add a key named `OPENROUTER_API_KEY="<YOUR_API_KEY>"`

- In `app.py` line 388, You can change the model to your like, I'm using here openrouter in openai format

- Run `python3 app.py`, when your relative path is at the folder of the project

---

## Inputs

| Prompt | Example |
|---|---|
| Grid size | `5*5` |
| Inventory Size | `20` |
| Number of Chests | `2` |

Each Chest will request:

- X, Y Coordinations

- Held Object Type

- Amount of that Type

---

## Outputs

- A render of the grid each time a tool is called by the Model

- The function tool called name and Result

- A message from the Model after finishing each turn

- The Agent's behaviour is recorded in an external text file `behaviour_log.txt`

---

## Constraints

| Category | Allowed Values |
|---|---|
| Object Types | `Block`, `Chest`, `Door` → *Don't write "Chest" in any Chest Held Object Type* |
| Directions | `Upward`, `Downward`, `Rightward`, `Leftward` |
| Colors | `red`, `green`, `blue`, `yellow`, `light_grey`, `white`, `black`, `magenta`, `cyan` |