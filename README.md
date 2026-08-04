# English Dictionary

このリポジトリは、英単語・短い英語フレーズの学習用辞書をMarkdown中心で管理するための作業場所です。辞書本文は `entries/` に1語または1フレーズ1ファイルで保存し、`queue/words.csv` で進捗を管理します。

## CodexからGitHubへ追加する標準フロー

本文生成にOpenAI APIやGitHub Actionsは使用しない。利用者がCodex等のリポジトリを編集できるAIエージェントへ見出し語を指示し、そのエージェント自身が本文を作成してGitHubへPull Requestを出す。

標準フローは次のとおり。

1. 利用者がCodex等へ「`<見出し語>`を辞書に追加してPRを作成してください」と指示する。
2. エージェントが `AGENTS.md`、v3・v4生成仕様を全文読み、`entries/` に完成記事を直接作成する。チャットの分割出力は使わず、必要な情報が揃うまでファイルを作成・修正する。
3. `scripts/validate_entry.py` で形式検査する。
4. エージェントがv3・v4チェック仕様を全文読み、生成時の分類を再利用しないゼロベース監査を行う。修正があれば完成版全文へ反映して再検査する。
5. `queue/words.csv` と日付ログを更新し、`scripts/validate_repository.py` と全単体テストを実行する。
6. エージェントが専用ブランチへcommit・pushし、Pull Requestを作成する。
7. GitHub ActionsはAI生成を行わず、PR内の記事形式、queueとの整合、単体テストだけを再検証する。
8. 人がPRを承認・マージすると、`.github/workflows/sync-notion.yml` が完成記事をNotionへ同期する。

Notion上の新規ページは、添付元仕様どおり `ALL=見出し語`、`タグ=英単語`、`Status=未着手` とする。同じALL値の既存ページは上書きせずスキップする。NotionからGitHub Pagesへの既存反映処理は変更しない。

Excelおよび索引エクスポートは標準フローでは実行しない。既存スクリプトは過去の手動運用との互換性のためだけに残している。

### GitHubの初回設定

GitHubリポジトリでは次を設定する。

- Secret `NOTION_TOKEN`: 対象データソースへ追加権限を持つNotion Integrationのトークン。
- Variable `NOTION_DATA_SOURCE_ID`: NotionのデータソースID。現在のローカル既定値は `37783e96-dad5-4fd2-82c0-37c0147b625b`。
- `main` ブランチへの直接pushを禁止し、Pull Requestと1名以上の承認を必須にする。
- `Validate dictionary changes` を必須チェックにする。

既定ブランチ名が `main` 以外の場合は `sync-notion.yml` の対象ブランチも変更する。OpenAI APIキーは不要であり、GitHub Secretsにも登録しない。

### Codexへの依頼例

```text
「abandon」を現行のv3・v4仕様で辞書に追加し、独立したゼロベースチェック、形式検証、queue・logs更新まで行ってください。
完了後は専用ブランチへcommit・pushし、GitHubでPull Requestを作成してください。
```

このリポジトリでは、短く「`abandon`を辞書に追加してPRを作成してください」と指示しても同じ標準フローとして扱う。

## 基本構成

- `AGENTS.md`: Codex向けの運用ルール。
- `prompts/entry_spec_v3.md`: ChatGPT向け指示書から移植した、文書の内容・品質・構成に関する基礎生成仕様。v4でも全文を先に読む。
- `prompts/entry_spec_v4.md`: 構文単位の棚卸し、品詞転換、分詞形容詞、再帰形、最小対立、品詞整合を必須化した現行追加生成仕様。
- `prompts/check_spec_v3.md`: 正確性とゼロベース棚卸しに関する基礎チェック仕様。v4でも全文を先に読む。
- `prompts/check_spec_v4.md`: 生成時の分類を再利用しない独立構文マトリクスと、品詞・構文境界監査を必須化した現行追加チェック仕様。
- `prompts/entry_spec_v1.md`, `prompts/check_spec_v1.md`, `prompts/entry_spec_v2.md`, `prompts/check_spec_v2.md`: 既存記事の履歴参照用に残す旧仕様。
- `queue/words.csv`: 作成予定語、進捗、出力先ファイルを管理するキュー。
- `entries/`: 1語1Markdownの記事本文。
- `scripts/`: slug作成、形式検査、索引出力、結合出力、進捗表示のスクリプト。
- `scripts/import_to_notion.py`: 完成記事を添付仕様の階層・ブロック構造でNotionへ追加する。`--entry` で単一または複数記事を直接指定できる。
- `scripts/validate_repository.py`: queueと記事ファイルの重複、欠落、front matterの不整合を検査する。
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
3. Codexは `prompts/entry_spec_v3.md` と `prompts/entry_spec_v4.md` を順に読み、語義・構文棚卸し、必須構文マトリクス、網羅性照合を行ってから、`entries/` 配下に1語1Markdownで作成する。
4. `scripts/validate_entry.py` で形式検査する。
5. 形式検査に通ったら、Codexは `prompts/check_spec_v3.md` と `prompts/check_spec_v4.md` を順に読み、既存本文の校正と、生成時の分類を再利用しない独立したゼロベース棚卸しを行う。
6. チェックで修正が必要なら本文を修正し、問題がなければ front matter の `checked` を `true`、`queue/words.csv` の status を `checked` にする。
7. `queue/words.csv` と `logs/` を更新する。
8. `scripts/export_index.py` や `scripts/export_all_markdown.py` で出力する。

v4ではv3の品質基準をすべて継承する。類義語は原則3～8語、反意語は適する品詞・意味軸で原則2～6語、コロケーションは各語義につき原則4～10件を目安とするが、機械的な合格条件にはしない。さらに、表層形、品詞、完全な統語フレーム、中心意味、語順、評価、地域・レジスターを対応づけた構文マトリクスを生成時と独立チェック時に別々に作り、主要な分詞形容詞、再帰形、代名詞位置、語順違い、品詞境界の漏れを防ぐ。記事全体の文字数は一律に制限せず、独立した学習価値のある情報が残っていないことを完成基準とする。

添付元のChatGPT向け指示に含まれていた会話上の依頼分類、応答の分割制御、Notion保存手順は、Codexプロジェクトの本文品質とは別のためv3・v4へ移植していない。辞書記事は常に1見出し語1ファイルの完成版として保存し、`【続きあり】` などの会話制御用文字列を本文へ入れない。

## Codexに依頼する時の例文

通常は、処理件数を明示して依頼する。

例:

```text
queue/words.csv のうち status が pending の単語を指定件数だけ処理してください。
今回は5件処理してください。

必ず prompts/entry_spec_v3.md と prompts/entry_spec_v4.md をこの順で最初から最後まで読んでから、entries/ 配下に1語1Markdownで記事を作成してください。
作成後、scripts/validate_entry.py で形式検査してください。
形式検査に通ったら、必ず prompts/check_spec_v3.md と prompts/check_spec_v4.md をこの順で読み、生成時の分類を再利用しない独立したゼロベース棚卸しを行い、問題がなければ status を checked、checked を true にしてください。
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
必ずv3・v4の生成仕様とチェック仕様をすべて読んでから、旧本文を完全と仮定せず、語義・構文をゼロから棚卸しして確認してください。
必要があれば本文を修正し、queue/words.csv と logs/ を更新してください。
```

生成時は原則として自動チェックまで行うため、通常の完成状態は `checked` になる。人間の追加確認が必要な場合のみ `needs_review` にする。

## 検査・エクスポート方法

キュー状況を確認する:

```powershell
python scripts/queue_status.py
```

status別件数に加えて、`prompt_version` 別件数も表示される。これにより、旧v1～v3記事と現行v4で生成・再チェック済みの記事を区別できる。

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

基礎となる長文生成仕様は `prompts/entry_spec_v3.md` の `【生成仕様】` から `【生成仕様終わり】` までに置く。現行v4はこれを全文継承する追加仕様として `prompts/entry_spec_v4.md` に置く。大きな互換性変更を行う場合は既存ファイルを上書きせず、次のバージョンを作成して `AGENTS.md` とREADMEの参照先を更新する。

## 旧版記事の扱い

既存記事の `prompt_version: entry_spec_v1`、`entry_spec_v2`、`entry_spec_v3` は、作成時の履歴として保持する。v3・v4仕様で個別チェックを完了し、必要な本文修正と形式検査が済んだ記事だけ `prompt_version: entry_spec_v4` に更新する。旧版の `checked` は当時の仕様でのチェック済みを意味し、v4準拠を意味しない。
