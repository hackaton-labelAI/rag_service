import uuid
import pandas
from openai import AsyncOpenAI
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import requests
from requests import session
import json
from services.gpt_service import stream_output

router = APIRouter()

# Словарь для хранения соответствий user_id и WebSocket
knowledge_base_path = 'data/База знаний.csv'
active_connections = {}
df = pandas.read_csv(knowledge_base_path)


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    # Генерация уникального идентификатора пользователя
    user_id = str(uuid.uuid4())

    # Сохраняем WebSocket в словаре
    active_connections[user_id] = websocket

    generation_task = None
    await websocket.send_text(f'{{"session_id": "{user_id}"}}')
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("/stop"):
                break

            continue
    except asyncio.CancelledError:
        await websocket.send_text("[INFO] Генерация была прервана")
    finally:
        # Удаляем WebSocket из словаря при отключении
        del active_connections[user_id]


async def generate_results(user_id, files, chat_history):
    if user_id is not None:
        websocket = active_connections.get(user_id)
        if websocket is None:
            raise ValueError(f"WebSocket с user_id {user_id} не найден.")
    else:
        websocket = None

    # Выполняем асинхронный запрос к gpt_service
    answer = await stream_output(chat_history, files, websocket)

    TOKEN = '1000097868.110610.cfUF9zxN1MD7Ot8IHmr48LLXdtDv9Do9T9RZkfSL'
    openai = AsyncOpenAI(
        api_key=TOKEN,
        base_url="https://caila.io/api/adapters/openai"
    )

    def fetch_completion(prompt):
        url = "https://caila.io/api/adapters/openai/chat/completions"
        headers = {
            'Authorization': TOKEN,
            'Content-Type': 'application/json',
        }
        data = {
            "model": "just-ai/openai-proxy/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "stream": False
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            response_data = response.json()
            full_text = response_data.get('choices')[0].get('message').get('content')
            model = response_data.get('model', 'gpt-3.5-turbo')

            return {
                "full_text": full_text,
                "model": model
            }
        except Exception as e:
            return {"error": str(e)}

    prompt = """
        На вход тебе подается вопрос от пользователя %s
        Тебе необходимо относительно этого вопроса вернуть следующие характеристики:
        1) 'category' : категория вопроса 
        2) 'tegs': теги характерезующие вопрос от 2 до 4 шт
        3) 'f1': вопрос перефразированный формально 
        4) 'f2': вопрос перефразированный формально 
        5) 'f3': вопрос перефразированный формально 
        6) 'nf1': вопрос перефразированный неформально 
        7) 'nf2': вопрос перефразированный неформально 
        8) 'nf3': вопрос перефразированный неформально 
        9)  's1': вопрос перефразированный c сокращением
        10) 's2': вопрос перефразированный c сокращением
        11) 's3': вопрос перефразированный c сокращением

        Важно: f1, f2, f3, nf1, nf2, nf3, s1, s2, s3 должны быть уникальными
        Верни только json в следующем виде:
        {'category': <str>,
         'tegs': <str>,
         'f1': <str>,
         'f2': <str>,
         'f3': <str>, 
         'nf1': <str>,
         'nf2': <str>,
         'nf3': <str>, 
         's1': <str>,
         's2': <str>,
         's3': <str>, 
        }
        """

    # Получаем ответ от AI
    res = fetch_completion(prompt % str(chat_history))

    # Проверка на наличие ошибки
    if "error" in res:
        print(f"Ошибка при вызове API: {res['error']}")
        return

    try:
        # Парсим ответ в JSON
        response_json = json.loads(res['full_text'])

        # Проверка наличия всех ключей в JSON
        expected_keys = ['category', 'tegs', 'f1', 'f2', 'f3', 'nf1', 'nf2', 'nf3', 's1', 's2', 's3']
        if not all(key in response_json for key in expected_keys):
            raise ValueError("Некоторые ключи отсутствуют в ответе от API")

        category = response_json['category']
        tegs = response_json['tegs']
        f1, f2, f3 = response_json['f1'], response_json['f2'], response_json['f3']
        nf1, nf2, nf3 = response_json['nf1'], response_json['nf2'], response_json['nf3']
        s1, s2, s3 = response_json['s1'], response_json['s2'], response_json['s3']
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Ошибка обработки данных: {e}")
        return

    # Добавление строки в DataFrame и сохранение в CSV
    try:
        df.loc[len(df)] = [
            df.shape[0] + 1, category, tegs, chat_history, f1, f2, f3, nf1, nf2, nf3, s1, s2, s3, answer, None, None
        ]
        df.to_csv(knowledge_base_path, index=False)
    except Exception as e:
        print(f"Ошибка при записи в CSV: {e}")
