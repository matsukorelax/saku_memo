from datetime import date, timedelta


def _parse_date(s: str) -> date:
    """MM-DD → date（当年として解釈）"""
    m, d = s.split("/")
    today = date.today()
    return date(today.year, int(m), int(d))


def build_ascii_chart(tasks: list[dict]) -> str:
    """
    タスク一覧からASCIIガントチャートを生成する。

    例:
      タスクA  ████░░░░░░  03/24 - 03/27  [進行中]
      タスクB  ░░░████░░░  03/26 - 03/29  [未着手]
    """
    if not tasks:
        return "（タスクなし）"

    parsed = []
    for t in tasks:
        start = _parse_date(t["start_date"])
        end   = _parse_date(t["end_date"])
        if end < start:
            end = start
        parsed.append((t, start, end))

    min_date   = min(s for _, s, _ in parsed)
    max_date   = max(e for _, _, e in parsed)
    total_days = (max_date - min_date).days + 1

    max_name_len = max(len(t["name"]) for t, _, _ in parsed)

    lines = []
    for t, start, end in parsed:
        bar = "".join(
            "█" if start <= (min_date + timedelta(days=i)) <= end else "░"
            for i in range(total_days)
        )
        name = t["name"].ljust(max_name_len)
        status = t.get("status", "")
        lines.append(f"{name}  {bar}  {t['start_date']} - {t['end_date']}  [{status}]")

    return "\n".join(lines)
