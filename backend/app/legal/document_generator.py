"""
Document Generator for Legal Advice

Generates PDF and DOC files from legal advice responses.
"""

import os
import tempfile
from datetime import datetime
from typing import Optional
from pathlib import Path


class DocumentGenerator:
    """Generate PDF and DOC documents from legal advice"""

    @staticmethod
    def generate_legal_document(
        advice_data: dict,
        format: str = "pdf",
        case_number: Optional[str] = None,
        case_title: Optional[str] = None
    ) -> str:
        """
        Generate a document from legal advice data.

        Args:
            advice_data: Legal advice response data
            format: Document format ('pdf' or 'doc')
            case_number: Optional case number for filename
            case_title: Optional case title for document

        Returns:
            Path to the generated document file
        """
        # Create temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_prefix = f"legal_advice_{case_number or 'case'}_{timestamp}"
        
        if format == "pdf":
            return DocumentGenerator._generate_pdf(
                advice_data, filename_prefix, case_number, case_title
            )
        elif format == "doc":
            return DocumentGenerator._generate_doc(
                advice_data, filename_prefix, case_number, case_title
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def _generate_pdf(
        advice_data: dict,
        filename_prefix: str,
        case_number: Optional[str],
        case_title: Optional[str]
    ) -> str:
        """Generate PDF document from legal advice"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
        except ImportError:
            # Fallback to text file if reportlab not available
            return DocumentGenerator._generate_text_file(
                advice_data, filename_prefix, case_number, case_title, "txt"
            )

        # Create temporary file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{filename_prefix}.pdf")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2196F3'),
            spaceAfter=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10,
            leading=14
        )

        # Build document content
        content = []
        
        # Title
        title = case_title or "Legal Advice"
        content.append(Paragraph(f"Legal Advice Report", title_style))
        if case_number:
            content.append(Paragraph(f"Case: {case_number}", normal_style))
        content.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
        content.append(Spacer(1, 0.3*inch))

        # Category
        if advice_data.get('category'):
            content.append(Paragraph("Legal Category", heading_style))
            content.append(Paragraph(advice_data['category'], normal_style))
            content.append(Spacer(1, 0.2*inch))

        # Summary
        if advice_data.get('summary'):
            content.append(Paragraph("Summary", heading_style))
            content.append(Paragraph(advice_data['summary'], normal_style))
            content.append(Spacer(1, 0.2*inch))

        # Advice
        if advice_data.get('advice'):
            content.append(Paragraph("Legal Advice", heading_style))
            content.append(Paragraph(advice_data['advice'], normal_style))
            content.append(Spacer(1, 0.2*inch))

        # Relevant Provisions
        if advice_data.get('relevant_provisions'):
            content.append(Paragraph("Relevant Legal Provisions", heading_style))
            for provision in advice_data['relevant_provisions']:
                if isinstance(provision, dict):
                    prov_text = f"<b>{provision.get('act', 'N/A')} - {provision.get('section', 'N/A')}</b><br/>"
                    prov_text += f"{provision.get('description', '')}"
                    content.append(Paragraph(prov_text, normal_style))
                    content.append(Spacer(1, 0.1*inch))
            content.append(Spacer(1, 0.2*inch))

        # Case Laws
        if advice_data.get('case_laws'):
            content.append(Paragraph("Relevant Case Laws", heading_style))
            for case_law in advice_data['case_laws']:
                if isinstance(case_law, dict):
                    case_text = f"<b>{case_law.get('case_name', 'N/A')}</b> ({case_law.get('year', 'N/A')})<br/>"
                    case_text += f"Court: {case_law.get('court', 'N/A')}<br/>"
                    case_text += f"{case_law.get('summary', '')}"
                    content.append(Paragraph(case_text, normal_style))
                    content.append(Spacer(1, 0.1*inch))
            content.append(Spacer(1, 0.2*inch))

        # Disclaimer
        content.append(Spacer(1, 0.3*inch))
        disclaimer = "<i><b>Disclaimer:</b> This legal advice is generated by AI and should not be considered as professional legal advice. Please consult with a qualified legal professional for specific legal matters.</i>"
        content.append(Paragraph(disclaimer, normal_style))

        # Build PDF
        doc.build(content)
        
        return file_path

    @staticmethod
    def _generate_doc(
        advice_data: dict,
        filename_prefix: str,
        case_number: Optional[str],
        case_title: Optional[str]
    ) -> str:
        """Generate DOC document from legal advice"""
        try:
            from docx import Document
            from docx.shared import RGBColor, Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH
        except ImportError:
            # Fallback to text file if python-docx not available
            return DocumentGenerator._generate_text_file(
                advice_data, filename_prefix, case_number, case_title, "txt"
            )

        # Create temporary file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{filename_prefix}.docx")
        
        # Create Word document
        doc = Document()
        
        # Title
        title = doc.add_heading('Legal Advice Report', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        if case_number:
            doc.add_paragraph(f"Case: {case_number}")
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        doc.add_paragraph()  # Empty line

        # Category
        if advice_data.get('category'):
            doc.add_heading('Legal Category', level=2)
            doc.add_paragraph(advice_data['category'])
            doc.add_paragraph()

        # Summary
        if advice_data.get('summary'):
            doc.add_heading('Summary', level=2)
            doc.add_paragraph(advice_data['summary'])
            doc.add_paragraph()

        # Advice
        if advice_data.get('advice'):
            doc.add_heading('Legal Advice', level=2)
            doc.add_paragraph(advice_data['advice'])
            doc.add_paragraph()

        # Relevant Provisions
        if advice_data.get('relevant_provisions'):
            doc.add_heading('Relevant Legal Provisions', level=2)
            for provision in advice_data['relevant_provisions']:
                if isinstance(provision, dict):
                    p = doc.add_paragraph()
                    p.add_run(f"{provision.get('act', 'N/A')} - {provision.get('section', 'N/A')}").bold = True
                    p.add_run(f"\n{provision.get('description', '')}")
            doc.add_paragraph()

        # Case Laws
        if advice_data.get('case_laws'):
            doc.add_heading('Relevant Case Laws', level=2)
            for case_law in advice_data['case_laws']:
                if isinstance(case_law, dict):
                    p = doc.add_paragraph()
                    p.add_run(f"{case_law.get('case_name', 'N/A')} ({case_law.get('year', 'N/A')})").bold = True
                    p.add_run(f"\nCourt: {case_law.get('court', 'N/A')}")
                    p.add_run(f"\n{case_law.get('summary', '')}")
            doc.add_paragraph()

        # Disclaimer
        doc.add_paragraph()
        disclaimer = doc.add_paragraph()
        disclaimer.add_run("Disclaimer: ").bold = True
        disclaimer.add_run("This legal advice is generated by AI and should not be considered as professional legal advice. Please consult with a qualified legal professional for specific legal matters.")
        disclaimer.italic = True

        # Save document
        doc.save(file_path)
        
        return file_path

    @staticmethod
    def _generate_text_file(
        advice_data: dict,
        filename_prefix: str,
        case_number: Optional[str],
        case_title: Optional[str],
        extension: str = "txt"
    ) -> str:
        """Generate plain text file as fallback"""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{filename_prefix}.{extension}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("LEGAL ADVICE REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            if case_number:
                f.write(f"Case: {case_number}\n")
            f.write(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n")
            
            if advice_data.get('category'):
                f.write("LEGAL CATEGORY\n")
                f.write("-" * 40 + "\n")
                f.write(f"{advice_data['category']}\n\n")
            
            if advice_data.get('summary'):
                f.write("SUMMARY\n")
                f.write("-" * 40 + "\n")
                f.write(f"{advice_data['summary']}\n\n")
            
            if advice_data.get('advice'):
                f.write("LEGAL ADVICE\n")
                f.write("-" * 40 + "\n")
                f.write(f"{advice_data['advice']}\n\n")
            
            if advice_data.get('relevant_provisions'):
                f.write("RELEVANT LEGAL PROVISIONS\n")
                f.write("-" * 40 + "\n")
                for provision in advice_data['relevant_provisions']:
                    if isinstance(provision, dict):
                        f.write(f"{provision.get('act', 'N/A')} - {provision.get('section', 'N/A')}\n")
                        f.write(f"{provision.get('description', '')}\n\n")
            
            if advice_data.get('case_laws'):
                f.write("RELEVANT CASE LAWS\n")
                f.write("-" * 40 + "\n")
                for case_law in advice_data['case_laws']:
                    if isinstance(case_law, dict):
                        f.write(f"{case_law.get('case_name', 'N/A')} ({case_law.get('year', 'N/A')})\n")
                        f.write(f"Court: {case_law.get('court', 'N/A')}\n")
                        f.write(f"{case_law.get('summary', '')}\n\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("DISCLAIMER\n")
            f.write("=" * 60 + "\n")
            f.write("This legal advice is generated by AI and should not be considered as professional legal advice. Please consult with a qualified legal professional for specific legal matters.\n")
        
        return file_path


# Convenience function
def generate_legal_document(
    advice_data: dict,
    format: str = "pdf",
    case_number: Optional[str] = None,
    case_title: Optional[str] = None
) -> str:
    """Generate legal document from advice data"""
    return DocumentGenerator.generate_legal_document(
        advice_data, format, case_number, case_title
    )
