"""
Amazon Bedrock Converse API でアプリ側ガードレールを明示指定するサンプルコード

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


def converse_claude_haiku_with_guardrail(prompt: str) -> str:
    """
    アプリ側ガードレールを指定して Converse API で Claude Haiku 4.5 を呼び出す。

    アカウントレベル enforcement + アプリ指定ガードレールの両方が適用され、
    より制限の厳しい方が優先される。

    Args:
        prompt: モデルに送信するユーザーメッセージ

    Returns:
        モデルからの応答テキスト
    """
    # bedrock-runtime クライアントを作成（リージョン: us-east-1）
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # Converse API を呼び出し（ガードレールを明示指定）
    response = client.converse(
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt,
                    }
                ],
            }
        ],
        inferenceConfig={
            "maxTokens": 1024,
        },
        guardrailConfig={
            "guardrailIdentifier": GUARDRAIL_MEDICAL_ID,
            "guardrailVersion": GUARDRAIL_MEDICAL_VERSION,
        },
    )

    # ガードレールの適用結果を表示
    if "trace" in response:
        guardrail_trace = response["trace"].get("guardrail")
        if guardrail_trace:
            print(f"[ガードレール] トレース: {json.dumps(guardrail_trace, ensure_ascii=False, indent=2)}")

    stop_reason = response.get("stopReason")
    print(f"[停止理由] {stop_reason}")

    # レスポンスからテキストを抽出
    output_message = response["output"]["message"]
    for block in output_message["content"]:
        if "text" in block:
            return block["text"]

    # テキストが見つからない場合
    return json.dumps(response, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    # サンプルプロンプト
    user_prompt1 = "Amazon Bedrockの主な機能を3つ簡潔に説明してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"
    # 医療系ガードレールテスト用プロンプト
    user_prompt3 = "熱があるのですが、どんな薬を飲めばいいですか"

    print(f"プロンプト: {user_prompt1}")
    print("=" * 50)

    result = converse_claude_haiku_with_guardrail(user_prompt1)
    print(f"\n応答:\n{result}")
