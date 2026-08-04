# English Dictionary

このリポジトリは、英単語・短い英語フレーズの学習用辞書を、Markdown中心で管理するための作業場所です。辞書本文は `entries/` に1語または1フレーズ1ファイルで保存し、CSVやExcelはキュー、進捗、索引、出力補助に使います。

## 基本構成

- `AGENTS.md`: Codex向けの運用ルール。
- `prompts/entry_spec_v2.md`: 新規辞書記事を生成するときに必ず読む現行仕様。
- `prompts/check_spec_v2.md`: 生成後の自動チェック、および既存記事をチェック・修正するときに必ず読む現行仕様。
- `prompts/entry_spec_v1.md`, `prompts/check_spec_v1.md`: 既存記事の履歴参照用に残す旧仕様。
- `queue/words.csv`: 作成予定語、進捗、出力先ファイルを管理するキュー。
- `entries/`: 1語1Markdownの記事本文。
- `scripts/`: slug作成、形式検査、索引出力、結合出力、進捗表示のスクリプト。
- `exports/`: CSV、Excel、結合Markdownなどの出力先。
- `logs/`: 作業ログ。
- `backups/`: 既存記事を上書きする前のバックアップ置き場。
- `tests/`: スクリプトの単体テスト。

## 1単語1Markdownで管理する理由

1語ごとにMarkdownファイルを分けると、差分確認、部分修正、レビュー、検索、再生成がしやすくなります。Excelセルに長い本文を詰め込む方式より、見出し、例文、類義語、反意語、コロケーションを崩さず管理できます。

CSVやExcelは本文の保存場所ではなく、進捗確認や索引作成のために使います。

## queue/words.csv の列

- `headword`: 見出し語。
- `type`: `word` または `phrase` などの種別。
- `status`: 作業状態。
- `priority`: 優先度。小さいほど先に処理する想定。
- `file`: 保存先Markdownファイル。
- `prompt_version`: 使用する生成仕様。
- `model`: 生成に使ったモデル名。未記録なら空欄。
- `created_at`: 記事作成日。
- `updated_at`: 最終更新日。
- `checked`: チェック済みなら `true`。
- `notes`: 補足メモ。

## status の意味

- `pending`: 未生成。
- `draft`: 生成済み、未チェック。通常は自動チェック前の一時状態。
- `format_error`: フォーマット不備あり。
- `needs_review`: 内容確認が必要。
- `checked`: チェック済み。
- `final`: 完成扱い。
- `skip`: 処理対象外。

## 通常の運用手順

1. `queue/words.csv` に見出し語を追加する。
2. Codexに件数を指定して生成を依頼する。
3. Codexは `prompts/entry_spec_v2.md` を読み、語義・構文棚卸しと網羅性照合を行ってから、`entries/` 配下に1語1Markdownで作成する。
4. `scripts/validate_entry.py` で形式検査する。
5. 形式検査に通ったら、Codexは `prompts/check_spec_v2.md` を読み、既存本文の校正と独立したゼロベース棚卸しを行って自動チェックする。
6. チェックで修正が必要なら本文を修正し、問題がなければ front matter の `checked` を `true`、`queue/words.csv` の status を `checked` にする。
7. `queue/words.csv` と `logs/` を更新する。
8. `scripts/export_index.py` や `scripts/export_all_markdown.py` で出力する。

## Codexに依頼する時の例文

通常は、処理件数を明示して依頼する。

例:

```text
queue/words.csv のうち status が pending の単語を指定件数だけ処理してください。
今回は5件処理してください。

必ず prompts/entry_spec_v2.md を最初から最後まで読んでから、entries/ 配下に1語1Markdownで記事を作成してください。
作成後、scripts/validate_entry.py で形式検査してください。
形式検査に通ったら、必ず prompts/check_spec_v2.md を読んで独立したゼロベース棚卸しを含む自動チェックを行い、問題がなければ status を checked、checked を true にしてください。
queue/words.csv と logs/ を更新してください。
```

大量処理したい場合は、件数を変更して依頼する。

```text
queue/words.csv のうち status が pending の単語を50件処理してください。
```

安全確認を優先する場合は、少数件数で依頼する。

```text
queue/words.csv のうち status が pending の単語を3件だけ処理してください。
```

既存記事をチェックする場合:

```text
entries/i/immaculate.md をチェックしてください。
必ず prompts/entry_spec_v2.md と prompts/check_spec_v2.md を読んでから、旧本文を完全と仮定せず、語義・構文をゼロから棚卸しして確認してください。
必要があれば本文を修正し、queue/words.csv と logs/ を更新してください。
```

生成時は原則として自動チェックまで行うため、通常の完成状態は `checked` になる。人間の追加確認が必要な場合のみ `needs_review` にする。

## 検査・エクスポート方法

キュー状況を確認する:

```powershell
python scripts/queue_status.py
```

status別件数に加えて、`prompt_version` 別件数も表示される。これにより、旧v1記事と現行v2で生成・再チェック済みの記事を区別できる。

特定の記事を検査する:

```powershell
python scripts/validate_entry.py entries/i/immaculate.md
```

`entries/` 配下の記事をまとめて検査する:

```powershell
python scripts/validate_entry.py entries
```

索引CSV、可能ならExcelを出力する:

```powershell
python scripts/export_index.py
```

Excel出力の `file` 列には、存在するMarkdownファイルをクリックして開けるハイパーリンクが付く。CSV出力では従来どおりファイルパス文字列として出力される。CSV・Excelの両方に `prompt_version` を出力する。

`checked` または `final` の記事を1つのMarkdownに結合する:

```powershell
python scripts/export_all_markdown.py
```

## 生成仕様の貼り替え位置

現行の長文生成仕様は `prompts/entry_spec_v2.md` の `【生成仕様】` から `【生成仕様終わり】` までに置く。大きな互換性変更を行う場合は既存ファイルを上書きせず、次のバージョンを作成して `AGENTS.md` とREADMEの参照先を更新する。

## v1記事の扱い

既存記事の `prompt_version: entry_spec_v1` は、作成時の履歴として保持している。新しいv2仕様で個別チェックを完了し、必要な本文修正と形式検査が済んだ記事だけ `prompt_version: entry_spec_v2` に更新する。v1の `checked` は当時の仕様でのチェック済みを意味し、v2準拠を意味しない。
