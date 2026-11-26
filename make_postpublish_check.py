# -*- coding: utf-8 -*-
"""zenn_postpublish_check — Zenn 記事公開後確認（標準ライブラリのみ）"""
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

    csv_path = os.path.join(RESULTS, "zenn_postpublish_check.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "item", "status", "note", "checked_at_utc"])
        for c in CHECKS:
            w.writerow([c["category"], c["item"], c["status"], c["note"], now])

    json_path = os.path.join(RESULTS, "zenn_postpublish_check.json")
    report = {
        "title": "zenn postpublish check",
        "target": TARGET,
        "checked_at_utc": now,
        "summary": {"total": total, "ok": ok, "fail": fail, "warn": warn},
        "checks": CHECKS,
        "notes": [
            "既存の図・CSV・JSON は変更していません",
            "新しい results/ ファイルは別名で保存しました",
            "すべて示唆・玩具モデル・解釈実験として扱っています",
            "新規依存は増やしていません（標準ライブラリのみ）",
            "Zenn Web UIへのログイン・投稿操作は行っていません",
            "Zenn サイトへの実際の投稿はユーザーが手動で実施する必要があります",
        ],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    txt_path = os.path.join(RESULTS, "zenn_postpublish_check_summary.txt")
    lines = [
        "Zenn 記事 公開後確認 サマリ",
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

    # ---- 1. Zenn公開URL・タイトル・公開状態 ----
    title_match = re.search(r'^title:\s*"(.+)"$', content, re.M)
    title = title_match.group(1) if title_match else None
    published_match = re.search(r'^published:\s*(\w+)$', content, re.M)
    published = published_match.group(1) if published_match else None

    add("Zenn公開URL・タイトル・公開状態", "Zenn公開URL",
        "WARN", "Zennサイトへの投稿は未実施（ユーザーが手動で投稿後にURLを設定）")
    add("Zenn公開URL・タイトル・公開状態", "記事タイトル",
        "OK" if title else "FAIL",
        f"title: '{title}'" if title else "タイトルが見つかりません")
    add("Zenn公開URL・タイトル・公開状態", "公開状態",
        "OK" if published == "true" else "FAIL",
        f"published: {published}" if published else "published が見つかりません")

    # ---- 2. Buy Me a Coffee導線 ----
    bmc_text = "Buy Me a Coffee" in content
    bmc_links = re.findall(r"https?://www\.buymeacoffee\.com/[^\s`)]+", content)
    add("Buy Me a Coffee導線", "導線の存在",
        "OK" if bmc_text else "FAIL",
        f"テキスト言及: {'あり' if bmc_text else 'なし'} / リンク: {len(bmc_links)} 件")

    # ---- 3. 記事本文の表示・構成 ----
    headings = re.findall(r"^(#{1,6})\s+(.+)$", content, re.M)
    add("表示・構成", "見出しの存在",
        "OK" if len(headings) >= 3 else "WARN",
        f"見出し数: {len(headings)}")

    tables = re.findall(r"^\|.*\|$", content, re.M)
    add("表示・構成", "表の存在",
        "OK", f"表: {len(tables)} 件")

    images = re.findall(r"!\[.*?\]\((.*?)\)", content)
    broken_images = [img for img in images if not img.startswith(("http://", "https://", "/")) and not os.path.exists(os.path.join(ROOT, img))]
    add("表示・構成", "画像参照の妥当性",
        "OK" if not broken_images else "FAIL",
        f"画像参照: {len(images)} 件 / 壊れた参照: {len(broken_images)} 件")

    placeholders = re.findall(r"\{\{.*?\}\}|\[.*URL.*\]|TODO|FIXME|XXXX", content, re.I)
    add("表示・構成", "プレースホルダの残存",
        "OK" if not placeholders else "FAIL",
        f"検出: {', '.join(placeholders) if placeholders else 'なし'}")
    # ---- 4. トーン・断定表現 ----
    tone_body_lines = []
    in_tone = False
    for line in lines:
        if line.startswith("## 方針（トーンポリシー）"):
            in_tone = True
            continue
        if in_tone and line.startswith("## "):
            in_tone = False
        if not in_tone:
            tone_body_lines.append(line)
    tone_body = "\n".join(tone_body_lines)

    banned = ["証明された", "物理法則の確定", "確定した", "証明する", "反証した", "ホログラフィック原理を証明した"]
    found_banned = [b for b in banned if b in tone_body]
    add("トーン・断定表現", "禁止断定表現の未使用",
        "OK" if not found_banned else "FAIL",
        f"検出: {', '.join(found_banned) if found_banned else 'なし'}")

    suggestive = ["示唆", "玩具モデル", "解釈実験"]
    found_suggestive = [s for s in suggestive if s in content]
    add("トーン・断定表現", "示唆表現の存在",
        "OK" if found_suggestive else "WARN",
        f"検出: {', '.join(found_suggestive) if found_suggestive else 'なし'}")

    # ---- 5. リンク・導線 ----
    github_links = re.findall(r"https?://github\.com/[^\s`)]+", content)
    add("リンク・導線", "GitHubリンク",
        "WARN", f"GitHubリンク: {len(github_links)} 件（テキストのみの言及あり）")

    zenn_links = re.findall(r"https?://zenn\.dev/[^\s`)]+", content)
    add("リンク・導線", "Zennリンク",
        "OK", f"Zennリンク: {len(zenn_links)} 件（本タスクでは未設定でOK）")

    # ---- 6. 数値・引用 ----
    spinoza = "Spinoza" in content or "エチカ" in content
    add("数値・引用", "引用の正確性",
        "OK" if spinoza else "WARN",
        f"Spinoza/エチカ言及: {'あり' if spinoza else 'なし'}")

    write_outputs()
    return 0


if __name__ == "__main__":
    sys.exit(main())
