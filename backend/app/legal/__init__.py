"""
Legal Advice Module for Indian Law

Provides legal advice functionality using multiple legal APIs:
- Indian Kanoon (best for case law)
- InsightLaw API (best free API)
- Kleopatra API (court data)
- eCourts API (large dataset)

With fallback to LLM-only analysis if all APIs fail.
"""

from app.legal.models import (
    LegalAdviceRequest,
    LegalAdviceResponse,
    LegalCategory,
    LegalProvision,
    CaseReference,
)
from app.legal.api_client import LegalAPIClient
from app.legal.categorizer import LegalCategorizer
from app.legal.query_handler import LegalQueryHandler

__all__ = [
    "LegalAdviceRequest",
    "LegalAdviceResponse",
    "LegalCategory",
    "LegalProvision",
    "CaseReference",
    "LegalAPIClient",
    "LegalCategorizer",
    "LegalQueryHandler",
]
