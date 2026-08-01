"""
Amazon Bedrock ConverseStream API を使用して
Claude Haiku 4.5 をストリーミング呼び出しするサンプルコード

前提条件:
- boto3 がインストール済み (pip install boto3)
- AWS 認証情報が設定済み (AWS CLI の configure、環境変数、または IAM ロール)
- Amazon Bedrock で Claude Haiku 4.5 モデルへのアクセスが有効化済み
"""

import boto3


def converse_stream_claude_haiku(prompt: str) -> None:
    """
    ConverseStream API で Claude Haiku 4.5 にプロンプトを送信し、
    ストリーミングでレスポンスを出力する。

    Args:
        prompt: モデルに送信するユーザーメッセージ
    """
    # bedrock-runtime クライアントを作成（リージョン: us-east-1）
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # ConverseStream API を呼び出し
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
    )

    # ストリーミングレスポンスを処理
    stream = response["stream"]
    for event in stream:
        # テキストのチャンクを逐次出力
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"]["delta"]
            if "text" in delta:
                print(delta["text"], end="", flush=True)

    # ストリーム終了後に改行を出力
    print()


if __name__ == "__main__":
    # サンプルプロンプト
    user_prompt1 = "Amazon Bedrockの主な機能を3つ簡潔に説明してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"

    print(f"プロンプト: {user_prompt1}")
    print("-" * 50)

    converse_stream_claude_haiku(user_prompt1)
