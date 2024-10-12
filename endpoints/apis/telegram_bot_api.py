from typing import List, Dict

from fastapi import APIRouter, Body

from endpoints.ws.chat_ws import df, knowledge_base_path
from services.gpt_service import stream_output

router = APIRouter()

@router.post(
    "/api/telegram_get_response",
    tags=["document"],
)
async def get_response(data: Dict = Body(None, description="")):
    question = data['question']
    files = data['chunks']

    answer = await stream_output(None, files, None)

    df.loc[len(df)] = [None, None, None, None, question, None, None, None, None, None, None, None, None, answer,
                       files, None]
    df.to_csv(knowledge_base_path, index=False)

    return answer

