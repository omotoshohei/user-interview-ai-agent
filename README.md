# User Interview AI Agent

This project implements an AI agent designed to conduct user interviews and generate reports. It's a demonstration of an automated system for gathering user feedback and insights.

## Project Setup

To set up the project, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/user-interview-ai-agent.git
    cd user-interview-ai-agent
    ```

2.  **Create and activate a Python virtual environment:**
    This project uses `uv` for dependency management. If you don't have `uv` installed, you can install it via `pip install uv`.
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

## How to Run

The main script for conducting user interviews is `script/run-user-interview.py`.

To run the user interview agent, use the following command, replacing `"Your interview topic"` with the desired topic:

```bash
python script/run-user-interview.py --user-request "Your interview topic"
```

## Generating PDF Reports

A utility script `script/convert_md_to_pdf.py` is provided to convert the generated Markdown reports into PDF format. This script uses `markdown-it-py` and `weasyprint` for styled PDF output.

To convert a Markdown report (e.g., `output/20250722-do-you-like-nike.md`) to PDF, use:

```bash
.venv/bin/python script/convert_md_to_pdf.py output/20250722-do-you-like-nike.md
```

**Note:** Ensure that the `font/` directory contains `GenShinGothic-Regular.ttf` and `GenShinGothic-Bold.ttf` for proper display of Japanese characters in the PDF reports.

## Sensitive Information

This project may involve sensitive information, particularly within a `.env` file for API keys or configurations. It is crucial that the contents of this file are not exposed or committed to public repositories. The `.gitignore` file is configured to prevent this.
