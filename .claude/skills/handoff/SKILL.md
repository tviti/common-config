---
name: handoff
description: Write a handoff document that transfers what this session learned to a specific named recipient — another agent, a later session, or a person. Use whenever the user says handoff, hand off, write this up for, brief the next agent, or otherwise asks to package the current session's findings for someone who wasn't here. The recipient and their task are given as arguments.
argument-hint: "<who receives this, and what they'll do with it>"
disable-model-invocation: true
---

# Handoff

Package what this session learned into a document a specific recipient can act on without having been here.

The recipient and their task are in `$ARGUMENTS`.

If `$ARGUMENTS` is empty or names a recipient without a task ("for another agent"), ask one question before writing: who receives this, and what will they be doing with it. Don't guess — the audience determines what's signal. A repair agent needs the failure mechanism; a reviewer needs the decision rationale; a writer needs the shape of the argument. Guessing produces a document that serves none of them.

## Calibrate to the reader

Assume the recipient has everything you had at the start of this session — the same repo, files, docs, access — and none of what you learned during it. That single assumption sets the whole boundary:

- **Don't spend words on what they can read for themselves.** Directory layouts, function signatures, public API docs, the contents of files they'll open anyway.
- **Do spend words on what cost this session something to learn.** The behavior that contradicted the documentation. The three plausible causes eliminated. The constraint that only surfaced on the fourth attempt.

Length follows from that, not from a target. A session that established one fact produces a short document. Don't pad to look thorough.

## Do not prescribe method

Write what is known. Do not tell the recipient how to work.

No directives to explore first, plan before acting, spawn subagents, verify assumptions, or proceed in phases. No "you should begin by...". The recipient has their own instructions and their own judgment about method. Method boilerplate is the most common failure in these documents: it buries the findings under scaffolding and reads as condescension.

The exception is a genuine hazard discovered in this session — "the test suite mutates `fixtures/` and must be run against a copy" — which is a finding, not a directive.

## Structure

Use this template. Drop any section that would be empty rather than writing "N/A" or "none identified". Add a section if this session produced something that doesn't fit.

```markdown
# Handoff: <subject in a few words>

**For:** <recipient and their task, from the invocation>
**From:** <date> session in <repo/branch, or other working context>

## Bottom line
<2–5 sentences. The single most useful thing this session produced. If the
recipient reads nothing else, this is what they need.>

## Established
<What is known and how it's known. One claim per bullet, each with a pointer
to the evidence. Distinguish "observed" from "confirmed by the user".>

## Uncertain
<Claims not established, each with what it rests on and what would settle it.
Mark confidence plainly: likely, plausible, guess.>

## Ruled out
<Each candidate, why it was eliminated, and how firmly. This is often the most
valuable section and the one most often omitted — it's what stops the recipient
from re-running work this session already did.>

## Given
<Constraints, preferences, and decisions the user stated. Treat as settled;
flag any the findings now call into question rather than silently overriding.>

## Pointers
<Paths with line ranges, commands that reproduce, identifiers, URLs, PR/issue
numbers. Copy-pasteable.>

## Open for the recipient
<Questions this session couldn't answer that bear on their task.>
```

## Precision in the claims

Every factual claim carries its evidence. `src/auth/session.py:112-140`, the exact command with its flags, the URL. A claim the recipient can't trace is a claim they have to re-derive, which defeats the document.

Keep the epistemic register honest — the recipient will act on this, and false confidence is worse than an admitted gap:

| Instead of | Write |
| --- | --- |
| "The cache invalidation is broken." | "Observed: stale reads after `flush()` in `cache.py:88`, reproduced 5/5 with `pytest -k stale`. Mechanism not established." |
| "I looked into the connection pool and it seemed fine." | "Ruled out: pool exhaustion. Pool size peaked at 4/20 during the failure window (`logs/pool.log:2201`)." |
| "You may want to consider refactoring the handler." | "The handler at `api/routes.py:340` catches `Exception` and returns 200, which is why the failure was invisible in monitoring." |

## Finishing

Default output path is `~/.claude-handoffs/<repo-name>/YYYY-MM-DD-<short-slug>.md` — a dedicated user-level directory, outside both the working repo and Claude Code's own managed state under `~/.claude/`. `<repo-name>` is the current repository's directory name (basename of the git root), which keeps handoffs from different projects from blending together in one flat listing. A handoff is transient working material for a later session or agent, not checked-in documentation, so it does not belong in the repo. Create the directory (and the `<repo-name>` subdirectory) if needed. If the user named a path, use theirs.

Then print two things and stop:

1. The path.
2. A one-line seed prompt for starting the recipient, e.g. `Read handoffs/2026-08-03-cache-staleness.md. Design a repair for the stale-read bug it describes.`

Don't summarize the document back in chat — the user was here for all of it.
