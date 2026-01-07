import operator
import argparse
import os
from datetime import datetime
from typing import Annotated, Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
ChatOpenAI.model_rebuild()
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from shared import Persona, LanguageCode, t, p

###### Use dotenv if available ######
try:
    from dotenv import load_dotenv
    from pathlib import Path
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    import warnings
    warnings.warn("dotenv not found. Please set environment variables manually.", ImportWarning)
################################################


# Data Models
class TranslationPersona(Persona):
    """Persona for evaluating Japanese translations from a reader's perspective."""
    reader_type: str = Field(..., description="Type of reader: business_professional, young_adult, general_consumer")
    age_range: str = Field(..., description="Age range of the persona")
    reading_context: str = Field(..., description="Context in which they read marketing content")


class TranslationPersonas(BaseModel):
    """List of translation evaluation personas."""
    personas: list[TranslationPersona] = Field(
        default_factory=list, description="List of translation personas"
    )


class TranslationIssue(BaseModel):
    """A single issue found in the translation."""
    original_phrase: str = Field(..., description="The problematic phrase in the translation")
    issue_type: str = Field(..., description="Type of issue: unnatural_phrasing, awkward_word_choice, tone_mismatch, grammatical_error, cultural_inappropriateness")
    severity: str = Field(..., description="Severity: minor, moderate, major")
    explanation: str = Field(..., description="Why this phrase sounds unnatural")
    suggested_rewrite: str = Field(..., description="Suggested natural Japanese alternative")


class TranslationEvaluation(BaseModel):
    """Evaluation result from a single persona."""
    persona: TranslationPersona = Field(..., description="The persona who evaluated")
    overall_impression: str = Field(..., description="Overall impression of the translation")
    issues: list[TranslationIssue] = Field(default_factory=list, description="Issues found")
    scores: dict[str, int] = Field(default_factory=dict, description="Scores by criteria")
    positive_points: list[str] = Field(default_factory=list, description="What works well")


class TranslationEvaluationResult(BaseModel):
    """Container for all evaluations."""
    evaluations: list[TranslationEvaluation] = Field(
        default_factory=list, description="List of persona evaluations"
    )


class TranslationEvaluationState(BaseModel):
    """State for the translation evaluation agent."""
    source_text: str = Field(..., description="Original English text")
    translated_text: str = Field(..., description="Japanese translation to evaluate")
    language: LanguageCode = Field(default="jp", description="Output language")
    personas: Annotated[list[TranslationPersona], operator.add] = Field(
        default_factory=list, description="Generated personas"
    )
    evaluations: Annotated[list[TranslationEvaluation], operator.add] = Field(
        default_factory=list, description="Evaluation results"
    )
    summary_report: str = Field(default="", description="Final summary report")


# Core Classes
class TranslationPersonaGenerator:
    """Generates reader perspective personas for translation evaluation."""

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "jp"):
        self.llm = llm.with_structured_output(TranslationPersonas)
        self.lang = lang

    def run(self, source_text: str) -> TranslationPersonas:
        prompt = ChatPromptTemplate.from_messages([
            ("system", p("translation_evaluation", "persona_generator_system", self.lang)),
            ("human", p("translation_evaluation", "persona_generator_human", self.lang)),
        ])
        chain = prompt | self.llm
        return chain.invoke({"source_text": source_text})


class TranslationEvaluator:
    """Evaluates Japanese translation from each persona's perspective."""

    SCORING_CRITERIA = ["naturalness", "fluency", "tone_appropriateness", "clarity"]

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "jp"):
        self.llm = llm
        self.lang = lang

    def run(self, source_text: str, translated_text: str, personas: list[TranslationPersona]) -> TranslationEvaluationResult:
        evaluations = []
        for persona in personas:
            evaluation = self._evaluate_for_persona(source_text, translated_text, persona)
            evaluations.append(evaluation)
        return TranslationEvaluationResult(evaluations=evaluations)

    def _evaluate_for_persona(self, source_text: str, translated_text: str, persona: TranslationPersona) -> TranslationEvaluation:
        # Get overall impression and positive points
        impression_data = self._get_impression(source_text, translated_text, persona)
        # Find issues
        issues = self._find_issues(source_text, translated_text, persona)
        # Generate scores
        scores = self._generate_scores(translated_text, persona, issues)

        return TranslationEvaluation(
            persona=persona,
            overall_impression=impression_data["impression"],
            issues=issues,
            scores=scores,
            positive_points=impression_data["positives"]
        )

    def _get_impression(self, source_text: str, translated_text: str, persona: TranslationPersona) -> dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", p("translation_evaluation", "impression_system", self.lang)),
            ("human", p("translation_evaluation", "impression_human", self.lang)),
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "persona_name": persona.name,
            "persona_background": persona.background,
            "age_range": persona.age_range,
            "reading_context": persona.reading_context,
            "source_text": source_text,
            "translated_text": translated_text
        })

        import json
        try:
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            return json.loads(result)
        except (json.JSONDecodeError, KeyError):
            return {"impression": "評価できませんでした", "positives": []}

    def _find_issues(self, source_text: str, translated_text: str, persona: TranslationPersona) -> list[TranslationIssue]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", p("translation_evaluation", "issues_system", self.lang)),
            ("human", p("translation_evaluation", "issues_human", self.lang)),
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "persona_name": persona.name,
            "persona_background": persona.background,
            "source_text": source_text,
            "translated_text": translated_text
        })

        import json
        try:
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            issues_data = json.loads(result)
            return [TranslationIssue(**issue) for issue in issues_data]
        except (json.JSONDecodeError, KeyError, TypeError):
            return []

    def _generate_scores(self, translated_text: str, persona: TranslationPersona, issues: list[TranslationIssue]) -> dict[str, int]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", p("translation_evaluation", "scores_system", self.lang)),
            ("human", p("translation_evaluation", "scores_human", self.lang)),
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "persona_name": persona.name,
            "translated_text": translated_text,
            "issue_count": len(issues)
        })

        import json
        try:
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            return json.loads(result)
        except (json.JSONDecodeError, KeyError):
            return {c: 5 for c in self.SCORING_CRITERIA}


class TranslationReportGenerator:
    """Generates the final summary report."""

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "jp"):
        self.llm = llm
        self.lang = lang

    def run(self, source_text: str, translated_text: str, evaluations: list[TranslationEvaluation]) -> str:
        report = [f"# {t('translation_eval_title', self.lang)}\n\n"]

        # Research Outline
        report.append(f"## {t('research_outline', self.lang)}\n\n")
        report.append(f"**{t('source_text', self.lang)}:**\n")
        report.append(f"> {source_text}\n\n")
        report.append(f"**{t('translated_text', self.lang)}:**\n")
        report.append(f"> {translated_text}\n\n")
        report.append(f"**{t('method', self.lang)}:** {t('evaluation_method_translation', self.lang)}\n\n")
        report.append(f"**{t('number_of_personas', self.lang)}:** {len(evaluations)}\n\n")

        # Calculate overall score
        all_scores = {"naturalness": [], "fluency": [], "tone_appropriateness": [], "clarity": []}
        for ev in evaluations:
            for criterion in all_scores:
                if criterion in ev.scores:
                    all_scores[criterion].append(ev.scores[criterion])

        avg_scores = {k: sum(v)/len(v) if v else 0 for k, v in all_scores.items()}
        overall_avg = sum(avg_scores.values()) / len(avg_scores) if avg_scores else 0

        report.append(f"**{t('overall_score', self.lang)}:** {overall_avg:.1f}/10\n\n")
        report.append("---\n\n")

        # Personas section
        report.append(f"## {t('evaluation_personas', self.lang)}\n\n")
        for i, ev in enumerate(evaluations, 1):
            persona = ev.persona
            report.append(f"**{t('persona', self.lang)} {i}: {persona.name}** ({persona.reader_type})\n")
            report.append(f"- {t('age_range', self.lang)}: {persona.age_range}\n")
            report.append(f"- {t('background', self.lang)}: {persona.background}\n")
            report.append(f"- {t('reading_context', self.lang)}: {persona.reading_context}\n\n")

        # Evaluation details
        report.append(f"## {t('evaluation_details', self.lang)}\n\n")
        for ev in evaluations:
            report.append(f"### {ev.persona.name}\n\n")
            report.append(f"**{t('overall_impression', self.lang)}:** {ev.overall_impression}\n\n")

            if ev.positive_points:
                report.append(f"**{t('positive_points', self.lang)}:**\n")
                for point in ev.positive_points:
                    report.append(f"- {point}\n")
                report.append("\n")

            if ev.issues:
                report.append(f"**{t('issues_found', self.lang)}:**\n\n")
                for issue in ev.issues:
                    severity_icon = {"minor": "🟡", "moderate": "🟠", "major": "🔴"}.get(issue.severity, "⚪")
                    report.append(f"{severity_icon} **{issue.issue_type}** ({issue.severity})\n")
                    report.append(f"- {issue.original_phrase}\n")
                    report.append(f"- {issue.explanation}\n")
                    report.append(f"- → {issue.suggested_rewrite}\n\n")
            else:
                report.append(f"**{t('issues_found', self.lang)}:** {t('no_issues', self.lang)}\n\n")

        # Scores summary
        report.append(f"## {t('scores_summary', self.lang)}\n\n")

        header = f"| {t('criteria', self.lang)} |"
        separator = "|------|"
        for i, ev in enumerate(evaluations, 1):
            header += f" P{i} |"
            separator += "----|"
        header += f" {t('avg', self.lang)} |"
        separator += "------|"
        report.append(header + "\n")
        report.append(separator + "\n")

        for criterion in ["naturalness", "fluency", "tone_appropriateness", "clarity"]:
            row = f"| {t(criterion, self.lang)} |"
            scores = []
            for ev in evaluations:
                score = ev.scores.get(criterion, 5)
                scores.append(score)
                row += f" {score} |"
            avg = sum(scores) / len(scores) if scores else 0
            row += f" {avg:.1f} |"
            report.append(row + "\n")
        report.append("\n")

        # Consolidated recommendations
        report.append(f"## {t('improvement_summary', self.lang)}\n\n")
        all_issues = []
        for ev in evaluations:
            for issue in ev.issues:
                if issue.suggested_rewrite not in [i["rewrite"] for i in all_issues]:
                    all_issues.append({
                        "original": issue.original_phrase,
                        "rewrite": issue.suggested_rewrite,
                        "severity": issue.severity
                    })

        if all_issues:
            # Sort by severity
            severity_order = {"major": 0, "moderate": 1, "minor": 2}
            all_issues.sort(key=lambda x: severity_order.get(x["severity"], 3))

            for i, issue in enumerate(all_issues[:5], 1):
                report.append(f"{i}. {issue['original']} → {issue['rewrite']}\n")
        else:
            report.append(f"{t('no_improvements_needed', self.lang)}\n")

        return "".join(report)


class TranslationEvaluationAgent:
    """Main agent orchestrating the translation evaluation pipeline."""

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "jp"):
        self.lang = lang
        self.persona_generator = TranslationPersonaGenerator(llm=llm, lang=lang)
        self.translation_evaluator = TranslationEvaluator(llm=llm, lang=lang)
        self.report_generator = TranslationReportGenerator(llm=llm, lang=lang)
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(TranslationEvaluationState)

        workflow.add_node("generate_personas", self._generate_personas)
        workflow.add_node("evaluate_translation", self._evaluate_translation)
        workflow.add_node("generate_report", self._generate_report)

        workflow.set_entry_point("generate_personas")
        workflow.add_edge("generate_personas", "evaluate_translation")
        workflow.add_edge("evaluate_translation", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    def _generate_personas(self, state: TranslationEvaluationState) -> dict[str, Any]:
        personas = self.persona_generator.run(state.source_text)
        return {"personas": personas.personas}

    def _evaluate_translation(self, state: TranslationEvaluationState) -> dict[str, Any]:
        result = self.translation_evaluator.run(
            state.source_text,
            state.translated_text,
            state.personas
        )
        return {"evaluations": result.evaluations}

    def _generate_report(self, state: TranslationEvaluationState) -> dict[str, Any]:
        report = self.report_generator.run(
            state.source_text,
            state.translated_text,
            state.evaluations
        )
        return {"summary_report": report}

    def run(self, source_text: str, translated_text: str) -> str:
        initial_state = TranslationEvaluationState(
            source_text=source_text,
            translated_text=translated_text,
            language=self.lang
        )
        final_state = self.graph.invoke(initial_state)
        return final_state["summary_report"]


def main():
    parser = argparse.ArgumentParser(description="Translation Evaluation AI Agent (EN→JP)")
    parser.add_argument("--source", type=str, help="Original English text")
    parser.add_argument("--source-file", type=str, help="Path to file containing English text")
    parser.add_argument("--translation", type=str, help="Japanese translation text")
    parser.add_argument("--translation-file", type=str, help="Path to file containing Japanese translation")
    parser.add_argument("--output-name", type=str, help="Custom output filename (without extension)")
    parser.add_argument("--model-name", type=str, default="gpt-5-mini", help="OpenAI model name")
    parser.add_argument("--lang", type=str, choices=["en", "jp"], default="jp", help="Output language: en or jp")
    args = parser.parse_args()

    # Get source text
    if args.source:
        source_text = args.source
    elif args.source_file:
        with open(args.source_file, 'r', encoding='utf-8') as f:
            source_text = f.read()
    else:
        parser.error("Either --source or --source-file is required")

    # Get translated text
    if args.translation:
        translated_text = args.translation
    elif args.translation_file:
        with open(args.translation_file, 'r', encoding='utf-8') as f:
            translated_text = f.read()
    else:
        parser.error("Either --translation or --translation-file is required")

    # Initialize LLM and agent
    # GPT-5-mini only supports temperature=1.0
    temperature = 1.0 if "gpt-5" in args.model_name.lower() else 0.3
    llm = ChatOpenAI(model_name=args.model_name, temperature=temperature)
    agent = TranslationEvaluationAgent(llm=llm, lang=args.lang)

    # Run evaluation
    report = agent.run(source_text=source_text, translated_text=translated_text)

    # Save output
    output_dir = "output/translation"
    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")
    if args.output_name:
        file_name = f"{date_str}-{args.output_name}.md"
    else:
        file_name = f"{date_str}-translation-eval.md"
    output_path = os.path.join(output_dir, file_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(t("report_saved_translation", args.lang).format(path=output_path))
    print("\n" + report)


if __name__ == "__main__":
    main()
