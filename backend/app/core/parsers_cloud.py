"""
Cloud OCR parsers - No Tesseract needed, works perfectly in Docker
"""
import os
import base64
from pathlib import Path
import pypdf
import pdfplumber
import docx
from PIL import Image
import io


class CloudOCRParser:
    """Production-grade OCR using cloud services"""
    
    # ===== AWS TEXTRACT =====
    
    @staticmethod
    def ocr_with_aws_textract(image_bytes: bytes) -> str:
        """
        AWS Textract - Best accuracy, production-ready
        Cost: $1.50 per 1000 pages
        """
        try:
            import boto3
            
            textract = boto3.client('textract', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            
            response = textract.detect_document_text(
                Document={'Bytes': image_bytes}
            )
            
            text = ""
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    text += item['Text'] + "\n"
            
            return text.strip()
            
        except Exception as e:
            print(f"  [AWS Textract] Error: {e}")
            return ""
    
    # ===== GOOGLE CLOUD VISION =====
    
    @staticmethod
    def ocr_with_google_vision(image_bytes: bytes) -> str:
        """
        Google Cloud Vision API
        Cost: $1.50 per 1000 pages
        """
        try:
            from google.cloud import vision
            
            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=image_bytes)
            
            response = client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                return texts[0].description
            
            return ""
            
        except Exception as e:
            print(f"  [Google Vision] Error: {e}")
            return ""
    
    # ===== AZURE COMPUTER VISION =====
    
    @staticmethod
    def ocr_with_azure(image_bytes: bytes) -> str:
        """
        Azure Computer Vision
        Cost: $1.00 per 1000 pages
        """
        try:
            from azure.cognitiveservices.vision.computervision import ComputerVisionClient
            from msrest.authentication import CognitiveServicesCredentials
            
            subscription_key = os.getenv('AZURE_VISION_KEY')
            endpoint = os.getenv('AZURE_VISION_ENDPOINT')
            
            client = ComputerVisionClient(
                endpoint, 
                CognitiveServicesCredentials(subscription_key)
            )
            
            # Read text from image
            read_response = client.read_in_stream(
                io.BytesIO(image_bytes),
                raw=True
            )
            
            # Get operation location
            operation_location = read_response.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]
            
            # Wait for result
            import time
            while True:
                result = client.get_read_result(operation_id)
                if result.status.lower() not in ['notstarted', 'running']:
                    break
                time.sleep(1)
            
            # Extract text
            text = ""
            if result.status.lower() == 'succeeded':
                for page in result.analyze_result.read_results:
                    for line in page.lines:
                        text += line.text + "\n"
            
            return text.strip()
            
        except Exception as e:
            print(f"  [Azure Vision] Error: {e}")
            return ""
    
    # ===== EASYOCR (Open Source Alternative) =====
    
    @staticmethod
    def ocr_with_easyocr(image_bytes: bytes) -> str:
        """
        EasyOCR - Open source, works in Docker, GPU accelerated
        Free but requires GPU for good performance
        """
        try:
            import easyocr
            
            # Initialize reader (cached after first use)
            if not hasattr(CloudOCRParser, '_easyocr_reader'):
                CloudOCRParser._easyocr_reader = easyocr.Reader(['en'], gpu=True)
            
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Perform OCR
            results = CloudOCRParser._easyocr_reader.readtext(image)
            
            # Extract text
            text = "\n".join([result[1] for result in results])
            return text.strip()
            
        except Exception as e:
            print(f"  [EasyOCR] Error: {e}")
            return ""
    
    # ===== PADDLEOCR (Open Source Alternative) =====
    
    @staticmethod
    def ocr_with_paddleocr(image_bytes: bytes) -> str:
        """
        PaddleOCR - Open source, fast, works in Docker
        Free and doesn't require GPU
        """
        try:
            from paddleocr import PaddleOCR
            
            # Initialize OCR (cached after first use)
            if not hasattr(CloudOCRParser, '_paddle_ocr'):
                CloudOCRParser._paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
            
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Perform OCR
            result = CloudOCRParser._paddle_ocr.ocr(image, cls=True)
            
            # Extract text
            text = ""
            for line in result[0]:
                text += line[1][0] + "\n"
            
            return text.strip()
            
        except Exception as e:
            print(f"  [PaddleOCR] Error: {e}")
            return ""
    
    # ===== MAIN PARSER METHODS =====
    
    @staticmethod
    def parse_pdf(file_path: str, ocr_backend: str = "aws") -> tuple[str, list[dict]]:
        """Extract text and tables from PDF"""
        text = ""
        tables = []
        
        # Try direct text extraction first
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                text += page_text + "\n"
        
        # If scanned PDF, use cloud OCR
        if len(text.strip()) < 50:
            print(f"  [Parser] Detected scanned PDF, using {ocr_backend} OCR...")
            
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
            
            if ocr_backend == "aws":
                text = CloudOCRParser.ocr_with_aws_textract(pdf_bytes)
            elif ocr_backend == "google":
                text = CloudOCRParser.ocr_with_google_vision(pdf_bytes)
            elif ocr_backend == "azure":
                text = CloudOCRParser.ocr_with_azure(pdf_bytes)
            elif ocr_backend == "easyocr":
                text = CloudOCRParser.ocr_with_easyocr(pdf_bytes)
            elif ocr_backend == "paddleocr":
                text = CloudOCRParser.ocr_with_paddleocr(pdf_bytes)
        
        # Extract tables
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
        text = "\n".join([para.text for para in doc.paragraphs])
        
        tables = []
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                table_data.append([cell.text for cell in row.cells])
            tables.append({"data": table_data})
        
        return text.strip(), tables
    
    @staticmethod
    def parse_image(file_path: str, ocr_backend: str = "aws") -> tuple[str, list[dict]]:
        """Extract text from image using cloud OCR"""
        
        with open(file_path, "rb") as f:
            image_bytes = f.read()
        
        if ocr_backend == "aws":
            text = CloudOCRParser.ocr_with_aws_textract(image_bytes)
        elif ocr_backend == "google":
            text = CloudOCRParser.ocr_with_google_vision(image_bytes)
        elif ocr_backend == "azure":
            text = CloudOCRParser.ocr_with_azure(image_bytes)
        elif ocr_backend == "easyocr":
            text = CloudOCRParser.ocr_with_easyocr(image_bytes)
        elif ocr_backend == "paddleocr":
            text = CloudOCRParser.ocr_with_paddleocr(image_bytes)
        else:
            text = ""
        
        return text.strip(), []
    
    @staticmethod
    def parse_document(file_path: str, ocr_backend: str = "aws") -> tuple[str, list[dict]]:
        """Parse document based on file extension"""
        ext = Path(file_path).suffix.lower()
        
        if ext == ".pdf":
            return CloudOCRParser.parse_pdf(file_path, ocr_backend)
        elif ext in [".docx", ".doc"]:
            return CloudOCRParser.parse_docx(file_path)
        elif ext in [".png", ".jpg", ".jpeg"]:
            return CloudOCRParser.parse_image(file_path, ocr_backend)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
