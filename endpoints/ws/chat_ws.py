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
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("/stop"):
                continue

            await websocket.send_text(f'Ваш идентификатор: {user_id}')
            break
    except asyncio.CancelledError:
        await websocket.send_text("[INFO] Генерация была прервана")
