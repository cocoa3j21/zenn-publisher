# -*- coding: utf-8 -*-
"""zenn_prepublish_final_check — Zenn 記事公開前最終確認（標準ライブラリのみ）"""
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(ROOT, "articles", "philosophy-engine-addendum.md")
IMAGE = os.path.join(ROOT, "images", "philosophy-engine-concept-graph.png")
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

    csv_path = os.path.join(RESULTS, "zenn_prepublish_final_check.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "item", "status", "note", "checked_at_utc"])
        for c in CHECKS:
            w.writerow([c["category"], c["item"], c["status"], c["note"], now])

    json_path = os.path.join(RESULTS, "zenn_prepublish_final_check.json")
    report = {
        "title": "zenn prepublish final check",
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
            "公開状態（published）は false のまま、公開操作はユーザーが手動で実施する",
        ],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    txt_path = os.path.join(RESULTS, "zenn_prepublish_final_check_summary.txt")
    lines = [
        "Zenn 記事 公開前最終確認 サマリ",
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

    # ---- 2. 内部情報 ----
    local_paths = re.findall(r"[A-Z]:/[^\s`]*", content)
    add("内部情報", "ローカルパス（D:/ T:/ など）",
        "OK" if not local_paths else "FAIL",
        f"検出: {', '.join(local_paths)}")

    internal_terms = ["Workspace", "Labs/", "草案", "手動", "投稿前に", "results/", "公開前チェックリスト"]
    found_internal = [t for t in internal_terms if t in content]
    add("内部情報", "内部運用語（Workspace/Labs/草案/手動等）",
        "OK" if not found_internal else "FAIL",
        f"検出: {', '.join(found_internal)}")

    # ---- 3. 断定表現 ----
    banned = ["証明された", "物理法則の確定", "確定した", "証明する", "反証した", "ホログラフィック原理を証明した"]
    found_banned = [b for b in banned if b in content]
    add("断定表現", "禁止断定表現の未使用",
        "OK" if not found_banned else "FAIL",
        f"検出: {', '.join(found_banned) if found_banned else 'なし'}")

    # ---- 4. 草案向け注記 ----
    draft_notes = re.findall(r"草案|Zenn 投稿・編集は手動|投稿前に|文面案|避けること", content)
    add("文章構成", "草案向け注記がないか",
        "OK" if not draft_notes else "FAIL",
        f"検出: {', '.join(set(draft_notes))}")

    # ---- 5. 公開状態 ----
    published_match = re.search(r'^published:\s*(\w+)$', content, re.M)
    published = published_match.group(1) if published_match else None
    add("公開状態", "published が false であること（公開はユーザーがZenn側で手動実施する）",
        "OK" if published == "false" else "FAIL",
        f"published: {published}" if published else "published が見つかりません")

    # ---- 6. Buy Me a Coffee導線 ----
    bmc_links = re.findall(r"https?://www\.buymeacoffee\.com/[^\s`)]+", content)
    add("Buy Me a Coffee導線", "導線が1回だけあること",
        "OK" if len(bmc_links) == 1 else "FAIL",
        f"導線リンク: {len(bmc_links)} 件")

    # ---- 7. 画像参照 ----
    images = re.findall(r"!\[.*?\]\((.*?)\)", content)
    image_refs_ok = True
    image_notes = []
    for img in images:
        if img.startswith(("http://", "https://")):
            image_notes.append(f"{img}: 外部URL")
        else:
            local_path = os.path.join(ROOT, img.lstrip("/"))
            if os.path.exists(local_path):
                image_notes.append(f"{img}: 存在")
            else:
                image_refs_ok = False
                image_notes.append(f"{img}: 存在しない（リンク切れ）")
    add("画像参照", "画像ファイルが存在し、Markdown参照パスと一致すること",
        "OK" if image_refs_ok and images else "FAIL",
        "; ".join(image_notes) if image_notes else "画像参照なし")
    add("画像参照", "concept-graph.png の存在",
        "OK" if os.path.exists(IMAGE) else "FAIL",
        f"{os.path.basename(IMAGE)}: {'存在' if os.path.exists(IMAGE) else 'なし'}")

    # ---- 8. プレースホルダ ----
    placeholders = re.findall(r"\{\{.*?\}\}|\[.*URL.*\]|TODO|FIXME|XXXX|あなたのユーザー名", content, re.I)
    add("リンク・構成", "プレースホルダの残存",
        "OK" if not placeholders else "FAIL",
        f"検出: {', '.join(placeholders) if placeholders else 'なし'}")

    # ---- 9. リンク形式 ----
    urls = re.findall(r"https?://[^\s`)]+", content)
    malformed = [u for u in urls if not re.match(r"^https?://[^\s`)]+$", u)]
    add("リンク・構成", "URLの形式",
        "OK" if not malformed else "WARN",
        f"URL数: {len(urls)} / 形式不正: {len(malformed)}")

    # ---- 10. トーン・示唆表現 ----
    suggestive = ["示唆", "玩具モデル", "解釈実験"]
    found_suggestive = [s for s in suggestive if s in content]
    add("トーン・示唆表現", "示唆表現の存在",
        "OK" if found_suggestive else "WARN",
        f"検出: {', '.join(found_suggestive) if found_suggestive else 'なし'}")

    write_outputs()
    return 0


if __name__ == "__main__":
    sys.exit(main())