"""
Amazon Bedrock InvokeModel API を使用して Claude Haiku 4.5 を呼び出すサンプルコード

前提条件:
- boto3 がインストール済み (pip install boto3)
- AWS 認証情報が設定済み (AWS CLI の configure、環境変数、または IAM ロール)
- Amazon Bedrock で Claude Haiku 4.5 モデルへのアクセスが有効化済み
"""

import json
import boto3


def invoke_claude_haiku(prompt: str) -> str:
    """
    Claude Haiku 4.5 にプロンプトを送信し、レスポンスのテキストを返す。

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

    # InvokeModel API を呼び出し
    response = client.invoke_model(
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json",
    )

    # レスポンスボディを解析
    response_body = json.loads(response["body"].read())

    # content 配列から type が "text" のブロックを探してテキストを返す
    for block in response_body["content"]:
        if block.get("type") == "text":
            return block["text"]

    # text ブロックが見つからない場合はレスポンス全体を返す（デバッグ用）
    return json.dumps(response_body, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # サンプルプロンプト
    user_prompt1 = "Amazon Bedrockの主な機能を3つ簡潔に説明してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"

    print(f"プロンプト: {user_prompt1}")
    print("-" * 50)

    result = invoke_claude_haiku(user_prompt1)
    print(f"応答:\n{result}")
