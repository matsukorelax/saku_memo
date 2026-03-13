import json
import os
import urllib.request
import urllib.error


def _load_env(env_path=".env"):
    """`.env` ファイルを読んで環境変数に設定する。"""
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def run_ticket_helper(inputs: dict, config_path="config.json") -> str:
    """
    起票ヘルパーワークフローを実行して結果テキストを返す。
    inputs: Difyワークフローの入力項目辞書
    """
    _load_env()

    base_url = os.environ.get("DIFY_BASE_URL", "https://api.dify.ai").rstrip("/")
    api_key  = os.environ.get("DIFY_API_KEY", "")

    url = f"{base_url}/v1/workflows/run"
    payload = json.dumps({
        "inputs": inputs,
        "response_mode": "blocking",
        "user": "skuldop"
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            body = json.loads(res.read().decode("utf-8"))
            return body["data"]["outputs"].get("result", "（出力なし）")
    except urllib.error.HTTPError as e:
        return f"[Dify エラー] {e.code}: {e.read().decode('utf-8')}"
    except Exception as e:
        return f"[エラー] {e}"
