"""The section rename changes labels, not the four-line entry contract."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_entry import validate_text, validation_warnings
from import_to_notion import markdown_to_blocks

OLD = '【コロケーション】'
NEW = '【コロケーション・構文例】'

class CollocationLabelTests(unittest.TestCase):
    def test_current_entries_validate_equally_under_both_labels(self):
        for word in ('stretch', 'involve', 'disturb', 'considerable'):
            text = (ROOT / 'entries' / word[0] / f'{word}.md').read_text(encoding='utf-8')
            with self.subTest(word=word):
                self.assertEqual(validate_text(text), [])
                self.assertEqual(validate_text(text.replace(OLD, NEW)), [])
                self.assertEqual(validation_warnings(text), validation_warnings(text.replace(OLD, NEW)))

    def test_both_labels_export_identical_notion_blocks(self):
        text = f'{OLD}\n\n・test a pattern\n用途: 構文を試す。\n例: Test a pattern.\n訳: 構文を試す。\n'
        legacy = markdown_to_blocks(text)
        self.assertEqual(legacy, markdown_to_blocks(text.replace(OLD, NEW)))
        self.assertEqual(legacy[0]['heading_3']['rich_text'][0]['text']['content'], NEW[1:-1])
        self.assertEqual(len(legacy), 2)

    def test_new_label_does_not_bypass_fixed_layout_errors(self):
        malformed = f'{NEW}\n\n・test a pattern\n例: Test a pattern.\n訳: 構文を試す。\n'
        with self.assertRaisesRegex(ValueError, '4 fixed lines'):
            markdown_to_blocks(malformed)
        text = (ROOT / 'entries/c/considerable.md').read_text(encoding='utf-8')
        broken = text.replace(OLD, NEW).replace('用途:', 'BAD:', 1)
        self.assertTrue(validate_text(broken))
