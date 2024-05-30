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


LOG_FILE = "8_ebbas_game.json"

global_instructions = f"""
Game Rules:
This is a game with two players. Both are LLMs.
The objective is to participate in a role-play. The scenario is that a world-famous artist and superstar
has made a new artwork under great secrecy and the interest is enormous. Today the art is to be revealed.
There is a press conference with the artist answering questions about their latest artwork.
All messages in the press conference but the artist's final monologue are limited to 40 words, both the questions and the artist's answers.
Please respect the restricted line length.

1. Roles:
One LLM are given the role of a famous artist. The other acts as the International Press, addressing questions to the artist.
The International Press decides the artist's name, but the nature of the artwork will grow during the press conference.

2. Playing the Game:
The International Press welcomes the audience and introduces the artist by name and merits.
They ask the artist about their latest artwork, the artistic process, and inspirations. 
The press conference continues with 4-6 Questions and Answers, mimicking the dynamics of a real-world press event.
The artwork can be a sculpture, installation, painting, photograph, or any form of Art discussed during the press conference.

3. Ending the Game:
The game concludes with the artist presenting their artwork in a poetic monologue, a maximum of 180 words.
The presentation of the artwork serves as the climax of the game, revealing how well the artist's responses aligned with the nature of the revealed work. 
The International Press then ends the conference by presenting three review headlines of the artwork, each ranked with 1-5 stars. E.g. "Art Without an Audience", 3 stars, NY Times.
After the reviews, then the next player's message should only be exactly "{SIGNAL_END_OF_CONVERSATION}"
"""

p1_role_desc = """
You are acting as the International Press, an important
institution in the 'Art Word', presenting the artist and asking 4-6 questions
before the new Art Work is presented. You seem to be almost starstruck by the artist, admiring the artwork.
Due to the nature of questionening, the International Press can in fact influence the art a lot by asking leading
questions with built-in statements, e.g. "Who do you think will dive down in a submarine 3000 feet to watch the sculpture?",
"Why did you paint with finger colors?", or "How many sky-diving animals are participating in the performance?"
"""


"""p1 = Player(name="International Press",
               role_desc=p1_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""

"""p1 = Player(name="International Press",
               role_desc=p1_role_desc,
               backend=ClaudeAnthropic(model="claude-3-opus-20240229"),
               global_prompt=global_instructions)"""

"""p1 = Player(name="International Press",
               role_desc=p1_role_desc,
               backend=CohereChat(model="command-r-plus"),
               global_prompt=global_instructions)"""


p1 = Player(name="International Press",
               role_desc=p1_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p1_role_desc),
               global_prompt=global_instructions)



p2_role_desc = """
You are acting as the world-famous Artist, answering questions at the press conference and describing your new piece of Art.
Your responses should be realistic and in line with the persona of a famous artist. You pretend to have full control.
You are a Conceptualist, and you may need to provoke to get your important message across.
Many people admire you, don't make them disappointed: they think you are Divine."""

"""p2 = Player(name="The Artist",
               role_desc=p2_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""

"""p2 = Player(name="The Artist", role_desc=p2_role_desc,
               backend=ClaudeAnthropic(model="claude-3-opus-20240229"),
               global_prompt=global_instructions)"""

p2 = Player(name="The Artist",
               role_desc=p2_role_desc,
               backend=CohereChat(model="command-r-plus"),
               global_prompt=global_instructions)

"""p2 = Player(name="The Artist",
               role_desc=p2_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p2_role_desc),
               global_prompt=global_instructions)"""



players = [p1, p2]

# arena = Arena(players, ModeratedConversation([player.name for player in players], moderator, parallel=False))

environment: ModifiedConversation = ModifiedConversation([player.name for player in players], parallel=False)

environment.message_pool.append_message(Message("System", f"Now you speak, {players[0].name}", 0))

arena = Arena(players, environment)


arena.launch_cli(max_steps=18, interactive=False)

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