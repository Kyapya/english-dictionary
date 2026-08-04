# Project instructions

このリポジトリは、英単語・短い英語フレーズの学習用辞書をMarkdown中心で管理するためのプロジェクトである。

## 基本方針

- 辞書本文は1語または1フレーズにつき1つのMarkdownファイルとして `entries/` 配下に保存する。
- ExcelやCSVは本文保存ではなく、単語キュー、進捗、索引、出力用に使う。
- 本文生成時は必ず `prompts/entry_spec_v2.md` を最初から最後まで読む。
- 生成後は必ず `prompts/check_spec_v2.md` も最初から最後まで読み、生成時の自己確認とは独立した自動チェックを行う。
- 個別チェック時も必ず `prompts/entry_spec_v2.md` と `prompts/check_spec_v2.md` を読む。
- 生成仕様・チェック仕様を勝手に要約、簡略化、改変しない。
- 不確かな語源、年代、地域差、頻度などは断定しない。
- 既存の辞書記事を上書きする前に差分を確認する。
- 変更後は `queue/words.csv` の status を更新する。
- 作業ログは `logs/` に日付付きMarkdownで残す。

## ファイル命名

- 見出し語は `headword` と呼ぶ。
- ファイル名は小文字、半角英数字、ハイフンを基本とする。
- スペースはハイフンに変換する。
- アポストロフィ、スラッシュ、句読点などは原則削除またはハイフン化する。
- 同名衝突が起きる場合は `__word`、`__phrase`、`__verb` などの接尾辞を付ける。
- 保存先は原則 `entries/{先頭1文字または先頭2文字}/{slug}.md` とする。

例:
- `abandon` → `entries/a/abandon.md`
- `immaculate` → `entries/i/immaculate.md`
- `take off` → `entries/t/take-off.md`
- `can't help doing` → `entries/c/cant-help-doing.md`

## ステータス

`queue/words.csv` の status は次の値を使う。

- `pending`: 未生成
- `draft`: 生成済み、未チェック。原則として自動チェック前の一時状態。
- `format_error`: フォーマット不備あり
- `needs_review`: 内容確認が必要
- `checked`: チェック済み
- `final`: 完成扱い
- `skip`: 処理対象外

## 生成時のルール

- 一度に処理する件数は、ユーザーが依頼時に明示した件数に従う。
- 件数指定がない場合は、安全のため pending から5件だけ処理する。
- 大量処理を依頼された場合でも、既存ファイルの上書き、形式エラー、処理失敗が発生した場合は作業を止め、ログに記録する。
- まず `prompts/entry_spec_v2.md` を読み、本文を書く前に語義・構文棚卸し、対応づけ、網羅性マトリクス、双方向照合を内部で行う。
- 主要語義、主要構文、句動詞、地域差、レジスター、語源は、可能な限り複数の信頼できる辞書・コーパス・用例資料と整合させる。
- 本文の先頭にはYAML front matterを付ける。
- その下に、生成仕様で指定された本文を置く。
- 本文内の大見出しは、生成仕様の指定どおり全角シャープを使う。
- `＃発音記号`、`＃語源`、`＃意味や関連情報の出力（日本語訳）` は必須とする。
- `＃語形成` は学習価値がある場合、`＃コアイメージ` は多義語で有益な場合のみ、指定順で置く。
- 生成直後の一時状態は `draft` とする。
- 生成後、`scripts/validate_entry.py` で形式検査を行う。
- 形式検査で問題があれば status を `format_error` または `needs_review` にする。
- 形式検査に通ったら、必ず `prompts/check_spec_v2.md` を読み、旧本文の校正とゼロベース棚卸しを分けて自動チェックする。
- 自動チェックで修正が必要な場合は、記事ファイルへ修正版全文を反映し、`updated_at` を更新する。差分だけを残して本文を未修正にしてはならない。
- 修正後は `scripts/validate_entry.py` を再実行する。
- 自動チェック後に問題がなければ front matter の `checked: true` にし、queueのstatusを `checked` にする。
- 内容確認が残る場合は status を `needs_review` にし、理由を `queue/words.csv` の notes と `logs/` に記録する。

## Markdown本文の基本形

各辞書記事は次のようなfront matterを持つ。

```yaml
---
headword: immaculate
type: word
status: draft
prompt_version: entry_spec_v2
model: unknown
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
checked: false
tags: []
---
```

front matterの下に、`prompts/entry_spec_v2.md` の仕様に従った本文を置く。

## チェック時のルール

- 生成後の自動チェック時、および個別チェック時は `prompts/entry_spec_v2.md` と `prompts/check_spec_v2.md` を読む。
- 自動チェックと個別チェックで品質、確認観点、本文修正ルールに差を付けない。
- 既存本文の項目構成を完全と仮定せず、見出し語をゼロから語義・構文棚卸しして旧本文と比較する。
- 説明の正確性、例文の自然さ、主要語義・主要構文の網羅、類義語・反意語・コロケーションの妥当性、学習者向けの過不足、フォーマット遵守を確認する。
- 修正が必要な場合は、本文全体を壊さず、必要箇所だけ修正する。
- 修正後に `updated_at` を更新する。
- チェック済みの場合は `checked: true` にし、queueのstatusを `checked` にする。
- 修正不要の場合も、logsに「修正不要」と明記する。

## 仕様バージョンの移行

- `entry_spec_v1` / `check_spec_v1` は既存記事の生成履歴を保つため残す。
- 新規記事は `entry_spec_v2` / `check_spec_v2` を使用する。
- `prompt_version: entry_spec_v1` の既存記事をv2で再チェックした場合、v2基準を満たし修正・検査が完了した時点で `prompt_version: entry_spec_v2` に更新する。
- v1記事を、再チェックせずにv2準拠と見なさない。

## スクリプト

- `scripts/slugify.py`: headwordから保存パス用slugを作る。
- `scripts/validate_entry.py`: Markdown本文の形式を検査する。
- `scripts/export_index.py`: queueとentriesから索引CSV、可能ならExcelを出力する。Excelの `file` 列には、対応するMarkdownファイルをクリックして開けるハイパーリンクを付ける。
- `scripts/export_all_markdown.py`: checkedまたはfinalの記事を1つのMarkdownに結合する。
- `scripts/queue_status.py`: queueの件数をstatus別に表示する。

## 注意

- 辞書記事本文をExcelセルに詰め込まない。
- Excelには索引、進捗、短い要約、ファイルパスだけを出す。
- Excel索引の `file` 列は、作成済みMarkdownファイルをクリックして開けるリンクにする。
- 生成仕様の長さが大きいため、AGENTS.mdには全文を入れず、prompts配下のファイルを読む。
