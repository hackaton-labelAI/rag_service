import json
from typing import List
from openai import AsyncOpenAI
from whoosh.scoring import dfree

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
            model="just-ai/openai-proxy/gpt-4o",
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

        model="just-ai/openai-proxy/gpt-4o",
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