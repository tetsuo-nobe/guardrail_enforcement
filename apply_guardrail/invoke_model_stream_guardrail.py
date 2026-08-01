"""
Amazon Bedrock InvokeModelWithResponseStream API でアプリ側ガードレールを明示指定するサンプルコード

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


def invoke_claude_haiku_stream_with_guardrail(prompt: str) -> None:
    """
    アプリ側ガードレールを指定して Claude Haiku 4.5 をストリーミング呼び出しする。

    アカウントレベル enforcement + アプリ指定ガードレールの両方が適用され、
    より制限の厳しい方が優先される。

    Args:
        prompt: モデルに送信するユーザーメッセージ
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

    # InvokeModelWithResponseStream API を呼び出し（ガードレールを明示指定）
    response = client.invoke_model_with_response_stream(
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json",
        guardrailIdentifier=GUARDRAIL_MEDICAL_ID,
        guardrailVersion=GUARDRAIL_MEDICAL_VERSION,
    )

    # ストリーミングレスポンスを処理
    stream = response["body"]
    for event in stream:
        chunk = event.get("chunk")
        if chunk:
            payload = json.loads(chunk["bytes"].decode("utf-8"))

            # ガードレールの適用結果を表示
            if payload.get("type") == "message_stop":
                guardrail_result = payload.get("amazon-bedrock-guardrailAction")
                if guardrail_result:
                    print(f"\n[ガードレール] アクション: {guardrail_result}")

            # content_block_delta イベントからテキストを逐次出力
            if payload.get("type") == "content_block_delta":
                delta = payload.get("delta", {})
                if delta.get("type") == "text_delta":
                    print(delta["text"], end="", flush=True)

    # ストリーム終了後に改行を出力
    print()


if __name__ == "__main__":
    # サンプルプロンプト
    user_prompt1 = "Amazon Bedrockの主な機能を3つ簡潔に説明してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"
    # 医療系ガードレールテスト用プロンプト
    user_prompt3 = "熱があるのですが、どんな薬を飲めばいいですか"

    print(f"プロンプト: {user_prompt1}")
    print("=" * 50)

    invoke_claude_haiku_stream_with_guardrail(user_prompt1)
