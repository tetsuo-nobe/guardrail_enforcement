"""
Strands Agents SDK でアプリ側ガードレールを明示指定するサンプルコード

アカウントレベルの enforcement ガードレールに加えて、
アプリ側で別のガードレール（医療系）を指定し、両方が union で適用されることを確認する。

前提条件:
- strands-agents, python-dotenv がインストール済み
- AWS 認証情報が設定済み (AWS CLI の configure、環境変数、または IAM ロール)
- Amazon Bedrock で Claude Haiku 4.5 モデルへのアクセスが有効化済み
- .env に GUARDRAIL_MEDICAL_ID と GUARDRAIL_MEDICAL_VERSION を設定済み
"""

import os

from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel

# .env ファイルから環境変数を読み込む
load_dotenv()

# アプリ側で指定するガードレール（.env から読み込み）
GUARDRAIL_MEDICAL_ID = os.environ.get("GUARDRAIL_MEDICAL_ID")
GUARDRAIL_MEDICAL_VERSION = os.environ.get("GUARDRAIL_MEDICAL_VERSION", "1")


def run_agent_with_guardrail(prompt: str) -> str:
    """
    アプリ側ガードレールを指定して Strands Agent で Claude Haiku 4.5 を呼び出す。

    アカウントレベル enforcement + アプリ指定ガードレールの両方が適用され、
    より制限の厳しい方が優先される。

    Args:
        prompt: エージェントに送信するユーザーメッセージ

    Returns:
        エージェントからの応答テキスト
    """
    # BedrockModel を作成（ガードレール付き）
    model = BedrockModel(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        region_name="us-east-1",
        guardrail_id=GUARDRAIL_MEDICAL_ID,
        guardrail_version=GUARDRAIL_MEDICAL_VERSION,
        guardrail_trace="enabled",
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
    # 医療系ガードレールテスト用プロンプト
    user_prompt3 = "熱があるのですが、どんな薬を飲めばいいですか"

    print(f"プロンプト: {user_prompt1}")
    print("=" * 50)

    result = run_agent_with_guardrail(user_prompt1)
    print(f"\n応答:\n{result}")
