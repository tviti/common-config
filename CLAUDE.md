# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal dotfiles managed with GNU Stow. The repo root itself is the Stow package — top-level dirs (`.agents/`, `.claude/`, `.config/`, `.local/`) mirror `$HOME` and get symlinked there. There is no build/test/lint tooling; changes here are file edits (shell config, aliases, skills) plus a restow.

## Applying changes

Never invoke `stow` directly. Always run:

```
.local/bin/restow-configs
```

It restows this repo (`~/common-config`) and, if present, a sibling `~/machine-config` package. Raw `stow -R .` from certain working directories prints spurious "skipping target which was current stow directory" warnings — use the script instead. `~/machine-config` may not exist on a given machine; the script requires it to exist (`set -euo pipefail`) or it fails, so don't assume it's there.

## Skill placement convention

- Default: canonical skill lives at `.agents/skills/<name>/SKILL.md`, with `.claude/skills/<name>` as a relative symlink to it (`../../.agents/skills/<name>`). This keeps the skill usable by harnesses other than Claude Code (e.g. opencode), as long as the frontmatter stays to the common subset (`name`, `description` — no Claude-Code-only fields).
- Exception: if a skill depends on Claude-Code-specific features — `$ARGUMENTS` templating, `disable-model-invocation`, `argument-hint` — put it directly under `.claude/skills/<name>/SKILL.md` with no `.agents` counterpart or symlink. Example: `handoff`.

## Gotchas

- `git mv` fails on untracked files ("not under version control"). Use plain `mv` then `git add` instead.
- The sandbox can silently reset `cd` back to the project directory when you try to `cd` elsewhere (e.g. `/tmp`). Check `pwd` after any `cd` before trusting subsequent relative-path commands.
- Stray Emacs undo-tree files (`*.~undo-tree~`) are expected and already covered by `.gitignore` — don't try to clean them up.
