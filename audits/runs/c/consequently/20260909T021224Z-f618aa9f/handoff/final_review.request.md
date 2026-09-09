# Independent review handoff

Stage: `final_review`

The response must be one JSON object matching the supplied review schema. Create it in a separate model session; do not use the generation session.

## Prompt

# final_review_spec_v2

この仕様は、最新版の記事本文、pre/post-blind resolution、影響範囲checkerの再検査・再利用manifest、固定済みblind inventory、具体的未解決事項だけを入力として、第三者最終審査が合否を判断するための意味基準だけを定める。入力分離、順序、hash、seal、記録、件数網羅、status同期は `scripts/run_word.py`、`scripts/workflow_revision.py`、`scripts/generate_audit_manifest.py` が強制する。

final reviewは新たな全面レビューをもう一巡する段階ではない。本文hash、すべてのfindingの完全な裁定、pass再検査・再利用条件、source union、blind chronology、未解決blockerゼロを照合する。hash、件数、集合、時系列、schemaはコードの結果を使い、内容を長大に復唱しない。

## PASSの意味基準

次をすべて満たす場合だけ `PASS` とする。

1. 記事の事実、語法、発音、例文、訳が正しく、見出し語の意味方向・意味役割・適用範囲を誤学習させない。
2. 主要な品詞、語義、派生・転換、専門用法、完全な統語フレームが過不足なく扱われ、語義境界、コアイメージ、定義、語法、コロケーション、語彙関係の間に矛盾がない。
3. 例文と訳で、述語、主語・目的語・補語、行為者・経験者・対象・結果、肯否、比較基準、程度、数量、時制・相・法、条件・因果・目的、修飾範囲、焦点、情報構造、レジスター、話者評価が保存されている。
4. 地域差、専門・制度用法、頻度、語源、語形成、語義境界、文法制約、絶対表現などの高リスク主張が、当該主張へ適用できる根拠に支えられ、反例・矛盾・適用範囲が確認されている。検索見出し、資料名だけ、別義の用例は根拠にしない。
5. checker/cold findingはpre-blind、final-blind findingはpost-blindで重複・欠落なく裁定され、採用修正の影響範囲checkerが再検査済みで、再利用passはspec・正規化入力・source artifact・schema・独立性・request bindingがすべて一致している。
6. blind inventoryの各 `semantic_assertion` を最新版へ適用しても、候補の境界・作用方向・包含/除外関係・一般化範囲に反する記述がない。
7. final blindがcold reviewおよびpre-blind revisionより後で、pre-blind修正後本文hashに束縛されている。final-blind findingの採用修正がある場合は、影響checker再検査後の新本文を新しい独立final blindが確認している。
8. `insufficient_evidence`、未検査範囲、無効pass、判断衝突、未確認の修正影響が残っていない。

## REJECTの意味基準

上記のいずれかを満たさない場合は `REJECT` とする。blockerにできるのは、事実・語法・発音の誤り、例文/訳の誤り、主要語義・構文の欠落または過剰収録、根拠と本文の矛盾、内容仕様の必須項目違反、未判定・未解決項目である。各blockerには対象ID、問題、必要な修正を記録する。条件付き合格は使わない。

本文と矛盾しない分類粒度・棚卸し構成の差、より良い表現の提案、任意の改善余地は、それだけを理由に `REJECT` にせず、非blocking noteとして記録する。`REJECT` は審査失敗ではなく、問題を検出して完了した正常な最終判定である。

## 出力

入力に `inventories` / `response_template` がある場合、それが照合対象IDの正本である。IDを作り直さず、ひな形の未判定欄を独立に判定する。未判定は合格ではない。`target_results` / `relation_results` の `notes` には、対応する対象の `text` / 関係の `description` 全文を引用し、その対象固有の判断理由を記載する。入力欠落を空集合と推測しない。

`final_review_v2` JSONとして、全target/relation/normal candidate/blind candidate/finding/evidence/source-unionの個別結果、再検査・再利用manifestの照合結果、`decision` (`pass | reject`)、`blockers`、非blocking `notes` を返す。`PASS` は全個別結果がpass、未解決・hold・`insufficient_evidence`が0件、blockerが0件の場合に限る。本文は変更しない。新しい内容上のblockerを見つけた場合は正常なREJECTとし、修正、影響範囲再検査、final blind再実行へ戻す。


## Input packet

```json
{
  "stage": "final_review",
  "entry_body": "\n＃発音記号\n\nCambridge: 米 /ˈkɑːn.sə.kwənt.li/｜英 /ˈkɒn.sɪ.kwənt.li/。Oxford: 米 /ˈkɑːn.sɪ.kwent.li/｜英 /ˈkɒn.sɪ.kwənt.li/。いずれも4音節で、第1音節に主強勢がある。第1音節は米語で /ɑː/、英語で /ɒ/ と表記される。米語では、Cambridge は第2音節を /ə/・第3音節を /kwənt/、Oxford は /ɪ/・/kwent/ と表記する。英語の表記は両辞書で同じである。  \n\n＃語源\n\n`consequently` は `consequent` と関連し、`consequent` はラテン語 *consequi*「あとに従う」にさかのぼる。  \n\n＃語形成\n\n・`consequence`：名詞。「結果、影響」。特に複数形 `consequences` は好ましくない結果を指しやすい。  \n・`consequent`：形容詞。ある出来事の結果として続くことを表す。  \n・`consequential`：形容詞。「結果として生じる」、また「重要な結果を伴う、重要な」。`consequently` と違い、因果関係をつなぐ副詞ではなく形容詞である。  \n\n＃意味・用法・関連表現\n\n1. 【副詞・文副詞／接続副詞】その結果、したがって\n\n【日本語訳・定義】前に述べた事実・状況・判断を理由として、後に述べる結果が続くことを示す。単に出来事が後の時点で起こることではなく、前件から後件が結果または論理的帰結として導かれることを表す。  \n\n【頻度】〈6/10〉  \n\n【レジスター/領域】結果や帰結を述べる文章・説明で用いられる。  \n\n【文法パターン】`〈原因となる文〉. Consequently, 〈結果の文〉`＝その結果、…／`〈原因となる文〉; consequently, 〈結果の文〉`＝…、したがって…／`〈主語〉 + consequently + 〈動詞句〉`＝その結果〈主語〉は…する／`〈主語〉 + be + consequently + 〈補語〉`＝〈主語〉はその結果…である／`〈主語〉 + 〈動詞句1〉 and consequently + 〈動詞句2〉`＝〈主語〉は…し、その結果…する。文中では主語の後で主要動詞の前に置く形のほか、`be` の後で補語の前に置く形がある。  \n\n【コロケーション】\n\n・`Consequently, 〈結果の文〉`  \n用途: 直前に述べた原因・根拠を受けて、文全体の結果を明示する。  \n例: The train service was suspended. Consequently, many employees worked from home.  \n訳: 列車の運行が停止された。その結果、多くの従業員が在宅勤務をした。  \n\n・`〈原因となる文〉; consequently, 〈結果の文〉`  \n用途: 原因と結果を一続きの文で示す。  \n例: The evidence was incomplete; consequently, the committee postponed its decision.  \n訳: 証拠が不十分だった。その結果、委員会は決定を延期した。  \n\n・`〈主語〉 + consequently + 〈動詞句〉`  \n用途: 結果を表す副詞として、主語の後、主要動詞の前に置く。  \n例: Demand fell sharply, and the company consequently reduced production.  \n訳: 需要が急減したため、その会社は結果として生産を減らした。  \n\n・`〈主語〉 + be + consequently + 〈過去分詞・形容詞〉`  \n用途: `be` の後で、ある事情の結果としての状態や判断を補語で説明する。  \n例: The deadline was missed, and the application was consequently rejected.  \n訳: 締切に間に合わなかったため、その申請は結果として却下された。  \n\n・`〈主語〉 + 〈動詞句1〉 and consequently + 〈動詞句2〉`  \n用途: 同じ主語の二つの述語を結び、前の内容の結果として後の行為や状態を示す。  \n例: The region receives little rainfall and consequently faces frequent water shortages.  \n訳: その地域は降雨量が少なく、その結果しばしば水不足に直面する。  \n\n【語法・注意】`consequently` は、前に述べた事情・根拠から結果または論理的帰結を示す副詞であり、単なる時間順だけを示す語ではない。文頭だけでなく、接続詞の後や `be` の後で補語の前にも置ける。  \n\n【類義語】\n\n・therefore  \n定義: 前に述べた事実・理由から結果または結論が導かれることを示す。  \n頻度: 〈7/10〉  \n違い: `consequently` と同様に、前の事情を受けた結果を示す。  \n例: The data are incomplete; therefore, no firm conclusion can be drawn.  \n訳: データが不完全なので、確かな結論は導けない。  ",
  "_output_metadata": {
    "schema_version": "final_review_v2",
    "stage": "final_review",
    "run_id": "blind-consequently-20260909T021224Z-f618aa9f",
    "context_id": "blind-consequently-context-20260909T021224Z-f618aa9f",
    "input_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
    "prompt_sha256": "5fa21ad0e8186e05e00c459e6201d7062a5d550a003831b40e182ba27c7a625a",
    "input_artifacts": [
      "entry_body",
      "sealed_final_blind",
      "pre_blind_resolution",
      "post_blind_resolution",
      "checker_recheck_manifest",
      "targeted_adjudications",
      "final_review_spec"
    ],
    "blind_output_sha256": "772b984433379e919865a919d92c83ed0eca97907eabee8c18310d60167a8bdd"
  },
  "pass_findings": {
    "schema_version": "normal_review_v2",
    "stage": "normal_review",
    "run_id": "normal-consequently-20260909T021224Z-f618aa9f",
    "context_id": "normal-consequently-context-20260909T021224Z-f618aa9f",
    "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
    "prompt_sha256": "5178f5a14a9525317811a34e6cd307108436f4babc1299fcd2eb9031f28ba737",
    "input_artifacts": [
      "router_selected_sections",
      "checker_pass_specs"
    ],
    "recorded_at": "2026-09-09T02:26:05.405483+00:00",
    "pass_outputs": [
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "translation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "translation-handoff-20260909-f618aa9f-retry-cc3f"
        },
        "checked": true,
        "findings": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "sense-structure",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5.6-sol",
          "ingested_by": "human",
          "agent_id": "checker-sense-structure-f618aa9f-r2-4c91b7",
          "same_model_as_generation": true
        },
        "checked": true,
        "findings": []
      },
      {
        "pass_id": "frame-relation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "frame-relation-reviewer-2ef298f1-3777-47a1-96b1-b5b69da4a73b"
        },
        "antonym_axis_blind_record": {
          "schema_version": "antonym_axis_blind_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
          "blind_request_sha256": "c0fb952058b6306c95f8c5af7d6f1105c8159da1366167059506fa8a4a7f4f05",
          "recorded_at": "2026-09-09T02:19:41Z",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "frame-relation-reviewer-2ef298f1-3777-47a1-96b1-b5b69da4a73b"
          },
          "axes": []
        },
        "antonym_axis_adjudication_record": {
          "schema_version": "antonym_axis_adjudication_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
          "stage2_request_sha256": "ea16f7ab777ca067caee7cc414c2a1888b4fb43996b3e68d7ec03167f224b993",
          "blind_record_sha256": "3d1527ee6368c14f987dd9a95c5d155553e2b9111a6f4627b2991ff1863ff3f4",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "frame-relation-reviewer-2ef298f1-3777-47a1-96b1-b5b69da4a73b"
          },
          "adjudications": [],
          "frame_findings": [],
          "unrouted_observations": [],
          "aligned_at": "2026-09-09T02:26:38Z"
        },
        "aligned_at": "2026-09-09T02:27:10.239154+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "example-attribution",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "consequently-example-attribution-checker-20260909"
        },
        "blind_attribution_record": {
          "schema_version": "example_attribution_blind_record_v1",
          "pass_id": "example-attribution",
          "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
          "blind_request_sha256": "6e2276b191f0c1fd64fec8a4040003cb34aabb62557a4280b2987df6b4a5b372",
          "recorded_at": "2026-09-09T02:20:05.000Z",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "consequently-example-attribution-checker-20260909"
          },
          "attributions": [
            {
              "example_id": "ex-f767a03494db",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "Demand fell sharply",
                "consequently reduced production"
              ],
              "rationale": "「Demand fell sharply」と「consequently reduced production」が需要急減を前件、減産を帰結として結ぶため sense:001 が一意に自然である。単なる後続時点を示す subsequently/then 的な読みでは、減産が需要急減から導かれるという同じ文内の結果関係を表せない。"
            },
            {
              "example_id": "ex-975eb656016f",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "The deadline was missed",
                "application was consequently rejected"
              ],
              "rationale": "「The deadline was missed」と「application was consequently rejected」が締切不履行を理由、申請却下を帰結として連結するため sense:001 が一意に自然である。単なる時間的な後続を表す読みでは、却下が締切不履行の結果として示されるこの構文関係を説明できない。"
            },
            {
              "example_id": "ex-626810ae87f4",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "receives little rainfall",
                "consequently faces frequent water shortages"
              ],
              "rationale": "「receives little rainfall」と「consequently faces frequent water shortages」が少雨を前件、水不足に直面することを帰結として結ぶため sense:001 が一意に自然である。単に後に水不足が起きるという時間順の読みでは、少雨から水不足へ至る結果関係を担う副詞の働きにならない。"
            },
            {
              "example_id": "ex-df19cd38f4d1",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "The evidence was incomplete",
                "consequently, the committee postponed its decision"
              ],
              "rationale": "「The evidence was incomplete」と「consequently, the committee postponed its decision」が不完全な証拠を理由、決定延期を帰結として接続するので sense:001 が一意に自然である。then のような次の手順・時点を示す読みでは、延期が証拠不十分から導かれる関係を表せない。"
            },
            {
              "example_id": "ex-7f32ad2a3e0d",
              "classification": "unique",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "The train service was suspended",
                "Consequently, many employees worked from home"
              ],
              "rationale": "「The train service was suspended」と「Consequently, many employees worked from home」が列車運休を前件、在宅勤務を帰結として結ぶため sense:001 が一意に自然である。subsequently のように単なる出来事の順序を示す読みでは、在宅勤務が運休を受けた結果であるという同一文脈の意味関係を表せない。"
            }
          ]
        },
        "aligned_at": "2026-09-09T02:26:05.402637+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "qualification",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5.6",
          "ingested_by": "human",
          "agent_id": "qualification-checker-20260909-f618aa9f"
        },
        "findings": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "pronunciation",
        "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "consequently-pronunciation-checker-20260909"
        },
        "findings": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "evidence",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "checker-evidence-f618aa9f-r2-59e221"
        },
        "checked": true,
        "findings": [
          {
            "id": "CHECK-EVID-001",
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "pronunciation",
              "line_start": 15,
              "line_end": 15,
              "exact_quote": "さらに米語では第2音節が /ə/、英語では /ɪ/ となる。"
            },
            "severity": "blocking",
            "rationale": "C002/U002 の根拠は地域別IPAを示すが、F002（Cambridge）は米語第2音節を /ə/ とする一方、F004（Oxford）は米語を /ˈkɑːnsɪkwentli/ と記録する。本文はこの食い違いを示さず、米語第2音節 /ə/ を無条件に断定しているため、提示された根拠集合からこの主張を直接支持できない。",
            "evidence_link_ids": [
              "F002",
              "F004"
            ],
            "suggested_direction": "Cambridgeの表記に帰属させるか、両資料に共通して支持される地域差の記述へ主張を限定する。"
          },
          {
            "id": "CHECK-EVID-002",
            "taxonomy_id": "evidence_claim_mismatch",
            "location": {
              "section": "etymology",
              "line_start": 19,
              "line_end": 19,
              "exact_quote": "形容詞 `consequent` に副詞語尾 `-ly` が付いた語である。`consequent` はラテン語 *consequi*「あとに従う、続いて起こる」にさかのぼり、`con-`「ともに」と *sequi*「従う」に関係する。"
            },
            "severity": "blocking",
            "rationale": "C004/F007 は consequently が consequent に関連し、ラテン語 consequi（follow after）、com-、sequi（follow）へつながることを支持する。しかし提示されたfactは consequent + -ly という語形成、または `con-` が「ともに」を意味することを記録していない。本文はF007が直接支持する範囲を超えている。",
            "evidence_link_ids": [
              "F007"
            ],
            "suggested_direction": "F007が直接記録する consequent と consequi『follow after』の関係に限定するか、形態素と日本語グロスを直接支持する根拠へ差し替える。"
          }
        ]
      }
    ],
    "checker_reviewers": {
      "translation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "translation-handoff-20260909-f618aa9f-retry-cc3f"
      },
      "sense-structure": {
        "mode": "handoff",
        "declared_model": "gpt-5.6-sol",
        "ingested_by": "human",
        "agent_id": "checker-sense-structure-f618aa9f-r2-4c91b7",
        "same_model_as_generation": true
      },
      "frame-relation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "frame-relation-reviewer-2ef298f1-3777-47a1-96b1-b5b69da4a73b"
      },
      "example-attribution": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "consequently-example-attribution-checker-20260909"
      },
      "qualification": {
        "mode": "handoff",
        "declared_model": "gpt-5.6",
        "ingested_by": "human",
        "agent_id": "qualification-checker-20260909-f618aa9f"
      },
      "pronunciation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "consequently-pronunciation-checker-20260909"
      },
      "evidence": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "checker-evidence-f618aa9f-r2-59e221"
      }
    },
    "independent_candidates": [],
    "summary": "Independent checker passes completed by parallel handoff; frame-relation preserved its serial blind/adjudication dependency."
  },
  "cold_review": {
    "summary": "問題候補あり。発音説明が辞書間・話者間にあり得る表記差を断定しており、派生語 consequential の説明も結果に関する語義を落としている。いずれも学習者が不正確な一般化をするおそれがある。",
    "findings": [
      {
        "id": "COLD-001",
        "location": "発音記号",
        "severity": "high",
        "description": "米語第2音節を /ə/、英語第2音節を /ɪ/ と一律に対比し、さらに quent の母音はいずれも /ə/ と断定している。発音辞書には米語を /ɪ/、quent を /e/ と表記するものもあり得るため、この説明だけを唯一の発音規則として学ばせるのは不正確になり得る。",
        "reason": "「米語は第1音節が /ɑː/、英語は /ɒ/ で、さらに米語では第2音節が /ə/、英語では /ɪ/ となる。`quent` の母音はいずれも弱く /ə/ と発音する。」は、本文に示した一組のIPAを地域差一般として断定している。実際の辞書表記には第2音節・quent 部分に揺れがあり得るので、学習者が /ə/ と /ɪ/ の対立を常に守るべき規則だと誤解するおそれがある。",
        "suggested_direction": "採用した辞書・表記体系を明示するか、「辞書により米語の第2音節や quent 部分の表記に揺れがある」と注記して、地域差を単一の絶対規則として説明しない。",
        "scope_anchors": [
          {
            "id": "COLD-001-A1",
            "exact_quote": "米語は第1音節が /ɑː/、英語は /ɒ/ で、さらに米語では第2音節が /ə/、英語では /ɪ/ となる。`quent` の母音はいずれも弱く /ə/ と発音する。",
            "location_hint": "発音記号節の2文目から3文目"
          }
        ]
      },
      {
        "id": "COLD-002",
        "location": "語形成",
        "severity": "medium",
        "description": "consequential を「重要な、重大な」に限定し、consequently と対比して因果関係をつなぐ語ではないと述べると、結果として続くという consequential の別の語義・用法との関係が見えなくなる。",
        "reason": "「・`consequential`：形容詞。「重要な、重大な」。`consequently` と違い、因果関係をつなぐ副詞ではない。」は、品詞の違いを説明する意図は分かるものの、consequential にも「結果として生じる・続く」という語義がある点を落としている。そのため、学習者はこの語が consequence / consequent と共有する結果に関する意味を持たないと一般化しかねない。",
        "suggested_direction": "「重要な、重大な」を主要な現代用法として示すなら、結果として生じる意味もあることを補い、consequently とは『因果をつなぐ副詞ではなく形容詞である』と品詞・機能の差に限定して対比する。",
        "scope_anchors": [
          {
            "id": "COLD-002-A1",
            "exact_quote": "・`consequential`：形容詞。「重要な、重大な」。`consequently` と違い、因果関係をつなぐ副詞ではない。",
            "location_hint": "語形成節の consequential 項目"
          }
        ]
      },
      {
        "id": "COLD-003",
        "location": "意味・用法・関連表現／文法パターン",
        "severity": "low",
        "description": "主語の直後・主要動詞の前という語順を基本形として示すだけでは、助動詞・完了形・受動態のある文で consequently を置く位置を狭く覚えさせやすい。後段に be の例はあるが、パターン説明自体が包括的ではない。",
        "reason": "「`〈主語〉 + consequently + 〈動詞句〉`＝その結果〈主語〉は…する。文頭で使うときは通常後ろにコンマを置き、二つの独立した節をコンマだけでつなぐ `…, consequently, …` は避ける。」は、consequently の文中位置を主語直後・主要動詞前に固定的に読める形で提示している。実際には助動詞・be・完了形などに応じた位置もあるため、このパターンだけを一般規則とすると誤用につながり得る。",
        "suggested_direction": "「主語の後、主要動詞の前」は一例・よくある位置として示し、助動詞や be の後にも置けることを短く補足するか、文中配置のパターンを複数提示する。",
        "scope_anchors": [
          {
            "id": "COLD-003-A1",
            "exact_quote": "`〈主語〉 + consequently + 〈動詞句〉`＝その結果〈主語〉は…する。文頭で使うときは通常後ろにコンマを置き、二つの独立した節をコンマだけでつなぐ `…, consequently, …` は避ける。",
            "location_hint": "意味・用法・関連表現節の文法パターン"
          },
          {
            "id": "COLD-003-A2",
            "exact_quote": "用途: 結果を表す副詞として、主語の後、主要動詞の前に置く。",
            "location_hint": "コロケーションの〈主語〉 + consequently + 〈動詞句〉項目"
          }
        ]
      }
    ],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "cold-reviewer-f618aa9f"
    },
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-consequently-20260909T021224Z-f618aa9f",
    "context_id": "cold-consequently-context-20260909T021224Z-f618aa9f",
    "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
    "prompt_sha256": "25c298d1a4305746147791bd442cd725a92737c8f0802b992ea88e5c6ff76a5d",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-09T02:30:46.800135+00:00"
  },
  "final_blind": {
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "provisional_decision": "pass",
    "independent_candidates": [
      {
        "id": "independent-candidate-1",
        "surface_form": "consequently",
        "frame": "Consequently, clause; clause; consequently, clause",
        "meaning": "前件として述べられた事実・状況・判断から、後件が結果または論理的帰結として導かれることを示す文副詞・接続副詞",
        "disposition": "included",
        "rationale": "Consequently, clause; clause; consequently, clause は、先行する命題を根拠・原因として後続の命題を結果又は帰結として提示する同一の文接続的用法である。",
        "semantic_assertions": [
          {
            "id": "assertion-1",
            "statement": "後件は前件との単なる時間的な前後関係ではなく、前件から生じる結果又は論理的帰結として解釈されなければならない。",
            "polarity": "must_hold",
            "scope": "前置された consequently とセミコロン後の consequently が結ぶ二つの命題"
          },
          {
            "id": "assertion-2",
            "statement": "consequently は後件の内容全体を、先行命題に照らした結果・帰結として位置づけなければならない。",
            "polarity": "must_hold",
            "scope": "文頭又はセミコロン後に置かれる consequently"
          }
        ]
      },
      {
        "id": "independent-candidate-2",
        "surface_form": "consequently",
        "frame": "subject + consequently + verb phrase; subject + be + consequently + complement; verb phrase 1 and consequently + verb phrase 2",
        "meaning": "前に示された事情・出来事を原因又は根拠として、その節内の行為・状態・判断を結果又は帰結として示す副詞",
        "disposition": "included",
        "rationale": "subject + consequently + verb phrase; subject + be + consequently + complement; verb phrase 1 and consequently + verb phrase 2 は、いずれも先行する事情に対する結果として節内の述語又は補語を修飾する同一の因果的副詞用法である。",
        "semantic_assertions": [
          {
            "id": "assertion-3",
            "statement": "修飾される行為・状態・判断は、文脈又は同じ文の先行内容に示される事情の結果として理解されなければならない。",
            "polarity": "must_hold",
            "scope": "動詞前、be の後、又は and の後に置かれる consequently"
          },
          {
            "id": "assertion-4",
            "statement": "この用法は出来事の単なる後続時点だけを表してはならない。",
            "polarity": "must_not_hold",
            "scope": "節内の consequently"
          }
        ]
      },
      {
        "id": "independent-candidate-3",
        "surface_form": "consequently",
        "frame": "temporal-adverb use meaning 'afterwards' or 'later'",
        "meaning": "単に時間的に後で起きることを示す副詞",
        "disposition": "excluded",
        "rationale": "temporal-adverb use meaning 'afterwards' or 'later' は consequent の因果・帰結関係を要求せず、consequently の主要な意味範囲には含めない。",
        "semantic_assertions": [
          {
            "id": "assertion-5",
            "statement": "先行事実と後続事実の時間順序だけで用法が成立してはならず、結果又は論理的帰結の関係が必要である。",
            "polarity": "must_not_hold",
            "scope": "consequently の意味範囲"
          }
        ]
      }
    ],
    "article_findings": [],
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5.6-sol",
      "ingested_by": "human",
      "agent_id": "final-blind-consequently-f618aa9f",
      "same_model_as_generation": true
    },
    "run_id": "blind-consequently-20260909T021224Z-f618aa9f",
    "context_id": "blind-consequently-context-20260909T021224Z-f618aa9f",
    "input_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
    "prompt_sha256": "3a481b4b5b1236ff386e148bcacc574570b305e79f5e155e9afcd34091f7785c",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-09T04:03:30.949140+00:00"
  },
  "blind_seal": {
    "schema_version": "blind_seal_v3",
    "stage": "blind_seal",
    "entry_path": "entries/c/consequently.md",
    "body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
    "final_blind_path": "audits/runs/c/consequently/20260909T021224Z-f618aa9f/final_blind.json",
    "final_blind_sha256": "c0a3eb07fa10a8615eda514de66ee135a31363a89a240dfe694a989038f62416",
    "blind_output_sha256": "772b984433379e919865a919d92c83ed0eca97907eabee8c18310d60167a8bdd",
    "sealed_at": "2026-09-08T21:03:44.596438-07:00"
  },
  "pre_blind_resolution": {
    "schema_version": "pre_blind_resolution_v1",
    "resolutions": [
      {
        "id": "CHECK-EVID-001",
        "finding_id": "CHECK-EVID-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Cambridge と Oxford の米語IPA表記の差を併記し、単一の地域規則としての断定を削除した。",
        "resolved_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae"
      },
      {
        "id": "CHECK-EVID-002",
        "finding_id": "CHECK-EVID-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "語源説明を consequent と Latin consequi の直接に支持された関係に限定した。",
        "resolved_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae"
      },
      {
        "id": "COLD-001",
        "finding_id": "COLD-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用辞書ごとのIPAを明示し、後半母音を一律に教える説明を削除した。",
        "resolved_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae"
      },
      {
        "id": "COLD-002",
        "finding_id": "COLD-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "consequential の結果として生じる語義と重要な結果を伴う語義を、既存の根拠に沿って追記した。",
        "resolved_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae"
      },
      {
        "id": "COLD-003",
        "finding_id": "COLD-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "文中配置を主語後だけに固定せず、be の後で補語の前に置く形も示した。",
        "resolved_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae"
      }
    ]
  },
  "pre_blind_revision": {
    "schema_version": "pre_blind_revision_v1",
    "input_body_sha256": "bfd615520d08ca8ffe1289c11b66e47dd876aabff126d7400418a6fd69ada0fd",
    "output_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
    "recorded_at": "2026-09-09T02:32:16Z",
    "changed_units": [
      "collocations_examples",
      "etymology",
      "frames",
      "pronunciation",
      "word_formation"
    ],
    "invalidated_passes": [
      "evidence",
      "example-attribution",
      "frame-relation",
      "pronunciation",
      "qualification",
      "sense-structure",
      "translation"
    ],
    "full_recheck": false
  },
  "checker_recheck_manifest": {
    "schema_version": "checker_recheck_manifest_v1",
    "current_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
    "revision_plan_sha256": "9d6d2a216fff4966a4c20fde0c6226008a9100a8e7992373eb640382aded6fb5",
    "full_recheck": false,
    "invalidated_passes": [
      "evidence",
      "example-attribution",
      "frame-relation",
      "pronunciation",
      "qualification",
      "sense-structure",
      "translation"
    ],
    "pass_results": [
      {
        "pass_id": "evidence",
        "mode": "rechecked",
        "validated_on_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "spec_sha256": "eb1176fc4fc1868fa5e3a7184cee757798c8d07d9b26c45d0b3f261a4703e497",
        "normalized_input_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "source_artifact_sha256": "3cd55b2a4ad2f05074a8294eb22de0b80cb76f9e5632b089c401cf878ca0af1c",
        "output_sha256": "eb1176fc4fc1868fa5e3a7184cee757798c8d07d9b26c45d0b3f261a4703e497",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "notes": "Independent recheck output retained; subsequent resolution required for recorded findings."
      },
      {
        "pass_id": "example-attribution",
        "mode": "rechecked",
        "validated_on_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "spec_sha256": "91edd659a6d9023731007b172b184f9d4cd8de3ffb296126de83cc427dbed2d0",
        "normalized_input_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "source_artifact_sha256": "3cd55b2a4ad2f05074a8294eb22de0b80cb76f9e5632b089c401cf878ca0af1c",
        "output_sha256": "91edd659a6d9023731007b172b184f9d4cd8de3ffb296126de83cc427dbed2d0",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "notes": "Independent recheck output retained; subsequent resolution required for recorded findings."
      },
      {
        "pass_id": "frame-relation",
        "mode": "rechecked",
        "validated_on_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "spec_sha256": "1e4cbdd845c3c4410c8adb761842a4e1441579296a101d72bcbfbe67606e233a",
        "normalized_input_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "source_artifact_sha256": "3cd55b2a4ad2f05074a8294eb22de0b80cb76f9e5632b089c401cf878ca0af1c",
        "output_sha256": "1e4cbdd845c3c4410c8adb761842a4e1441579296a101d72bcbfbe67606e233a",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "notes": "Independent recheck output retained; subsequent resolution required for recorded findings."
      },
      {
        "pass_id": "pronunciation",
        "mode": "rechecked",
        "validated_on_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "spec_sha256": "442dfc62fa60398bcf5f43670cdc65360abb8d3daa26b8fda6e97906c58be3b2",
        "normalized_input_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "source_artifact_sha256": "3cd55b2a4ad2f05074a8294eb22de0b80cb76f9e5632b089c401cf878ca0af1c",
        "output_sha256": "442dfc62fa60398bcf5f43670cdc65360abb8d3daa26b8fda6e97906c58be3b2",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "notes": "Independent recheck output retained; subsequent resolution required for recorded findings."
      },
      {
        "pass_id": "qualification",
        "mode": "rechecked",
        "validated_on_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "spec_sha256": "2e2380b986a190a128d38062c029f237952af8da23d1634e90920f9016a4b5fb",
        "normalized_input_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "source_artifact_sha256": "3cd55b2a4ad2f05074a8294eb22de0b80cb76f9e5632b089c401cf878ca0af1c",
        "output_sha256": "2e2380b986a190a128d38062c029f237952af8da23d1634e90920f9016a4b5fb",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "notes": "Independent recheck output retained; subsequent resolution required for recorded findings."
      },
      {
        "pass_id": "sense-structure",
        "mode": "rechecked",
        "validated_on_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "spec_sha256": "1803064f0bf293c6f14877411bd754690125c834c5a0cdfe8b3ecb9cbcd2300f",
        "normalized_input_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "source_artifact_sha256": "3cd55b2a4ad2f05074a8294eb22de0b80cb76f9e5632b089c401cf878ca0af1c",
        "output_sha256": "1803064f0bf293c6f14877411bd754690125c834c5a0cdfe8b3ecb9cbcd2300f",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "notes": "Independent recheck output retained; subsequent resolution required for recorded findings."
      },
      {
        "pass_id": "translation",
        "mode": "rechecked",
        "validated_on_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "spec_sha256": "dc76f7764ddddd610554b8267defbeaeff944c4b812179804ce83b54154ea827",
        "normalized_input_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "source_artifact_sha256": "3cd55b2a4ad2f05074a8294eb22de0b80cb76f9e5632b089c401cf878ca0af1c",
        "output_sha256": "dc76f7764ddddd610554b8267defbeaeff944c4b812179804ce83b54154ea827",
        "schema_valid": true,
        "reviewer_independent": true,
        "request_binding_valid": true,
        "notes": "Independent recheck output retained; subsequent resolution required for recorded findings."
      }
    ]
  },
  "post_blind_resolution": {
    "schema_version": "post_blind_resolution_v1",
    "resolutions": []
  },
  "post_blind_verification": {
    "schema_version": "post_blind_verification_v1",
    "verified_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
    "checker_recheck_manifest_sha256": "557e41b066c7233443a4af7dd3ea98988305e2f72447d31fb6781a14516ab61d",
    "final_blind_sha256": "c0a3eb07fa10a8615eda514de66ee135a31363a89a240dfe694a989038f62416",
    "verified_at": "2026-09-09T04:05:00Z",
    "final_attempt": 1
  },
  "targeted_adjudications": {
    "schema_version": "targeted_adjudications_v1",
    "requests": [],
    "adjudications": []
  },
  "source_inventory": {
    "schema_version": "source_inventory_v2",
    "stage": "source_inventory",
    "headword": "consequently",
    "run_id": "source-consequently-20260909T021224Z-f618aa9f",
    "context_id": "source-consequently-context-20260909T021224Z-f618aa9f",
    "input_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
    "prompt_sha256": "a5172ff43a877d1434d7396c9e545bd40fb15b4af21b0dc74624088e6bca0b45",
    "input_artifacts": [
      "headword",
      "source_first_spec"
    ],
    "recorded_at": "2026-09-09T02:20:00Z",
    "source_first_audit": {
      "version": "source_first_audit_v2",
      "profile": "standard",
      "profile_reason": "bounded default profile",
      "limits": {
        "max_sources": 6,
        "max_facts": 48,
        "max_research_rounds": 2,
        "max_post_cold_rechecks": null,
        "max_final_attempts": 2
      },
      "usage": {
        "sources_used": 5,
        "facts_used": 10,
        "research_rounds_used": 1,
        "post_cold_rechecks_used": 0,
        "final_attempts_used": 1
      },
      "research_status": "complete",
      "stop_reason": "coverage_axes_closed",
      "open_questions": [],
      "inventory_completed_before_article_comparison": true,
      "inventory_completed_at": "2026-09-08T18:06:13.884074-07:00",
      "article_comparison_started_at": "2026-09-08T18:06:13.925826-07:00",
      "coverage_axes": [
        {
          "axis": "lexical_senses",
          "status": "covered",
          "source_fact_ids": [
            "F001",
            "F003",
            "F005"
          ],
          "notes": "Three independent learner/general dictionaries give the causal-result sense."
        },
        {
          "axis": "part_of_speech_and_frames",
          "status": "covered",
          "source_fact_ids": [
            "F001",
            "F003",
            "F006"
          ],
          "notes": "The sources identify an adverb and illustrate sentence-initial and clause-internal placement."
        },
        {
          "axis": "derived_and_related_forms",
          "status": "covered",
          "source_fact_ids": [
            "F007",
            "F008",
            "F009",
            "F010"
          ],
          "notes": "Directly attested related forms cover the article's word-formation note."
        },
        {
          "axis": "specialist_and_legal_uses",
          "status": "not_applicable",
          "source_fact_ids": [],
          "notes": "The consulted dictionaries record no separate specialist or legal sense for the headword."
        },
        {
          "axis": "register_region_and_frequency",
          "status": "covered",
          "source_fact_ids": [
            "F003",
            "F005"
          ],
          "notes": "Oxford places the word in its effect/cause language-bank material; Merriam-Webster lists it with causal-result synonyms."
        },
        {
          "axis": "pronunciation_and_etymology",
          "status": "covered",
          "source_fact_ids": [
            "F002",
            "F004",
            "F007"
          ],
          "notes": "Oxford and Cambridge provide regional IPA, and Etymonline supplies the consequent/consequi lineage."
        }
      ],
      "sources": [
        {
          "id": "S001",
          "title": "Cambridge Dictionary — consequently",
          "locator": "https://dictionary.cambridge.org/dictionary/english/consequently",
          "source_type": "learner_dictionary",
          "source_role": "general_lexicon",
          "independence_group": "cambridge_university_press",
          "facts": [
            {
              "id": "F001",
              "form": "consequently",
              "kind": "lexical_sense",
              "statement": "Consequently is an adverb meaning as a result or therefore.",
              "source_detail": "The headword definition gives ‘as a result’ and ‘as a result; therefore’."
            },
            {
              "id": "F002",
              "form": "consequently",
              "kind": "pronunciation",
              "statement": "Cambridge gives UK /ˈkɒn.sɪ.kwənt.li/ and US /ˈkɑːn.sə.kwənt.li/.",
              "source_detail": "The pronunciation entry displays the two regional IPA forms."
            }
          ]
        },
        {
          "id": "S002",
          "title": "Oxford Advanced Learner's Dictionary — consequently",
          "locator": "https://www.oxfordlearnersdictionaries.com/definition/english/consequently",
          "source_type": "learner_dictionary",
          "source_role": "general_lexicon",
          "independence_group": "oxford_university_press",
          "facts": [
            {
              "id": "F003",
              "form": "consequently",
              "kind": "lexical_sense",
              "statement": "Consequently means as a result or therefore and is used to describe an effect.",
              "source_detail": "The sole adverb sense gives ‘as a result; therefore’ and its language-bank section is headed ‘Describing the effect of something’."
            },
            {
              "id": "F004",
              "form": "consequently",
              "kind": "pronunciation",
              "statement": "Oxford gives British /ˈkɒnsɪkwəntli/ and American /ˈkɑːnsɪkwentli/.",
              "source_detail": "The entry prints separate British and North American IPA forms."
            },
            {
              "id": "F006",
              "form": "consequently",
              "kind": "grammar_frame",
              "statement": "Consequently can occur after a coordinator or in a copular clause before a complement.",
              "source_detail": "Oxford illustrates ‘and consequently to human health’ and ‘was consequently unable to start’."
            }
          ]
        },
        {
          "id": "S003",
          "title": "Merriam-Webster — consequently",
          "locator": "https://www.merriam-webster.com/dictionary/consequently",
          "source_type": "general_dictionary",
          "source_role": "general_lexicon",
          "independence_group": "merriam_webster",
          "facts": [
            {
              "id": "F005",
              "form": "consequently",
              "kind": "lexical_sense",
              "statement": "Consequently means as a result, in view of what has been stated, or accordingly.",
              "source_detail": "The definition explicitly gives these three formulations."
            }
          ]
        },
        {
          "id": "S004",
          "title": "Etymonline — consequent",
          "locator": "https://www.etymonline.com/word/consequent",
          "source_type": "etymology_dictionary",
          "source_role": "etymology_reference",
          "independence_group": "etymonline",
          "facts": [
            {
              "id": "F007",
              "form": "consequently",
              "kind": "etymology",
              "statement": "Consequently is related to consequent, from Latin consequi ‘to follow after’, formed from com- and sequi ‘to follow’.",
              "source_detail": "The consequent entry gives the Latin formation and explicitly lists Consequently as related."
            },
            {
              "id": "F010",
              "form": "consequent",
              "kind": "derived_form",
              "statement": "Consequent is an adjective for something following as an effect or result.",
              "source_detail": "The source defines consequent as following or resulting and identifies it as related to consequently."
            }
          ]
        },
        {
          "id": "S005",
          "title": "Oxford Advanced Learner's Dictionary — consequential and consequence",
          "locator": "https://www.oxfordlearnersdictionaries.com/definition/english/consequential",
          "source_type": "learner_dictionary",
          "source_role": "supporting_lexicon",
          "independence_group": "oxford_university_press",
          "facts": [
            {
              "id": "F008",
              "form": "consequential",
              "kind": "derived_form",
              "statement": "Consequential is a formal adjective that can mean resulting or important with important results.",
              "source_detail": "Oxford records both the resultant sense and the ‘important’ sense."
            },
            {
              "id": "F009",
              "form": "consequence",
              "kind": "derived_form",
              "statement": "Consequence is a noun for a result; plural consequences often suggests adverse results.",
              "source_detail": "Oxford's consequence entry states the result sense and its tendency toward negative results."
            }
          ]
        }
      ],
      "source_union": [
        {
          "id": "U001",
          "source_fact_ids": [
            "F001",
            "F003",
            "F005"
          ],
          "canonical_statement": "Consequently is an adverb that marks a result or conclusion following from stated circumstances.",
          "disposition": "included",
          "rationale": "This is the article's sole lexical sense."
        },
        {
          "id": "U002",
          "source_fact_ids": [
            "F002",
            "F004"
          ],
          "canonical_statement": "The word has distinct British and American vowel realizations in the first two syllables.",
          "disposition": "included",
          "rationale": "The regional IPA is stated in the pronunciation section."
        },
        {
          "id": "U003",
          "source_fact_ids": [
            "F006"
          ],
          "canonical_statement": "Consequently can occur inside a clause as well as in result-linking sentence position.",
          "disposition": "included",
          "rationale": "The article teaches clause-internal placement with attested patterns."
        },
        {
          "id": "U004",
          "source_fact_ids": [
            "F007"
          ],
          "canonical_statement": "The word derives through consequent from the Latin follow-after verb consequi.",
          "disposition": "included",
          "rationale": "This supports the compact etymology."
        },
        {
          "id": "U005",
          "source_fact_ids": [
            "F008"
          ],
          "canonical_statement": "Consequential is a related adjective and is not the causal connective adverb consequently.",
          "disposition": "included",
          "rationale": "This contrast prevents a common form-based confusion."
        },
        {
          "id": "U006",
          "source_fact_ids": [
            "F009"
          ],
          "canonical_statement": "Consequence is a related result noun whose plural often has negative-result associations.",
          "disposition": "included",
          "rationale": "This is a directly supported word-formation note."
        },
        {
          "id": "U007",
          "source_fact_ids": [
            "F010"
          ],
          "canonical_statement": "Consequent is a related adjective for something that follows as an effect or result.",
          "disposition": "included",
          "rationale": "This supports the related-form entry."
        }
      ],
      "claim_units": [
        {
          "id": "C001",
          "union_ids": [
            "U001"
          ],
          "subject_form": "consequently",
          "claim_type": "definition",
          "statement": "It introduces a result rather than a merely later event.",
          "article_target_ids": [
            "sense-1-definition",
            "sense-1-usage"
          ],
          "source_supports": [
            {
              "source_fact_id": "F001",
              "support_summary": "Cambridge defines the adverb as ‘as a result’."
            },
            {
              "source_fact_id": "F003",
              "support_summary": "Oxford defines it as ‘as a result; therefore’."
            },
            {
              "source_fact_id": "F005",
              "support_summary": "Merriam-Webster includes ‘in view of the foregoing’."
            }
          ]
        },
        {
          "id": "C002",
          "union_ids": [
            "U002"
          ],
          "subject_form": "consequently",
          "claim_type": "pronunciation",
          "statement": "British and American pronunciation differ in the first and second syllable vowels.",
          "article_target_ids": [
            "pronunciation"
          ],
          "source_supports": [
            {
              "source_fact_id": "F002",
              "support_summary": "Cambridge supplies separate UK and US IPA forms."
            },
            {
              "source_fact_id": "F004",
              "support_summary": "Oxford independently supplies British and American IPA."
            }
          ]
        },
        {
          "id": "C003",
          "union_ids": [
            "U003"
          ],
          "subject_form": "consequently",
          "claim_type": "grammar_frame",
          "statement": "It can modify a clause internally, including after a coordinator and before a complement.",
          "article_target_ids": [
            "sense-1-patterns",
            "sense-1-collocations"
          ],
          "source_supports": [
            {
              "source_fact_id": "F006",
              "support_summary": "Oxford examples attest both clause-internal placements."
            }
          ]
        },
        {
          "id": "C004",
          "union_ids": [
            "U004"
          ],
          "subject_form": "consequently",
          "claim_type": "etymology",
          "statement": "Its history is tied to the idea of following after.",
          "article_target_ids": [
            "etymology"
          ],
          "source_supports": [
            {
              "source_fact_id": "F007",
              "support_summary": "Etymonline traces consequent to Latin consequi ‘follow after’."
            }
          ]
        },
        {
          "id": "C005",
          "union_ids": [
            "U005"
          ],
          "subject_form": "consequential",
          "claim_type": "derived_form",
          "statement": "Consequential is an adjective with resultant and important senses.",
          "article_target_ids": [
            "word-formation"
          ],
          "source_supports": [
            {
              "source_fact_id": "F008",
              "support_summary": "Oxford records both adjectival senses."
            }
          ]
        },
        {
          "id": "C006",
          "union_ids": [
            "U006"
          ],
          "subject_form": "consequence",
          "claim_type": "derived_form",
          "statement": "Consequence is a related result noun and its plural often suggests negative results.",
          "article_target_ids": [
            "word-formation"
          ],
          "source_supports": [
            {
              "source_fact_id": "F009",
              "support_summary": "Oxford gives the noun sense and the plural association."
            }
          ]
        },
        {
          "id": "C007",
          "union_ids": [
            "U007"
          ],
          "subject_form": "consequent",
          "claim_type": "derived_form",
          "statement": "Consequent is a related adjective for an effect or result that follows.",
          "article_target_ids": [
            "word-formation"
          ],
          "source_supports": [
            {
              "source_fact_id": "F010",
              "support_summary": "The source describes consequent as following as an effect or result."
            }
          ]
        }
      ]
    }
  },
  "resolutions": {
    "schema_version": "resolutions_v2",
    "stage": "resolutions",
    "run_id": "resolution-consequently-20260909T021224Z-f618aa9f",
    "context_id": "resolution-consequently-context-20260909T021224Z-f618aa9f",
    "input_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
    "prompt_sha256": "7dfcaa0a828a334dbb84d1d31ed97312d0a9661a7aca70a7815a9f88b31ea2f1",
    "input_artifacts": [
      "entry_body",
      "all_findings"
    ],
    "recorded_at": "2026-09-09T04:04:00Z",
    "resolutions": [
      {
        "id": "CHECK-EVID-001",
        "finding_id": "CHECK-EVID-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "Cambridge と Oxford の米語IPA表記の差を併記し、単一の地域規則としての断定を削除した。",
        "resolved_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae"
      },
      {
        "id": "CHECK-EVID-002",
        "finding_id": "CHECK-EVID-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "語源説明を consequent と Latin consequi の直接に支持された関係に限定した。",
        "resolved_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae"
      },
      {
        "id": "COLD-001",
        "finding_id": "COLD-001",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用辞書ごとのIPAを明示し、後半母音を一律に教える説明を削除した。",
        "resolved_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae"
      },
      {
        "id": "COLD-002",
        "finding_id": "COLD-002",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "consequential の結果として生じる語義と重要な結果を伴う語義を、既存の根拠に沿って追記した。",
        "resolved_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae"
      },
      {
        "id": "COLD-003",
        "finding_id": "COLD-003",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "文中配置を主語後だけに固定せず、be の後で補語の前に置く形も示した。",
        "resolved_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae"
      }
    ]
  },
  "inventories": {
    "target_results": [
      {
        "id": "pronunciation:001",
        "kind": "pronunciation",
        "location": "line:4",
        "section": "＃発音記号",
        "sense": "",
        "text_sha256": "dfdbcd0a7870a814e24d7112b5ee13525cc77e4a2d0f894e6eedf9c78fca17ba",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "Cambridge: 米 /ˈkɑːn.sə.kwənt.li/｜英 /ˈkɒn.sɪ.kwənt.li/。Oxford: 米 /ˈkɑːn.sɪ.kwent.li/｜英 /ˈkɒn.sɪ.kwənt.li/。いずれも4音節で、第1音節に主強勢がある。第1音節は米語で /ɑː/、英語で /ɒ/ と表記される。米語では、Cambridge は第2音節を /ə/・第3音節を /kwənt/、Oxford は /ɪ/・/kwent/ と表記する。英語の表記は両辞書で同じである。"
      },
      {
        "id": "etymology:001",
        "kind": "etymology",
        "location": "line:8",
        "section": "＃語源",
        "sense": "",
        "text_sha256": "498a140adca720de1341c8318ddf1546f5d081e17dd932bed2eec563845fa605",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "`consequently` は `consequent` と関連し、`consequent` はラテン語 *consequi*「あとに従う」にさかのぼる。"
      },
      {
        "id": "word_formation:001",
        "kind": "word_formation",
        "location": "line:12",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "23beb9c950bed7b57ff6f6d1f757ba2846084df1aebf47f9744d633a86fb58c3",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`consequence`：名詞。「結果、影響」。特に複数形 `consequences` は好ましくない結果を指しやすい。"
      },
      {
        "id": "word_formation:002",
        "kind": "word_formation",
        "location": "line:13",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "1ce27adc0e541ee13edf6c658805f2fc87eb22b980dd4b44a1676aa1b6268474",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`consequent`：形容詞。ある出来事の結果として続くことを表す。"
      },
      {
        "id": "word_formation:003",
        "kind": "word_formation",
        "location": "line:14",
        "section": "＃語形成",
        "sense": "",
        "text_sha256": "424c3777f6de6d3e53b3a5d56d9aeaf68977c91983f8db9b1c004acb6ed1b979",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`consequential`：形容詞。「結果として生じる」、また「重要な結果を伴う、重要な」。`consequently` と違い、因果関係をつなぐ副詞ではなく形容詞である。"
      },
      {
        "id": "sense_boundary:001",
        "kind": "sense_boundary",
        "location": "line:18",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "e1761f51b09d261eeff7e94e278748308d00602d0dbb8c406e151ec77afd7ab5",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "1. 【副詞・文副詞／接続副詞】その結果、したがって"
      },
      {
        "id": "definition:001",
        "kind": "definition",
        "location": "line:20",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "4af6d8af98f5af9c7b6fa441d5a6a8c6863856011c2b784de0a58345b18036b7",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "前に述べた事実・状況・判断を理由として、後に述べる結果が続くことを示す。単に出来事が後の時点で起こることではなく、前件から後件が結果または論理的帰結として導かれることを表す。"
      },
      {
        "id": "frequency:001",
        "kind": "frequency",
        "location": "line:22",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "a23a06d2905d81231d50626f046f9464d12c1d151c753524c4d99e404a59a4ef",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "〈6/10〉"
      },
      {
        "id": "register:001",
        "kind": "register",
        "location": "line:24",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "c2397193b29599f8c8277d39d323acb2d60aa1e089c9d3ad71d5e0610dcfd5bf",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "結果や帰結を述べる文章・説明で用いられる。"
      },
      {
        "id": "grammar_pattern:001",
        "kind": "grammar_pattern",
        "location": "line:26",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "c56d9bdc6f97d6a0d00aac9b8d78b0d97a48fb0768c5297331ec1b6c6eb6f508",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`〈原因となる文〉. Consequently, 〈結果の文〉`＝その結果、…"
      },
      {
        "id": "grammar_pattern:002",
        "kind": "grammar_pattern",
        "location": "line:26",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "a78ff99aae0a3bf8555611c369c06b0531726e336de4ad78f566a54198b5f3cc",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`〈原因となる文〉; consequently, 〈結果の文〉`＝…、したがって…"
      },
      {
        "id": "grammar_pattern:003",
        "kind": "grammar_pattern",
        "location": "line:26",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "ce8babef46b2fef2866b5dbd79984df10ccfc99ac673884f2ac12440341da2ea",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`〈主語〉 + consequently + 〈動詞句〉`＝その結果〈主語〉は…する"
      },
      {
        "id": "grammar_pattern:004",
        "kind": "grammar_pattern",
        "location": "line:26",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "e04d77878a96bfec3d80ca65e0624f5b6773889d44713ac6b019eaab21d238b8",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`〈主語〉 + be + consequently + 〈補語〉`＝〈主語〉はその結果…である"
      },
      {
        "id": "grammar_pattern:005",
        "kind": "grammar_pattern",
        "location": "line:26",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "be3675bb21705f0006a2a9d368790a2c48090d3d4a35f8020fc8b599da8998f3",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "`〈主語〉 + 〈動詞句1〉 and consequently + 〈動詞句2〉`＝〈主語〉は…し、その結果…する。文中では主語の後で主要動詞の前に置く形のほか、`be` の後で補語の前に置く形がある。"
      },
      {
        "id": "collocation:001",
        "kind": "collocation",
        "location": "lines:30-33",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "18b95a73a0ef4931955dfe81380389263029f9121238b928522186eab59eebf8",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`Consequently, 〈結果の文〉`\n用途: 直前に述べた原因・根拠を受けて、文全体の結果を明示する。\n例: The train service was suspended. Consequently, many employees worked from home.\n訳: 列車の運行が停止された。その結果、多くの従業員が在宅勤務をした。"
      },
      {
        "id": "collocation:002",
        "kind": "collocation",
        "location": "lines:35-38",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "7ad71bb79bec3638d3311139412a75fc0d2a09f7433334dc2f19548732a54a26",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`〈原因となる文〉; consequently, 〈結果の文〉`\n用途: 原因と結果を一続きの文で示す。\n例: The evidence was incomplete; consequently, the committee postponed its decision.\n訳: 証拠が不十分だった。その結果、委員会は決定を延期した。"
      },
      {
        "id": "collocation:003",
        "kind": "collocation",
        "location": "lines:40-43",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "e3311316e5c3f3edb60eafecc19c98191617533aa248c6fb0d9eb0689dadd2a6",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`〈主語〉 + consequently + 〈動詞句〉`\n用途: 結果を表す副詞として、主語の後、主要動詞の前に置く。\n例: Demand fell sharply, and the company consequently reduced production.\n訳: 需要が急減したため、その会社は結果として生産を減らした。"
      },
      {
        "id": "collocation:004",
        "kind": "collocation",
        "location": "lines:45-48",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "0682401babbee4f32e1e96c37e6f142321fd6e67a6fdd19e24d6995da3ccf192",
        "requires_evidence": true,
        "evidence_policy": "one_source",
        "text": "・`〈主語〉 + be + consequently + 〈過去分詞・形容詞〉`\n用途: `be` の後で、ある事情の結果としての状態や判断を補語で説明する。\n例: The deadline was missed, and the application was consequently rejected.\n訳: 締切に間に合わなかったため、その申請は結果として却下された。"
      },
      {
        "id": "collocation:005",
        "kind": "collocation",
        "location": "lines:50-53",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "6ebe87dab5948223a1f8284550fd4c56006dac834f3f2e0dd210b2dd254e91f8",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・`〈主語〉 + 〈動詞句1〉 and consequently + 〈動詞句2〉`\n用途: 同じ主語の二つの述語を結び、前の内容の結果として後の行為や状態を示す。\n例: The region receives little rainfall and consequently faces frequent water shortages.\n訳: その地域は降雨量が少なく、その結果しばしば水不足に直面する。"
      },
      {
        "id": "usage_note:001",
        "kind": "usage_note",
        "location": "line:55",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "4202b11af3091959cc4bdb34999726ee85d0ee963d7635ec33ea3821398551e0",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "`consequently` は、前に述べた事情・根拠から結果または論理的帰結を示す副詞であり、単なる時間順だけを示す語ではない。文頭だけでなく、接続詞の後や `be` の後で補語の前にも置ける。"
      },
      {
        "id": "synonym:001",
        "kind": "synonym",
        "location": "lines:59-64",
        "section": "＃意味・用法・関連表現",
        "sense": "1. 【副詞・文副詞／接続副詞】その結果、したがって",
        "text_sha256": "b5498a69fb4edbebeafee0505a0831308971bde4c8e850c449b661c4d0c09132",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary",
        "text": "・therefore\n定義: 前に述べた事実・理由から結果または結論が導かれることを示す。\n頻度: 〈7/10〉\n違い: `consequently` と同様に、前の事情を受けた結果を示す。\n例: The data are incomplete; therefore, no firm conclusion can be drawn.\n訳: データが不完全なので、確かな結論は導けない。"
      }
    ],
    "relation_results": [
      {
        "id": "example_translation:001",
        "kind": "example_translation",
        "target_ids": [
          "collocation:001"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "26750269ee9dd5b51b69765498e65b4a87effedbbc0238eb29e302fcc51b1271",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:002",
        "kind": "example_translation",
        "target_ids": [
          "collocation:002"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "0fddd7231b615b1468c1bb23515fe6ee82ffdf770efff68aeac4dbb2df355152",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:003",
        "kind": "example_translation",
        "target_ids": [
          "collocation:003"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "ae6f03bfc90aa62807a5306af7169ced4893be7f3fe0c7eef691a27f2c6671be",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:004",
        "kind": "example_translation",
        "target_ids": [
          "collocation:004"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "b7bd8e4f64f2b5b4416c868f399db21d336bb2525a56cb9582dc575f8de0f7d3",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "example_translation:005",
        "kind": "example_translation",
        "target_ids": [
          "collocation:005"
        ],
        "description": "コロケーションの用途、英文、訳で意味役割、修飾範囲、程度、レジスターが保存されていることを確認する。",
        "text_sha256": "2c3d879214f4eaf61bfe50841656663a25b4c418dce8fa21d84fb2637c575cf5",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "sense_definition_consistency:001",
        "kind": "sense_definition_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001"
        ],
        "description": "語義見出しの訳語・範囲と詳細定義が矛盾せず、見出しだけが定義より広い対象や物理的実体を断定していないことを確認する。",
        "text_sha256": "a610295e5ff2f26df8c51c3804bd7d2fb7fd9bef0c6ea2226069e2ad051c2267",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_usage_consistency:001",
        "kind": "definition_usage_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "usage_note:001"
        ],
        "description": "語義定義と語法・注意が互いに矛盾せず、注意書きで定義上の問題を後付け補修していないことを確認する。",
        "text_sha256": "fce9e9eb0b0e86ca9ca46179914e226d1702b8d93d1ac7cbe7296a1d33593011",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "definition_lexical_relation_consistency:001",
        "kind": "definition_lexical_relation_consistency",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "synonym:001"
        ],
        "description": "語義定義と類義語・反意語の上下関係、同義性、対立軸が矛盾せず、「別名」「広い呼称」「一種」などの関係が記事内で一貫することを確認する。",
        "text_sha256": "8277cf72d7d0cb887addb8bf5f8c64f4f8f91b1550440bc0da1b166b0d6adaa3",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:001",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:001",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "64266f8218e05b59fa5b328e57c30ff8773bcf7a71d4f83ce958af62d763bcd1",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:002",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:002",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "33e3dd99672a0cbf8186f4543cfaf38387d49b4c3e6f9fa3bc5989274908219d",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:003",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:003",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "ca4b8c251b857a52dc628a70fd4679f3bb7bcb9d3bc05c2f7cdbb60f1fc93be6",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:004",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:004",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "d39d1fcb6bead03cfe5f556fb3e00a9c692d7a5787e71641df1dec0c91665da5",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "pattern_example_coverage:005",
        "kind": "pattern_example_coverage",
        "target_ids": [
          "grammar_pattern:005",
          "collocation:001",
          "collocation:002",
          "collocation:003",
          "collocation:004",
          "collocation:005"
        ],
        "description": "文法パターンの意味・統語制約が同じ語義の用例群と整合し、主要フレームに自然な実例が対応することを確認する。",
        "text_sha256": "a3106a17ca4a65a6958aa03d9c19259e674f0f72ec86650194e7c3959f412dcb",
        "requires_evidence": true,
        "evidence_policy": "one_source"
      },
      {
        "id": "article_learning_risk:001",
        "kind": "article_learning_risk",
        "target_ids": [
          "sense_boundary:001",
          "definition:001",
          "usage_note:001"
        ],
        "description": "記事全体の語義構成、対比、訳語、限定表現から学習者が誤った一般化をしないことを横断確認する。",
        "text_sha256": "c6348d2d5096d4deca4d8be1a25c81d9b918e4a08525c424396b0f0b7d75ca3b",
        "requires_evidence": true,
        "evidence_policy": "two_sources_or_primary"
      }
    ],
    "normal_candidate_results": [],
    "blind_candidate_results": [
      {
        "id": "independent-candidate-1",
        "surface_form": "consequently",
        "frame": "Consequently, clause; clause; consequently, clause",
        "meaning": "前件として述べられた事実・状況・判断から、後件が結果または論理的帰結として導かれることを示す文副詞・接続副詞",
        "disposition": "included",
        "rationale": "Consequently, clause; clause; consequently, clause は、先行する命題を根拠・原因として後続の命題を結果又は帰結として提示する同一の文接続的用法である。",
        "semantic_assertions": [
          {
            "id": "assertion-1",
            "statement": "後件は前件との単なる時間的な前後関係ではなく、前件から生じる結果又は論理的帰結として解釈されなければならない。",
            "polarity": "must_hold",
            "scope": "前置された consequently とセミコロン後の consequently が結ぶ二つの命題"
          },
          {
            "id": "assertion-2",
            "statement": "consequently は後件の内容全体を、先行命題に照らした結果・帰結として位置づけなければならない。",
            "polarity": "must_hold",
            "scope": "文頭又はセミコロン後に置かれる consequently"
          }
        ]
      },
      {
        "id": "independent-candidate-2",
        "surface_form": "consequently",
        "frame": "subject + consequently + verb phrase; subject + be + consequently + complement; verb phrase 1 and consequently + verb phrase 2",
        "meaning": "前に示された事情・出来事を原因又は根拠として、その節内の行為・状態・判断を結果又は帰結として示す副詞",
        "disposition": "included",
        "rationale": "subject + consequently + verb phrase; subject + be + consequently + complement; verb phrase 1 and consequently + verb phrase 2 は、いずれも先行する事情に対する結果として節内の述語又は補語を修飾する同一の因果的副詞用法である。",
        "semantic_assertions": [
          {
            "id": "assertion-3",
            "statement": "修飾される行為・状態・判断は、文脈又は同じ文の先行内容に示される事情の結果として理解されなければならない。",
            "polarity": "must_hold",
            "scope": "動詞前、be の後、又は and の後に置かれる consequently"
          },
          {
            "id": "assertion-4",
            "statement": "この用法は出来事の単なる後続時点だけを表してはならない。",
            "polarity": "must_not_hold",
            "scope": "節内の consequently"
          }
        ]
      },
      {
        "id": "independent-candidate-3",
        "surface_form": "consequently",
        "frame": "temporal-adverb use meaning 'afterwards' or 'later'",
        "meaning": "単に時間的に後で起きることを示す副詞",
        "disposition": "excluded",
        "rationale": "temporal-adverb use meaning 'afterwards' or 'later' は consequent の因果・帰結関係を要求せず、consequently の主要な意味範囲には含めない。",
        "semantic_assertions": [
          {
            "id": "assertion-5",
            "statement": "先行事実と後続事実の時間順序だけで用法が成立してはならず、結果又は論理的帰結の関係が必要である。",
            "polarity": "must_not_hold",
            "scope": "consequently の意味範囲"
          }
        ]
      }
    ],
    "finding_results": [
      {
        "id": "CHECK-EVID-001",
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "pronunciation",
          "line_start": 15,
          "line_end": 15,
          "exact_quote": "さらに米語では第2音節が /ə/、英語では /ɪ/ となる。"
        },
        "severity": "blocking",
        "rationale": "C002/U002 の根拠は地域別IPAを示すが、F002（Cambridge）は米語第2音節を /ə/ とする一方、F004（Oxford）は米語を /ˈkɑːnsɪkwentli/ と記録する。本文はこの食い違いを示さず、米語第2音節 /ə/ を無条件に断定しているため、提示された根拠集合からこの主張を直接支持できない。",
        "evidence_link_ids": [
          "F002",
          "F004"
        ],
        "suggested_direction": "Cambridgeの表記に帰属させるか、両資料に共通して支持される地域差の記述へ主張を限定する。"
      },
      {
        "id": "CHECK-EVID-002",
        "taxonomy_id": "evidence_claim_mismatch",
        "location": {
          "section": "etymology",
          "line_start": 19,
          "line_end": 19,
          "exact_quote": "形容詞 `consequent` に副詞語尾 `-ly` が付いた語である。`consequent` はラテン語 *consequi*「あとに従う、続いて起こる」にさかのぼり、`con-`「ともに」と *sequi*「従う」に関係する。"
        },
        "severity": "blocking",
        "rationale": "C004/F007 は consequently が consequent に関連し、ラテン語 consequi（follow after）、com-、sequi（follow）へつながることを支持する。しかし提示されたfactは consequent + -ly という語形成、または `con-` が「ともに」を意味することを記録していない。本文はF007が直接支持する範囲を超えている。",
        "evidence_link_ids": [
          "F007"
        ],
        "suggested_direction": "F007が直接記録する consequent と consequi『follow after』の関係に限定するか、形態素と日本語グロスを直接支持する根拠へ差し替える。"
      },
      {
        "id": "COLD-001",
        "location": "発音記号",
        "severity": "high",
        "description": "米語第2音節を /ə/、英語第2音節を /ɪ/ と一律に対比し、さらに quent の母音はいずれも /ə/ と断定している。発音辞書には米語を /ɪ/、quent を /e/ と表記するものもあり得るため、この説明だけを唯一の発音規則として学ばせるのは不正確になり得る。",
        "reason": "「米語は第1音節が /ɑː/、英語は /ɒ/ で、さらに米語では第2音節が /ə/、英語では /ɪ/ となる。`quent` の母音はいずれも弱く /ə/ と発音する。」は、本文に示した一組のIPAを地域差一般として断定している。実際の辞書表記には第2音節・quent 部分に揺れがあり得るので、学習者が /ə/ と /ɪ/ の対立を常に守るべき規則だと誤解するおそれがある。",
        "suggested_direction": "採用した辞書・表記体系を明示するか、「辞書により米語の第2音節や quent 部分の表記に揺れがある」と注記して、地域差を単一の絶対規則として説明しない。",
        "scope_anchors": [
          {
            "id": "COLD-001-A1",
            "exact_quote": "米語は第1音節が /ɑː/、英語は /ɒ/ で、さらに米語では第2音節が /ə/、英語では /ɪ/ となる。`quent` の母音はいずれも弱く /ə/ と発音する。",
            "location_hint": "発音記号節の2文目から3文目"
          }
        ]
      },
      {
        "id": "COLD-002",
        "location": "語形成",
        "severity": "medium",
        "description": "consequential を「重要な、重大な」に限定し、consequently と対比して因果関係をつなぐ語ではないと述べると、結果として続くという consequential の別の語義・用法との関係が見えなくなる。",
        "reason": "「・`consequential`：形容詞。「重要な、重大な」。`consequently` と違い、因果関係をつなぐ副詞ではない。」は、品詞の違いを説明する意図は分かるものの、consequential にも「結果として生じる・続く」という語義がある点を落としている。そのため、学習者はこの語が consequence / consequent と共有する結果に関する意味を持たないと一般化しかねない。",
        "suggested_direction": "「重要な、重大な」を主要な現代用法として示すなら、結果として生じる意味もあることを補い、consequently とは『因果をつなぐ副詞ではなく形容詞である』と品詞・機能の差に限定して対比する。",
        "scope_anchors": [
          {
            "id": "COLD-002-A1",
            "exact_quote": "・`consequential`：形容詞。「重要な、重大な」。`consequently` と違い、因果関係をつなぐ副詞ではない。",
            "location_hint": "語形成節の consequential 項目"
          }
        ]
      },
      {
        "id": "COLD-003",
        "location": "意味・用法・関連表現／文法パターン",
        "severity": "low",
        "description": "主語の直後・主要動詞の前という語順を基本形として示すだけでは、助動詞・完了形・受動態のある文で consequently を置く位置を狭く覚えさせやすい。後段に be の例はあるが、パターン説明自体が包括的ではない。",
        "reason": "「`〈主語〉 + consequently + 〈動詞句〉`＝その結果〈主語〉は…する。文頭で使うときは通常後ろにコンマを置き、二つの独立した節をコンマだけでつなぐ `…, consequently, …` は避ける。」は、consequently の文中位置を主語直後・主要動詞前に固定的に読める形で提示している。実際には助動詞・be・完了形などに応じた位置もあるため、このパターンだけを一般規則とすると誤用につながり得る。",
        "suggested_direction": "「主語の後、主要動詞の前」は一例・よくある位置として示し、助動詞や be の後にも置けることを短く補足するか、文中配置のパターンを複数提示する。",
        "scope_anchors": [
          {
            "id": "COLD-003-A1",
            "exact_quote": "`〈主語〉 + consequently + 〈動詞句〉`＝その結果〈主語〉は…する。文頭で使うときは通常後ろにコンマを置き、二つの独立した節をコンマだけでつなぐ `…, consequently, …` は避ける。",
            "location_hint": "意味・用法・関連表現節の文法パターン"
          },
          {
            "id": "COLD-003-A2",
            "exact_quote": "用途: 結果を表す副詞として、主語の後、主要動詞の前に置く。",
            "location_hint": "コロケーションの〈主語〉 + consequently + 〈動詞句〉項目"
          }
        ]
      }
    ],
    "evidence_checks": [],
    "source_inventory_results": [
      {
        "id": "U001",
        "source_fact_ids": [
          "F001",
          "F003",
          "F005"
        ],
        "canonical_statement": "Consequently is an adverb that marks a result or conclusion following from stated circumstances.",
        "disposition": "included",
        "rationale": "This is the article's sole lexical sense."
      },
      {
        "id": "U002",
        "source_fact_ids": [
          "F002",
          "F004"
        ],
        "canonical_statement": "The word has distinct British and American vowel realizations in the first two syllables.",
        "disposition": "included",
        "rationale": "The regional IPA is stated in the pronunciation section."
      },
      {
        "id": "U003",
        "source_fact_ids": [
          "F006"
        ],
        "canonical_statement": "Consequently can occur inside a clause as well as in result-linking sentence position.",
        "disposition": "included",
        "rationale": "The article teaches clause-internal placement with attested patterns."
      },
      {
        "id": "U004",
        "source_fact_ids": [
          "F007"
        ],
        "canonical_statement": "The word derives through consequent from the Latin follow-after verb consequi.",
        "disposition": "included",
        "rationale": "This supports the compact etymology."
      },
      {
        "id": "U005",
        "source_fact_ids": [
          "F008"
        ],
        "canonical_statement": "Consequential is a related adjective and is not the causal connective adverb consequently.",
        "disposition": "included",
        "rationale": "This contrast prevents a common form-based confusion."
      },
      {
        "id": "U006",
        "source_fact_ids": [
          "F009"
        ],
        "canonical_statement": "Consequence is a related result noun whose plural often has negative-result associations.",
        "disposition": "included",
        "rationale": "This is a directly supported word-formation note."
      },
      {
        "id": "U007",
        "source_fact_ids": [
          "F010"
        ],
        "canonical_statement": "Consequent is a related adjective for something that follows as an effect or result.",
        "disposition": "included",
        "rationale": "This supports the related-form entry."
      }
    ]
  },
  "response_template": {
    "decision": null,
    "blockers": [],
    "notes": [],
    "target_results": [
      {
        "id": "pronunciation:001",
        "status": null,
        "notes": "",
        "target_id": "pronunciation:001"
      },
      {
        "id": "etymology:001",
        "status": null,
        "notes": "",
        "target_id": "etymology:001"
      },
      {
        "id": "word_formation:001",
        "status": null,
        "notes": "",
        "target_id": "word_formation:001"
      },
      {
        "id": "word_formation:002",
        "status": null,
        "notes": "",
        "target_id": "word_formation:002"
      },
      {
        "id": "word_formation:003",
        "status": null,
        "notes": "",
        "target_id": "word_formation:003"
      },
      {
        "id": "sense_boundary:001",
        "status": null,
        "notes": "",
        "target_id": "sense_boundary:001"
      },
      {
        "id": "definition:001",
        "status": null,
        "notes": "",
        "target_id": "definition:001"
      },
      {
        "id": "frequency:001",
        "status": null,
        "notes": "",
        "target_id": "frequency:001"
      },
      {
        "id": "register:001",
        "status": null,
        "notes": "",
        "target_id": "register:001"
      },
      {
        "id": "grammar_pattern:001",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:001"
      },
      {
        "id": "grammar_pattern:002",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:002"
      },
      {
        "id": "grammar_pattern:003",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:003"
      },
      {
        "id": "grammar_pattern:004",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:004"
      },
      {
        "id": "grammar_pattern:005",
        "status": null,
        "notes": "",
        "target_id": "grammar_pattern:005"
      },
      {
        "id": "collocation:001",
        "status": null,
        "notes": "",
        "target_id": "collocation:001"
      },
      {
        "id": "collocation:002",
        "status": null,
        "notes": "",
        "target_id": "collocation:002"
      },
      {
        "id": "collocation:003",
        "status": null,
        "notes": "",
        "target_id": "collocation:003"
      },
      {
        "id": "collocation:004",
        "status": null,
        "notes": "",
        "target_id": "collocation:004"
      },
      {
        "id": "collocation:005",
        "status": null,
        "notes": "",
        "target_id": "collocation:005"
      },
      {
        "id": "usage_note:001",
        "status": null,
        "notes": "",
        "target_id": "usage_note:001"
      },
      {
        "id": "synonym:001",
        "status": null,
        "notes": "",
        "target_id": "synonym:001"
      }
    ],
    "relation_results": [
      {
        "id": "example_translation:001",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:001"
      },
      {
        "id": "example_translation:002",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:002"
      },
      {
        "id": "example_translation:003",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:003"
      },
      {
        "id": "example_translation:004",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:004"
      },
      {
        "id": "example_translation:005",
        "status": null,
        "notes": "",
        "relation_id": "example_translation:005"
      },
      {
        "id": "sense_definition_consistency:001",
        "status": null,
        "notes": "",
        "relation_id": "sense_definition_consistency:001"
      },
      {
        "id": "definition_usage_consistency:001",
        "status": null,
        "notes": "",
        "relation_id": "definition_usage_consistency:001"
      },
      {
        "id": "definition_lexical_relation_consistency:001",
        "status": null,
        "notes": "",
        "relation_id": "definition_lexical_relation_consistency:001"
      },
      {
        "id": "pattern_example_coverage:001",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:001"
      },
      {
        "id": "pattern_example_coverage:002",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:002"
      },
      {
        "id": "pattern_example_coverage:003",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:003"
      },
      {
        "id": "pattern_example_coverage:004",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:004"
      },
      {
        "id": "pattern_example_coverage:005",
        "status": null,
        "notes": "",
        "relation_id": "pattern_example_coverage:005"
      },
      {
        "id": "article_learning_risk:001",
        "status": null,
        "notes": "",
        "relation_id": "article_learning_risk:001"
      }
    ],
    "normal_candidate_results": [],
    "blind_candidate_results": [
      {
        "id": "independent-candidate-1",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-1",
          "assertion-2"
        ],
        "verified_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "assertion_results": [
          {
            "id": "assertion-1",
            "status": null,
            "notes": ""
          },
          {
            "id": "assertion-2",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-candidate-2",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-3",
          "assertion-4"
        ],
        "verified_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "assertion_results": [
          {
            "id": "assertion-3",
            "status": null,
            "notes": ""
          },
          {
            "id": "assertion-4",
            "status": null,
            "notes": ""
          }
        ]
      },
      {
        "id": "independent-candidate-3",
        "status": null,
        "notes": "",
        "assertion_ids": [
          "assertion-5"
        ],
        "verified_body_sha256": "23329760d3d9cb045d4edda70223bd380de1685d5ebd089e1d2f2578ce3c94ae",
        "assertion_results": [
          {
            "id": "assertion-5",
            "status": null,
            "notes": ""
          }
        ]
      }
    ],
    "finding_results": [
      {
        "id": "CHECK-EVID-001",
        "status": null,
        "notes": ""
      },
      {
        "id": "CHECK-EVID-002",
        "status": null,
        "notes": ""
      },
      {
        "id": "COLD-001",
        "status": null,
        "notes": ""
      },
      {
        "id": "COLD-002",
        "status": null,
        "notes": ""
      },
      {
        "id": "COLD-003",
        "status": null,
        "notes": ""
      }
    ],
    "evidence_checks": [],
    "source_inventory_results": [
      {
        "id": "U001",
        "status": null,
        "notes": "",
        "union_id": "U001"
      },
      {
        "id": "U002",
        "status": null,
        "notes": "",
        "union_id": "U002"
      },
      {
        "id": "U003",
        "status": null,
        "notes": "",
        "union_id": "U003"
      },
      {
        "id": "U004",
        "status": null,
        "notes": "",
        "union_id": "U004"
      },
      {
        "id": "U005",
        "status": null,
        "notes": "",
        "union_id": "U005"
      },
      {
        "id": "U006",
        "status": null,
        "notes": "",
        "union_id": "U006"
      },
      {
        "id": "U007",
        "status": null,
        "notes": "",
        "union_id": "U007"
      }
    ],
    "checker_recheck_results": [
      {
        "id": "evidence",
        "pass_id": "evidence",
        "status": null,
        "notes": ""
      },
      {
        "id": "example-attribution",
        "pass_id": "example-attribution",
        "status": null,
        "notes": ""
      },
      {
        "id": "frame-relation",
        "pass_id": "frame-relation",
        "status": null,
        "notes": ""
      },
      {
        "id": "pronunciation",
        "pass_id": "pronunciation",
        "status": null,
        "notes": ""
      },
      {
        "id": "qualification",
        "pass_id": "qualification",
        "status": null,
        "notes": ""
      },
      {
        "id": "sense-structure",
        "pass_id": "sense-structure",
        "status": null,
        "notes": ""
      },
      {
        "id": "translation",
        "pass_id": "translation",
        "status": null,
        "notes": ""
      }
    ],
    "chronology_results": [
      {
        "id": "body_hash_binding",
        "check_id": "body_hash_binding",
        "status": null,
        "notes": ""
      },
      {
        "id": "cold_and_normal_before_revision",
        "check_id": "cold_and_normal_before_revision",
        "status": null,
        "notes": ""
      },
      {
        "id": "revision_before_final_blind",
        "check_id": "revision_before_final_blind",
        "status": null,
        "notes": ""
      },
      {
        "id": "final_blind_before_seal",
        "check_id": "final_blind_before_seal",
        "status": null,
        "notes": ""
      },
      {
        "id": "post_blind_completion",
        "check_id": "post_blind_completion",
        "status": null,
        "notes": ""
      }
    ]
  },
  "input_bindings": {
    "pass_findings.json": "9c52be81c17aa1610366ef77fe2eb9d5a79680e2c632c694e61c33d1b18847db",
    "cold_review.json": "f47db51c6aadf5fe8129a0f19be4299ff144ccdff5e27bc010659400dd19987b",
    "final_blind.json": "c0a3eb07fa10a8615eda514de66ee135a31363a89a240dfe694a989038f62416",
    "blind_seal.json": "2a209bd412ecb80eafcfd5ec9653e05f1a90e95e84c907a318875eafdc8c5e75",
    "pre_blind_resolution.json": "791aab170c264b7e1cdab54e1721aec395fabb94b475df406c15bbbd88f2422a",
    "pre_blind_revision.json": "a56f9a2f429a85e32da0ffbec4bd53ec71001e09c339e24659986c8b61e917dd",
    "checker_recheck_manifest.json": "3c5943f544c98325c9d2feeb35a1bee95f7719b8f063c5a10a0086950316a03e",
    "post_blind_resolution.json": "d570a60ac7a9e04e748cbf368df3a0142c9abc740713501b019f9f6c13bdcfa5",
    "post_blind_verification.json": "d0ae8b481385480408c1d4cbc24399c5d404561af1ffef8326bf4c3108759d27",
    "targeted_adjudications.json": "af5af9b139e61078d584a712c70a3ce285f0407cc7fa63836b8195db9ea9f3b6",
    "source_inventory.json": "bad5d8e9e488f146a079aecef165cc72716e979e0dadff48d81e485809f5ddd8",
    "resolutions.json": "3a3a1fed0804c69472fd06937e8ed606953b87a27557511ff709540d4b3869fc",
    "check_passes/checker_passes.stage1.json": "cf5f77d69f6b055d59c108ace506f800ccff8396bffe7f453d9daac859235448",
    "check_passes/evidence.json": "c722c7c7ec47daecfdf442e3c508328f9d0dcbb197e76ddb958fc66748a5bfcd",
    "check_passes/evidence.request.json": "a2f47a56ce6e5fb7e28ea49b435da312d5745109e35fa8762ceb3453c7afb83f",
    "check_passes/example-attribution.alignment-key.json": "b7ac374114c612a868bbad25da7cd76246a280d2827f0518b4deeebe66b832bf",
    "check_passes/example-attribution.blind-record.json": "349ee3c1876ac2eac55fade8de8e667cde3a6b327749491917a882a33a67b0ba",
    "check_passes/example-attribution.json": "e2a8c92ae4c54674fa487582a4fb86b0de3714ed8eb5e2499d187e3dd59b2709",
    "check_passes/example-attribution.request.json": "ef23abb24d81f73cac5dcd7595b3855660049af5e72b915f730b4c61c84043bf",
    "check_passes/frame-relation.antonym-axis.adjudication-record.json": "e31e19ded9cb428178e2163060b0964c770f9266328230030dc6ec224c7f284a",
    "check_passes/frame-relation.antonym-axis.alignment-key.json": "0fa72c898099d0eb28c43aace387a43bbf4b530594a87e57a4c1ba88c28b288d",
    "check_passes/frame-relation.antonym-axis.blind-record.json": "71ce502d9ed8dccf48c5bb0e52a4c1b92ea69594cfb85534334bb194a19fe20d",
    "check_passes/frame-relation.antonym-axis.stage2.request.json": "0fd444fcd09ce9bad871c59cf3babe28c2fcde65785bd461fb4bd7bd4e451f58",
    "check_passes/frame-relation.request.json": "03233ff3a0dbb7bbbe45c5d92bc145e8a658dbb5f7f863b0046ceecaf6a96a3f",
    "check_passes/input_snapshot.json": "e325ac4cf6ecad96ad8d3ebae599ab32705f57c386c0bb7920a9b12a2bf3fd88",
    "check_passes/pronunciation.json": "3cd1f6978abba427bb760147df23b65ea61d91f3cbcde7e7286facc5de6f87c2",
    "check_passes/pronunciation.request.json": "acc6c8348e78fdf631aca4391364fca4a72bfa1b42e344cdfc8a9797a070b971",
    "check_passes/qualification.json": "73050a850bd5ee73e8afea2a69c3edb7407a116968b603d348c70d899a4d4646",
    "check_passes/qualification.request.json": "790be3ad63fa97ea2b1845ab5d62f705cd870a966a543d69ac3b8c769fe26c70",
    "check_passes/sense-structure.json": "e3e59a707a8692d5cf29cf0b3e407473cf30b33aaab40081671dd5ca811bb20f",
    "check_passes/sense-structure.request.json": "4b2041c5b81c253942874b8ebbf059bc8d5f4cf44c71daa050418884010b11a7",
    "check_passes/translation.json": "5265bbb6569bbf2cb6bf82d01143992b8f1cf2795c458755c946e015ca1f9874",
    "check_passes/translation.request.json": "34f229ffe07393c4fcc986f969cfa55e62f55461193129374c7436cd1893c49e"
  },
  "contract_version": "review_preflight_v1"
}
```
