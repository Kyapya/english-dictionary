// Run in Work code mode as an async function with (tools, root, repository).
// File bytes stay inside tool orchestration; only the verified receipt is returned.
const quote = value => "'" + value.replaceAll("'", "'\\''") + "'";
const command = async args => {
  const result = await tools.exec_command({cmd: "python scripts/publish_checkpoint.py " + args, workdir: root, max_output_tokens: 10000});
  if (result.exit_code !== 0) throw new Error(result.output);
  return JSON.parse(result.output);
};
const shaOf = result => {
  if (result.isError) throw new Error(JSON.stringify(result));
  const value = result.structuredContent;
  const sha = value?.sha || value?.result?.sha;
  if (!/^[0-9a-f]{40}$/.test(sha || "")) throw new Error("Connector returned no valid SHA");
  return sha;
};
let planText = "", planLength;
do {
  const part = await command("plan --offset " + planText.length);
  planLength = part.total;
  if (!part.chunk.length && planText.length < planLength) throw new Error("Incomplete publication plan");
  planText += part.chunk;
} while (planText.length < planLength);
const plan = JSON.parse(planText);
let parent = plan.remote_base;
const uploaded = new Set();
for (const commit of plan.commits) {
  for (const entry of commit.entries) {
    if (!entry.sha || uploaded.has(entry.sha)) continue;
    let content = "", total;
    do {
      const part = await command("blob --sha " + entry.sha + " --offset " + content.length);
      total = part.total;
      if (!part.chunk.length && content.length < total) throw new Error("Incomplete blob transfer");
      content += part.chunk;
    } while (content.length < total);
    if (content.length !== total) throw new Error("Blob transfer length mismatch");
    const sha = shaOf(await tools.mcp__codex_apps__github_create_blob({repository_full_name: repository, content, encoding: "base64"}));
    if (sha !== entry.sha) throw new Error("Uploaded blob hash mismatch");
    uploaded.add(sha);
  }
  const tree = shaOf(await tools.mcp__codex_apps__github_create_tree({repository_full_name: repository, base_tree_sha: commit.base_tree_sha, tree_elements: commit.entries}));
  if (tree !== commit.tree_sha) throw new Error("Uploaded tree mismatch");
  parent = shaOf(await tools.mcp__codex_apps__github_create_commit({repository_full_name: repository, parent_sha: parent, tree_sha: tree, message: commit.message}));
}
if (plan.commits.length) {
  const result = await tools.mcp__codex_apps__github_update_ref({repository_full_name: repository, branch_name: plan.branch, sha: parent, force: false});
  if (result.isError) throw new Error(JSON.stringify(result));
}
return await command("accept --sha " + quote(parent));
