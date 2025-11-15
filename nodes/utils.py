"""
Utility functions for the LangGraph application.
"""


def extract_pdf_content(pdf: dict) -> str:
    """
    Mock function to simulate PDF content extraction.
    
    In a real implementation, this would extract text from PDF based on the type.
    For now, it returns mocked extracted text.
    
    Args:
        pdf: Dictionary with 'type' and 'data' fields
        
    Returns:
        Mocked extracted text from the PDF
    """
    if not pdf or pdf.get("type") is None:
        return ""
    
    pdf_type = pdf.get("type", "unknown")
    pdf_data = pdf.get("data", "")
    
    # Mock extraction based on type
    if pdf_type == "base64":
        return f"[Mocked PDF extraction] Document provided as base64. Content summary: Research findings on longevity and health optimization."
    elif pdf_type == "url":
        return f"[Mocked PDF extraction] Document from URL: {pdf_data[:50] if pdf_data else 'N/A'}. Content summary: Medical research and clinical data."
    elif pdf_type == "file_id":
        return f"[Mocked PDF extraction] Document with file_id: {pdf_data}. Content summary: Patient health records and analysis."
    else:
        return "[Mocked PDF extraction] Unknown document type."

