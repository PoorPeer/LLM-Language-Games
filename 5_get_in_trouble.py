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


LOG_FILE = "5_get_in_trouble.json"

global_instructions = f"""
This is a cooperative exercise with two players (LLMs). The players are storytellers, and they take turns creating a joint narrative.
The story must be cohesive and have one clear main character. The two narrators will push each other creating extreme drama in a short format.

Game Rules:
The objective is to cooperate and create a cohesive story where the main character gets in deep trouble, by adding one sentence after the other.
The sentences must not be longer than 20 words, and the story must be told within 16 sentences.
This mini-format places high demands on the narrative outline and effectiveness.
Both players are professional storytellers with the common goal of crafting an engaging narrative.

1. Playing the Game:
One player starts with a single sentence. The other player adds the next sentence, building upon the previous one and continuing the story.
The players take turns, adding lines to the story. Pretty soon, the main character must get in trouble.
The situation should be so dangerous that the survival chances are small.
The more catastrophic and hopeless situations, the more thrilling the story. The storyteller creates "cliffhangers" to challenge each other.

2. Example:
Player 1: Once upon a time a young girl lived in a desert hut with her mom and dad.
Player 2: The girl was lonely and longed for a friend to play with, someone in her age.
Player 1: One day she found an entrance to a cave in the sand.
Player 2: She went down the old stone stairs with a candle in her hand, when suddenly the door closed behind her. 
etc.

3. Ending the Game:
The story ends when the main character resolves the situation.
When the drama is over the storytellers end the story quickly, and assess it by an "action score".
The action score should estimate the narrative quality on a scale from 1-10, decided upon by the players in common.
When the action score is agreed upon, then the next player's message should only be exactly "{SIGNAL_END_OF_CONVERSATION}"
"""

p1_role_desc = """
You are Player 1. You will write the first sentence."""

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



p2_role_desc = """
You are Player 2."""

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