"""
Amazon Bedrock InvokeModel API でアプリ側ガードレールを明示指定するサンプルコード

アカウントレベルの enforcement ガードレールに加えて、
アプリ側で別のガードレール（医療系）を指定し、両方が union で適用されることを確認する。

前提条件:
- boto3, python-dotenv がインストール済み
- AWS 認証情報が設定済み (AWS CLI の configure、環境変数、または IAM ロール)
- Amazon Bedrock で Claude Haiku 4.5 モデルへのアクセスが有効化済み
- .env に GUARDRAIL_MEDICAL_ID と GUARDRAIL_MEDICAL_VERSION を設定済み
"""

import json
import os

import boto3
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()

# アプリ側で指定するガードレール（.env から読み込み）
GUARDRAIL_MEDICAL_ID = os.environ.get("GUARDRAIL_MEDICAL_ID")
GUARDRAIL_MEDICAL_VERSION = os.environ.get("GUARDRAIL_MEDICAL_VERSION", "1")


def invoke_claude_haiku_with_guardrail(prompt: str) -> str:
    """
    アプリ側ガードレールを指定して Claude Haiku 4.5 にプロンプトを送信する。

    アカウントレベル enforcement + アプリ指定ガードレールの両方が適用され、
    より制限の厳しい方が優先される。

    Args:
        prompt: モデルに送信するユーザーメッセージ

    Returns:
        モデルからの応答テキスト
    """
    # bedrock-runtime クライアントを作成（リージョン: us-east-1）
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # リクエストボディを構築
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_tokens": 1024,
    }

    # InvokeModel API を呼び出し（ガードレールを明示指定）
    response = client.invoke_model(
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json",
        guardrailIdentifier=GUARDRAIL_MEDICAL_ID,
        guardrailVersion=GUARDRAIL_MEDICAL_VERSION,
    )

    # レスポンスボディを解析
    response_body = json.loads(response["body"].read())

    # ガードレールの適用結果を表示
    if "amazon-bedrock-guardrailAction" in response_body:
        action = response_body["amazon-bedrock-guardrailAction"]
        print(f"[ガードレール] アクション: {action}")

    # content 配列から type が "text" のブロックを探してテキストを返す
    for block in response_body.get("content", []):
        if block.get("type") == "text":
            return block["text"]

    # text ブロックが見つからない場合はレスポンス全体を返す（デバッグ用）
    return json.dumps(response_body, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # サンプルプロンプト
    user_prompt1 = "Amazon Bedrockの主な機能を3つ簡潔に説明してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"
    # 医療系ガードレールテスト用プロンプト
    user_prompt3 = "熱があるのですが、どんな薬を飲めばいいですか"

    print(f"プロンプト: {user_prompt1}")
    print("=" * 50)

    result = invoke_claude_haiku_with_guardrail(user_prompt1)
    print(f"\n応答:\n{result}")
