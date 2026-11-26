# -*- coding: utf-8 -*-
"""zenn_role_separation_check — 役割分離（情報宇宙トイ指標の除去）検証（標準ライブラリのみ）"""
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
ARTICLE = os.path.join(ROOT, "articles", "philosophy-engine-addendum.md")
IMAGE = os.path.join(ROOT, "images", "philosophy-engine-concept-graph.png")
DRAFT = os.path.join(
    os.path.sep.join([os.path.dirname(ROOT), "Labs", "information_cosmos_toy",
                      "draft_uniqueness_consistency.md"]))
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

    csv_path = os.path.join(RESULTS, "zenn_role_separation_check.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "item", "status", "note", "checked_at_utc"])
        for c in CHECKS:
            w.writerow([c["category"], c["item"], c["status"], c["note"], now])

    json_path = os.path.join(RESULTS, "zenn_role_separation_check.json")
    report = {
        "title": "zenn role separation check",
        "article": os.path.relpath(ARTICLE, ROOT).replace(os.sep, "/"),
        "draft": "Labs/information_cosmos_toy/draft_uniqueness_consistency.md",
        "checked_at_utc": now,
        "summary": {"total": total, "ok": ok, "fail": fail, "warn": warn},
        "checks": CHECKS,
        "notes": [
            "哲学エンジン記事から一意率・一致率を除去し、境界符号化トイ側の draft に移した",
            "既存の engine/*.py・run_*.py・server.py・data/・results/・docs/benchmark_* は未変更",
            "すべて示唆・玩具モデル・解釈実験として扱っている",
            "新規依存は増やしていない（標準ライブラリのみ）",
            "published は false のまま（公開操作はユーザーが手動で実施する）",
        ],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    txt_path = os.path.join(RESULTS, "zenn_role_separation_check_summary.txt")
    lines = [
        "Zenn 役割分離チェック サマリ",
        f"チェック日時(UTC): {now}",
        f"記事: articles/philosophy-engine-addendum.md",
        f"移動先: Labs/information_cosmos_toy/draft_uniqueness_consistency.md",
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
    if not os.path.exists(ARTICLE):
        add("全般", "記事存在", "FAIL", f"{ARTICLE} が見つかりません")
        write_outputs()
        return 1

    with open(ARTICLE, encoding="utf-8") as f:
        art = f.read()

    # ---- 1. 役割分離の本体 ----
    toy_terms = ["一意率", "一致率", "ビット一致", "圧縮比", "失敗率"]
    found_toy = [t for t in toy_terms if t in art]
    add("役割分離", "記事から他Proj指標を除去",
        "OK" if not found_toy else "FAIL",
        f"検出: {', '.join(found_toy) if found_toy else 'なし'}")

    real_terms = ["最小支持根拠", "単体遮断", "迂回", "独立検算"]
    missing_real = [t for t in real_terms if t not in art]
    add("役割分離", "実データ側の用語が存在",
        "OK" if not missing_real else "FAIL",
        f"欠落: {', '.join(missing_real) if missing_real else 'なし（4語とも存在）'}")

    if "既存記事との差別化点" in art:
        add("役割分離", "既存記事との差別化点が明記", "OK", "セクション存在")
    else:
        add("役割分離", "既存記事との差別化点が明記", "FAIL", "セクションなし")

    if os.path.exists(DRAFT):
        with open(DRAFT, encoding="utf-8") as f:
            drf = f.read()
        ok_draft = ("一意率" in drf) and ("一致率" in drf)
        add("役割分離", "draft 側に2指標が戻っている",
            "OK" if ok_draft else "FAIL",
            f"draft 存在 / 一意率={'一意率' in drf} 一致率={'一致率' in drf}")
    else:
        add("役割分離", "draft 側に2指標が戻っている", "FAIL", f"{DRAFT} が見つかりません")

    # ---- 2. プライバシー ----
    email_pat = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    phones = re.findall(r"\d{2,4}[- ]\d{2,4}[- ]\d{4}", art)
    emails = email_pat.findall(art)
    secret_pat = re.compile(r"(api[_-]?key|secret|token|password|passwd|private[_-]?key)\s*[:=]\s*[\S]+", re.I)
    add("プライバシー", "個人情報・秘密情報の非混入",
        "OK" if not (phones or emails or secret_pat.findall(art)) else "FAIL",
        f"メール={len(emails)} 電話={len(phones)} 秘密={len(secret_pat.findall(art))}")

    # ---- 3. 内部情報 ----
    local_paths = re.findall(r"[A-Z]:/[^\s`)]*", art)
    internal_terms = ["Workspace", "Labs/", "results/", "草案", "手動", "投稿前に"]
    found_internal = [t for t in internal_terms if t in art]
    add("内部情報", "ローカルパス・内部運用語の非混入",
        "OK" if not local_paths and not found_internal else "FAIL",
        f"ローカルパス={len(local_paths)} 内部語={found_internal}")

    # ---- 4. 断定表現 ----
    banned = ["証明された", "物理法則の確定", "確定した", "証明する", "反証した",
              "ホログラフィック原理を証明した", "間違いなく", "宇宙の正体"]
    found_banned = [b for b in banned if b in art]
    add("断定表現", "禁止断定表現の未使用",
        "OK" if not found_banned else "FAIL",
        f"検出: {', '.join(found_banned) if found_banned else 'なし'}")

    # ---- 5. 草案向け注記 ----
    draft_notes = re.findall(r"草案|Zenn 投稿・編集は手動|投稿前に|文面案|避けること", art)
    add("文章構成", "草案向け注記の非混入",
        "OK" if not draft_notes else "FAIL",
        f"検出: {', '.join(set(draft_notes)) if draft_notes else 'なし'}")

    # ---- 6. 導線 ----
    bmc_links = re.findall(r"https?://www\.buymeacoffee\.com/[^\s`)]+", art)
    add("導線", "Buy Me a Coffee 導線が1回だけ",
        "OK" if len(bmc_links) == 1 else "FAIL",
        f"リンク数={len(bmc_links)}")

    # ---- 7. 画像・リンク ----
    imgs = re.findall(r"!\[.*?\]\((.*?)\)", art)
    broken = []
    for i in imgs:
        if not i.startswith(("http://", "https://")):
            if not os.path.exists(os.path.join(ROOT, i.lstrip("/"))):
                broken.append(i)
    add("画像参照", "画像参照が壊れていない",
        "OK" if not broken and imgs else ("WARN" if not imgs else "FAIL"),
        f"参照={len(imgs)} 破損={len(broken)} 画像存在={os.path.exists(IMAGE)}")

    urls = re.findall(r"https?://[^\s`)]+", art)
    add("リンク", "URLの本数と形式",
        "OK" if urls else "WARN",
        f"URL数={len(urls)}")

    placeholders = re.findall(r"\{\{.*?\}}|TODO|FIXME|XXXX|あなたのユーザー名", art, re.I)
    add("リンク", "プレースホルダの非混入",
        "OK" if not placeholders else "FAIL",
        f"検出: {', '.join(placeholders) if placeholders else 'なし'}")

    # ---- 8. 公開状態 ----
    m = re.search(r"^published:\s*(\w+)$", art, re.M)
    pub = m.group(1) if m else None
    add("公開状態", "published が false",
        "OK" if pub == "false" else "FAIL",
        f"published={pub}")

    # ---- 9. トーン ----
    suggestive = [s for s in ["示唆", "玩具モデル", "解釈実験"] if s in art]
    add("トーン", "示唆表現の存在",
        "OK" if suggestive else "WARN",
        f"検出: {suggestive}")

    write_outputs()
    return 0


if __name__ == "__main__":
    sys.exit(main())
