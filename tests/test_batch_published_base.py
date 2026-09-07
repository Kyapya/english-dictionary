"""Regressions for excluding unmerged control metadata from word branches."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import start_words as batch

STARTER = '''import json, pathlib, subprocess, sys
root = pathlib.Path.cwd()
word = sys.argv[1]
p = root / 'audits/workflow_runs' / word / 'fixture.json'
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps({'headword': word, 'branch': subprocess.check_output(
    ['git', 'branch', '--show-current'], text=True).strip(), 'status': 'in_progress',
    'stage': 'preflight', 'deadline_at': 'fixed-test-deadline'}))
'''


class PublishedBaseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / 'control'
        self.root.mkdir()
        batch.git(self.root, 'init', '-b', 'main')
        batch.git(self.root, 'config', 'user.name', 'Batch test')
        batch.git(self.root, 'config', 'user.email', 'test@example.invalid')
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/start_word.py').write_text(STARTER)
        (self.root / 'scripts/run_word.py').write_text('# fixture\n')
        batch.git(self.root, 'add', '.')
        batch.git(self.root, 'commit', '-m', 'published fixture')
        self.published = batch.git(self.root, 'rev-parse', 'HEAD')
        self.remote = self.base / 'remote.git'
        subprocess.run(['git', 'clone', '--bare', str(self.root), str(self.remote)],
                       check=True, capture_output=True)
        batch.git(self.root, 'remote', 'add', 'origin', str(self.remote))
        self.queue = batch.Queue(self.root)

    def test_unmerged_control_commits_are_not_word_bases(self):
        self.queue.enqueue(['alpha'])
        batch.git(self.root, 'add', 'queue')
        batch.git(self.root, 'commit', '-m', 'control-only queue checkpoint')
        control_head = batch.git(self.root, 'rev-parse', 'HEAD')
        self.assertNotEqual(self.published, control_head)
        self.queue.enqueue(['beta'])
        self.assertTrue(all(j['base_sha'] == self.published for j in self.queue.jobs()))
        self.queue.dispatch(max_active=2)
        for job in self.queue.jobs():
            work = self.queue.workspace(job)
            self.assertEqual('active', job['status'])
            self.assertFalse((work / 'queue/jobs').exists())
            self.assertFalse((work / 'queue/batches').exists())
            self.assertEqual(self.published, batch.git(work, 'merge-base', 'HEAD', control_head))

    def test_missing_remote_main_fails_without_partial_intake(self):
        batch.git(self.remote, 'update-ref', '-d', 'refs/heads/main')
        with self.assertRaises(subprocess.CalledProcessError):
            self.queue.enqueue(['alpha', 'beta'])
        self.assertFalse((self.root / 'queue/jobs').exists())
        self.assertFalse((self.root / 'queue/batches').exists())

    def advance_remote(self):
        other = self.base / 'other'
        subprocess.run(['git', 'clone', str(self.remote), str(other)], check=True, capture_output=True)
        batch.git(other, 'config', 'user.name', 'Other test')
        batch.git(other, 'config', 'user.email', 'other@example.invalid')
        (other / 'published-update.txt').write_text('new main revision')
        batch.git(other, 'add', '.')
        batch.git(other, 'commit', '-m', 'advance published main')
        batch.git(other, 'push', 'origin', 'main')
        return batch.git(other, 'rev-parse', 'HEAD')

    def test_new_main_must_be_fetched_before_new_job_is_saved(self):
        self.queue.enqueue(['alpha'])
        original = batch.read(self.queue.job_path('alpha'))
        new_main = self.advance_remote()
        with self.assertRaisesRegex(ValueError, 'fetch origin main'):
            self.queue.enqueue(['beta'])
        self.assertFalse(self.queue.job_path('beta').exists())
        batch.git(self.root, 'fetch', 'origin', 'main')
        self.queue.enqueue(['beta'])
        self.assertEqual(new_main, batch.read(self.queue.job_path('beta'))['base_sha'])
        self.assertEqual(original, batch.read(self.queue.job_path('alpha')))

    def test_remote_lookup_does_not_hold_queue_lock(self):
        real_git = batch.git
        def checked_git(root, *args):
            if args and args[0] == 'ls-remote':
                with self.queue.lock():
                    pass
            return real_git(root, *args)
        with patch.object(batch, 'git', side_effect=checked_git):
            self.queue.enqueue(['alpha'])
        self.assertEqual('queued', self.queue.jobs()[0]['status'])

    def test_remote_response_must_be_exact_main_reference(self):
        real_git = batch.git
        def malformed(root, *args):
            if args and args[0] == 'ls-remote':
                return self.published + '\trefs/heads/other'
            return real_git(root, *args)
        with patch.object(batch, 'git', side_effect=malformed), self.assertRaises(ValueError):
            self.queue.enqueue(['alpha'])
        self.assertFalse(self.queue.job_path('alpha').exists())

    def test_status_is_available_without_remote_access(self):
        self.queue.enqueue(['alpha'])
        batch.git(self.root, 'remote', 'remove', 'origin')
        self.assertEqual(1, self.queue.snapshot()['counts']['queued'])


if __name__ == '__main__':
    unittest.main()
