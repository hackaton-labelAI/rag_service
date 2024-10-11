from endpoints.apis.chat_api_base import BaseChatApi
from endpoints.models.chat_context import ChatContext
from endpoints.models.rag_response_data import RAGResponseData
from services.answer_service import resolve_issue
from services.search import search
import asyncio




class ChatApiImpl(BaseChatApi):
    async def chat(self, chat_context: ChatContext) -> RAGResponseData:
        if len(chat_context) >= 2:
            pass
        else:
            texts = resolve_issue(chat_context)
            tasks = [search(id, text) for id, text in enumerate(texts)]
            return await asyncio.gather(*tasks)
        # return await super().chat(chat_context)