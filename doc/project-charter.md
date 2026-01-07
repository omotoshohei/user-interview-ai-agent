# Project Charter: AI Research Agents

> **Last Updated**: 2026-01-07
> **Status**: Active (Phase 3: Optimization)

## 1. Project Summary

**AI Research Agents**は、LangGraphを活用したマルチエージェントシステムのポートフォリオ構築プロジェクトです。
UXリサーチ、SEO検索意図評価、翻訳品質評価、マーケティング文章評価など、高度な判断を要する定性的な分析業務を、専門的な「ペルソナ」を持つAIエージェント群により自動化・効率化します。
本来であれば高コストな「ユーザーインタビューに基づく精査」という理想的なワークフローを、LangGraph上のAIエージェントで再現することで、アイデアやコンテンツに対する**「客観的で妥当な評価基準」**を低コストで提供することを目的としています。
当初の「User Interview AI Agent」単体から発展し、現在は共通アーキテクチャに基づく多様なリサーチエージェント群として拡張されています。

## 2. Business Case

| 項目                           | 分析内容                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **現状の課題 (Problem)** | ・アイデアやAI生成コンテンツを評価する際、**「何を基準に評価すればよいか分からない」**という課題がある。`<br>`・本来はユーザーインタビューに基づいて精査するのがベストだが、コストと時間（数時間/件、数万円/件）がかかりすぎるため、頻繁には実施できない。                                                                                                                                                |
| **解決策 (Solution)**    | ・LangGraphを用いて**ユーザーインタビューと全く同じワークフローをAI上で構成**し、専門知識を持つ複数のペルソナによる精査を自動化。`<br>`・「ちゃんとした内容で精査する」ための評価基準とプロセスを、CLIツールとして提供。                                                                                                                                                                            |
| **想定効果 (Benefits)**  | ・**評価基準の確立**: 曖昧になりがちな定性評価に対し、擬似ユーザーフィードバックに基づく明確な基準を提供。`<br>`・**時間短縮**: 調査・評価タスクを数分で完了（90%以上の工数削減）。`<br>`・**コスト削減**: 外部委託や人件費と比較し、APIコスト（数円〜数十円/回）による圧倒的な低コスト化。`<br>`・**品質向上**: 人間が見落としがちな観点を、複数のAIペルソナが網羅的に指摘。 |

## 3. Goals & Objectives (SMART)

* **O1: 多様な定性調査タスクの実用的な自動化**
  * KR1 (Scope): 4種類の主要エージェント（インタビュー、SEO、翻訳、文章評価）を実装し、実務で利用可能な状態にする。【達成済】
  * KR2 (Quality): 生成されたレポートが、修正なしで意思決定やコンテンツ改善に利用できるレベル（主観満足度80%以上）を維持する。
  * KR3 (i18n): すべてのエージェントで日本語・英語の両言語に対応する。【達成済】
* **O2: 運用コストとパフォーマンスの最適化**
  * KR1 (Cost): モデル比較（gpt-5-mini vs others）を実施し、品質を維持しつつコスト効率の良いモデル構成を確立する。(2026-01完了)
  * KR2 (Efficiency): レポート生成からPDF化までのワークフローを完全自動化する。

## 4. Scope

### In Scope

**Core Agents**:

**User Interview Agent**: 架空ペルソナによるインタビューシミュレーション

**SEO Search Intent Evaluation Agent**: 検索意図（Informational/Navigational/Transactional）に基づくコンテンツ評価

* **Translation Evaluation Agent**: 文化的背景を考慮した翻訳自然さ評価

**Sentence Evaluation Agent**: ターゲット読者視点での文章評価

**Shared Infrastructure**:

*  LangGraphを用いたステートフルなエージェント基盤
*  共通ペルソナモデル定義
*  Markdownレポート出力 & PDF変換機能 (日本語フォント対応)

**Interface**: CLI (Command Line Interface)

### Out of Scope

* **GUI**: Webブラウザやモバイルアプリ上のGUI実装（現フェーズではCLI運用に特化）
* **Real Users**: 実際の人間を対象としたインタビュー機能
* **SaaS Sales**: 外部向けの商用SaaSとしてのパッケージング（あくまで社内ツール/ポートフォリオ）

## 5. Deliverables

1. **Source Code**: GitHubリポジトリ (`ai-research-agents`)
2. **Scripts**: 各種エージェント実行スクリプト (`script/run-*.py`)
3. **Reports**: 定形化されたMarkdownおよびPDFレポート (`output/`)
4. **Documentation**: README, モデル比較レポート, 開発ドキュメント

## 6. Stakeholders & Team

| Role                          | Name   | Responsibility                                                 |
| ----------------------------- | ------ | -------------------------------------------------------------- |
| **Project Owner / Dev** | Shohei | プロジェクト全体の意思決定、要件定義、設計、実装、テスト、利用 |
| **Reviewer**            | TBA    | UX/ユーザビリティに関するフィードバック                        |

## 7. Timeline & Milestones

* **Phase 1: MVP (2025-07 〜 2025-08)**
  * User Interview Agentのプロトタイプ開発
  * 基本アーキテクチャの検証
* **Phase 2: Expansion (2025-09 〜 2025-12)**
  * SEO, Translation, Sentence Evaluation Agentの追加
  * 多言語対応 (i18n)
  * 共通基盤の整備 (LangGraph移行)
* **Phase 3: Optimization (2026-01 〜 Current)**
  * モデル性能評価 (gpt-5-mini選定)
  * PDF出力機能の実装
  * 全体リファクタリングとドキュメント整備
  * **(New)** 実際の運用での利用・検証 (Practical Operation)
  * **(New)** 新規ユースケースの探索・追加 (Explore New Use Cases)

## 8. Risks & Constraints

* **Risks**:
  * LLMのモデル更新による出力挙動の変化（プロンプトの再調整が必要になる可能性）。
  * APIコストの予期せぬ増大（監視により緩和）。
* **Constraints**:
  * 個人開発のため、開発リソースは週数時間に限定される。
  * 日本語PDF生成におけるフォント依存（GenShinGothic等が必要）。

## 9. Resources & Budget

* **Budget**: OpenAI API利用料（月間予算内で運用、変動費）
* **Tools**:
  * **Development**: Python, UV, Cursor, VS Code
  * **AI Models**: OpenAI (GPT-4o, GPT-5-mini), Google (Gemini)
  * **Frameworks**: LangGraph, LangChain

## 10. Detailed Requirements

> 本セクションはプロジェクトの詳細な機能的・非機能的要件を定義します。

### 10.1 Functional Requirements (機能要件)

#### 10.1.1 Shared Capabilities (共通機能)

* **CLIインターフェース**: 全てのエージェントはコマンドライン（Pythonスクリプト）から実行可能であること。
* **多言語対応 (i18n)**: 出力レポートは日本語 (`--lang jp`) および英語 (`--lang en`) の両方に対応すること。
* **レポート出力**: 分析結果はMarkdown形式で保存され、必要に応じてPDFに変換可能であること。
* **モデル選択**: 実行時に利用するLLMモデル（OpenAI gpt-5-mini, gpt-4o 等）を指定可能であること。

#### 10.1.2 Agent Specifics (エージェント別機能)

* **A. User Interview Agent**
  * 指定されたトピックに基づき、多様な背景を持つ架空のユーザーペルソナを生成する。
  * 設定されたペルソナに対し、チャット形式で深掘りインタビューを自動実行する。
  * インタビュー内容を分析し、インサイトを要約したレポートを生成する。
* **B. SEO Search Intent Evaluation Agent**
  * ターゲットキーワードに対する検索意図（Informational, Navigational, Transactional）を分析する。
  * 3つの異なる検索意図ペルソナを生成し、対象コンテンツがニーズを満たしているか評価する。
  * Relevance, Clarity, Completeness, Persuasiveness の4軸でスコアリングを行う。
* **C. Translation Evaluation Agent**
  * 原文と翻訳文を比較し、文法的な正確さだけでなく「自然さ」「トーン」を評価する。
  * 3つの異なる読者ペルソナ（例：ビジネスマン、一般消費者、若者）視点でのフィードバックを提供する。
  * 具体的な修正提案（Rewrite Suggestions）を生成する。
* **D. Sentence Evaluation Agent**
  * 文章の利用シーン（Context）に基づき、最適な評価ペルソナを動的に生成する。
  * Clarity, Impact, Tone, Persuasiveness の観点から詳細なフィードバックを行う。

### 10.2 Non-Functional Requirements (非機能要件)

* **性能 (Performance)**: 各エージェントの処理は、人間が行う場合の1/10以下の時間（数分以内）で完了すること。また、LangGraph上でペルソナごとの並列処理を行うこと。
* **コスト (Cost)**: APIコストは、人間による作業や外部委託と比較して圧倒的に安価（数十円/回レベル）であること。デフォルトでコストパフォーマンスの高いモデルを使用すること。
* **信頼性 (Reliability)**: LangGraphにより状態管理を行い、エラー時の復帰やデバッグが容易であること。生成される評価コメントは主観満足度80%以上の品質を維持すること。

### 10.3 Target Users (ターゲットユーザー)

* **プロダクトマネージャー (PM)**: ユーザーインタビューの代行、企画書のブラッシュアップ。
* **コンテンツマーケター / ライター**: 記事のSEO評価、キャッチコピーの推敲。
* **エンジニア / 開発者**: 多言語対応時の翻訳チェック、ドキュメントの分かりやすさ評価。

### 10.4 Technical Stack (技術スタック)

* **Backend**: Python, LangGraph, LangChain
* **AI Models**: OpenAI API (GPT-4o, GPT-5-mini), Google Gemini API
* **Environment**: UV (Python Package Manager)
* **Output**: Markdown, PDF (VivaLi/ReportLab)

---

# Appendix A: Market Research (Phase 1 Context)

*プロジェクト開始当初(2025年)の市場分析メモ*

## 1. DeepResearch まとめ

### 市場動向

* AI ネイティブ UX リサーチはまだ黎明期で、買い手がベンダー名を１つ挙げるのも難しい“グリーンフィールド”状態。
* 急速に導入が進めば既存 UX リサーチ市場（年間 250 億 USD 規模）の置き換え余地がある。

### 競合・類似プロダクト (2025年時点)

* “自動インタビュー＋要約” 機能をうたう SaaS が 9 社ほど登場。
* いずれも **月額 50–200 USD/seat** の価格帯で、中小チームにリーチしている。

### 技術スタック妥当性

* LangGraph には「インタビュアー／インタビュイー／サマライザー」のマルチエージェント例があり、テンプレート流用や拡張が容易である。

## 2. Initial Business Case (MVP試算)

| 項目                   | 試算 (2025 MVP)                                                |
| ---------------------- | -------------------------------------------------------------- |
| **対象作業削減** | インタビュー設計 1h + 要約 0.5h =**1.5h／回**            |
| **想定利用頻度** | **1回／週**（社内プロダクト開発ペース）                  |
| **時給換算**     | ¥8,000／h（シニア PM 人件費相当）                             |
| **年間削減効果** | 1.5h × 1 × 48週 × ¥8,000 ≒**¥0.576 M**             |
| **開発コスト**   | ・開発 20h (¥160k)`<br>`・API費 (月¥5k ≒ 年¥60k)         |
| **ROI**          | 初年度：効果 ¥0.576 M / コスト ¥0.22 M →**約 2.6 倍** |
