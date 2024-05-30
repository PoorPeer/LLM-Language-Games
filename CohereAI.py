from typing import List
import re
import os
from tenacity import retry, stop_after_attempt, wait_random_exponential
from chatarena.backends.base import IntelligenceBackend, register_backend
from chatarena.message import Message, SYSTEM_NAME
from cohere import Client, ChatMessage

@register_backend
class CohereChat(IntelligenceBackend):
  stateful = False
  type_name = "cohere"

  def __init__(self, max_tokens: int = 256, model: str = "command-r-plus"):
    super().__init__()

    self.max_tokens = max_tokens
    self.model = model

    self.client = Client(os.environ.get("COHEREAI_API_KEY"))


  @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=1, max=60))
  def _get_response(self, history: List[ChatMessage], message: str, preamble: str = "") -> str:
        response = self.client.chat(chat_history=history, message=message, preamble=preamble)

        return response.text.strip()

  def query(
        self,
        agent_name: str,
        role_desc: str,
        history_messages: List[Message],
        global_prompt: str = None,
        request_msg: Message = None,
        *args,
        **kwargs,
    ) -> str:
        """
        Format the input and call the Claude API.

        args:
            agent_name: the name of the agent
            role_desc: the description of the role of the agent
            env_desc: the description of the environment
            history_messages: the history of the conversation, or the observation for the agent
            request_msg: the request from the system to guide the agent's next response
        """

        messages: List[ChatMessage] = []
        current_message = ""

        if not request_msg:
            if len(history_messages) > 0:
                request_msg = history_messages[-1]
                history_messages = history_messages[:-1]
            else:
                request_msg = Message("System", f"Now you speak, {agent_name}", 0)


        for i, message in enumerate(history_messages):
            if message.agent_name == agent_name:
                if current_message != "":
                    messages.append({"role": "USER", "message": current_message})
                messages.append({"role": "CHATBOT", "message": message.content})
                current_message = ""
            else:
                current_message += f"\n\n[{message.agent_name}]: {message.content}"
        
        if current_message != "":
          messages.append({"role": "USER", "message": current_message})

        preamble = ""

        if global_prompt:
            preamble += global_prompt + "\n\n"

        preamble += role_desc

        last_message = f"[{request_msg.agent_name}]: {request_msg.content}"

        # print("MESSAGES:", messages)
        # print("LAST_MESSAGE", last_message)

        response = self._get_response(messages, last_message, preamble)

        # Remove the agent name if the response starts with it
        return re.sub(rf"^\s*\[?({re.escape(agent_name)})?({re.escape(agent_name.lower())})?\]?\s*:?", "", response).strip()
  
  async def async_query(
          self,
          agent_name: str,
          role_desc: str,
          history_messages: List[Message],
          global_prompt: str = None,
          request_msg: Message = None,
          *args,
        **kwargs,
      ) -> str:
          """Async querying."""
          raise NotImplementedError

        