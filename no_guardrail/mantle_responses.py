"""
Amazon Bedrock mantle エンドポイント（Responses API）を使用して
GPT-5.6 Luna を呼び出すサンプルコード

前提条件:
- openai, python-dotenv がインストール済み (uv add openai python-dotenv)
- .env ファイルに OPENAI_API_KEY を設定済み
- Amazon Bedrock で GPT-5.6 Luna モデルへのアクセスが有効化済み

注意:
- GPT-5.6 Luna は Chat Completions API には対応しておらず、Responses API を使用する
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# .env ファイルから環境変数を読み込む
load_dotenv()


def mantle_gpt56_luna(prompt: str) -> str:
    """
    mantle エンドポイント経由で GPT-5.6 Luna にプロンプトを送信し、
    レスポンスのテキストを返す。

    Args:
        prompt: モデルに送信するユーザーメッセージ

    Returns:
        モデルからの応答テキスト
    """
    # OpenAI クライアントを bedrock-mantle エンドポイントに向けて作成
    client = OpenAI(
        base_url="https://bedrock-mantle.us-east-1.api.aws/openai/v1",
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    # Responses API を呼び出し
    response = client.responses.create(
        model="openai.gpt-5.6-luna",
        input=prompt,
    )

    # レスポンスからテキストを抽出して返す
    return response.output_text


if __name__ == "__main__":
    # サンプルプロンプト
    user_prompt1 = "Amazon Bedrockの主な機能を3つ簡潔に説明してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"

    print(f"プロンプト: {user_prompt2}")
    print("-" * 50)

    result = mantle_gpt56_luna(user_prompt2)
    print(f"応答:\n{result}")
