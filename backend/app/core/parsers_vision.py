import base64
from pathlib import Path
import pypdf
import pdfplumber
import docx
from langchain_ollama import ChatOllama
from app.core.config import settings


class VisionDocumentParser:
    """Extract text using Ollama vision models (no Tesseract needed)"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> tuple[str, list[dict]]:
        """Extract text and tables from PDF"""
        text = ""
        tables = []
        
        # Extract text with pypdf
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                text += page_text + "\n"
        
        # If no text extracted, it might be a scanned PDF
        if len(text.strip()) < 50:
            print("  [Parser] Detected scanned PDF, using vision model...")
            try:
                import pdf2image
                images = pdf2image.convert_from_path(file_path)
                text = ""
                
                for i, image in enumerate(images):
                    print(f"  [Parser] Processing page {i+1}/{len(images)} with vision model")
                    page_text = VisionDocumentParser._ocr_with_vision(image)
                    text += page_text + "\n"
            except Exception as e:
                print(f"  [Parser] Vision OCR failed: {e}")
        
        # Extract tables with pdfplumber
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend([{"data": table} for table in page_tables])
        except:
            pass
        
        return text.strip(), tables
    
    @staticmethod
    def parse_docx(file_path: str) -> tuple[str, list[dict]]:
        """Extract text and tables from DOCX"""
        doc = docx.Document(file_path)
        
        # Extract text
        text = "\n".join([para.text for para in doc.paragraphs])
        
        # Extract tables
        tables = []
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                table_data.append([cell.text for cell in row.cells])
            tables.append({"data": table_data})
        
        return text.strip(), tables
    
    @staticmethod
    def parse_image(file_path: str) -> tuple[str, list[dict]]:
        """Extract text from image using Ollama vision model"""
        from PIL import Image
        
        print("  [Parser] Using vision model for OCR...")
        image = Image.open(file_path)
        text = VisionDocumentParser._ocr_with_vision(image)
        
        return text.strip(), []
    
    @staticmethod
    def _ocr_with_vision(image) -> str:
        """Use Ollama vision model to extract text from image"""
        import io

        # Convert image to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Use vision model
        try:
            llm = ChatOllama(
                base_url=settings.ollama_base_url,
                model=settings.ollama_vision_model,
                temperature=0,
                num_gpu=1  # Use GPU acceleration
            )

            prompt = """Extract all text from this image exactly as it appears.
Include all text, numbers, dates, and formatting.
Do not add any commentary, just return the extracted text."""

            # Use HumanMessage format with image_url
            from langchain_core.messages import HumanMessage
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{img_base64}"}
                ]
            )

            response = llm.invoke([message])

            return response.content

        except Exception as e:
            print(f"  [Parser] Vision model error: {e}")
            raise e
    
    @staticmethod
    def parse_document(file_path: str) -> tuple[str, list[dict]]:
        """Parse document based on file extension"""
        ext = Path(file_path).suffix.lower()
        
        if ext == ".pdf":
            return VisionDocumentParser.parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return VisionDocumentParser.parse_docx(file_path)
        elif ext in [".png", ".jpg", ".jpeg"]:
            return VisionDocumentParser.parse_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
