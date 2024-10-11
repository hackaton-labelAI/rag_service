import asyncio
import os
import aiohttp
from annoy import AnnoyIndex

f = 1536
t = AnnoyIndex(f, 'angular')

async def vectorizer_text(id: int, text: str):
    vector = await vectorize_text(text)
    t.add_item(id, vector)


def save_vectors():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(current_dir, '../data/vectorize.ann')

    t.build(50)
    t.save(file_path)

async def find_closest_vectors(text: str):
    vector = await vectorize_text(text)
    return t.get_nns_by_vector(vector, 10)

async def load_vectorizer():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(current_dir, '../data/vectorize.ann')

    t.load(file_path)

async def vectorize_text(text: str):
    url = 'https://caila.io/api/mlpgateway/account/1000062767/model/51056/predict'
    api_token = os.environ.get('MLP_TOKEN', '1000097868.110610.cfUF9zxN1MD7Ot8IHmr48LLXdtDv9Do9T9RZkfSL')

    headers = {
        'MLP-API-KEY': api_token,
        'Content-Type': 'application/json'
    }

    payload = {
        'texts': [text]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result['embedded_texts'][0]['vector']
            else:
                print(response)
                print(f"Error: {response.status}")
                return None


# async def main():
    # texts = [
    #     "Привет, мир!!!",
    #     "Это первая строка.",
    #     "Вот еще одна строка.",
    #     "Текст для векторизации.",
    #     "Асинхронное программирование.",
    #     "Python — мощный язык.",
    #     "Изучение новых технологий.",
    #     "Продолжение следует.",
    #     "Асинхронные функции.",
    #     "Финальная строка."
    # ]
    #
    # tasks = [vectorizer_text(id, text) for id, text in enumerate(texts)]
    # await asyncio.gather(*tasks)
    # save_vectors()

#     await load_vectorizer()
#
#     d = await find_closest_vectors("Сегодня мы поговорим про векторизацию")
#     print(d)
#
# # Запуск основной функции
# asyncio.run(main())
