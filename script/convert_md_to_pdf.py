import argparse
import os
import datetime
from markdown_it import MarkdownIt
from weasyprint import HTML, CSS

# Function to convert markdown to PDF
def convert_md_to_pdf(md_content: str, output_pdf_path: str):
    # Add a timestamp to the output file name
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_pdf_path = f"{os.path.splitext(output_pdf_path)[0]}-{timestamp}.pdf"

    # Convert markdown to HTML
    md = MarkdownIt()
    html_content = md.render(md_content)

    # CSS for styling
    css = CSS(string='''
        @font-face {
            font-family: 'GenShinGothic';
            src: url('../font/GenShinGothic-Regular.ttf');
        }
        @font-face {
            font-family: 'GenShinGothic-Bold';
            src: url('../font/GenShinGothic-Bold.ttf');
        }
        body {
            font-family: 'GenShinGothic', sans-serif;
            font-size: 12px;
        }
        h1 {
            font-family: 'GenShinGothic-Bold', sans-serif;
            font-size: 24px;
        }
        h2 {
            font-family: 'GenShinGothic-Bold', sans-serif;
            font-size: 18px;
        }
        h3 {
            font-family: 'GenShinGothic-Bold', sans-serif;
            font-size: 14px;
        }
    ''')

    # Create PDF
    HTML(string=html_content).write_pdf(output_pdf_path, stylesheets=[css])
    print(f"Successfully converted markdown to {output_pdf_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown file to PDF.")
    parser.add_argument("markdown_file", help="Path to the input markdown file.")
    args = parser.parse_args()

    if not os.path.exists(args.markdown_file):
        print(f"Error: File not found at {args.markdown_file}")
        return

    output_pdf_path = os.path.join('output', os.path.basename(os.path.splitext(args.markdown_file)[0]) + ".pdf")

    with open(args.markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    convert_md_to_pdf(md_content, output_pdf_path)

if __name__ == "__main__":
    main()
