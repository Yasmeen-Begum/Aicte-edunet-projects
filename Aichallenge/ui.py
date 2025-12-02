"""
Gradio web interface
"""

import logging
from pathlib import Path
from datetime import datetime

import gradio as gr
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from vector_store import VectorStoreManager
from llm_manager import LLMManager
from agents import MedicalReportCrew

logger = logging.getLogger(__name__)

class MedicalSummarizerUI:
    """Gradio interface for the application"""
    
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.llm_manager = LLMManager(self.vector_store)
        self.crew = MedicalReportCrew(self.vector_store, self.llm_manager)
        self.session_history = []
        self.last_summary = None
    
    def process_file(self, file, custom_followup_date, progress=gr.Progress()):
        """Process uploaded file and return summary"""
        if file is None:
            return "Please upload a file.", "", None, ""
        
        try:
            def update_progress(status, value):
                progress(value, desc=status)
            
            # Process the report
            summary = self.crew.process_report(file.name, update_progress)
            
            # Store in session history
            self.session_history.append({
                "filename": Path(file.name).name,
                "summary": summary,
                "timestamp": summary.timestamp
            })
            
            # Store last summary for PDF generation
            self.last_summary = {
                "filename": Path(file.name).name,
                "summary": summary,
                "custom_followup": custom_followup_date
            }
            
            # Determine which follow-up date to use
            follow_up_display = custom_followup_date if custom_followup_date else (getattr(summary, 'follow_up_date', None) or "Not specified")
            
            # Format output
            result = f"""
# Medical Report Summary

**File:** {Path(file.name).name}
**Processed:** {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Processing Time:** {summary.processing_time:.2f} seconds

---

{summary.summary_text}

---

**Document ID:** {summary.document_id}
**Total Reports in Session:** {len(self.session_history)}
"""
            
            stats = f"Processing Time: {summary.processing_time:.2f}s | Reports Processed: {len(self.session_history)}"
            
            # Generate PDF
            pdf_path = self._generate_pdf(Path(file.name).name, summary, custom_followup_date)
            
            return result, stats, pdf_path, follow_up_display
            
        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            logger.error(error_msg)
            return error_msg, "Error occurred", None, ""
    
    def _generate_pdf(self, filename: str, summary, custom_followup_date=None) -> str:
        """Generate PDF from summary"""
        try:
            # Create PDF filename
            pdf_filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = Path("./outputs") / pdf_filename
            pdf_path.parent.mkdir(exist_ok=True)
            
            # Create PDF
            doc = SimpleDocTemplate(str(pdf_path), pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#2C3E50',
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor='#34495E',
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Add title
            elements.append(Paragraph("Medical Report Summary", title_style))
            elements.append(Spacer(1, 12))
            
            # Add metadata
            elements.append(Paragraph(f"<b>Original File:</b> {filename}", styles['Normal']))
            elements.append(Paragraph(f"<b>Generated:</b> {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            elements.append(Paragraph(f"<b>Processing Time:</b> {summary.processing_time:.2f} seconds", styles['Normal']))
            elements.append(Paragraph(f"<b>Document ID:</b> {summary.document_id}", styles['Normal']))
            
            # Add follow-up date
            follow_up = custom_followup_date if custom_followup_date else (getattr(summary, 'follow_up_date', None) or "Not specified")
            elements.append(Paragraph(f"<b>Next Check-up:</b> {follow_up}", styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Add summary content
            summary_lines = summary.summary_text.split('\n')
            for line in summary_lines:
                if line.startswith('## '):
                    # Heading
                    elements.append(Spacer(1, 12))
                    elements.append(Paragraph(line.replace('## ', ''), heading_style))
                elif line.strip():
                    # Regular text
                    elements.append(Paragraph(line, styles['Normal']))
                    elements.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"PDF generated: {pdf_path}")
            return str(pdf_path)
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            return None
    
    def launch(self):
        """Launch Gradio interface"""
        
        with gr.Blocks(title="Medical Report Summarizer", theme=gr.themes.Soft()) as interface:
            gr.Markdown("""
            # Medical Report Summarizer
            
            Upload medical reports (PDF, TXT, DOCX, JPG, PNG, WebP) to get AI-powered summaries with dietary recommendations.
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    file_input = gr.File(
                        label="Upload Medical Report",
                        file_types=[".pdf", ".txt", ".docx", ".jpg", ".jpeg", ".png", ".webp"]
                    )
                    
                    gr.Markdown("### Next Check-up Date")
                    followup_date_input = gr.Textbox(
                        label="Set Custom Follow-up Date (Optional)",
                        placeholder="e.g., 2024-12-15 or In 2 weeks",
                        info="Leave empty to use auto-detected date from report"
                    )
                    
                    submit_btn = gr.Button("Generate Summary", variant="primary", size="lg")
                    
                    followup_display = gr.Textbox(
                        label="Detected/Set Follow-up Date",
                        interactive=False,
                        value=""
                    )
                    
                    stats_output = gr.Textbox(label="Statistics", interactive=False)
                    pdf_download = gr.File(label="Download Summary as PDF", interactive=False)
                
                with gr.Column(scale=2):
                    summary_output = gr.Markdown(label="Summary")
            
          
            
            submit_btn.click(
                fn=self.process_file,
                inputs=[file_input, followup_date_input],
                outputs=[summary_output, stats_output, pdf_download, followup_display]
            )
        
        interface.launch(share=False, server_name="0.0.0.0", server_port=7860)
