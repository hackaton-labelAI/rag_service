from typing import List, Dict

from fastapi import APIRouter, Body
from pydantic import BaseModel

from endpoints.ws.chat_ws import df, knowledge_base_path
from services.gpt_service import stream_output, output
from services.search import search

router = APIRouter()

class InputModel(BaseModel):
    question: str
    chunks: List

@router.post(
    "/api/telegram_get_response",
    tags=["document"],
)
async def get_response(data: InputModel):
    question = data.question

    files = await search(None, question)

    answer = await output(question, files)

    df.loc[len(df)] = [None, None, None, None, question, None, None, None, None, None, None, None, None, answer,
                       files, None]
    df.to_csv(knowledge_base_path, index=False)

    return answer
