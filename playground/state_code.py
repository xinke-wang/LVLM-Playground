import json
from enum import Enum


class JSONSerializableEnum(Enum):

    def __json__(self):
        return self.name

    @classmethod
    def to_json(cls, obj):
        if isinstance(obj, cls):
            return obj.name
        return obj


class GameStatus(JSONSerializableEnum):
    WIN = 101
    LOSE = 102
    TIE = 103
    INVALID_MOVE = 104
    IN_PROGRESS = 105
    MAX_TRIAL_REACHED = 106
    ERROR = 107


class GameStatusEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, GameStatus):
            return obj.name
        return super().default(obj)
