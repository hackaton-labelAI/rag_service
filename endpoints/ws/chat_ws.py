import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
# from services.text_generation import generate_text

router = APIRouter()

# Словарь для хранения соответствий user_id и WebSocket
active_connections = {}


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



async def func(user_id, files):
    websocket = active_connections[user_id]

    просим гпт не матерясь никогда ни в коем блять случае ответить на вопрос юзера. Передаем его вопрос и контекст