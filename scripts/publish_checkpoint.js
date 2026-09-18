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
const jsonPayload = result => {
  if (result?.isError) throw new Error(JSON.stringify(result));
  if (result?.structuredContent != null) {
    const value = result.structuredContent;
    if (typeof value.content === "string") {
      try { return JSON.parse(value.content); } catch (_) { /* use wrapper */ }
    }
    return value;
  }
  const text = result?.content?.find?.(item => item.type === "text")?.text;
  if (text) return JSON.parse(text);
  return result;
};
const objects = value => {
  const found = [];
  const visit = item => {
    if (!item || typeof item !== "object") return;
    found.push(item);
    for (const child of Array.isArray(item) ? item : Object.values(item)) visit(child);
  };
  visit(value);
  return found;
};
const inspect = await command("inspect");
const [owner, repoName] = repository.split("/");
const findBranchHead = async () => {
  const branchSearch = jsonPayload(await tools.mcp__codex_apps__github_search_branches({
    owner, repo_name: repoName, query: inspect.branch, page_size: 100,
  }));
  const exists = objects(branchSearch).some(item =>
    item.name === inspect.branch || item.branch === inspect.branch);
  if (!exists) return undefined;
  const ref = jsonPayload(await tools.mcp__codex_apps__github_fetch({
    url: "https://api.github.com/repos/" + repository + "/git/ref/heads/" + inspect.branch,
  }));
  const refRow = objects(ref).find(item =>
    /^[0-9a-f]{40}$/.test(item.object?.sha || ""));
  if (!refRow) throw new Error("Connector returned no verifiable branch head");
  return refRow.object.sha;
};
const branchHead = await findBranchHead();
let remoteBase = branchHead;
let remoteBaseTree;
if (!remoteBase) {
  const repo = jsonPayload(await tools.mcp__codex_apps__github_fetch({
    url: "https://api.github.com/repos/" + repository,
  }));
  const repoRow = objects(repo).find(item => typeof item.default_branch === "string");
  if (!repoRow) throw new Error("Connector returned no default branch");
  const base = jsonPayload(await tools.mcp__codex_apps__github_fetch({
    url: "https://api.github.com/repos/" + repository + "/branches/" + encodeURIComponent(repoRow.default_branch),
  }));
  const baseRow = objects(base).find(item =>
    /^[0-9a-f]{40}$/.test(item.commit?.sha || "") &&
    /^[0-9a-f]{40}$/.test(item.commit?.commit?.tree?.sha || item.commit?.tree?.sha || ""));
  if (!baseRow) throw new Error("Connector returned no verifiable default-branch base");
  remoteBase = baseRow.commit.sha;
  remoteBaseTree = baseRow.commit.commit?.tree?.sha || baseRow.commit.tree.sha;
}
let prepareArgs = "prepare --repository " + quote(repository);
if (branchHead) prepareArgs += " --remote-head " + quote(branchHead);
else prepareArgs += " --remote-base " + quote(remoteBase) + " --remote-base-tree " + quote(remoteBaseTree);
if (settings.validationMode) prepareArgs += " --validation-mode " + quote(settings.validationMode);
const prepared = await command(prepareArgs);
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
const verifiedHead = await findBranchHead();
if (verifiedHead !== parent) throw new Error("Remote branch verification failed after publication");
return await command("accept --sha " + quote(parent) + suffix);
