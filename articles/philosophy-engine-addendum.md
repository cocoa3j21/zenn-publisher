---
title: "哲学エンジン：Spinoza『エチカ』の依存関係を検証する"
emoji: "🧠"
type: tech
topics:
  - python
  - philosophy
  - spinoza
  - zenn
published: true
---

# Zenn追記原稿（草案）— philosophy_engine 移設

このフォルダは、既存 `D:/Workspace/philosophy_engine/` を **`D:/Workspace/Labs/philosophy_engine/` へ移設**したものです。
公開用ミラーは引き続き `T:/spinoza_export`（cocoa3j21/spinoza-ethics-engine）を維持します。

## 方針（トーンポリシー）

- すべて「示唆」「玩具モデル」「解釈実験」として扱う
- 「証明」「物理法則の確定」「確定した」などの断定表現は使わない
- 各結果の直後に「その指標が何を測っていないか」を併記する
- 復元・解析は総当たり等の玩具実装であり、実用の圧縮器と同じ土俵で比較しない

## 内容

| 項目 | 内容 | 出典 |
|---|---|---|
| `engine/core.py` | 概念グラフの構築・巡回ロジック（哲学的対話の玩具モデル） | Labs/philosophy_engine/engine |
| `engine/comparative.py` | 複数哲学者の概念構造を並べた比較試行 | Labs/philosophy_engine/engine |
| `engine/explorer.py` | 概念空間の探索・近傍走査（解釈実験） | Labs/philosophy_engine/engine |
| `engine/benchmark_core.py` | 指標測定の基礎関数（一意率・一致率等の算出） | Labs/philosophy_engine/engine |
| `docs/` | 設計メモ・解析メモ・未解決課題 | Labs/philosophy_engine/docs |
| `data/` | デカルト・カント・ライプニッツ・スピノザ等の概念データ（JSON） | Labs/philosophy_engine/data |

## 関連リンク

- 移設元（元プロジェクト）: `D:/Workspace/philosophy_engine/`（廃止・今後は Labs 側を正本とする）
- 公開用ミラー: `T:/spinoza_export`（cocoa3j21/spinoza-ethics-engine、引き続き維持・同期は手動）
- Labs 全体: `D:/Workspace/Labs/README.md`（このフォルダへのリンクあり）

## Zenn 記事への追記イメージ（草案）

> このセクションでは、哲学的概念の関係性をグラフとして表現し、巡回・比較する玩具モデルの記録を示します。あくまで「こういう数値が出た」という示唆であり、哲学体系の正当性や物理法則を主張するものではありません。

※ 本原稿は草案であり、Zenn 投稿・編集は手動で行います。投稿前に `results/` の数値と照合してください。

## Buy Me a Coffee 導線（補完）

- 主導線: Zenn 組み込みの Buy Me a Coffee（記事下のチップ）を主導線にする
- 本文中の上限: 1 回
- 図表の後 → テキストリンク 1 文（理由: 結果を読んで、続きを見る価値があるか判断した直後）
- 結論メモの後（記事末尾） → 2〜3 行の締め（理由: 断定を強める流れを避けて、感謝ベースで置く）

文面案:
> こういう玩具モデルを、同じ速さで作り続けるための支援になります。
> 読んで面白ければ、そのまま投げ銭でも十分嬉しいです。

避けること:
- 支援しないと続きが読めない、という情報を縛る導線
- 支援で〜が分かる、という成果の約束
- 記事冒頭での導線
- 結論の直前に置いて断定を後押しする形

## 公開前チェックリスト（補完）

| 区分 | 内容 | 状態 |
|---|---|---|
| トーン | 示唆・玩具モデル・断定回避 | OK |
| Buy Me a Coffee | Zenn 組み込み主導線・本文 1 回まで | OK |
| 公開前注意 | 数値出典・手動編集 | OK |

※ このチェックリストは投稿前に Zenn エディタで最終確認してください。
