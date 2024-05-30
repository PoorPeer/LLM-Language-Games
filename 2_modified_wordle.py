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


LOG_FILE = "2_modified_wordle.json"



global_instructions =f"""
This is a game with two players (LLMs).
One is the Guesser and the other is the Concealer.
Both are focused and they write as little as possible.
The Concealer is hiding a secret five-letter word.
The Guesser aims to guess the secret word within five attempts,
combining the information from the Concealer's feedback to infer the secret word.
The Concealer wins if the Guesser fails to reveal the word within five attempts.
The concealer must be honest and provide accurate feedback after every guessing attempt.

1. Starting the Game:
The Concealer hides a secret word, that is guessable and tells the Guesser "Start guessing".
The Guesses pick a valid, five-letter long word as a first guess.

2. Playing the Game:
The Concealer provides accurate feedback by telling which letters in the guessed word are in the correct position in the secret word,
or which letters in the guessed word are in the secret word but in another position.
Feedback must be given after each guess.
After the Concealer provides feedback, the Guesser will make a new attempt to guess the secret word.
The Guesser should choose new words never used to get additional information in every round.
The information adds up to increasingly better clues to the secret word.
If someone breaks the game rules, the other player can accuse them.
If the accusation is motivated, the cheater loses.

3. Example (where the Concealer chooses "SMALL" as the secret word.)
Concealer: Guesser, you can start.
Guesser: "MOULD"
Concealer: "M" is in the secret word but not in the correct position.
The letter "L" is in the secret word and the correct position.
Guesser: "CLAMS"
Concealer: "L", "M" and "S" are in the secret word but not in the correct positions.
etc.

4. Winning the Game:
The Guesser wins ten points if the secret word is found within five attempts. The Concealer then says "You win!"
If the Guesser fails to find the secret word within five attempts, the Concealer must tell the secret word to win ten points
A player also wins if they discover that the other player is trying to cheat.
When someone wins, the game ends. 
When the game has ended, then the next player's message should only be only and exactly "{SIGNAL_END_OF_CONVERSATION}"
"""

p1_role_desc = """
You are the Concealer.
"""



"""p1 = Player(name="Concealer",
               role_desc=p1_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""

p1 = Player(name="Concealer",
               role_desc=p1_role_desc,
               backend=ClaudeAnthropic(model="claude-3-opus-20240229"),
               global_prompt=global_instructions)

"""p1 = Player(name="Concealer",
               role_desc=p1_role_desc,
               backend=CohereChat(model="command-r-plus"),
               global_prompt=global_instructions)"""

"""p1 = Player(name="Concealer",
               role_desc=p1_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p1_role_desc),
               global_prompt=global_instructions)"""


p2_role_desc = """
You are the Guesser.
"""


"""p2 = Player(name="Guesser",
               role_desc=p2_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""

"""p2 = Player(name="Guesser", role_desc=p2_role_desc,
               backend=ClaudeAnthropic(model="claude-3-opus-20240229"),
               global_prompt=global_instructions)"""

p2 = Player(name="Guesser",
               role_desc=p2_role_desc,
               backend=CohereChat(model="command-r-plus"),
               global_prompt=global_instructions)

"""p2 = Player(name="Guesser",
               role_desc=p2_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p2_role_desc),
               global_prompt=global_instructions)"""



players = [p1, p2]

environment: ModifiedConversation = ModifiedConversation([player.name for player in players], parallel=False)

environment.message_pool.append_message(Message("System", f"Now you speak, {players[0].name}", 0))

arena = Arena(players, environment)


arena.launch_cli(max_steps=16, interactive=False)

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