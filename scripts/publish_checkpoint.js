// Run as an async function with (tools, root, repository, options = {}).
// options.python selects an existing interpreter; never extract credentials.
// notify emits progress without file contents. Errors stop here; no automatic
// approval retries, alternate transports, or force updates.
const settings = typeof options === "undefined" ? {} : options;
const windows = /^[A-Za-z]:[\\/]/.test(root);
const quote = value => windows
  ? "'" + value.replaceAll("'", "''") + "'"
  : "'" + value.replaceAll("'", "'\\''") + "'";
const interpreter = settings.python
  ? (windows ? "& " : "") + quote(settings.python)
  : "python";
const progress = settings.notify || (() => {});
const command = async args => {
  let result = await tools.exec_command({cmd: interpreter + " -X utf8 scripts/publish_checkpoint.py " + args, workdir: root, max_output_tokens: 10000});
  let output = result.output;
  while (result.session_id && result.exit_code == null) {
    result = await tools.write_stdin({session_id: result.session_id, chars: "", yield_time_ms: 1000, max_output_tokens: 10000});
    output += result.output;
  }
  if (result.exit_code !== 0) throw new Error(output || "Publication command failed");
  return JSON.parse(output);
};
const shaOf = result => {
  if (result.isError) throw new Error(JSON.stringify(result));
  const value = result.structuredContent;
  const sha = value?.sha || value?.result?.sha;
  if (!/^[0-9a-f]{40}$/.test(sha || "")) throw new Error("Connector returned no valid SHA");
  return sha;
};
const prepared = await command("prepare --repository " + quote(repository));
const planId = prepared.plan_id;
if (!/^[0-9a-f]{64}$/.test(planId || "")) throw new Error("Invalid publication plan ID");
const suffix = " --plan-id " + planId;
progress({stage: "prepared", resumed: prepared.resumed, planId});
let planText = "", planLength;
do {
  const part = await command("plan --offset " + planText.length + suffix);
  planLength = part.total;
  if (!part.chunk.length && planText.length < planLength) throw new Error("Incomplete publication plan");
  planText += part.chunk;
} while (planText.length < planLength);
const plan = JSON.parse(planText);
if (plan.repository !== repository) throw new Error("Publication destination mismatch");
const saved = await command("state" + suffix);
let parent = plan.remote_base;
const uploaded = new Set(saved.blobs);
const trees = new Set(saved.trees);
for (const commit of plan.commits) {
  if (saved.commits[commit.local_sha]) {
    parent = saved.commits[commit.local_sha];
    progress({stage: "commit-reused", sha: parent});
    continue;
  }
  for (const entry of commit.entries) {
    if (!entry.sha || uploaded.has(entry.sha)) continue;
    let content = "", total;
    do {
      const part = await command("blob --sha " + entry.sha + " --offset " + content.length + suffix);
      total = part.total;
      if (!part.chunk.length && content.length < total) throw new Error("Incomplete blob transfer");
      content += part.chunk;
    } while (content.length < total);
    if (content.length !== total) throw new Error("Blob transfer length mismatch");
    const sha = shaOf(await tools.mcp__codex_apps__github_create_blob({repository_full_name: repository, content, encoding: "base64"}));
    if (sha !== entry.sha) throw new Error("Uploaded blob hash mismatch");
    uploaded.add(sha);
    await command("progress --kind blob --sha " + sha + suffix);
    progress({stage: "blob-uploaded", path: entry.path, completedBlobs: uploaded.size});
  }
  let tree = commit.tree_sha;
  if (!trees.has(tree)) {
    tree = shaOf(await tools.mcp__codex_apps__github_create_tree({repository_full_name: repository, base_tree_sha: commit.base_tree_sha, tree_elements: commit.entries}));
    if (tree !== commit.tree_sha) throw new Error("Uploaded tree mismatch");
    await command("progress --kind tree --sha " + tree + suffix);
    trees.add(tree);
  }
  parent = shaOf(await tools.mcp__codex_apps__github_create_commit({repository_full_name: repository, parent_sha: parent, tree_sha: tree, message: commit.message}));
  await command("progress --kind commit --sha " + parent + " --local-sha " + commit.local_sha + suffix);
  progress({stage: "commit-created", sha: parent});
}
if (plan.commits.length && prepared.published_head !== parent) {
  const result = prepared.branch_exists
    ? await tools.mcp__codex_apps__github_update_ref({repository_full_name: repository, branch_name: plan.branch, sha: parent, force: false})
    : await tools.mcp__codex_apps__github_create_branch({repository_full_name: repository, branch_name: plan.branch, sha: parent});
  if (result.isError) throw new Error("Publication commit " + parent + ": " + JSON.stringify(result));
}
return await command("accept --sha " + quote(parent));
