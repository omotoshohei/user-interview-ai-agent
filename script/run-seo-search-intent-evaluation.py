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
    # Load .env from project root (parent of script directory)
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    import warnings
    warnings.warn("dotenv not found. Please set environment variables manually.", ImportWarning)
################################################


# Data Models
class SearchIntentPersona(Persona):
    """Persona based on search intent type."""
    intent_type: str = Field(..., description="Type of search intent: informational, navigational, or transactional")
    search_query: str = Field(..., description="Example search query this persona would use")
    looking_for: list[str] = Field(default_factory=list, description="What information this persona is looking for")


class SearchIntentPersonas(BaseModel):
    """List of search intent personas."""
    personas: list[SearchIntentPersona] = Field(
        default_factory=list, description="List of search intent personas"
    )


class DialogueTurn(BaseModel):
    """A single turn in the evaluation dialogue."""
    question: str = Field(..., description="Question asked by the persona")
    answer: str = Field(..., description="How well the content answers this question")
    satisfied: bool = Field(..., description="Whether the persona is satisfied with the answer")


class Evaluation(BaseModel):
    """Evaluation result from a single persona."""
    persona: SearchIntentPersona = Field(..., description="The persona who evaluated")
    dialogue: list[DialogueTurn] = Field(default_factory=list, description="Evaluation dialogue")
    scores: dict[str, int] = Field(default_factory=dict, description="Scores by criteria")
    suggestions: list[str] | dict[str, list[str]] = Field(default_factory=list, description="Improvement suggestions")


class EvaluationResult(BaseModel):
    """Container for all evaluations."""
    evaluations: list[Evaluation] = Field(
        default_factory=list, description="List of persona evaluations"
    )


class ContentEvaluationState(BaseModel):
    """State for the content evaluation agent."""
    target_keyword: str = Field(..., description="Target keyword for SEO")
    content: str = Field(..., description="Product description to evaluate")
    language: LanguageCode = Field(default="en", description="Output language")
    personas: Annotated[list[SearchIntentPersona], operator.add] = Field(
        default_factory=list, description="Generated personas"
    )
    evaluations: Annotated[list[Evaluation], operator.add] = Field(
        default_factory=list, description="Evaluation results"
    )
    summary_report: str = Field(default="", description="Final summary report")


# Core Classes
class SearchIntentPersonaGenerator:
    """Generates fixed personas for SEO content evaluation."""

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "en", intents: list[str] = None):
        self.llm = llm  # Keep for potential future use
        self.lang = lang
        self.intent = intents[0] if intents else "informational"  # Use first intent from CLI

    def run(self, target_keyword: str) -> SearchIntentPersonas:
        """Return fixed 3 personas for SEO evaluation."""
        personas = [
            SearchIntentPersona(
                name="Alex Chen" if self.lang == "en" else "田中 誠",
                background="Marketing Specialist at a company with about 3 years of digital marketing experience. Familiar with digital advertising but lacks deep SEO knowledge and struggles with technical aspects like coding or server configurations." if self.lang == "en" else "事業会社のマーケティング担当者。デジタルマーケティング歴は3年程度。広告運用などの知識はあるがSEOには詳しくなく、特に技術的な内容（テクニカルSEO）には苦手意識を持っている。",
                intent_type=self.intent,
                search_query=f"{target_keyword} basics for marketers" if self.lang == "en" else f"{target_keyword} わかりやすく マーケティング",
                looking_for=[
                    "Simple explanations without technical jargon" if self.lang == "en" else "専門用語を使わないわかりやすい説明",
                    "Impact on marketing performance" if self.lang == "en" else "マーケティング成果への影響",
                    "Actionable items for non-engineers" if self.lang == "en" else "エンジニアでなくても実践できること",
                    "Checklist for basic improvements" if self.lang == "en" else "基本的な改善チェックリスト",
                ]
            ),
            SearchIntentPersona(
                name="Sarah Miller" if self.lang == "en" else "鈴木 花子",
                background="Small business owner running an e-commerce store for 3 years. Self-taught in digital marketing with limited budget for SEO tools. Looking for practical, cost-effective solutions to improve online visibility." if self.lang == "en" else "Eコマースストアを3年間経営する中小企業オーナー。デジタルマーケティングは独学で習得し、SEOツールへの予算は限られている。オンラインでの認知度向上のため、実用的でコスト効率の良いソリューションを探している。",
                intent_type=self.intent,
                search_query=f"{target_keyword} for small business" if self.lang == "en" else f"{target_keyword} 中小企業向け",
                looking_for=[
                    "Pricing and affordability" if self.lang == "en" else "価格と手頃さ",
                    "Ease of use without technical expertise" if self.lang == "en" else "専門知識なしでの使いやすさ",
                    "Quick wins and actionable tips" if self.lang == "en" else "すぐに実践できるアドバイス",
                    "Time investment required" if self.lang == "en" else "必要な時間投資",
                ]
            ),
            SearchIntentPersona(
                name="Jordan Lee" if self.lang == "en" else "山田 翔太",
                background="University student who recently started learning SEO and digital marketing. Taking an online course and trying to understand fundamental concepts. No practical experience yet but eager to learn." if self.lang == "en" else "最近SEOとデジタルマーケティングの学習を始めた大学生。オンラインコースを受講中で、基本的な概念を理解しようとしている。実務経験はまだないが、学習意欲は高い。",
                intent_type=self.intent,
                search_query=f"what is {target_keyword}" if self.lang == "en" else f"{target_keyword} とは",
                looking_for=[
                    "Clear explanations of basic concepts" if self.lang == "en" else "基本概念のわかりやすい説明",
                    "Beginner-friendly terminology" if self.lang == "en" else "初心者向けの用語説明",
                    "Step-by-step learning resources" if self.lang == "en" else "ステップバイステップの学習リソース",
                    "Real-world examples for better understanding" if self.lang == "en" else "理解を深めるための実例",
                ]
            ),
        ]
        return SearchIntentPersonas(personas=personas)


class ContentEvaluator:
    """Evaluates content from each persona's perspective."""

    SCORING_CRITERIA = ["relevance", "clarity", "completeness", "persuasiveness"]

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "en"):
        self.llm = llm
        self.lang = lang

    def run(self, content: str, personas: list[SearchIntentPersona]) -> EvaluationResult:
        evaluations = []
        for persona in personas:
            evaluation = self._evaluate_for_persona(content, persona)
            evaluations.append(evaluation)
        return EvaluationResult(evaluations=evaluations)

    def _evaluate_for_persona(self, content: str, persona: SearchIntentPersona) -> Evaluation:
        # Generate evaluation dialogue
        dialogue = self._generate_dialogue(content, persona)
        # Generate scores
        scores = self._generate_scores(content, persona, dialogue)
        # Generate suggestions
        suggestions = self._generate_suggestions(content, persona, dialogue)

        return Evaluation(
            persona=persona,
            dialogue=dialogue,
            scores=scores,
            suggestions=suggestions
        )

    def _generate_dialogue(self, content: str, persona: SearchIntentPersona) -> list[DialogueTurn]:
        looking_for_str = "\n".join([f"- {item}" for item in persona.looking_for]) if persona.looking_for else "- General product information"

        prompt = ChatPromptTemplate.from_messages([
            ("system", p("seo_evaluation", "dialogue_system", self.lang)),
            ("human", p("seo_evaluation", "dialogue_human", self.lang)),
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "persona_name": persona.name,
            "persona_background": persona.background,
            "intent_type": persona.intent_type,
            "search_query": persona.search_query,
            "looking_for": looking_for_str,
            "content": content
        })

        # Parse JSON response
        import json
        try:
            # Clean up the response - extract JSON array
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            dialogue_data = json.loads(result)
            return [DialogueTurn(**turn) for turn in dialogue_data]
        except (json.JSONDecodeError, KeyError):
            # Fallback if parsing fails
            return [DialogueTurn(
                question="Could not parse evaluation",
                answer="Please check the content manually",
                satisfied=False
            )]

    def _generate_scores(self, content: str, persona: SearchIntentPersona, dialogue: list[DialogueTurn]) -> dict[str, int]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", p("seo_evaluation", "scores_system", self.lang)),
            ("human", p("seo_evaluation", "scores_human", self.lang)),
        ])

        dialogue_str = "\n".join([
            f"Q: {t.question}\nA: {t.answer} (Satisfied: {t.satisfied})"
            for t in dialogue
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "persona_name": persona.name,
            "intent_type": persona.intent_type,
            "content": content,
            "dialogue": dialogue_str
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

    def _generate_suggestions(self, content: str, persona: SearchIntentPersona, dialogue: list[DialogueTurn]) -> dict[str, list[str]]:
        unsatisfied = [d for d in dialogue if not d.satisfied]
        if not unsatisfied:
            return {"add_topics": [], "rewrite_suggestions": []}

        prompt = ChatPromptTemplate.from_messages([
            ("system", p("seo_evaluation", "suggestions_system", self.lang)),
            ("human", p("seo_evaluation", "suggestions_human", self.lang)),
        ])

        # Include both Question and Answer (Reasoning)
        questions_str = "\n".join([
            f"- Q: {t.question}\n  A: {t.answer}" 
            for t in unsatisfied
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "persona_name": persona.name,
            "intent_type": persona.intent_type,
            "questions": questions_str
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
            # Fallback
            return {
                "add_topics": ["Failed to parse specific suggestions."],
                "rewrite_suggestions": []
            }


class SummaryReportGenerator:
    """Generates the final summary report."""

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "en"):
        self.llm = llm
        self.lang = lang

    def run(self, target_keyword: str, content: str, evaluations: list[Evaluation]) -> str:
        # Build report sections
        report = [f"# {t('seo_eval_title', self.lang)}\n\n"]

        # Research Outline section
        report.append(f"## {t('research_outline', self.lang)}\n\n")
        report.append(f"**{t('target_keyword', self.lang)}:** {target_keyword}\n\n")
        report.append(f"**{t('content_under_evaluation', self.lang)}:**\n")
        report.append(f"> {content[:200]}...\n\n")
        report.append(f"**{t('method', self.lang)}:** {t('evaluation_method_seo', self.lang)}\n\n")
        report.append(f"**{t('number_of_personas', self.lang)}:** {len(evaluations)}\n\n")

        # Calculate overall scores for outline
        all_scores = {"relevance": [], "clarity": [], "completeness": [], "persuasiveness": []}
        for ev in evaluations:
            for criterion in all_scores:
                if criterion in ev.scores:
                    all_scores[criterion].append(ev.scores[criterion])

        avg_scores = {k: sum(v)/len(v) if v else 0 for k, v in all_scores.items()}
        overall_avg = sum(avg_scores.values()) / len(avg_scores) if avg_scores else 0

        report.append(f"**{t('overall_score', self.lang)}:** {overall_avg:.1f}/10\n\n")
        report.append("---\n\n")

        # Personas section
        report.append(f"## {t('personas_generated', self.lang)}\n\n")
        for i, ev in enumerate(evaluations, 1):
            persona = ev.persona
            report.append(f"**{t('persona', self.lang)} {i}: {persona.name}** ({persona.intent_type.title()} Intent)\n")
            report.append(f"- {t('background', self.lang)}: {persona.background}\n")
            report.append(f"- {t('search_query', self.lang)}: \"{persona.search_query}\"\n")
            report.append(f"- {t('looking_for', self.lang)}:\n")
            if persona.looking_for:
                for item in persona.looking_for:
                    report.append(f"  - {item}\n")
            report.append("\n")

        # Evaluation dialogues
        report.append(f"## {t('evaluation_dialogues', self.lang)}\n")
        for ev in evaluations:
            report.append(f"### {ev.persona.name} ({ev.persona.intent_type.title()} Intent)\n")
            for turn in ev.dialogue:
                status = t('satisfied', self.lang) if turn.satisfied else t('not_satisfied', self.lang)
                report.append(f"**Q:** {turn.question}\n")
                report.append(f"**A:** {turn.answer} ({status})\n\n")

        # Scores summary table
        report.append(f"## {t('scores_summary', self.lang)}\n")
        criteria = ["relevance", "clarity", "completeness", "persuasiveness"]

        # Header
        header = f"| {t('criteria', self.lang)} |"
        separator = "|----------|"
        for i, ev in enumerate(evaluations, 1):
            header += f" P{i} |"
            separator += "----|"
        header += f" {t('avg', self.lang)} |"
        separator += "-----|"
        report.append(header + "\n")
        report.append(separator + "\n")

        # Rows
        for criterion in criteria:
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

        # Recommendations
        report.append(f"## {t('recommendations', self.lang)}\n")
        
        all_add_topics = []
        all_rewrite_suggestions = []

        for ev in evaluations:
            if isinstance(ev.suggestions, dict):
                # New format
                if "add_topics" in ev.suggestions:
                    all_add_topics.extend(ev.suggestions["add_topics"])
                if "rewrite_suggestions" in ev.suggestions:
                    all_rewrite_suggestions.extend(ev.suggestions["rewrite_suggestions"])
            elif isinstance(ev.suggestions, list):
                # Old format fallback
                all_rewrite_suggestions.extend(ev.suggestions)

        # De-duplicate while keeping order
        def dedup(items):
            seen = set()
            result = []
            for item in items:
                if item not in seen:
                    result.append(item)
                    seen.add(item)
            return result

        unique_add_topics = dedup(all_add_topics)
        unique_rewrite_suggestions = dedup(all_rewrite_suggestions)

        if self.lang == "jp":
            report.append(f"### 追加すべきトピック\n")
        else:
            report.append(f"### Additional Topics\n")
        
        if unique_add_topics:
            for i, topic in enumerate(unique_add_topics, 1):
                report.append(f"{i}. {topic}\n")
        else:
            report.append("None.\n")
        report.append("\n")

        if self.lang == "jp":
            report.append(f"### リライトすべき箇所\n")
        else:
            report.append(f"### Rewrite Suggestions\n")

        if unique_rewrite_suggestions:
            for i, suggestion in enumerate(unique_rewrite_suggestions, 1):
                report.append(f"{i}. {suggestion}\n")
        else:
            report.append("None.\n")

        return "".join(report)


class ContentEvaluationAgent:
    """Main agent orchestrating the content evaluation pipeline."""

    def __init__(self, llm: ChatOpenAI, lang: LanguageCode = "en", intents: list[str] = None):
        self.lang = lang
        self.persona_generator = SearchIntentPersonaGenerator(llm=llm, lang=lang, intents=intents)
        self.content_evaluator = ContentEvaluator(llm=llm, lang=lang)
        self.summary_generator = SummaryReportGenerator(llm=llm, lang=lang)
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(ContentEvaluationState)

        workflow.add_node("generate_personas", self._generate_personas)
        workflow.add_node("conduct_evaluations", self._conduct_evaluations)
        workflow.add_node("generate_summary", self._generate_summary)

        workflow.set_entry_point("generate_personas")
        workflow.add_edge("generate_personas", "conduct_evaluations")
        workflow.add_edge("conduct_evaluations", "generate_summary")
        workflow.add_edge("generate_summary", END)

        return workflow.compile()

    def _generate_personas(self, state: ContentEvaluationState) -> dict[str, Any]:
        personas = self.persona_generator.run(state.target_keyword)
        return {"personas": personas.personas}

    def _conduct_evaluations(self, state: ContentEvaluationState) -> dict[str, Any]:
        result = self.content_evaluator.run(state.content, state.personas)
        return {"evaluations": result.evaluations}

    def _generate_summary(self, state: ContentEvaluationState) -> dict[str, Any]:
        report = self.summary_generator.run(
            state.target_keyword,
            state.content,
            state.evaluations
        )
        return {"summary_report": report}

    def run(self, target_keyword: str, content: str) -> str:
        initial_state = ContentEvaluationState(
            target_keyword=target_keyword,
            content=content,
            language=self.lang
        )
        final_state = self.graph.invoke(initial_state)
        return final_state["summary_report"]


def main():
    parser = argparse.ArgumentParser(description="SEO Search Intent Evaluation AI Agent")
    parser.add_argument("--keyword", type=str, help="Target keyword for SEO (will prompt if not provided)")
    parser.add_argument("--content", type=str, help="Product description text")
    parser.add_argument("--content-file", type=str, help="Path to file containing product description")
    parser.add_argument("--model-name", type=str, default="gpt-5-mini", help="OpenAI model name")
    parser.add_argument("--lang", type=str, choices=["en", "jp"], default="en", help="Output language: en or jp")
    parser.add_argument("--intent", type=str, nargs="+", 
                        choices=["informational", "navigational", "transactional"],
                        default=["informational"],
                        help="Search intent type(s) to evaluate. Default: informational only (for blog articles)")
    parser.add_argument("--output-dir", type=str, help="Directory to save the output report")
    args = parser.parse_args()

    # Get content from argument or file
    if args.content:
        content = args.content
    elif args.content_file:
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        parser.error("Either --content or --content-file is required")

    # Get keyword from argument or prompt
    if args.keyword:
        keyword = args.keyword
    else:
        prompt_msg = "ターゲットキーワードを入力してください: " if args.lang == "jp" else "Enter the target keyword: "
        keyword = input(prompt_msg).strip()
        if not keyword:
            parser.error("Target keyword is required")

    # Initialize LLM and agent
    # GPT-5-mini only supports temperature=1.0
    temperature = 1.0 if "gpt-5" in args.model_name.lower() else 0.3
    llm = ChatOpenAI(model_name=args.model_name, temperature=temperature)
    agent = ContentEvaluationAgent(llm=llm, lang=args.lang, intents=args.intent)

    # Run evaluation
    report = agent.run(target_keyword=keyword, content=content)

    # Save output
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = "output/seo-evaluation"
    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")
    keyword_str = keyword.lower().replace(' ', '-')
    file_name = f"{date_str}-eval-{keyword_str}.md"
    output_path = os.path.join(output_dir, file_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(t("report_saved_seo", args.lang).format(path=output_path))
    print("\n" + report)


if __name__ == "__main__":
    main()
