import asyncio
import re

from click import prompt
from openai import AsyncOpenAI

from services.prompts import generate_chunks_prompt

TOKEN = '1000097868.110610.cfUF9zxN1MD7Ot8IHmr48LLXdtDv9Do9T9RZkfSL'
openai = AsyncOpenAI(
    api_key=TOKEN,
    base_url="https://caila.io/api/adapters/openai"
)


def create_final_chunk(text, chunk):
    pass


async def fetch_completion(prompt: str):
    try:
        res = await openai.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="just-ai/vllm-qwen2-72b-awq",
            temperature=0,
            response_format={"type": "json_object"},
            stream=False
        )

        response_json = res
        input_tokens = int(res.usage.prompt_tokens)
        output_tokens = int(res.usage.completion_tokens)
        content = res.choices[0].message.content

        return {
            "response_json": response_json,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "full_text": content
        }
    except Exception as e:
        print(f"error {e}")


async def ranking(query, chunks):
    def chunks_to_string(data):
        res = ""
        for i, item in enumerate(data):
            res += f"{i} -> {item['contextualized_content']}"
        return res

    ranking_prompt = f"""
    Тебе надо отранжировать записи которые наиболее чётко соответствуют запросу пользователя, те которые вообще о другом не возвращать
    
    Запрос:
    {query}
    
    Записи:
    {chunks_to_string(chunks)}
    
    Формат ответа: номер записи, новая строка и так от лучшего к худшему. НОМЕР ЗАПИСИ ПОВТОРЯТЬСЯ НЕ МОЖЕТ   
    """
    res = await fetch_completion(ranking_prompt)
    numbers = re.findall(r'\d+', res['full_text'])

    numbers = [int(num) for num in numbers]

    unique_numbers = []
    seen = set()

    for num in numbers:
        if num not in seen:
            seen.add(num)
            unique_numbers.append(num)

    result = []
    for index in unique_numbers:  # Используем уникальные индексы
        result.append(next((item for item in chunks if item["original_index"] == 2), None))
    return result


async def interaction_with_llm(document: str):
    res = await openai.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": generate_chunks_prompt(document),
                    }
                ]
            }
        ],

        model="just-ai/vllm-qwen2-72b-awq",
        temperature=0,
        stream=False
    )

    response_json = res
    input_tokens = int(res.usage.prompt_tokens)
    output_tokens = int(res.usage.completion_tokens)
    content = res.choices[0].message.content

    return {
        "response_json": response_json,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "full_text": content
    }


async def stream_output(chat_history, chunks, websocket):
    prompt_output = f"""
    Ответь на вопрос пользователя исходя из документов  <документы>{[chunk['contextualized_content'] for chunk in chunks]}</документы> или 
    из истории чата. Запрещено употреблять нецензурную лексику, иначе котики погибнут. 
    В идеале делать чуть ли не прямую цитату из документов.
    """
    try:
        if chat_history is not None:
            dd = chat_history
        else:
            dd = []
        dd.append({"role": "user", "content": prompt_output})
        res = await openai.chat.completions.create(
            messages=dd,
            model="just-ai/vllm-qwen2-72b-awq",
            temperature=0,
            stream=True
        )

        answer = ""
        async for chunk in res:
            content = chunk.choices[0].delta.content
            answer += content
            await websocket.send_text(f'{{"llm_message": "{content}"}}')
        await websocket.send_text('{"llm_message": "<|endoftext|>"}')

        return answer
    except Exception as e:
        print(f"error {e}")

async def output(chat_history, chunks):
    prompt_output = f"""
    Ответь на вопрос пользователя {chat_history} исходя из документов  <документы>{[chunk['contextualized_content'] for chunk in chunks]}</документы> или 
    из истории чата. Запрещено употреблять нецензурную лексику, иначе котики погибнут. 
    В идеале делать чуть ли не прямую цитату из документов.
    """
    try:
        dd =[]
        dd.append({"role": "user", "content": prompt_output})
        res = await openai.chat.completions.create(
            messages=dd,
            model="just-ai/vllm-qwen2-72b-awq",
            temperature=0,
            stream=False
        )

        response_json = res
        input_tokens = int(res.usage.prompt_tokens)
        output_tokens = int(res.usage.completion_tokens)
        content = res.choices[0].message.content

        return content

    except Exception as e:
        print(f"error {e}")

# async def get_response_from_llm(users_question, chunks):
#     res = await openai.chat.completions.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": generate_chunks_prompt(document),
#                     }
#                 ]
#             }
#         ],
#
#         model="just-ai/vllm-qwen2-72b-awq",
#         temperature=0,
#         stream=False
#     )
#
#     response_json = res
#     input_tokens = int(res.usage.prompt_tokens)
#     output_tokens = int(res.usage.completion_tokens)
#     content = res.choices[0].message.content
#
#     return {
#         "response_json": response_json,
#         "input_tokens": input_tokens,
#         "output_tokens": output_tokens,
#         "full_text": content
#     }


if __name__ == "__main__":
    asyncio.run(ranking("Какие льготы получит сын если я умру?", [{'contextualized_content': 'Трава сегодня красивая'},
                                                                  {
                                                                      'contextualized_content': 'Если кот умрёт его надо похоранить'},
                                                                  {
                                                                      'contextualized_content': 'Получит выплату в размере 1 миллион'}]))
