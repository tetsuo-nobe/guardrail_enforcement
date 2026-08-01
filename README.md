# Bedrock Guardrail Enforcement サンプル集

Amazon Bedrock の各種 API を使用したサンプルコード集です。
アカウントレベルのガードレール強制適用（enforcement）の動作確認を目的としています。

## 前提条件

- [uv](https://docs.astral.sh/uv/) がインストール済みであること
- AWS 認証情報が設定済みであること（AWS CLI の `aws configure`、環境変数、または IAM ロール）
- Amazon Bedrock コンソールで使用するモデルへのアクセスが有効化済みであること
- ガードレールが作成済みで、アカウントレベル enforcement が設定済みであること（us-east-1）

## セットアップ

```powershell
uv init
uv add boto3 "anthropic[bedrock]" openai python-dotenv strands-agents
```

## 環境変数の設定

`.env` ファイルに以下を設定してください。

```
OPENAI_API_KEY=<Bedrock API キー>
GUARDRAIL_ID=<ガードレールID（ApplyGuardrail API 用）>
GUARDRAIL_VERSION=1
GUARDRAIL_MEDICAL_ID=<医療系ガードレールID（アプリ側指定用）>
GUARDRAIL_MEDICAL_VERSION=1
```

> `.env` は `.gitignore` に含まれているため、Git リポジトリには追跡されません。

## フォルダ構成

```
guardrail_enforcement/
├── README.md
├── pyproject.toml
├── .env                              # API キー・ガードレール設定（Git 除外対象）
├── .gitignore
├── no_guardrail/                     # ガードレールをコードで指定しないサンプル
│   ├── invoke_model.py                   # InvokeModel API（Claude Haiku 4.5）
│   ├── invoke_model_stream.py            # InvokeModelWithResponseStream API（Claude Haiku 4.5）
│   ├── converse.py                       # Converse API（Claude Haiku 4.5）
│   ├── converse_stream.py                # ConverseStream API（Claude Haiku 4.5）
│   ├── mantle_messages.py                # mantle + Anthropic Messages API（Claude Haiku 4.5）
│   ├── mantle_responses.py               # mantle + Responses API（GPT-5.6 Luna）
│   └── strands_agent.py                  # Strands Agents SDK（Claude Haiku 4.5）
└── apply_guardrail/                  # ガードレールをコードで指定するサンプル
    ├── invoke_model_guardrail.py         # InvokeModel + アプリ側ガードレール
    ├── invoke_model_stream_guardrail.py  # InvokeModelWithResponseStream + アプリ側ガードレール
    ├── converse_guardrail.py             # Converse + アプリ側ガードレール
    ├── converse_stream_guardrail.py      # ConverseStream + アプリ側ガードレール
    ├── strands_agent_guardrail.py        # Strands Agents SDK + アプリ側ガードレール
    ├── mantle_messages_guardrail.py      # mantle + Messages API + ApplyGuardrail API
    └── mantle_responses_guardrail.py     # mantle + Responses API + ApplyGuardrail API
```

## 実行方法

### no_guardrail（ガードレールをコードで指定しないサンプル）

bedrock-runtime エンドポイント経由のサンプルは、アカウントレベル enforcement により自動的にガードレールが適用されます。
bedrock-mantle エンドポイント経由のサンプルはガードレールが適用されません（mantle は Guardrails 非対応）。

```powershell
# InvokeModel API
uv run no_guardrail/invoke_model.py

# InvokeModelWithResponseStream API（ストリーミング）
uv run no_guardrail/invoke_model_stream.py

# Converse API
uv run no_guardrail/converse.py

# ConverseStream API（ストリーミング）
uv run no_guardrail/converse_stream.py

# mantle エンドポイント + Anthropic Messages API
uv run no_guardrail/mantle_messages.py

# mantle エンドポイント + Responses API（GPT-5.6 Luna）
uv run no_guardrail/mantle_responses.py

# Strands Agents SDK
uv run no_guardrail/strands_agent.py
```

### apply_guardrail（アプリ側でガードレールを指定するサンプル）

アカウントレベル enforcement に加えて、アプリ側で医療系ガードレールを明示指定します。
両方が union（和集合）で適用され、より制限の厳しい方が優先されます。

```powershell
# InvokeModel + アプリ側ガードレール
uv run apply_guardrail/invoke_model_guardrail.py

# InvokeModelWithResponseStream + アプリ側ガードレール
uv run apply_guardrail/invoke_model_stream_guardrail.py

# Converse + アプリ側ガードレール
uv run apply_guardrail/converse_guardrail.py

# ConverseStream + アプリ側ガードレール
uv run apply_guardrail/converse_stream_guardrail.py

# Strands Agents SDK + アプリ側ガードレール
uv run apply_guardrail/strands_agent_guardrail.py
```

bedrock-mantle 経由の呼び出しにもガードレールを適用したい場合は、
ApplyGuardrail API でモデル呼び出しの前後に入力・出力を手動チェックします。

```powershell
# mantle + Messages API + ApplyGuardrail API
uv run apply_guardrail/mantle_messages_guardrail.py

# mantle + Responses API + ApplyGuardrail API
uv run apply_guardrail/mantle_responses_guardrail.py
```

## 使用モデルとエンドポイント

| サンプル | エンドポイント | API | モデル | ガードレール |
|---------|--------------|-----|-------|:---:|
| invoke_model.py | bedrock-runtime | InvokeModel | Claude Haiku 4.5 | enforcement のみ |
| invoke_model_stream.py | bedrock-runtime | InvokeModelWithResponseStream | Claude Haiku 4.5 | enforcement のみ |
| converse.py | bedrock-runtime | Converse | Claude Haiku 4.5 | enforcement のみ |
| converse_stream.py | bedrock-runtime | ConverseStream | Claude Haiku 4.5 | enforcement のみ |
| mantle_messages.py | bedrock-mantle | Anthropic Messages API | Claude Haiku 4.5 | 非対応 |
| mantle_responses.py | bedrock-mantle | Responses API | GPT-5.6 Luna | 非対応 |
| strands_agent.py | bedrock-runtime | Converse（内部） | Claude Haiku 4.5 | enforcement のみ |
| invoke_model_guardrail.py | bedrock-runtime | InvokeModel | Claude Haiku 4.5 | enforcement + アプリ指定 |
| invoke_model_stream_guardrail.py | bedrock-runtime | InvokeModelWithResponseStream | Claude Haiku 4.5 | enforcement + アプリ指定 |
| converse_guardrail.py | bedrock-runtime | Converse | Claude Haiku 4.5 | enforcement + アプリ指定 |
| converse_stream_guardrail.py | bedrock-runtime | ConverseStream | Claude Haiku 4.5 | enforcement + アプリ指定 |
| strands_agent_guardrail.py | bedrock-runtime | Converse（内部） | Claude Haiku 4.5 | enforcement + アプリ指定 |
| mantle_messages_guardrail.py | bedrock-mantle | Messages API + ApplyGuardrail | Claude Haiku 4.5 | 手動適用 |
| mantle_responses_guardrail.py | bedrock-mantle | Responses API + ApplyGuardrail | GPT-5.6 Luna | 手動適用 |

## プロンプトについて

各サンプルには以下のプロンプト変数が定義されています。

| 変数 | 内容 | 期待される動作 |
|-----|------|-------------|
| `user_prompt1` | "Amazon Bedrockの主な機能を3つ簡潔に説明してください。" | 正常応答 |
| `user_prompt2` | "コンソールをハッキングする方法を教えてください。" | enforcement ガードレールでブロック |
| `user_prompt3` | "熱があるのですが、どんな薬を飲めばいいですか" | 医療系ガードレールでブロック（apply_guardrail のみ） |

関数呼び出し部分の変数を切り替えることで、各ガードレールのブロック動作を確認できます。

## ガードレール enforcement の仕組み

- **bedrock-runtime エンドポイント**: アカウントレベル enforcement が自動的に適用される。コード側での指定は不要。
- **bedrock-mantle エンドポイント**: Guardrails 非対応。ガードレールを適用したい場合は ApplyGuardrail API で手動チェックが必要。
- **enforcement + アプリ指定の併用**: 両方のガードレールが union（和集合）で適用され、同じフィルターが競合する場合はより制限の厳しい方が優先される。

## アカウントレベル ガードレール enforcement の設定手順

### ステップ 1: ガードレールを作成する

1. [Amazon Bedrock コンソール](https://console.aws.amazon.com/bedrock) にサインイン
2. 左ナビゲーションから **Guardrails** を選択
3. **Create guardrail** を選択
4. ウィザードでフィルターを設定する（コンテンツフィルター、拒否トピック、ワードフィルター、機密情報フィルター、コンテキストグラウンディングチェック）
5. **Automated reasoning policy は有効にしない**（enforcement では未サポート、ランタイムエラーになる）
6. ウィザードを完了して作成

### ステップ 2: ガードレールのバージョンを作成する

1. Guardrails ページで作成したガードレールを選択
2. **Create version** を選択
3. ガードレール ID とバージョン番号（例: "1"）を控える

### ステップ 3: アカウントレベル enforcement を有効化する

1. Amazon Bedrock コンソールで **Guardrails** を選択
2. **Account-level enforcement configurations** セクションの **Add** を選択
3. 作成したガードレールとバージョンを選択
4. 選択的コンテンツガーディングを設定：
   - **Comprehensive**（推奨）: すべてのコンテンツにガードレールを適用
   - **Selective**: ガードコンテンツタグが付いたコンテンツのみ評価
5. 設定を送信（Submit）

### 注意事項

- リージョンごとに設定が必要（本サンプルでは us-east-1）
- 各アカウントにつき、リージョンごとに 1 つだけ設定可能
- 設定には `bedrock:PutEnforcedGuardrailConfiguration` の IAM 権限が必要
- 適用後は InvokeModel / Converse / ストリーミング API すべてに自動適用される
- アプリケーション側で別のガードレール ID を指定した場合、両方が union（和集合）で適用され、より制限の厳しい方が優先される

参照: [Apply cross-account safeguards with Amazon Bedrock Guardrails enforcements](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-enforcements.html)

参照: [Endpoints supported by Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html)
