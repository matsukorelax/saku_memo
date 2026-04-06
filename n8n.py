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


def _post(payload: dict, url_env: str = "N8N_WEBHOOK_URL"):
    _load_env()
    url      = os.environ.get(url_env, "") or os.environ.get("N8N_WEBHOOK_URL", "")
    user     = os.environ.get("N8N_BASIC_USER", "")
    password = os.environ.get("N8N_BASIC_PASS", "")

    if not url:
        print(f"[n8n] {url_env} が未設定のためスキップ")
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


def notify_gantt(ascii_chart: str):
    """タスク登録時にASCIIガントチャートをn8nへ送信する。"""
    _post(
        {"type": "gantt", "ascii_chart": ascii_chart},
        url_env="N8N_GANTT_WEBHOOK_URL",
    )


def notify_bottleneck(task_name: str, end_date: str, ascii_chart: str, bottlenecks: str):
    """ボトルネック追記時にn8nへ送信する。n8nがDify→Slackへ連携する。"""
    _post(
        {
            "type":        "bottleneck",
            "task_name":   f"タスク名:{task_name}",
            "end_date":    f"終了日:{end_date}",
            "ascii_chart": ascii_chart,
            "bottlenecks": bottlenecks,
        },
        url_env="N8N_BOTTLENECK_WEBHOOK_URL",
    )
