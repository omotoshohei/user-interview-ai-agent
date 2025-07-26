import operator
from typing import Annotated, Any, Optional
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.caches import BaseCache
ChatOpenAI.model_rebuild()
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
import os

###### Use dotenv if available ######
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    import warnings
    warnings.warn("dotenv not found. Please make sure to set your environment variables manually.", ImportWarning)
################################################


# ペルソナを表すデータモデル
class Persona(BaseModel):
    name: str = Field(..., description="ペルソナの名前")
    background: str = Field(..., description="ペルソナの持つ背景")


# ペルソナのリストを表すデータモデル
class Personas(BaseModel):
    personas: list[Persona] = Field(
        default_factory=list, description="ペルソナのリスト"
    )


# インタビュー内容を表すデータモデル
class Interview(BaseModel):
    persona: Persona = Field(..., description="インタビュー対象のペルソナ")
    question: str = Field(..., description="インタビューでの質問")
    answer: str = Field(..., description="インタビューでの回答")


# インタビュー結果のリストを表すデータモデル
class InterviewResult(BaseModel):
    interviews: list[Interview] = Field(
        default_factory=list, description="インタビュー結果のリスト"
    )

# 要件定義生成AIエージェントのステート
class InterviewState(BaseModel):
    user_request: str = Field(..., description="クライアントの議題")
    personas: Annotated[list[Persona], operator.add] = Field(
        default_factory=list, description="生成されたペルソナのリスト"
    )
    interviews: Annotated[list[Interview], operator.add] = Field(
        default_factory=list, description="実施されたインタビューのリスト"
    )
    output_doc: str = Field(default="", description="生成されたユーザーインタビューのまとめドキュメント")



# ペルソナを生成するクラス
class PersonaGenerator:
    def __init__(self, llm: ChatOpenAI, k: int = 10):
        self.llm = llm.with_structured_output(Personas)
        self.k = k

    def run(self, user_request: str) -> Personas:
        # プロンプトテンプレートを定義
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたはユーザーインタビュー用の多様なペルソナを作成する専門家です。",
                ),
                (
                    "human",
                    f"以下のユーザーリクエストに関するインタビュー用に、{self.k}人の多様なペルソナを生成してください.\n\n"
                    "トピック: {user_request}\n\n"
                    "各ペルソナには名前と簡単な背景を含めてください。年齢、性別、職業、トピックに対する知識レベルにおいて多様性を確保してください。",
                ),
            ]
        )
        # ペルソナ生成のためのチェーンを作成
        chain = prompt | self.llm
        # ペルソナを生成
        return chain.invoke({"user_request": user_request})


# インタビューを実施するクラス
class InterviewConductor:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def run(self, user_request: str, personas: list[Persona]) -> InterviewResult:
        # 質問を生成
        questions = self._generate_questions(
            user_request=user_request, personas=personas
        )
        # 回答を生成
        answers = self._generate_answers(personas=personas, questions=questions)
        # 質問と回答の組み合わせからインタビューリストを作成
        interviews = self._create_interviews(
            personas=personas, questions=questions, answers=answers
        )
        # インタビュー結果を返す
        return InterviewResult(interviews=interviews)

    def _generate_questions(
        self, user_request: str, personas: list[Persona]
    ) -> list[str]:
        # 質問生成のためのプロンプトを定義
        question_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたはクライアントの依頼に基づいて適切な質問を生成するユーザーインタビューの専門家です。",
                ),
                (
                    "human",
                    "以下の議題について、1つの質問を生成してください。\n\n"
                    "議題: {user_request}\n"
                    "ペルソナ: {persona_name} - {persona_background}\n\n"
                    "質問は具体的で、このペルソナの視点から重要な情報を引き出すように設計してください。",
                ),
            ]
        )
        # 質問生成のためのチェーンを作成
        question_chain = question_prompt | self.llm | StrOutputParser()

        # 各ペルソナに対する質問クエリを作成
        question_queries = [
            {
                "user_request": user_request,
                "persona_name": persona.name,
                "persona_background": persona.background,
            }
            for persona in personas
        ]
        # 質問をバッチ処理で生成
        return question_chain.batch(question_queries)

    def _generate_answers(
        self, personas: list[Persona], questions: list[str]
    ) -> list[str]:
        # 回答生成のためのプロンプトを定義
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは以下のペルソナとして回答しています:  {persona_name} - {persona_background}",
                ),
                ("human", "質問: {question}"),
            ]
        )
        # 回答生成のためのチェーンを作成
        answer_chain = answer_prompt | self.llm | StrOutputParser()

        # 各ペルソナに対する回答クエリを作成
        answer_queries = [
            {
                "persona_name": persona.name,
                "persona_background": persona.background,
                "question": question,
            }
            for persona, question in zip(personas, questions)
        ]
        # 回答をバッチ処理で生成
        return answer_chain.batch(answer_queries)

    def _create_interviews(
        self, personas: list[Persona], questions: list[str], answers: list[str]
    ) -> list[Interview]:
        # ペルソナ毎に質問と回答の組み合わせからインタビューオブジェクトを作成
        return [
            Interview(persona=persona, question=question, answer=answer)
            for persona, question, answer in zip(personas, questions, answers)
        ]



# 要件定義書を生成するクラス
class RequirementsDocumentGenerator:
    def __init__(self, llm: ChatOpenAI, k: int):
        self.llm = llm
        self.k = k

    def run(self, user_request: str, interviews: list[Interview]) -> str:
        # プロンプトを定義
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an user interview insights analyst.",
                ),
                (
                    "human",
                    "Build a concise survey report from the answers, quantifying recurring themes.\n\n"
                    "Theme: {user_request}\n\n"
                    "Interview Result:\n{interview_results}\n"
                    "Output structure:\n"
                    "## Executive Summary\n"
                    "## Quantitative Stats (theme | mentions | % of 10) – list top 5‑7 themes\n"
                    "## Key Qualitative Insights (organised by theme, incl. 1‑2 persona quotes)\n"
                    f"## Example Personas (Generate {self.k} distinct personas based on the interviews)\n"
                    "## Recommended Next Actions\n\n"
                    "Language is to be English\n\n:"
                ),
            ]
        )
        # ユーザーインタビューのドキュメントを生成するチェーンを作成
        chain = prompt | self.llm | StrOutputParser()
        # ユーザーインタビューのドキュメントを生成
        return chain.invoke(
            {
                "user_request": user_request,
                "interview_results": "\n".join(
                    f"ペルソナ: {i.persona.name} - {i.persona.background}\n"
                    f"質問: {i.question}\n回答: {i.answer}\n"
                    for i in interviews
                ),
            }
        )


# ユーザーインタビューAIエージェントのクラス
class DocumentationAgent:
    def __init__(self, llm: ChatOpenAI, k: Optional[int] = None):
        # 各種ジェネレータの初期化
        self.persona_generator = PersonaGenerator(llm=llm, k=k)
        self.interview_conductor = InterviewConductor(llm=llm)
        # self.information_evaluator = InformationEvaluator(llm=llm)
        self.requirements_generator = RequirementsDocumentGenerator(llm=llm, k=k)

        # グラフの作成
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        # グラフの初期化
        workflow = StateGraph(InterviewState)

        # 各ノードの追加
        workflow.add_node("generate_personas", self._generate_personas)
        workflow.add_node("conduct_interviews", self._conduct_interviews)
        workflow.add_node("generate_output", self._generate_output)

        # エントリーポイントの設定
        workflow.set_entry_point("generate_personas")

        # ノード間のエッジの追加
        workflow.add_edge("generate_personas", "conduct_interviews")
        workflow.add_edge("conduct_interviews", "generate_output")
        workflow.add_edge("generate_output", END)

        # グラフのコンパイル
        return workflow.compile()

    def _generate_personas(self, state: InterviewState) -> dict[str, Any]:
        # ペルソナの生成
        new_personas: Personas = self.persona_generator.run(state.user_request)
        return {"personas": new_personas.personas}

    def _conduct_interviews(self, state: InterviewState) -> dict[str, Any]:
        # インタビューの実施
        new_interviews: InterviewResult = self.interview_conductor.run(
            state.user_request, state.personas[-10:]
        )
        return {"interviews": new_interviews.interviews}


    def _generate_output(self, state: InterviewState) -> dict[str, Any]:
        # インタビュー結果のドキュメント生成
        output_doc: str = self.requirements_generator.run(
            state.user_request, state.interviews
        )
        return {"output_doc": output_doc}

    def run(self, user_request: str) -> str:
        # 初期状態の設定
        initial_state = InterviewState(user_request=user_request)
        # グラフの実行
        final_state = self.graph.invoke(initial_state)
        # 最終的な要件定義書の取得
        return final_state["output_doc"]

import argparse
from datetime import datetime

# メイン関数
def main():
    # コマンドライン引数を解析
    parser = argparse.ArgumentParser(description="ユーザーインタビューAIエージェント")
    parser.add_argument("--user-request", type=str, required=True, help="ユーザーインタビューの議題")
    parser.add_argument("--k", type=int, default=10, help="生成するペルソナの人数")
    parser.add_argument("--model-name", type=str, default="gpt-4.1-mini-2025-04-14", help="使用するOpenAIモデル名")
    args = parser.parse_args()

    # ChatOpenAIモデルを初期化
    llm = ChatOpenAI(model_name=args.model_name, temperature=0.3)

    # 要件定義書生成AIエージェントを初期化
    agent = DocumentationAgent(llm=llm, k=args.k)
    # エージェントを実行して最終的な出力を取得
    final_output = agent.run(user_request=args.user_request)

    # Add the title to the output
    title = f"# User Interview - {args.user_request}\n\n"
    final_output_with_title = title + final_output

    # 出力ディレクトリを作成
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # ファイル名を生成
    date_str = datetime.now().strftime("%Y%m%d")
    topic_str = args.user_request.lower().replace(' ', '-')
    file_name = f"{date_str}-{topic_str}.md"
    output_path = os.path.join(output_dir, file_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_output_with_title)
    print(f"ユーザーインタビューのレポートが '{output_path}' に保存されました。")

    # 最終的な出力を表示
    print(final_output_with_title)

if __name__ == "__main__":
    main()
