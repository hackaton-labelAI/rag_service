
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
# from services.text_generation import generate_text

router = APIRouter()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    generation_task = None
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("/stop"):
                continue

            await websocket.send_text("fsdffdsf")
            break
    except WebSocketDisconnect:
        print("Клиент отключился")
    except asyncio.CancelledError:
        await websocket.send_text("[INFO] Генерация была прервана")
