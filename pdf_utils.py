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

def create_summary_pdf(summary, sentiment):
    """Create a PDF with the meeting summary and analysis"""
    # Create a Unicode-compatible PDF
    pdf = SummaryPDF()
    # Add a font that supports various languages
    pdf.add_page()
    
    # Add summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Summary', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    # Handle non-ASCII characters in summary
    try:
        pdf.multi_cell(0, 5, summary)
    except UnicodeEncodeError:
        # If encoding fails, try to encode as UTF-8 compatible text
        pdf.multi_cell(0, 5, summary.encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.ln(5)
    
    # Add sentiment analysis
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Sentiment Analysis', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    # Handle non-ASCII characters in sentiment
    try:
        pdf.multi_cell(0, 5, sentiment)
    except UnicodeEncodeError:
        # If encoding fails, try to encode as UTF-8 compatible text
        pdf.multi_cell(0, 5, sentiment.encode('latin-1', 'replace').decode('latin-1'))
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file_path = temp_file.name
    temp_file.close()
    
    # Save PDF to temporary file
    try:
        pdf.output(temp_file_path)
    except Exception as e:
        st.error(f"Error creating PDF: {e}")
        # Create a fallback basic PDF if original fails
        basic_pdf = FPDF()
        basic_pdf.add_page()
        basic_pdf.set_font('Arial', 'B', 16)
        basic_pdf.cell(40, 10, 'Summary')
        basic_pdf.output(temp_file_path)
    
    return temp_file_path

def get_pdf_download_link(pdf_path, filename="meeting_summary.pdf"):
    """Generate a download link for the PDF file
    
    Note: This function is kept for backwards compatibility, but we recommend using
    Streamlit's native download_button instead.
    """
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        b64_pdf = base64.b64encode(pdf_bytes).decode()
        # Make the link more prominent and add some styling
        href = f'''
        <a href="data:application/pdf;base64,{b64_pdf}" 
           download="{filename}" 
           style="display: inline-block; padding: 10px 20px; 
                  background-color: #4CAF50; color: white; 
                  text-align: center; text-decoration: none; 
                  font-size: 16px; border-radius: 4px;">
           📥 Download Summary as PDF
        </a>
        '''
        
        # Don't delete the file yet - do it on next run
        if 'pdf_to_cleanup' in st.session_state and st.session_state.pdf_to_cleanup != pdf_path:
            try:
                os.unlink(st.session_state.pdf_to_cleanup)
            except:
                pass
        
        # Store the current PDF path for cleanup next time
        st.session_state.pdf_to_cleanup = pdf_path
            
        return href
    except Exception as e:
        st.error(f"Error creating PDF download link: {e}")
        return "PDF download failed. Please try again."