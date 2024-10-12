import asyncio
import os
import uuid
from typing import List

from openai import AsyncOpenAI
from pydantic.dataclasses import dataclass


from services.gpt_service import interaction_with_llm
# from services.prompts import generate_doc_context_prompt

from indexing.parse_data_service import ReturnFormat, ChunkData

@dataclass
class ChunkData:
    char_position_start: int
    char_position_end: int
    chunk_text: str
    chapter: str


@dataclass
class ReturnFormat:
    chunk_text: List[ChunkData]
    full_chapter_text: str


openai = AsyncOpenAI(
    api_key=os.environ.get('MLP_TOKEN', '1000097868.110610.cfUF9zxN1MD7Ot8IHmr48LLXdtDv9Do9T9RZkfSL'),
    base_url="https://caila.io/api/adapters/openai"
)

# ix = get_index()


@dataclass
class IndexingChunk:
    chunk: str
    context: str
    char_position_start: int
    char_position_end: int
    chapter: str
    chunk_id: str


async def indexing_file(file_info: str) :
    """Тут распараллелить процесс по массиву"""
    res = await interaction_with_llm(file_info)
    print(res['full_text'])
    # for chapter in file_info:
    #     chapter_text = chapter.full_chapter_text
    #     chunks_text = [cc.chunk_text for cc in chapter.chunk_text]
    #     res = await interaction_with_llm(chunks_text)
    #     lines = res['full_text'].split('\n')
    #
    #
    #     filtered_lines = [line for line in lines if line.strip() and line[0].isdigit()]
    #
    #     for i in range(len(chapter_text) -1):
    #         print(f"{chunks_text[i]} -> {filtered_lines[i]}")
    #     break


    # writer = ix.writer()
    # processed_chunks = []
    # for chapter in file_info:
    #     for chunk in chapter.chunk_text:
    #         document_context_promt = generate_doc_context_prompt(chapter.full_chapter_text)
    #         generate_chunks_context_promt = generate_doc_context_prompt(chunk.chunk_text)
    #         context = await interaction_with_llm(document_context_promt, generate_chunks_context_promt)
    #         context = context['full_text']
    #         id = str(uuid.uuid4())
    #         indexed_chunk = IndexingChunk(
    #             chunk_id=id,
    #             chunk=chunk.chunk_text,
    #             char_position_start=chunk.char_position_start,
    #             char_position_end=chunk.char_position_end,
    #             chapter=chapter.full_chapter_text,
    #             context=context
    #         )
    #         processed_chunks.append(indexed_chunk)
    #
    #         writer.add_document(id=u"{}".format(id),
    #                             chunk_text=u"{}".format(chunk.chunk_text),
    #                             context=u"{}".format(context))
    #
    # writer.commit()
    # return processed_chunks

#
#
# if __name__ == "__main__":
#     async def test():
#         document = 'девки в озере купались, хуй резиновый нашли. Целый день они ебались даже в школу не пошли'
#         chunk = 'хуй резиновый'
#
#         test_chunk_data = ChunkData(
#             chunk_text=chunk,
#             char_position_start=0,
#             char_position_end=100,
#             chapter=document
#         )
#
#         test_data = ReturnFormat(chunk_text=[test_chunk_data],
#                                  chapter=document,
#                                  full_chapter_text=document)
#
#         await indexing_file([test_data])
#
#         document = 'Помидоры помидоры помидоры овощи'
#         chunk = 'овощи'
#
#         test_chunk_data = ChunkData(
#             chunk_text=chunk,
#             char_position_start=0,
#             char_position_end=100,
#             chapter = document
#         )
#
#         test_data = ReturnFormat(chunk_text=[test_chunk_data],
#                                  chapter=document,
#                                  full_chapter_text=document)
#
#         await indexing_file([test_data])
#
#         document = 'пизда едет на кобыле а хуй на скорой помощи'
#         chunk = 'а хуй'
#
#         test_chunk_data = ChunkData(
#             chunk_text=chunk,
#             char_position_start=0,
#             char_position_end=100,
#             chapter=document
#         )
#
#         test_data = ReturnFormat(chunk_text=[test_chunk_data],
#                                  chapter=document,
#                                  full_chapter_text=document)
#
#         await indexing_file([test_data])
#
#         from whoosh.qparser import QueryParser
#
#         with ix.searcher() as searcher:
#             query = QueryParser("chunk_text", ix.schema).parse("резиновый")
#             results = searcher.search(query)
#             print(results[0])
#
#
#     asyncio.run(test())
