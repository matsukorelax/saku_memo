import json
import os
import urllib.request
import urllib.error


def _load_env(env_path=".env"):
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def _post(payload: dict):
    _load_env()
    url      = os.environ.get("N8N_WEBHOOK_URL", "")
    user     = os.environ.get("N8N_BASIC_USER", "")
    password = os.environ.get("N8N_BASIC_PASS", "")

    if not url:
        print("[n8n] N8N_WEBHOOK_URL が未設定のためスキップ")
        return

    import base64
    token = base64.b64encode(f"{user}:{password}".encode()).decode()

    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            print(f"[n8n] 通知成功: {res.status}")
    except Exception as e:
        print(f"[n8n] 通知失敗（無視）: {e}")


def notify_ticket(ticket_id: int, inputs: dict, body: str):
    """チケット保存時にn8nへ通知する。"""
    _post({
        "records": [
            {
                "Project":     "skuldop",
                "ID":          str(ticket_id),
                "Title":       inputs.get("memo_check_log", ""),
                "Description": body,
            }
        ]
    })


def notify_status(ticket_id: int, status: str):
    """ステータス変更時にn8nへ通知する。"""
    _post({
        "event":     "status_changed",
        "ticket_id": ticket_id,
        "status":    status,
    })
