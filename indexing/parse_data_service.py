import asyncio
import re
from typing import List
from venv import create

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic.dataclasses import dataclass
import tiktoken

from indexing.indexing_chunk_serivece import indexing_file, ReturnFormat, ChunkData
from services.gpt_service import interaction_with_llm

tokenizer = tiktoken.get_encoding("cl100k_base")

def token_length_function(text):
    """Функция для подсчета количества токенов в тексте."""
    tokens = tokenizer.encode(text)
    return len(tokens)


def parsing_data_from_pdf(file_name: str, token_chunk: int = 300, overlay: int = 50) -> str:
    file_path = f'../data/{file_name}'

    loader = PyPDFLoader(file_path)
    file = loader.load()
    content = ''.join(file[i].page_content for i in range(len(file)))
    return indexing_data_from_text(content, token_chunk, overlay)



def indexing_data_from_text(text: str, token_chunk: int = 300, overlay: int = 50) -> List[ReturnFormat]:
    chunk_data_list = []

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ".", ",", ";"],
        chunk_size=token_chunk,
        chunk_overlap=overlay,
        length_function=token_length_function,
        is_separator_regex=False,
        add_start_index=True
    )
    text_chunks = text_splitter.split_text(text)
    for text_chunk in text_chunks:
        chunk = create_final_chunk(text, text_chunk)
        add_to_bm25()
        add_to_vector_store()
        chunk_data_list.append(chunk)


    return all_data

#  APPROVED
if __name__ == "__main__":
    content = parsing_data_from_pdf('dd.pdf')
    content = content[102]
    print(content)
    # sentences = content.split('.')

    # numbered_sentences = [f"{i + 1}-> {sentence.strip()}" for i, sentence in enumerate(sentences) if sentence.strip()]

    # numbered_content = '. '.join(numbered_sentences)
    # print(numbered_content)
    # asyncio.run(indexing_file(content))


    # leng = 0
    # for dd in chunks:
    #     leng += len(dd.chunk_text)
    # print(leng)
    # asyncio.run(indexing_file(chunks))
    # for i, return_format in enumerate(result):
    #     print(f"Total chunks in section {i}: {len(return_format.chunk_text)}")
    #     for chunk in return_format.chunk_text:
    #         print(f"Chunk Text: {chunk.chunk_text}, Start: {chunk.char_position_start}, End: {chunk.char_position_end}, Chapter: {chunk.chapter}")
    #         print(f"Full Chapter Text: {return_format.full_chapter_text}")

# print(f"all_data must be 12, but real: {len(result)}")