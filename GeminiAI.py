from typing import List
import re
import os
from tenacity import retry, stop_after_attempt, wait_random_exponential
from chatarena.backends.base import IntelligenceBackend, register_backend
from chatarena.message import Message, SYSTEM_NAME
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from vertexai.generative_models._generative_models import Content

vertexai.init(project="project-name-here", location="europe-north1")

@register_backend
class GeminiChat(IntelligenceBackend):
  stateful = False
  type_name = "gemini"

  def __init__(self, max_tokens: int = 256, model: str = "gemini-pro", system_prompt: str = ""):
    super().__init__()

    self.max_tokens = max_tokens
    self.model = model

    self.client = GenerativeModel(model, system_instruction=system_prompt)


  @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=1, max=60))
  def _get_response(self, messages: List[Content]) -> str:
        response = self.client.generate_content(messages)

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

        messages: List[Content] = []
        current_message = ""

        if len(history_messages) == 0 or history_messages[0].agent_name == agent_name:
            history_messages.insert(0, Message("System", f"Please speak, {agent_name}", 0))


        for i, message in enumerate(history_messages):
            if message.agent_name == agent_name:
                if current_message != "":
                    messages.append(Content(role="user", parts=[Part.from_text(current_message)]))
                messages.append(Content(role="model", parts=[Part.from_text(message.content)]))
                current_message = ""
            else:
                current_message += f"\n\n[{message.agent_name}]: {message.content}"
        
        if current_message != "":
            messages.append(Content(role="user", parts=[Part.from_text(current_message)]))

        response = self._get_response(messages)

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

    