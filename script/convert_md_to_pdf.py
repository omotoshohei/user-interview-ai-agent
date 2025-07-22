import argparse
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Function to convert markdown to PDF
def convert_md_to_pdf(md_content: str, output_pdf_path: str):
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Register Japanese fonts from the 'font' directory
    try:
        # Define font paths
        regular_font_path = os.path.join(os.path.dirname(__file__), '..', 'font', 'GenShinGothic-Regular.ttf')
        bold_font_path = os.path.join(os.path.dirname(__file__), '..', 'font', 'GenShinGothic-Bold.ttf')

        # Register fonts
        pdfmetrics.registerFont(TTFont('GenShinGothic-Regular', regular_font_path))
        pdfmetrics.registerFont(TTFont('GenShinGothic-Bold', bold_font_path))

        # Assign fonts to styles
        styles['Normal'].fontName = 'GenShinGothic-Regular'
        styles['h1'].fontName = 'GenShinGothic-Bold'
        styles['h2'].fontName = 'GenShinGothic-Bold'
        styles['h3'].fontName = 'GenShinGothic-Bold'
    except Exception as e:
        print(f"Warning: Could not load Japanese font. Japanese characters may not display correctly in PDF. Error: {e}")

    for line in md_content.split('\n'):
        if line.startswith('# '):
            story.append(Paragraph(line[2:], styles['h1']))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], styles['h2']))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], styles['h3']))
        elif line.strip() == '':
            story.append(Spacer(1, 0.2 * 10))
        else:
            story.append(Paragraph(line, styles['Normal']))
    
    doc.build(story)

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown file to PDF.")
    parser.add_argument("markdown_file", help="Path to the input markdown file.")
    args = parser.parse_args()

    if not os.path.exists(args.markdown_file):
        print(f"Error: File not found at {args.markdown_file}")
        return

    output_pdf_path = os.path.splitext(args.markdown_file)[0] + ".pdf"

    with open(args.markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    convert_md_to_pdf(md_content, output_pdf_path)
    print(f"Successfully converted {args.markdown_file} to {output_pdf_path}")

if __name__ == "__main__":
    main()
