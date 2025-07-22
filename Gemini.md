This project contains sensitive information in a `.env` file. It is critical that the contents of this file are not accessed or leaked.

## Project Setup

This project uses a Python virtual environment located at `.venv`. All Python-related commands, especially package installation (`pip`), should be executed using the binaries within this virtual environment (e.g., `.venv/bin/pip install ...`).

## How to Run

The main script is `script/run-user-interview.py`. To run the user interview agent, use the following command, replacing the topic as needed:

```bash
python script/run-user-interview.py --user-request "Your interview topic"
```

## Workflow

Our interactions will generally fall into three categories:

1.  **Consultation:** For general questions, advice, or discussions related to application development, architecture, or problem-solving.
2.  **Coding:** For tasks involving writing, modifying, or refactoring code to build or enhance applications.
3.  **Verification/Deployment:** For tasks related to testing, verifying functionality, or deploying applications.

### Generating PDF Reports

A new script, `script/convert_md_to_pdf.py`, has been added to convert Markdown reports to PDF format. This script utilizes `markdown-it-py` and `weasyprint` to create styled PDFs with proper headings and fonts.

To convert a Markdown report (e.g., `output/20250722-do-you-like-nike.md`) to PDF, use the following command:

```bash
.venv/bin/python script/convert_md_to_pdf.py output/20250722-do-you-like-nike.md
```

**Note:** Ensure the `markdown-it-py` and `weasyprint` libraries are installed in your virtual environment (`.venv/bin/pip install -r requirements.txt`) and that the `font/` directory contains `GenShinGothic-Regular.ttf` and `GenShinGothic-Bold.ttf` for optimal display of Japanese characters.