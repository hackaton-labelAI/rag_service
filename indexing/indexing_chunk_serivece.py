import asyncio
import os
from typing import List

from openai import AsyncOpenAI
from pydantic.dataclasses import dataclass
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in, open_dir

from indexing.parse_data_service import ReturnFormat, ChunksData

openai = AsyncOpenAI(
            api_key=os.environ.get('MLP_TOKEN', '1000097868.110610.cfUF9zxN1MD7Ot8IHmr48LLXdtDv9Do9T9RZkfSL'),
            base_url="https://caila.io/api/adapters/openai"
        )


def get_index():
    if not os.listdir("indexdir"):
        schema = Schema(chunk_text=TEXT(stored=True), context=TEXT(stored=True), id=str())
        ix = create_in("indexdir", schema)

    else:
        ix = open_dir("indexdir")
    return ix


ix = get_index()
writer = ix.writer()


@dataclass
class IndexingChunk:
    chunk: str
    context: str
    char_position_start: int
    char_position_end: int
    chapter: str
    chunk_id:


async def indexing_file(file_info: List[ReturnFormat]) -> List[IndexingChunk]:
    """Тут распараллелить процесс по массиву"""
    processed_chunks = []
    for chapter in file_info:
        for chunk in chapter.chunk_text:
            document_context_promt = generate_doc_context_promt(chapter.full_chapter_text)
            generate_chunks_context_promt = generate_doc_context_promt(chunk.chunk_text)
            context = await interaction_with_llm(document_context_promt, generate_chunks_context_promt)
            context = context['response_json'].choices[0].message.content
            indexed_chunk = IndexingChunk(
                chunk=chunk.chunk_text,
                char_position_start=chunk.char_position_start,
                char_position_end=chunk.char_position_end,
                chapter=chapter.full_chapter_text,
                context=context
            )
            processed_chunks.append(indexed_chunk)

            writer.add_document(chunk_text=u"{}".format(chunk.chunk_text), context=u"{}".format(context))
            # помещаем в lupyne чанк текст. И создаем копию ф-ции, которая еще и контекст сует
    writer.commit()
    ix.store()
    return processed_chunks


def generate_doc_context_promt(doc_content):
    promt = f"""
<document>
{doc_content}
</document>
"""
    return promt


def generate_chunks_context_promt(chunk):
    promt = f"""
Here is the chunk we want to situate within the whole document
<chunk>
{chunk}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
Answer only with the succinct context and nothing else.
    """
    return promt


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
    document = 'девки в озере купались хуй резиновый нашли. Целый день они ебались даже в школу не пошли'
    chunk = 'хуй резиновый'

    # test_chunk_data = ChunksData(
    #     chunk_text=chunk,
    #     char_position_start=0,
    #     char_position_end=100
    # )
    #
    # test_data = ReturnFormat(chunk_text=[test_chunk_data],
    #                          chapter=document,
    #                          full_chapter_text=document)


    # asyncio.run(indexing_file([test_data]))

    from whoosh.qparser import QueryParser
    with ix.searcher() as searcher:
        query = QueryParser("chunk_text", ix.schema).parse("резиновый")
        results = searcher.search(query)
        print(results[0])