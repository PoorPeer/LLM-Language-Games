import os

os.environ["OPENAI_API_KEY"] = "paste-the-API-key-here"

os.environ["COHEREAI_API_KEY"] = "paste-the-API-key-here"

os.environ["HF_TOKEN"] = "paste-the-API-key-here"

os.environ["ANTHROPIC_API_KEY"] = "paste-the-API-key-here"


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


LOG_FILE = "4_sentence_size_fight.json"

global_instructions = f"""
This is a game with two players (LLMs). Both are creative and competent writers who seldom make any mistakes.
The players must take turns adding every other word to construct a joint, complete sentence.
The sentence must adhere to the grammatical rules, which include proper syntax, at least subject and predicate, semantic completeness, and logical coherence.
The players must add one and only one word at a time.
The players must not remove any word from the sentence.
All previous words must be printed out along with the new word in every step.
Players must add punctuation marks only to end the sentence officially.
The players may also have objectives described in their role descriptions.
The players monitor each other contributions to watch for rule-breaking.
If a player violates grammatical rules, the other player should say "Cheater!" and explain why.
If a player breaks any rule and the other discover it, the cheating player loses the game.

3. Example
Player 1: The
Player 2: The cat
Player 1: The cat took
Player 2: The cat took a
Player 1: The cat took a leap
etc.

3. Winning the Game:

The game can end in two ways; either if some player complete the sentence with a period, or if some player break the rules.
A player confirms defeat and ends the game by writing "You win!"
If the game has ended, then the next player's message should only be exactly "{SIGNAL_END_OF_CONVERSATION}"
"""

p1_role_desc = """
You are the Extender.
You aim to extend the sentence beyond 10 words, to create a longer sentence than ten words.
You have to complete the "more-than-10-word" sentence with a period (.) to win.
You start by adding the first word to the sentence. You should add words that expand the sentence without breaking grammatical rules.
If the sentence is grammatically sound and exceeds 10 words, and you demonstrate how to complete the sentence by adding the last words, then you win.
Be aware that your opponent will try to complete a shorten sentence than 10 words and you have to counteract this.


"""


"""p1 = Player(name="Extender",
               role_desc=p1_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""

"""p1 = Player(name="Extender",
               role_desc=p1_role_desc,
               backend=ClaudeAnthropic(model="claude-3-opus-20240229"),
               global_prompt=global_instructions)"""

"""p1 = Player(name="Extender",
               role_desc=p1_role_desc,
               backend=CohereChat(model="command-r-plus"),
               global_prompt=global_instructions)"""

p1 = Player(name="Extender",
               role_desc=p1_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p1_role_desc),
               global_prompt=global_instructions)




p2_role_desc = """
You are the Completer.
You will aim to create a shorter sentence than ten words; to complete the sentence with less than 10 words.
You can add a last word and period, or only a period to conclude a sentence with less than 10 words.
If you can finalize the sentence with a period (.) before reaching 10 words, ensuring the syntax and semantics are grammatically correct, then you win.

"""

"""p2 = Player(name="Completer",
               role_desc=p2_role_desc,
               backend=OpenAIChat(model="gpt-4"),
               global_prompt=global_instructions)"""


"""p2 = Player(name="Completer", role_desc=p2_role_desc,
               backend=ClaudeAnthropic(model="claude-3-opus-20240229"),
               global_prompt=global_instructions)"""

p2 = Player(name="Completer",
               role_desc=p2_role_desc,
               backend=CohereChat(model="command-r-plus"),
               global_prompt=global_instructions)


"""p2 = Player(name="Completer",
               role_desc=p2_role_desc,
               backend=GeminiChat(model="gemini-pro", system_prompt=global_instructions + "\n\n" + p2_role_desc),
               global_prompt=global_instructions)"""

players = [p1, p2]


arena = Arena(players, ModifiedConversation([player.name for player in players], parallel=False))

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