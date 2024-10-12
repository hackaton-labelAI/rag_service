import asyncio
import re
from typing import List
from services.vector_bd import VectorDB
from services.bm25_search_service import get_index, indexing_document
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic.dataclasses import dataclass
from services.pars_links import parse_links
import json
from transformers import AutoTokenizer


@dataclass
class dr:
    version: int
    label: str
    text: str

@dataclass
class ChunkData:
    chunk_text: str
    data: List[dr]
    link: str

@dataclass
class ReturnFormat:
    chunk_text: List[ChunkData]
    full_chapter_text: str

bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def token_length_function(text):
    tokens = bert_tokenizer.encode(text, truncation=False)
    return len(tokens)

def parsing_data_from_pdf(file_name: str, section_links: dict, token_chunk: int = 250, overlay: int = 50) -> List[ReturnFormat]:
    file_path = f'../data/{file_name}'

    loader = PyPDFLoader(file_path)
    file = loader.load()
    content = ''.join(file[i].page_content for i in range(len(file)))
    pattern = r'(Раздел \d+\.\s[^\n]+)(.*?)(?=Раздел \d+\.|$)'
    sections = re.findall(pattern, content, re.DOTALL)
    texts = [{'label': section[0], 'text': section[1].strip()} for section in sections]

    result = []
    for text in texts:
        parsed_data = parsing_data_from_text([text], section_links, token_chunk, overlay)
        result.extend(parsed_data)
    return result

def parsing_data_from_web(token_chunk: int = 450, overlay: int = 100) -> List[ReturnFormat]:
    section_links = parse_links("https://company.rzd.ru/ru/9353/page/105104?id=1604#7275")

    loader = WebBaseLoader(['https://company.rzd.ru/ru/9353/page/105104?id=1604#navPart_7274'])
    file = loader.load()
    content = ''.join(file[i].page_content for i in range(len(file)))

    pattern = r'(Раздел \d+\.\s[^\n]+)(.*?)(?=Раздел \d+\.|$)'
    sections = re.findall(pattern, content, re.DOTALL)

    texts = [{'label': section[0].strip(), 'text': section[1].strip()} for section in sections if section[1].strip()]

    result = []
    for text in texts:
        parsed_data = parsing_data_from_text([text], section_links, token_chunk, overlay)
        result.extend(parsed_data)

    return result

def parsing_data_from_text(content: List[dict], section_links: dict, token_chunk: int = 450, overlay: int = 100) -> List[ReturnFormat]:
    all_data = []

    for text in content:
        chunk_data_list = []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=token_chunk,
            chunk_overlap=overlay,
            length_function=token_length_function
        )

        chunks = text_splitter.split_text(text['text'])
        section_label = text['label']

        link = section_links.get(section_label, "Ссылка не найдена")

        for chunk in chunks:
            chunk = chunk.strip()

            if len(chunk) > 10 and not chunk.startswith("Раздел"):
                chunk_data = ChunkData(
                    chunk_text=chunk,
                    data=[dr(version=1, label=text['label'], text=chunk)],
                    link=link
                )
                chunk_data_list.append(chunk_data)

        all_data.append(ReturnFormat(
            chunk_text=chunk_data_list,
            full_chapter_text=text['text']
        ))

    return all_data

def format_result_to_json(result: List[ReturnFormat]) -> List[dict[str, any]]:
    """Функция для форматирования результата в JSON-формат."""
    formatted_result = []

    for return_format in result:
        for chunk in return_format.chunk_text:
            formatted_result.append({
                "doc_id": "1",  # фиксируем значение
                "content": return_format.full_chapter_text,
                "chunk": {
                    "chunk_id": f"doc_1_chunk_{len(formatted_result)}",
                    "original_index": len(formatted_result),
                    "content": chunk.chunk_text,
                    "version": "1",
                    "link": chunk.link
                }
            })

    return formatted_result

if __name__ == "__main__":
    section_links = parse_links("https://company.rzd.ru/ru/9353/page/105104?id=1604#7275")
    result = parsing_data_from_web()
    formatted_json = format_result_to_json(result)
    print(json.dumps(formatted_json, indent=2, ensure_ascii=False))
    # vector_db = VectorDB()
    # vector_db.load_data(formatted_json)
    # iix = get_index('../data/bm')
    # indexing_document(iix, formatted_json)
