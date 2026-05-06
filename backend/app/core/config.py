from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-coder:latest"
    ollama_vision_model: str = "llama3.2-vision"

    # Model Provider: "local" for Ollama, "api" for HuggingFace
    model_provider: str = Field(default="local", alias="MODEL_CALL")  # "local" or "api"

    # HuggingFace Configuration
    hf_access_token: str = Field(default="", alias="HUGGINGFACE_ACCESS_TOKEN")
    hf_model_name: str = Field(default="meta-llama/Llama-3.2-1B-Instruct", alias="MODEL_NAME")

    # Folders
    input_folder: str = "./documents"
    output_folder: str = "./output"

    # OCR Method
    ocr_method: str = "vision"  # "tesseract" or "vision" or "cloud"

    # Cloud OCR (for production)
    aws_region: str = "us-east-1"
    use_cloud_ocr: bool = False

    # Security/JWT Auth
    secret_key: str = "YOUR_SUPER_SECRET_KEY_CHANGEME_IN_PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7 # 1 week

    # Legal API Configuration
    # Primary: Indian Kanoon (best for case law)
    indian_kanoon_enabled: bool = True
    indian_kanoon_base_url: str = "https://api.indiankanoon.org"

    # Secondary: InsightLaw API (best free API)
    insightlaw_enabled: bool = True
    insightlaw_api_key: str = ""
    insightlaw_base_url: str = "https://api.insightlaw.in"

    # Tertiary: Kleopatra API (court data)
    kleopatra_enabled: bool = True
    kleopatra_api_key: str = ""
    kleopatra_base_url: str = "https://api.kleopatra.io"

    # Backup: eCourts API (large dataset)
    ecourts_enabled: bool = True
    ecourts_api_key: str = ""
    ecourts_base_url: str = "https://api.ecourts.gov.in"

    # Fallback to LLM-only if all APIs fail
    fallback_to_llm_only: bool = True

settings = Settings()
