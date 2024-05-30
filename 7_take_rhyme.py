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


LOG_FILE = "7_take_rhyme.json"


global_instructions = f"""
Game Overview:
This is a cooperative game where two LLMs - Players 1 and 2 - write poetry together.
The objective is to write a poem by taking turns, by rhyming on each other's contributions, and leaving unrhymed strophes for the other player to rhyme on.
The poem should rhyme on every second strophe - the rhyming pattern "AA, BB, CC" - but the players must never rhyme by their own.
Instead, Player 1 only writes one strophe "A" to begin with.
After that, Player 2 writes two strophes; one rhyming with the earlier strophe "A" from player 1,
and another strophe "B" for Player 1 to rhyme with in the next round.

1. Starting instructions:
Player 1 starts by writing a single poetic strophe/sentence with no ending rhyme (A).

2. Playing the Game / States:
Player 2 continues the poem by writing a strophe rhyming with Player 1's latest strophe,
and adds another poetic strophe that must not rhyme with the former (A, B).
Player 1 continues by writing another strophe rhyming with Player 2's latest strophe,
and adds another poetic strophe that must not rhyme with the former (B, C).
And so on, when the players take turns and repeat this pattern the rhyming poem grows.

3. Examples:
Player 1: "In a garden bloomed a solitary rose."
Player 2: "Its petals were red, unfurled in repose."
          "Amidst the plants, a wind of will blew."
Player 1: "In a whispering sound, a petal flew,"
          "made the wind wiggle, and caused a storm"
Player 2: "that swept across oceans, became a new norm"
           etc. 

4. Ending the poem:
The poem must be between 10-16 strophes long.
Player 2 will end with a single strophe, rhyming on Player 1:s latest strophe.
Afterwards, the assessment remains.

After the poem, the artists (Player 1 and 2) will assess its qualities together.
1-5 points should be given for the formal qualities (rhyme, meter, prosody).
1-5 points should be given for the content (coherent, poetic, and evocative).
Keep the assessment brief and accurate. When both players have agreed on the evaluation,
the next player in turn says only and exactly "{SIGNAL_END_OF_CONVERSATION}"
"""


p1_role_desc = """You are Player 1.
                You start the poem.
                You are a futurist poet, who likes to break the poetical tradition.
                Your role model is Mayakovsky.
                Your favorite themes are transhumanism and technology.
                The beginning strophes should have between 7 - 9 words.
                The starting strophe sets the meter and theme for the poem.
                Make sure the poem gets an unusual and unexpected start!"""


"""p1 = Player(name="Player 1",
               role_desc=p1_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""

"""p1 = Player(name="player 1",
               role_desc=p1_role_desc,
               backend=ClaudeAnthropic(model="claude-3-opus-20240229"),
               global_prompt=global_instructions)"""

"""p1 = Player(name="player 1",
               role_desc=p1_role_desc,
               backend=CohereChat(model="command-r-plus"),
               global_prompt=global_instructions)"""

p1 = Player(name="player 1",
               role_desc=p1_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p1_role_desc),
               global_prompt=global_instructions)


p2_role_desc = """You are Player 2.
                You will end the poem.
                You are a romantic poet, who sees the beauty in everything.
                Your role model is Lord Byron.
                Your favorite themes are unexpected friendship and global consciousness.
                You are very flexible and good at adopting to the fellow writer."""

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

arena.launch_cli(max_steps=18, interactive=False)

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