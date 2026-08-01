"""
Strands Agents SDK を使用したシンプルなエージェントのサンプルコード

Claude Haiku 4.5 を bedrock-runtime エンドポイント経由で使用する。

前提条件:
- strands-agents がインストール済み (uv add strands-agents)
- AWS 認証情報が設定済み (AWS CLI の configure、環境変数、または IAM ロール)
- Amazon Bedrock で Claude Haiku 4.5 モデルへのアクセスが有効化済み
"""

from strands import Agent
from strands.models import BedrockModel


def run_agent(prompt: str) -> str:
    """
    Strands Agent を使って Claude Haiku 4.5 にプロンプトを送信し、
    レスポンスのテキストを返す。

    Args:
        prompt: エージェントに送信するユーザーメッセージ

    Returns:
        エージェントからの応答テキスト
    """
    # BedrockModel を作成（リージョン: us-east-1、モデル: Claude Haiku 4.5）
    model = BedrockModel(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        region_name="us-east-1",
    )

    # エージェントを作成
    agent = Agent(
        model=model,
        system_prompt="あなたは親切で簡潔に回答する日本語アシスタントです。",
    )

    # エージェントを実行
    result = agent(prompt)

    return str(result)


if __name__ == "__main__":
    # サンプルプロンプト
    user_prompt1 = "Amazon Bedrockの主な機能を3つ簡潔に説明してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"

    print(f"プロンプト: {user_prompt1}")
    print("=" * 50)

    result = run_agent(user_prompt1)
    print(f"\n応答:\n{result}")
