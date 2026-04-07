def build_report(tasks: list[dict], bottlenecks_map: dict) -> str:
    """
    タスク一覧とボトルネックからテキストレポートを生成する。

    例:
      【仕様確認】3/31 - 4/2  進行中
        ⚠ 3/31 仕様書が古くて確認に時間がかかった

      【テスト実施】4/3 - 4/5  完了
        （ボトルネックなし）
    """
    if not tasks:
        return "（タスクなし）"

    blocks = []
    for t in tasks:
        header = f"【{t['name']}】{t['start_date']} - {t['end_date']}  {t['status']}"
        bns = bottlenecks_map.get(t["id"], [])
        if bns:
            bn_lines = "\n".join(f"  ⚠ {b['created_at']} {b['content']}" for b in bns)
            blocks.append(f"{header}\n{bn_lines}")
        else:
            blocks.append(f"{header}\n  （ボトルネックなし）")

    return "\n\n".join(blocks)
