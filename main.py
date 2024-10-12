from endpoints.apis.telegram_bot_api import router
from endpoints.router_init import app
from endpoints.ws.chat_ws import router as ChatWSRouter

app.include_router(ChatWSRouter)
app.include_router(router)