import re
from typing import List, Tuple, Union
from .BaseTests import MessageTest, ManualDependentMessageTest, ManualIndependentMessageTest

format_regex = r"^\"?(\w+) - (\w+)\"?$"


class FormatTest(MessageTest):
    def test(self, message: str, previous_messages: list[str]) -> bool:
        return re.match(format_regex, message) is not None


class LetterStringGrow(MessageTest):
    def test(self, message: str, previous_messages: list[str]) -> bool:
        parsed_message = parse_message(message)

        if parsed_message is None:
            return True

        if len(previous_messages) == 0:
            return len(parsed_message[1]) == 1

        parsed_previous_message = parse_message(previous_messages[-1])

        if parsed_previous_message is None:
            return True

        return len(parsed_message[1]) == len(parsed_previous_message[1]) + 1

class LetterStringContainsPrevious(MessageTest):
    def test(self, message: str, previous_messages: list[str]) -> bool:
        parsed_message = parse_message(message)

        if parsed_message is None:
            return True
        
        if (len(previous_messages) == 0):
            return True
        
        parsed_previous_message = parse_message(previous_messages[-1])

        if parsed_previous_message is None:
            return True
        
        return parsed_previous_message[1] in parsed_message[1] 

class LetterStringExistsInWord(MessageTest):
    def test(self, message: str, previous_messages: list[str]) -> bool:
        parsed_message = parse_message(message)

        if parsed_message is None:
            return True

        return parsed_message[1] in parsed_message[0]


class WordHasNotBeenUsed(MessageTest):
    def test(self, message: str, previous_messages: list[str]) -> bool:
        parsed_message = parse_message(message)

        if parsed_message is None:
            return True

        parsed_previous_messages = [parse_message(
            previous_message) for previous_message in previous_messages]

        parsed_previous_messages = [
            previous_message for previous_message in parsed_previous_messages if previous_message is not None]

        return all(parsed_message[0] not in previous_message[0] for previous_message in parsed_previous_messages)


# class CheaterAssessement(MessageTest):
#     def __init__(self) -> None:
#         super().__init__()
#         self.other_tests: List[MessageTest] = [
#             LetterStringGrow(), LetterStringExistsInWord(), WordHasNotBeenUsed(), LetterStringContainsPrevious(), FormatTest()]

#     def test(self, message: str, previous_messages: list[str]) -> bool:
#         parsed_message = parse_message(message)

#         if len(previous_messages) == 0:
#             return parsed_message is not None

#         passed_other_tests = all(other_test.test(
#             previous_messages[-1], previous_messages[:-1]) for other_test in self.other_tests)
        
#         return parsed_message is not None or not passed_other_tests

class WrongCheaterAssessement(ManualDependentMessageTest):
    def __init__(self) -> None:
        super().__init__("Does the player call you a cheater when you don't cheat? Y=NO N=YES")

class WordExists(ManualIndependentMessageTest):
    def __init__(self) -> None:
        super().__init__("Does the word exist?")


# class PlayerIsNice(ManualDependentMessageTest):
#     def __init__(self) -> None:
#         super().__init__("Is the player nice?")


def parse_message(message: str) -> Union[Tuple[str, str], None]:
    message_match = re.match(format_regex, message)

    return (message_match.group(1), message_match.group(2)) if message_match is not None else None
