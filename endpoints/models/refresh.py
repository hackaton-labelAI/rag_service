import asyncio
import re
from typing import List
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic.dataclasses import dataclass
import datetime
from indexing.parse_data_service import parsing_data_from_web, format_result_to_json, ChunkData
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.vector_bd import VectorDB
from services.bm25_search_service import get_index, indexing_document
from transformers import AutoTokenizer

app = FastAPI()
scheduler = AsyncIOScheduler()

@dataclass
class dr:
    version: int
    label: str
    text: str

@dataclass
class ReturnFormat:
    chunk_text: List[ChunkData]
    full_chapter_text: str

bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def token_length_function(text):
    tokens = bert_tokenizer.encode(text, truncation=False)
    return len(tokens)

async def update_vector_db():
    result = parsing_data_from_web()
    formatted_json = format_result_to_json(result)
    vector_db = VectorDB()
    vector_db.load_data(formatted_json)
    iix = get_index('../data/bm')
    indexing_document(iix, formatted_json)
    print("Векторная база данных обновлена.")

@app.on_event("startup")
async def startup_event():
    first_run_time = datetime.datetime.now() + datetime.timedelta(days=3)
    first_run_time = first_run_time.replace(hour=0, minute=0, second=0, microsecond=0)
    scheduler.add_job(update_vector_db, 'date', run_date=first_run_time)
    scheduler.add_job(update_vector_db, 'cron', week='*', hour=0, minute=0, id='weekly_update')
    scheduler.start()
    await update_vector_db()

@app.get("/update")
async def manual_update():
    await update_vector_db()
    return {"message": "Векторная база данных обновлена."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
