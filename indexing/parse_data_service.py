import re
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic.dataclasses import dataclass
import tiktoken


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


tokenizer = tiktoken.get_encoding("cl100k_base")

def token_length_function(text):
    """Функция для подсчета количества токенов в тексте."""
    tokens = tokenizer.encode(text)
    return len(tokens)


def parsing_data_from_pdf(file_name: str, token_chunk: int = 250, overlay: int = 50) -> List[ReturnFormat]:
    file_path = f'../data/{file_name}'

    loader = PyPDFLoader(file_path)
    file = loader.load()
    content = ''.join(file[i].page_content for i in range(len(file)))
    return parsing_data_from_text(content, token_chunk, overlay)



def parsing_data_from_text(content: str, token_chunk: int = 250, overlay: int = 50) -> List[ReturnFormat]:
    pattern = r'(Раздел \d+)(.*?)(?=Раздел \d+|$)'
    sections = re.findall(pattern, content, re.DOTALL)

    texts = [{'label': section[0], 'text': section[1].strip()} for section in sections]

    chunk_data_list = []

    all_data = []

    for text in texts:
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ".", ",", ";"],
            chunk_size=token_chunk,
            chunk_overlap=overlay,
            length_function=token_length_function,
            is_separator_regex=False,
            add_start_index=True
        )
        text_chunks = text_splitter.split_text(text['text'])

        current_position = 0

        for chunk in text_chunks:
            # Получаем начало и конец чанка в оригинальном тексте
            start_char_idx = content.find(chunk, current_position)
            end_char_idx = start_char_idx + len(chunk)

            # Если не нашли кусок, продолжаем
            if start_char_idx == -1:
                print(f"Chunk not found in content: {chunk}")
                continue

            chunk_data = ChunkData(
                char_position_start=start_char_idx,
                char_position_end=end_char_idx,
                chunk_text=chunk,
                chapter=text['label']
            )
            chunk_data_list.append(chunk_data)

            current_position = end_char_idx

        all_data.append(ReturnFormat(
            chunk_text=chunk_data_list,
            full_chapter_text=content
        ))

    return all_data

#  APPROVED
if __name__ == "__main__":
    result = parsing_data_from_pdf('dd.pdf')
    for i, return_format in enumerate(result):
        print(f"Total chunks in section {i}: {len(return_format.chunk_text)}")
        for chunk in return_format.chunk_text:
            print(
                f"Chunk Text: {chunk.chunk_text}, Start: {chunk.char_position_start}, End: {chunk.char_position_end}, Chapter: {chunk.chapter}")

print(f"all_data must be 12, but real: {len(result)}")