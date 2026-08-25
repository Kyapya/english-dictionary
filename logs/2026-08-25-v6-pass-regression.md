# v6 checker-pass regression trial (2026-08-25)

- 対象: assess, obvious
- ケース定義: `tests/fixtures/check_pass_v6_regressions.json`
- 方法: v5監査で確認済みの欠陥種について、現在の修正版本文に残る対応位置が、担当v6パスのsection限定入力に含まれ、finding schemaを通過することを再生検証した。
- 注意: 文字列一致で辞書学的判断を代替するものではなく、既知の検査観点が分割時に脱落していないことを確認する構造回帰である。

| case | word | taxonomy | owner pass | visible section | line | result |
|---|---|---|---|---|---:|---|
| obvious-regional-qualification | obvious | `regional_qualification` | `qualification` | `usage_notes` | 382 | PASS |
| obvious-sense-boundary | obvious | `sense_boundary_overlap` | `sense-structure` | `usage_notes` | 103 | PASS |
| obvious-technical-term | obvious | `technical_terminology_conventionality` | `qualification` | `usage_notes` | 382 | PASS |
| assess-absolute-scope | assess | `absolute_scope_counterexample` | `qualification` | `sense_structure` | 44 | PASS |
| assess-sense-boundary | assess | `sense_boundary_overlap` | `sense-structure` | `word_formation` | 26 | PASS |
| assess-technical-term | assess | `technical_terminology_conventionality` | `qualification` | `word_formation` | 31 | PASS |
| assess-example-translation | assess | `example_translation_alignment` | `translation` | `collocations_examples` | 271 | PASS |
| assess-lexical-relation | assess | `lexical_relation_mislabel` | `frame-relation` | `lexical_relations` | 116 | PASS |
| assess-compound-generalization | assess | `compound_component_generalization` | `sense-structure` | `word_formation` | 26 | PASS |
| assess-pronunciation | assess | `pronunciation_symbol_explanation` | `pronunciation` | `pronunciation` | 15 | PASS |
| assess-argument-role | assess | `argument_slot_role_mismatch` | `frame-relation` | `frames` | 50 | PASS |
| assess-cross-section | assess | `cross_section_internal_contradiction` | `sense-structure` | `usage_notes` | 273 | PASS |

結果: 12/12 PASS。既知欠陥種の担当パス不明・入力範囲外・schema不適合は0件。
