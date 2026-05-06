"""
Legal Categorizer - Classifies user queries into legal categories

Uses LLM to analyze the user's legal issue and identify:
- The relevant legal category (criminal, civil, property, family, etc.)
- Keywords for searching
- Applicable areas of law
"""

from typing import Dict, List, Optional
from app.core.llm_client import UnifiedLLM
from app.core.config import settings
from app.legal.models import LEGAL_CATEGORIES


class LegalCategorizer:
    """
    Categorizes legal queries into relevant Indian law categories.
    Uses LLM for intelligent classification.
    """

    CATEGORY_LIST = "\n".join([
        f"- {cat.id}: {cat.name} - {cat.description}"
        for cat in LEGAL_CATEGORIES
    ])

    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        """Lazy initialization of LLM to get current model from settings"""
        if self._llm is None:
            self._llm = UnifiedLLM(temperature=0.1)
        return self._llm

    async def categorize(self, query: str) -> Dict:
        """
        Categorize a legal query into relevant categories.

        Args:
            query: User's legal question or issue description

        Returns:
            Dict with:
                - category_id: Primary category ID
                - category_name: Category name
                - keywords: Keywords for searching
                - sub_categories: Related categories
                - confidence: Classification confidence
        """
        prompt = f"""Analyze this legal query and classify it into the most appropriate Indian legal category.

Legal Categories:
{self.CATEGORY_LIST}

Query: {query}

Respond in this exact format:
category_id: <category_id>
category_name: <category_name>
keywords: <comma-separated keywords for legal search>
sub_categories: <comma-separated related category IDs>
confidence: <0.0-1.0 confidence score>"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()

            # Parse the response
            result = self._parse_response(content)
            return result

        except Exception as e:
            # Fallback to default category on error
            return {
                "category_id": "other",
                "category_name": "Other/General",
                "keywords": self._extract_keywords(query),
                "sub_categories": [],
                "confidence": 0.5,
                "error": str(e)
            }

    def _parse_response(self, content: str) -> Dict:
        """Parse the LLM response into structured data"""
        result = {
            "category_id": "other",
            "category_name": "Other/General",
            "keywords": [],
            "sub_categories": [],
            "confidence": 0.5
        }

        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("category_id:"):
                result["category_id"] = line.split(":", 1)[1].strip()
            elif line.startswith("category_name:"):
                result["category_name"] = line.split(":", 1)[1].strip()
            elif line.startswith("keywords:"):
                keywords_str = line.split(":", 1)[1].strip()
                result["keywords"] = [k.strip() for k in keywords_str.split(",") if k.strip()]
            elif line.startswith("sub_categories:"):
                subs_str = line.split(":", 1)[1].strip()
                result["sub_categories"] = [s.strip() for s in subs_str.split(",") if s.strip()]
            elif line.startswith("confidence:"):
                try:
                    result["confidence"] = float(line.split(":", 1)[1].strip())
                except:
                    result["confidence"] = 0.5

        # Validate category exists
        valid_ids = {cat.id for cat in LEGAL_CATEGORIES}
        if result["category_id"] not in valid_ids:
            result["category_id"] = "other"
            result["category_name"] = "Other/General"

        # If no keywords extracted, try to extract from original query
        if not result["keywords"]:
            result["keywords"] = ["legal", "advice"]

        return result

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract basic keywords from text"""
        # Simple keyword extraction - in production, use more sophisticated NLP
        common_legal_terms = [
            "landlord", "tenant", "rental", "deposit", "lease",
            "divorce", "custody", "marriage", "alimony", "maintenance",
            "contract", "breach", "damages", "payment",
            "property", "land", "title", "deed", "registration",
            "accident", "insurance", "compensation", "claim",
            "criminal", "fir", "police", "bail", "arrest",
            "tax", "income", "gst", "customs", "penalty",
            "consumer", "defect", "refund", "warranty",
            "company", "shareholder", "merger", "ipo",
            "employment", "termination", "salary", "bonus",
            "rti", "information", "government",
            "copyright", "trademark", "patent", "ip"
        ]

        text_lower = text.lower()
        keywords = [term for term in common_legal_terms if term in text_lower]
        return keywords if keywords else ["legal", "dispute"]

    def get_category_info(self, category_id: str) -> Optional[Dict]:
        """Get full category information by ID"""
        for cat in LEGAL_CATEGORIES:
            if cat.id == category_id:
                return {
                    "id": cat.id,
                    "name": cat.name,
                    "description": cat.description,
                    "applicable_acts": cat.applicable_acts
                }
        return None

    def get_all_categories(self) -> List[Dict]:
        """Get all available legal categories"""
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "applicable_acts": cat.applicable_acts
            }
            for cat in LEGAL_CATEGORIES
        ]


# Singleton instance
legal_categorizer = LegalCategorizer()
