"""Batch intake tests use local bare Git remotes; no LLM/network credentials.

The small starter is a test double for orchestration boundaries, NOT a content
review. Existing run_word/guard suites remain responsible for quality gates.
"""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import run_words as batch

STARTER = '''import json, pathlib, sys
root = pathlib.Path(__file__).resolve().parents[1]
word = sys.argv[1]
branch = __import__('subprocess').check_output(['git', 'branch', '--show-current'], cwd=root, text=True).strip()
path = root / 'audits/workflow_runs' / word / 'test-run.json'
path.parent.mkdir(parents=True, exist_ok=True)
value = {'run_id': word + '-test', 'headword': word, 'branch': branch,
         'status': 'in_progress', 'stage': 'preflight', 'deadline_at': 'fixed-test-deadline',
         'review_ingest_failures': {'count': 2}}
path.write_text(json.dumps(value))
print(path.relative_to(root))
'''


def run(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


class IntakeParsingTests(unittest.TestCase):
    def test_one_word(self):
        self.assertEqual(batch.words_from(['apple']), [{'headword': 'apple', 'slug': 'apple'}])

    def test_many_delimiters_case_and_dedup(self):
        words = batch.words_from(['Apple, banana\napple；cherry、date'])
        self.assertEqual([w['slug'] for w in words], ['apple', 'banana', 'cherry', 'date'])

    def test_phrase_is_not_split_on_space(self):
        self.assertEqual(batch.words_from(['in spite of'])[0]['slug'], 'in-spite-of')

    def test_invalid_input_is_rejected(self):
        for value in ['', '日本語', '--help', '../apple', 'apple/banana', 'apple;$(echo x)']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                batch.words_from([value])

    def test_slug_collisions_are_not_silently_deduplicated(self):
        with self.assertRaises(ValueError):
            batch.words_from(['re-cover', 're cover'])

    def test_text_and_json_files(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'words.txt'
            p.write_text('\ufeffapple\nbanana\n', encoding='utf-8')
            self.assertEqual(len(batch.words_from([], p)), 2)
            p = Path(d) / 'words.json'
            p.write_text('["apple", "banana"]')
            self.assertEqual(len(batch.words_from([], p)), 2)
            p.write_text('{"word": "apple"}')
            with self.assertRaises(ValueError):
                batch.words_from([], p)


class BatchGitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'repo'
        self.remote = self.base / 'remote.git'
        self.root.mkdir()
        run(self.root, 'init', '-b', 'main')
        run(self.root, 'config', 'user.name', 'Batch test')
        run(self.root, 'config', 'user.email', 'batch-test@example.invalid')
        subprocess.run(['git', 'init', '--bare', str(self.remote)], check=True, capture_output=True)
        run(self.root, 'remote', 'add', 'origin', str(self.remote))
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/start_word.py').write_text(STARTER)
        batch.write_json(self.root / batch.CONFIG, {'schema_version': batch.VERSION, 'max_active_words': 2})
        (self.root / 'README.md').write_text('test fixture\n')
        run(self.root, 'add', '.')
        run(self.root, 'commit', '-m', 'fixture')
        run(self.root, 'push', '-u', 'origin', 'main')

    def request(self, *words, batch_id='test-batch'):
        return batch.enqueue(self.root, batch.words_from(list(words)), batch_id=batch_id)

    def get_job(self, slug, batch_id='test-batch'):
        return batch.job_in(batch.load_batch(self.root, batch_id), slug)

    def publish(self, job):
        # Local fixture transport only; production Work uses the connector.
        run(batch.workspace(self.root, job), 'push', '-u', 'origin', job['branch'])

    def prepared(self, *words):
        self.request(*words)
        batch.prepare(self.root, 'test-batch')
        return self.get_job(words[0])

    def started(self, word='apple'):
        job = self.prepared(word)
        self.publish(job)
        return batch.start(self.root, 'test-batch', word)

    def set_manifest_status(self, job, status):
        work = batch.workspace(self.root, job)
        path = work / job['run_path']
        value = batch.read_json(path)
        value.update(status=status, stage='completed' if status == 'completed' else 'preflight')
        if status == 'budget_exhausted':
            value['stop_reason'] = 'test budget exhausted'
        batch.write_json(path, value)
        return path

    def test_intake_never_starts_run_or_worktree(self):
        value = self.request('apple', 'banana')
        self.assertTrue(all(j['state'] == 'queued' for j in value['jobs']))
        self.assertNotIn('deadline_at', json.dumps(value))
        self.assertFalse((self.root / 'audits').exists())
        self.assertFalse((batch.common_dir(self.root) / 'dictionary-word-worktrees').exists())

    def test_word_base_excludes_unmerged_coordinator_commits(self):
        base = run(self.root, 'rev-parse', 'origin/main')
        (self.root / 'coordinator-only.txt').write_text('intake administration')
        run(self.root, 'add', '.')
        run(self.root, 'commit', '-m', 'coordinator-only metadata')
        value = self.request('apple')
        self.assertEqual(value['base_sha'], base)
        batch.prepare(self.root, 'test-batch')
        self.assertFalse((batch.workspace(self.root, self.get_job('apple')) / 'coordinator-only.txt').exists())

    def test_three_thousand_words_are_durable_and_no_runs_started(self):
        value = self.request(*(f'word{i}' for i in range(3000)))
        self.assertEqual(len(batch.load_batch(self.root, value['batch_id'])['jobs']), 3000)
        self.assertFalse((self.root / 'audits').exists())
        self.assertTrue(batch.validate(self.root)['valid'])

    def test_idempotent_request_id_and_reject_changed_request(self):
        first = self.request('apple')
        self.assertEqual(first, self.request('apple'))
        with self.assertRaises(ValueError):
            self.request('banana')
        self.assertEqual(self.get_job('apple')['job_id'], first['jobs'][0]['job_id'])

    def test_cross_batch_duplicate_links_to_same_job(self):
        self.request('apple')
        second = self.request('apple', 'banana', batch_id='second')
        self.assertEqual(second['jobs'][0]['state'], 'linked')
        self.assertEqual(second['jobs'][0]['job_id'], self.get_job('apple')['job_id'])
        self.assertTrue(batch.validate(self.root)['valid'])

    def test_bad_request_does_not_partially_save(self):
        self.request('re-cover')
        with self.assertRaises(ValueError):
            self.request('apple', 're cover', batch_id='second')
        self.assertFalse(batch.batch_path(self.root, 'second').exists())

    def test_checked_existing_entry_is_not_regenerated(self):
        p = self.root / batch.entry_path('apple')
        p.parent.mkdir(parents=True)
        p.write_text('---\nheadword: apple\nchecked: true\n---\nContent\n')
        run(self.root, 'add', '.')
        run(self.root, 'commit', '-m', 'existing checked entry')
        run(self.root, 'push', 'origin', 'main')
        value = self.request('apple')
        self.assertEqual(value['jobs'][0]['state'], 'existing')

    def test_preparation_is_bounded_and_worktrees_are_isolated(self):
        self.request('apple', 'banana', 'cherry')
        value = batch.prepare(self.root, 'test-batch')
        self.assertEqual([j['state'] for j in value['jobs']], ['prepared', 'prepared', 'queued'])
        a, b = value['jobs'][:2]
        self.assertNotEqual(batch.workspace(self.root, a), batch.workspace(self.root, b))
        for job in (a, b):
            work = batch.workspace(self.root, job)
            self.assertEqual(run(work, 'branch', '--show-current'), job['branch'])
            self.assertFalse((work / 'audits').exists())
            self.assertEqual(run(work, 'status', '--porcelain'), '')
        self.assertEqual(run(self.root, 'branch', '--show-current'), 'main')

    def test_capacity_is_shared_between_batches_and_intake_still_works(self):
        self.prepared('apple', 'banana')
        self.request('cherry', batch_id='second')
        value = batch.prepare(self.root, 'second')
        self.assertEqual(value['jobs'][0]['state'], 'queued')

    def test_single_slot_configuration_preserves_serial_operation(self):
        batch.write_json(self.root / batch.CONFIG, {'schema_version': batch.VERSION, 'max_active_words': 1})
        self.request('apple', 'banana')
        value = batch.prepare(self.root, 'test-batch')
        self.assertEqual([j['state'] for j in value['jobs']], ['prepared', 'queued'])

    def test_reservation_must_be_published_before_start(self):
        job = self.prepared('apple')
        result = batch.start(self.root, 'test-batch', 'apple')
        self.assertEqual(result['action'], 'reservation_publication_pending')
        self.assertIsNone(batch.own_run(self.root, job))

    def test_start_calls_existing_guarded_starter_and_second_start_does_not_reset(self):
        job = self.started()
        self.assertEqual(job['state'], 'in_progress')
        path = batch.workspace(self.root, job) / job['run_path']
        before = path.read_bytes()
        again = batch.start(self.root, 'test-batch', 'apple')
        self.assertEqual(again['run_path'], job['run_path'])
        self.assertEqual(before, path.read_bytes())

    def test_new_word_can_be_enqueued_during_guarded_start(self):
        job = self.prepared('apple')
        self.publish(job)
        original = batch.subprocess.run
        def intercept(argv, *args, **kwargs):
            if isinstance(argv, list) and len(argv) > 1 and str(argv[1]).endswith('start_word.py'):
                self.request('banana', batch_id='second')
            return original(argv, *args, **kwargs)
        with patch.object(batch.subprocess, 'run', side_effect=intercept):
            batch.start(self.root, 'test-batch', 'apple')
        self.assertEqual(self.get_job('banana', 'second')['state'], 'queued')

    def test_completed_and_blocked_jobs_do_not_block_other_words(self):
        job = self.started()
        self.set_manifest_status(job, 'budget_exhausted')
        value = batch.refresh(self.root, 'test-batch')
        self.assertEqual(value['jobs'][0]['state'], 'blocked')
        with self.assertRaises(ValueError):
            batch.start(self.root, 'test-batch', 'apple')
        self.request('banana', 'cherry', batch_id='second')
        value = batch.prepare(self.root, 'second')
        self.assertTrue(all(j['state'] == 'prepared' for j in value['jobs']))

    def test_status_and_refresh_do_not_touch_deadlines_or_failure_counters(self):
        job = self.started()
        path = batch.workspace(self.root, job) / job['run_path']
        before = path.read_bytes()
        batch.report(self.root, batch.load_batch(self.root, 'test-batch'))
        batch.refresh(self.root, 'test-batch')
        self.assertEqual(path.read_bytes(), before)

    def test_completion_is_not_mistaken_for_merge(self):
        job = self.started()
        self.set_manifest_status(job, 'completed')
        value = batch.refresh(self.root, 'test-batch', fetch=True)
        self.assertEqual(value['jobs'][0]['state'], 'review_complete')
        work = batch.workspace(self.root, job)
        run(work, 'add', '.')
        run(work, 'commit', '-m', 'complete synthetic run')
        run(work, 'push', 'origin', 'HEAD:main')
        value = batch.refresh(self.root, 'test-batch', fetch=True)
        self.assertEqual(value['jobs'][0]['state'], 'merged')

    def test_failed_starter_is_not_automatically_restarted(self):
        job = self.prepared('apple')
        self.publish(job)
        work = batch.workspace(self.root, job)
        (work / 'scripts/start_word.py').write_text('raise SystemExit(9)\n')
        value = batch.start(self.root, 'test-batch', 'apple')
        self.assertEqual(value['state'], 'inspection_required')
        with self.assertRaises(ValueError):
            batch.start(self.root, 'test-batch', 'apple')
        with self.assertRaises(ValueError):
            batch.recover(self.root, 'test-batch', 'apple')

    def test_original_guard_block_is_preserved_not_retried(self):
        job = self.prepared('apple')
        self.publish(job)
        work = batch.workspace(self.root, job)
        (work / 'scripts/start_word.py').write_text('print(\'{"status":"restart_confirmation_required","runs":[]}\')\nraise SystemExit(4)\n')
        value = batch.start(self.root, 'test-batch', 'apple')
        self.assertEqual(value['state'], 'blocked')
        with self.assertRaises(ValueError):
            batch.recover(self.root, 'test-batch', 'apple')

    def test_remote_scan_failure_allows_only_explicit_pre_start_recovery(self):
        job = self.prepared('apple')
        self.publish(job)
        work = batch.workspace(self.root, job)
        (work / 'scripts/start_word.py').write_text('print(\'{"status":"remote_run_scan_failed"}\')\nraise SystemExit(5)\n')
        batch.start(self.root, 'test-batch', 'apple')
        value = batch.recover(self.root, 'test-batch', 'apple')
        self.assertEqual(value['state'], 'prepared')
        self.assertNotIn('start_attempted_at', value)

    def test_remote_reservation_conflict_does_not_overwrite(self):
        job = self.prepared('apple')
        self.publish(job)
        # A second clone has a different request ID but the same deterministic branch.
        other = self.base / 'other'
        subprocess.run(['git', 'clone', '-b', 'main', str(self.remote), str(other)], check=True, capture_output=True)
        run(other, 'config', 'user.name', 'Other test')
        run(other, 'config', 'user.email', 'other@example.invalid')
        second = batch.enqueue(other, batch.words_from(['apple']), batch_id='other-request')
        value = batch.prepare(other, second['batch_id'])
        self.assertEqual(value['jobs'][0]['state'], 'external')
        self.assertFalse(batch.workspace(other, value['jobs'][0]).exists())

    def test_worker_checkout_cannot_dispatch_a_second_coordinator(self):
        job = self.prepared('apple')
        with self.assertRaises(ValueError):
            batch.enqueue(batch.workspace(self.root, job), batch.words_from(['banana']), batch_id='bad')

    def test_lost_worktree_restores_same_published_run(self):
        job = self.started()
        work = batch.workspace(self.root, job)
        run(work, 'add', '.')
        run(work, 'commit', '-m', 'checkpoint synthetic run')
        self.publish(job)
        run(self.root, 'worktree', 'unlock', str(work))
        run(self.root, 'worktree', 'remove', str(work))
        restored = batch.recover(self.root, 'test-batch', 'apple')
        self.assertEqual(restored['state'], 'in_progress')
        self.assertEqual(restored['run_path'], job['run_path'])

    def test_inflight_job_keeps_slot_when_starter_outcome_is_unknown(self):
        job = self.prepared('apple', 'banana')
        value = batch.load_batch(self.root, 'test-batch')
        value['jobs'][0].update(state='inspection_required', start_attempted_at='test')
        batch.write_json(batch.batch_path(self.root, 'test-batch'), value)
        self.request('cherry', batch_id='second')
        result = batch.prepare(self.root, 'second')
        self.assertEqual(result['jobs'][0]['state'], 'queued')

    def test_start_in_separate_words_uses_distinct_manifests(self):
        self.prepared('apple', 'banana')
        for word in ('apple', 'banana'):
            self.publish(self.get_job(word))
            batch.start(self.root, 'test-batch', word)
        a, b = self.get_job('apple'), self.get_job('banana')
        self.assertNotEqual(batch.workspace(self.root, a) / a['run_path'], batch.workspace(self.root, b) / b['run_path'])
        self.assertEqual(a['state'], 'in_progress')
        self.assertEqual(b['state'], 'in_progress')

    def test_lock_excludes_another_coordinator(self):
        with batch.lock(self.root):
            with self.assertRaises(ValueError):
                self.request('apple')

    def test_corrupted_state_fails_closed(self):
        self.request('apple')
        p = batch.batch_path(self.root, 'test-batch')
        p.write_text('{bad json')
        with self.assertRaises(ValueError):
            batch.prepare(self.root, 'test-batch')

    def test_run_path_escape_is_rejected(self):
        value = self.request('apple')
        value['jobs'][0]['run_path'] = '../../escape.json'
        batch.write_json(batch.batch_path(self.root, 'test-batch'), value)
        with self.assertRaises(ValueError):
            batch.load_batch(self.root, 'test-batch')

    def test_cli_single_word_and_multiword_same_interface(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(batch.main(['--root', str(self.root), 'enqueue', 'apple', '--batch-id', 'one']), 0)
            self.assertEqual(batch.main(['--root', str(self.root), 'enqueue', 'banana', 'cherry', '--batch-id', 'two']), 0)
        self.assertEqual(len(batch.load_batch(self.root, 'one')['jobs']), 1)
        self.assertEqual(len(batch.load_batch(self.root, 'two')['jobs']), 2)


if __name__ == '__main__':
    unittest.main()
