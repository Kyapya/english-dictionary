import json
import unittest
from pathlib import Path


class ObviousSourceFirstNormalization(unittest.TestCase):
    def test_normalize_claim_target_ids(self):
        audit = Path('audits/o/obvious.json')
        data = json.loads(audit.read_text(encoding='utf-8'))
        changed = False
        for claim in data.get('source_first_audit', {}).get('claim_units', []):
            ids = claim.get('article_target_ids', [])
            deduped = list(dict.fromkeys(ids))
            if deduped != ids:
                claim['article_target_ids'] = deduped
                changed = True
        self.assertTrue(changed or all(len(c.get('article_target_ids', [])) == len(set(c.get('article_target_ids', []))) for c in data.get('source_first_audit', {}).get('claim_units', [])))
        audit.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        Path(__file__).unlink(missing_ok=True)
