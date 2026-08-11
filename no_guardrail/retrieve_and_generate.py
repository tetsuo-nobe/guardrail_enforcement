"""
Amazon Bedrock RetrieveAndGenerate API でナレッジベースを使用するサンプルコード

ガードレールをコードで指定しないバージョン。
RetrieveAndGenerate API では guardrailConfiguration を指定しない場合、
アカウントレベル enforcement のガードレールは適用されない。
（bedrock-runtime の InvokeModel / Converse とは異なる動作）

前提条件:
- boto3, python-dotenv がインストール済み
- AWS 認証情報が設定済み (AWS CLI の configure、環境変数、または IAM ロール)
- Amazon Bedrock で Claude Haiku 4.5 モデルへのアクセスが有効化済み
- ナレッジベースが作成・同期済み
- .env に KNOWLEDGE_BASE_ID を設定済み
- enforcement 設定で Embed モデルを excluded_models に追加済み

注意:
- RetrieveAndGenerate API は bedrock-agent-runtime エンドポイントを使用する
- このサンプルでは guardrailConfiguration を指定していないため、
  enforcement ガードレールは適用されない（有害プロンプトもブロックされない）
- enforcement を含むガードレールを適用するには apply_guardrail/ 版を使用する
"""

import os

import boto3
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()

# ナレッジベースの設定（.env から読み込み）
KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID")

# 生成に使用するモデル ARN
# RetrieveAndGenerate API ではクロスリージョン推論プロファイルの ARN を指定する
# アカウント ID は STS から動的に取得
_sts_client = boto3.client("sts")
_account_id = _sts_client.get_caller_identity()["Account"]
MODEL_ARN = f"arn:aws:bedrock:us-east-1:{_account_id}:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0"


def retrieve_and_generate(query: str) -> str:
    """
    ナレッジベースから情報を検索し、回答を生成する。

    RetrieveAndGenerate API は以下を一括で実行する：
    1. ナレッジベースからクエリに関連するドキュメントを検索（Retrieve）
    2. 検索結果をコンテキストとしてモデルに渡し、回答を生成（Generate）

    ガードレールはコードで指定しないが、アカウントレベル enforcement が
    設定されている場合は自動的に適用される。

    Args:
        query: ナレッジベースに対するクエリ

    Returns:
        生成された回答テキスト
    """
    # bedrock-agent-runtime クライアントを作成（リージョン: us-east-1）
    client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

    # RetrieveAndGenerate API を呼び出し（ガードレール指定なし）
    response = client.retrieve_and_generate(
        input={
            "text": query,
        },
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelArn": MODEL_ARN,
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

    return output_text


if __name__ == "__main__":
    # サンプルプロンプト（ナレッジベースの内容に応じて変更してください）
    user_prompt1 = "ナレッジベースに格納されたドキュメントの内容を要約してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"

    print(f"プロンプト: {user_prompt2}")
    print("-" * 50)

    result = retrieve_and_generate(user_prompt2)
    print(f"\n応答:\n{result}")
