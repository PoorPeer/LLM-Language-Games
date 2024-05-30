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


LOG_FILE = "3_dynamicYesNo.json"


global_instructions = f"""
Game Overview:
This is a game for two players (LLMs). The objective is to narrow down the thinking by asking strategic yes-or-no questions.
The players excel in logical and critical thinking, and seldom makes any mistakes.
At first, the players think of different things but their clues weave together so that they eventually think of the same or very similar things.

2. Playing the Game:
Player 1 starts by asking a question, which Player 2 will answer.
The players must answer each other's latest question before putting another question.
Every question must be answered honestly with ”Yes” or ”No”, then a question is asked to the other player in the same line.
Information from both player merges, forcing the players to think of new subjects as the scope narrows during the game.
Eventually, what the players think of becomes more and more similar.


3. Game strategies:
Always start with broad questions to narrow down categories (e.g., ”Is it a living thing?”, "Is it man-made?").
Use information from the earlier answers to refine subsequent questions, becoming more specific.
Always consider earlier information before asking the next question.
Adjust your subject to fit all earlier information so far in the game.
Choose new subjects based on the information gathered during the game.
Make sure to always have a specific subject in mind.
Be accurate and economize with the questions.
The goal is to reach a point where only one object fits all criteria, indicating it's time to guess.


4. Examples:
Player 1: Is the subject a living thing?
Player 2: Yes, is the living thing a plant?
Player 1: No, is the living thing a person?
Player 2: Yes, is the person from America? etc.


5. Ending the Game:
When all possible subjects but one are exhausted, a player may guess the subject on their turn.
The game ends if a player successfully guesses the right subject, or if the opponent presents an alternate
subject that fits all prior answers. The other player then confirm this by saying "You win!"
The winners are rewarded with 10 points. It also ends if no player wins within 20 turns.
If the game has ended, then the next player's message should only be exactly "{SIGNAL_END_OF_CONVERSATION}"
"""

p1_role_desc = """
You are Player 1. You start by thinking of the planet Venus (do not reveal this).
You will need to change to think of other objects during the game.
This is because what you think of must fit all the questions and answers from you and the other player."""

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



p2_role_desc = """
You are Player 2. You start by thinking of the 19th century computing pioneer Ada Lovelace (do not reveal this).
You will need to change to think of other objects during the game.
This is because what you think of must fit all the questions and answers from you and the other player.
"""

""""p2 = Player(name="Player 2",
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