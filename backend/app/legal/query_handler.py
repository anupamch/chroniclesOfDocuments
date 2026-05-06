"""
Legal Query Handler - Coordinates legal advice generation

Coordinates between:
1. LegalCategorizer - to identify the category
2. LegalAPIClient - to fetch relevant provisions and cases
3. LLM - to generate structured legal advice (supports Ollama and HuggingFace)

With fallback to LLM-only analysis if all APIs fail.
"""

import time
import logging
from typing import Dict, List, Optional
from app.core.config import settings
from app.core.llm_client import UnifiedLLM
from app.legal.models import (
    LegalAdviceRequest,
    LegalAdviceResponse,
    LegalProvision,
    CaseReference,
)
from app.legal.api_client import legal_api_client
from app.legal.categorizer import legal_categorizer

logger = logging.getLogger(__name__)


class LegalQueryHandler:
    """
    Handles legal advice queries by coordinating between
    categorizer, API client, and LLM.
    """

    def __init__(self):
        self._llm = None
        self.categorizer = legal_categorizer
        self.api_client = legal_api_client
        self.fallback_to_llm = settings.fallback_to_llm_only

    @property
    def llm(self):
        """Lazy initialization of LLM to get current model from settings"""
        if self._llm is None:
            self._llm = UnifiedLLM(temperature=0.3)
        return self._llm

    async def process_legal_query(
        self,
        request: LegalAdviceRequest
    ) -> LegalAdviceResponse:
        """
        Process a legal query and generate advice.

        Steps:
        1. Categorize the query (or use provided case context)
        2. Search for relevant provisions via APIs
        3. Search for relevant case laws via APIs
        4. Generate structured advice using LLM
        5. Add disclaimers
        """
        start_time = time.time()

        try:
            # Use query or case context for categorization
            query_for_category = request.case_context if request.case_context else request.query

            # Step 1: Categorize the query
            logger.info(f"Categorizing query: {query_for_category[:100]}...")
            category_result = await self.categorizer.categorize(query_for_category)
            category_id = category_result["category_id"]
            category_name = category_result["category_name"]
            keywords = category_result.get("keywords", [])

            logger.info(f"Category: {category_id} ({category_name})")

            # Step 2: Search for relevant provisions
            logger.info("Searching for legal provisions...")
            provisions = []
            case_refs = []
            sources_used = []

            try:
                provisions, prov_sources = await self.api_client.search_provisions(
                    query=request.query,
                    category=category_id,
                    limit=5
                )
                if prov_sources:
                    sources_used.extend(prov_sources)
                logger.info(f"Found {len(provisions)} provisions")
            except Exception as e:
                logger.warning(f"Provisions search failed: {e}")

            # Step 3: Search for relevant cases
            try:
                cases, case_sources = await self.api_client.search_cases(
                    query=request.query,
                    category=category_id,
                    limit=5
                )
                if case_sources:
                    sources_used.extend(case_sources)
                logger.info(f"Found {len(cases)} cases")
            except Exception as e:
                logger.warning(f"Case search failed: {e}")

            # Step 4: If no API results, try fallback
            if not provisions and not case_refs and self.fallback_to_llm:
                logger.info("No API results, using LLM-only fallback")
                sources_used.append("llm_fallback")
                provisions = await self._get_provisions_from_llm(request.query, category_id)
                case_refs = await self._get_cases_from_llm(request.query, category_id)

            # Step 5: Generate advice
            logger.info("Generating legal advice...")
            query_summary, advice = await self._generate_advice(
                query=request.query,
                category_id=category_id,
                category_name=category_name,
                provisions=provisions,
                cases=case_refs,
                language=request.language or "en",
                case_context=request.case_context,
                case_number=request.case_number,
                case_title=request.case_title
            )

            # Step 6: Add disclaimers
            disclaimers = self._generate_disclaimers(sources_used)

            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)

            return LegalAdviceResponse(
                query_summary=query_summary,
                category=category_id,
                relevant_provisions=provisions,
                case_references=case_refs,
                advice=advice,
                disclaimers=disclaimers,
                sources_used=list(set(sources_used)),
                processing_time_ms=processing_time
            )

        except Exception as e:
            logger.error(f"Error processing legal query: {e}")
            # Return error response
            processing_time = int((time.time() - start_time) * 1000)
            return LegalAdviceResponse(
                query_summary="Error processing query",
                category="other",
                relevant_provisions=[],
                case_references=[],
                advice="An error occurred while processing your query. Please try again or consult a qualified advocate.",
                disclaimers=[
                    "This is general information only",
                    "Not a substitute for professional legal advice",
                    "Consult a qualified advocate for your specific case"
                ],
                sources_used=[],
                processing_time_ms=processing_time
            )

    async def _get_provisions_from_llm(
        self,
        query: str,
        category_id: str
    ) -> List[LegalProvision]:
        """Get relevant provisions using LLM knowledge"""
        prompt = f"""Based on the user's legal query, list the relevant provisions of Indian law.

Query: {query}
Category: {category_id}

Respond with relevant Indian legal provisions in this format:
Act Name - Section Number: Brief description

For example:
Indian Penal Code, 1860 - Section 302: Punishment for murder
Transfer of Property Act, 1882 - Section 108: Rights and liabilities of lessor and lessee

List 3-5 most relevant provisions:"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()

            provisions = []
            for line in content.split("\n"):
                line = line.strip()
                if " - " in line or ":" in line:
                    parts = line.split(" - ") if " - " in line else line.split(":")
                    if len(parts) >= 2:
                        act_section = parts[0].strip()
                        description = parts[1].strip() if len(parts) > 1 else ""

                        # Try to split act and section
                        if " - " in line:
                            act_name, section = act_section.rsplit(" - ", 1)
                        else:
                            act_name = act_section
                            section = "N/A"

                        provisions.append(LegalProvision(
                            act=act_name.strip(),
                            section=section.strip(),
                            description=description,
                            source="llm_fallback"
                        ))

            return provisions[:5]
        except Exception as e:
            logger.warning(f"LLM provisions failed: {e}")
            return []

    async def _get_cases_from_llm(
        self,
        query: str,
        category_id: str
    ) -> List[CaseReference]:
        """Get relevant case laws using LLM knowledge"""
        prompt = f"""Based on the user's legal query, list relevant Indian case laws.

Query: {query}
Category: {category_id}

Respond with relevant case laws in this format:
Case Name - Year - Court: Brief summary

For example:
Vijay Kumar Gupta vs. R.K. Sahu (2019) Delhi High Court: Security deposit refund
Mohan Kumar vs. State (2020) Supreme Court: Bail principles

List 2-4 most relevant cases:"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()

            cases = []
            for line in content.split("\n"):
                line = line.strip()
                if len(line) > 10:
                    # Try to parse case info
                    cases.append(CaseReference(
                        case_name=line[:100],  # Truncate if too long
                        summary=line,
                        source="llm_fallback"
                    ))

            return cases[:4]
        except Exception as e:
            logger.warning(f"LLM cases failed: {e}")
            return []

    async def _generate_advice(
        self,
        query: str,
        category_id: str,
        category_name: str,
        provisions: List[LegalProvision],
        cases: List[CaseReference],
        language: str = "en",
        case_context: Optional[str] = None,
        case_number: Optional[str] = None,
        case_title: Optional[str] = None
    ) -> tuple[str, str]:
        """Generate structured legal advice using LLM"""

        # Prepare case context
        case_context_str = ""
        if case_context:
            case_context_str = f"""
CASE TIMELINE/CONTEXT:
{case_context}

"""

        # Prepare provisions context
        provisions_context = ""
        if provisions:
            provisions_context = "\nRelevant Legal Provisions:\n"
            for p in provisions[:5]:
                provisions_context += f"- {p.act}, {p.section}: {p.description[:200]}\n"

        # Prepare cases context
        cases_context = ""
        if cases:
            cases_context = "\nRelevant Case Laws:\n"
            for c in cases[:3]:
                case_info = f"- {c.case_name}"
                if c.year:
                    case_info += f" ({c.year})"
                if c.court:
                    case_info += f" {c.court}"
                cases_context += case_info + "\n"

        case_ref = ""
        if case_number or case_title:
            case_ref = f"\n\nCASE REFERENCE: {case_number or ''} - {case_title or ''}"

        prompt = f"""You are a legal advisor providing general legal information under Indian law.

{case_context_str}User's Legal Query:
{query}

Category: {category_name} ({category_id}){case_ref}
{provisions_context}
{cases_context}

Based on the above information:

1. First, provide a brief summary of the user's legal issue based on the case context (1-2 sentences)

2. Then provide general legal guidance:
   - What laws apply to this situation
   - What legal options the user has
   - What steps they might consider
   - What documents or evidence they should gather

3. Important:
   - Do not provide specific legal advice
   - Recommend consulting a qualified advocate
   - Mention that laws may have changed

Keep the advice clear, practical, and easy to understand.
Write in {language} language.

Format your response:
---
SUMMARY: <brief summary>

LEGAL GUIDANCE:
<your guidance>

NEXT STEPS:
- Step 1
- Step 2
- Step 3
---"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()

            # Parse summary and advice
            summary = query[:150] + "..."  # Default summary
            advice = content

            # Try to extract summary if explicitly marked
            if "SUMMARY:" in content:
                parts = content.split("SUMMARY:", 1)
                if len(parts) > 1:
                    summary_part = parts[1].split("LEGAL GUIDANCE:")[0].strip()
                    summary = summary_part[:200]

            return summary, advice

        except Exception as e:
            logger.warning(f"LLM advice generation failed: {e}")
            return (
                query[:150] + "...",
                "Based on the general principles of Indian law, we recommend consulting a qualified advocate who can provide specific advice based on the details of your case. Legal matters often require professional representation."
            )

    def _generate_disclaimers(self, sources_used: List[str]) -> List[str]:
        """Generate appropriate disclaimers based on sources used"""
        disclaimers = [
            "This is general legal information only, not specific legal advice.",
            "This does not create an attorney-client relationship.",
            "Consult a qualified advocate for advice specific to your situation.",
            "Laws and interpretations may have changed; verify current provisions."
        ]

        if "llm_fallback" in sources_used:
            disclaimers.append(
                "Note: This response is based on AI knowledge and may not reflect current law."
            )

        return disclaimers


# Singleton instance
legal_query_handler = LegalQueryHandler()
