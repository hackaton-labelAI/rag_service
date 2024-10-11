from typing import List

from pydantic.dataclasses import dataclass

from indexing.parse_data_service import ReturnFormat


@dataclass
class IndexingChunk:
    chunk: str
    context: str
    char_position_start: int
    char_position_end: int
    chapter: str
    unique_id: str


def indexing_file(file_info :List[ReturnFormat]):
    """Тут распаралелить процесс по массиву"""
    pass