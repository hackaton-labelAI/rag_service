import asyncio
import re
from typing import List
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic.dataclasses import dataclass
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

@dataclass
class ReturnFormat:
    chunk_text: List[ChunkData]
    full_chapter_text: str

# Загружаем токенизатор BERT
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
from typing import List
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic.dataclasses import dataclass
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

@dataclass
class ReturnFormat:
    chunk_text: List[ChunkData]
    full_chapter_text: str

# Загружаем токенизатор BERT
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def token_length_function(text):
    """Функция для подсчета количества токенов в тексте."""
    tokens = bert_tokenizer.encode(text, truncation=False)
    return len(tokens)

def parsing_data_from_pdf(file_name: str, token_chunk: int = 250, overlay: int = 50) -> List[ReturnFormat]:
    file_path = f'../data/{file_name}'

    loader = PyPDFLoader(file_path)
    file = loader.load()
    content = ''.join(file[i].page_content for i in range(len(file)))
    pattern = r'(Раздел \d+\.\s[^\n]+)(.*?)(?=Раздел \d+\.|$)'
    sections = re.findall(pattern, content, re.DOTALL)
    texts = [{'label': section[0], 'text': section[1].strip()} for section in sections]

    result = []
    for text in texts:
        parsed_data = parsing_data_from_text([text], token_chunk, overlay)
        result.extend(parsed_data)
    return result

def parsing_data_from_web(token_chunk: int = 450, overlay: int = 100) -> List[ReturnFormat]:
    loader = WebBaseLoader(['https://company.rzd.ru/ru/9353/page/105104?id=1604#navPart_7274'])
    file = loader.load()
    content = ''.join(file[i].page_content for i in range(len(file)))
    pattern = r'(Раздел \d+\.\s[^\n]+)(.*?)(?=Раздел \d+\.|$)'
    sections = re.findall(pattern, content, re.DOTALL)

    texts = [{'label': section[0].strip(), 'text': section[1].strip()} for section in sections if section[1].strip()]

    result = []
    for text in texts:
        parsed_data = parsing_data_from_text([text], token_chunk, overlay)
        result.extend(parsed_data)

    return result

def parsing_data_from_text(content: List[dict], token_chunk: int = 450, overlay: int = 100) -> List[ReturnFormat]:
    all_data = []

    for text in content:
        chunk_data_list = []

        # Создание объекта RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=token_chunk,
            chunk_overlap=overlay,
            length_function=token_length_function
        )

        # Разделение текста на чанки
        chunks = text_splitter.split_text(text['text'])
        for chunk in chunks:
            chunk = chunk.strip()  # Удаляем лишние пробелы

            # Добавляем чанк, только если он не пустой и имеет осмысленное содержание
            if len(chunk) > 10 and not chunk.startswith("Раздел"):  # Избегаем заголовков и слишком коротких чанков
                chunk_data = ChunkData(
                    chunk_text=chunk,
                    data=[dr(version=1, label=text['label'], text=chunk)]
                )
                chunk_data_list.append(chunk_data)

        all_data.append(ReturnFormat(
            chunk_text=chunk_data_list,
            full_chapter_text=text['text']
        ))

    return all_data

def format_result_to_json(result: List[ReturnFormat]) -> List[dict[str, any]]:
    formatted_result = {}

    for return_format in result:
        for chunk in return_format.chunk_text:
            original_uuid = chunk.data[0].label

            if original_uuid not in formatted_result:
                formatted_result[original_uuid] = {
                    "doc_id": "1",  # фиксируем значение
                    "content": return_format.full_chapter_text,
                    "chunks": [],
                }

            formatted_result[original_uuid]["chunks"].append({
                "chunk_id": f"doc_1_chunk_{len(formatted_result[original_uuid]['chunks'])}",
                "original_index": len(formatted_result[original_uuid]["chunks"]),
                "content": chunk.chunk_text,
                "version": "1"
            })

    return list(formatted_result.values())

if __name__ == "__main__":
    result = parsing_data_from_web()
    formatted_json = format_result_to_json(result)
    print(json.dumps(formatted_json, indent=2, ensure_ascii=False))


def token_length_function(text):
    """Функция для подсчета количества токенов в тексте."""
    tokens = bert_tokenizer.encode(text, truncation=False)
    return len(tokens)


def parsing_data_from_pdf(file_name: str, token_chunk: int = 250, overlay: int = 50) -> List[ReturnFormat]:
    file_path = f'../data/{file_name}'

    loader = PyPDFLoader(file_path)
    file = loader.load()
    content = ''.join(file[i].page_content for i in range(len(file)))
    pattern = r'(Раздел \d+\.\s[^\n]+)(.*?)(?=Раздел \d+\.|$)'
    sections = re.findall(pattern, content, re.DOTALL)
    texts = [{'label': section[0], 'text': section[1].strip()} for section in sections]
    result = []
    for text in texts:
        parsed_data = parsing_data_from_text([text], token_chunk, overlay)
        result.extend(parsed_data)
    return result

def parsing_data_from_web(token_chunk: int = 450, overlay: int = 100) -> List[ReturnFormat]:
    loader = WebBaseLoader(['https://company.rzd.ru/ru/9353/page/105104?id=1604#navPart_7274'])
    file = loader.load()
    content = ''.join(file[i].page_content for i in range(len(file)))
    pattern = r'(Раздел \d+\.\s[^\n]+)(.*?)(?=Раздел \d+\.|$)'
    sections = re.findall(pattern, content, re.DOTALL)

    texts = [{'label': section[0].strip(), 'text': section[1].strip()} for section in sections if section[1].strip()]

    result = []
    for text in texts:
        parsed_data = parsing_data_from_text([text], token_chunk, overlay)
        result.extend(parsed_data)

    return result

def parsing_data_from_text(content: List[dict], token_chunk: int = 450, overlay: int = 100) -> List[ReturnFormat]:
    all_data = []

    for text in content:
        chunk_data_list = []

        # Создание объекта RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=token_chunk,
            chunk_overlap=overlay,
            length_function=token_length_function
        )

        # Разделение текста на чанки
        chunks = text_splitter.split_text(text['text'])
        for chunk in chunks:
            chunk = chunk.strip()  # Удаляем лишние пробелы

            # Добавляем чанк, только если он не пустой и имеет осмысленное содержание
            if len(chunk) > 10 and not chunk.startswith("Раздел"):  # Избегаем заголовков и слишком коротких чанков
                chunk_data = ChunkData(
                    chunk_text=chunk,
                    data=[dr(version=1, label=text['label'], text=chunk)]
                )
                chunk_data_list.append(chunk_data)

        all_data.append(ReturnFormat(
            chunk_text=chunk_data_list,
            full_chapter_text=text['text']
        ))

    return all_data

def format_result_to_json(result: List[ReturnFormat]) -> List[dict[str, any]]:
    formatted_result = {}

    for return_format in result:
        for chunk in return_format.chunk_text:
            original_uuid = chunk.data[0].label

            if original_uuid not in formatted_result:
                formatted_result[original_uuid] = {
                    "doc_id": "1",  # фиксируем значение
                    "content": return_format.full_chapter_text,
                    "chunks": [],
                }


            formatted_result[original_uuid]["chunks"].append({
                "chunk_id": f"doc_1_chunk_{len(formatted_result[original_uuid]['chunks'])}",
                "original_index": len(formatted_result[original_uuid]["chunks"]),
                "content": chunk.chunk_text,
                "version": "1"
            })

    return list(formatted_result.values())

if __name__ == "__main__":
    result = parsing_data_from_web()
    formatted_json = format_result_to_json(result)
    print(json.dumps(formatted_json, indent=2, ensure_ascii=False))