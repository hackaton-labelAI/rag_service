import asyncio
import json
import os
import pickle
from typing import List, Dict, Any

import aiohttp
from annoy import AnnoyIndex
from openai import AsyncOpenAI
from tqdm import tqdm


class VectorDB:
    def __init__(self):
        self.f = 768
        self.t = AnnoyIndex(self.f, 'angular')
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.chunks = []
        self.db_path = os.path.join(current_dir, '../data/vectorize.ann')
        self.data_path = os.path.join(current_dir, '../data/data.txt')
        self.query_cache = {}
        TOKEN = '1000097868.110610.cfUF9zxN1MD7Ot8IHmr48LLXdtDv9Do9T9RZkfSL'
        self.openai = AsyncOpenAI(
            api_key=TOKEN,
            base_url="https://caila.io/api/adapters/openai"
        )

    async def situate_context(self, doc: str, chunk: str) -> str:
        DOCUMENT_CONTEXT_PROMPT = """
        <document>
        {doc_content}
        </document>
        """

        CHUNK_CONTEXT_PROMPT = """
        Here is the chunk we want to situate within the whole document
        <chunk>
        {chunk_content}
        </chunk>

        Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
        Answer only with the succinct context and nothing else.
        """

        response = await self.openai.chat.completions.create(
            model="just-ai/openai-proxy/gpt-4o",
            max_tokens=1000,
            temperature=0.0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": DOCUMENT_CONTEXT_PROMPT.format(doc_content=doc),
                            "cache_control": {"type": "ephemeral"}  # we will make use of prompt caching for the full documents
                        },
                        {
                            "type": "text",
                            "text": CHUNK_CONTEXT_PROMPT.format(chunk_content=chunk),
                        },
                    ]
                },
            ],
            extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
        )

        return response.choices[0].message.content

    async def load_data(self, dataset: List[Dict[str, Any]], parallel_threads: int = 10, addData=False):
        if not addData:
            if os.path.exists(self.db_path):
                print("Loading vector database from disk.")
                self.load_db()
                return

        async def process_chunk(doc, chunk, current_id):
            contextualized_text = await self.situate_context(doc['content'], chunk['content'])
            full_text = f"{chunk['content']}\n\n{contextualized_text}"
            vector = await self.vectorize_text(full_text)
            self.chunks.append({
                'doc_id': doc['doc_id'],
                'chunk_id': chunk['chunk_id'],
                'original_index': chunk['original_index'],
                'original_content': chunk['content'],
                'contextualized_content': f"{chunk['content']}\n\n{contextualized_text}",
                'version': chunk['version']
            })
            self.t.add_item(len(self.chunks) - 1, vector)

        semaphore = asyncio.Semaphore(parallel_threads)

        async def limited_process_chunk(doc, chunk, current_id):
            async with semaphore:
                await process_chunk(doc, chunk, current_id)

        tasks = []
        current_id = len(self.chunks)
        for doc in dataset:
            for chunk in doc['chunks']:
                tasks.append(limited_process_chunk(doc, chunk, current_id))
                current_id += 1

        # Use asyncio.gather for parallel processing instead of as_completed
        await asyncio.gather(*tasks)

        self.save_db()

    def save_db(self):
        self.t.build(50)
        self.t.save(self.db_path)
        with open(self.data_path, "wb") as file:
            pickle.dump(self.chunks, file)

    def load_db(self):
        if not os.path.exists(self.db_path):
            raise ValueError("Vector database file not found. Use load_data to create a new database.")
        self.t.load(self.db_path)
        with open(self.data_path, "rb") as file:
            self.chunks = pickle.load(file)

    async def search(self, query: str, k: int = 20) -> List[Dict[str, Any]]:
        if query in self.query_cache:
            query_embedding = self.query_cache[query]
        else:
            query_embedding = await self.vectorize_text(query)
            self.query_cache[query] = query_embedding

        similarities = self.t.get_nns_by_vector(query_embedding, k)

        return [self.chunks[i] for i in similarities]

    async def vectorize_text(self, query: str):
        url = 'https://caila.io/api/mlpgateway/account/1000062767/model/26534/predict'
        api_token = os.environ.get('MLP_TOKEN', '1000097868.110610.cfUF9zxN1MD7Ot8IHmr48LLXdtDv9Do9T9RZkfSL')

        headers = {
            'MLP-API-KEY': api_token,
            'Content-Type': 'application/json'
        }

        payload = {
            'texts': [query]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['embedded_texts'][0]['vector']
                else:
                    print(f"Error: {response.status}")
                    return None


async def main():
    v_db = VectorDB()
    with open('../data/main_chunks.json', 'r') as f:
        transformed_dataset = json.load(f)
    await v_db.load_data(transformed_dataset)
    await v_db.search("какие у меня есть привелегии?")

if __name__ == "__main__":
    asyncio.run(main())
