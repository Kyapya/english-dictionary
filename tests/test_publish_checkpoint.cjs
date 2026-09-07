const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const run = new AsyncFunction('tools', 'root', 'repository', fs.readFileSync(path.join(__dirname, '../scripts/publish_checkpoint.js'), 'utf8'));
const sha = n => String(n).repeat(40);

function fixture(corrupt = false) {
  const content = Buffer.alloc(70000, 173).toString('base64');
  const plan = JSON.stringify({branch: 'entry/test', remote_base: sha(1), commits: [{message: 'x'.repeat(25000), tree_sha: sha(2), base_tree_sha: sha(3), entries: [{path: 'binary.xlsx', mode: '100644', type: 'blob', sha: sha(4)}]}]});
  const calls = [];
  const tools = {
    async exec_command({cmd}) {
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
      calls.push('ref'); return {};
    },
  };
  return {tools, calls};
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
