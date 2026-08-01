"""
Amazon Bedrock mantle エンドポイント（Anthropic Messages API）を使用して
Claude Haiku 4.5 を呼び出すサンプルコード

前提条件:
- anthropic[bedrock] がインストール済み (uv add "anthropic[bedrock]")
- AWS 認証情報が設定済み (AWS CLI の configure、環境変数、または IAM ロール)
- Amazon Bedrock で Claude Haiku 4.5 モデルへのアクセスが有効化済み
"""

from anthropic import AnthropicBedrockMantle


def mantle_claude_haiku(prompt: str) -> str:
    """
    mantle エンドポイント経由で Claude Haiku 4.5 にプロンプトを送信し、
    レスポンスのテキストを返す。

    Args:
        prompt: モデルに送信するユーザーメッセージ

    Returns:
        モデルからの応答テキスト
    """
    # mantle エンドポイント用クライアントを作成（リージョン: us-east-1）
    client = AnthropicBedrockMantle(aws_region="us-east-1")

    # Messages API を呼び出し
    message = client.messages.create(
        model="anthropic.claude-haiku-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    # テキスト部分を抽出して返す
    for block in message.content:
        if block.type == "text":
            return block.text

    # テキストが見つからない場合
    return str(message)


if __name__ == "__main__":
    # サンプルプロンプト
    user_prompt1 = "Amazon Bedrockの主な機能を3つ簡潔に説明してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"

    print(f"プロンプト: {user_prompt1}")
    print("-" * 50)

    result = mantle_claude_haiku(user_prompt1)
    print(f"応答:\n{result}")
