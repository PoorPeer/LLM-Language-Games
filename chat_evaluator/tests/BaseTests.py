from abc import ABC, abstractmethod
from typing import Union
from rich import print
import os


class MessageTest(ABC):
    @abstractmethod
    def test(self, message: str, previous_messages: list[str]) -> bool:
        assert False, "This method must be implemented in a subclass"


class ManualMessageTest(MessageTest):
    def __init__(self, prompt: str) -> None:
        super().__init__()
        self.prompt = prompt

    def get_answer(self) -> bool:
        print("Write 'y' if the message passes, 'n' if it fails")
        # Read keypress from the user
        user_input = input().lower()
        while user_input not in ['y', 'n']:
            print("Invalid input, please write 'y' or 'n'")
            user_input = input().lower()
        return user_input == 'y'


class ManualIndependentMessageTest(ManualMessageTest):
    def __init__(self, prompt: str) -> None:
        super().__init__(prompt)

    def test(self, message: str, previous_messages: list[str]) -> bool:
        print("\n" * 100)
        print(f"Test: {self.prompt}")
        print(f"Message: {message}")

        return self.get_answer()


class ManualDependentMessageTest(ManualMessageTest):
    def __init__(self, prompt: str) -> None:
        super().__init__(prompt)

    def test(self, message: str, previous_messages: list[str]) -> bool:
        print("\n" * 100)
        print(f"Test: {self.prompt}")
        print("Previous messages:")

        for previous_message in previous_messages:
            print(previous_message)
        print(f"Message: {message}")

        return self.get_answer()


class GameTest(ABC):
    @abstractmethod
    def test(self, message_history: list[str]) -> bool:
        assert False, "This method must be implemented in a subclass"


TestType = Union[MessageTest, GameTest]
