# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from endpoints.apis.document_api_base import BaseDocumentApi
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
from endpoints.models.document_response import DocumentResponse


router = APIRouter()

ns_pkg = endpoints
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/api/document",
    responses={
        200: {"model": DocumentResponse, "description": "Successful document retrieval"},
    },
    tags=["document"],
    response_model_by_alias=True,
)
async def get_document(
) -> DocumentResponse:
    """Get the full document with text and images"""
    if not BaseDocumentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDocumentApi.subclasses[0]().get_document()
