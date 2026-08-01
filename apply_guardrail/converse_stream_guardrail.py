"""
Amazon Bedrock ConverseStream API でアプリ側ガードレールを明示指定するサンプルコード

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


def converse_stream_claude_haiku_with_guardrail(prompt: str) -> None:
    """
    アプリ側ガードレールを指定して ConverseStream API で Claude Haiku 4.5 をストリーミング呼び出しする。

    アカウントレベル enforcement + アプリ指定ガードレールの両方が適用され、
    より制限の厳しい方が優先される。

    Args:
        prompt: モデルに送信するユーザーメッセージ
    """
    # bedrock-runtime クライアントを作成（リージョン: us-east-1）
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # ConverseStream API を呼び出し（ガードレールを明示指定）
    response = client.converse_stream(
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
            "streamProcessingMode": "async",
        },
    )

    # ストリーミングレスポンスを処理
    stream = response["stream"]
    for event in stream:
        # テキストのチャンクを逐次出力
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"]["delta"]
            if "text" in delta:
                print(delta["text"], end="", flush=True)

        # メタデータ（停止理由やガードレール情報）を表示
        if "messageStop" in event:
            stop_reason = event["messageStop"].get("stopReason")
            print(f"\n[停止理由] {stop_reason}")

        # ガードレールのトレース情報
        if "metadata" in event:
            trace = event["metadata"].get("trace")
            if trace and "guardrail" in trace:
                print(f"[ガードレール] トレース: {json.dumps(trace['guardrail'], ensure_ascii=False, indent=2)}")

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

    converse_stream_claude_haiku_with_guardrail(user_prompt1)
