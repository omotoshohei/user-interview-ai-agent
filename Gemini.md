This project contains sensitive information in a `.env` file. It is critical that the contents of this file are not accessed or leaked.

## Project Setup

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

## How to Run

### User Interview Agent
Generates diverse personas and conducts simulated interviews on a given topic.
```bash
PYTHONPATH=script python script/run-user-interview.py --user-request "Your topic" --k 10
```
Output: `output/general-question/YYYYMMDD-<topic>.md`

### SEO Search Intent Evaluation Agent
Evaluates product descriptions using 3 search intent personas (informational, navigational, transactional).
```bash
PYTHONPATH=script python script/run-seo-search-intent-evaluation.py --keyword "keyword" --content "text..."
PYTHONPATH=script python script/run-seo-search-intent-evaluation.py --keyword "keyword" --content-file "file.txt"
```
Output: `output/seo-evaluation/YYYYMMDD-eval-<keyword>.md`

### Translation Evaluation Agent
Evaluates EN→JP translations using 3 reader-perspective personas.
```bash
PYTHONPATH=script python script/run-translation-evaluation.py --source "English" --translation "日本語"
PYTHONPATH=script python script/run-translation-evaluation.py --source-file "en.txt" --translation-file "jp.txt"
```
Output: `output/translation/YYYYMMDD-translation-eval.md`

### Sentence Evaluation Agent
Evaluates marketing/business sentences using dynamically generated personas.
```bash
PYTHONPATH=script python script/run-sentence-evaluation.py --background "context" --sentence "text"
PYTHONPATH=script python script/run-sentence-evaluation.py --background-file "context.txt" --sentence "text"
```
Output: `output/sentence-evaluation/YYYYMMDD-sentence-eval.md`

### PDF Generation
```bash
python script/convert_md_to_pdf.py output/<folder>/<report>.md
```
Note: Requires `GenShinGothic-*.ttf` in `font/` for Japanese support.

## Workflow

1. **Consultation:** General questions, advice, or discussions
2. **Coding:** Writing, modifying, or refactoring code
3. **Verification/Deployment:** Testing, verifying, or running scripts
