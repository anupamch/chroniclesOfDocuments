"""
Legal API Client with Multi-Provider Fallback Strategy

Supports:
- Indian Kanoon (best for case law)
- InsightLaw API (best free API)
- Kleopatra API (court data)
- eCourts API (large dataset)

With automatic fallback when one API fails.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
import httpx
from app.core.config import settings
from app.legal.models import LegalProvision, CaseReference, SearchResultProvision, SearchResultCase

logger = logging.getLogger(__name__)


class LegalAPIClient:
    """
    Multi-provider legal API client with fallback strategy.
    Tries APIs in order of reliability: Indian Kanoon → InsightLaw → Kleopatra → eCourts
    """

    def __init__(self):
        self.providers = []
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize enabled providers in order of preference"""
        if settings.indian_kanoon_enabled:
            self.providers.append("indian_kanoon")
        if settings.insightlaw_enabled and settings.insightlaw_api_key:
            self.providers.append("insightlaw")
        if settings.kleopatra_enabled and settings.kleopatra_api_key:
            self.providers.append("kleopatra")
        if settings.ecourts_enabled and settings.ecourts_api_key:
            self.providers.append("ecourts")

        logger.info(f"Legal API providers initialized: {self.providers}")

    async def search_provisions(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> tuple[List[LegalProvision], List[str]]:
        """
        Search for legal provisions across all enabled APIs.
        Returns provisions and list of sources used.
        """
        all_provisions = []
        sources_used = []

        for provider in self.providers:
            try:
                if provider == "indian_kanoon":
                    provisions = await self._search_indian_kanoon(query, limit)
                elif provider == "insightlaw":
                    provisions = await self._search_insightlaw(query, category, limit)
                elif provider == "kleopatra":
                    provisions = await self._search_kleopatra(query, category, limit)
                elif provider == "ecourts":
                    provisions = await self._search_ecourts(query, category, limit)

                if provisions:
                    all_provisions.extend(provisions)
                    sources_used.append(provider)
                    logger.info(f"Found {len(provisions)} provisions from {provider}")
                    # If we got results, we can continue to get more from other providers
                    # or stop early if we have enough
                    if len(all_provisions) >= limit * 2:
                        break

            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                continue

        # Remove duplicates based on act + section
        seen = set()
        unique_provisions = []
        for p in all_provisions:
            key = f"{p.act}_{p.section}"
            if key not in seen:
                seen.add(key)
                unique_provisions.append(p)

        return unique_provisions[:limit], sources_used

    async def search_cases(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> tuple[List[CaseReference], List[str]]:
        """
        Search for case laws across all enabled APIs.
        Returns cases and list of sources used.
        """
        all_cases = []
        sources_used = []

        for provider in self.providers:
            try:
                if provider == "indian_kanoon":
                    cases = await self._search_indian_kanoon_cases(query, limit)
                elif provider == "insightlaw":
                    cases = await self._search_insightlaw_cases(query, category, limit)
                elif provider == "kleopatra":
                    cases = await self._search_kleopatra_cases(query, category, limit)
                elif provider == "ecourts":
                    cases = await self._search_ecourts_cases(query, category, limit)

                if cases:
                    all_cases.extend(cases)
                    sources_used.append(provider)
                    logger.info(f"Found {len(cases)} cases from {provider}")
                    if len(all_cases) >= limit * 2:
                        break

            except Exception as e:
                logger.warning(f"Provider {provider} failed for case search: {e}")
                continue

        # Remove duplicates based on case name
        seen = set()
        unique_cases = []
        for c in all_cases:
            key = c.case_name.lower().strip()
            if key not in seen:
                seen.add(key)
                unique_cases.append(c)

        return unique_cases[:limit], sources_used

    # ===== Indian Kanoon API =====

    async def _search_indian_kanoon(
        self,
        query: str,
        limit: int = 10
    ) -> List[LegalProvision]:
        """Search Indian Kanoon for legal provisions"""
        # Indian Kanoon doesn't have a public API, so we simulate with search
        # In production, you'd need to implement proper API or web scraping
        # This is a placeholder that returns mock data for demonstration
        logger.info(f"Searching Indian Kanoon for: {query}")

        # Note: Indian Kanoon doesn't provide a public API
        # In production, you would need to:
        # 1. Use their official API (if available with subscription)
        # 2. Use web scraping (legal but against ToS)
        # 3. Use a third-party aggregator

        # For now, return empty - will fallback to other APIs
        return []

    async def _search_indian_kanoon_cases(
        self,
        query: str,
        limit: int = 10
    ) -> List[CaseReference]:
        """Search Indian Kanoon for case laws"""
        logger.info(f"Searching Indian Kanoon cases for: {query}")
        # Placeholder - same as above
        return []

    # ===== InsightLaw API =====

    async def _search_insightlaw(
        self,
        query: str,
        category: Optional[str],
        limit: int = 10
    ) -> List[LegalProvision]:
        """Search InsightLaw API for legal provisions"""
        if not settings.insightlaw_api_key:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{settings.insightlaw_base_url}/api/v1/provisions/search",
                    headers={
                        "Authorization": f"Bearer {settings.insightlaw_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "query": query,
                        "category": category,
                        "limit": limit
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    provisions = []
                    for item in data.get("results", []):
                        provisions.append(LegalProvision(
                            act=item.get("act_name", ""),
                            section=item.get("section", ""),
                            title=item.get("title"),
                            description=item.get("text", ""),
                            source="insightlaw",
                            url=item.get("url")
                        ))
                    return provisions
            except Exception as e:
                logger.warning(f"InsightLaw API error: {e}")

        return []

    async def _search_insightlaw_cases(
        self,
        query: str,
        category: Optional[str],
        limit: int = 10
    ) -> List[CaseReference]:
        """Search InsightLaw API for case laws"""
        if not settings.insightlaw_api_key:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{settings.insightlaw_base_url}/api/v1/cases/search",
                    headers={
                        "Authorization": f"Bearer {settings.insightlaw_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "query": query,
                        "category": category,
                        "limit": limit
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    cases = []
                    for item in data.get("results", []):
                        cases.append(CaseReference(
                            case_name=item.get("case_name", ""),
                            year=item.get("year"),
                            court=item.get("court"),
                            citation=item.get("citation"),
                            summary=item.get("summary"),
                            source="insightlaw",
                            url=item.get("url")
                        ))
                    return cases
            except Exception as e:
                logger.warning(f"InsightLaw cases API error: {e}")

        return []

    # ===== Kleopatra API =====

    async def _search_kleopatra(
        self,
        query: str,
        category: Optional[str],
        limit: int = 10
    ) -> List[LegalProvision]:
        """Search Kleopatra API for legal provisions"""
        if not settings.kleopatra_api_key:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{settings.kleopatra_base_url}/api/v1/legal provisions",
                    headers={
                        "X-API-Key": settings.kleopatra_api_key
                    },
                    params={
                        "q": query,
                        "type": category,
                        "limit": limit
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    provisions = []
                    for item in data.get("data", []):
                        provisions.append(LegalProvision(
                            act=item.get("act", ""),
                            section=item.get("section", ""),
                            title=item.get("title"),
                            description=item.get("content", ""),
                            source="kleopatra",
                            url=item.get("link")
                        ))
                    return provisions
            except Exception as e:
                logger.warning(f"Kleopatra API error: {e}")

        return []

    async def _search_kleopatra_cases(
        self,
        query: str,
        category: Optional[str],
        limit: int = 10
    ) -> List[CaseReference]:
        """Search Kleopatra API for case laws"""
        if not settings.kleopatra_api_key:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{settings.kleopatra_base_url}/api/v1/cases",
                    headers={
                        "X-API-Key": settings.kleopatra_api_key
                    },
                    params={
                        "q": query,
                        "type": category,
                        "limit": limit
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    cases = []
                    for item in data.get("data", []):
                        cases.append(CaseReference(
                            case_name=item.get("title", ""),
                            year=item.get("year"),
                            court=item.get("court"),
                            citation=item.get("citation"),
                            summary=item.get("snippet"),
                            source="kleopatra",
                            url=item.get("link")
                        ))
                    return cases
            except Exception as e:
                logger.warning(f"Kleopatra cases API error: {e}")

        return []

    # ===== eCourts API =====

    async def _search_ecourts(
        self,
        query: str,
        category: Optional[str],
        limit: int = 10
    ) -> List[LegalProvision]:
        """Search eCourts API for legal provisions"""
        # eCourts primarily has case data, not provisions
        # This is a placeholder
        return []

    async def _search_ecourts_cases(
        self,
        query: str,
        category: Optional[str],
        limit: int = 10
    ) -> List[CaseReference]:
        """Search eCourts API for case laws"""
        if not settings.ecourts_api_key:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{settings.ecourts_base_url}/api/judgments",
                    headers={
                        "Authorization": f"Bearer {settings.ecourts_api_key}"
                    },
                    params={
                        "search": query,
                        "limit": limit
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    cases = []
                    for item in data.get("judges", []):
                        cases.append(CaseReference(
                            case_name=item.get("case_title", ""),
                            year=item.get("judgment_year"),
                            court=item.get("court_name"),
                            citation=item.get("citation"),
                            summary=item.get("abstract"),
                            source="ecourts",
                            url=item.get("judgment_link")
                        ))
                    return cases
            except Exception as e:
                logger.warning(f"eCourts API error: {e}")

        return []


# Singleton instance
legal_api_client = LegalAPIClient()
