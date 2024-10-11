from endpoints.apis.chat_api_base import BaseChatApi
from endpoints.models.chat_context import ChatContext
from endpoints.models.rag_response_data import RAGResponseData


class ChatApiImpl(BaseChatApi):
    async def chat(self, chat_context: ChatContext) -> RAGResponseData:
        return await super().chat(chat_context)