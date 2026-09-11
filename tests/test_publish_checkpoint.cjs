const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const run = new AsyncFunction('tools', 'root', 'repository', 'options', fs.readFileSync(path.join(__dirname, '../scripts/publish_checkpoint.js'), 'utf8'));
const sha = n => String(n).repeat(40);

function fixture(corrupt = false, branchExists = true) {
  const content = Buffer.alloc(70000, 173).toString('base64');
  const plan = JSON.stringify({repository: 'owner/repo', branch: 'entry/test', branch_exists: branchExists, remote_base: sha(1), commits: [{local_sha: sha(6), message: 'x'.repeat(25000), tree_sha: sha(2), base_tree_sha: sha(3), entries: [{path: 'binary.xlsx', mode: '100644', type: 'blob', sha: sha(4)}]}]});
  const calls = [];
  const state = {blobs: [], trees: [], commits: {}};
  let publishedHead;
  const result = value => ({exit_code: 0, output: JSON.stringify(value)});
  const tools = {
    async exec_command({cmd}) {
      if (cmd.includes(' prepare ')) return result({plan_id: 'a'.repeat(64), branch_exists: branchExists, published_head: publishedHead});
      if (cmd.includes(' state ')) return result(state);
      if (cmd.includes(' progress ')) {
        const kind = cmd.match(/--kind (\w+)/)[1];
        const value = cmd.match(/--sha ([a-f0-9]+)/)[1];
        if (kind === 'blob') state.blobs.push(value);
        if (kind === 'tree') state.trees.push(value);
        if (kind === 'commit') state.commits[sha(6)] = value;
        return result({progress: kind});
      }
      const offset = Number((cmd.match(/--offset (\d+)/) || [0, 0])[1]);
      const text = cmd.includes(' blob ') ? content : plan;
      if (cmd.includes(' accept ')) return {exit_code: 0, output: JSON.stringify({verified: true})};
      return {exit_code: 0, output: JSON.stringify({total: text.length, chunk: text.slice(offset, offset + 12000)})};
    },
    async mcp__codex_apps__github_create_blob(args) {
      assert.equal(args.content, content);
      assert.equal(args.encoding, 'base64');
      calls.push('blob');
      return {structuredContent: {sha: corrupt ? sha(9) : sha(4)}};
    },
    async mcp__codex_apps__github_create_tree() { calls.push('tree'); return {structuredContent: {sha: sha(2)}}; },
    async mcp__codex_apps__github_create_commit(args) {
      assert.equal(args.parent_sha, sha(1));
      calls.push('commit'); return {structuredContent: {sha: sha(5)}};
    },
    async mcp__codex_apps__github_update_ref(args) {
      assert.equal(args.force, false);
      calls.push('ref'); publishedHead = args.sha; return {};
    },
    async mcp__codex_apps__github_create_branch(args) {
      assert.equal(args.sha, sha(5)); calls.push('create'); return {};
    },
  };
  return {tools, calls, state};
}

test('large plans and binary blobs transfer without model-visible content', async () => {
  const {tools, calls} = fixture();
  assert.deepEqual(await run(tools, '/repo', 'owner/repo'), {verified: true});
  assert.deepEqual(calls, ['blob', 'tree', 'commit', 'ref']);
});

test('hash mismatch never updates branch', async () => {
  const {tools, calls} = fixture(true);
  await assert.rejects(run(tools, '/repo', 'owner/repo'), /blob hash mismatch/);
  assert.deepEqual(calls, ['blob']);
});

test('new branches are created directly without a failed ref update', async () => {
  const {tools, calls} = fixture(false, false);
  await run(tools, '/repo', 'owner/repo');
  assert.deepEqual(calls, ['blob', 'tree', 'commit', 'create']);
});

test('retry reuses verified blobs and trees after a commit failure', async () => {
  const {tools, calls} = fixture();
  const original = tools.mcp__codex_apps__github_create_commit;
  tools.mcp__codex_apps__github_create_commit = async () => { throw new Error('transport failed'); };
  await assert.rejects(run(tools, '/repo', 'owner/repo'), /transport failed/);
  tools.mcp__codex_apps__github_create_commit = original;
  await run(tools, '/repo', 'owner/repo');
  assert.equal(calls.filter(x => x === 'blob').length, 1);
  assert.equal(calls.filter(x => x === 'tree').length, 1);
});

test('approval rejection stops without ref writes or automatic retry', async () => {
  const {tools, calls} = fixture();
  tools.mcp__codex_apps__github_create_blob = async () => ({isError: true, content: 'approval denied'});
  await assert.rejects(run(tools, '/repo', 'owner/repo'), /approval denied/);
  assert.deepEqual(calls, []);
});

test('progress contains paths and counts, not article bytes', async () => {
  const {tools} = fixture();
  const updates = [];
  await run(tools, "C:/Work/Owner's repo", 'owner/repo',
            {python: "C:/Tools/Python/python.exe", notify: x => updates.push(x)});
  assert.ok(updates.some(x => x.stage === 'blob-uploaded'));
  assert.ok(updates.every(x => !('content' in x)));
});
