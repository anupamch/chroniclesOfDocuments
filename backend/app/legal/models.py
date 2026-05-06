"""
Pydantic models for Legal Advice functionality
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class LegalAdviceRequest(BaseModel):
    """Request model for legal advice"""
    query: str = Field(..., description="User's legal question or issue description")
    language: Optional[str] = Field("en", description="Response language (en/hi)")
    # Optional context from case timeline
    case_context: Optional[str] = Field(None, description="Timeline story or case context for contextual advice")
    case_number: Optional[str] = Field(None, description="Case number for reference")
    case_title: Optional[str] = Field(None, description="Case title for reference")


class LegalProvision(BaseModel):
    """Model for a legal provision/section"""
    act: str = Field(..., description="Name of the act (e.g., 'Indian Penal Code, 1860')")
    section: str = Field(..., description="Section number (e.g., 'Section 302')")
    title: Optional[str] = Field(None, description="Title of the section")
    description: str = Field(..., description="Description or text of the provision")
    source: str = Field(..., description="Source API (indian_kanoon, insightlaw, kleopatra, ecourts)")
    url: Optional[str] = Field(None, description="Link to the full provision")


class CaseReference(BaseModel):
    """Model for a case law reference"""
    case_name: str = Field(..., description="Name of the case")
    year: Optional[int] = Field(None, description="Year of the judgment")
    court: Optional[str] = Field(None, description="Court that delivered the judgment")
    citation: Optional[str] = Field(None, description="Legal citation")
    summary: Optional[str] = Field(None, description="Brief summary of the case")
    source: str = Field(..., description="Source API")
    url: Optional[str] = Field(None, description="Link to the full case")


class LegalCategory(BaseModel):
    """Model for a legal category"""
    id: str = Field(..., description="Category ID (e.g., 'property_dispute')")
    name: str = Field(..., description="Category name (e.g., 'Property Dispute')")
    description: str = Field(..., description="Description of the category")
    applicable_acts: List[str] = Field(default_factory=list, description="List of applicable acts")


class LegalAdviceResponse(BaseModel):
    """Response model for legal advice"""
    query_summary: str = Field(..., description="Summary of the user's legal query")
    category: str = Field(..., description="Identified legal category")
    relevant_provisions: List[LegalProvision] = Field(default_factory=list, description="Relevant legal provisions")
    case_references: List[CaseReference] = Field(default_factory=list, description="Relevant case laws")
    advice: str = Field(..., description="Generated legal advice")
    disclaimers: List[str] = Field(default_factory=list, description="Legal disclaimers")
    sources_used: List[str] = Field(default_factory=list, description="APIs that provided data")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")


class SearchRequest(BaseModel):
    """Request model for legal search"""
    query: str = Field(..., description="Search keywords")
    category: Optional[str] = Field(None, description="Filter by category")
    limit: int = Field(10, ge=1, le=50, description="Maximum results to return")


class SearchResultProvision(BaseModel):
    """Search result for a legal provision"""
    act: str
    section: str
    title: Optional[str] = None
    description: str
    score: float = Field(..., description="Relevance score")
    source: str


class SearchResultCase(BaseModel):
    """Search result for a case"""
    case_name: str
    year: Optional[int] = None
    court: Optional[str] = None
    summary: Optional[str] = None
    score: float = Field(..., description="Relevance score")
    source: str


class SearchResponse(BaseModel):
    """Response model for legal search"""
    provisions: List[SearchResultProvision] = Field(default_factory=list)
    cases: List[SearchResultCase] = Field(default_factory=list)
    total_results: int
    sources_used: List[str]


# Pre-defined legal categories for Indian law
LEGAL_CATEGORIES = [
    LegalCategory(
        id="criminal",
        name="Criminal Law",
        description="Offenses, punishments, criminal procedure",
        applicable_acts=["Indian Penal Code, 1860", "Code of Criminal Procedure, 1973", "Indian Evidence Act, 1872"]
    ),
    LegalCategory(
        id="civil_dispute",
        name="Civil Dispute",
        description="General civil matters, suits, damages",
        applicable_acts=["Code of Civil Procedure, 1908", "Indian Contract Act, 1872", "Limitation Act, 1963"]
    ),
    LegalCategory(
        id="property_dispute",
        name="Property Dispute",
        description="Land, real estate, rental matters",
        applicable_acts=["Transfer of Property Act, 1882", "Registration Act, 1908", "Indian Easements Act, 1882"]
    ),
    LegalCategory(
        id="family_dispute",
        name="Family Dispute",
        description="Marriage, divorce, custody, inheritance",
        applicable_acts=["Hindu Marriage Act, 1955", "Hindu Succession Act, 1956", "Muslim Women Protection Act, 2019", "Divorce Act, 1869"]
    ),
    LegalCategory(
        id="labor_employment",
        name="Labor & Employment",
        description="Workplace disputes, employee rights",
        applicable_acts=["Industrial Disputes Act, 1947", "EPF Act, 1952", "Payment of Gratuity Act, 1972"]
    ),
    LegalCategory(
        id="corporate_commercial",
        name="Corporate & Commercial",
        description="Business law, companies, contracts",
        applicable_acts=["Companies Act, 2013", "LLP Act, 2008", "IBC, 2016", "Competition Act, 2002"]
    ),
    LegalCategory(
        id="tax",
        name="Tax Law",
        description="Income tax, GST, customs",
        applicable_acts=["Income Tax Act, 1961", "CGST Act, 2017", "Customs Act, 1962"]
    ),
    LegalCategory(
        id="consumer_protection",
        name="Consumer Protection",
        description="Consumer rights, complaints",
        applicable_acts=["Consumer Protection Act, 2019"]
    ),
    LegalCategory(
        id="constitutional",
        name="Constitutional Law",
        description="Fundamental rights, articles",
        applicable_acts=["Constitution of India"]
    ),
    LegalCategory(
        id="data_privacy",
        name="Data Privacy & IT",
        description="Data protection, cyber laws",
        applicable_acts=["Digital Personal Data Protection Act, 2023", "IT Act, 2000"]
    ),
    LegalCategory(
        id="rti",
        name="Right to Information",
        description="RTI requests and appeals",
        applicable_acts=["Right to Information Act, 2005"]
    ),
    LegalCategory(
        id="motor_accident",
        name="Motor Accident",
        description="Accident claims, compensation",
        applicable_acts=["Motor Vehicles Act, 1988"]
    ),
    LegalCategory(
        id="other",
        name="Other/General",
        description="Miscellaneous legal matters",
        applicable_acts=[]
    ),
]
