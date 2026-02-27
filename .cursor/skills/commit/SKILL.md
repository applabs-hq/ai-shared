---
name: commit
description: Create git commits for session changes. Use when the user asks to commit, when changes are ready to commit, or when finishing a task that should be committed. Commits are created by the agent without asking for approval.
---

# Commit Changes

Use this skill to create git commits for changes made in the session. Execute commits directly; do not ask the user to confirm before running `git add` and `git commit`.

---

## Rules (mandatory)

- **No attribution in commits.** The commit must be authored solely by the user. You must NOT add:
  - `Co-Authored-By` (or any co-author line)
  - "Made with Cursor" or "Generated with Cursor" or similar
  - Any footer or trailer that credits the AI or Cursor
- **Use only the `-m` flag for the message.** Run `git commit -m "message"` or `git commit -m "subject" -m "body"`. Do NOT use `-F` (file), do NOT write the message to a file then commit (a template could append attribution). The message must be passed literally on the command line.
- **Commit message = only your intended text.** The final commit must contain nothing but the conventional commit subject and optional body. No extra lines after the body.
- **Use imperative mood and conventional commits.** Follow the project's [commit conventions](../../docs/commit-conventions.md): `type(scope): description` (e.g. `feat(menu): add product quick controls`).
- **Add specific files only.** Use `git add <path>` for each file (or grouped paths). Never use `git add -A` or `git add .`.

---

## Process

1. **Assess changes**
   - Run `git status` and `git diff` to see what changed.
   - From conversation context, group changes into one or more logical commits.

2. **Plan commits**
   - Decide which files belong in each commit.
   - Draft the exact commit message(s) (conventional format, imperative, focus on why).

3. **Execute**
   - Run `git add` with the chosen paths for the first commit.
   - Run `git commit -m "subject"` or `git commit -m "subject" -m "body"` with only the intended message—no co-author or Cursor lines.
   - Repeat for further commits if needed.
   - Show the result with `git log --oneline -n <number>`.

4. **Verify (optional)**
   - If unsure, run `git log -1 --format=%B` and confirm the raw message has no "Co-Authored-By", "Cursor", or "Generated" lines.

---

## Summary

- One or more atomic commits; message only via `-m`; no co-author or Cursor attribution; no human sign-off step—commit as soon as the plan is clear.
