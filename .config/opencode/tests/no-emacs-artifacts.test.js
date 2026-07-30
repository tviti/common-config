import assert from "node:assert/strict"
import test from "node:test"
import { isEmacsArtifact } from "../plugins/no-emacs-artifacts.js"

test("blocks Emacs backup files", () => {
  assert.equal(isEmacsArtifact("/work/config.js~"), true)
})

test("blocks numbered backups and undo-tree files", () => {
  assert.equal(isEmacsArtifact("/work/config.js.~1~"), true)
  assert.equal(isEmacsArtifact("/work/config.js.~undo-tree~"), true)
})

test("blocks Emacs auto-save and lock files", () => {
  assert.equal(isEmacsArtifact("/work/#config.js#"), true)
  assert.equal(isEmacsArtifact("/work/.#config.js"), true)
})

test("allows ordinary files", () => {
  assert.equal(isEmacsArtifact("/work/config.js"), false)
  assert.equal(isEmacsArtifact("/work/~notes/config.js"), false)
  assert.equal(isEmacsArtifact("/work/.config.js"), false)
  assert.equal(isEmacsArtifact("/work/config#js"), false)
})

test("handles malformed tool arguments safely", () => {
  assert.equal(isEmacsArtifact(undefined), false)
  assert.equal(isEmacsArtifact(null), false)
  assert.equal(isEmacsArtifact({}), false)
})

test("only blocks read tool calls", async () => {
  const plugin = await (await import("../plugins/no-emacs-artifacts.js")).default()
  const before = plugin["tool.execute.before"]

  await assert.doesNotReject(() =>
    before(
      { tool: "glob", sessionID: "session", callID: "call" },
      { args: { filePath: "/work/config.js~" } },
    ),
  )
})
