import os

os.environ["OPENAI_API_KEY"] = "paste_the_API_key_here"

os.environ["COHEREAI_API_KEY"] = "paste_the_API_key_here"

os.environ["HF_TOKEN"] = "paste_the_API_key_here"


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

LOG_FILE = "1_letter_string.json"

global_instructions = f"""

This is a game with two players (LLMs). The output from Player 1 is the input to Player 2 and vice versa.
The players excel in instruction following and pay attention to each other's last contribution before making the next move.
Your output should be written with the form: "word - string", where the "word" is a valid English word,
and the "string" prolongs the string from the other player's last move with one letter.
There should be no other conversation between the players. You must not chat or cheat.

Game Overview:
The objective is to prolong the string letter-by-letter by choosing words that incorporate the sequence of letters (string).
New sequences should prolong the opponent's last string with exactly one letter. Any other modification of the string breaks the rules.
When a player cannot prolong the string, the other wins.

1. Starting the Game:
Player 1 starts by choosing any regular word and picking one single letter in this word to start the string.

2. Playing the Game:
Player 2 chooses another word containing the previous string and extends it with a new letter.
New words must contain the complete 'earlier' string with the newly added letter.
The string can be placed at any position in the word.
The string grows one letter at a time and the player writes out the complete string including the new letter.
Only existing words are allowed and must be new in the game; word reuse is unacceptable.
If a player swaps or removes letters in the string or reuses the same word, the other player can say "Cheater!" and win.

3. Example:
Player 1: ”say - s”
Player 2: ”sea - se”
Player 1: ”assert - ser”
Player 2: "service - serv"
etc.

4. Ending the Game:
The game ends if a player violates any game rule and the other player notices it.
Otherwise, the winner is the last player who successfully can extend the string following the rules.
If players cannot prolong without breaking the rules, they end the game with "You win.".
If the game has ended, then the next player's message should be nothing but this: "{SIGNAL_END_OF_CONVERSATION}"
"""
# New words must be unique in the game; words that already have been used cannot be used again.

p1_role_desc = """
You are Player 1. 
"""

# Change players by comment/uncomment the snippets:

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

p1 = Player(name="player 1",
               role_desc=p1_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p1_role_desc),
               global_prompt=global_instructions)



p2_role_desc = """
You are Player 2.
"""

"""p2 = Player(name="Player2",
               role_desc=p2_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""

"""p2 = Player(name="Player 2",
               role_desc=p2_role_desc,
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


arena.launch_cli(max_steps=16, interactive=False)

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