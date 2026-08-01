"""
Amazon Bedrock Converse API を使用して Claude Haiku 4.5 を呼び出すサンプルコード

前提条件:
- boto3 がインストール済み (pip install boto3)
- AWS 認証情報が設定済み (AWS CLI の configure、環境変数、または IAM ロール)
- Amazon Bedrock で Claude Haiku 4.5 モデルへのアクセスが有効化済み
"""

import boto3


def converse_claude_haiku(prompt: str) -> str:
    """
    Converse API で Claude Haiku 4.5 にプロンプトを送信し、レスポンスのテキストを返す。

    Args:
        prompt: モデルに送信するユーザーメッセージ

    Returns:
        モデルからの応答テキスト
    """
    # bedrock-runtime クライアントを作成（リージョン: us-east-1）
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # Converse API を呼び出し
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
    )

    # レスポンスからテキストを抽出
    output_message = response["output"]["message"]
    for block in output_message["content"]:
        if "text" in block:
            return block["text"]

    # テキストが見つからない場合
    return str(response)


if __name__ == "__main__":
    # サンプルプロンプト
    user_prompt1 = "Amazon Bedrockの主な機能を3つ簡潔に説明してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"

    print(f"プロンプト: {user_prompt1}")
    print("-" * 50)

    result = converse_claude_haiku(user_prompt1)
    print(f"応答:\n{result}")
