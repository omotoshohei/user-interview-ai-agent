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
class SentencePersona(Persona):
    """Dynamically generated persona based on background context."""
    perspective: str = Field(..., description="The persona's perspective, e.g., 'target customer', 'skeptical reader'")
    evaluation_focus: str = Field(..., description="What this persona focuses on, e.g., 'clarity', 'persuasiveness'")
    relevance: str = Field(..., description="Why this persona matters for the evaluation")


class SentencePersonas(BaseModel):
    """List of dynamically generated personas."""
    personas: list[SentencePersona] = Field(
        default_factory=list, description="List of sentence evaluation personas"
    )


class SentenceFeedback(BaseModel):
    """Feedback from a single persona."""
    persona: SentencePersona = Field(..., description="The persona providing feedback")
    overall_impression: str = Field(..., description="Overall impression of the sentence")
    strengths: list[str] = Field(default_factory=list, description="What works well")
    weaknesses: list[str] = Field(default_factory=list, description="What could be improved")
    scores: dict[str, int] = Field(default_factory=dict, description="Scores by criteria")


class SentenceFeedbackResult(BaseModel):
    """Container for all feedback."""
    feedback: list[SentenceFeedback] = Field(
        default_factory=list, description="List of persona feedback"
    )


class SentenceEvaluationState(BaseModel):
    """State for the sentence evaluation agent."""
    background: str = Field(..., description="Background context for the sentence")
    sentence: str = Field(..., description="The sentence to evaluate")
    language: LanguageCode = Field(default="en", description="Output language")
    personas: Annotated[list[SentencePersona], operator.add] = Field(
        default_factory=list, description="Generated personas"
    )
    feedback: Annotated[list[SentenceFeedback], operator.add] = Field(
        default_factory=list, description="Feedback results"
    )
    summary_report: str = Field(default="", description="Final summary report")


# Core Classes
class DynamicPersonaGenerator:
    """Generates personas dynamically based on the background context."""

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "en"):
        self.llm = llm.with_structured_output(SentencePersonas)
        self.lang = lang

    def run(self, background: str) -> SentencePersonas:
        prompt = ChatPromptTemplate.from_messages([
            ("system", p("sentence_evaluation", "persona_generator_system", self.lang)),
            ("human", p("sentence_evaluation", "persona_generator_human", self.lang)),
        ])
        chain = prompt | self.llm
        return chain.invoke({"background": background})


class SentenceEvaluator:
    """Evaluates sentences from each persona's perspective."""

    SCORING_CRITERIA = ["clarity", "impact", "tone", "persuasiveness"]

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "en"):
        self.llm = llm
        self.lang = lang

    def run(self, background: str, sentence: str, personas: list[SentencePersona]) -> SentenceFeedbackResult:
        feedback_list = []
        for persona in personas:
            feedback = self._evaluate_for_persona(background, sentence, persona)
            feedback_list.append(feedback)
        return SentenceFeedbackResult(feedback=feedback_list)

    def _evaluate_for_persona(self, background: str, sentence: str, persona: SentencePersona) -> SentenceFeedback:
        # Get evaluation
        eval_data = self._get_evaluation(background, sentence, persona)
        # Generate scores
        scores = self._generate_scores(background, sentence, persona, eval_data)

        return SentenceFeedback(
            persona=persona,
            overall_impression=eval_data.get("impression", ""),
            strengths=eval_data.get("strengths", []),
            weaknesses=eval_data.get("weaknesses", []),
            scores=scores
        )

    def _get_evaluation(self, background: str, sentence: str, persona: SentencePersona) -> dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", p("sentence_evaluation", "evaluation_system", self.lang)),
            ("human", p("sentence_evaluation", "evaluation_human", self.lang)),
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "persona_name": persona.name,
            "persona_background": persona.background,
            "perspective": persona.perspective,
            "evaluation_focus": persona.evaluation_focus,
            "background": background,
            "sentence": sentence
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
            return {"impression": "Could not parse evaluation", "strengths": [], "weaknesses": []}

    def _generate_scores(self, background: str, sentence: str, persona: SentencePersona, eval_data: dict) -> dict[str, int]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", p("sentence_evaluation", "scores_system", self.lang)),
            ("human", p("sentence_evaluation", "scores_human", self.lang)),
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "persona_name": persona.name,
            "background": background,
            "sentence": sentence,
            "strengths": ", ".join(eval_data.get("strengths", [])),
            "weaknesses": ", ".join(eval_data.get("weaknesses", []))
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



class SentenceReportGenerator:
    """Generates the final summary report."""

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "en"):
        self.llm = llm
        self.lang = lang

    def run(self, background: str, sentence: str, feedback: list[SentenceFeedback]) -> str:
        report = [f"# {t('sentence_eval_title', self.lang)}\n\n"]

        # Evaluation Context
        report.append(f"## {t('evaluation_context', self.lang)}\n\n")
        report.append(f"**{t('background', self.lang)}:** {background}\n\n")
        report.append(f"**{t('sentence', self.lang)}:** \"{sentence}\"\n\n")

        # Calculate overall score
        all_scores = {"clarity": [], "impact": [], "tone": [], "persuasiveness": []}
        for fb in feedback:
            for criterion in all_scores:
                if criterion in fb.scores:
                    all_scores[criterion].append(fb.scores[criterion])

        avg_scores = {k: sum(v)/len(v) if v else 0 for k, v in all_scores.items()}
        overall_avg = sum(avg_scores.values()) / len(avg_scores) if avg_scores else 0

        report.append(f"**{t('overall_score', self.lang)}:** {overall_avg:.1f}/10\n\n")
        report.append("---\n\n")

        # Generated Personas
        report.append(f"## {t('generated_personas', self.lang)}\n\n")
        for i, fb in enumerate(feedback, 1):
            persona = fb.persona
            report.append(f"**{t('persona', self.lang)} {i}: {persona.name}** ({persona.perspective})\n")
            report.append(f"- {t('focus', self.lang)}: {persona.evaluation_focus}\n")
            report.append(f"- {t('relevance_reason', self.lang)}: {persona.relevance}\n\n")

        # Evaluation Details
        report.append(f"## {t('evaluation_details', self.lang)}\n\n")
        for fb in feedback:
            report.append(f"### {fb.persona.name}\n\n")
            report.append(f"**{t('overall_impression', self.lang)}:** {fb.overall_impression}\n\n")

            if fb.strengths:
                report.append(f"**{t('strengths', self.lang)}:**\n")
                for strength in fb.strengths:
                    report.append(f"- {strength}\n")
                report.append("\n")

            if fb.weaknesses:
                report.append(f"**{t('weaknesses', self.lang)}:**\n")
                for weakness in fb.weaknesses:
                    report.append(f"- {weakness}\n")
                report.append("\n")

        # Scores Summary
        report.append(f"## {t('scores_summary', self.lang)}\n\n")
        criteria = ["clarity", "impact", "tone", "persuasiveness"]

        header = f"| {t('criteria', self.lang)} |"
        separator = "|----------|"
        for i in range(len(feedback)):
            header += f" P{i+1} |"
            separator += "----|"
        header += f" {t('avg', self.lang)} |"
        separator += "-----|"
        report.append(header + "\n")
        report.append(separator + "\n")

        for criterion in criteria:
            row = f"| {t(criterion, self.lang)} |"
            scores = []
            for fb in feedback:
                score = fb.scores.get(criterion, 5)
                scores.append(score)
                row += f" {score} |"
            avg = sum(scores) / len(scores) if scores else 0
            row += f" {avg:.1f} |"
            report.append(row + "\n")
        report.append("\n")

        # Recommendations
        report.append(f"## {t('recommendations', self.lang)}\n\n")
        recommendations = self._generate_recommendations(background, sentence, feedback)
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}\n")

        return "".join(report)

    def _generate_recommendations(self, background: str, sentence: str, feedback: list[SentenceFeedback]) -> list[str]:
        """Generate consolidated recommendations based on all persona feedback."""
        # Collect all weaknesses
        all_weaknesses = []
        for fb in feedback:
            all_weaknesses.extend(fb.weaknesses)

        if not all_weaknesses:
            return [t("no_recommendations", self.lang)]

        prompt = ChatPromptTemplate.from_messages([
            ("system", p("sentence_evaluation", "recommendations_system", self.lang)),
            ("human", p("sentence_evaluation", "recommendations_human", self.lang)),
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "background": background,
            "sentence": sentence,
            "weaknesses": "\n".join(f"- {w}" for w in all_weaknesses)
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
            return ["Review and address the identified weaknesses to improve clarity and impact."]


class SentenceEvaluationAgent:
    """Main agent orchestrating the sentence evaluation pipeline."""

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "en"):
        self.lang = lang
        self.persona_generator = DynamicPersonaGenerator(llm=llm, lang=lang)
        self.sentence_evaluator = SentenceEvaluator(llm=llm, lang=lang)
        self.report_generator = SentenceReportGenerator(llm=llm, lang=lang)
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(SentenceEvaluationState)

        workflow.add_node("generate_personas", self._generate_personas)
        workflow.add_node("evaluate_sentence", self._evaluate_sentence)
        workflow.add_node("generate_report", self._generate_report)

        workflow.set_entry_point("generate_personas")
        workflow.add_edge("generate_personas", "evaluate_sentence")
        workflow.add_edge("evaluate_sentence", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    def _generate_personas(self, state: SentenceEvaluationState) -> dict[str, Any]:
        personas = self.persona_generator.run(state.background)
        return {"personas": personas.personas}

    def _evaluate_sentence(self, state: SentenceEvaluationState) -> dict[str, Any]:
        result = self.sentence_evaluator.run(
            state.background,
            state.sentence,
            state.personas
        )
        return {"feedback": result.feedback}

    def _generate_report(self, state: SentenceEvaluationState) -> dict[str, Any]:
        report = self.report_generator.run(
            state.background,
            state.sentence,
            state.feedback
        )
        return {"summary_report": report}

    def run(self, background: str, sentence: str) -> str:
        initial_state = SentenceEvaluationState(
            background=background,
            sentence=sentence,
            language=self.lang
        )
        final_state = self.graph.invoke(initial_state)
        return final_state["summary_report"]


def main():
    parser = argparse.ArgumentParser(description="Sentence Evaluation AI Agent")
    parser.add_argument("--background", type=str, help="Background context for the sentence")
    parser.add_argument("--background-file", type=str, help="Path to file containing background context")
    parser.add_argument("--sentence", type=str, required=True, help="The sentence to evaluate")
    parser.add_argument("--output-name", type=str, help="Custom output filename (without extension)")
    parser.add_argument("--model-name", type=str, default="gpt-5-mini", help="OpenAI model name")
    parser.add_argument("--lang", type=str, choices=["en", "jp"], default="en", help="Output language: en or jp")
    args = parser.parse_args()

    # Get background
    if args.background:
        background = args.background
    elif args.background_file:
        with open(args.background_file, 'r', encoding='utf-8') as f:
            background = f.read()
    else:
        parser.error("Either --background or --background-file is required")

    # Initialize LLM and agent
    # GPT-5-mini only supports temperature=1.0
    temperature = 1.0 if "gpt-5" in args.model_name.lower() else 0.3
    llm = ChatOpenAI(model_name=args.model_name, temperature=temperature)
    agent = SentenceEvaluationAgent(llm=llm, lang=args.lang)

    # Run evaluation
    report = agent.run(background=background, sentence=args.sentence)

    # Save output
    output_dir = "output/sentence-evaluation"
    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")
    if args.output_name:
        file_name = f"{date_str}-{args.output_name}.md"
    else:
        file_name = f"{date_str}-sentence-eval.md"
    output_path = os.path.join(output_dir, file_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(t("report_saved_sentence", args.lang).format(path=output_path))
    print("\n" + report)


if __name__ == "__main__":
    main()
