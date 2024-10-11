from endpoints.apis.document_api_base import BaseDocumentApi
from endpoints.models.document_response import DocumentResponse


class DocumentApiImpl(BaseDocumentApi):

    async def get_document(self) -> DocumentResponse:
        return await super().get_document()