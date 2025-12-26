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

from shared import Persona

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
    suggestions: list[str] = Field(default_factory=list, description="Improvement suggestions")


class EvaluationResult(BaseModel):
    """Container for all evaluations."""
    evaluations: list[Evaluation] = Field(
        default_factory=list, description="List of persona evaluations"
    )


class ContentEvaluationState(BaseModel):
    """State for the content evaluation agent."""
    target_keyword: str = Field(..., description="Target keyword for SEO")
    content: str = Field(..., description="Product description to evaluate")
    personas: Annotated[list[SearchIntentPersona], operator.add] = Field(
        default_factory=list, description="Generated personas"
    )
    evaluations: Annotated[list[Evaluation], operator.add] = Field(
        default_factory=list, description="Evaluation results"
    )
    summary_report: str = Field(default="", description="Final summary report")


# Core Classes
class SearchIntentPersonaGenerator:
    """Generates personas based on search intent types."""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm.with_structured_output(SearchIntentPersonas)

    def run(self, target_keyword: str) -> SearchIntentPersonas:
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert in user behavior and search intent analysis. "
                "Generate 3 distinct personas representing different search intents for a product keyword."
            ),
            (
                "human",
                "Generate 3 personas for the keyword: {keyword}\n\n"
                "Create one persona for each search intent type:\n"
                "1. **Informational**: Someone researching to learn about the product category\n"
                "2. **Navigational/Comparative**: Someone comparing options before deciding\n"
                "3. **Transactional**: Someone ready to buy, looking for the right offer\n\n"
                "For each persona, include:\n"
                "- A realistic name\n"
                "- Their background and motivation\n"
                "- An example search query they would use\n"
                "- A list of 3 specific things they are looking for in the product description (looking_for)\n"
            ),
        ])
        chain = prompt | self.llm
        return chain.invoke({"keyword": target_keyword})


class ContentEvaluator:
    """Evaluates content from each persona's perspective."""

    SCORING_CRITERIA = ["relevance", "clarity", "completeness", "persuasiveness"]

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

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
            (
                "system",
                "You are {persona_name}, {persona_background}. "
                "Your search intent is {intent_type}. "
                "You searched for: \"{search_query}\"\n\n"
                "You are looking for the following information:\n{looking_for}\n\n"
                "After reading the product description, answer whether you found what you were looking for. "
                "Be conversational and specific about what you did or didn't find."
            ),
            (
                "human",
                "Product Description:\n{content}\n\n"
                "For each thing you were looking for, respond to the question 'Did you find the information you were looking for?'\n"
                "Answer naturally, like: 'Yes, I was looking for X and the description clearly explained...' or "
                "'No, I was hoping to find X but the description didn't mention...'\n\n"
                "Generate exactly 3 evaluation responses in this JSON format:\n"
                "[\n"
                '  {{"question": "Did you find the information about [specific thing]?", "answer": "[Your conversational response about what you found or didn\'t find]", "satisfied": true/false}},\n'
                '  {{"question": "Did you find the information about [specific thing]?", "answer": "[Your conversational response]", "satisfied": true/false}},\n'
                '  {{"question": "Did you find the information about [specific thing]?", "answer": "[Your conversational response]", "satisfied": true/false}}\n'
                "]"
            ),
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
            (
                "system",
                "You are evaluating content from the perspective of {persona_name} ({intent_type} intent). "
                "Based on the evaluation dialogue, score the content on these criteria (1-10):\n"
                "- relevance: How well does it match the search intent?\n"
                "- clarity: How easy is it to understand?\n"
                "- completeness: Does it answer key questions?\n"
                "- persuasiveness: Does it motivate action?"
            ),
            (
                "human",
                "Content:\n{content}\n\n"
                "Evaluation Dialogue:\n{dialogue}\n\n"
                "Respond with ONLY a JSON object like: "
                '{{"relevance": 8, "clarity": 7, "completeness": 6, "persuasiveness": 9}}'
            ),
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

    def _generate_suggestions(self, content: str, persona: SearchIntentPersona, dialogue: list[DialogueTurn]) -> list[str]:
        unsatisfied = [t for t in dialogue if not t.satisfied]
        if not unsatisfied:
            return ["Content meets this persona's needs well."]

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a content optimization expert. Based on the unsatisfied questions, "
                "provide 1-3 specific, actionable suggestions to improve the content."
            ),
            (
                "human",
                "Persona: {persona_name} ({intent_type} intent)\n"
                "Unsatisfied Questions:\n{questions}\n\n"
                "Provide suggestions as a simple list, one per line, no numbering."
            ),
        ])

        questions_str = "\n".join([f"- {t.question}" for t in unsatisfied])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "persona_name": persona.name,
            "intent_type": persona.intent_type,
            "questions": questions_str
        })

        return [s.strip() for s in result.strip().split("\n") if s.strip()]


class SummaryReportGenerator:
    """Generates the final summary report."""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def run(self, target_keyword: str, content: str, evaluations: list[Evaluation]) -> str:
        # Build report sections
        report = [f"# SEO Search Intent Evaluation Report\n\n"]

        # Research Outline section
        report.append("## Research Outline\n\n")
        report.append(f"**Target Keyword:** {target_keyword}\n\n")
        report.append("**Content Under Evaluation:**\n")
        report.append(f"> {content}\n\n")
        report.append(f"**Evaluation Method:** Search Intent Persona Analysis\n\n")
        report.append(f"**Number of Personas:** {len(evaluations)}\n\n")

        # Calculate overall scores for outline
        all_scores = {"relevance": [], "clarity": [], "completeness": [], "persuasiveness": []}
        for eval in evaluations:
            for criterion in all_scores:
                if criterion in eval.scores:
                    all_scores[criterion].append(eval.scores[criterion])

        avg_scores = {k: sum(v)/len(v) if v else 0 for k, v in all_scores.items()}
        overall_avg = sum(avg_scores.values()) / len(avg_scores) if avg_scores else 0

        report.append(f"**Overall Score:** {overall_avg:.1f}/10\n\n")
        report.append("---\n\n")

        # Personas section
        report.append("## Personas Generated\n\n")
        for i, eval in enumerate(evaluations, 1):
            p = eval.persona
            report.append(f"**Persona {i}: {p.name}** ({p.intent_type.title()} Intent)\n")
            report.append(f"- Background: {p.background}\n")
            report.append(f"- Search Query: \"{p.search_query}\"\n")
            report.append(f"- Looking for:\n")
            if p.looking_for:
                for item in p.looking_for:
                    report.append(f"  - {item}\n")
            report.append("\n")

        # Evaluation dialogues
        report.append("## Evaluation Dialogues\n")
        for eval in evaluations:
            report.append(f"### {eval.persona.name} ({eval.persona.intent_type.title()} Intent)\n")
            for turn in eval.dialogue:
                status = "satisfied" if turn.satisfied else "NOT satisfied"
                report.append(f"**Q:** {turn.question}\n")
                report.append(f"**A:** {turn.answer} ({status})\n\n")

        # Scores summary table
        report.append("## Scores Summary\n")
        criteria = ["relevance", "clarity", "completeness", "persuasiveness"]

        # Header
        header = "| Criteria |"
        separator = "|----------|"
        for i, eval in enumerate(evaluations, 1):
            header += f" P{i} |"
            separator += "----|"
        header += " Avg |"
        separator += "-----|"
        report.append(header + "\n")
        report.append(separator + "\n")

        # Rows
        for criterion in criteria:
            row = f"| {criterion.title()} |"
            scores = []
            for eval in evaluations:
                score = eval.scores.get(criterion, 5)
                scores.append(score)
                row += f" {score} |"
            avg = sum(scores) / len(scores) if scores else 0
            row += f" {avg:.1f} |"
            report.append(row + "\n")
        report.append("\n")

        # Recommendations
        report.append("## Recommendations\n")
        all_suggestions = []
        for eval in evaluations:
            for suggestion in eval.suggestions:
                if suggestion not in all_suggestions and "meets" not in suggestion.lower():
                    all_suggestions.append(suggestion)

        if all_suggestions:
            for i, suggestion in enumerate(all_suggestions[:5], 1):
                report.append(f"{i}. {suggestion}\n")
        else:
            report.append("No major improvements needed. Content performs well across all personas.\n")

        return "".join(report)


class ContentEvaluationAgent:
    """Main agent orchestrating the content evaluation pipeline."""

    def __init__(self, llm: ChatOpenAI):
        self.persona_generator = SearchIntentPersonaGenerator(llm=llm)
        self.content_evaluator = ContentEvaluator(llm=llm)
        self.summary_generator = SummaryReportGenerator(llm=llm)
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
            content=content
        )
        final_state = self.graph.invoke(initial_state)
        return final_state["summary_report"]


def main():
    parser = argparse.ArgumentParser(description="SEO Search Intent Evaluation AI Agent")
    parser.add_argument("--keyword", type=str, required=True, help="Target keyword for SEO")
    parser.add_argument("--content", type=str, help="Product description text")
    parser.add_argument("--content-file", type=str, help="Path to file containing product description")
    parser.add_argument("--model-name", type=str, default="gpt-4.1-mini-2025-04-14", help="OpenAI model name")
    args = parser.parse_args()

    # Get content from argument or file
    if args.content:
        content = args.content
    elif args.content_file:
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        parser.error("Either --content or --content-file is required")

    # Initialize LLM and agent
    llm = ChatOpenAI(model_name=args.model_name, temperature=0.3)
    agent = ContentEvaluationAgent(llm=llm)

    # Run evaluation
    report = agent.run(target_keyword=args.keyword, content=content)

    # Save output
    output_dir = "output/seo-evaluation"
    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")
    keyword_str = args.keyword.lower().replace(' ', '-')
    file_name = f"{date_str}-eval-{keyword_str}.md"
    output_path = os.path.join(output_dir, file_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Evaluation report saved to '{output_path}'")
    print("\n" + report)


if __name__ == "__main__":
    main()
