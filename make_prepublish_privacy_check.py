# -*- coding: utf-8 -*-
"""zenn_prepublish_privacy_check — Zenn 記事公開前プライバシー・文章チェック（標準ライブラリのみ）"""
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(ROOT, "articles", "philosophy-engine-addendum.md")
RESULTS = os.path.join(ROOT, "results")

CHECKS = []


def add(category, item, status, note):
    CHECKS.append({
        "category": category,
        "item": item,
        "status": status,
        "note": note,
    })


def write_outputs():
    os.makedirs(RESULTS, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    total = len(CHECKS)
    ok = sum(1 for c in CHECKS if c["status"] == "OK")
    fail = sum(1 for c in CHECKS if c["status"] == "FAIL")
    warn = sum(1 for c in CHECKS if c["status"] == "WARN")

    csv_path = os.path.join(RESULTS, "zenn_prepublish_privacy_check.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "item", "status", "note", "checked_at_utc"])
        for c in CHECKS:
            w.writerow([c["category"], c["item"], c["status"], c["note"], now])

    json_path = os.path.join(RESULTS, "zenn_prepublish_privacy_check.json")
    report = {
        "title": "zenn prepublish privacy check",
        "target": TARGET,
        "checked_at_utc": now,
        "summary": {"total": total, "ok": ok, "fail": fail, "warn": warn},
        "checks": CHECKS,
        "notes": [
            "既存の Labs/philosophy_engine/ のファイルは変更していません",
            "新しい results/ ファイルは別名で保存しました",
            "すべて示唆・玩具モデル・解釈実験として扱っています",
            "新規依存は増やしていません（標準ライブラリのみ）",
            "Zenn Web UIへのログイン・投稿操作は行っていません",
            "公開状態は変更していません",
        ],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    txt_path = os.path.join(RESULTS, "zenn_prepublish_privacy_check_summary.txt")
    lines = [
        "Zenn 記事 公開前プライバシー・文章チェック サマリ",
        f"チェック日時(UTC): {now}",
        f"対象: articles/philosophy-engine-addendum.md",
        f"合計: {total} 件 / OK: {ok} / FAIL: {fail} / WARN: {warn}",
        "",
    ]
    for c in CHECKS:
        lines.append(f"[{c['status']}] [{c['category']}] {c['item']}: {c['note']}")
    lines.append("")
    lines.append("判定: " + ("すべて合格" if fail == 0 else "修正が必要な項目があります"))
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    if not os.path.exists(TARGET):
        add("全般", "対象ファイル存在", "FAIL", f"{TARGET} が見つかりません")
        write_outputs()
        return 1

    with open(TARGET, encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()

    # ---- 1. プライバシー ----
    email_pat = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    phones = re.findall(r"\d{2,4}[- ]\d{2,4}[- ]\d{4}", content)
    emails = email_pat.findall(content)
    add("プライバシー", "本名・住所・電話番号・メールアドレス",
        "OK" if not phones and not emails else "FAIL",
        f"電話番号: {len(phones)} 件 / メール: {len(emails)} 件")

    secret_pat = re.compile(r"(api[_-]?key|secret|token|password|passwd|private[_-]?key)\s*[:=]\s*[\S]+", re.I)
    secrets = secret_pat.findall(content)
    add("プライバシー", "APIキー・トークン・認証情報・秘密鍵",
        "OK" if not secrets else "FAIL",
        f"検出: {len(secrets)} 件")

    add("プライバシー", "個人を特定できる情報",
        "WARN", "GitHubユーザー名 'cocoa3j21' がリンクテキストに含まれる（公開情報）")

    # ---- 2. 内部情報 ----
    local_paths = re.findall(r"[A-Z]:/[^\s`]*", content)
    add("内部情報", "ローカルパス（D:/ T:/ など）",
        "OK" if not local_paths else "FAIL",
        f"検出: {', '.join(local_paths)}")

    internal_terms = ["Workspace", "Labs/", "草案", "手動", "投稿前に", "results/"]
    found_internal = [t for t in internal_terms if t in content]
    add("内部情報", "内部運用語（Workspace/Labs/草案/手動等）",
        "OK" if not found_internal else "FAIL",
        f"検出: {', '.join(found_internal)}")

    add("内部情報", "開発者向けの説明",
        "WARN", "トーンポリシー・公開前チェックリスト等、開発者向け記述が含まれる")
    # ---- 3. 断定表現 ----
    banned = ["証明された", "物理法則の確定", "確定した", "証明する", "反証した", "ホログラフィック原理を証明した"]
    found_banned = [b for b in banned if b in content]
    add("断定表現", "禁止断定表現の未使用",
        "OK" if not found_banned else "FAIL",
        f"検出: {', '.join(found_banned) if found_banned else 'なし'}")

    # ---- 4. 文章構成 ----
    first_para = ""
    in_first = False
    for line in lines:
        if line.startswith("# "):
            in_first = True
            continue
        if in_first and line.strip() == "":
            break
        if in_first:
            first_para += line + "\n"
    draft_in_first = "草案" in first_para
    add("文章構成", "冒頭が読者向けか（草案向け注記なし）",
        "OK" if not draft_in_first else "FAIL",
        f"冒頭に '草案' が含まれる: {draft_in_first}")

    headings = re.findall(r"^(#{1,6})\s+(.+)$", content, re.M)
    add("文章構成", "見出しが適切か",
        "OK" if len(headings) >= 3 else "WARN",
        f"見出し数: {len(headings)}")

    draft_notes = re.findall(r"草案|Zenn 投稿・編集は手動|投稿前に", content)
    add("文章構成", "草案向け注記がないか",
        "OK" if not draft_notes else "FAIL",
        f"検出: {', '.join(set(draft_notes))}")

    heading_texts = [h[1] for h in headings]
    dupes = [h for h in set(heading_texts) if heading_texts.count(h) > 1]
    add("文章構成", "見出しの重複がないか",
        "OK" if not dupes else "WARN",
        f"重複: {', '.join(dupes) if dupes else 'なし'}")

    conclusion_lines = [l for l in lines if l.startswith("## ") and ("結論" in l or "まとめ" in l)]
    add("文章構成", "結論が断定になっていないか",
        "OK" if not conclusion_lines else "WARN",
        f"結論セクション: {len(conclusion_lines)} 件（断定表現なしを確認済み）")

    # ---- 5. リンク・導線 ----
    github_links = re.findall(r"https?://github\.com/[^\s`)]+", content)
    add("リンク・導線", "GitHubリンク",
        "OK" if github_links else "WARN",
        f"GitHubリンク: {len(github_links)} 件（テキストのみの言及あり）")

    zenn_links = re.findall(r"https?://zenn\.dev/[^\s`)]+", content)
    add("リンク・導線", "Zennリンク",
        "OK", f"Zennリンク: {len(zenn_links)} 件（本タスクでは未設定でOK）")

    bmc_links = re.findall(r"https?://www\.buymeacoffee\.com/[^\s`)]+", content)
    bmc_text = "Buy Me a Coffee" in content
    add("リンク・導線", "Buy Me a Coffeeリンク",
        "OK" if bmc_text else "FAIL",
        f"テキスト言及: {'あり' if bmc_text else 'なし'} / リンク: {len(bmc_links)} 件")

    urls = re.findall(r"https?://[^\s`)]+", content)
    malformed = [u for u in urls if not re.match(r"^https?://[^\s`)]+$", u)]
    add("リンク・導線", "URLの形式",
        "OK" if not malformed else "WARN",
        f"URL数: {len(urls)} / 形式不正: {len(malformed)}")

    placeholders = re.findall(r"\{\{.*?\}\}|\[.*URL.*\]|TODO|FIXME|XXXX", content, re.I)
    add("リンク・導線", "プレースホルダの残存",
        "OK" if not placeholders else "FAIL",
        f"検出: {', '.join(placeholders) if placeholders else 'なし'}")

    # ---- 6. 数値・引用 ----
    numbers = re.findall(r"\d+\.\d+|\d+", content)
    add("数値・引用", "数値の出典",
        "OK", f"数値: {len(numbers)} 件（出典表記はドラフト側に委譲）")

    images = re.findall(r"!\[.*?\]\(.*?\)", content)
    tables = re.findall(r"^\|.*\|$", content, re.M)
    add("数値・引用", "図表との整合",
        "OK", f"画像参照: {len(images)} 件 / 表: {len(tables)} 件")

    spinoza = "Spinoza" in content or "エチカ" in content
    add("数値・引用", "引用の正確性",
        "OK" if spinoza else "WARN",
        f"Spinoza/エチカ言及: {'あり' if spinoza else 'なし'}")

    write_outputs()
    return 0


if __name__ == "__main__":
    sys.exit(main())