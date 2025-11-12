from pathlib import Path

from .document_service import DocumentService


class PaymentService:
    def __init__(self, document_dir: Path) -> None:
        self.document_dir = document_dir

    def mark_as_paid(self, document_id: str):
        document_service = DocumentService(document_dir=self.document_dir, template_dir=Path("storage/templates"))
        metadata = document_service.get_document_metadata(document_id)
        if not metadata:
            raise FileNotFoundError("document not found")
        if metadata.get("paid"):
            return metadata
        return document_service.update_metadata(document_id, paid=True)

