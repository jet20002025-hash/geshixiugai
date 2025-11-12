from fastapi import APIRouter

from .api.templates import router as template_router
from .api.documents import router as document_router
from .api.payments import router as payment_router

__all__ = [
    "APIRouter",
    "template_router",
    "document_router",
    "payment_router",
]

