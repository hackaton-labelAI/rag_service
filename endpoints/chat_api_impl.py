from endpoints.apis.chat_api_base import BaseChatApi
from endpoints.models.chat_context import ChatContext
from endpoints.models.chat_rag_data import ChatRAGData
from endpoints.models.rag_response_data import RAGResponseData
from services.answer_service import resolve_issue
from services.gpt_service import ranking
from services.search import search
import asyncio
from endpoints.ws.chat_ws import generate_results


class ChatApiImpl(BaseChatApi):
    async def chat(self, chat_context: ChatContext) -> RAGResponseData:
        if len(chat_context.context) >= 2:
            context = chat_context.context[-5:]
            query = context[-1].text_data.content
            texts = await resolve_issue(query)
            tasks = [search(id, text) for id, text in enumerate(texts)]
            results = await asyncio.gather(*tasks)
            res = {}
            for task in results:
                for chunk in task:
                    if chunk['chunk_id'] not in res:
                        res[chunk['chunk_id']] = chunk

            resp = list(res.values())
            dd = await ranking(query, resp)
            cc = []
            for item in dd:
                cc.append(ChatRAGData(chunk_text=item['original_content']))
            chat_history = [ll.text_data for ll in context]
            asyncio.create_task(generate_results(chat_context.session_id, dd, chat_history))
            return RAGResponseData(
                id="test",
                status="ok",
                data=cc
            )
        else:

            texts = await resolve_issue(chat_context.context[0].text_data.content)
            tasks = [search(id, text) for id, text in enumerate(texts)]
            results = await asyncio.gather(*tasks)
            res = {}  # Инициализируем пустой словарь для хранения уникальных chunk

            for task in results:
                for chunk in task:
                    if chunk['chunk_id'] not in res:
                        res[chunk['chunk_id']] = chunk

            resp = list(res.values())
            dd = await ranking(chat_context.context[0].text_data.content, resp)

            cc=[]
            for item in dd:
                cc.append(ChatRAGData(chunk_text=item['original_content']))
            chat_history = [ll.text_data for ll in chat_context.context]
            asyncio.create_task(generate_results(chat_context.session_id, dd, chat_history))
            return RAGResponseData(
                id= "test",
                status = "ok",
                data=cc
            )

        # return await super().chat(chat_context)