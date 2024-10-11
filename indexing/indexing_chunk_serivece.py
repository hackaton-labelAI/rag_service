import asyncio
import os
import uuid
from typing import List

from openai import AsyncOpenAI
from pydantic.dataclasses import dataclass

from indexing.parse_data_service import ReturnFormat, ChunkData
from services.prompts import generate_doc_context_prompt, generate_chunks_context_prompt
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
            document_context_prompt = generate_doc_context_prompt(chapter.full_chapter_text)
            generate_chunks_context_prompt = generate_doc_context_prompt(chunk.chunk_text)
            context = await interaction_with_llm(document_context_prompt, generate_chunks_context_prompt)
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
    async def test_bm25():
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


    async def test_prompt():
        document="""
        Коллективным договором Петропавловского отделения Южно-Уральской
железной дороги - филиала ОАО «РЖД» на 2023 - 2025 годы могут быть
определены категории лиц, которые относятся, либо не относятся к
неработающим пенсионерам данного филиала. Установление более широкого
по сравнению с установленным настоящим Договором перечня категорий лиц,
которые относятся к неработающим пенсионерам данного филиала,
допускается только по согласованию с Комиссией по подготовке коллективного
договора ОАО «РЖД» и контролю за его выполнением в установленном
порядке.
В настоящем Договоре используются следующие понятия:
Работники - физические лица, вступившие и состоящие в трудовых
отношениях с ОАО «РЖД»;
Работодатель, Компания - ОАО «РЖД»;
представитель Работников, Профсоюз - первичная профсоюзная
организация ОАО «Российские железные дороги» Российского
профессионального союза железнодорожников и транспортных строителей
(РОСПРОФЖЕЛ), объединяющая в своих рядах более половины работников
ОАО «РЖД»;
представитель Работодателя - генеральный директор - председатель
правления ОАО «РЖД», а также лица, уполномоченные им в порядке,
установленном законодательством Российской Федерации;
филиал - обособленное структурное подразделение Компании,
действующее в соответствии с уставом ОАО «РЖД», утвержденным
постановлением Правительства Российской Федерации от 27 октября 2021 года
№ 1838;
представительство - обособленное структурное подразделение
Компании, действующее в соответствии с уставом ОАО «РЖД», утвержденным
постановлением Правительства Российской Федерации от 27 октября
2021 года № 1838;
спортивный оператор Компании в части организации и проведения
физкультурных и массовых спортивных мероприятий - Российское
физкультурно-спортивное общество «Локомотив», РФСО «Локомотив»;
объекты социальной сферы - учреждения здравоохранения,
образовательные учреждения, учреждения культуры и спорта, учрежденные
ОАО «РЖД», структурные подразделения филиалов, специализирующиеся на
санаторно-курортном лечении, оздоровлении и отдыхе, а также структурные
подразделения филиалов, специализирующиеся на проведении спортивных,
культурно-просветительских и иных корпоративных мероприятий;
региональные особенности - различия филиалов, других структурных
подразделений, представительств: в социально-демографическом «портрете»
        """
        chunk = ''

        document_context_prompt = generate_doc_context_prompt(document)
        generate_chunks_context_prompt = generate_doc_context_prompt(chunk)

        print(await interaction_with_llm(document_context_prompt, generate_chunks_context_prompt))


    #asyncio.run(test_bm25())
    asyncio.run(test_prompt())
