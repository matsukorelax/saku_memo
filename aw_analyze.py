import json
import re
from datetime import datetime, timezone, timedelta
from collections import defaultdict

JST = timezone(timedelta(hours=9))

# Load data
with open('aw_this_week.json', encoding='utf-8') as f:
    this_week_raw = json.load(f)
with open('aw_last_week.json', encoding='utf-8') as f:
    last_week_raw = json.load(f)
with open('aw_afk.json', encoding='utf-8') as f:
    afk_raw = json.load(f)

# ---- AFK: deduplicate ----
seen_ids = set()
afk_deduped = []
for e in afk_raw:
    if e['id'] not in seen_ids:
        seen_ids.add(e['id'])
        afk_deduped.append(e)

active_total_afk = sum(e['duration'] for e in afk_deduped if e['data'].get('status') == 'not-afk')

def normalize_title(title):
    title = re.sub(r'^\(\d+\)\s*', '', title)
    title = re.sub(r'[\U0001F500-\U0001F9FF]', '', title)
    return title.strip()

def merge_events(events):
    events = sorted(events, key=lambda e: e['timestamp'])
    merged = []
    for e in events:
        app = e['data'].get('app', '')
        title = normalize_title(e['data'].get('title', ''))
        dur = e['duration']
        ts = e['timestamp']
        if merged and merged[-1]['app'] == app and normalize_title(merged[-1]['title']) == title:
            merged[-1]['duration'] += dur
        else:
            merged.append({'app': app, 'title': title, 'duration': dur, 'timestamp': ts})
    return merged

def classify(app, title):
    app_l = app.lower()
    title_l = title.lower()

    ai_browser_kw = ['claude.ai', 'chat.openai', 'chatgpt', 'gemini', 'copilot.microsoft',
                     'anthropic', 'perplexity', 'dify', 'claude - ']
    for kw in ai_browser_kw:
        if kw in title_l:
            return 'AIツール'

    if 'cursor' in app_l:
        return '開発'

    dev_apps = ['code.exe', 'devenv.exe', 'pycharm', 'intellij', 'vim', 'nvim',
                'cmd.exe', 'powershell', 'wt.exe', 'windowsterminal', 'gitkraken',
                'sourcetree', 'fork.exe', 'git']
    if any(a in app_l for a in dev_apps):
        return '開発'

    dev_title_kw = ['github', 'gitlab', 'stackoverflow', 'vs code', 'visual studio',
                    'docker', 'terminal', 'debug', 'pull request', 'commit', 'repository',
                    'node -', 'python -', 'npm', 'localhost']
    if any(t in title_l for t in dev_title_kw):
        return '開発'

    comm_apps = ['slack', 'zoom', 'teams', 'discord', 'line', 'outlook', 'thunderbird']
    comm_title_kw = ['slack', 'zoom', 'google meet', 'webex', 'discord', 'gmail', 'line -']
    if any(a in app_l for a in comm_apps):
        return 'コミュニケーション'
    if any(t in title_l for t in comm_title_kw):
        return 'コミュニケーション'

    design_kw = ['figma', 'figjam', 'miro', 'whimsical', 'sketch', 'adobe', 'canva']
    if any(t in title_l for t in design_kw):
        return 'デザイン・企画'

    task_kw = ['linear', 'jira', 'asana', 'trello', 'backlog', 'clickup']
    if any(t in title_l for t in task_kw):
        return 'タスク管理'

    doc_kw = ['google docs', 'spreadsheet', 'スプレッドシート', 'confluence', 'notion',
              'excel', 'word', 'powerpoint', 'google スライド', 'slides', 'bigquery',
              'looker', 'analytics', 'esa ']
    if any(t in title_l for t in doc_kw):
        return 'ドキュメント・分析'

    # YouTube / entertainment -> その他
    return 'その他'

# ---- Process this week ----
this_week = merge_events(this_week_raw)

day_totals = defaultdict(float)
day_sessions = defaultdict(list)

for e in this_week:
    ts = datetime.fromisoformat(e['timestamp']).astimezone(JST)
    day = ts.strftime('%Y-%m-%d')
    day_totals[day] += e['duration']
    day_sessions[day].append(e)

cat_totals = defaultdict(float)
for e in this_week:
    cat = classify(e['app'], e['title'])
    cat_totals[cat] += e['duration']

# ---- Process last week ----
last_week = merge_events(last_week_raw)
last_cat_totals = defaultdict(float)
for e in last_week:
    cat = classify(e['app'], e['title'])
    last_cat_totals[cat] += e['duration']

this_week_total = sum(cat_totals.values())

# ---- Context switches per day ----
day_switches = defaultdict(int)
for day, sessions in day_sessions.items():
    sess_sorted = sorted(sessions, key=lambda x: x['timestamp'])
    prev_app = None
    for s in sess_sorted:
        if prev_app is not None and s['app'] != prev_app:
            day_switches[day] += 1
        prev_app = s['app']

# ---- App/title time ----
title_time_by_cat = defaultdict(lambda: defaultdict(float))
for e in this_week:
    cat = classify(e['app'], e['title'])
    key = f"{e['app']} | {e['title']}"
    title_time_by_cat[cat][key] += e['duration']

def fmt_h(secs):
    h = secs / 3600
    return f"{h:.1f}h"

def bar_chart(h, max_h):
    if max_h <= 0:
        return chr(0x2591) * 8
    filled = round((h / max_h) * 8)
    filled = min(max(filled, 0), 8)
    empty = 8 - filled
    return chr(0x2588) * filled + chr(0x2591) * empty

print("## Weekly Review - 2026/03/30 〜 2026/04/02")
print()

total_active_secs = sum(day_totals.values())
num_days = len([d for d in day_totals if day_totals[d] > 300])

print("### 週間サマリー")
print(f"- 合計アクティブ時間: {total_active_secs/3600:.1f}時間")
print(f"- 稼働日数: {num_days}日")
avg = total_active_secs / 3600 / max(num_days, 1)
print(f"- 1日平均: {avg:.1f}時間")
print()

print("### 日別アクティブ時間")
day_names = {'2026-03-30': '月', '2026-03-31': '火', '2026-04-01': '水', '2026-04-02': '木'}
max_h_val = max((v/3600 for v in day_totals.values()), default=1)
for day in sorted(day_totals.keys()):
    h = day_totals[day] / 3600
    dn = day_names.get(day, day[-5:])
    sw = day_switches.get(day, 0)
    print(f"{dn} {bar_chart(h, max_h_val)} {h:.1f}h")
print()

print("### 今週やったこと")
cat_order = ['開発', 'AIツール', 'ドキュメント・分析', 'デザイン・企画', 'コミュニケーション', 'タスク管理', 'その他']

for cat in cat_order:
    t = cat_totals.get(cat, 0)
    if t < 60:
        continue
    print(f"\n#### {cat} ({fmt_h(t)})")
    items = title_time_by_cat.get(cat, {})
    top = sorted(items.items(), key=lambda x: -x[1])[:6]
    for label, d in top:
        if d > 60:
            title_only = label.split(' | ', 1)[1] if ' | ' in label else label
            print(f"  - {title_only[:80]} ({fmt_h(d)})")

print()
print("### カテゴリ別時間（週合計）")
print("| カテゴリ | 時間 | 比率 | 先週比 |")
print("|---|---|---|---|")
for cat in cat_order:
    t = cat_totals.get(cat, 0)
    if t < 60:
        continue
    pct = t / this_week_total * 100 if this_week_total > 0 else 0
    lt = last_cat_totals.get(cat, 0)
    if lt > 0:
        diff = (t - lt) / lt * 100
        diff_str = f"+{diff:.0f}%" if diff >= 0 else f"{diff:.0f}%"
    else:
        diff_str = "—"
    print(f"| {cat} | {fmt_h(t)} | {pct:.0f}% | {diff_str} |")

print()
print("### 今週のハイライト")
busiest_day = max(day_totals.items(), key=lambda x: x[1])
most_sw_day = max(day_switches.items(), key=lambda x: x[1]) if day_switches else ('2026-03-30', 0)
bdn = day_names.get(busiest_day[0], busiest_day[0])
msdn = day_names.get(most_sw_day[0], most_sw_day[0])

print(f"- 最も集中できた日: {bdn}曜日（{fmt_h(busiest_day[1])}と最長稼働）")
print(f"- 最もスイッチが多かった日: {msdn}曜日（{most_sw_day[1]}回のアプリ切り替え）")

ai_items = title_time_by_cat.get('AIツール', {})
if ai_items:
    top_ai = max(ai_items.items(), key=lambda x: x[1])
    ai_label = top_ai[0].split(' | ', 1)[1] if ' | ' in top_ai[0] else top_ai[0]
    print(f"- よく使ったAIツール: {ai_label[:60]}")
else:
    print("- AIツール: 記録なし（ブラウザタイトルで判定）")

print()
print("### 来週への提案")
top_cat = max(cat_totals.items(), key=lambda x: x[1]) if cat_totals else ('—', 0)
sw_values = list(day_switches.values())
avg_sw = sum(sw_values) / len(sw_values) if sw_values else 0

print(f"1. {bdn}曜日の稼働パターン（集中できた環境・時間帯）を来週も意図的に再現する")
if most_sw_day[1] > 30:
    print(f"2. {msdn}曜日はスイッチが{most_sw_day[1]}回と多い傾向。通知をオフにしてまとまった作業時間を確保する")
else:
    print(f"2. コンテキストスイッチは平均{avg_sw:.0f}回/日と抑えられている。この集中パターンを維持する")
print(f"3. 「{top_cat[0]}」が今週の主軸（{fmt_h(top_cat[1])}）。来週の目標と照合して優先順位を再確認する")
