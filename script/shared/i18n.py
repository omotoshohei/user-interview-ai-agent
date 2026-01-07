"""
Internationalization (i18n) module for AI Research Agents.
Provides bilingual support (English/Japanese) for all agents.
"""

from typing import Literal

LanguageCode = Literal["en", "jp"]


# =============================================================================
# PROMPTS - LLM System/Human messages organized by agent
# =============================================================================

PROMPTS = {
    # -------------------------------------------------------------------------
    # User Interview Agent
    # -------------------------------------------------------------------------
    "user_interview": {
        "persona_generator_system": {
            "en": "You are an expert at creating diverse personas for user interviews.",
            "jp": "あなたはユーザーインタビュー用の多様なペルソナを作成する専門家です。"
        },
        "persona_generator_human": {
            "en": (
                "Generate {k} diverse personas for user interviews on the following topic.\n\n"
                "Topic: {user_request}\n\n"
                "Include a name and brief background for each persona. "
                "Ensure diversity in age, gender, occupation, and knowledge level regarding the topic."
            ),
            "jp": (
                "以下のユーザーリクエストに関するインタビュー用に、{k}人の多様なペルソナを生成してください.\n\n"
                "トピック: {user_request}\n\n"
                "各ペルソナには名前と簡単な背景を含めてください。年齢、性別、職業、トピックに対する知識レベルにおいて多様性を確保してください。"
            )
        },
        "question_generator_system": {
            "en": "You are a user interview expert who generates appropriate questions based on client requests.",
            "jp": "あなたはクライアントの依頼に基づいて適切な質問を生成するユーザーインタビューの専門家です。"
        },
        "question_generator_human": {
            "en": (
                "Generate one question about the following topic.\n\n"
                "Topic: {user_request}\n"
                "Persona: {persona_name} - {persona_background}\n\n"
                "Design the question to be specific and to elicit important information from this persona's perspective."
            ),
            "jp": (
                "以下の議題について、1つの質問を生成してください。\n\n"
                "議題: {user_request}\n"
                "ペルソナ: {persona_name} - {persona_background}\n\n"
                "質問は具体的で、このペルソナの視点から重要な情報を引き出すように設計してください。"
            )
        },
        "answer_generator_system": {
            "en": "You are responding as the following persona: {persona_name} - {persona_background}",
            "jp": "あなたは以下のペルソナとして回答しています: {persona_name} - {persona_background}"
        },
        "answer_generator_human": {
            "en": "Question: {question}",
            "jp": "質問: {question}"
        },
        "insights_generator_system": {
            "en": "You are a user interview insights analyst.",
            "jp": "あなたはユーザーインタビューのインサイト分析の専門家です。"
        },
        "insights_generator_human": {
            "en": (
                "Build a concise survey report from the answers, quantifying recurring themes.\n\n"
                "Theme: {user_request}\n\n"
                "Interview Result:\n{interview_results}\n"
                "Output structure:\n"
                "## Executive Summary\n"
                "## Quantitative Stats (theme | mentions | % of {k}) – list top 5-7 themes\n"
                "## Key Qualitative Insights (organised by theme, incl. 1-2 persona quotes)\n"
                "## Recommended Next Actions\n\n"
                "Language is to be English\n\n"
            ),
            "jp": (
                "回答から簡潔な調査レポートを作成し、繰り返し出現するテーマを定量化してください。\n\n"
                "テーマ: {user_request}\n\n"
                "インタビュー結果:\n{interview_results}\n"
                "出力構成:\n"
                "## エグゼクティブサマリー\n"
                "## 定量的統計（テーマ | 言及数 | {k}人中の%）– 上位5-7テーマをリスト\n"
                "## 主要な定性的インサイト（テーマ別に整理、1-2のペルソナ引用を含む）\n"
                "## 推奨される次のアクション\n\n"
                "言語は日本語で\n\n"
            )
        },
    },

    # -------------------------------------------------------------------------
    # SEO Search Intent Evaluation Agent
    # -------------------------------------------------------------------------
    "seo_evaluation": {
        "persona_generator_system": {
            "en": (
                "You are an expert in user behavior and search intent analysis. "
                "Generate 3 distinct personas representing different search intents for a product keyword."
            ),
            "jp": (
                "あなたはユーザー行動と検索意図分析の専門家です。"
                "商品キーワードに対する異なる検索意図を代表する3人の異なるペルソナを生成してください。"
            )
        },
        "persona_generator_human": {
            "en": (
                "Generate 3 personas for the keyword: {keyword}\n\n"
                "Create one persona for each search intent type:\n"
                "1. **Informational**: Someone researching to learn about the product category\n"
                "2. **Navigational/Comparative**: Someone comparing options before deciding\n"
                "3. **Transactional**: Someone ready to buy, looking for the right offer\n\n"
                "For each persona, include:\n"
                "- A realistic name\n"
                "- Their background and motivation\n"
                "- An example search query they would use\n"
                "- A list of 3 specific things they are looking for in the product description (looking_for)"
            ),
            "jp": (
                "以下のキーワードに対して3人のペルソナを生成してください: {keyword}\n\n"
                "各検索意図タイプに1人ずつペルソナを作成してください:\n"
                "1. **情報収集型**: 商品カテゴリについて調べて学ぼうとしている人\n"
                "2. **比較検討型**: 決定前に選択肢を比較している人\n"
                "3. **取引型**: 購入準備ができており、適切なオファーを探している人\n\n"
                "各ペルソナには以下を含めてください:\n"
                "- 現実的な名前\n"
                "- 背景とモチベーション\n"
                "- 使用する検索クエリの例\n"
                "- 商品説明で探している3つの具体的な事項 (looking_for)"
            )
        },
        "persona_generator_informational": {
            "en": (
                "Generate 3 personas for the keyword: {keyword}\n\n"
                "ALL personas should have **INFORMATIONAL** intent (learning/researching, not buying).\n"
                "Create personas with DIFFERENT EXPERTISE LEVELS:\n\n"
                "1. **Beginner**: Someone new to the topic, looking for basic definitions and concepts\n"
                "   - Search query example: 'what is [topic]' or '[topic] 101'\n"
                "2. **Intermediate**: Someone familiar with basics, looking for practical how-to guides\n"
                "   - Search query example: '[topic] checklist' or 'how to [do topic]'\n"
                "3. **Advanced/Expert**: Someone experienced, looking for advanced techniques or edge cases\n"
                "   - Search query example: '[topic] advanced techniques' or '[topic] best practices 2024'\n\n"
                "For each persona, include:\n"
                "- A realistic name\n"
                "- Their background, job role, and why they're researching this\n"
                "- An example search query matching their expertise level\n"
                "- A list of 3 specific things they are looking for (looking_for)\n"
                "- Set intent_type to 'informational' for all personas"
            ),
            "jp": (
                "以下のキーワードに対して3人のペルソナを生成してください: {keyword}\n\n"
                "全てのペルソナは**情報収集型**（学習・調査目的、購入目的ではない）である必要があります。\n"
                "異なる**専門知識レベル**のペルソナを作成してください:\n\n"
                "1. **初心者**: トピックに初めて触れる人、基本的な定義と概念を求めている\n"
                "   - 検索クエリ例: 「[トピック]とは」「[トピック] 入門」\n"
                "2. **中級者**: 基本を理解している人、実践的なハウツーガイドを求めている\n"
                "   - 検索クエリ例: 「[トピック] チェックリスト」「[トピック] やり方」\n"
                "3. **上級者/エキスパート**: 経験豊富な人、高度なテクニックやエッジケースを求めている\n"
                "   - 検索クエリ例: 「[トピック] 上級テクニック」「[トピック] ベストプラクティス 2024」\n\n"
                "各ペルソナには以下を含めてください:\n"
                "- 現実的な名前\n"
                "- 背景、職種、なぜこのトピックを調べているか\n"
                "- 専門知識レベルに合った検索クエリの例\n"
                "- 探している3つの具体的な事項 (looking_for)\n"
                "- intent_typeは全ペルソナで 'informational' に設定"
            )
        },
        "dialogue_system": {
            "en": (
                "You are {persona_name}, {persona_background}. "
                "Your search intent is {intent_type}. "
                "You searched for: \"{search_query}\"\n\n"
                "You are looking for the following information:\n{looking_for}\n\n"
                "After reading the product description, answer whether you found what you were looking for. "
                "Be conversational and specific about what you did or didn't find."
            ),
            "jp": (
                "あなたは{persona_name}で、{persona_background}です。"
                "あなたの検索意図は{intent_type}です。"
                "あなたは「{search_query}」と検索しました。\n\n"
                "あなたは以下の情報を探しています:\n{looking_for}\n\n"
                "商品説明を読んだ後、探していた情報が見つかったかどうか答えてください。"
                "何が見つかったか、見つからなかったかについて、会話的かつ具体的に述べてください。"
            )
        },
        "dialogue_human": {
            "en": (
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
            "jp": (
                "商品説明:\n{content}\n\n"
                "探していた各項目について、「探していた情報は見つかりましたか？」という質問に答えてください。\n"
                "自然に答えてください。例：「はい、Xについて探していたのですが、説明に明確に記載されていました...」または"
                "「いいえ、Xについて知りたかったのですが、説明には記載されていませんでした...」\n\n"
                "以下のJSON形式で正確に3つの評価回答を生成してください:\n"
                "[\n"
                '  {{"question": "[具体的な項目]についての情報は見つかりましたか？", "answer": "[見つかったもの・見つからなかったものについての会話的な回答]", "satisfied": true/false}},\n'
                '  {{"question": "[具体的な項目]についての情報は見つかりましたか？", "answer": "[会話的な回答]", "satisfied": true/false}},\n'
                '  {{"question": "[具体的な項目]についての情報は見つかりましたか？", "answer": "[会話的な回答]", "satisfied": true/false}}\n'
                "]"
            )
        },
        "scores_system": {
            "en": (
                "You are evaluating content from the perspective of {persona_name} ({intent_type} intent). "
                "Based on the evaluation dialogue, score the content on these criteria (1-10):\n"
                "- relevance: How well does it match the search intent?\n"
                "- clarity: How easy is it to understand?\n"
                "- completeness: Does it answer key questions?\n"
                "- persuasiveness: Does it motivate action?"
            ),
            "jp": (
                "{persona_name}（{intent_type}意図）の視点からコンテンツを評価しています。"
                "評価対話に基づいて、以下の基準でコンテンツを採点してください（1-10）:\n"
                "- 関連性: 検索意図にどの程度マッチしているか？\n"
                "- 明確さ: 理解しやすいか？\n"
                "- 完全性: 重要な質問に答えているか？\n"
                "- 説得力: 行動を促すか？"
            )
        },
        "scores_human": {
            "en": (
                "Content:\n{content}\n\n"
                "Evaluation Dialogue:\n{dialogue}\n\n"
                "Respond with ONLY a JSON object like: "
                '{{"relevance": 8, "clarity": 7, "completeness": 6, "persuasiveness": 9}}'
            ),
            "jp": (
                "コンテンツ:\n{content}\n\n"
                "評価対話:\n{dialogue}\n\n"
                "以下のようなJSONオブジェクトのみで回答してください: "
                '{{"relevance": 8, "clarity": 7, "completeness": 6, "persuasiveness": 9}}'
            )
        },
        "suggestions_system": {
            "en": (
                "You are a content optimization expert. Based on the unsatisfied questions AND the persona's detailed feedback, "
                "provide specific, actionable suggestions categorized into 'Topics to Add' and 'Parts to Rewrite'."
            ),
            "jp": (
                "あなたはコンテンツ最適化の専門家です。満たされなかった質問と、それに対するペルソナの具体的なフィードバックに基づいて、"
                "具体的で実行可能な改善案を「追加すべきトピック」と「リライトすべき箇所」に分類して提案してください。"
            )
        },
        "suggestions_human": {
            "en": (
                "Persona: {persona_name} ({intent_type} intent)\n"
                "Unsatisfied Points (Question & Reason):\n{questions}\n\n"
                "Respond with ONLY a JSON object in this format:\n"
                '{{\n'
                '  "add_topics": ["Suggestion 1 (Reason)", "Suggestion 2 (Reason)"],\n'
                '  "rewrite_suggestions": ["Suggestion 1 (Reason)", "Suggestion 2 (Reason)"]\n'
                '}}'
            ),
            "jp": (
                "ペルソナ: {persona_name}（{intent_type}意図）\n"
                "不満点（質問と理由）:\n{questions}\n\n"
                "以下のJSON形式のみで回答してください:\n"
                '{{\n'
                '  "add_topics": ["追加案1（理由）", "追加案2（理由）"],\n'
                '  "rewrite_suggestions": ["リライト案1（理由）", "リライト案2（理由）"]\n'
                '}}'
            )
        },
    },

    # -------------------------------------------------------------------------
    # Translation Evaluation Agent
    # -------------------------------------------------------------------------
    "translation_evaluation": {
        "persona_generator_system": {
            "en": (
                "You are an expert at creating reader personas for evaluating Japanese translations of marketing content. "
                "Generate 3 distinct reader perspective personas."
            ),
            "jp": (
                "あなたはマーケティングコンテンツの日本語翻訳を評価するための読者ペルソナを作成する専門家です。"
                "3人の異なる読者視点のペルソナを生成してください。"
            )
        },
        "persona_generator_human": {
            "en": (
                "Generate 3 personas for evaluating the Japanese translation of the following English marketing text:\n\n"
                "Source text: {source_text}\n\n"
                "Create the following 3 types of reader personas:\n"
                "1. **Business Professional** (30-40s): Someone who regularly reads formal business documents\n"
                "2. **Young Adult** (20s): Someone sensitive to casual expressions and exposed to modern language on social media\n"
                "3. **General Consumer** (wide age range): Someone who reads ads and marketing materials from a general perspective\n\n"
                "Include name, background, age range, and reading context for each persona."
            ),
            "jp": (
                "以下の英語マーケティングテキストの日本語翻訳を評価するための3人のペルソナを生成してください:\n\n"
                "原文: {source_text}\n\n"
                "以下の3タイプの読者ペルソナを作成してください:\n"
                "1. **ビジネスプロフェッショナル** (30-40代): フォーマルなビジネス文書を日常的に読む人\n"
                "2. **若年層** (20代): カジュアルな表現に敏感で、SNSなどで最新の言葉遣いに触れている人\n"
                "3. **一般消費者** (幅広い年齢層): 広告やマーケティング資料を一般的な視点で読む人\n\n"
                "各ペルソナには名前、背景、年齢層、読書コンテキストを含めてください。"
            )
        },
        "impression_system": {
            "en": (
                "You are {persona_name}. {persona_background}\n"
                "Age range: {age_range}, Reading context: {reading_context}\n\n"
                "Evaluate the marketing translation as a reader."
            ),
            "jp": (
                "あなたは{persona_name}です。{persona_background}\n"
                "年齢層: {age_range}、読書コンテキスト: {reading_context}\n\n"
                "マーケティング翻訳文を読者として評価してください。"
            )
        },
        "impression_human": {
            "en": (
                "Source (English):\n{source_text}\n\n"
                "Translation (Japanese):\n{translated_text}\n\n"
                "From your perspective, about this translation:\n"
                "1. State your overall impression in 1-2 sentences\n"
                "2. List 1-3 things you think work well\n\n"
                "Respond in this JSON format:\n"
                '{{"impression": "Overall impression", "positives": ["Good point 1", "Good point 2"]}}'
            ),
            "jp": (
                "原文（英語）:\n{source_text}\n\n"
                "翻訳文（日本語）:\n{translated_text}\n\n"
                "この翻訳について、あなたの視点から:\n"
                "1. 全体的な印象を1-2文で述べてください\n"
                "2. 良いと思った点を1-3個挙げてください\n\n"
                "以下のJSON形式で回答してください:\n"
                '{{"impression": "全体的な印象", "positives": ["良い点1", "良い点2"]}}'
            )
        },
        "issues_system": {
            "en": (
                "You are {persona_name}. {persona_background}\n"
                "As a Japanese native speaker, identify unnatural parts in the translation."
            ),
            "jp": (
                "あなたは{persona_name}です。{persona_background}\n"
                "日本語ネイティブとして、翻訳文の不自然な箇所を特定してください。"
            )
        },
        "issues_human": {
            "en": (
                "Source (English):\n{source_text}\n\n"
                "Translation (Japanese):\n{translated_text}\n\n"
                "Find up to 3 unnatural parts and suggest improvements for each.\n"
                "Return an empty array if there are no problems.\n\n"
                "Respond in this JSON format:\n"
                "[\n"
                '  {{\n'
                '    "original_phrase": "Problematic phrase",\n'
                '    "issue_type": "unnatural_phrasing/awkward_word_choice/tone_mismatch/grammatical_error/cultural_inappropriateness",\n'
                '    "severity": "minor/moderate/major",\n'
                '    "explanation": "Why it is unnatural",\n'
                '    "suggested_rewrite": "More natural expression"\n'
                '  }}\n'
                "]"
            ),
            "jp": (
                "原文（英語）:\n{source_text}\n\n"
                "翻訳文（日本語）:\n{translated_text}\n\n"
                "不自然に感じる箇所を最大3つ見つけて、それぞれについて改善案を提案してください。\n"
                "問題がない場合は空の配列を返してください。\n\n"
                "以下のJSON形式で回答してください:\n"
                "[\n"
                '  {{\n'
                '    "original_phrase": "問題のあるフレーズ",\n'
                '    "issue_type": "unnatural_phrasing/awkward_word_choice/tone_mismatch/grammatical_error/cultural_inappropriateness",\n'
                '    "severity": "minor/moderate/major",\n'
                '    "explanation": "なぜ不自然か",\n'
                '    "suggested_rewrite": "より自然な表現"\n'
                '  }}\n'
                "]"
            )
        },
        "scores_system": {
            "en": "You are evaluating translation quality as {persona_name}.",
            "jp": "あなたは{persona_name}として翻訳品質を評価しています。"
        },
        "scores_human": {
            "en": (
                "Translation:\n{translated_text}\n\n"
                "Number of issues found: {issue_count}\n\n"
                "Score on the following criteria (1-10):\n"
                "- naturalness: Does it read like a native wrote it?\n"
                "- fluency: Is the flow smooth?\n"
                "- tone_appropriateness: Is the tone appropriate for marketing?\n"
                "- clarity: Is the meaning clear?\n\n"
                "JSON format: "
                '{{"naturalness": 8, "fluency": 7, "tone_appropriateness": 9, "clarity": 8}}'
            ),
            "jp": (
                "翻訳文:\n{translated_text}\n\n"
                "発見された問題数: {issue_count}\n\n"
                "以下の基準で1-10点で評価してください:\n"
                "- naturalness（自然さ）: ネイティブが書いたように読めるか\n"
                "- fluency（流暢さ）: 文章の流れがスムーズか\n"
                "- tone_appropriateness（トーンの適切さ）: マーケティング文として適切な調子か\n"
                "- clarity（明確さ）: 意味が明確に伝わるか\n\n"
                "JSON形式で回答: "
                '{{"naturalness": 8, "fluency": 7, "tone_appropriateness": 9, "clarity": 8}}'
            )
        },
    },

    # -------------------------------------------------------------------------
    # Sentence Evaluation Agent
    # -------------------------------------------------------------------------
    "sentence_evaluation": {
        "persona_generator_system": {
            "en": (
                "You are an expert at understanding communication contexts and creating relevant reviewer personas. "
                "Based on the given background, generate 3 diverse personas who would be ideal reviewers for this type of content."
            ),
            "jp": (
                "あなたはコミュニケーションの文脈を理解し、適切なレビュアーペルソナを作成する専門家です。"
                "与えられた背景に基づいて、このタイプのコンテンツの理想的なレビュアーとなる3人の多様なペルソナを生成してください。"
            )
        },
        "persona_generator_human": {
            "en": (
                "Background context:\n{background}\n\n"
                "Generate 3 distinct personas who should evaluate content written for this context. "
                "Each persona should have:\n"
                "- A realistic name\n"
                "- A relevant background that makes them a good evaluator\n"
                "- Their perspective (e.g., 'target audience member', 'skeptical decision-maker', 'busy executive')\n"
                "- What they focus on when evaluating (e.g., 'clarity and brevity', 'credibility and specifics', 'emotional appeal')\n"
                "- Why their feedback matters for this context\n\n"
                "Make the personas diverse - they should bring different viewpoints to the evaluation."
            ),
            "jp": (
                "背景コンテキスト:\n{background}\n\n"
                "この文脈で書かれたコンテンツを評価すべき3人の異なるペルソナを生成してください。"
                "各ペルソナには以下を含めてください:\n"
                "- 現実的な名前\n"
                "- 良い評価者となる関連性のある背景\n"
                "- 彼らの視点（例：「ターゲットオーディエンスのメンバー」「懐疑的な意思決定者」「多忙なエグゼクティブ」）\n"
                "- 評価時に重視すること（例：「明確さと簡潔さ」「信頼性と具体性」「感情的な訴求力」）\n"
                "- なぜ彼らのフィードバックがこの文脈で重要か\n\n"
                "ペルソナを多様にしてください - 評価に異なる視点をもたらすべきです。"
            )
        },
        "evaluation_system": {
            "en": (
                "You are {persona_name}, {persona_background}.\n"
                "Your perspective: {perspective}\n"
                "You focus on: {evaluation_focus}\n\n"
                "Evaluate the given sentence from your unique viewpoint."
            ),
            "jp": (
                "あなたは{persona_name}で、{persona_background}です。\n"
                "あなたの視点: {perspective}\n"
                "あなたが重視すること: {evaluation_focus}\n\n"
                "あなた独自の視点から与えられた文章を評価してください。"
            )
        },
        "evaluation_human": {
            "en": (
                "Context: {background}\n\n"
                "Sentence to evaluate:\n\"{sentence}\"\n\n"
                "Provide your evaluation in this JSON format:\n"
                '{{\n'
                '  "impression": "Your overall impression in 1-2 sentences",\n'
                '  "strengths": ["strength 1", "strength 2"],\n'
                '  "weaknesses": ["weakness 1", "weakness 2"]\n'
                '}}'
            ),
            "jp": (
                "コンテキスト: {background}\n\n"
                "評価する文章:\n「{sentence}」\n\n"
                "以下のJSON形式で評価を提供してください:\n"
                '{{\n'
                '  "impression": "1-2文での全体的な印象",\n'
                '  "strengths": ["強み1", "強み2"],\n'
                '  "weaknesses": ["弱み1", "弱み2"]\n'
                '}}'
            )
        },
        "scores_system": {
            "en": "You are {persona_name} evaluating a sentence. Based on your analysis, score the sentence.",
            "jp": "あなたは{persona_name}として文章を評価しています。分析に基づいて、文章を採点してください。"
        },
        "scores_human": {
            "en": (
                "Context: {background}\n"
                "Sentence: \"{sentence}\"\n\n"
                "Your evaluation found:\n"
                "Strengths: {strengths}\n"
                "Weaknesses: {weaknesses}\n\n"
                "Score the sentence on these criteria (1-10):\n"
                "- clarity: Is the meaning immediately understood?\n"
                "- impact: Does it grab attention / is it memorable?\n"
                "- tone: Does it match the intended voice for this context?\n"
                "- persuasiveness: Does it motivate the desired action?\n\n"
                "Respond with ONLY a JSON object: "
                '{{"clarity": 8, "impact": 7, "tone": 9, "persuasiveness": 6}}'
            ),
            "jp": (
                "コンテキスト: {background}\n"
                "文章: 「{sentence}」\n\n"
                "あなたの評価結果:\n"
                "強み: {strengths}\n"
                "弱み: {weaknesses}\n\n"
                "以下の基準で文章を採点してください（1-10）:\n"
                "- clarity（明確さ）: 意味がすぐに理解できるか？\n"
                "- impact（インパクト）: 注意を引くか / 記憶に残るか？\n"
                "- tone（トーン）: この文脈で意図された声に合っているか？\n"
                "- persuasiveness（説得力）: 望ましい行動を促すか？\n\n"
                "JSONオブジェクトのみで回答: "
                '{{"clarity": 8, "impact": 7, "tone": 9, "persuasiveness": 6}}'
            )
        },
        "recommendations_system": {
            "en": (
                "You are an expert copywriter and communication specialist. "
                "Based on the feedback from multiple reviewers, generate 3-5 actionable recommendations "
                "to improve the sentence. Each recommendation should be specific and practical."
            ),
            "jp": (
                "あなたは専門のコピーライターでありコミュニケーションスペシャリストです。"
                "複数のレビュアーからのフィードバックに基づいて、文章を改善するための"
                "3-5個の実行可能な推奨事項を生成してください。各推奨事項は具体的で実用的であるべきです。"
            )
        },
        "recommendations_human": {
            "en": (
                "Context: {background}\n\n"
                "Sentence being evaluated: \"{sentence}\"\n\n"
                "Identified weaknesses from reviewers:\n{weaknesses}\n\n"
                "Generate 3-5 specific, actionable recommendations to improve this sentence. "
                "Each recommendation should address one or more weaknesses and be immediately actionable. "
                "Respond with ONLY a JSON array of strings: [\"recommendation 1\", \"recommendation 2\", ...]"
            ),
            "jp": (
                "コンテキスト: {background}\n\n"
                "評価対象の文章: 「{sentence}」\n\n"
                "レビュアーから特定された弱み:\n{weaknesses}\n\n"
                "この文章を改善するための3-5個の具体的で実行可能な推奨事項を生成してください。"
                "各推奨事項は1つ以上の弱みに対処し、すぐに実行可能であるべきです。"
                "文字列のJSON配列のみで回答: [\"推奨事項1\", \"推奨事項2\", ...]"
            )
        },
    },
}


# =============================================================================
# LABELS - Report section headers and UI strings
# =============================================================================

LABELS = {
    # Common labels
    "research_outline": {"en": "Research Outline", "jp": "調査概要"},
    "topic": {"en": "Topic", "jp": "トピック"},
    "method": {"en": "Method", "jp": "評価方法"},
    "number_of_personas": {"en": "Number of Personas", "jp": "ペルソナ数"},
    "overall_score": {"en": "Overall Score", "jp": "総合スコア"},
    "generated_personas": {"en": "Generated Personas", "jp": "生成されたペルソナ"},
    "persona": {"en": "Persona", "jp": "ペルソナ"},
    "background": {"en": "Background", "jp": "背景"},
    "recommendations": {"en": "Recommendations", "jp": "改善提案"},
    "scores_summary": {"en": "Scores Summary", "jp": "スコアサマリー"},
    "avg": {"en": "Avg", "jp": "平均"},
    "criteria": {"en": "Criteria", "jp": "基準"},

    # User Interview Agent
    "user_interview_title": {"en": "User Interview", "jp": "ユーザーインタビュー"},
    "interview_method": {"en": "Persona-based User Interview Simulation", "jp": "ペルソナベースのユーザーインタビューシミュレーション"},
    "interview_details": {"en": "Interview Details", "jp": "インタビュー詳細"},
    "executive_summary": {"en": "Executive Summary", "jp": "エグゼクティブサマリー"},
    "quantitative_stats": {"en": "Quantitative Stats", "jp": "定量的統計"},
    "key_qualitative_insights": {"en": "Key Qualitative Insights", "jp": "主要な定性的インサイト"},
    "recommended_next_actions": {"en": "Recommended Next Actions", "jp": "推奨される次のアクション"},
    "report_saved_interview": {"en": "User interview report saved to '{path}'.", "jp": "ユーザーインタビューのレポートが '{path}' に保存されました。"},

    # SEO Search Intent Evaluation Agent
    "seo_eval_title": {"en": "SEO Search Intent Evaluation Report", "jp": "SEO検索意図評価レポート"},
    "target_keyword": {"en": "Target Keyword", "jp": "ターゲットキーワード"},
    "content_under_evaluation": {"en": "Content Under Evaluation", "jp": "評価対象コンテンツ"},
    "evaluation_method_seo": {"en": "Search Intent Persona Analysis", "jp": "検索意図ペルソナ分析"},
    "personas_generated": {"en": "Personas Generated", "jp": "生成されたペルソナ"},
    "search_query": {"en": "Search Query", "jp": "検索クエリ"},
    "looking_for": {"en": "Looking for", "jp": "探している情報"},
    "evaluation_dialogues": {"en": "Evaluation Dialogues", "jp": "評価対話"},
    "satisfied": {"en": "satisfied", "jp": "満足"},
    "not_satisfied": {"en": "NOT satisfied", "jp": "不満"},
    "intent_informational": {"en": "Informational", "jp": "情報収集型"},
    "intent_navigational": {"en": "Navigational/Comparative", "jp": "比較検討型"},
    "intent_transactional": {"en": "Transactional", "jp": "取引型"},
    "relevance": {"en": "Relevance", "jp": "関連性"},
    "clarity": {"en": "Clarity", "jp": "明確さ"},
    "completeness": {"en": "Completeness", "jp": "完全性"},
    "persuasiveness": {"en": "Persuasiveness", "jp": "説得力"},
    "report_saved_seo": {"en": "Evaluation report saved to '{path}'", "jp": "評価レポートが '{path}' に保存されました。"},

    # Translation Evaluation Agent
    "translation_eval_title": {"en": "Translation Evaluation Report", "jp": "翻訳評価レポート"},
    "source_text": {"en": "Source (English)", "jp": "原文（英語）"},
    "translated_text": {"en": "Translation (Japanese)", "jp": "翻訳文（日本語）"},
    "evaluation_method_translation": {"en": "Reader Perspective Persona Analysis", "jp": "読者視点ペルソナ分析"},
    "evaluation_personas": {"en": "Evaluation Personas", "jp": "評価ペルソナ"},
    "age_range": {"en": "Age Range", "jp": "年齢層"},
    "reading_context": {"en": "Reading Context", "jp": "読書コンテキスト"},
    "evaluation_details": {"en": "Evaluation Details", "jp": "評価詳細"},
    "overall_impression": {"en": "Overall Impression", "jp": "全体的な印象"},
    "positive_points": {"en": "Positive Points", "jp": "良い点"},
    "issues_found": {"en": "Issues Found", "jp": "指摘事項"},
    "no_issues": {"en": "None (natural translation)", "jp": "なし（自然な翻訳です）"},
    "naturalness": {"en": "Naturalness", "jp": "自然さ"},
    "fluency": {"en": "Fluency", "jp": "流暢さ"},
    "tone_appropriateness": {"en": "Tone Appropriateness", "jp": "トーン適切さ"},
    "improvement_summary": {"en": "Improvement Summary", "jp": "改善提案まとめ"},
    "no_improvements_needed": {"en": "No improvements needed. Translation quality is good.", "jp": "改善が必要な箇所はありません。翻訳品質は良好です。"},
    "report_saved_translation": {"en": "Translation evaluation report saved to '{path}'.", "jp": "翻訳評価レポートが '{path}' に保存されました。"},

    # Sentence Evaluation Agent
    "sentence_eval_title": {"en": "Sentence Evaluation Report", "jp": "文章評価レポート"},
    "evaluation_context": {"en": "Evaluation Context", "jp": "評価コンテキスト"},
    "sentence": {"en": "Sentence", "jp": "文章"},
    "focus": {"en": "Focus", "jp": "重視点"},
    "relevance_reason": {"en": "Relevance", "jp": "関連性"},
    "strengths": {"en": "Strengths", "jp": "強み"},
    "weaknesses": {"en": "Weaknesses", "jp": "弱み"},
    "impact": {"en": "Impact", "jp": "インパクト"},
    "tone": {"en": "Tone", "jp": "トーン"},
    "no_recommendations": {"en": "No specific improvements needed based on the evaluation.", "jp": "評価に基づいて具体的な改善は必要ありません。"},
    "report_saved_sentence": {"en": "Sentence evaluation report saved to '{path}'", "jp": "文章評価レポートが '{path}' に保存されました。"},

    # Severity labels for translation issues
    "severity_minor": {"en": "minor", "jp": "軽度"},
    "severity_moderate": {"en": "moderate", "jp": "中度"},
    "severity_major": {"en": "major", "jp": "重度"},
}


# =============================================================================
# Helper Functions
# =============================================================================

def t(key: str, lang: LanguageCode) -> str:
    """
    Get translated label by key.

    Args:
        key: Label key from LABELS dict
        lang: Language code ('en' or 'jp')

    Returns:
        Translated string

    Example:
        >>> t('research_outline', 'jp')
        '調査概要'
    """
    if key not in LABELS:
        return key  # Return key itself if not found
    return LABELS[key].get(lang, LABELS[key].get("en", key))


def p(agent: str, prompt_key: str, lang: LanguageCode) -> str:
    """
    Get translated prompt by agent and key.

    Args:
        agent: Agent name (e.g., 'user_interview', 'seo_evaluation')
        prompt_key: Prompt key within the agent
        lang: Language code ('en' or 'jp')

    Returns:
        Translated prompt string

    Example:
        >>> p('user_interview', 'persona_generator_system', 'jp')
        'あなたはユーザーインタビュー用の多様なペルソナを作成する専門家です。'
    """
    if agent not in PROMPTS:
        return f"[Missing agent: {agent}]"
    if prompt_key not in PROMPTS[agent]:
        return f"[Missing prompt: {agent}.{prompt_key}]"
    return PROMPTS[agent][prompt_key].get(lang, PROMPTS[agent][prompt_key].get("en", ""))
