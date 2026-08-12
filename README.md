# English Dictionary

このリポジトリは、英単語・短い英語フレーズの学習用辞書をMarkdown中心で管理するための作業場所です。辞書本文は `entries/` に1語または1フレーズ1ファイルで保存し、`queue/words.csv` で進捗を管理します。

## CodexからGitHubへ追加する標準フロー

本文生成にOpenAI APIやGitHub Actionsは使用しない。利用者がCodex等のリポジトリを編集できるAIエージェントへ見出し語を指示し、そのエージェント自身が本文を作成してGitHubへPull Requestを出す。

標準フローは次のとおり。

1. 利用者がCodex等へ「`<見出し語>`を辞書に追加してPRを作成してください」と指示する。
2. エージェントが `AGENTS.md` と現行完全版 `prompts/entry_spec_v5.md` だけを全文読み、`entries/` に完成記事を直接作成する。チャットの分割出力は使わず、必要な情報が揃うまでファイルを作成・修正する。
3. `scripts/validate_entry.py` で形式検査する。
4. エージェントが現行完全版 `prompts/check_spec_v5.md` だけを全文読み、生成時の分類を再利用しないゼロベース監査を行う。修正があれば完成版全文へ反映して再検査する。この時点ではまだ `checked: true` にしない。
5. 文脈を継承しない新しい会話または独立実行へ、front matterを除いた最新版本文と「英単語解説として問題がないか、内容上の問題を前提なしで指摘してください」という短い依頼だけを渡し、コールドレビューを行う。生成仕様、チェック仕様、過去の指摘、差分、queue、logs、既存判定は渡さない。
6. 元の作業実行が、コールドレビューの各問題候補を現行仕様と信頼できる資料で検証し、`採用`、`不採用`、`保留` に判定する。採用指摘だけを本文へ反映し、保留があれば `needs_review` にする。
7. 判定・修正後の最新版全文に対して、内容監査、双方向照合、発音監査、書式監査、形式検証を再実行する。変更箇所だけの確認では完了扱いにしない。
8. 全候補の判定、保留ゼロ、採用修正、全文再検査が完了した後だけ、`queue/words.csv` と日付ログを更新し、statusを `checked`、checkedを `true` にする。`scripts/validate_repository.py` と全単体テストも実行する。
9. エージェントが専用ブランチへcommit・pushし、Pull Requestを作成する。
10. GitHub ActionsはAI生成を行わず、PR内の記事形式、queueとの整合、単体テストだけを再検証する。
11. 検証成功後、エージェントがPull Requestを `main` へマージする。利用者がレビュー待ちを明示した場合だけ、マージせず停止する。
12. `.github/workflows/sync-notion.yml` がマージされた完成記事をNotionへ同期する。
13. エージェントがNotion同期ワークフローの成功を確認してから依頼完了を報告する。

Notion同期では `prompts/notion_spec_v1.md` に従い、同じ `ALL=見出し語` のページがあれば本文を更新し、なければ `タグ=英単語` の新規ページを作成する。本文変更前に `Status=進行中` とし、新旧ブロックの入れ替えと更新後検査が完了した後だけ `Status=完了` にする。同じALL値が複数ある場合は、Notion APIの `last_edited_time` が最新のページだけを更新し、ほかの重複ページは変更しない。見出しラベルと本文を分け、コロケーション・類義語・反意語は1エントリ1ブロックにする。GitHub上では同じ見出し語のMarkdownを最新版へ上書きし、GitHubを現行版の正本とする。

Excelおよび索引エクスポートは標準フローでは実行しない。既存スクリプトは過去の手動運用との互換性のためだけに残している。

### GitHubの初回設定

GitHubリポジトリでは次を設定する。

- Secret `NOTION_TOKEN`: 対象データソースへ追加権限を持つNotion Integrationのトークン。
- Variable `NOTION_DATA_SOURCE_ID`: NotionのデータソースID。現在のローカル既定値は `37783e96-dad5-4fd2-82c0-37c0147b625b`。
- `main` ブランチへの直接pushを禁止し、Pull Request経由の変更を必須にする。標準フローを完全自動化する場合は、人の承認を必須にするブランチルールを設定しない。
- `Validate dictionary changes` を必須チェックにする。

既定ブランチ名が `main` 以外の場合は `sync-notion.yml` の対象ブランチも変更する。OpenAI APIキーは不要であり、GitHub Secretsにも登録しない。

### Codexへの依頼例

```text
「abandon」を現行の完全版v5仕様で辞書に追加し、独立したゼロベースチェック、形式検証、queue・logs更新まで行ってください。
完了後は専用ブランチへcommit・pushし、GitHubでPull Requestを作成してください。
```

このリポジトリでは、短く「`abandon`を辞書に追加してPRを作成してください」と指示しても同じ標準フローとして扱う。

## 基本構成

- `AGENTS.md`: Codex向けの運用ルール。
- `prompts/entry_spec_v5.md`: 文書品質、語義・構文棚卸し、品詞転換、分詞形容詞、再帰形、最小対立、品詞整合、見出し、空行、行末半角スペース、固定行数をすべて含む現行完全版生成仕様。生成時に読む仕様はこの1ファイルだけである。
- `prompts/check_spec_v5.md`: 校正、独立構文マトリクス、ゼロベース棚卸し、品詞・構文境界監査、コールドレビュー、指摘の判定・修正、全文再検査、本文書式、完了条件をすべて含む現行完全版チェック仕様。通常チェックと後続判定・再検査を管理する実行だけが読み、コールドレビュー担当には渡さない。
- `prompts/notion_spec_v1.md`: 完成版をNotionへ転記するときのプロパティ、見出し階層、1エントリ1ブロック、改行、インライン表記を定める仕様。
- `prompts/entry_spec_v1.md`～`prompts/entry_spec_v4.md` と対応するチェック仕様: 既存記事の生成・確認履歴を再現する場合だけ参照する旧仕様。現行の生成・チェックでは読まない。
- `queue/words.csv`: 作成予定語、進捗、出力先ファイルを管理するキュー。
- `entries/`: 1語1Markdownの記事本文。
- `scripts/`: slug作成、形式検査、索引出力、結合出力、進捗表示のスクリプト。
- `scripts/import_to_notion.py`: 完成記事を `prompts/notion_spec_v1.md` の階層・ブロック構造でNotionへ同期する。`--entry` で単一または複数記事を直接指定でき、同じ見出し語が複数ある場合は最終更新日時が最新のページだけを更新する。
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
3. Codexは `prompts/entry_spec_v5.md` だけを読み、語義・構文棚卸し、必須構文マトリクス、網羅性照合を行ってから、`entries/` 配下に1語1Markdownで作成する。
4. `scripts/validate_entry.py` で形式検査する。
5. 形式検査に通ったら、Codexは `prompts/check_spec_v5.md` だけを読み、既存本文の校正と、生成時の分類を再利用しない独立したゼロベース棚卸しを行う。
6. 通常チェック後の最新版本文だけを文脈非継承の独立実行へ渡し、短い依頼でコールドレビューする。
7. 元の作業実行が全指摘候補を根拠確認して `採用`、`不採用`、`保留` に判定し、採用指摘だけを本文へ反映する。
8. 判定・修正後の最新版全文を再検査し、形式検証も再実行する。
9. 保留がなく、全文再検査に成功した場合だけ、front matterの `checked` を `true`、`queue/words.csv` のstatusを `checked` にする。
10. `queue/words.csv` と `logs/` を更新する。
11. 必要な場合だけ `scripts/export_index.py` や `scripts/export_all_markdown.py` で出力する。

現行v5は、従来の有効な品質・内容・監査・書式要件を完全版へ統合している。類義語は原則3～8語、反意語は適する品詞・意味軸で原則2～6語、コロケーションは各語義につき原則4～10件を目安とするが、機械的な合格条件にはしない。さらに、表層形、品詞、完全な統語フレーム、中心意味、語順、評価、地域・レジスターを対応づけた構文マトリクスを生成時と独立チェック時に別々に作り、主要な分詞形容詞、再帰形、代名詞位置、語順違い、品詞境界の漏れを防ぐ。記事全体の文字数は一律に制限せず、独立した学習価値のある情報が残っていないことを完成基準とする。構造見出し以外の本文行は行末半角スペース2個、独立ブロック間は空行1行という原指示の表示書式も機械検査する。

添付元のChatGPT向け指示に含まれていた会話上の依頼分類と応答の分割制御だけは、ファイルへ直接完成版を保存するリポジトリ運用へ置き換えている。文書作成の品質と書式は `prompts/entry_spec_v5.md`、独立チェックは `prompts/check_spec_v5.md`、Notion保存の表示変換は `prompts/notion_spec_v1.md` へ分離している。辞書記事は常に1見出し語1ファイルの完成版として保存し、`【続きあり】` などの会話制御用文字列を本文へ入れない。

## Codexに依頼する時の例文

通常は、処理件数を明示して依頼する。

例:

```text
queue/words.csv のうち status が pending の単語を指定件数だけ処理してください。
今回は5件処理してください。

必ず prompts/entry_spec_v5.md だけを最初から最後まで読んでから、entries/ 配下に1語1Markdownで記事を作成してください。
作成後、scripts/validate_entry.py で形式検査してください。
形式検査に通ったら、必ず prompts/check_spec_v5.md だけを最初から最後まで読み、生成時の分類を再利用しない独立したゼロベース棚卸しを行ってください。
通常チェック後は、文脈を継承しない独立実行へfront matterを除いた最新版本文と短い依頼だけを渡してコールドレビューし、全指摘候補を採用・不採用・保留に判定してください。
採用修正後の最新版全文を再検査し、保留がなく全検証に成功した場合だけ status を checked、checked を true にしてください。
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
必ず prompts/check_spec_v5.md だけを読んでから、旧本文を完全と仮定せず、語義・構文をゼロから棚卸しして確認してください。
通常チェック後に文脈非継承のコールドレビュー、全指摘候補の判定・必要な修正、最新版全文の再検査まで行ってください。
保留がなく全検証に成功した場合だけ checked にし、queue/words.csv と logs/ を更新してください。
```

生成時は通常チェック、コールドレビュー、指摘の判定・修正、全文再検査まで行うため、全工程に合格した通常の完成状態は `checked` になる。コールドレビュー未実施、候補未判定、保留あり、または再検査未完了の場合は `needs_review` または未チェック状態にする。

## 検査・エクスポート方法

キュー状況を確認する:

```powershell
python scripts/queue_status.py
```

status別件数に加えて、`prompt_version` 別件数も表示される。これにより、旧v1～v4記事と現行v5で生成・再チェック済みの記事を区別できる。

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

現行生成仕様の全文は `prompts/entry_spec_v5.md`、現行チェック仕様の全文は `prompts/check_spec_v5.md` に置く。新しい要件を追加するときは、旧版との連鎖参照を作らず、各現行完全版へ統合する。Notion表示変換は `prompts/notion_spec_v1.md` に分離する。大きな互換性変更を行う場合は次の完全版を作成し、`AGENTS.md` とREADMEの参照先を新しい単一ファイルへ更新する。

## 旧版記事の扱い

既存記事の `prompt_version: entry_spec_v1`～`entry_spec_v4` は、作成時の履歴として保持する。現行完全版 `prompts/check_spec_v5.md` で個別チェックを完了し、必要な本文修正とv5形式検査が済んだ記事だけ `prompt_version: entry_spec_v5` に更新する。旧版の `checked` は当時の仕様でのチェック済みを意味し、v5準拠を意味しない。
