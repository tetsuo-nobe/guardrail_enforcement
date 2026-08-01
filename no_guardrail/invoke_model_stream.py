"""
Amazon Bedrock InvokeModelWithResponseStream API を使用して
Claude Haiku 4.5 をストリーミング呼び出しするサンプルコード

前提条件:
- boto3 がインストール済み (pip install boto3)
- AWS 認証情報が設定済み (AWS CLI の configure、環境変数、または IAM ロール)
- Amazon Bedrock で Claude Haiku 4.5 モデルへのアクセスが有効化済み
"""

import json
import boto3


def invoke_claude_haiku_stream(prompt: str) -> None:
    """
    Claude Haiku 4.5 にプロンプトを送信し、ストリーミングでレスポンスを出力する。

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

    # InvokeModelWithResponseStream API を呼び出し
    response = client.invoke_model_with_response_stream(
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json",
    )

    # ストリーミングレスポンスを処理
    stream = response["body"]
    for event in stream:
        chunk = event.get("chunk")
        if chunk:
            payload = json.loads(chunk["bytes"].decode("utf-8"))
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

    print(f"プロンプト: {user_prompt1}")
    print("-" * 50)

    invoke_claude_haiku_stream(user_prompt1)
