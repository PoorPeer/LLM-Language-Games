from typing import Dict, Union, List
from tinydb.table import Document, Table


class DBType:
    def __init__(self, id: Union[int, None] = None):
        self.id = id

    def get_id(self) -> int:
        if self.id is None:
            raise ValueError(
                "Object not in database when attempting to get id.")
        return self.id

    def insert_into_table(self, table: Table) -> None:
        doc_id = table.insert(self.to_dict())

        self.id = doc_id

    def update_in_table(self, table: Table) -> None:
        table.update(self.to_dict(), doc_ids=[self.get_id()])

    def is_in_db(self) -> bool:
        return self.id is not None

    def to_dict(self) -> Dict:
        raise NotImplementedError

    @staticmethod
    def from_dict(data: Document):
        raise NotImplementedError


class GameType(DBType):
    def __init__(self, name: str, id: Union[int, None] = None):
        super().__init__(id)
        self.name = name

    def to_dict(self) -> Dict:
        return {'name': self.name}

    @staticmethod
    def from_dict(data: Document) -> 'GameType':
        return GameType(data['name'], data.doc_id)


class Model(DBType):
    def __init__(self, name: str, id: Union[int, None] = None):
        super().__init__(id)
        self.name = name

    def to_dict(self) -> Dict:
        return {'name': self.name}

    @staticmethod
    def from_dict(data: Document) -> 'Model':
        return Model(data['name'], data.doc_id)


class Game(DBType):
    def __init__(self, game_type: int, players: List[int], id: Union[int, None] = None):
        super().__init__(id)
        self.game_type = game_type
        self.players = players

    def to_dict(self) -> Dict:
        return {'game_type': self.game_type, 'players': self.players}

    @staticmethod
    def from_dict(data: Document) -> 'Game':
        return Game(data['game_type'], data['players'], data.doc_id)


class Message(DBType):
    def __init__(self, sender: int, game: int, content: str, turn: int, id: int | None = None):
        super().__init__(id)
        self.sender = sender
        self.game = game
        self.content = content
        self.turn = turn

    def to_dict(self) -> Dict:
        return {'sender': self.sender, 'game': self.game, 'content': self.content, 'turn': self.turn}

    @staticmethod
    def from_dict(data: Document) -> 'Message':
        return Message(data['sender'], data['game'], data['content'], data['turn'], data.doc_id)


class Test(DBType):
    def __init__(self, name: str, id: Union[int, None] = None):
        super().__init__(id)
        self.name = name

    def to_dict(self) -> Dict:
        return {'name': self.name}

    @staticmethod
    def from_dict(data: Document) -> 'Test':
        return Test(data['name'], data.doc_id)


class TestResult(DBType):
    def __init__(self, test: int, message: int, result: bool, id: Union[int, None] = None):
        super().__init__(id)
        self.test = test
        self.message = message
        self.result = result

    def to_dict(self) -> Dict:
        return {'test': self.test, 'message': self.message, 'result': self.result}

    @staticmethod
    def from_dict(data: Document) -> 'TestResult':
        return TestResult(data['test'], data['message'], data['result'], data.doc_id)
