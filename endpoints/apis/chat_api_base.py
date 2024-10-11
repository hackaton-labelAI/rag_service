# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from endpoints.models.chat_context import ChatContext
from endpoints.models.rag_response_data import RAGResponseData


class BaseChatApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseChatApi.subclasses = BaseChatApi.subclasses + (cls,)
    async def chat(
        self,
        chat_context: ChatContext,
    ) -> RAGResponseData:
        ...
