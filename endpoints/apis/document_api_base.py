# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from endpoints.models.document_response import DocumentResponse


class BaseDocumentApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDocumentApi.subclasses = BaseDocumentApi.subclasses + (cls,)
    async def get_document(
        self,
    ) -> DocumentResponse:
        """Get the full document with text and images"""
        ...
