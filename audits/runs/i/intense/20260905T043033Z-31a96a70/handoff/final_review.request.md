# Independent review handoff

Stage: `final_review`

The response must be one JSON object matching the supplied review schema. Create it in a separate model session; do not use the generation session.

## Prompt

# final_review_spec_v2

この仕様は、最新版の記事本文、全checker/cold/final-blind finding、全resolution、固定済みblind inventoryを入力として、第三者最終審査が合否を判断するための意味基準だけを定める。入力分離、順序、hash、seal、記録、件数網羅、status同期は `scripts/run_word.py` と `scripts/generate_audit_manifest.py` が強制する。

## PASSの意味基準

次をすべて満たす場合だけ `PASS` とする。

1. 記事の事実、語法、発音、例文、訳が正しく、見出し語の意味方向・意味役割・適用範囲を誤学習させない。
2. 主要な品詞、語義、派生・転換、専門用法、完全な統語フレームが過不足なく扱われ、語義境界、コアイメージ、定義、語法、コロケーション、語彙関係の間に矛盾がない。
3. 例文と訳で、述語、主語・目的語・補語、行為者・経験者・対象・結果、肯否、比較基準、程度、数量、時制・相・法、条件・因果・目的、修飾範囲、焦点、情報構造、レジスター、話者評価が保存されている。
4. 地域差、専門・制度用法、頻度、語源、語形成、語義境界、文法制約、絶対表現などの高リスク主張が、当該主張へ適用できる根拠に支えられ、反例・矛盾・適用範囲が確認されている。検索見出し、資料名だけ、別義の用例は根拠にしない。
5. 通常棚卸しとblind棚卸しの差、すべてのfinding、採否理由、修正結果、残存リスクを個別に吟味し、問題確認済みfindingが最新版の本文全体で解決され、正しい意味関係が別箇所で再び破られていない。
6. blind inventoryの各 `semantic_assertion` を最新版へ適用しても、候補の境界・作用方向・包含/除外関係・一般化範囲に反する記述がない。

## REJECTの意味基準

上記のいずれかを満たさない場合は `REJECT` とする。blockerにできるのは、事実・語法・発音の誤り、例文/訳の誤り、主要語義・構文の欠落または過剰収録、根拠と本文の矛盾、内容仕様の必須項目違反、未判定・未解決項目である。各blockerには対象ID、問題、必要な修正を記録する。条件付き合格は使わない。

本文と矛盾しない分類粒度・棚卸し構成の差、より良い表現の提案、任意の改善余地は、それだけを理由に `REJECT` にせず、非blocking noteとして記録する。`REJECT` は審査失敗ではなく、問題を検出して完了した正常な最終判定である。

## 出力

`final_review_v2` JSONとして、全target/relation/normal candidate/blind candidate/finding/evidence/source-unionの個別結果、`decision` (`pass | reject`)、`blockers`、非blocking `notes` を返す。`PASS` は全個別結果がpass、未解決・holdが0件、blockerが0件の場合に限る。本文は変更しない。


## Input packet

```json
{
  "stage": "final_review",
  "entry_body": "\n＃発音記号\n\n米・英: /ɪnˈtens/。2音節で、第2音節の /tens/ に主強勢がある。  \n\n＃語源\n\n15世紀初頭に、フランス語を経てラテン語 intensus「引き伸ばされた、張り詰めた」から英語に入った。intensus は intendere の過去分詞に由来する。  \n\n現在の intense は、程度・力・感情などの強度や度合いが非常に高いことを表す。  \n\n＃語形成\n\n・intensity（名詞）— 強度、激しさ。  \n・intensify（動詞）— 強まる、強める。自動詞・他動詞の両方で使う。  \n・intensive（形容詞）— 集中的な、徹底的な。限られた期間・範囲に活動や資源を集中投入することを表す。intense と活動用法で重なる場合があるが、intense は強度・力・緊張・感情の高さに、intensive は集中投入の範囲・期間に焦点を置きやすい。  \n・intensification（名詞）— 強化、激化。  \n\n＃コアイメージ\n\n程度・力・エネルギー・感情の強度や度合いが非常に高い。対象により、経験される強さ、活動の負荷、または人・視線・関係に表れる強い感情として現れる。  \n\n・対象の程度・感覚・感情の強度が非常に高い → 「強烈な、非常に強い」（語義1）  \n・活動や行動の強度・エネルギー・努力・緊張や負荷が非常に高い → 「激しい、活動量の多い」（語義2）  \n・人・視線・表情・関係に強い感情や態度が表れる／強い結びつきがある → 「感情や態度の強い、張り詰めた」（語義3）  \n\n＃意味・用法・関連表現\n\n1. 【形容詞・限定／叙述】強烈な、非常に強い\n\n【日本語訳・定義】感情、感覚、痛み、暑さ、色、関心、圧力などの程度・強度が非常に高いこと。intense pleasure「非常に強い喜び」のように、好ましい対象にも使う。  \n\n【頻度】〈5/10〉  \n\n※Oxford 5000ではC1レベルの学習語彙。上の10段階は語義別の厳密な順位ではなく、学習上の相対的な目安である。  \n\n【レジスター/領域】一般語として使われる形容詞。  \n\n【文法パターン】intense + 〈感情・感覚・性質・熱・色などを表す名詞〉＝程度・強度が非常に高い～／intense energy・determination・concentration＝エネルギー・決意・集中の強度が非常に高い／under intense pressure/scrutiny＝強い圧力・厳しい監視の下で  \n\n【コロケーション】\n\n・intense pain  \n用途: 身体的な痛みが非常に強いことを表す。  \n例: He felt intense pain in his lower back.  \n訳: 彼は腰の下部に激しい痛みを感じた。  \n\n・intense heat  \n用途: 暑さや熱が非常に強いことを表す。  \n例: The intense heat made it dangerous to work outside.  \n訳: 強烈な暑さのため、屋外で働くのは危険だった。  \n\n・intense pressure  \n用途: 外部からかかる重圧や心理的な圧力が非常に強いことを表す。  \n例: The new manager is under intense pressure to improve the results.  \n訳: 新しい管理職は、業績を改善するよう非常に強い重圧を受けている。  \n\n・intense interest  \n用途: ある対象に向けられる関心が非常に強いことを表す。  \n例: The discovery attracted intense interest from researchers around the world.  \n訳: その発見は世界中の研究者から強い関心を集めた。  \n\n・intense anger  \n用途: 怒りの感情が非常に強いことを表す。  \n例: The decision provoked intense anger among local residents.  \n訳: その決定は地元住民の激しい怒りを引き起こした。  \n\n・intense blue  \n用途: 色の強さや濃さが際立ち、強い印象を与えることを表す。  \n例: The intense blue of the lake stood out against the white snow.  \n訳: 湖の鮮やかな青が白い雪を背景に際立っていた。  \n\n【語法・注意】intense は感情、感覚、熱、色、関心、圧力など、強さの対象を表す名詞と結びつく。intense pleasure のような好ましい対象にも、intense pain や intense anger のような好ましくない対象にも使える。  \n\n【類義語】\n\n・strong  \n定義: intense と比較される、幅広い「強い」を表す関連語。  \n頻度: 〈5/10〉  \n違い: strong は幅広い強さを表し、intense は感覚・感情などの強度が非常に高いことに焦点を置く。  \n例: intense pain  \n訳: 強い痛み。  \n\n・extreme  \n定義: intense と比較される、通常の範囲からの逸脱に焦点を置く関連語。  \n頻度: 〈5/10〉  \n違い: extreme は通常の範囲や限界からの逸脱に焦点があり、intense は体感や感情の強さにも使う。  \n例: intense heat  \n訳: 強烈な暑さ。  \n\n・powerful  \n定義: intense と比較される、作用する力や影響に焦点を置く関連語。  \n頻度: 〈5/10〉  \n違い: powerful は作用する力や影響力に焦点があり、intense は経験される強度や圧にも使う。  \n例: intense interest  \n訳: 強い関心。  \n\n2. 【形容詞・限定／叙述】激しい、活動量の多い\n\n【日本語訳・定義】活動・競争・議論・訓練などの強度、エネルギー、努力、緊張や負荷が非常に高いこと。短期集中を伴う場合にも使うが、短期間であることは必須ではない。  \n\n【頻度】〈5/10〉  \n\n【レジスター/領域】一般語として使われる形容詞。  \n\n【文法パターン】intense + 〈活動・競争・議論・訓練など〉＝強度・エネルギー・努力・緊張や負荷が非常に高い活動・競争など  \n\n【コロケーション】\n\n・intense competition  \n用途: 競争が非常に激しく、参加者に大きな努力や緊張を求めることを表す。  \n例: There is intense competition for places at the top universities.  \n訳: 一流大学の枠をめぐって激しい競争がある。  \n\n・intense activity  \n用途: 活動の強度・エネルギー・負荷が非常に高いことを表す。  \n例: The airport experienced a period of intense activity before the holiday.  \n訳: その空港では休暇前に活動が非常に活発な時期があった。  \n\n【語法・注意】intense は強度・力・緊張・感情が高いことを表し、intensive は限られた期間・範囲に活動や資源を集中投入することを表す傾向がある。活動用法では重なる場合があり、感情性・客観性だけを決め手にしない。  \n\n【類義語】\n\n・fierce  \n定義: intense と比較される、競争・対立の激しさに焦点を置く関連語。  \n頻度: 〈5/10〉  \n違い: fierce は攻撃性や対立を含みやすく、intense は敵意のない活動の強さにも使える。  \n例: intense competition  \n訳: 激しい競争。  \n\n・vigorous  \n定義: intense と比較される、活力や積極的なエネルギーに焦点を置く関連語。  \n頻度: 〈5/10〉  \n違い: vigorous は活力や積極的なエネルギーに焦点があり、intense は活動の緊張や負荷も表す。  \n例: intense activity  \n訳: 激しい活動。  \n\n・strenuous  \n定義: intense と比較される、大きな努力を要する行為に焦点を置く関連語。  \n頻度: 〈5/10〉  \n違い: strenuous は行為がきつく多大な努力を要することに焦点があり、intense は活動の緊張感や負荷も表す。  \n例: intense training  \n訳: 激しい訓練。  \n\n3. 【形容詞・人・視線・表情・関係】感情や態度の強い、張り詰めた\n\n【日本語訳・定義】人・視線・表情・関係などについて、強い感情や意見が表れる、強く感じられる、または強い感情的な結びつきがあること。人・表情の表出、人物への評価、関係の情緒的な強さを区別する。  \n\n【頻度】〈5/10〉  \n\n【レジスター/領域】一般語として使われる形容詞。  \n\n【文法パターン】an intense person＝感情や態度が強く、存在感や圧のある人（評価は文脈依存）／an intense look/gaze＝集中・鋭さ・強い感情を帯びた視線／an intense relationship＝情緒的な結びつきや相互作用が強い関係  \n\n【コロケーション】\n\n・an intense look  \n用途: 強い感情や集中を帯びた視線・表情を表す。  \n例: She gave him an intense look when he mentioned the accusation.  \n訳: 彼がその告発について話すと、彼女は彼に鋭く強い視線を向けた。  \n\n・an intense person  \n用途: 感情や態度が強く、存在感や圧のある人を表す。肯定・否定の評価は文脈で変わる。  \n例: He is an intense person who takes every project very seriously.  \n訳: 彼はどのプロジェクトにも非常に真剣に取り組む、強い存在感のある人だ。  \n\n・an intense relationship  \n用途: 感情的な結びつきや相互作用が非常に強い関係を表す。  \n例: Their intense relationship left little room for emotional distance.  \n訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。  \n\n【語法・注意】人への用法は強い感情や態度を持つという評価で、必ず外に表出するとは限らない。視線・表情では集中・鋭さ・感情の表れ、relationship では情緒的な結びつきや相互作用の強さを表す。  \n\n【類義語】\n\n・serious  \n定義: intense と比較される、真剣さや重要性に焦点を置く関連語。  \n頻度: 〈5/10〉  \n違い: serious は真面目さや重要性に焦点があり、intense は強い感情や張り詰めた印象も表す。  \n例: an intense person  \n訳: 感情や態度の強い人。  \n\n・passionate  \n定義: intense と比較される、熱意や強い関与に焦点を置く関連語。  \n頻度: 〈5/10〉  \n違い: passionate は熱意や強い関与を表し、intense より肯定的な評価になりやすい。  \n例: an intense look  \n訳: 強い視線。  \n\n・earnest  \n定義: intense と比較される、誠実さや真摯さに焦点を置く関連語。  \n頻度: 〈5/10〉  \n違い: earnest は誠実さや真摯さに焦点があり、intense は感情の強さや対人的な圧も表す。  \n例: an intense relationship  \n訳: 感情的な結びつきの強い関係。  ",
  "_output_metadata": {
    "schema_version": "final_review_v2",
    "stage": "final_review",
    "run_id": "blind-intense-20260905T043033Z-31a96a70",
    "context_id": "blind-intense-context-20260905T043033Z-31a96a70",
    "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
    "prompt_sha256": "3158e690b19b0f822a032dffa1cbfe1d38d64a0de2c1dba582554fa2b729f117",
    "input_artifacts": [
      "entry_body",
      "all_findings",
      "resolutions",
      "sealed_final_blind",
      "final_review_spec"
    ],
    "blind_output_sha256": "c2db53eb4d6f1b0404c60a6358187da30337779e5bddbcd739c0d43e7ca7a84f"
  },
  "pass_findings": {
    "schema_version": "normal_review_v2",
    "stage": "normal_review",
    "run_id": "normal-intense-20260905T043033Z-31a96a70",
    "context_id": "normal-intense-context-20260905T043033Z-31a96a70",
    "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
    "prompt_sha256": "5178f5a14a9525317811a34e6cd307108436f4babc1299fcd2eb9031f28ba737",
    "input_artifacts": [
      "router_selected_sections",
      "checker_pass_specs"
    ],
    "recorded_at": "2026-09-05T05:08:14.229080+00:00",
    "pass_outputs": [
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "translation",
        "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "codex-translation-handoff-20260905T043033Z-31a96a70"
        },
        "findings": [
          {
            "taxonomy_id": "example_translation_alignment",
            "location": {
              "section": "collocations_examples",
              "line_start": 122,
              "line_end": 122,
              "exact_quote": "用途: 競争が非常に激しく、参加者に大きな努力や緊張を求めることを表す。"
            },
            "severity": "blocking",
            "rationale": "「intense competition」は競争の強度・激しさを表すが、参加者に大きな努力や緊張を求めることまで必ず含意しない。「参加者に…求める」とすると、原文の強度の説明に、参加者への要求という追加の関係を加えている。",
            "evidence_link_ids": [],
            "suggested_direction": "競争の強度・激しさが非常に高いことを表す、とするなど、参加者への努力・緊張の要求を断定しない方向に直す。"
          }
        ]
      },
      {
        "pass_id": "sense-structure",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "sense-structure-20260905T043033Z-31a96a70"
        },
        "findings": [
          {
            "taxonomy_id": "sense_boundary_overlap",
            "location": {
              "section": "sense_structure",
              "line_start": 111,
              "line_end": 111,
              "exact_quote": "【日本語訳・定義】活動・競争・議論・訓練などの強度、エネルギー、努力、緊張や負荷が非常に高いこと。短期集中を伴う場合にも使うが、短期間であることは必須ではない。  "
            },
            "severity": "blocking",
            "rationale": "語義1も語義2も、対象の程度・強度が非常に高いという同じスカラー意味を述べている。語義2で短期間を必須条件から外しているため、現在の境界は活動・競争・議論・訓練という対象領域と、それに伴う努力・負荷を挙げただけになり、語義1の文法パターンにある intense energy・determination・concentration や pressure とも重なる。活動用法を独立語義として残すなら、対象分野以外の必須となる意味的差異が必要である。",
            "evidence_link_ids": [],
            "suggested_direction": "語義1と2を統合し、活動・競争・訓練のコロケーションと intensive との対比を一般義の語法注記へ移す。分ける場合は、活動義に対象領域だけではない独立した中心意味・結果状態・負荷の条件を明示する。"
          },
          {
            "taxonomy_id": "cross_section_internal_contradiction",
            "location": {
              "section": "core_image",
              "line_start": 36,
              "line_end": 36,
              "exact_quote": "・人・視線・表情・関係に強い感情や態度が表れる／強い結びつきがある → 「感情や態度の強い、張り詰めた」（語義3）  "
            },
            "severity": "minor",
            "rationale": "コアイメージは人にも強い感情や態度が外に表れると記述しているが、語義3の語法注記は、人への用法が強い感情や態度を持つという人物評価であり、必ず外に表出するとは限らないと明示する。視線・表情の表出、人物への評価、関係の情緒的な強さを同じ表出条件で表すため、セクション間で人用法の意味範囲が一致していない。",
            "evidence_link_ids": [],
            "suggested_direction": "人については「強い感情や態度が感じられる／そうした人物と評価される」とし、外的な表出は視線・表情に限定するようコアイメージの枝を修正する。"
          }
        ]
      },
      {
        "pass_id": "frame-relation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "agent-frame-relation-stage1-31a96a70"
        },
        "antonym_axis_blind_record": {
          "schema_version": "antonym_axis_blind_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
          "blind_request_sha256": "12baa8d9929aa1dceed6f2ef9d86d8309df6ebe453a5077882e7e52252112d25",
          "recorded_at": "2026-09-05T04:39:05Z",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "agent-frame-relation-stage1-31a96a70"
          },
          "axes": []
        },
        "antonym_axis_adjudication_record": {
          "schema_version": "antonym_axis_adjudication_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
          "stage2_request_sha256": "210fe411d58762321f5392a96277c932c1a509fbda617127282057279cbf208b",
          "blind_record_sha256": "fe6c8b9bb0c53f45438baf55e045ee32989d28db77f1cada52386133a7f26c6d",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "agent-frame-relation-stage1-31a96a70"
          },
          "adjudications": [],
          "frame_findings": [
            {
              "taxonomy_id": "lexical_relation_mislabel",
              "location": {
                "section": "lexical_relations",
                "line_start": 201,
                "line_end": 206,
                "exact_quote": "・earnest\n定義: intense と比較される、誠実さや真摯さに焦点を置く関連語。\n頻度: 〈5/10〉\n違い: earnest は誠実さや真摯さに焦点があり、intense は感情の強さや対人的な圧も表す。\n例: an intense relationship\n訳: 感情的な結びつきの強い関係。"
              },
              "severity": "minor",
              "rationale": "In sense 3, earnest centers on sincerity and earnestness rather than the sense's central emotional or attitudinal intensity and strong emotional bond. The example and translation repeat an intense relationship instead of realizing earnest, so this is only a related word, not a sufficiently central synonym for this entry.",
              "evidence_link_ids": [],
              "suggested_direction": "削除"
            }
          ],
          "unrouted_observations": []
        },
        "aligned_at": "2026-09-05T05:16:35.396327+00:00",
        "findings": [
          {
            "taxonomy_id": "lexical_relation_mislabel",
            "location": {
              "section": "lexical_relations",
              "line_start": 201,
              "line_end": 206,
              "exact_quote": "・earnest\n定義: intense と比較される、誠実さや真摯さに焦点を置く関連語。\n頻度: 〈5/10〉\n違い: earnest は誠実さや真摯さに焦点があり、intense は感情の強さや対人的な圧も表す。\n例: an intense relationship\n訳: 感情的な結びつきの強い関係。"
            },
            "severity": "minor",
            "rationale": "In sense 3, earnest centers on sincerity and earnestness rather than the sense's central emotional or attitudinal intensity and strong emotional bond. The example and translation repeat an intense relationship instead of realizing earnest, so this is only a related word, not a sufficiently central synonym for this entry.",
            "evidence_link_ids": [],
            "suggested_direction": "削除"
          }
        ],
        "unrouted_observations": []
      },
      {
        "pass_id": "example-attribution",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a06fe0-31a9-7a70-b6a0-4f8d2c91e3ab"
        },
        "blind_attribution_record": {
          "schema_version": "example_attribution_blind_record_v1",
          "pass_id": "example-attribution",
          "stage": 1,
          "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
          "blind_request_sha256": "fec74fdec576fbf8f3dee99795b187454db8c77f995275cee84ab2a18ac8d0e3",
          "recorded_at": "2026-09-05T04:40:07Z",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "01a06fe0-31a9-7a70-b6a0-4f8d2c91e3ab"
          },
          "attributions": [
            {
              "example_id": "ex-618b1e2d1835",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "intense activity"
              ],
              "rationale": "「intense activity」は activity という活動・出来事そのものの強度を述べる。sense:001なら痛み・熱・関心など対象の程度、sense:003なら人や関係の感情的な強さを述べるが、この文では intense が修飾するのは活動そのものなので sense:002 が最も自然である。"
            },
            {
              "example_id": "ex-f10457dba432",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "under intense pressure"
              ],
              "rationale": "「under intense pressure」では pressure という重圧・心理的負担の強度が述べられている。sense:002は活動自体の強度、sense:003は人や表情の強い態度を表すが、managerや改善行動は背景であり、intense が直接修飾する pressure には sense:001 が適合する。"
            },
            {
              "example_id": "ex-f137e090eaf0",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "gave him an intense look"
              ],
              "rationale": "「gave him an intense look」は相手に向けられた look が告発への強い反応や緊張を伝える構文である。sense:001の一般的な程度の高さとして視覚的性質を述べる読みも考えられるが、この文で修飾されるのは色や感覚ではなく対人的な視線なので sense:003 が最も自然である。"
            },
            {
              "example_id": "ex-aecfe7e4a6f2",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "intense interest"
              ],
              "rationale": "「intense interest」は interest という関心・心理状態の強度を表す。sense:003なら研究者などの人や表情・関係を修飾するが、この文では researchers は関心の担い手にすぎず、intense の修飾対象は interest そのものなので sense:001 が適合する。"
            },
            {
              "example_id": "ex-e0190302d4ac",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "intense competition"
              ],
              "rationale": "「intense competition」は places をめぐって参加者が競い合う活動・過程の激しさを表す。sense:001の感情や感覚の強度として読む余地はあるが、この文で intense が修飾するのは感情ではなく competition という活動であり、sense:003の人物・関係用法でもないため sense:002 が最も自然である。"
            },
            {
              "example_id": "ex-291ac3c2eaad",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "intense pain"
              ],
              "rationale": "「intense pain」は lower back に感じる pain という身体感覚の強度を表す。sense:002は活動・行動の負荷、sense:003は人や表情・関係の感情的な強さを表すが、ここで修飾されるのは人の態度ではなく痛みそのものなので sense:001 が適合する。"
            },
            {
              "example_id": "ex-46cb08cdd57e",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "intense anger"
              ],
              "rationale": "「intense anger」は decision が引き起こした anger という感情の強度を表す。sense:003なら residents の人やその表情が強い感情を示すことになるが、among local residents は感情の担い手を示すだけで、intense の修飾対象は anger なので sense:001 が最も自然である。"
            },
            {
              "example_id": "ex-19eac558e240",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "intense blue"
              ],
              "rationale": "「intense blue」は lake の blue という色の視覚的な強さ・濃さを表し、white snow との対比で際立つ。sense:002の活動強度や sense:003の人・視線・関係の感情的強さでは、この色名を直接修飾する使われ方を説明できないため sense:001 が一意である。"
            },
            {
              "example_id": "ex-b5f7e74a14c5",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "intense person",
                "very seriously"
              ],
              "rationale": "「intense person」と「very seriously」は、主語である人の性格・態度の真剣さと感情的な強さを直接述べる。sense:002なら project や取り組みという活動自体が intense になるはずだが、文の修飾対象は活動ではなく person なので sense:003 が最も自然である。"
            },
            {
              "example_id": "ex-e7ed333e39d3",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:003"
              ],
              "discriminating_terms": [
                "intense relationship",
                "emotional distance"
              ],
              "rationale": "「intense relationship」と「emotional distance」は、二者間の感情的な結びつきや相互作用の強さを示す。sense:001の個別の感情・感覚の強度や sense:002の活動の激しさでは、relationshipそのものと距離の置きにくさを修飾するこの構文を説明できないため sense:003 が一意である。"
            },
            {
              "example_id": "ex-c01abcd41d78",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "intense heat"
              ],
              "rationale": "「intense heat」は屋外作業を危険にする heat という熱・暑さの強度を表す。sense:002の活動用法なら work 自体の負荷を修飾するが、work outside は結果に関わる背景行動であり、intense が直接かかる heat には sense:001 が適合する。"
            }
          ],
          "findings": []
        },
        "aligned_at": "2026-09-05T05:08:14.225802+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "qualification",
        "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "codex-qualification-handoff-20260905T043033Z-31a96a70"
        },
        "findings": [
          {
            "taxonomy_id": "regional_qualification",
            "location": {
              "section": "frequency_register",
              "line_start": 44,
              "line_end": 44,
              "exact_quote": "【頻度】〈5/10〉"
            },
            "severity": "minor",
            "rationale": "「【頻度】〈5/10〉」を3語義に一律付しているが、直後の注記はこの数値を学習上の相対的な目安としており、英語全体での遭遇頻度を示す尺度・根拠になっていない。Oxford 5000のC1も学習到達度であって頻度ではなく、語義ごとの頻度差や主要構文の優先度を判断できない。",
            "evidence_link_ids": [],
            "suggested_direction": "英語全体のコーパス頻度に基づく尺度と根拠を示すか、5/10とC1を学習レベル・学習上の目安として頻度欄から分離し、必要なら語義・構文ごとの頻度差を注記する。"
          }
        ]
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "pronunciation",
        "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "codex-pronunciation-handoff-20260905T043033Z-31a96a70"
        },
        "findings": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "evidence",
        "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "codex-evidence-handoff-20260905T043033Z-31a96a70"
        },
        "findings": [
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 88,
              "line_end": 93,
              "exact_quote": "・strong  \\n定義: intense と比較される、幅広い「強い」を表す関連語。  \\n頻度: 〈5/10〉  \\n違い: strong は幅広い強さを表し、intense は感覚・感情などの強度が非常に高いことに焦点を置く。  \\n例: intense pain  \\n訳: 強い痛み。  "
            },
            "severity": "blocking",
            "rationale": "EVID-001の根拠はintenseの中心義を支えるが、strong自体の定義・頻度・例文およびstrongとintenseの差を直接支持しない。",
            "evidence_link_ids": [
              "EVID-001"
            ],
            "suggested_direction": "strongを直接扱う根拠へ差し替えるか、定義・頻度・比較を削除または限定してholdする。"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 95,
              "line_end": 100,
              "exact_quote": "・extreme  \\n定義: intense と比較される、通常の範囲からの逸脱に焦点を置く関連語。  \\n頻度: 〈5/10〉  \\n違い: extreme は通常の範囲や限界からの逸脱に焦点があり、intense は体感や感情の強さにも使う。  \\n例: intense heat  \\n訳: 強烈な暑さ。  "
            },
            "severity": "blocking",
            "rationale": "EVID-001はintenseが極端な強度を表すことは支えるが、extremeの定義・頻度・例文や両語の意味境界を直接支持しない。",
            "evidence_link_ids": [
              "EVID-001"
            ],
            "suggested_direction": "extremeの比較を直接支持する根拠へ差し替えるか、比較・頻度・例文を削除または限定してholdする。"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 102,
              "line_end": 107,
              "exact_quote": "・powerful  \\n定義: intense と比較される、作用する力や影響に焦点を置く関連語。  \\n頻度: 〈5/10〉  \\n違い: powerful は作用する力や影響力に焦点があり、intense は経験される強度や圧にも使う。  \\n例: intense interest  \\n訳: 強い関心。  "
            },
            "severity": "blocking",
            "rationale": "EVID-001の根拠にはpowerful自体の定義・頻度・例文、作用する力と経験される強度の対比を裏付ける事実がない。",
            "evidence_link_ids": [
              "EVID-001"
            ],
            "suggested_direction": "powerfulを直接扱う根拠へ差し替えるか、比較欄を削除または限定してholdする。"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 135,
              "line_end": 140,
              "exact_quote": "・fierce  \\n定義: intense と比較される、競争・対立の激しさに焦点を置く関連語。  \\n頻度: 〈5/10〉  \\n違い: fierce は攻撃性や対立を含みやすく、intense は敵意のない活動の強さにも使える。  \\n例: intense competition  \\n訳: 激しい競争。  "
            },
            "severity": "blocking",
            "rationale": "EVID-002はintenseの活動・競争用法を支えるが、fierceの定義・頻度・例文および攻撃性との対比を直接支持しない。",
            "evidence_link_ids": [
              "EVID-002"
            ],
            "suggested_direction": "fierceを直接扱う根拠へ差し替えるか、定義・頻度・比較を削除または限定してholdする。"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 142,
              "line_end": 147,
              "exact_quote": "・vigorous  \\n定義: intense と比較される、活力や積極的なエネルギーに焦点を置く関連語。  \\n頻度: 〈5/10〉  \\n違い: vigorous は活力や積極的なエネルギーに焦点があり、intense は活動の緊張や負荷も表す。  \\n例: intense activity  \\n訳: 激しい活動。  "
            },
            "severity": "blocking",
            "rationale": "EVID-002の根拠にはvigorousの定義・頻度・例文やvigorousとintenseの焦点の差を裏付ける事実がない。",
            "evidence_link_ids": [
              "EVID-002"
            ],
            "suggested_direction": "vigorousを直接扱う根拠へ差し替えるか、比較欄を削除または限定してholdする。"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 149,
              "line_end": 154,
              "exact_quote": "・strenuous  \\n定義: intense と比較される、大きな努力を要する行為に焦点を置く関連語。  \\n頻度: 〈5/10〉  \\n違い: strenuous は行為がきつく多大な努力を要することに焦点があり、intense は活動の緊張感や負荷も表す。  \\n例: intense training  \\n訳: 激しい訓練。  "
            },
            "severity": "blocking",
            "rationale": "EVID-002はintenseの活動強度を支えるだけで、strenuousの定義・頻度・例文や両語の意味範囲を直接支持しない。",
            "evidence_link_ids": [
              "EVID-002"
            ],
            "suggested_direction": "strenuousを直接扱う根拠へ差し替えるか、比較・頻度・例文を削除または限定してholdする。"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 192,
              "line_end": 197,
              "exact_quote": "訳: 感情や態度の強い人。  \\n\\n・passionate  \\n定義: intense と比較される、熱意や強い関与に焦点を置く関連語。  \\n頻度: 〈5/10〉  \\n違い: passionate は熱意や強い関与を表し、intense より肯定的な評価になりやすい。  "
            },
            "severity": "blocking",
            "rationale": "EVID-003はintenseの人・表情に関する用法を支えるが、seriousの定義・頻度・例文および両語の焦点の差を直接支持しない。",
            "evidence_link_ids": [
              "EVID-003"
            ],
            "suggested_direction": "seriousを直接扱う根拠へ差し替えるか、定義・頻度・比較を削除または限定してholdする。"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 199,
              "line_end": 204,
              "exact_quote": "訳: 強い視線。  \\n\\n・earnest  \\n定義: intense と比較される、誠実さや真摯さに焦点を置く関連語。  \\n頻度: 〈5/10〉  \\n違い: earnest は誠実さや真摯さに焦点があり、intense は感情の強さや対人的な圧も表す。  "
            },
            "severity": "blocking",
            "rationale": "EVID-003の根拠にはpassionateの定義・頻度・例文や肯定的評価との対比を裏付ける事実がない。",
            "evidence_link_ids": [
              "EVID-003"
            ],
            "suggested_direction": "passionateを直接扱う根拠へ差し替えるか、比較・頻度・例文を削除または限定してholdする。"
          },
          {
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "lexical_relations",
              "line_start": 206,
              "line_end": 211,
              "exact_quote": "訳: 感情的な結びつきの強い関係。  "
            },
            "severity": "blocking",
            "rationale": "EVID-003の根拠にあるearnestnessはintenseの説明の一部にすぎず、earnest自体の定義・頻度・例文や両語の差を直接支持しない。",
            "evidence_link_ids": [
              "EVID-003"
            ],
            "suggested_direction": "earnestを直接扱う根拠へ差し替えるか、比較・頻度・例文を削除または限定してholdする。"
          }
        ]
      }
    ],
    "checker_reviewers": {
      "translation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "codex-translation-handoff-20260905T043033Z-31a96a70"
      },
      "sense-structure": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "sense-structure-20260905T043033Z-31a96a70"
      },
      "frame-relation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "agent-frame-relation-stage1-31a96a70"
      },
      "example-attribution": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a06fe0-31a9-7a70-b6a0-4f8d2c91e3ab"
      },
      "qualification": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "codex-qualification-handoff-20260905T043033Z-31a96a70"
      },
      "pronunciation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "codex-pronunciation-handoff-20260905T043033Z-31a96a70"
      },
      "evidence": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "codex-evidence-handoff-20260905T043033Z-31a96a70"
      }
    },
    "independent_candidates": [],
    "summary": "Independent checker passes completed by parallel handoff; frame-relation preserved its serial blind/adjudication dependency."
  },
  "cold_review": {
    "reviewer_provenance": {
      "reviewer_role": "independent_context_free_cold_reviewer",
      "stage": "cold_review",
      "review_basis": "entry_body_only",
      "session_mode": "separate_model_session",
      "run_id": "cold-intense-20260905T043033Z-31a96a70",
      "context_id": "cold-intense-context-20260905T043033Z-31a96a70",
      "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
    },
    "summary": "問題候補9件。特に intensive との対比、語義1・2の境界、人物・関係に対する語義3の説明には、学習者の誤った一般化につながる余地がある。その他は語源年代、コロケーションの射程、訳語・類義語の精度に関する軽微な問題である。",
    "findings": [
      {
        "id": "CR-001",
        "location": "＃語源・英語への流入時期",
        "severity": "low",
        "description": "英語への流入時期を「15世紀初頭」と断定している点は、初出時期と後の比喩的用法の成立を混同している可能性がある。",
        "reason": "intense は一般的な語源記述では14世紀後半から英語に見られ、15世紀には比喩的な用法が発達したと説明されることが多い。現在の文面のままだと、英語に入った時期を遅く伝える。 対象本文: 15世紀初頭に、フランス語を経てラテン語 intensus「引き伸ばされた、張り詰めた」から英語に入った。",
        "suggested_direction": "英語での初出を14世紀後半とし、15世紀の比喩義を述べたい場合は初出とは分けて記載する。フランス語経由とラテン語起源の関係も資料に即して整理する。",
        "scope_anchors": [
          {
            "id": "CR-001-A1",
            "exact_quote": "15世紀初頭に、フランス語を経てラテン語 intensus「引き伸ばされた、張り詰めた」から英語に入った。",
            "location_hint": "＃語源の最初の文"
          }
        ]
      },
      {
        "id": "CR-002",
        "location": "＃語形成・intensive／語義2・語法・注意",
        "severity": "medium",
        "description": "intensive を「限られた期間・範囲」への活動・資源の集中投入で特徴づけており、期間や範囲の限定が語の中核条件であるように読める。",
        "reason": "intensive は活動・努力・資源投入の度合いが高い、集中的・徹底的であるという意味で、短期性や有限範囲は用法によって現れる特徴にすぎない。intensive research や intensive care などでは、この文面の期間・範囲の条件は一律には成立しない。 対象本文: intensive（形容詞）— 集中的な、徹底的な。限られた期間・範囲に活動や資源を集中投入することを表す。intense と活動用法で重なる場合があるが、intense は強度・力・緊張・感情の高さに、intensive は集中投入の範囲・期間に焦点を置きやすい。／intense は強度・力・緊張・感情が高いことを表し、intensive は限られた期間・範囲に活動や資源を集中投入することを表す傾向がある。活動用法では重なる場合があり、感情性・客観性だけを決め手にしない。",
        "suggested_direction": "短期・限定範囲は典型例の一部として示し、intensive の中心を「集中・高密度・徹底性」に置く。intense との違いは、感じられる強烈さ・活動の高い強度と、集中や高密度・徹底性の対比として説明する。",
        "scope_anchors": [
          {
            "id": "CR-002-A1",
            "exact_quote": "intensive（形容詞）— 集中的な、徹底的な。限られた期間・範囲に活動や資源を集中投入することを表す。intense と活動用法で重なる場合があるが、intense は強度・力・緊張・感情の高さに、intensive は集中投入の範囲・期間に焦点を置きやすい。",
            "location_hint": "＃語形成の intensive の項目"
          },
          {
            "id": "CR-002-A2",
            "exact_quote": "intense は強度・力・緊張・感情が高いことを表し、intensive は限られた期間・範囲に活動や資源を集中投入することを表す傾向がある。活動用法では重なる場合があり、感情性・客観性だけを決め手にしない。",
            "location_hint": "語義2の【語法・注意】"
          }
        ]
      },
      {
        "id": "CR-003",
        "location": "コアイメージと語義1・語義2の区分",
        "severity": "medium",
        "description": "語義1と語義2の分割が、実際の対象の重なりを十分に示しておらず、互いに別の意味であるように見える。",
        "reason": "intense は感覚・感情・心理状態・圧力・活動のいずれにも、基本的に「強度が高い」という同じ尺度的な意味で使われる。本文でも energy・determination・concentration を語義1に置く一方、activity・競争・訓練を語義2に置いており、どこからが別義なのかを判定する基準がないため、学習者が対象名詞ごとの固定的な訳語規則を作りやすい。 対象本文: ・対象の程度・感覚・感情の強度が非常に高い → 「強烈な、非常に強い」（語義1）／・活動や行動の強度・エネルギー・努力・緊張や負荷が非常に高い → 「激しい、活動量の多い」（語義2）／intense energy・determination・concentration＝エネルギー・決意・集中の強度が非常に高い／活動・競争・議論・訓練などの強度、エネルギー、努力、緊張や負荷が非常に高いこと。短期集中を伴う場合にも使うが、短期間であることは必須ではない。",
        "suggested_direction": "語義1・2は相互排他的な別義ではなく、同じ強度のコアイメージからの使用域のまとまりだと明示する。「経験される感覚・状態」と「活動のペース・努力・負荷」のように、何の強さを見ているかで整理し、concentration や pressure のような共有領域を注記する。",
        "scope_anchors": [
          {
            "id": "CR-003-A1",
            "exact_quote": "・対象の程度・感覚・感情の強度が非常に高い → 「強烈な、非常に強い」（語義1）",
            "location_hint": "＃コアイメージの語義1への矢印"
          },
          {
            "id": "CR-003-A2",
            "exact_quote": "・活動や行動の強度・エネルギー・努力・緊張や負荷が非常に高い → 「激しい、活動量の多い」（語義2）",
            "location_hint": "＃コアイメージの語義2への矢印"
          },
          {
            "id": "CR-003-A3",
            "exact_quote": "intense energy・determination・concentration＝エネルギー・決意・集中の強度が非常に高い",
            "location_hint": "語義1の【文法パターン】"
          },
          {
            "id": "CR-003-A4",
            "exact_quote": "活動・競争・議論・訓練などの強度、エネルギー、努力、緊張や負荷が非常に高いこと。短期集中を伴う場合にも使うが、短期間であることは必須ではない。",
            "location_hint": "語義2の【日本語訳・定義】"
          }
        ]
      },
      {
        "id": "CR-004",
        "location": "語義2・intense activity",
        "severity": "low",
        "description": "intense activity の説明が努力・緊張・負荷の高い活動に寄りすぎている。空港の例は、個々の活動が身体的に激しいというより、業務の量・ペース・忙しさが非常に高い用法である。",
        "reason": "この定義と例文訳のずれにより、学習者が intense activity を必ず高負荷な活動と一般化し、「活動が盛ん・忙しい」という a period of intense activity の用法を取りこぼす。 対象本文: 活動・競争・議論・訓練などの強度、エネルギー、努力、緊張や負荷が非常に高いこと。短期集中を伴う場合にも使うが、短期間であることは必須ではない。／用途: 活動の強度・エネルギー・負荷が非常に高いことを表す。／例: The airport experienced a period of intense activity before the holiday.／訳: その空港では休暇前に活動が非常に活発な時期があった。",
        "suggested_direction": "活動量・忙しさ・活動の盛んな状態も説明に含め、空港の例は「業務が非常に忙しい時期」など、量やペースを含む訳にする。",
        "scope_anchors": [
          {
            "id": "CR-004-A1",
            "exact_quote": "活動・競争・議論・訓練などの強度、エネルギー、努力、緊張や負荷が非常に高いこと。短期集中を伴う場合にも使うが、短期間であることは必須ではない。",
            "location_hint": "語義2の【日本語訳・定義】"
          },
          {
            "id": "CR-004-A2",
            "exact_quote": "用途: 活動の強度・エネルギー・負荷が非常に高いことを表す。",
            "location_hint": "語義2の intense activity の用途"
          },
          {
            "id": "CR-004-A3",
            "exact_quote": "例: The airport experienced a period of intense activity before the holiday.",
            "location_hint": "語義2の intense activity の例文"
          },
          {
            "id": "CR-004-A4",
            "exact_quote": "訳: その空港では休暇前に活動が非常に活発な時期があった。",
            "location_hint": "語義2の intense activity の訳"
          }
        ]
      },
      {
        "id": "CR-005",
        "location": "語義1・intense blue",
        "severity": "low",
        "description": "色について「濃さ」と説明すると、intense blue が必ず暗い色・濃い色を指すように読める。",
        "reason": "色の intense は通常、鮮やかさ・彩度・鮮明さや視覚的な強い印象を表し、暗さや明度の低さを含意しない。訳の「鮮やかな青」は適切な方向だが、用途説明の「濃さ」と揃っていない。 対象本文: 用途: 色の強さや濃さが際立ち、強い印象を与えることを表す。／訳: 湖の鮮やかな青が白い雪を背景に際立っていた。",
        "suggested_direction": "「鮮やかさ・彩度・鮮明さが際立つ」などに置き換え、暗い青に限らないことを明記する。",
        "scope_anchors": [
          {
            "id": "CR-005-A1",
            "exact_quote": "用途: 色の強さや濃さが際立ち、強い印象を与えることを表す。",
            "location_hint": "語義1の intense blue の用途"
          },
          {
            "id": "CR-005-A2",
            "exact_quote": "訳: 湖の鮮やかな青が白い雪を背景に際立っていた。",
            "location_hint": "語義1の intense blue の訳"
          }
        ]
      },
      {
        "id": "CR-006",
        "location": "語義1・文法パターン・scrutiny の訳",
        "severity": "low",
        "description": "scrutiny を「監視」と固定しているため、厳しい精査・吟味という広い意味が狭められている。",
        "reason": "under intense scrutiny は、人物・発言・計画などが報道、世論、法的手続き、専門家などから厳しく調べられる状況にも使う。監視だけとすると、物理的な見張りに限定する誤解が生じる。 対象本文: under intense pressure/scrutiny＝強い圧力・厳しい監視の下で",
        "suggested_direction": "「厳しい精査の下で」「厳しい目にさらされて」などを基本訳にし、文脈によって監視・吟味になると補足する。",
        "scope_anchors": [
          {
            "id": "CR-006-A1",
            "exact_quote": "under intense pressure/scrutiny＝強い圧力・厳しい監視の下で",
            "location_hint": "語義1の【文法パターン】末尾"
          }
        ]
      },
      {
        "id": "CR-007",
        "location": "語義3・an intense person",
        "severity": "medium",
        "description": "人に対する intense を「存在感や圧のある人」と寄せすぎており、コアイメージの「感情が表れる」と後段の「必ず外に表出するとは限らない」も緊張している。",
        "reason": "an intense person は、強い感情だけでなく、非常に真剣・熱心・集中している、感情的に圧倒される、あるいは一緒にいると負担に感じる、といった文脈依存の評価を表しうる。存在感や圧は一部の読みであり、外見上の表出も必須ではないため、現在の説明だけでは意味の幅を誤って固定しやすい。 対象本文: 対象により、経験される強さ、活動の負荷、または人・視線・関係に表れる強い感情として現れる。／【日本語訳・定義】人・視線・表情・関係などについて、強い感情や意見が表れる、強く感じられる、または強い感情的な結びつきがあること。人・表情の表出、人物への評価、関係の情緒的な強さを区別する。／an intense person＝感情や態度が強く、存在感や圧のある人（評価は文脈依存）／用途: 感情や態度が強く、存在感や圧のある人を表す。肯定・否定の評価は文脈で変わる。／【語法・注意】人への用法は強い感情や態度を持つという評価で、必ず外に表出するとは限らない。",
        "suggested_direction": "「感情・性格・取り組み方が強烈で、真剣・熱心、または圧倒的に感じられる人への評価」と広げ、肯定・否定・負担感のいずれにもなりうることを例とともに示す。人の用法を感情の外的表出とは分けてコアイメージにも反映する。",
        "scope_anchors": [
          {
            "id": "CR-007-A1",
            "exact_quote": "対象により、経験される強さ、活動の負荷、または人・視線・関係に表れる強い感情として現れる。",
            "location_hint": "＃コアイメージの説明文"
          },
          {
            "id": "CR-007-A2",
            "exact_quote": "【日本語訳・定義】人・視線・表情・関係などについて、強い感情や意見が表れる、強く感じられる、または強い感情的な結びつきがあること。人・表情の表出、人物への評価、関係の情緒的な強さを区別する。",
            "location_hint": "語義3の【日本語訳・定義】"
          },
          {
            "id": "CR-007-A3",
            "exact_quote": "an intense person＝感情や態度が強く、存在感や圧のある人（評価は文脈依存）",
            "location_hint": "語義3の【文法パターン】"
          },
          {
            "id": "CR-007-A4",
            "exact_quote": "用途: 感情や態度が強く、存在感や圧のある人を表す。肯定・否定の評価は文脈で変わる。",
            "location_hint": "語義3の an intense person の用途"
          },
          {
            "id": "CR-007-A5",
            "exact_quote": "【語法・注意】人への用法は強い感情や態度を持つという評価で、必ず外に表出するとは限らない。",
            "location_hint": "語義3の【語法・注意】冒頭"
          }
        ]
      },
      {
        "id": "CR-008",
        "location": "語義3・an intense relationship",
        "severity": "medium",
        "description": "intense relationship を主に「強い情緒的な結びつき」と説明しており、親密で肯定的な関係に寄りすぎている。",
        "reason": "intense relationship は感情的に強烈・濃密であることを表すが、親密さや強い絆だけでなく、執着、緊張、衝突、不安定さなどを含む関係にも使える。intimate relationship や close relationship と同義だと誤解される余地がある。 対象本文: an intense relationship＝情緒的な結びつきや相互作用が強い関係／用途: 感情的な結びつきや相互作用が非常に強い関係を表す。／訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。／relationship では情緒的な結びつきや相互作用の強さを表す。",
        "suggested_direction": "「感情的に強烈で、親密にも緊張をはらむこともある関係」とし、強い絆を必ずしも含意しないこと、肯定・否定の評価が文脈依存であることを補足する。",
        "scope_anchors": [
          {
            "id": "CR-008-A1",
            "exact_quote": "an intense relationship＝情緒的な結びつきや相互作用が強い関係",
            "location_hint": "語義3の【文法パターン】"
          },
          {
            "id": "CR-008-A2",
            "exact_quote": "用途: 感情的な結びつきや相互作用が非常に強い関係を表す。",
            "location_hint": "語義3の an intense relationship の用途"
          },
          {
            "id": "CR-008-A3",
            "exact_quote": "訳: 彼らの濃密な関係には、感情的な距離を置く余地がほとんどなかった。",
            "location_hint": "語義3の an intense relationship の訳"
          },
          {
            "id": "CR-008-A4",
            "exact_quote": "relationship では情緒的な結びつきや相互作用の強さを表す。",
            "location_hint": "語義3の【語法・注意】末尾"
          }
        ]
      },
      {
        "id": "CR-009",
        "location": "語義1・類義語・extreme",
        "severity": "low",
        "description": "extreme と intense の違いを一方向に整理しており、extreme も感覚・感情・熱などの名詞を自然に修飾するという重なりが見えない。",
        "reason": "extreme pain、extreme anger、extreme heat などは通常の用法であり、extreme が感情や体感に使えないわけではない。現在の対比だと、学習者が「感情には intense、限界には extreme」と固定的に一般化しやすい。 対象本文: 違い: extreme は通常の範囲や限界からの逸脱に焦点があり、intense は体感や感情の強さにも使う。",
        "suggested_direction": "両語が痛み・感情・熱などで重なることを先に示し、extreme は尺度の端・通常範囲からの逸脱、intense は経験される強烈さや作用の強さに焦点を置く傾向として説明する。",
        "scope_anchors": [
          {
            "id": "CR-009-A1",
            "exact_quote": "違い: extreme は通常の範囲や限界からの逸脱に焦点があり、intense は体感や感情の強さにも使う。",
            "location_hint": "語義1の extreme の【類義語】の違い"
          }
        ]
      }
    ],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "01a07002-2009-7a72-8c77-13175b5190b6"
    },
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-intense-20260905T043033Z-31a96a70",
    "context_id": "cold-intense-context-20260905T043033Z-31a96a70",
    "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
    "prompt_sha256": "0ed4409a73095a9a2968bdcdb20bc397be345af84bff2c3558a48f08a5488aae",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-05T05:28:15.096164+00:00"
  },
  "final_blind": {
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-intense-20260905T043033Z-31a96a70",
    "context_id": "blind-intense-context-20260905T043033Z-31a96a70",
    "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
    "prompt_sha256": "1bb7b1a1c7f589a50a704d1ce6c1ecd0bfb1c9fb689fd481d21bf608438eb7b5",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false,
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "01a0700a-7831-79f1-9f58-d9e7cb4cf08c"
    },
    "provisional_decision": "reject",
    "independent_candidates": [
      {
        "id": "IC-001",
        "surface_form": "intense",
        "frame": "intense + <sensation, emotion, quality, or physical-property noun>",
        "meaning": "very great or very strong degree",
        "disposition": "included",
        "rationale": "The intense + <sensation, emotion, quality, or physical-property noun> frame is covered by the article's general high-degree sense.",
        "semantic_assertions": [
          {
            "id": "IC-001:A1",
            "statement": "The modified referent must have an extreme degree of strength, force, or amount, without intensity alone fixing positive or negative valence.",
            "polarity": "must_hold",
            "scope": "core image, first sense, usage note, and examples"
          }
        ]
      },
      {
        "id": "IC-002",
        "surface_form": "intense",
        "frame": "intense + <activity, competition, discussion, or training noun>",
        "meaning": "very high activity or effort intensity",
        "disposition": "included",
        "rationale": "The intense + <activity, competition, discussion, or training noun> frame is explicitly represented with competition and activity examples.",
        "semantic_assertions": [
          {
            "id": "IC-002:A1",
            "statement": "The activity frame must express high action, effort, energy, tension, or load and must not make short duration a requirement.",
            "polarity": "must_hold",
            "scope": "second sense and its usage note"
          }
        ]
      },
      {
        "id": "IC-003",
        "surface_form": "intense",
        "frame": "an intense person / be intense about <topic>",
        "meaning": "a person with strong feelings, opinions, or attitudes",
        "disposition": "included",
        "rationale": "The intense person frame is covered by the article's person-related sense and its context-dependent evaluation.",
        "semantic_assertions": [
          {
            "id": "IC-003:A1",
            "statement": "The person frame must describe strong feelings, opinions, or attitudes and must not entail either negative evaluation or outward expression in every context.",
            "polarity": "must_hold",
            "scope": "person-related definition, grammar pattern, and usage note"
          }
        ]
      },
      {
        "id": "IC-004",
        "surface_form": "intense",
        "frame": "an intense look/gaze/expression",
        "meaning": "a look or expression conveying strong concentration or feeling",
        "disposition": "included",
        "rationale": "The intense look/gaze/expression frame is covered by the article's gaze and expression pattern and example.",
        "semantic_assertions": [
          {
            "id": "IC-004:A1",
            "statement": "The look or expression frame must describe conveyed concentration, sharpness, or feeling rather than automatically the observer's personality.",
            "polarity": "must_hold",
            "scope": "third sense grammar pattern, look example, and usage note"
          }
        ]
      },
      {
        "id": "IC-005",
        "surface_form": "intense",
        "frame": "an intense relationship",
        "meaning": "a relationship with strong emotional connection or interaction",
        "disposition": "included",
        "rationale": "The intense relationship frame is separately covered as a strong emotional bond and interaction.",
        "semantic_assertions": [
          {
            "id": "IC-005:A1",
            "statement": "The relationship frame must concern emotional connection or interaction strength, not merely duration or frequency.",
            "polarity": "must_hold",
            "scope": "third sense relationship definition, example, and usage note"
          }
        ]
      }
    ],
    "article_findings": [
      {
        "id": "AF-001",
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "意味・用法・関連表現 / 語義1 / 頻度注記",
          "line_start": 35,
          "line_end": 35,
          "exact_quote": "※Oxford 5000ではC1レベルの学習語彙。"
        },
        "severity": "blocking",
        "rationale": "The statement 「※Oxford 5000ではC1レベルの学習語彙。」 misclassifies intense: the Oxford 3000/5000 CEFR list places it at B2, not C1."
      }
    ],
    "recorded_at": "2026-09-05T05:41:21.146514+00:00"
  },
  "blind_seal": {
    "schema_version": "blind_seal_v3",
    "stage": "blind_seal",
    "entry_path": "entries/i/intense.md",
    "body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
    "final_blind_path": "audits/runs/i/intense/20260905T043033Z-31a96a70/final_blind.json",
    "final_blind_sha256": "f8fee16a23c9f8a1ef44f24fb5f7e0349d524bf82834718173b84d3a2dbc640b",
    "blind_output_sha256": "c2db53eb4d6f1b0404c60a6358187da30337779e5bddbcd739c0d43e7ca7a84f",
    "sealed_at": "2026-09-05T14:41:47.733468+09:00"
  },
  "resolutions": {
    "schema_version": "resolutions_v1",
    "stage": "resolutions",
    "run_id": "resolution-intense-20260905T043033Z-31a96a70",
    "context_id": "resolution-intense-context-20260905T043033Z-31a96a70",
    "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
    "prompt_sha256": "04ab1fe768a576a6f376dbb82c98e96d9d3cf1938ad860af031a5ca86538b86d",
    "input_artifacts": [
      "entry_body",
      "all_findings"
    ],
    "recorded_at": "2026-09-05T05:51:51+00:00",
    "reviewer_provenance": {
      "reviewer_role": "independent_finding_resolution_agent",
      "session_mode": "independent_resolution",
      "reviewer": {
        "mode": "independent",
        "declared_model": "gpt-5",
        "agent_id": "codex-independent-finding-resolution-20260905T043033Z-31a96a70"
      },
      "input_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
      "sealed_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241",
      "upstream_reviewers": [
        {
          "stage": "normal_review",
          "pass_id": "translation",
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "codex-translation-handoff-20260905T043033Z-31a96a70"
        },
        {
          "stage": "normal_review",
          "pass_id": "sense-structure",
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "sense-structure-20260905T043033Z-31a96a70"
        },
        {
          "stage": "normal_review",
          "pass_id": "frame-relation",
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "agent-frame-relation-stage1-31a96a70"
        },
        {
          "stage": "normal_review",
          "pass_id": "qualification",
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "codex-qualification-handoff-20260905T043033Z-31a96a70"
        },
        {
          "stage": "normal_review",
          "pass_id": "evidence",
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "codex-evidence-handoff-20260905T043033Z-31a96a70"
        },
        {
          "stage": "cold_review",
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a07002-2009-7a72-8c77-13175b5190b6"
        },
        {
          "stage": "final_blind",
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a0700a-7831-79f1-9f58-d9e7cb4cf08c"
        }
      ]
    },
    "resolutions": [
      {
        "id": "normal-translation-001",
        "finding_id": "normal-translation-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: the competition note adds an unsupported entailment that participants must be made to exert effort or feel tension; retain only the high-intensity competition meaning.",
        "evidence_link_ids": [
          "EVID-002"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-sense-structure-001",
        "finding_id": "normal-sense-structure-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: the activity sense still overlaps the general high-degree sense through energy, determination, concentration, and pressure without an explicit shared-core boundary.",
        "evidence_link_ids": [
          "EVID-001",
          "EVID-002"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-sense-structure-002",
        "finding_id": "normal-sense-structure-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: the core image treats person-related intensity as outwardly manifested while the sense-3 note correctly says outward expression is not required for a person.",
        "evidence_link_ids": [
          "EVID-003"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-frame-relation-001",
        "finding_id": "normal-frame-relation-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: the earnest comparison is not directly supported by the person/expression evidence and its example repeats an intense relationship instead of realizing earnest.",
        "evidence_link_ids": [
          "EVID-003"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-qualification-001",
        "finding_id": "normal-qualification-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: F-021 supports Oxford C1, but the repeated 5/10 field is not a sourced corpus-frequency scale and should be relabeled or separately qualified.",
        "evidence_link_ids": [
          "EVID-008"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-evidence-001",
        "finding_id": "normal-evidence-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: EVID-001 supports intense, not strong's definition, score, example, or contrast.",
        "evidence_link_ids": [
          "EVID-001"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-evidence-002",
        "finding_id": "normal-evidence-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: EVID-001 supports intense, not extreme's definition, score, example, or contrast.",
        "evidence_link_ids": [
          "EVID-001"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-evidence-003",
        "finding_id": "normal-evidence-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: EVID-001 does not directly support powerful's definition, score, example, or force-versus-experienced-intensity contrast.",
        "evidence_link_ids": [
          "EVID-001"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-evidence-004",
        "finding_id": "normal-evidence-004",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: EVID-002 supports intense activity/competition, not fierce's definition, score, example, or aggression contrast.",
        "evidence_link_ids": [
          "EVID-002"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-evidence-005",
        "finding_id": "normal-evidence-005",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: EVID-002 does not directly support vigorous's definition, score, example, or comparison with intense.",
        "evidence_link_ids": [
          "EVID-002"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-evidence-006",
        "finding_id": "normal-evidence-006",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: EVID-002 supports intense activity, not strenuous's definition, score, example, or meaning boundary.",
        "evidence_link_ids": [
          "EVID-002"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-evidence-007",
        "finding_id": "normal-evidence-007",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: EVID-003 supports intense's person/expression use, not serious's definition, score, example, or comparison.",
        "evidence_link_ids": [
          "EVID-003"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-evidence-008",
        "finding_id": "normal-evidence-008",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: EVID-003 does not directly support passionate's definition, score, example, or positive-evaluation contrast.",
        "evidence_link_ids": [
          "EVID-003"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "normal-evidence-009",
        "finding_id": "normal-evidence-009",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: EVID-003 does not directly support earnest's definition, score, example, or comparison.",
        "evidence_link_ids": [
          "EVID-003"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "CR-001",
        "finding_id": "CR-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: clarify the etymological dating and distinguish first attestation from later semantic development.",
        "evidence_link_ids": [
          "EVID-004"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "CR-002",
        "finding_id": "CR-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: describe intensive through concentration, density, and thoroughness, with limited period or scope as a tendency rather than a universal condition.",
        "evidence_link_ids": [
          "EVID-005"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "CR-003",
        "finding_id": "CR-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: make explicit that senses 1 and 2 share the high-intensity core while grouping experienced states separately from activity effort, pace, and load.",
        "evidence_link_ids": [
          "EVID-001",
          "EVID-002"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "CR-004",
        "finding_id": "CR-004",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: include activity volume, pace, and busyness so intense activity is not taught as necessarily physically or effortfully demanding.",
        "evidence_link_ids": [
          "EVID-002"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "CR-005",
        "finding_id": "CR-005",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: explain intense blue through visual vividness, saturation, or prominence without implying darkness or low lightness.",
        "evidence_link_ids": [
          "EVID-001"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "CR-006",
        "finding_id": "CR-006",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: broaden scrutiny from physical surveillance to severe scrutiny, examination, or public/professional attention as context requires.",
        "evidence_link_ids": [
          "EVID-001"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "CR-007",
        "finding_id": "CR-007",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: broaden intense person to context-dependent intensity in feeling, character, seriousness, focus, or interpersonal pressure without requiring outward display.",
        "evidence_link_ids": [
          "EVID-003"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "CR-008",
        "finding_id": "CR-008",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: describe intense relationship as strong emotional involvement or interaction that may be intimate, tense, conflicted, or unstable, not necessarily positively bonded.",
        "evidence_link_ids": [
          "EVID-003"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "CR-009",
        "finding_id": "CR-009",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Adopted for the next cycle: show that extreme and intense overlap with pain, anger, and heat while distinguishing endpoint-of-scale emphasis from experienced or operative intensity.",
        "evidence_link_ids": [
          "EVID-001"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      },
      {
        "id": "AF-001",
        "finding_id": "AF-001",
        "status": "resolved",
        "disposition": "rejected",
        "rationale": "Rejected. The current source inventory's F-021 and U-008 explicitly support the article's Oxford 5000 C1 statement; the final-blind B2 claim is contradicted by that sealed inventory.",
        "evidence_link_ids": [
          "EVID-008"
        ],
        "resolved_body_sha256": "b356fbc16ee2ee211dadf76a50a0cfc0f6293f42676b40e33ec3052b444a8241"
      }
    ]
  }
}
```
