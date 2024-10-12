from endpoints.apis.chat_api_base import BaseChatApi
from endpoints.models.chat_context import ChatContext
from endpoints.models.chat_rag_data import ChatRAGData
from endpoints.models.rag_response_data import RAGResponseData
from services.answer_service import resolve_issue
from services.gpt_service import ranking
from services.search import search
import asyncio




class ChatApiImpl(BaseChatApi):
    async def chat(self, chat_context: ChatContext) -> RAGResponseData:
        if len(chat_context.context) >= 2:
            pass
        else:
            res = {}
            texts = await resolve_issue(chat_context.context[0].text_data.content)
            tasks = [search(id, text) for id, text in enumerate(texts)]
            results = await asyncio.gather(*tasks)
            for task in results:
                for chunk in task:
                    res[chunk['chunk_id']] = chunk
            resp = list(res.values())
            dd = await ranking(chat_context.context[0].text_data.content, resp)

            cc=[]
            for item in dd:
                cc.append(ChatRAGData(chunk_text=item['contextualized_content']))
            return RAGResponseData(
                id= "test",
                status = "ok",
                data=cc
            )

        # return await super().chat(chat_context)