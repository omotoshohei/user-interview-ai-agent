"""
Model Comparison Script for SEO Evaluation

Compares output quality and cost across multiple LLM models:
- gpt-4.1-mini (OpenAI)
- gemini-3.0-flash (Google)
- GPT-5 mini (OpenAI)
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Any

# Add script directory to path for shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "script"))

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

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.callbacks import get_openai_callback

# Import SEO Evaluation components
from shared import LanguageCode, t, p
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import operator
from typing import Annotated
from langgraph.graph import END, StateGraph


# ============================================================================
# MODEL CONFIGURATIONS
# ============================================================================

MODEL_CONFIGS = {
    "gpt-4.1-mini": {
        "provider": "openai",
        "model_name": "gpt-4.1-mini-2025-04-14",
        "input_cost_per_million": 0.40,
        "output_cost_per_million": 1.60,
        "temperature": 0.3,
    },
    "gemini-3-flash": {
        "provider": "google",
        "model_name": "gemini-3-flash-preview",
        "input_cost_per_million": 0.50,
        "output_cost_per_million": 3.00,
        "temperature": 0.3,
    },
    "GPT-5-mini": {
        "provider": "openai",
        "model_name": "gpt-5-mini",
        "input_cost_per_million": 0.25,
        "output_cost_per_million": 2.00,
        "temperature": 1.0,  # GPT-5 mini only supports temperature=1.0
    },
}


# ============================================================================
# DATA MODELS (from SEO evaluation)
# ============================================================================

class Persona(BaseModel):
    """Base persona model."""
    name: str = Field(..., description="Persona name")
    background: str = Field(..., description="Persona background")


class SearchIntentPersona(Persona):
    """Persona based on search intent type."""
    intent_type: str = Field(..., description="Type of search intent: informational, navigational, or transactional")
    search_query: str = Field(..., description="Example search query this persona would use")
    looking_for: list[str] = Field(default_factory=list, description="What information this persona is looking for")


class SearchIntentPersonas(BaseModel):
    """List of search intent personas."""
    personas: list[SearchIntentPersona] = Field(default_factory=list, description="List of search intent personas")


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
    evaluations: list[Evaluation] = Field(default_factory=list, description="List of persona evaluations")


class ContentEvaluationState(BaseModel):
    """State for the content evaluation agent."""
    target_keyword: str = Field(..., description="Target keyword for SEO")
    content: str = Field(..., description="Product description to evaluate")
    language: LanguageCode = Field(default="en", description="Output language")
    personas: Annotated[list[SearchIntentPersona], operator.add] = Field(default_factory=list, description="Generated personas")
    evaluations: Annotated[list[Evaluation], operator.add] = Field(default_factory=list, description="Evaluation results")
    summary_report: str = Field(default="", description="Final summary report")


# ============================================================================
# USAGE TRACKER WITH TIKTOKEN ESTIMATION
# ============================================================================

import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using tiktoken. Falls back to character-based estimation for non-OpenAI models."""
    try:
        # Try to get encoding for the model
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fall back to cl100k_base for unknown models (works for most modern models)
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # Fallback: rough estimate of 4 characters per token
        return len(text) // 4


class UsageTracker:
    """Track token usage across multiple LLM calls using tiktoken estimation."""
    
    def __init__(self, model_name: str, config: dict):
        self.model_name = model_name
        self.config = config
        self.input_tokens = 0
        self.output_tokens = 0
        self.input_texts = []
        self.output_texts = []
    
    def add_usage(self, input_tokens: int, output_tokens: int):
        """Add usage from API response metadata."""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
    
    def add_text(self, input_text: str, output_text: str):
        """Add text for tiktoken-based estimation."""
        self.input_texts.append(input_text)
        self.output_texts.append(output_text)
    
    def estimate_tokens(self):
        """Estimate tokens from collected texts using tiktoken."""
        model = self.config.get("model_name", "gpt-4")
        
        for text in self.input_texts:
            self.input_tokens += count_tokens(text, model)
        
        for text in self.output_texts:
            self.output_tokens += count_tokens(text, model)
        
        # Clear texts after estimation
        self.input_texts = []
        self.output_texts = []
    
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
    
    @property
    def cost(self) -> float:
        input_cost = (self.input_tokens / 1_000_000) * self.config["input_cost_per_million"]
        output_cost = (self.output_tokens / 1_000_000) * self.config["output_cost_per_million"]
        return input_cost + output_cost
    
    def to_dict(self) -> dict:
        return {
            "model": self.model_name,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost,
        }


# ============================================================================
# LLM WRAPPER WITH TRACKING
# ============================================================================

class TrackedLLM:
    """Wrapper that tracks token usage for any LLM."""
    
    def __init__(self, llm, tracker: UsageTracker, provider: str):
        self.llm = llm
        self.tracker = tracker
        self.provider = provider
    
    def invoke(self, *args, **kwargs):
        response = self.llm.invoke(*args, **kwargs)
        self._extract_usage(response)
        return response
    
    def _extract_usage(self, response):
        """Extract token usage from response metadata."""
        if hasattr(response, 'response_metadata'):
            metadata = response.response_metadata
            
            if self.provider == "openai":
                usage = metadata.get("token_usage", {})
                self.tracker.add_usage(
                    usage.get("prompt_tokens", 0),
                    usage.get("completion_tokens", 0)
                )
            elif self.provider == "google":
                usage = metadata.get("usage_metadata", {})
                self.tracker.add_usage(
                    usage.get("prompt_token_count", 0),
                    usage.get("candidates_token_count", 0)
                )
    
    def with_structured_output(self, schema):
        """Return a new TrackedLLM with structured output."""
        new_llm = self.llm.with_structured_output(schema)
        return TrackedLLM(new_llm, self.tracker, self.provider)
    
    def __or__(self, other):
        """Support pipe operator for chains."""
        return self.llm | other


# ============================================================================
# SIMPLIFIED SEO EVALUATION AGENT
# ============================================================================

class SimpleSEOEvaluator:
    """Simplified SEO evaluator for model comparison with token tracking."""
    
    def __init__(self, llm: TrackedLLM, lang: LanguageCode = "en"):
        self.llm = llm
        self.lang = lang
    
    def run(self, keyword: str, content: str) -> str:
        """Run a simplified SEO evaluation and return the report."""
        
        # Step 1: Generate personas
        personas = self._generate_personas(keyword)
        
        # Step 2: Evaluate content for each persona
        evaluations = []
        for persona in personas:
            evaluation = self._evaluate_for_persona(content, persona)
            evaluations.append(evaluation)
        
        # Step 3: Generate summary report
        report = self._generate_report(keyword, content, evaluations)
        
        # Estimate tokens from collected texts
        self.llm.tracker.estimate_tokens()
        
        return report
    
    def _generate_personas(self, keyword: str) -> list[SearchIntentPersona]:
        """Generate search intent personas."""
        system_prompt = p("seo_evaluation", "persona_generator_system", self.lang)
        human_prompt = p("seo_evaluation", "persona_generator_human", self.lang).format(keyword=keyword)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", p("seo_evaluation", "persona_generator_human", self.lang)),
        ])
        
        structured_llm = self.llm.with_structured_output(SearchIntentPersonas)
        chain = prompt | structured_llm.llm
        result = chain.invoke({"keyword": keyword})
        
        # Track input text for token estimation
        input_text = system_prompt + "\n" + human_prompt
        
        # Extract usage from structured output
        if hasattr(result, 'response_metadata'):
            self.llm._extract_usage(result)
        
        # Get output text for estimation
        if isinstance(result, SearchIntentPersonas):
            output_text = result.model_dump_json()
            personas = result.personas
        elif isinstance(result, dict):
            import json
            output_text = json.dumps(result)
            personas = [SearchIntentPersona(**p_data) for p_data in result.get("personas", [])]
        else:
            output_text = str(result)
            personas = result.personas if hasattr(result, 'personas') else []
        
        # Add text for tiktoken estimation
        self.llm.tracker.add_text(input_text, output_text)
        
        return personas
    
    def _evaluate_for_persona(self, content: str, persona: SearchIntentPersona) -> Evaluation:
        """Evaluate content from a persona's perspective."""
        looking_for_str = "\n".join([f"- {item}" for item in persona.looking_for]) if persona.looking_for else "- General product information"
        
        # Build prompts for tracking
        system_prompt = p("seo_evaluation", "dialogue_system", self.lang)
        human_prompt = p("seo_evaluation", "dialogue_human", self.lang).format(
            persona_name=persona.name,
            persona_background=persona.background,
            intent_type=persona.intent_type,
            search_query=persona.search_query,
            looking_for=looking_for_str,
            content=content
        )
        
        # Generate dialogue
        dialogue_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", p("seo_evaluation", "dialogue_human", self.lang)),
        ])
        
        chain = dialogue_prompt | self.llm.llm | StrOutputParser()
        dialogue_result = chain.invoke({
            "persona_name": persona.name,
            "persona_background": persona.background,
            "intent_type": persona.intent_type,
            "search_query": persona.search_query,
            "looking_for": looking_for_str,
            "content": content
        })
        
        # Track input/output for token estimation
        input_text = system_prompt + "\n" + human_prompt
        self.llm.tracker.add_text(input_text, dialogue_result)
        
        # Parse dialogue
        import json
        try:
            result = dialogue_result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            dialogue_data = json.loads(result)
            dialogue = [DialogueTurn(**turn) for turn in dialogue_data]
        except (json.JSONDecodeError, KeyError):
            dialogue = [DialogueTurn(
                question="Could not parse evaluation",
                answer="Please check the content manually",
                satisfied=False
            )]
        
        # Generate scores
        scores = {"relevance": 7, "clarity": 7, "completeness": 7, "persuasiveness": 7}
        
        return Evaluation(
            persona=persona,
            dialogue=dialogue,
            scores=scores,
            suggestions=["Review content for this persona's needs"]
        )
    
    def _generate_report(self, keyword: str, content: str, evaluations: list[Evaluation]) -> str:
        """Generate summary report."""
        report = [f"# SEO Evaluation Report\n\n"]
        report.append(f"**Keyword:** {keyword}\n\n")
        report.append(f"**Content:** {content[:200]}...\n\n")
        report.append(f"**Personas Evaluated:** {len(evaluations)}\n\n")
        
        for i, ev in enumerate(evaluations, 1):
            report.append(f"## Persona {i}: {ev.persona.name}\n")
            report.append(f"- Intent: {ev.persona.intent_type}\n")
            report.append(f"- Search Query: \"{ev.persona.search_query}\"\n\n")
            
            report.append("### Dialogue\n")
            for turn in ev.dialogue[:3]:  # Limit to 3 turns
                status = "✓" if turn.satisfied else "✗"
                report.append(f"**Q:** {turn.question}\n")
                report.append(f"**A:** {turn.answer} {status}\n\n")
        
        return "".join(report)


# ============================================================================
# MODEL COMPARISON
# ============================================================================

def create_llm(model_key: str, config: dict, tracker: UsageTracker):
    """Create an LLM instance based on configuration."""
    temperature = config.get("temperature", 0.3)
    if config["provider"] == "openai":
        llm = ChatOpenAI(model_name=config["model_name"], temperature=temperature)
    elif config["provider"] == "google":
        llm = ChatGoogleGenerativeAI(model=config["model_name"], temperature=temperature)
    else:
        raise ValueError(f"Unknown provider: {config['provider']}")
    
    return TrackedLLM(llm, tracker, config["provider"])


def run_comparison(keyword: str, content: str, models: list[str] = None) -> dict:
    """Run SEO evaluation with multiple models and compare results."""
    
    if models is None:
        models = list(MODEL_CONFIGS.keys())
    
    results = {}
    
    for model_key in models:
        if model_key not in MODEL_CONFIGS:
            print(f"  ⚠ Unknown model: {model_key}, skipping...")
            continue
        
        config = MODEL_CONFIGS[model_key]
        tracker = UsageTracker(model_key, config)
        
        print(f"\n{'='*60}")
        print(f"Running: {model_key}")
        print(f"{'='*60}")
        
        try:
            llm = create_llm(model_key, config, tracker)
            evaluator = SimpleSEOEvaluator(llm, lang="en")
            
            output = evaluator.run(keyword, content)
            
            results[model_key] = {
                "output": output,
                "usage": tracker.to_dict(),
                "error": None,
            }
            
            print(f"  ✓ Completed: {tracker.total_tokens} tokens, ${tracker.cost:.4f}")
            
        except Exception as e:
            results[model_key] = {
                "output": None,
                "usage": tracker.to_dict(),
                "error": str(e),
            }
            print(f"  ✗ Error: {e}")
    
    return results


def generate_comparison_report(keyword: str, content: str, results: dict) -> str:
    """Generate a markdown comparison report."""
    
    report = []
    report.append("# Model Comparison Report: SEO Evaluation\n\n")
    report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    report.append(f"**Keyword:** {keyword}\n\n")
    report.append(f"**Content:** {content[:300]}{'...' if len(content) > 300 else ''}\n\n")
    
    # Cost comparison table
    report.append("## Cost Comparison\n\n")
    report.append("| Model | Input Tokens | Output Tokens | Total Tokens | Cost (USD) |\n")
    report.append("|-------|-------------|---------------|--------------|------------|\n")
    
    for model_key, result in results.items():
        usage = result["usage"]
        if result["error"]:
            report.append(f"| {model_key} | - | - | - | ERROR |\n")
        else:
            report.append(f"| {model_key} | {usage['input_tokens']:,} | {usage['output_tokens']:,} | {usage['total_tokens']:,} | ${usage['cost_usd']:.4f} |\n")
    
    report.append("\n")
    
    # Output comparison
    report.append("## Output Comparison\n\n")
    report.append("Review the outputs below to evaluate quality:\n\n")
    
    for model_key, result in results.items():
        report.append(f"---\n\n")
        report.append(f"### {model_key}\n\n")
        
        if result["error"]:
            report.append(f"**Error:** {result['error']}\n\n")
        else:
            report.append(f"```\n{result['output']}\n```\n\n")
    
    return "".join(report)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Compare LLM models on SEO Evaluation task")
    parser.add_argument("--keyword", type=str, required=True, help="Target keyword for SEO")
    parser.add_argument("--content", type=str, help="Product description text")
    parser.add_argument("--content-file", type=str, help="Path to file containing product description")
    parser.add_argument("--models", type=str, nargs="+", 
                        default=list(MODEL_CONFIGS.keys()),
                        help=f"Models to compare. Options: {list(MODEL_CONFIGS.keys())}")
    args = parser.parse_args()
    
    # Get content
    if args.content:
        content = args.content
    elif args.content_file:
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        parser.error("Either --content or --content-file is required")
    
    print("\n" + "="*60)
    print("MODEL COMPARISON: SEO EVALUATION")
    print("="*60)
    print(f"Keyword: {args.keyword}")
    print(f"Content: {content[:100]}...")
    print(f"Models: {args.models}")
    
    # Run comparison
    results = run_comparison(args.keyword, content, args.models)
    
    # Generate report
    report = generate_comparison_report(args.keyword, content, results)
    
    # Save report
    output_dir = os.path.dirname(__file__)
    date_str = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(output_dir, f"{date_str}-comparison-report.md")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n" + "="*60)
    print(f"Report saved to: {output_path}")
    print("="*60)
    print("\n" + report)


if __name__ == "__main__":
    main()
