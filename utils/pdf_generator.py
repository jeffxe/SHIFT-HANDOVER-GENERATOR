import re
from fpdf import FPDF

class SRE_PDF(FPDF):
    def header(self):
        # Draw a thick orange line at the very top of every page
        self.set_fill_color(255, 107, 0)
        self.rect(0, 0, 210, 4, "F")

def clean_text_for_pdf(text: str) -> str:
    """
    Replaces common emojis with text labels and filters out unsupported unicode
    characters to prevent CP-1252 encoding errors in standard PDF fonts.
    """
    replacements = {
        "🔄": "Shift",
        "🔴": "CRITICAL -",
        "⚠️": "WARNING -",
        "✅": "RESOLVED -",
        "👀": "WATCHLIST -",
        "💡": "RECOMMENDATIONS -",
        "📊": "SUMMARY -",
        "🏥": "HEALTH -",
        "📋": "ISSUES -",
        "🔓": "OPEN -",
        "🗑️": "DUPLICATES -",
        "⚡": "RUN -",
        "🤖": "AGENT -",
        "📄": "REPORT -"
    }
    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)
        
    # Replace non-latin1 characters with '?' to avoid crashing FPDF
    cleaned = []
    for char in text:
        try:
            char.encode('latin-1')
            cleaned.append(char)
        except UnicodeEncodeError:
            cleaned.append("?")
    return "".join(cleaned)

def markdown_to_pdf(markdown_text: str) -> bytes:
    """
    Parses a markdown report and renders it to a visually polished
    orange and black SRE PDF document using FPDF2.
    """
    markdown_text = clean_text_for_pdf(markdown_text)
    
    pdf = SRE_PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    
    lines = markdown_text.split("\n")
    current_table_rows = []
    
    def render_pending_table():
        nonlocal current_table_rows
        if current_table_rows:
            # Table border line color (neutral light gray)
            pdf.set_draw_color(180, 180, 180)
            
            with pdf.table(col_widths=None, text_align="LEFT") as table:
                for row_idx, row in enumerate(current_table_rows):
                    row_cells = table.row()
                    for cell in row:
                        if row_idx == 0:
                            # Table Header: SRE Orange Background, White Text
                            pdf.set_fill_color(255, 107, 0)
                            pdf.set_text_color(255, 255, 255)
                            pdf.set_font("Helvetica", style="B", size=9)
                        else:
                            # Table Rows: White Background, Dark Gray Text
                            pdf.set_fill_color(255, 255, 255)
                            pdf.set_text_color(30, 30, 30)
                            pdf.set_font("Helvetica", style="", size=9)
                        row_cells.cell(cell)
            pdf.ln(4)
            current_table_rows = []

    for line in lines:
        stripped = line.strip()
        
        # Check if it is a table row
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            is_separator = all(re.match(r'^:?-+:?$', c) for c in cells) if cells else False
            if not is_separator and cells:
                current_table_rows.append(cells)
            continue
        else:
            render_pending_table()
            
        if not stripped:
            pdf.ln(3)
            continue
            
        # Parse headers
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            # Title: Bold Orange
            pdf.set_text_color(255, 107, 0)
            pdf.set_font("Helvetica", style="B", size=18)
            pdf.multi_cell(pdf.epw, 10, title, markdown=True)
            pdf.ln(3)
        elif stripped.startswith("## "):
            subtitle = stripped[3:].strip()
            # Section headers: Bold Orange
            pdf.set_text_color(255, 107, 0)
            pdf.set_font("Helvetica", style="B", size=13)
            pdf.multi_cell(pdf.epw, 8, subtitle, markdown=True)
            pdf.ln(2)
        elif stripped.startswith("### "):
            subsubtitle = stripped[4:].strip()
            # Sub-section headers: Bold Dark Gray
            pdf.set_text_color(50, 50, 50)
            pdf.set_font("Helvetica", style="B", size=11)
            pdf.multi_cell(pdf.epw, 8, subsubtitle, markdown=True)
            pdf.ln(2)
        elif stripped.startswith("* ") or stripped.startswith("- ") or stripped.startswith("+ "):
            # Bullet lists: Orange bullet symbol, Dark text
            bullet_text = stripped[2:].strip()
            pdf.set_text_color(255, 107, 0)
            pdf.write(6, "* ")
            pdf.set_text_color(30, 30, 30)
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(pdf.epw, 6, bullet_text, markdown=True)
        else:
            # Paragraph text: Dark text
            indent = "    " if line.startswith("    ") or line.startswith("\t") else ""
            pdf.set_text_color(30, 30, 30)
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(pdf.epw, 6, f"{indent}{stripped}", markdown=True)
            
    # Render any remaining table
    render_pending_table()
    return bytes(pdf.output())
