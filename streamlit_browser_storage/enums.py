
from enum import Enum, unique


@unique
class Action(Enum):

    SET = "SET"

    GET = "GET"

    GET_ALL = "GET_ALL"

    DELETE = "DELETE"

    DELETE_ALL = "DELETE_ALL"
