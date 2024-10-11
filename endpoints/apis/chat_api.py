# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from endpoints.apis.chat_api_base import BaseChatApi
import endpoints

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from endpoints.models.extra_models import TokenModel  # noqa: F401
from endpoints.models.chat_context import ChatContext
from endpoints.models.rag_response_data import RAGResponseData


router = APIRouter()

ns_pkg = endpoints
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/api/chat",
    responses={
        200: {"model": RAGResponseData, "description": "Successful response"},
    },
    tags=["chat"],
    response_model_by_alias=True,
)
async def chat(
    chat_context: ChatContext = Body(None, description=""),
) -> RAGResponseData:
    if not BaseChatApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseChatApi.subclasses[0]().chat(chat_context)
