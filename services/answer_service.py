import asyncio
import json
from typing import List
from services.prompts import prompt_multiplication
from endpoints.models.chat_context import ChatContext
from services.find_service import ranking, find_chunks
from services.gpt_service import fetch_completion


def answer_in_chat(chat_context: ChatContext):
    strs = resolve_issue()
    res = []
    for str in strs:
        find_chunks(str)
    res = ranking(res)
    # начать генерацию ответа в ws
    return res
    pass


async def resolve_issue(question: str)-> List[str]:
    arr_questions = []

    res = await fetch_completion(prompt_multiplication % (str(question)))

    try:
        json_data = json.loads(res['full_text'])
        # print(json_data)
    except json.JSONDecodeError as e:
        print(f"Ошибка при преобразовании в JSON: {e}")
        json_data = None

    # print(json(res['full_text']))
    return json_data['arr']
result = asyncio.run(resolve_issue('Есть ли у меня привилегии если я работаю в РЖД?'))

print(result)
