import asyncio
import os
import uuid
from typing import List

from openai import AsyncOpenAI
from pydantic.dataclasses import dataclass

from indexing.parse_data_service import ReturnFormat, ChunkData
from services.prompts import generate_doc_context_promt
from services.search_services import get_index


openai = AsyncOpenAI(
    api_key=os.environ.get('MLP_TOKEN', '1000097868.110610.cfUF9zxN1MD7Ot8IHmr48LLXdtDv9Do9T9RZkfSL'),
    base_url="https://caila.io/api/adapters/openai"
)

ix = get_index()


@dataclass
class IndexingChunk:
    chunk: str
    context: str
    char_position_start: int
    char_position_end: int
    chapter: str
    chunk_id: str


async def indexing_file(file_info: List[ReturnFormat]) -> List[IndexingChunk]:
    """Тут распараллелить процесс по массиву"""
    writer = ix.writer()
    processed_chunks = []
    for chapter in file_info:
        for chunk in chapter.chunk_text:
            document_context_promt = generate_doc_context_promt(chapter.full_chapter_text)
            generate_chunks_context_promt = generate_doc_context_promt(chunk.chunk_text)
            context = await interaction_with_llm(document_context_promt, generate_chunks_context_promt)
            context = context['full_text']
            id = str(uuid.uuid4())
            indexed_chunk = IndexingChunk(
                chunk_id=id,
                chunk=chunk.chunk_text,
                char_position_start=chunk.char_position_start,
                char_position_end=chunk.char_position_end,
                chapter=chapter.full_chapter_text,
                context=context
            )
            processed_chunks.append(indexed_chunk)

            writer.add_document(id=u"{}".format(id),
                                chunk_text=u"{}".format(chunk.chunk_text),
                                context=u"{}".format(context))

    writer.commit()
    return processed_chunks


async def interaction_with_llm(document_context_promt: str, chunk_generate_promt: str):
    res = await openai.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": document_context_promt,
                        "cache_control": {"type": "ephemeral"}
                    },
                    {
                        "type": "text",
                        "text": chunk_generate_promt,
                    }
                ]
            }
        ],

        model="just-ai/openai-proxy/gpt-4o",
        temperature=0,
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


if __name__ == "__main__":
    async def test():
        document = 'девки в озере купались, хуй резиновый нашли. Целый день они ебались даже в школу не пошли'
        chunk = 'хуй резиновый'

        test_chunk_data = ChunkData(
            chunk_text=chunk,
            char_position_start=0,
            char_position_end=100,
            chapter=document
        )

        test_data = ReturnFormat(chunk_text=[test_chunk_data],
                                 chapter=document,
                                 full_chapter_text=document)

        await indexing_file([test_data])

        document = 'Помидоры помидоры помидоры овощи'
        chunk = 'овощи'

        test_chunk_data = ChunkData(
            chunk_text=chunk,
            char_position_start=0,
            char_position_end=100,
            chapter = document
        )

        test_data = ReturnFormat(chunk_text=[test_chunk_data],
                                 chapter=document,
                                 full_chapter_text=document)

        await indexing_file([test_data])

        document = 'пизда едет на кобыле а хуй на скорой помощи'
        chunk = 'а хуй'

        test_chunk_data = ChunkData(
            chunk_text=chunk,
            char_position_start=0,
            char_position_end=100,
            chapter=document
        )

        test_data = ReturnFormat(chunk_text=[test_chunk_data],
                                 chapter=document,
                                 full_chapter_text=document)

        await indexing_file([test_data])

        from whoosh.qparser import QueryParser

        with ix.searcher() as searcher:
            query = QueryParser("chunk_text", ix.schema).parse("резиновый")
            results = searcher.search(query)
            print(results[0])


    asyncio.run(test())
