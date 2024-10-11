from typing import List

import openai
from pydantic.dataclasses import dataclass

from indexing.parse_data_service import ReturnFormat
from openai import AsyncOpenAI


@dataclass
class IndexingChunk:
    chunk: str
    context: str
    char_position_start: int
    char_position_end: int
    chapter: str
    unique_id: str


def indexing_file(file_info: List[ReturnFormat]) -> List[IndexingChunk]:
    """Тут распараллелить процесс по массиву"""
    # for chank in file_info:
    #     indexed_chunk = IndexingChunk(
    #         chunk=
    #     )


async def fetch_completion(prompt: str, count = 0):
    try:
        res = await openai.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="just-ai/just-ai/vllm-llama3.1-8b",
            temperature=0,
            response_format={"type": "json_object"},
            stream=False
        )

        response_json = res
        input_tokens = int(res.usage.prompt_tokens)
        output_tokens = int(res.usage.completion_tokens)
        content = res.choices[0].message.content

        return {
            "response_json": response_json,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "full_text": content
        }
    except Exception as e:
      print(e)

