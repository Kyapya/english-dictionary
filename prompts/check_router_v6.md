# check_router_v6

このファイルは、通常チェックを内容欠陥タクソノミー別の独立パスへ配送する小型ルーターである。本文の書式・front matter・固定行数・表記形式は先に `scripts/validate_entry.py` が検査し、各パスへは下記のentry sectionだけを渡す。プロセス欠陥 `finding_scope_transfer_loss` と `raw_adjudication_manifest_divergence` はパスへ配送せず、オーケストレータと原出力からの機械生成で防止する。

## パス対応表

| pass | 担当分類 | entry section selector |
|---|---|---|
| translation | example_translation_alignment, semantic_direction_reversal | definitions, collocations_examples, lexical_relations |
| sense-structure | sense_boundary_overlap, cross_section_internal_contradiction, compound_component_generalization | core_image, sense_structure, usage_notes, word_formation |
| frame-relation | argument_slot_role_mismatch, lexical_relation_mislabel | sense_structure, frames, collocations_examples, lexical_relations |
| qualification | regional_qualification, absolute_scope_counterexample, technical_terminology_conventionality | etymology, word_formation, sense_structure, frequency_register, usage_notes, collocations_examples |
| pronunciation | pronunciation_symbol_explanation | pronunciation |
| evidence | evidence_claim_mismatch | pronunciation, etymology, word_formation, core_image, sense_structure, frequency_register, frames, collocations_examples, usage_notes, lexical_relations |

## 機械可読ルーター

<!-- CHECK_ROUTER_V6_JSON_BEGIN -->
```json
{
  "schema_version": "check_router_v6",
  "excluded_process_categories": [
    "finding_scope_transfer_loss",
    "raw_adjudication_manifest_divergence"
  ],
  "finding_schema": {
    "required": ["taxonomy_id", "location", "severity", "rationale"],
    "severity": ["blocking", "minor"],
    "location_required": ["section", "line_start", "line_end", "exact_quote"]
  },
  "passes": [
    {
      "id": "translation",
      "specification": "prompts/check_pass_translation_v6.md",
      "taxonomy_ids": ["example_translation_alignment", "semantic_direction_reversal"],
      "sections": ["definitions", "collocations_examples", "lexical_relations"]
    },
    {
      "id": "sense-structure",
      "specification": "prompts/check_pass_sense_structure_v6.md",
      "taxonomy_ids": ["sense_boundary_overlap", "cross_section_internal_contradiction", "compound_component_generalization"],
      "sections": ["core_image", "sense_structure", "usage_notes", "word_formation"]
    },
    {
      "id": "frame-relation",
      "specification": "prompts/check_pass_frame_relation_v6.md",
      "taxonomy_ids": ["argument_slot_role_mismatch", "lexical_relation_mislabel"],
      "sections": ["sense_structure", "frames", "collocations_examples", "lexical_relations"]
    },
    {
      "id": "qualification",
      "specification": "prompts/check_pass_qualification_v6.md",
      "taxonomy_ids": ["regional_qualification", "absolute_scope_counterexample", "technical_terminology_conventionality"],
      "sections": ["etymology", "word_formation", "sense_structure", "frequency_register", "usage_notes", "collocations_examples"]
    },
    {
      "id": "pronunciation",
      "specification": "prompts/check_pass_pronunciation_v6.md",
      "taxonomy_ids": ["pronunciation_symbol_explanation"],
      "sections": ["pronunciation"]
    },
    {
      "id": "evidence",
      "specification": "prompts/check_pass_evidence_v6.md",
      "taxonomy_ids": ["evidence_claim_mismatch"],
      "sections": ["pronunciation", "etymology", "word_formation", "core_image", "sense_structure", "frequency_register", "frames", "collocations_examples", "usage_notes", "lexical_relations"]
    }
  ]
}
```
<!-- CHECK_ROUTER_V6_JSON_END -->

各パスは自分の `taxonomy_ids` 以外のfindingを出さない。別分類の疑いは `unrouted_observation` として調整役へ返し、調整役が唯一の担当パスへ配送する。全パスの出力は `scripts/check_passes.py` がschemaと分類の一意性を検証する。
