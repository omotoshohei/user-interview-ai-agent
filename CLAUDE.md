# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI agents built with LangGraph that use persona-based analysis for user research and content evaluation. Each agent generates personas, conducts simulated interactions, and produces structured reports.

## Project Structure

```
script/
├── shared/
│   ├── __init__.py              # Exports shared models and i18n
│   ├── persona_base.py          # Base Persona, Personas models
│   └── i18n.py                  # Bilingual translations (EN/JP)
├── run-user-interview.py        # User Interview Agent
├── run-seo-search-intent-evaluation.py  # SEO Search Intent Evaluation Agent
├── run-translation-evaluation.py # Translation Evaluation Agent
├── run-sentence-evaluation.py   # Sentence Evaluation Agent
└── convert_md_to_pdf.py         # Markdown to PDF converter

output/
├── general-question/            # User Interview reports
├── seo-evaluation/              # SEO Search Intent Evaluation reports
├── translation/                 # Translation Evaluation reports
└── sentence-evaluation/         # Sentence Evaluation reports

examples/                        # Sample output reports
doc/                             # Project documentation
font/                            # Japanese fonts for PDF generation
```

## Commands

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Run user interview agent
PYTHONPATH=script python script/run-user-interview.py --user-request "Your topic" --k 10
PYTHONPATH=script python script/run-user-interview.py --user-request "Your topic" --k 10 --lang jp

# Run SEO search intent evaluation agent
PYTHONPATH=script python script/run-seo-search-intent-evaluation.py --keyword "keyword" --content "text..."
PYTHONPATH=script python script/run-seo-search-intent-evaluation.py --keyword "keyword" --content-file "file.txt" --lang jp

# Run translation evaluation agent (default: Japanese output)
PYTHONPATH=script python script/run-translation-evaluation.py --source "English text" --translation "日本語翻訳"
PYTHONPATH=script python script/run-translation-evaluation.py --source-file "en.txt" --translation-file "jp.txt" --lang en

# Run sentence evaluation agent
PYTHONPATH=script python script/run-sentence-evaluation.py --background "context" --sentence "text to evaluate"
PYTHONPATH=script python script/run-sentence-evaluation.py --background-file "context.txt" --sentence "text" --lang jp

# Convert markdown report to PDF
python script/convert_md_to_pdf.py output/<folder>/<report>.md
```

**Language flag (`--lang`):** All agents support `--lang en` (English) or `--lang jp` (Japanese) for both prompts and report output. Defaults: `en` for all agents except Translation Evaluation which defaults to `jp`.

## Architecture

**Shared Components** (`script/shared/`):
- `Persona`, `Personas` - Base Pydantic models used by all agents
- `i18n` module - Bilingual support with `t()` for labels and `p()` for prompts

**User Interview Agent** (`script/run-user-interview.py`):
- Pipeline: `generate_personas` → `conduct_interviews` → `generate_output` → END
- Generates k diverse personas, simulates Q&A interviews, produces insight report
- Includes full interview transcripts with each persona's Q&A

**SEO Search Intent Evaluation Agent** (`script/run-seo-search-intent-evaluation.py`):
- Pipeline: `generate_personas` → `conduct_evaluations` → `generate_summary` → END
- Creates 3 search intent personas (informational, navigational, transactional)
- Each persona has a "looking_for" list of specific information they seek
- Conversational evaluation: "Did you find the information about X?"
- Scoring: Relevance, Clarity, Completeness, Persuasiveness (1-10 scale)

**Translation Evaluation Agent** (`script/run-translation-evaluation.py`):
- Pipeline: `generate_personas` → `evaluate_translation` → `generate_report` → END
- Creates 3 reader-perspective personas (business professional, young adult, general consumer)
- Evaluates EN→JP translation naturalness, identifies issues with rewrite suggestions
- Scoring: Naturalness, Fluency, Tone Appropriateness, Clarity (1-10 scale)

**Sentence Evaluation Agent** (`script/run-sentence-evaluation.py`):
- Pipeline: `generate_personas` → `evaluate_sentence` → `generate_report` → END
- Dynamically generates 3 personas based on background context (not fixed types)
- Evaluates marketing/business writing sentences
- Scoring: Clarity, Impact, Tone, Persuasiveness (1-10 scale)

## Output Formats

**User Interview Reports** (`output/general-question/YYYYMMDD-<topic>.md`):
- Research Outline (topic, method, persona count)
- Generated Personas
- Interview Details (Q&A per persona)
- Executive Summary
- Quantitative Stats
- Key Qualitative Insights
- Recommended Next Actions

**SEO Search Intent Evaluation Reports** (`output/seo-evaluation/YYYYMMDD-eval-<keyword>.md`):
- Research Outline (keyword, content, method, overall score)
- Personas Generated (with "Looking for" list per persona)
- Evaluation Dialogues (conversational Q&A per persona)
- Scores Summary table
- Recommendations

**Translation Evaluation Reports** (`output/translation/YYYYMMDD-translation-eval.md`):
- 評価概要 (source, translation, method, overall score)
- 評価ペルソナ (3 reader personas)
- 評価詳細 (issues with severity and rewrite suggestions)
- スコアサマリー table
- 改善提案まとめ

**Sentence Evaluation Reports** (`output/sentence-evaluation/YYYYMMDD-sentence-eval.md`):
- Evaluation Context (background, sentence, overall score)
- Generated Personas (dynamically created from context)
- Evaluation Details (strengths, weaknesses per persona)
- Scores Summary table
- Recommendations

## Configuration

- `OPENAI_API_KEY` required in `.env` file
- Default model: `gpt-4.1-mini-2025-04-14`
- Japanese fonts (`GenShinGothic-*.ttf`) in `font/` for PDF generation
