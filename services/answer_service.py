import asyncio
import json
from typing import List
from services.prompts import prompt_multiplication
from endpoints.models.chat_context import ChatContext
from services.find_service import ranking, find_chunks
from services.gpt_service import fetch_completion


def answer_in_chat(chat_context: ChatContext):
    # strs = resolve_issue()
    res = []
    # for str in strs:
    #     find_chunks(str)
    # res = ranking(res)
    # начать генерацию ответа в ws
    return res
    pass


async def resolve_issue(question: str)-> List[str]:
    arr_questions = []

    try:
        response = await fetch_completion(prompt_multiplication % (str(question)))
        lines = response['full_text'].split('\n')

        questions = []

        for line in lines:
            line = line.strip()
            if line and line[0].isdigit():  # Проверяем, начинается ли строка с числа
                questions.append(line)  # Добавляем в массив

        return questions
    except json.JSONDecodeError as e:
        print(f"Ошибка при преобразовании в JSON: {e}")
        return [question]
