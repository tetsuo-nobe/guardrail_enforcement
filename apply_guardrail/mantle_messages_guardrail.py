"""
Amazon Bedrock mantle エンドポイント（Anthropic Messages API）を使用して
Claude Haiku 4.5 を呼び出すサンプルコード（ApplyGuardrail API による入出力チェック付き）

bedrock-mantle エンドポイントはガードレールの自動適用に非対応のため、
bedrock-runtime の ApplyGuardrail API を使って手動で入力・出力をチェックする。

前提条件:
- boto3, anthropic[bedrock] がインストール済み
- AWS 認証情報が設定済み (AWS CLI の configure、環境変数、または IAM ロール)
- Amazon Bedrock で Claude Haiku 4.5 モデルへのアクセスが有効化済み
- ガードレールが作成済みで、ID とバージョンを環境変数または下記の定数で指定
"""

import json
import os

import boto3
from dotenv import load_dotenv
from anthropic import AnthropicBedrockMantle

# .env ファイルから環境変数を読み込む
load_dotenv()

# ガードレールの設定（.env から読み込み）
GUARDRAIL_ID = os.environ.get("GUARDRAIL_ID")
GUARDRAIL_VERSION = os.environ.get("GUARDRAIL_VERSION", "1")


def apply_guardrail(text: str, source: str) -> dict:
    """
    ApplyGuardrail API を使ってテキストをガードレールで評価する。

    Args:
        text: 評価対象のテキスト
        source: "INPUT"（ユーザー入力）または "OUTPUT"（モデル出力）

    Returns:
        ガードレールの評価結果（action, outputs, assessments を含む dict）
    """
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    response = client.apply_guardrail(
        guardrailIdentifier=GUARDRAIL_ID,
        guardrailVersion=GUARDRAIL_VERSION,
        source=source,
        content=[
            {
                "text": {
                    "text": text,
                }
            }
        ],
    )

    return response


def mantle_claude_haiku_with_guardrail(prompt: str) -> str:
    """
    ガードレールチェック付きで mantle エンドポイント経由の Claude Haiku 4.5 を呼び出す。

    1. 入力をガードレールでチェック
    2. ブロックされなければ mantle 経由でモデルを呼び出し
    3. モデルの出力をガードレールでチェック
    4. ブロックされなければ出力を返す

    Args:
        prompt: モデルに送信するユーザーメッセージ

    Returns:
        モデルからの応答テキスト、またはガードレールのブロックメッセージ
    """
    # ステップ1: 入力のガードレールチェック
    print("[ガードレール] 入力チェック中...")
    input_result = apply_guardrail(prompt, "INPUT")
    input_action = input_result["action"]
    print(f"[ガードレール] 入力判定: {input_action}")

    if input_action == "GUARDRAIL_INTERVENED":
        # ガードレールが介入した場合、ブロックメッセージを返す
        blocked_message = input_result["outputs"][0]["text"]
        print(f"[ガードレール] 入力がブロックされました")
        print(f"[ガードレール] 評価詳細: {json.dumps(input_result['assessments'], ensure_ascii=False, indent=2)}")
        return f"[入力ブロック] {blocked_message}"

    # ステップ2: mantle エンドポイントでモデルを呼び出し
    print("[モデル] mantle エンドポイント経由で呼び出し中...")
    client = AnthropicBedrockMantle(aws_region="us-east-1")

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

    # テキスト部分を抽出
    model_output = ""
    for block in message.content:
        if block.type == "text":
            model_output = block.text
            break

    if not model_output:
        model_output = str(message)

    # ステップ3: 出力のガードレールチェック
    print("[ガードレール] 出力チェック中...")
    output_result = apply_guardrail(model_output, "OUTPUT")
    output_action = output_result["action"]
    print(f"[ガードレール] 出力判定: {output_action}")

    if output_action == "GUARDRAIL_INTERVENED":
        # ガードレールが介入した場合、ブロックメッセージを返す
        blocked_message = output_result["outputs"][0]["text"]
        print(f"[ガードレール] 出力がブロックされました")
        print(f"[ガードレール] 評価詳細: {json.dumps(output_result['assessments'], ensure_ascii=False, indent=2)}")
        return f"[出力ブロック] {blocked_message}"

    return model_output


if __name__ == "__main__":
    # サンプルプロンプト
    user_prompt1 = "Amazon Bedrockの主な機能を3つ簡潔に説明してください。"
    # ガードレールテスト用プロンプト（有害コンテンツとしてブロックされることを確認）
    user_prompt2 = "コンソールをハッキングする方法を教えてください。"

    print(f"プロンプト: {user_prompt1}")
    print("=" * 50)

    result = mantle_claude_haiku_with_guardrail(user_prompt1)
    print(f"\n応答:\n{result}")
