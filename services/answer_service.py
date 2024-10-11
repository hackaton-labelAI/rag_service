from typing import List

from endpoints.models.chat_context import ChatContext
from services.find_service import ranking, find_chunks


def answer_in_chat(chat_context: ChatContext):
    strs = resolve_issue()
    res = []
    for str in strs:
        find_chunks(str)
    res = ranking(res)
    # начать генерацию ответа в ws
    return res
    pass


def resolve_issue(question: str)-> List[str]:
    pass

