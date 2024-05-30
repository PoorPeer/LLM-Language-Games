import os

os.environ["OPENAI_API_KEY"] = "paste-the-API-key-here"

os.environ["COHEREAI_API_KEY"] = "paste-the-API-key-here"

os.environ["HF_TOKEN"] = "paste-the-API-key-here"


from chatarena.agent import Player, Moderator, SIGNAL_END_OF_CONVERSATION
from chatarena.backends import OpenAIChat
from chatarena.backends.hf_transformers import TransformersConversational
from chatarena.environments import Conversation
from chatarena.arena import Arena
from chatarena.message import Message
from ModifiedConversation import ModifiedConversation
import json
from ClaudeAnthropic import ClaudeAnthropic
from CohereAI import CohereChat
from GeminiAI import GeminiChat
import time


LOG_FILE = "9_bad_rules.json"


global_instructions = f"""
1. Game Setup:
This interactive game is for two players (LLMs).
The objective is to identify the horse owner and its house color through information sharing and logical reasoning. 
There are four (4) houses in a row, each in a different color. In each house lives only one person of a certain
nationality, and each person owns only one animal. Among these persons, only one is a horse owner.
If some house owners claim to drink or smoke certain things it can be considered red herrings.

2. Playing the Game:
Players take turns adding information to the scenario.
The information can relate to house colors, the nationalities of the owners, or the pets, but mentioning the word "horse" is not allowed.
Make accurate assertions; at most 20 statements are allowed, so a valid guessing should be made after 12-18 statements.
A player must follow the rules, otherwise, the other player says "Cheater!" and explain the fault.
If the cheating is confirmed, the game ends and the cheater loses.

3. Examples are statements like:
”The House number 3 is blue”
”The neighbor of the Englishman has a pig”
"The Russian lives in a red house"
"The turtle owner smokes Camel"

3. Winning the Game:
The first player to correctly identify the horse owner's nationality and house color wins.
One of the players should make a valid and motivated guessing to win.
If the other player confirms that the guessing is correct, the winner gets 10 points.
If the guessing is wrong, the other player presents their solution and wins 10 points instead.
After this, the winner ends the session by writing only and exactly "{SIGNAL_END_OF_CONVERSATION}" in the next turn.
"""

p1_role_desc = """
You are Player1 and you start adding a statement."""


"""p1 = Player(name="Player 1",
               role_desc=p1_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""

"""p1 = Player(name="Player 1",
               role_desc=p1_role_desc,
               backend=ClaudeAnthropic(model="claude-3-opus-20240229"),
               global_prompt=global_instructions)"""

"""p1 = Player(name="Player 1",
               role_desc=p1_role_desc,
               backend=CohereChat(model="command-r-plus"),
               global_prompt=global_instructions)"""

p1 = Player(name="Player 1",
               role_desc=p1_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p1_role_desc),
               global_prompt=global_instructions)

p2_role_desc ="""
There are two participants, Player1 and Player2. You are Player2."""


"""p2 = Player(name="Player 2",
               role_desc=p2_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""

"""p2 = Player(name="Player 2", role_desc=p2_role_desc,
               backend=ClaudeAnthropic(model="claude-3-opus-20240229"),
               global_prompt=global_instructions)"""

p2 = Player(name="Player 2",
               role_desc=p2_role_desc,
               backend=CohereChat(model="command-r-plus"),
               global_prompt=global_instructions)

"""p2 = Player(name="Player 2",
               role_desc=p2_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p2_role_desc),
               global_prompt=global_instructions)"""


players = [p1, p2]


environment: ModifiedConversation = ModifiedConversation([player.name for player in players], parallel=False)

environment.message_pool.append_message(Message("System", f"Now you speak, {players[0].name}", 0))

arena = Arena(players, environment)


arena.launch_cli(max_steps=22, interactive=False)

# arena.launch_cli(max_steps=16, interactive=True)

arena.save_history("temp.json")

f = open("temp.json")

message_history = json.load(f)

f.close()

os.remove("temp.json")

print(message_history)

data = {
    "players": [{"name": player.name, "model": player.backend.type_name} for player in players],
    "messages": [{"sender": message["agent_name"], "content": message["content"], "turn": message["turn"]} for message in message_history],
    "timestamp": time.time()
}

f = open(LOG_FILE)

previous_runs = []

try:
    previous_runs = json.load(f)
except:
    print("LOG FILE OVERWRITTEN, WRONG FORMAT")

f.close()

if not isinstance(previous_runs, list):
    print("LOG FILE OVERWRITTEN, NOT A LIST")
    previous_runs = []

previous_runs.append(data)

json.dump(previous_runs, open(LOG_FILE, "w"), indent=4)