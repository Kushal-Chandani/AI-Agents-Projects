from fpdf import FPDF
import re

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(255, 75, 75) # Accent color
        self.cell(0, 10, 'AI Fitness & Diet Plan', 0, 1, 'C')
        self.line(10, 20, 200, 20)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def clean_text(text):
    """Clean text for FPDF compatibility (Latin-1) and remove Markdown."""
    # Remove emojis and unsupported chars by encoding/decoding
    try:
        text = text.encode('latin-1', 'replace').decode('latin-1')
    except:
        text = str(text)
    
    # Simple markdown cleanup
    text = text.replace('**', '').replace('__', '')
    return text

def generate_pdf(title, content):
    """Generate a PDF file from text content."""
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Document Title
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0)
    pdf.cell(0, 10, clean_text(title), 0, 1, 'L')
    pdf.ln(5)
    
    # Content Body
    pdf.set_font("Arial", size=11)
    
    lines = content.split('\n')
    for line in lines:
        cleaned = clean_text(line)
        
        # Simple Header detection based on Markdown #
        if line.strip().startswith('#'):
            pdf.ln(4)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(50)
            # Remove hash and render
            header_text = re.sub(r'^#+\s*', '', cleaned)
            pdf.multi_cell(0, 8, header_text)
            pdf.set_font("Arial", size=11)
            pdf.set_text_color(0)
        elif line.strip().startswith('-') or line.strip().startswith('*'):
             # Bullet points
             pdf.set_x(15) # Indent
             pdf.multi_cell(0, 6, cleaned)
        else:
            # Normal text
            pdf.set_x(10)
            pdf.multi_cell(0, 6, cleaned)
            
    return pdf.output(dest='S').encode('latin-1')
