from typing import List

from pydantic.dataclasses import dataclass


@dataclass
class ChunksData:
    chunk_text: str
    char_position_start: int
    char_position_end: int

@dataclass
class ReturnFormat:
    chapter: str
    chunk_text: List[ChunksData]
    full_chapter_text: str


def parsing_data_from_pdf(path: str, token_chink: int = 512, overlay: bool = True)->List[ReturnFormat]:
    pass

def parsing_data_from_text(text: str, token_chink: int = 512, overlay: bool = True)->List[ReturnFormat]:
    pass