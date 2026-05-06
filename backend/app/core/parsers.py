import os
from pathlib import Path
import pypdf
import pdfplumber
import docx
import pytesseract
from PIL import Image


class DocumentParser:
    """Extract text and tables from various document formats"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> tuple[str, list[dict]]:
        """Extract text and tables from PDF (handles scanned PDFs)"""
        text = ""
        tables = []
        
        # Extract text with pypdf
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                text += page_text + "\n"
        
        # If no text extracted, it might be a scanned PDF - try OCR
        if len(text.strip()) < 50:  # Very little text means likely scanned
            print("  [Parser] Detected scanned PDF, applying OCR...")
            import pdf2image
            
            try:
                # Convert PDF pages to images
                images = pdf2image.convert_from_path(file_path)
                text = ""
                
                for i, image in enumerate(images):
                    print(f"  [Parser] OCR on page {i+1}/{len(images)}")
                    custom_config = r'--oem 3 --psm 6'
                    page_text = pytesseract.image_to_string(image, config=custom_config)
                    text += page_text + "\n"
            except Exception as e:
                print(f"  [Parser] OCR failed: {e}")
        
        # Extract tables with pdfplumber
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend([{"data": table} for table in page_tables])
        except:
            pass  # Tables extraction might fail on scanned PDFs
        
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
        """Extract text from image using OCR with preprocessing"""
        image = Image.open(file_path)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # OCR with better configuration for scanned documents
        custom_config = r'--oem 3 --psm 6'  # LSTM OCR, assume uniform text block
        text = pytesseract.image_to_string(image, config=custom_config)
        
        return text.strip(), []
    
    @staticmethod
    def parse_document(file_path: str) -> tuple[str, list[dict]]:
        """Parse document based on file extension"""
        ext = Path(file_path).suffix.lower()
        
        if ext == ".pdf":
            return DocumentParser.parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return DocumentParser.parse_docx(file_path)
        elif ext in [".png", ".jpg", ".jpeg"]:
            return DocumentParser.parse_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
