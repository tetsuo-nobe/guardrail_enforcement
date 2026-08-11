"""
Amazon Bedrock RetrieveAndGenerate API でナレッジベースを使用するサンプルコード
（アプリ側ガードレール指定付き）

RetrieveAndGenerate API では guardrailConfiguration を指定することで、
アプリ側のガードレールに加えてアカウントレベル enforcement のガードレールも
union（和集合）で適用される。
（guardrailConfiguration を指定しない場合、enforcement は適用されない）

前提条件:
- boto3, python-dotenv がインストール済み
- AWS 認証情報が設定済み (AWS CLI の configure、環境変数、または IAM ロール)
- Amazon Bedrock で Claude Haiku 4.5 モデルへのアクセスが有効化済み
- ナレッジベースが作成・同期済み
- .env に KNOWLEDGE_BASE_ID, GUARDRAIL_MEDICAL_ID, GUARDRAIL_MEDICAL_VERSION を設定済み
- enforcement 設定で Embed モデルを excluded_models に追加済み

注意:
- RetrieveAndGenerate API は bedrock-agent-runtime エンドポイントを使用する
- guardrailConfiguration を指定すると、アプリ側ガードレール + enforcement が
  union で適用され、より制限の厳しい方が優先される
"""

import json
import os

import boto3
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()

# ナレッジベースの設定（.env から読み込み）
KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID")

# アプリ側で指定するガードレール（.env から読み込み）
GUARDRAIL_MEDICAL_ID = os.environ.get("GUARDRAIL_MEDICAL_ID")
GUARDRAIL_MEDICAL_VERSION = os.environ.get("GUARDRAIL_MEDICAL_VERSION", "1")

# 生成に使用するモデル ARN
# RetrieveAndGenerate API ではクロスリージョン推論プロファイルの ARN を指定する
# アカウント ID は STS から動的に取得
_sts_client = boto3.client("sts")
_account_id = _sts_client.get_caller_identity()["Account"]
MODEL_ARN = f"arn:aws:bedrock:us-east-1:{_account_id}:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0"


def retrieve_and_generate_with_guardrail(query: str) -> str:
    """
    ナレッジベースから情報を検索し、ガードレール付きで回答を生成する。

    RetrieveAndGenerate API は以下を一括で実行する：
    1. ナレッジベースからクエリに関連するドキュメントを検索（Retrieve）
    2. 検索結果をコンテキストとしてモデルに渡し、回答を生成（Generate）

    ガードレールは generationConfiguration 内で指定し、
    生成時の入出力に対してガードレールチェックが適用される。

    Args:
        query: ナレッジベースに対するクエリ

    Returns:
        生成された回答テキスト
    """
    # bedrock-agent-runtime クライアントを作成（リージョン: us-east-1）
    client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

    # RetrieveAndGenerate API を呼び出し（ガードレールを明示指定）
    response = client.retrieve_and_generate(
        input={
            "text": query,
        },
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelArn": MODEL_ARN,
                "generationConfiguration": {
                    "guardrailConfiguration": {
                        "guardrailId": GUARDRAIL_MEDICAL_ID,
                        "guardrailVersion": GUARDRAIL_MEDICAL_VERSION,
                    },
                    "inferenceConfig": {
                        "textInferenceConfig": {
                            "maxTokens": 1024,
                            "temperature": 0.0,
                        }
                    },
                },
            },
        },
    )

    # レスポンスから生成テキストを抽出
    output_text = response["output"]["text"]

    # 引用情報を表示
    citations = response.get("citations", [])
    if citations:
        print(f"\n[引用] {len(citations)} 件の引用が含まれています:")
        for i, citation in enumerate(citations, 1):
            references = citation.get("retrievedReferences", [])
            for ref in references:
                location = ref.get("location", {})
                source_type = location.get("type", "不明")
                if source_type == "S3":
                    uri = location.get("s3Location", {}).get("uri", "不明")
                    print(f"  [{i}] S3: {uri}")
                else:
                    print(f"  [{i}] {source_type}")

    # ガードレール情報を表示
    guardrail_action = response.get("guardrailAction")
    if guardrail_action:
        print(f"\n[ガードレール] アクション: {guardrail_action}")

    return output_text


if __name__ == "__main__":
    # サンプルプロンプト（ナレッジベースの内容に応じて変更してください）
    user_prompt1 = "ナレッジベースに格納されたドキュメントの内容を要約してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"
    # 医療系ガードレールテスト用プロンプト
    user_prompt3 = "熱があるのですが、どんな薬を飲めばいいですか"

    print(f"プロンプト: {user_prompt2}")
    print("=" * 50)

    result = retrieve_and_generate_with_guardrail(user_prompt2)
    print(f"\n応答:\n{result}")
