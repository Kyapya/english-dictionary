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
  "entry_body": "\n＃発音記号\n\n基本: /pʌbˈlɪsəti/。米語では /pəˈblɪsəti/ も使われる。いずれも4音節で、第2音節に主強勢がある。/pʌbˈlɪsəti/ では第1音節が /pʌb/、第2音節が /ˈlɪs/ となる。/pəˈblɪsəti/ では第1音節が弱い /pə/ となり、/b/ は第2音節頭の /bl/ と発音される。これは米英の絶対的な地域差というより、辞書や話者による発音差として覚えるとよい。語末は /əti/ で、綴りの -ity を /aɪti/ と読まない。  \n\n＃語源\n\nフランス語 publicité を経て、ラテン語 publicus「公の、人民の」にさかのぼる。英語ではもともと「公にされている状態・公開性」を表し、そこから「世間に知られるようにすること」や、現代の「宣伝・広報活動」へ意味が発展した。  \n\n＃語形成\n\n・publicist：publicity を作り、扱い、広める仕事をする人。映画、作家、芸能人、企業などの広報担当者を指す。  \n・publicity campaign：商品、作品、行事、主張などに注目を集めるための宣伝・広報キャンペーン。  \n・publicity material：宣伝・広報用の資料。  \n・publicity stunt：世間の注目を集めるために意図して行う行為・仕掛け。話題作りの含みを持つ。  \n\n＃意味・用法・関連表現\n\n1. 【名詞・不可算】公衆の注目、報道上の露出\n\n【日本語訳・定義】人・企業・作品・出来事などが、新聞、テレビなどのメディアを通じて世間から受ける注目や報道上の露出。好意的とは限らず、good/bad/negative/unwanted publicity のように評価を添えられる。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準的な一般語。複数の一般辞書で主要な名詞として扱われる。  \n\n【文法パターン】gain/receive publicity＝世間の注目・報道を得る／widespread publicity＝広範な世間の注目・報道／good/bad/negative/unwanted publicity＝好意的な・悪い・否定的な・望まない注目／shun publicity＝世間の注目・報道を避ける  \n\n【コロケーション】\n\n・gain/receive publicity  \n用途: 人・団体・作品・出来事が世間の注目や報道を受けることを表す。  \n例: The charity gained widespread publicity after the athlete supported its campaign.  \n訳: その慈善団体は、その選手がキャンペーンを支持した後、広く世間の注目を浴びた。  \n\n・widespread publicity  \n用途: 広い地域や多くの媒体に及ぶ世間の注目・報道を表す。  \n例: The discovery received widespread publicity in the national press.  \n訳: その発見は全国紙で広く報道された。  \n\n・good/bad publicity  \n用途: 注目が対象に好影響または悪影響を与えることを評価する。  \n例: The scandal gave the company bad publicity.  \n訳: その不祥事は会社に否定的な世間の注目をもたらした。  \n\n・negative publicity  \n用途: 批判、不祥事、悪い報道などによる否定的な世間の注目を表す。  \n例: The restaurant responded quickly to the negative publicity surrounding the safety complaint.  \n訳: そのレストランは、安全性に関する苦情をめぐる否定的な報道にすぐ対応した。  \n\n・shun publicity  \n用途: 世間の注目や報道を意図的に避けることを表す。  \n例: The novelist shuns publicity and rarely gives interviews.  \n訳: その小説家は世間の注目を避け、めったにインタビューに応じない。  \n\n【語法・注意】現代の一般用法ではこの語義の publicity は通常不可算で、a publicity や publicities は一般に避け、a lot of publicity、the publicity surrounding the case のように使う。publicity は注目・報道を表し、好評や長期的な名声を必ず含むわけではない。good/bad/negative/unwanted publicity のように評価を添えられる。  \n\npublicity about 〈話題〉は話題に関する注目・報道、publicity for 〈対象〉（結果読み）は対象が受ける注目・報道を指す。対象に注目を集める活動読みの publicity for 〈対象〉は語義2で扱う。結果として受けた注目を明確にするなら gain/receive publicity for のように動詞で示す。古風・形式的には「公開性、公然性」の意味で使われることもある。  \n\n【類義語】\n\n・attention  \n定義: 人や話題に関心が向けられていること。  \n頻度: 〈10/10〉  \n違い: publicity は特に新聞・テレビなどを通じた公的な注目・露出に焦点があり、attention より媒体や公衆に寄る。  \n例: The announcement attracted attention from local residents.  \n訳: その発表は地元住民の注目を集めた。  \n\n・exposure  \n定義: 人・商品・活動などが公衆や媒体に知られること。  \n頻度: 〈8/10〉  \n違い: publicity は露出の機会一般より、世間の注目・報道を受けること、またはそれを集める活動を表す。  \n例: The interview gave the small business valuable exposure.  \n訳: そのインタビューは、その小企業に貴重な公的露出をもたらした。  \n\n・coverage  \n定義: 新聞、テレビ、ウェブなどによる報道。  \n頻度: 〈9/10〉  \n違い: coverage はメディアによる報道内容を指し、publicity は報道による注目や、注目を集める活動まで含む。  \n例: The issue received extensive media coverage.  \n訳: その問題はメディアで大きく報道された。  \n\n・fame  \n定義: 多くの人に知られている状態。  \n頻度: 〈10/10〉  \n違い: fame は知名度という状態を指すのに対し、publicity は一時的な注目・報道も表し、negative publicity のように評価中立である。  \n例: The actor achieved international fame after the film won several awards.  \n訳: その俳優は、その映画がいくつも賞を取った後、国際的な名声を得た。  \n\n2. 【名詞・不可算】宣伝活動、広報\n\n【日本語訳・定義】人、商品、作品、行事、主張などに世間の関心を集めるために行う広報・宣伝活動。広告に限らず、情報提供などの広報手段を含み得る。ここでは世間の注目を集める側の活動・手段に焦点を置く。  \n\n【頻度】〈9/10〉  \n\n【レジスター/領域】標準的な一般語。複数の一般辞書で活動・情報に関わる名詞用法として扱われる。  \n\n【文法パターン】publicity for 〈映画・商品・行事〉（活動読み）＝対象に注目を集める広報／advance publicity for 〈発売・行事〉＝発売・行事の事前広報／publicity campaign/material/stunt＝宣伝キャンペーン・資料・仕掛け  \n\n【コロケーション】\n\n・a publicity campaign  \n用途: 商品、作品、行事、主張などへの注目を集める計画的な宣伝活動を表す。  \n例: The museum launched a publicity campaign for its new exhibition.  \n訳: その博物館は新しい展覧会の広報キャンペーンを始めた。  \n\n・publicity material  \n用途: メディアや一般の人に提供する広報・宣伝用の資料を表す。  \n例: The press office prepared publicity material for the product launch.  \n訳: 広報室は製品発売のための宣伝資料を用意した。  \n\n・advance publicity for 〈発売・行事〉  \n用途: 映画、書籍、製品、行事などの開始前に行う事前広報を表す。  \n例: The organizers arranged advance publicity for the festival several months before it opened.  \n訳: 主催者は祭りの開幕数か月前から事前広報を手配した。  \n\n・a publicity stunt  \n用途: メディアや世間の注目を集めるために意図して行う行為・仕掛けを表す。  \n例: The company staged a publicity stunt by projecting its logo onto the river bridge.  \n訳: その会社は川に架かる橋へロゴを投影する話題作りの仕掛けを行った。  \n\n【語法・注意】この語義でも publicity は通常不可算で、a publicity campaign、a publicity stunt のように、数えられるのは campaign や stunt などの具体的な活動である。この語義の publicity for 〈対象〉は、対象に注目を集める活動を指す。対象が受ける注目・報道という結果読みは語義1に置く。  \n\nadvertising は通常、料金を払って掲載・放送する広告やその活動に焦点がある。一般的な区別では publicity と paid advertising を分けるが、辞書や文脈によっては publicity が有料広告・宣伝まで指すこともある。  \n\npublicity stunt は、世間の注目を集める意図を前面に出す行為・仕掛けを指す。publicity for 〈対象〉が対象の受けた注目・報道を表す結果読みになる場合は語義1の用法であり、この語義2の活動読みとは分ける。結果としての注目を明確にするなら、語義1の gain/receive publicity for のように動詞で示す。  \n\n【類義語】\n\n・advertising  \n定義: 商品、サービス、組織などを広告によって公衆に知らせる活動。  \n頻度: 〈10/10〉  \n違い: advertising は有料の広告メッセージや広告業務に焦点がある。publicity は通常、情報・活動によって公衆の注目を集める語だが、辞書や文脈によって paid advertising を含むこともある。  \n例: The company increased its advertising budget before the holiday season.  \n訳: その会社は休暇シーズンの前に広告予算を増やした。  \n\n・promotion  \n定義: 商品、サービス、作品、考えなどの販売・普及・認知を高める活動。  \n頻度: 〈9/10〉  \n違い: promotion は販売・普及も含む広い活動語で、publicity は公衆の注目を集める情報・活動に焦点がある。  \n例: The festival used social media promotion to sell more tickets.  \n訳: その祭りは、より多くのチケットを売るためにSNSで販促を行った。  \n\n・public relations  \n定義: 企業・組織・人物と公衆との関係を管理する活動。  \n頻度: 〈9/10〉  \n違い: public relations は公衆との関係全体を扱う広い活動で、publicity は注目を集める広報活動やその結果を指しやすい。  \n例: The company hired a public relations firm after the data breach.  \n訳: その会社はデータ漏えいの後、広報会社を雇った。  \n\n・marketing  \n定義: 市場調査、商品設計、価格設定、流通、宣伝などを通じて需要と販売を形成する活動。  \n頻度: 〈10/10〉  \n違い: marketing は市場活動全体を扱う広い語で、publicity と重なる場合もある。ただし publicity は人・作品・行事・主張にも用いられる、注目を集める情報発信や活動を指す。  \n例: The marketing team tested the new packaging with several customer groups.  \n訳: マーケティングチームは複数の顧客グループで新しい包装を試した。  ",
  "_output_metadata": {
    "schema_version": "final_review_v2",
    "stage": "final_review",
    "run_id": "blind-publicity-20260902T194039Z-23d464b6",
    "context_id": "blind-publicity-context-20260902T194039Z-23d464b6",
    "input_body_sha256": "2a79e044fd00e512fbd56935b8ef7b0b6e53fb843aff9ea30d2e2716e3466a8d",
    "prompt_sha256": "3158e690b19b0f822a032dffa1cbfe1d38d64a0de2c1dba582554fa2b729f117",
    "input_artifacts": [
      "entry_body",
      "all_findings",
      "resolutions",
      "sealed_final_blind",
      "final_review_spec"
    ],
    "blind_output_sha256": "c465ff17fb0104bdeaec7369218699bd9ac436dec43582571b778eca4a6160cf"
  },
  "pass_findings": {
    "schema_version": "normal_review_v2",
    "stage": "normal_review",
    "run_id": "normal-publicity-20260902T194039Z-23d464b6",
    "context_id": "normal-publicity-context-20260902T194039Z-23d464b6",
    "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
    "prompt_sha256": "5178f5a14a9525317811a34e6cd307108436f4babc1299fcd2eb9031f28ba737",
    "input_artifacts": [
      "router_selected_sections",
      "checker_pass_specs"
    ],
    "recorded_at": "2026-09-02T20:09:45.081144+00:00",
    "pass_outputs": [
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "translation",
        "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a063a8-9a9e-78f1-9fca-ce0fe46e50b0"
        },
        "findings": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "sense-structure",
        "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a063a8-a678-7083-b005-4bee3b3130ac"
        },
        "findings": []
      },
      {
        "pass_id": "frame-relation",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a063ad-98d2-7430-8a73-13aa483c109e"
        },
        "antonym_axis_blind_record": {
          "schema_version": "antonym_axis_blind_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
          "blind_request_sha256": "8e9b4d7dc0f727c40f58097f13aeb2bc780ac7c0d65ce94d7a482d33f740b124",
          "recorded_at": "2026-09-02T19:52:26Z",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "01a063ad-98d2-7430-8a73-13aa483c109e"
          },
          "axes": []
        },
        "antonym_axis_adjudication_record": {
          "schema_version": "antonym_axis_adjudication_record_v1",
          "pass_id": "frame-relation",
          "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
          "stage2_request_sha256": "4ab6bf4e682bffa4fa8a0912d9651a834b04f29f7fcb372b43be689d9e4d0d94",
          "blind_record_sha256": "19206392037543fe2be8499c9b3fb24c77339a105bbbe24d932e6fa4b2297b41",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "01a063ad-98d2-7430-8a73-13aa483c109e"
          },
          "adjudications": [],
          "frame_findings": [],
          "unrouted_observations": []
        },
        "aligned_at": "2026-09-02T20:15:04.119138+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "pass_id": "example-attribution",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a063a8-abbe-7e13-a49a-10d7581f5085"
        },
        "blind_attribution_record": {
          "schema_version": "example_attribution_blind_record_v1",
          "pass_id": "example-attribution",
          "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
          "blind_request_sha256": "a02539db6bd38eff541c3d6ef24b19a3871b2226c66f83945291a402cf55ef8a",
          "recorded_at": "2026-09-02T19:48:52.119Z",
          "reviewer": {
            "mode": "handoff",
            "declared_model": "gpt-5",
            "ingested_by": "human",
            "agent_id": "01a063a8-abbe-7e13-a49a-10d7581f5085"
          },
          "sense_inventory": [
            {
              "definition": "人・企業・作品・出来事などが、新聞、テレビなどのメディアを通じて世間から受ける注目や報道上の露出。好意的とは限らず、good/bad/negative/unwanted publicity のように評価を添えられる。",
              "label": "1. 【名詞・不可算】公衆の注目、報道上の露出",
              "sense_id": "sense:001"
            },
            {
              "definition": "人、商品、作品、行事、主張などに世間の関心を集めるために行う広報・宣伝活動。広告に限らず、情報提供などの広報手段を含み得る。ここでは世間の注目を集める側の活動・手段に焦点を置く。",
              "label": "2. 【名詞・不可算】宣伝活動、広報",
              "sense_id": "sense:002"
            }
          ],
          "blind_order": [
            "blind-01",
            "blind-02",
            "blind-03",
            "blind-04",
            "blind-05",
            "blind-06",
            "blind-07",
            "blind-08",
            "blind-09"
          ],
          "attributions": [
            {
              "classification": "unique",
              "blind_id": "blind-01",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "gained widespread publicity",
                "after the athlete supported"
              ],
              "example": "The charity gained widespread publicity after the athlete supported its campaign.",
              "example_id": "ex-93e5ac564ed0",
              "rationale": "\"gained widespread publicity\" は団体が publicity を獲得する結果状態を表し、widespread も広がった注目を示すため、最有力はsense:001（世間から受ける注目・報道上の露出）。sense:002（注目を集める広報活動）なら団体が活動を手配・実施する構文になるが、この文では publicity は支持後に団体が受けた結果であり、活動そのものとしては成立しない。",
              "translation": "その慈善団体は、その選手がキャンペーンを支持した後、広く世間の注目を浴びた。"
            },
            {
              "classification": "unique",
              "blind_id": "blind-02",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "staged a publicity stunt",
                "by projecting its logo"
              ],
              "example": "The company staged a publicity stunt by projecting its logo onto the river bridge.",
              "example_id": "ex-b3cd135cea73",
              "rationale": "\"staged a publicity stunt\" は会社が意図的に行った仕掛けという活動・手段の構文を作るため、最有力はsense:002（世間の関心を集める宣伝・広報活動）。sense:001（受ける注目・報道露出）は通常その活動の結果として会社に生じるものだが、この文の publicity は会社が実施した stunt の目的・性質を表し、受けた注目としては同じ位置で成立しない。",
              "translation": "その会社は川に架かる橋へロゴを投影する話題作りの仕掛けを行った。"
            },
            {
              "classification": "unique",
              "blind_id": "blind-03",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "shuns publicity",
                "rarely gives interviews"
              ],
              "example": "The novelist shuns publicity and rarely gives interviews.",
              "example_id": "ex-ee610cdc723c",
              "rationale": "\"shuns publicity\" は小説家が避ける対象として publicity を取り、rarely gives interviews は公的な露出を避ける行動を補強するため、最有力はsense:001（世間から受ける注目・報道露出）。sense:002（宣伝・広報活動）を避ける意味も抽象的には考えられるが、同じ文の publicity はインタビューと並ぶ本人への公衆の注目・露出であり、活動を運営する意味ではない。",
              "translation": "その小説家は世間の注目を避け、めったにインタビューに応じない。"
            },
            {
              "classification": "unique",
              "blind_id": "blind-04",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "prepared publicity material",
                "for the product launch"
              ],
              "example": "The press office prepared publicity material for the product launch.",
              "example_id": "ex-d9402edd47c2",
              "rationale": "\"prepared publicity material\" の目的語である publicity material は発売を知らせるために作成する資料で、活動・手段側の意味を表すため、最有力はsense:002（世間の関心を集める広報・宣伝の手段）。sense:001（受ける注目・報道露出）は資料として準備できる物ではないため、この名詞句の構文では成立しない。",
              "translation": "広報室は製品発売のための宣伝資料を用意した。"
            },
            {
              "classification": "unique",
              "blind_id": "blind-05",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "launched a publicity campaign",
                "for its new exhibition"
              ],
              "example": "The museum launched a publicity campaign for its new exhibition.",
              "example_id": "ex-24c2620e3b89",
              "rationale": "\"launched a publicity campaign\" の目的語 campaign は開始される活動であり、exhibition を知らせる手段としての publicity を指定するため、最有力はsense:002（宣伝・広報活動）。sense:001（受ける注目・報道露出）は開始できる campaign ではないため、この構文では競合しない。",
              "translation": "その博物館は新しい展覧会の広報キャンペーンを始めた。"
            },
            {
              "classification": "unique",
              "blind_id": "blind-06",
              "candidate_sense_ids": [
                "sense:002"
              ],
              "discriminating_terms": [
                "arranged advance publicity",
                "for the festival",
                "several months before it opened"
              ],
              "example": "The organizers arranged advance publicity for the festival several months before it opened.",
              "example_id": "ex-51c288100a2c",
              "rationale": "\"arranged advance publicity\" は主催者が publicity を手配する活動側の構文で、advance と開幕前の時点も計画的な告知を示すため、最有力はsense:002（祭りへの関心を集める事前の広報活動・手段）。sense:001（受ける注目・報道露出）は主催者が数か月前に手配する対象としては結果状態であり、この文の目的語位置では自然でない。",
              "translation": "主催者は祭りの開幕数か月前から事前広報を手配した。"
            },
            {
              "classification": "unique",
              "blind_id": "blind-07",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "negative publicity",
                "surrounding the safety complaint",
                "responded quickly to"
              ],
              "example": "The restaurant responded quickly to the negative publicity surrounding the safety complaint.",
              "example_id": "ex-89fae701bfc6",
              "rationale": "\"negative publicity\" は publicity を問題に関する報道・反響として位置付け、responded to はレストランがその結果状態に対処する構文を作るため、最有力はsense:001（苦情をめぐって世間・メディアから受ける否定的な注目や報道）。sense:002（注目を集める広報活動）はレストランが行う対外活動を指せるが、同じ文では publicity は苦情をめぐって既に生じた否定的な反響であり、行う活動としては成立しない。",
              "translation": "そのレストランは、安全性に関する苦情をめぐる否定的な報道にすぐ対応した。"
            },
            {
              "classification": "unique",
              "blind_id": "blind-08",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "gave the company bad publicity"
              ],
              "example": "The scandal gave the company bad publicity.",
              "example_id": "ex-b96ab1d45bb5",
              "rationale": "\"gave the company bad publicity\" は不祥事が会社にもたらした結果としての悪評・露出を表すため、最有力はsense:001（会社が受ける否定的な世間の注目・報道露出）。sense:002（広報活動・手段）は不祥事が会社に与える実施行為ではなく、同じ使役的な結果構文では成立しない。",
              "translation": "その不祥事は会社に否定的な世間の注目をもたらした。"
            },
            {
              "classification": "unique",
              "blind_id": "blind-09",
              "candidate_sense_ids": [
                "sense:001"
              ],
              "discriminating_terms": [
                "received widespread publicity",
                "in the national press"
              ],
              "example": "The discovery received widespread publicity in the national press.",
              "example_id": "ex-67f583463d68",
              "rationale": "\"received widespread publicity\" は発見を publicity の受け手にし、in the national press はその報道媒体を示すため、最有力はsense:001（発見がメディアを通じて受けた広い報道露出）。sense:002（宣伝・広報活動）は発見が受け取るものでも全国紙で発生する活動そのものでもなく、この受動的な構文では成立しない。",
              "translation": "その発見は全国紙で広く報道された。"
            }
          ],
          "aligned_at": "2026-09-02T19:51:00.890Z",
          "findings": [],
          "unrouted_observations": []
        },
        "aligned_at": "2026-09-02T20:09:45.077833+00:00",
        "findings": [],
        "unrouted_observations": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "qualification",
        "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a063ae-7397-7d11-bd3c-ef48120e90bf"
        },
        "findings": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "pass_id": "pronunciation",
        "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a063ae-78de-7f20-94cb-0ba3bc5cd081"
        },
        "findings": []
      },
      {
        "schema_version": "check_pass_response_v6",
        "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
        "pass_id": "evidence",
        "reviewer": {
          "mode": "handoff",
          "declared_model": "gpt-5",
          "ingested_by": "human",
          "agent_id": "01a063b6-5f04-7b60-9594-770de9de6088"
        },
        "findings": []
      }
    ],
    "checker_reviewers": {
      "translation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a063a8-9a9e-78f1-9fca-ce0fe46e50b0"
      },
      "sense-structure": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a063a8-a678-7083-b005-4bee3b3130ac"
      },
      "frame-relation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a063ad-98d2-7430-8a73-13aa483c109e"
      },
      "example-attribution": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a063a8-abbe-7e13-a49a-10d7581f5085"
      },
      "qualification": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a063ae-7397-7d11-bd3c-ef48120e90bf"
      },
      "pronunciation": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a063ae-78de-7f20-94cb-0ba3bc5cd081"
      },
      "evidence": {
        "mode": "handoff",
        "declared_model": "gpt-5",
        "ingested_by": "human",
        "agent_id": "01a063b6-5f04-7b60-9594-770de9de6088"
      }
    },
    "independent_candidates": [],
    "summary": "Independent checker passes completed by parallel handoff; frame-relation preserved its serial blind/adjudication dependency."
  },
  "cold_review": {
    "schema_version": "cold_review_v1",
    "stage": "cold_review",
    "run_id": "cold-publicity-20260902T194039Z-23d464b6",
    "context_id": "cold-publicity-context-20260902T194039Z-23d464b6",
    "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
    "prompt_sha256": "0ed4409a73095a9a2968bdcdb20bc397be345af84bff2c3558a48f08a5488aae",
    "input_artifacts": [
      "entry_body",
      "cold_review_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-02T20:21:41.124968+00:00",
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "01a063c3-6fed-7b53-8cc6-0d813213a0a0"
    },
    "summary": "問題候補なし",
    "findings": []
  },
  "final_blind": {
    "schema_version": "final_blind_v2",
    "stage": "final_blind",
    "run_id": "blind-publicity-20260902T194039Z-23d464b6",
    "context_id": "blind-publicity-context-20260902T194039Z-23d464b6",
    "input_body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
    "prompt_sha256": "1bb7b1a1c7f589a50a704d1ce6c1ecd0bfb1c9fb689fd481d21bf608438eb7b5",
    "input_artifacts": [
      "entry_body",
      "final_blind_prompt"
    ],
    "audit_visible": false,
    "recorded_at": "2026-09-02T20:36:17.618153+00:00",
    "reviewer": {
      "mode": "handoff",
      "declared_model": "gpt-5",
      "ingested_by": "human",
      "agent_id": "01a063c9-2a02-7ab0-95b8-54e79803c087"
    },
    "provisional_decision": "reject",
    "independent_candidates": [
      {
        "id": "cand-01",
        "surface_form": "publicity",
        "frame": "不可算名詞; S gain/receive publicity",
        "meaning": "主体が受ける公衆の注目・報道上の露出という結果",
        "disposition": "included",
        "rationale": "本文は「gain/receive publicity」を、publicity の結果として受ける注目・報道上の露出のフレームとして収録している。",
        "semantic_assertions": [
          {
            "id": "cand-01-a1",
            "statement": "このフレームの publicity は主体が受ける公衆の注目・報道上の露出を指す。",
            "polarity": "must_hold",
            "scope": "gain/receive publicity; result reading"
          },
          {
            "id": "cand-01-a2",
            "statement": "この結果読みは好意的な評価を必須条件にしてはならない。",
            "polarity": "must_not_hold",
            "scope": "gain/receive publicity; evaluation"
          }
        ]
      },
      {
        "id": "cand-02",
        "surface_form": "publicity",
        "frame": "不可算名詞; widespread/good/bad/negative/unwanted publicity",
        "meaning": "広がりや評価を伴う公衆の注目・報道上の露出",
        "disposition": "included",
        "rationale": "本文は「widespread/good/bad/negative/unwanted publicity」を、結果としての注目・報道の程度や評価を示す修飾フレームとして扱っている。",
        "semantic_assertions": [
          {
            "id": "cand-02-a1",
            "statement": "これらの修飾語は publicity の広がりまたは評価を変更する。",
            "polarity": "must_hold",
            "scope": "widespread/good/bad/negative/unwanted publicity"
          },
          {
            "id": "cand-02-a2",
            "statement": "good/bad/negative/unwanted publicity は publicity が必ず名声を意味することを含意してはならない。",
            "polarity": "must_not_hold",
            "scope": "evaluative publicity modifiers"
          }
        ]
      },
      {
        "id": "cand-03",
        "surface_form": "publicity",
        "frame": "不可算名詞; S shun publicity",
        "meaning": "主体が避ける対象となる公衆の注目・報道",
        "disposition": "included",
        "rationale": "本文は「shun publicity」を、主体が世間の注目や報道を意図的に避けるフレームとして収録している。",
        "semantic_assertions": [
          {
            "id": "cand-03-a1",
            "statement": "shun publicity では publicity は避けられる公衆の注目・報道を指す。",
            "polarity": "must_hold",
            "scope": "shun publicity"
          },
          {
            "id": "cand-03-a2",
            "statement": "このフレームは主体が宣伝活動を避けることだけを意味してはならない。",
            "polarity": "must_not_hold",
            "scope": "shun publicity; activity/result boundary"
          }
        ]
      },
      {
        "id": "cand-04",
        "surface_form": "publicity",
        "frame": "不可算名詞; publicity about/surrounding 〈topic〉",
        "meaning": "話題をめぐる公衆の注目・報道上の露出",
        "disposition": "included",
        "rationale": "本文は「publicity about 〈話題〉」と「the publicity surrounding the case」を、話題に関する注目・報道の結果読みとして説明している。",
        "semantic_assertions": [
          {
            "id": "cand-04-a1",
            "statement": "about/surrounding の補語は publicity が扱う話題を指定する。",
            "polarity": "must_hold",
            "scope": "publicity about/surrounding 〈topic〉"
          },
          {
            "id": "cand-04-a2",
            "statement": "このフレームの publicity は話題を宣伝する活動そのものに限定されてはならない。",
            "polarity": "must_not_hold",
            "scope": "publicity about/surrounding 〈topic〉; result/activity boundary"
          }
        ]
      },
      {
        "id": "cand-05",
        "surface_form": "publicity",
        "frame": "不可算名詞; publicity for 〈target〉（結果・受けた注目の読み）",
        "meaning": "対象が受ける公衆の注目・報道上の露出",
        "disposition": "included",
        "rationale": "本文は「publicity for 〈対象〉」に、対象が受けた注目を表す結果読みがあり得ると明示している。",
        "semantic_assertions": [
          {
            "id": "cand-05-a1",
            "statement": "この読みでは for の補語は注目・報道を受ける対象を指定する。",
            "polarity": "must_hold",
            "scope": "publicity for 〈target〉; result reading"
          },
          {
            "id": "cand-05-a2",
            "statement": "この読みの publicity は対象に注目を集める活動そのものを必須条件にしてはならない。",
            "polarity": "must_not_hold",
            "scope": "publicity for 〈target〉; result/activity boundary"
          }
        ]
      },
      {
        "id": "cand-06",
        "surface_form": "publicity",
        "frame": "不可算名詞; publicity for/about 〈target〉（活動・手段の読み）",
        "meaning": "対象に世間の関心を集める広報・宣伝活動",
        "disposition": "included",
        "rationale": "本文は「publicity for/about 〈映画・商品・行事〉＝～に関する広報・注目」を sense 2 の文法パターンに置き、対象への注目を集める活動の読みを収録している。",
        "semantic_assertions": [
          {
            "id": "cand-06-a1",
            "statement": "この読みでは publicity は対象への注目を集める活動または手段を指す。",
            "polarity": "must_hold",
            "scope": "publicity for/about 〈target〉; activity reading"
          },
          {
            "id": "cand-06-a2",
            "statement": "paid advertising を含み得るという注記は、すべての publicity が有料広告であることを意味してはならない。",
            "polarity": "must_not_hold",
            "scope": "publicity activity; advertising boundary"
          }
        ]
      },
      {
        "id": "cand-07",
        "surface_form": "publicity",
        "frame": "不可算名詞; advance publicity for 〈launch/event〉",
        "meaning": "発売・行事開始前に行う事前の宣伝・広報活動",
        "disposition": "included",
        "rationale": "本文は「advance publicity for 〈発売・行事〉」を、発売や行事の前に行う事前広報のフレームとして収録している。",
        "semantic_assertions": [
          {
            "id": "cand-07-a1",
            "statement": "advance publicity は対象の発売・開始より前に行われる。",
            "polarity": "must_hold",
            "scope": "advance publicity for 〈launch/event〉"
          },
          {
            "id": "cand-07-a2",
            "statement": "このフレームは事前の広報・宣伝活動を指し、対象そのものを指してはならない。",
            "polarity": "must_hold",
            "scope": "advance publicity for 〈launch/event〉"
          }
        ]
      },
      {
        "id": "cand-08",
        "surface_form": "publicity campaign",
        "frame": "可算名詞; a publicity campaign for 〈target〉",
        "meaning": "対象への注目を集める計画的な宣伝・広報活動",
        "disposition": "included",
        "rationale": "本文は「a publicity campaign」を、商品・作品・行事・主張への注目を集める計画的活動として収録している。",
        "semantic_assertions": [
          {
            "id": "cand-08-a1",
            "statement": "campaign が数えられる活動単位を表す。",
            "polarity": "must_hold",
            "scope": "a publicity campaign"
          },
          {
            "id": "cand-08-a2",
            "statement": "publicity campaign は対象への注目を集める目的を持つ。",
            "polarity": "must_hold",
            "scope": "a publicity campaign for 〈target〉"
          }
        ]
      },
      {
        "id": "cand-09",
        "surface_form": "publicity material",
        "frame": "不可算名詞; publicity material for 〈target〉",
        "meaning": "宣伝・広報に用いる資料",
        "disposition": "included",
        "rationale": "本文は「publicity material」を、メディアや一般の人に提供する宣伝・広報用資料として収録している。",
        "semantic_assertions": [
          {
            "id": "cand-09-a1",
            "statement": "material は宣伝・広報に用いる資料を指す。",
            "polarity": "must_hold",
            "scope": "publicity material"
          },
          {
            "id": "cand-09-a2",
            "statement": "publicity material は公衆の注目そのものを指してはならない。",
            "polarity": "must_not_hold",
            "scope": "publicity material; material/result boundary"
          }
        ]
      },
      {
        "id": "cand-10",
        "surface_form": "publicity stunt",
        "frame": "可算名詞; a publicity stunt",
        "meaning": "注目を集める意図で仕組まれた行為・仕掛け",
        "disposition": "included",
        "rationale": "本文は「a publicity stunt」を、メディアや世間の注目を集めるために意図して行う話題作りの行為として収録している。",
        "semantic_assertions": [
          {
            "id": "cand-10-a1",
            "statement": "stunt は注目を集めるために行われる具体的な行為を表す。",
            "polarity": "must_hold",
            "scope": "a publicity stunt"
          },
          {
            "id": "cand-10-a2",
            "statement": "publicity stunt は publicity という結果だけを表す名詞句として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "a publicity stunt; activity/result boundary"
          }
        ]
      },
      {
        "id": "cand-11",
        "surface_form": "publicity",
        "frame": "形式的・古風な不可算名詞; publicity as publicness",
        "meaning": "公開性・公然性",
        "disposition": "included",
        "rationale": "本文の publicity について、古風・形式的には「公開性、公然性」の意味で使われることもある」として、現代の注目・宣伝とは別の歴史的用法を注記している。",
        "semantic_assertions": [
          {
            "id": "cand-11-a1",
            "statement": "この用法の publicity は公開性・公然性を指す。",
            "polarity": "must_hold",
            "scope": "formal/archaic publicity"
          },
          {
            "id": "cand-11-a2",
            "statement": "この用法を現代のメディア露出または宣伝活動の通常用法として一般化してはならない。",
            "polarity": "must_not_hold",
            "scope": "formal/archaic publicity; register boundary"
          }
        ]
      },
      {
        "id": "cand-12",
        "surface_form": "publicist",
        "frame": "可算名詞; a publicist for 〈person/organization/work〉",
        "meaning": "人・組織・作品の publicity を獲得・管理・拡散する仕事をする人",
        "disposition": "included",
        "rationale": "本文は「publicist」を、映画・作家・芸能人・企業などの publicity を扱い広める広報担当者として語形成欄に収録している。",
        "semantic_assertions": [
          {
            "id": "cand-12-a1",
            "statement": "publicist は publicity を扱う人を指す。",
            "polarity": "must_hold",
            "scope": "a publicist for 〈person/organization/work〉"
          },
          {
            "id": "cand-12-a2",
            "statement": "publicist は publicity そのものを指す名詞として扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "publicist; person/thing boundary"
          }
        ]
      },
      {
        "id": "cand-13",
        "surface_form": "publicize",
        "frame": "他動詞; publicize 〈person/thing/event〉",
        "meaning": "人・物・出来事を公に知らせ、注目を集める",
        "disposition": "excluded",
        "rationale": "「publicize」は publicity と関連する主要な語族候補だが、本文の語形成欄には publicize の動詞フレームがなく、見出し語 publicity 自体の用法としては収録されていない。",
        "semantic_assertions": [
          {
            "id": "cand-13-a1",
            "statement": "publicize は対象を公に知らせる他動詞である。",
            "polarity": "must_hold",
            "scope": "publicize 〈person/thing/event〉"
          },
          {
            "id": "cand-13-a2",
            "statement": "publicize の動詞用法を publicity の名詞用法として分類してはならない。",
            "polarity": "must_not_hold",
            "scope": "publicize; part-of-speech boundary"
          }
        ]
      },
      {
        "id": "cand-14",
        "surface_form": "right of publicity",
        "frame": "法的定着句; the right of publicity",
        "meaning": "氏名・肖像などの商業利用を管理する法的権利",
        "disposition": "excluded",
        "rationale": "「right of publicity」は法的定着句としては候補になるが、本文はこの専門用法を扱わず、通常の publicity 単独の名詞フレームとしても提示していない。",
        "semantic_assertions": [
          {
            "id": "cand-14-a1",
            "statement": "the right of publicity は人格識別情報の商業利用に関する法的権利を指す。",
            "polarity": "must_hold",
            "scope": "the right of publicity; legal phrase"
          },
          {
            "id": "cand-14-a2",
            "statement": "通常の publicity 単独用法が法的権利そのものを指すと一般化してはならない。",
            "polarity": "must_not_hold",
            "scope": "publicity; legal specialization"
          }
        ]
      },
      {
        "id": "cand-15",
        "surface_form": "publicity",
        "frame": "可算名詞としての a publicity / publicities",
        "meaning": "現代一般用法で数えられる publicity の個体",
        "disposition": "excluded",
        "rationale": "本文は「a publicity や publicities は一般に避け」としており、現代の通常用法に可算名詞フレームを収録していない。",
        "semantic_assertions": [
          {
            "id": "cand-15-a1",
            "statement": "現代の一般用法では publicity は通常不可算である。",
            "polarity": "must_hold",
            "scope": "modern publicity countability"
          },
          {
            "id": "cand-15-a2",
            "statement": "a publicity や publicities を現代一般語の標準的な可算フレームとして扱ってはならない。",
            "polarity": "must_not_hold",
            "scope": "a publicity / publicities"
          }
        ]
      },
      {
        "id": "cand-16",
        "surface_form": "publicity",
        "frame": "動詞・形容詞への転換用法; *publicity 〈object〉 / *a publicity noun",
        "meaning": "見出し語 publicity 自体が動詞または通常の形容詞として機能する用法",
        "disposition": "excluded",
        "rationale": "本文全体は publicity を名詞として表示し、動詞・形容詞への転換用法を提示していない。publicity campaign のような前置修飾は名詞の attributive use であり、形容詞化の根拠にはならない。",
        "semantic_assertions": [
          {
            "id": "cand-16-a1",
            "statement": "見出し語 publicity は本文の通常用法では名詞である。",
            "polarity": "must_hold",
            "scope": "publicity part of speech"
          },
          {
            "id": "cand-16-a2",
            "statement": "publicity campaign の前置修飾を publicity の形容詞用法または動詞用法として分類してはならない。",
            "polarity": "must_not_hold",
            "scope": "publicity campaign; conversion boundary"
          }
        ]
      }
    ],
    "article_findings": [
      {
        "id": "finding-01",
        "taxonomy_id": "sense_boundary_overlap",
        "location": {
          "section": "意味・用法・関連表現 > 2 > 文法パターン",
          "line_start": 109,
          "line_end": 109,
          "exact_quote": "publicity for/about 〈映画・商品・行事〉＝～に関する広報・注目／advance publicity for 〈発売・行事〉＝発売・行事の事前広報／publicity campaign/material/stunt＝宣伝キャンペーン・資料・仕掛け"
        },
        "severity": "blocking",
        "rationale": "本文は「publicity for/about 〈映画・商品・行事〉＝～に関する広報・注目／advance publicity for 〈発売・行事〉＝発売・行事の事前広報／publicity campaign/material/stunt＝宣伝キャンペーン・資料・仕掛け」を宣伝・広報側の文法パターンとして掲げる一方、同じ publicity for/about の裸の名詞句について、対象が受ける注目・報道という結果読みと、対象に注目を集める活動読みの両方を認めている。for/about の表面形だけでは主体側の活動と対象側の結果を分離できず、sense 1 と sense 2 の境界が同一フレーム内で重なる。結果読みと活動読みを別フレームに分け、各前置詞と読みを明示的に割り当てる必要がある。"
      }
    ]
  },
  "blind_seal": {
    "schema_version": "blind_seal_v3",
    "stage": "blind_seal",
    "entry_path": "entries/p/publicity.md",
    "body_sha256": "3a0ce9461fe52d0833bcf5f4e1b64c6237a9fcb2a1e1db9f117b0cec096d0fd9",
    "final_blind_path": "audits/runs/p/publicity/20260902T194039Z-23d464b6/final_blind.json",
    "final_blind_sha256": "dee6fec32ef2fb27e76ea3f15a15e797c15febc9b57ce24dd22b278c310a68fa",
    "blind_output_sha256": "c465ff17fb0104bdeaec7369218699bd9ac436dec43582571b778eca4a6160cf",
    "sealed_at": "2026-09-03T05:39:35.785825+09:00"
  },
  "resolutions": {
    "schema_version": "resolutions_v1",
    "stage": "finding_resolution",
    "run_id": "20260902T194039Z-23d464b6",
    "resolutions": [
      {
        "id": "finding-01",
        "finding_id": "finding-01",
        "status": "resolved",
        "disposition": "adopted",
        "rationale": "採用する。元の文法パターンが publicity for/about を活動読みと結果読みの両方に束ねていたため、本文を改稿し、語義1では publicity about と publicity for の結果読み、語義2では publicity for の活動読みだけを明示した。語義2の語法注記でも結果読みを語義1へ戻し、同じ表面形の読み分けを明記した。",
        "required_changes": "publicity for/about の活動読みと結果読みを別フレームとして明示し、語義ブロック間の境界を重複させない。",
        "implemented_changes": "語義1の語法注記に結果読みを明記し、語義2の文法パターンを publicity for の活動読みへ限定し、語義2の語法注記と関連説明を同じ区別へ整合させた。",
        "resolved_body_sha256": "2a79e044fd00e512fbd56935b8ef7b0b6e53fb843aff9ea30d2e2716e3466a8d"
      }
    ]
  }
}
```
