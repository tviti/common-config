import path from "node:path"

/**
 * Return true for files that Emacs uses for backups, auto-save, or locking.
 */
export function isEmacsArtifact(filePath) {
  if (typeof filePath !== "string") return false

  const basename = path.basename(filePath)
  return basename.endsWith("~") || (basename.startsWith("#") && basename.endsWith("#")) || basename.startsWith(".#")
}

/** @type {import("@opencode-ai/plugin").Plugin} */
export default async function noEmacsArtifacts() {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool !== "read") return

      const filePath = output.args?.filePath
      if (!isEmacsArtifact(filePath)) return

      throw new Error(`Refusing to read Emacs backup or undo-tree file: ${filePath}`)
    },
  }
}
