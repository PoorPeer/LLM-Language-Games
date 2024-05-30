from typing import List
from anthropic import Anthropic
from anthropic.types import MessageParam
import re
import os
from tenacity import retry, stop_after_attempt, wait_random_exponential
from chatarena.backends.base import IntelligenceBackend, register_backend
from chatarena.message import Message, SYSTEM_NAME

os.environ["ANTHROPIC_API_KEY"] = "paste-the-API-key-here"

@register_backend
class ClaudeAnthropic(IntelligenceBackend):
  stateful = False
  type_name = "claude"

  def __init__(self, max_tokens: int = 256, model: str = "claude-3-opus-20240229"):
    super().__init__()

    self.max_tokens = max_tokens
    self.model = model

    self.client = Anthropic()


  @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=1, max=60))
  def _get_response(self, messages: List[MessageParam]) -> str:
        response = self.client.messages.create(max_tokens=self.max_tokens, messages=messages, model=self.model)

        return response.content[0].text.strip()

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

        all_messages = (
            [(SYSTEM_NAME, global_prompt), (SYSTEM_NAME, role_desc)]
            if global_prompt
            else [(SYSTEM_NAME, role_desc)]
        )

        for message in history_messages:
            all_messages.append((message.agent_name, message.content))
        if request_msg:
            all_messages.append((SYSTEM_NAME, request_msg.content))

        messages: List[MessageParam] = []
        current_message = ""

        for i, message in enumerate(all_messages):
            if i == 0:
                assert (
                    message[0] == SYSTEM_NAME
                )  # The first message should be from the system

            if message[0] == agent_name:
                if current_message != "":
                    messages.append({"role": "user", "content": current_message})
                messages.append({"role": "assistant", "content": message[1]})
                current_message = ""
            else:
                current_message += f"\n\n[{message[0]}]: {message[1]}"
        
        if request_msg:
            current_message += f"\n\n[{request_msg.agent_name}]: {request_msg.content}"

        if (current_message != ""):
          messages.append({"role": "user", "content": current_message})
        
        response = self._get_response(messages)

        # Remove the agent name if the response starts with it
        return re.sub(rf"^\s*\[?{re.escape(agent_name)}\]?\s*:?", "", response).strip()
  
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

        