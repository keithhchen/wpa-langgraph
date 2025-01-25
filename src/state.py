from typing import TypedDict, Annotated, TypeVar
import operator

T = TypeVar('T')

def take_latest(old_value, new_value) -> T:
    return new_value

class State(TypedDict):
    original_article: Annotated[str, take_latest]
    outline: Annotated[dict, take_latest]
    final_article: str
    insights: Annotated[str, operator.concat]
    transcript: Annotated[str, operator.concat]
    messages: Annotated[list, operator.add]
    paragraphs: Annotated[list, operator.add]
    metadata: dict
    preface: Annotated[str, operator.concat]

class ParagraphState(TypedDict):
    original_article: str
    node: dict