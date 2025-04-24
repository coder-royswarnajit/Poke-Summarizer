# pdf_utils.py
import streamlit as st
from fpdf import FPDF
import base64
import os
import tempfile
from datetime import datetime

class SummaryPDF(FPDF):
    def header(self):
        # Set up header with logo and title
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Poke Summarizer - Meeting Summary', 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        # Add footer with page numbers
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'R')

def create_summary_pdf(summary,sentiment):
    """Create a PDF with the meeting summary and analysis"""
    pdf = SummaryPDF()
    pdf.add_page()
    
    # Add summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Summary', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 5, summary)
    pdf.ln(5)
    
    
    # Add sentiment analysis
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Sentiment Analysis', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 5, sentiment)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file_path = temp_file.name
    temp_file.close()
    
    # Save PDF to temporary file
    pdf.output(temp_file_path)
    
    return temp_file_path

def get_pdf_download_link(pdf_path, filename="meeting_summary.pdf"):
    """Generate a download link for the PDF file"""
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    b64_pdf = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}">Download Summary as PDF</a>'
    
    # Cleanup the temporary file
    try:
        os.unlink(pdf_path)
    except Exception as e:
        st.warning(f"Error cleaning up temporary file: {e}")
        
    return href