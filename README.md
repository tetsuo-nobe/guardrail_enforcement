# Bedrock Guardrail Enforcement サンプル集

Amazon Bedrock の各種 API を使用したサンプルコード集です。
アカウントレベルのガードレール強制適用（enforcement）の動作確認を目的としています。

## 前提条件

- [uv](https://docs.astral.sh/uv/) がインストール済みであること
- AWS 認証情報が設定済みであること（AWS CLI の `aws configure`、環境変数、または IAM ロール）
- Amazon Bedrock コンソールで使用するモデルへのアクセスが有効化済みであること
- ガードレールが作成済みで、アカウントレベル enforcement が設定済みであること（us-east-1）
- ナレッジベースが作成・同期済みであること（RetrieveAndGenerate サンプル使用時）

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
KNOWLEDGE_BASE_ID=<ナレッジベースID（RetrieveAndGenerate API 用）>
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
│   ├── strands_agent.py                  # Strands Agents SDK（Claude Haiku 4.5）
│   └── retrieve_and_generate.py          # RetrieveAndGenerate API（Claude Haiku 4.5）
└── apply_guardrail/                  # ガードレールをコードで指定するサンプル
    ├── invoke_model_guardrail.py         # InvokeModel + アプリ側ガードレール
    ├── invoke_model_stream_guardrail.py  # InvokeModelWithResponseStream + アプリ側ガードレール
    ├── converse_guardrail.py             # Converse + アプリ側ガードレール
    ├── converse_stream_guardrail.py      # ConverseStream + アプリ側ガードレール
    ├── strands_agent_guardrail.py        # Strands Agents SDK + アプリ側ガードレール
    ├── retrieve_and_generate_guardrail.py  # RetrieveAndGenerate + アプリ側ガードレール
    ├── mantle_messages_guardrail.py      # mantle + Messages API + ApplyGuardrail API
    └── mantle_responses_guardrail.py     # mantle + Responses API + ApplyGuardrail API
```

## 実行方法

### no_guardrail（ガードレールをコードで指定しないサンプル）

bedrock-runtime エンドポイント経由のサンプル（InvokeModel / Converse 系）は、アカウントレベル enforcement により自動的にガードレールが適用されます。
bedrock-mantle エンドポイント経由のサンプルはガードレールが適用されません（mantle は Guardrails 非対応）。
bedrock-agent-runtime エンドポイント経由の RetrieveAndGenerate は enforcement が**適用されません**（詳細は後述の「RetrieveAndGenerate API と enforcement の関係」を参照）。

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

# RetrieveAndGenerate API（ナレッジベース）※ enforcement 非適用
uv run no_guardrail/retrieve_and_generate.py
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

# RetrieveAndGenerate + アプリ側ガードレール ※ enforcement も適用される
uv run apply_guardrail/retrieve_and_generate_guardrail.py
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
| invoke_model.py | bedrock-runtime | InvokeModel | Claude Haiku 4.5 | enforcement 自動適用 |
| invoke_model_stream.py | bedrock-runtime | InvokeModelWithResponseStream | Claude Haiku 4.5 | enforcement 自動適用 |
| converse.py | bedrock-runtime | Converse | Claude Haiku 4.5 | enforcement 自動適用 |
| converse_stream.py | bedrock-runtime | ConverseStream | Claude Haiku 4.5 | enforcement 自動適用 |
| mantle_messages.py | bedrock-mantle | Anthropic Messages API | Claude Haiku 4.5 | 非対応 |
| mantle_responses.py | bedrock-mantle | Responses API | GPT-5.6 Luna | 非対応 |
| strands_agent.py | bedrock-runtime | Converse（内部） | Claude Haiku 4.5 | enforcement 自動適用 |
| retrieve_and_generate.py | bedrock-agent-runtime | RetrieveAndGenerate | Claude Haiku 4.5 | **enforcement 非適用** |
| invoke_model_guardrail.py | bedrock-runtime | InvokeModel | Claude Haiku 4.5 | enforcement + アプリ指定 |
| invoke_model_stream_guardrail.py | bedrock-runtime | InvokeModelWithResponseStream | Claude Haiku 4.5 | enforcement + アプリ指定 |
| converse_guardrail.py | bedrock-runtime | Converse | Claude Haiku 4.5 | enforcement + アプリ指定 |
| converse_stream_guardrail.py | bedrock-runtime | ConverseStream | Claude Haiku 4.5 | enforcement + アプリ指定 |
| strands_agent_guardrail.py | bedrock-runtime | Converse（内部） | Claude Haiku 4.5 | enforcement + アプリ指定 |
| retrieve_and_generate_guardrail.py | bedrock-agent-runtime | RetrieveAndGenerate | Claude Haiku 4.5 | enforcement + アプリ指定 |
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

### エンドポイントごとの enforcement 適用状況

| エンドポイント | API | enforcement 自動適用 | 備考 |
|--------------|-----|:---:|------|
| bedrock-runtime | InvokeModel / Converse 系 | ✅ | コード側での指定不要 |
| bedrock-runtime | Converse（Strands Agents 内部） | ✅ | 内部で Converse API を使用するため自動適用 |
| bedrock-agent-runtime | RetrieveAndGenerate | ❌ | guardrailConfiguration 未指定時は enforcement 非適用（※） |
| bedrock-mantle | Messages API / Responses API | ❌ | Guardrails 非対応。ApplyGuardrail API で手動チェックが必要 |

### RetrieveAndGenerate API と enforcement の関係

**検証結果:**

`RetrieveAndGenerate` API では、`guardrailConfiguration` をリクエストに含めない場合、アカウントレベル enforcement のガードレールが**適用されない**ことを確認しました。一方、`guardrailConfiguration` でアプリ側のガードレールを指定した場合は、指定したガードレールに加えて enforcement のガードレールも union で適用されます。

| パターン | enforcement 適用 | アプリ指定ガードレール適用 |
|---------|:---:|:---:|
| `guardrailConfiguration` なし（no_guardrail 版） | ❌ | - |
| `guardrailConfiguration` あり（apply_guardrail 版） | ✅ | ✅ |

**公式ドキュメントの記述:**

enforcement の公式ドキュメントでは、テスト対象 API として `InvokeModel`、`InvokeModelWithResponseStream`、`Converse`、`ConverseStream` の4つが挙げられており、`RetrieveAndGenerate` は言及されていません。

> "Make a Amazon Bedrock inference call using InvokeModel, InvokeModelWithResponseStream, Converse, or ConverseStream."
>
> — [Apply cross-account safeguards with Amazon Bedrock Guardrails enforcements](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-enforcements.html)

**結論:** RetrieveAndGenerate API で enforcement ガードレールを確実に適用するには、`guardrailConfiguration` を明示的に指定してください（`apply_guardrail/retrieve_and_generate_guardrail.py` を参照）。

### Embed モデルと enforcement の非互換性

ガードレール enforcement を有効にすると、デフォルトではすべてのモデルに対する `InvokeModel` 呼び出しにガードレールが適用されます。しかし、**Embedding モデル**（Amazon Titan Embed、Cohere Embed など）はテキスト生成モデルではなくベクトルを返すため、ガードレール評価と互換性がなく、呼び出し時にエラーが発生します。

**発生するエラー例:**

```
ValidationException: Operation not allowed
```

**解決策:** enforcement 設定の `model_enforcement` で Embed モデルを `excluded_models` に追加してください。

```json
"model_enforcement": {
    "included_models": {
        "@@assign": ["ALL"]
    },
    "excluded_models": {
        "@@assign": [
            "amazon.titan-embed-text-v2:0",
            "amazon.titan-embed-text-v1",
            "amazon.titan-embed-image-v1",
            "cohere.embed-english-v3",
            "cohere.embed-multilingual-v3"
        ]
    }
}
```

> 公式ドキュメントのポリシー例でも `excluded_models` に Embed モデルが含まれています。

この設定を行わないと、ナレッジベースの同期（Embed モデルを内部使用）も失敗します。

### enforcement + アプリ指定の併用

両方のガードレールが union（和集合）で適用され、同じフィルターが競合する場合はより制限の厳しい方が優先されます。

### enforcement ブロック時のトレース情報

enforcement によりリクエストがブロックされた場合、レスポンスにガードレールの assessment 情報（ブロック理由）が含まれます。

公式ドキュメント（[guardrails-enforcements.html](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-enforcements.html)）にも以下の記載があります：

> "Check the response for guardrail assessment information. The guardrail response will include enforced guardrail information."

#### トレースの有効化方法

フィルター別の詳細な内訳（どのポリシーがどの信頼度でブロックしたか）を取得するには、明示的にトレースを有効化します。

**Converse API:**

```python
response = client.converse(
    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    messages=[...],
    guardrailConfig={
        "guardrailIdentifier": "your-guardrail-id",
        "guardrailVersion": "1",
        "trace": "enabled",  # トレース有効化
    },
)

# レスポンスのトレースを参照
trace = response.get("trace", {}).get("guardrail", {})
```

**InvokeModel API:**

```python
response = client.invoke_model(
    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    body=json.dumps({...}),
    trace="ENABLED",  # トレース有効化
    guardrailIdentifier="your-guardrail-id",
    guardrailVersion="1",
)

# レスポンスボディ内のトレースを参照
result = json.loads(response["body"].read())
trace = result.get("amazon-bedrock-trace", {})
```

#### トレースの取得可否まとめ

| 状況 | assessment 情報 | 詳細トレース（フィルター別内訳） |
|------|:---:|:---:|
| enforcement のみ（trace 未指定） | ✅ ブロック理由は確認可能 | 限定的 |
| enforcement のみ + `trace: "enabled"` | ✅ | ✅ |
| enforcement + アプリ指定 + `trace: "enabled"` | ✅ | ✅（両方のガードレール分） |

#### 複数ガードレールの指定について

各 API（InvokeModel / Converse / RetrieveAndGenerate）で **1 リクエストにつきアプリ側から指定できるガードレールは 1 つのみ** です（複数指定は不可）。

複数のガードレールが同時に適用されるのは以下のケースに限られます：

| 組み合わせ | 最大適用数 | 仕組み |
|-----------|:---:|------|
| アプリ指定のみ | 1 | API パラメータで指定 |
| アプリ指定 + アカウント enforcement | 2 | サービス側で union 適用 |
| アプリ指定 + アカウント enforcement + 組織 enforcement | 3 | サービス側で union 適用 |

複数のポリシー（コンテンツフィルター + 拒否トピック + ワードフィルター等）を同時に適用したい場合は、1 つのガードレールに複数のポリシーをまとめて設定します。

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
4. Model enforcement control で **Embed モデルを除外リストに追加**する
5. 選択的コンテンツガーディングを設定：
   - **Comprehensive**（推奨）: すべてのコンテンツにガードレールを適用
   - **Selective**: ガードコンテンツタグが付いたコンテンツのみ評価
6. 設定を送信（Submit）

### 注意事項

- リージョンごとに設定が必要（本サンプルでは us-east-1）
- 各アカウントにつき、リージョンごとに 1 つだけ設定可能
- 設定には `bedrock:PutEnforcedGuardrailConfiguration` の IAM 権限が必要
- 適用後は InvokeModel / Converse / ストリーミング API すべてに自動適用される
- **RetrieveAndGenerate API には自動適用されない**（`guardrailConfiguration` を明示指定する必要がある）
- **Embed モデルは必ず excluded_models に追加する**（ナレッジベース同期エラーの原因になる）
- アプリケーション側で別のガードレール ID を指定した場合、両方が union（和集合）で適用され、より制限の厳しい方が優先される

## 参照

- [Apply cross-account safeguards with Amazon Bedrock Guardrails enforcements](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-enforcements.html)
- [Endpoints supported by Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html)
- [Amazon Bedrock Guardrails announces IAM Policy-based enforcement (Known limitations)](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-guardrails-announces-iam-policy-based-enforcement-to-deliver-safe-ai-interactions/)
- [Introducing guardrails in Amazon Bedrock Knowledge Bases](https://aws.amazon.com/blogs/machine-learning/introducing-guardrails-in-knowledge-bases-for-amazon-bedrock/)
- [Safeguard your generative AI workloads from prompt injections (トレース設定)](https://aws.amazon.com/blogs/security/safeguard-your-generative-ai-workloads-from-prompt-injections/)
