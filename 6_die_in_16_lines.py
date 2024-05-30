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


LOG_FILE = "6_die_in_16_lines.json"

global_instructions = f"""
This game has two players/actors (LLMs) and is an improvised comedy scene on stage.
The players/actors have different experiences from improvising, which can affect the play.

Game Rules:
The objective is to tell a story where two characters meet their end within 16 lines of dialogue,
emphasizing creativity, humor, teamwork, and narrative finesse.
The task is to create an entertaining situation that leads to the passing away of both characters within a short period,
optionally by different reasons. One line must be shorter than 30 words, but it can contain more than one sentence.

1. Starting the Game:
Player 1 starts the improvisation with a line directed to Player 2.
The characters, their relations, and the situation will grow from the co-play. 

2. Playing the Game:
Players take turns and alternate, contributing one line of dialogue each time.
They must be effective to meet their end within eight lines of dialogue per player.
This back-and-forth continues until the story reaches its conclusion.
The challenge is for both to meet their end within less than sixteen lines of dialogue.

3. Example
Player 1: Holiday, Susan darling, isn't it lovely to lay on the beach!
Player 2: Shut up John, I'm trying to read but the sun is so sharp. Do you have the moisturization spray?
Player 1: No I forgot, but there lays a spray tin in the sand that someone must have forgotten. Shall I spray your back?
etc.

3. Strategies:
Players should build upon each other's contributions and obey.
Players are encouraged to help introduce potential ”dangers” that could lead to each character's demise.
The morbidity is a good presupposition for a creative and humorous plot.
Unexpected death causes have great humoristic potential.
Be flexible and receptive to the story direction, even if it diverges from the initial plan.

4. Ending the Game:
The game ends after 16 lines or when there is no living player who can talk. Players who "die" within the stipulated 16 lines get 10 points each.
When the game ends, the next player write "applause". Then it's time for assessment: The players assess the humorous quality of the dialogue with 1-10 additional points.
After the assessment,  the next player's message should only be exactly "{SIGNAL_END_OF_CONVERSATION}"
"""

p1_role_desc = """
You are a crazy Comedian and improv actor with limitless imagination. You will start the dialogue."""


"""p1 = Player(name="Comedian",
               role_desc=p1_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""

p1 = Player(name="Comedian",
               role_desc=p1_role_desc,
               backend=ClaudeAnthropic(model="claude-3-opus-20240229"),
               global_prompt=global_instructions)

"""p1 = Player(name="Comedian",
               role_desc=p1_role_desc,
               backend=CohereChat(model="command-r-plus"),
               global_prompt=global_instructions)"""


"""p1 = Player(name="Comedian",
               role_desc=p1_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p1_role_desc),
               global_prompt=global_instructions)"""



p2_role_desc = """
You are a somewhat square-headed Engineer who never made this kind of improvisation before now."""

"""p2 = Player(name="Engineer",
               role_desc=p2_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""

"""p2 = Player(name="Engineer", role_desc=p2_role_desc,
               backend=ClaudeAnthropic(model="claude-3-opus-20240229"),
               global_prompt=global_instructions)"""

p2 = Player(name="Engineer",
               role_desc=p2_role_desc,
               backend=CohereChat(model="command-r-plus"),
               global_prompt=global_instructions)

"""p2 = Player(name="Engineer",
               role_desc=p2_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p2_role_desc),
               global_prompt=global_instructions)"""


players = [p1, p2]

# arena = Arena(players, ModeratedConversation([player.name for player in players], moderator, parallel=False))

environment: ModifiedConversation = ModifiedConversation([player.name for player in players], parallel=False)

environment.message_pool.append_message(Message("System", f"Now you speak, {players[0].name}", 0))

arena = Arena(players, environment)


arena.launch_cli(max_steps=20, interactive=False)

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