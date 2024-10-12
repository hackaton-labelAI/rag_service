import uuid
import pandas

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

from services.gpt_service import stream_output

# from services.text_generation import generate_text

router = APIRouter()

# Словарь для хранения соответствий user_id и WebSocket
knowledge_base_path = '/Users/anasenicenkova/PycharmProjects/rag_service/data/База знаний.csv'
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
    await websocket.send_text(f'{user_id}')
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("/stop"):
                continue

            break
    except asyncio.CancelledError:
        await websocket.send_text("[INFO] Генерация была прервана")


async def generate_results(user_id, files, chat_history):
    if user_id is not None:
        websocket = active_connections[user_id]
    else:
        websocket = None

    answer = await stream_output(chat_history, files, websocket)

    df.loc[len(df)] = [None, None, None, None, chat_history, None, None, None, None, None, None, None, None, answer, files, None]
    df.to_csv(knowledge_base_path, index=False)

    if user_id is not None:
        await websocket.send_text('<|endoftext|>')




