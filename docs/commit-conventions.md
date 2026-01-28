# Commit Message Conventions

This project uses [Conventional Commits](https://www.conventionalcommits.org/) with [release-please](https://github.com/googleapis/release-please) for automated versioning and changelog generation.

## 🎯 What each `<type>` means

| Type       | Purpose                                 | Release impact                                   | Example                                       |
| ---------- | --------------------------------------- | ------------------------------------------------ | --------------------------------------------- |
| `feat`     | A new feature or enhancement            | Minor bump (1.2.0 → 1.3.0)                       | `feat(order): support scheduled pickups`      |
| `fix`      | A bug fix or regression fix             | Patch bump (1.2.3 → 1.2.4)                       | `fix(checkout): handle empty cart gracefully` |
| `perf`     | Performance improvement                 | Patch bump                                       | `perf(network): cache GET responses`          |
| `refactor` | Code restructuring (no behavior change) | No release (unless you include `!` for breaking) | `refactor(cart): extract item validator`      |
| `chore`    | Maintenance (CI, tooling, deps, docs)   | No release                                       | `chore(ci): bump flutter version in workflow` |
| `docs`     | Documentation updates                   | No release                                       | `docs(readme): add setup instructions`        |
| `test`     | Add or modify tests                     | No release                                       | `test(core): cover null edge case`            |
| `style`    | Code formatting or lint fixes           | No release                                       | `style: fix dartfmt line breaks`              |
| `build`    | Build system or dependency changes      | No release (unless major SDK bump)               | `build: update build_runner`                  |
| `ci`       | Continuous integration changes          | No release                                       | `ci: split lint and test jobs`                |

## 💥 Breaking changes

If your commit introduces a breaking change, add `!` after the type or include a footer.

### Option 1 – with "bang"

```
feat!(api): drop legacy authentication
```

### Option 2 – with footer

```
refactor(api): remove deprecated endpoints

BREAKING CHANGE: endpoints /v1/login and /v1/logout removed
```

🔹 **Release-please will detect this and bump the major version (1.4.2 → 2.0.0).**

## 🧩 Optional scopes

Use parentheses to narrow down where the change applies.

Think in domain or layer terms.

### Examples:

- `feat(ui): add order history screen`
- `fix(auth): retry refresh token if expired`
- `chore(ci): use release-please v4`
- `refactor(cart): simplify totals calculation`

## 🪄 Commit examples by context

### Product / feature

- `feat(order): allow scheduled orders`
- `fix(checkout): prevent payment duplication`
- `feat: add dark mode toggle`

### Tech / code health

- `refactor(cart): extract total calculator`
- `perf(api): cache menu items`
- `build: bump flutter 3.27.0`
- `chore(deps): update shared_preferences`

### CI / tooling

- `chore(ci): add commitlint workflow`
- `ci: run flutter test on pull requests`

## 🧾 Release behavior summary

| Commit type                             | Triggers new version? | Version bump                      |
| --------------------------------------- | --------------------- | --------------------------------- |
| `fix:`                                  | ✅                    | Patch                             |
| `feat:`                                 | ✅                    | Minor                             |
| `feat!:` or `BREAKING CHANGE:`          | ✅                    | Major                             |
| Others (`chore`, `docs`, `style`, etc.) | ❌                    | No bump (but appear in changelog) |

## 🧠 Tips for teams

- **PR title = commit title** → release-please will use that if you squash & merge.
  - (Make sure "Squash and merge" uses a proper message like `feat(api): add refund endpoint`.)
- If you use multiple commits, release-please reads them all since last tag.
- You can add additional context lines under the first line (like a normal commit message).
- Avoid generic "update stuff" or "fix bug" messages — they won't be useful in changelogs.

## 🧩 Optional extras (if you want to enforce)

Configure commitlint with allowed types:

```
types-enum: ['feat', 'fix', 'perf', 'refactor', 'chore', 'docs', 'style', 'test', 'build', 'ci']
```

Add scopes if you want (commitlint can validate allowed scopes too).

## 🚀 Example flow in action

You merge a PR titled:

```
feat(auth): support magic link login
```

release-please opens/updates a Release PR proposing:

```markdown
## [1.2.0] - 2025-11-11

### Features

- **auth:** support magic link login
```

Merge that → tag `v1.2.0` → Renovate bumps your apps' ref: `v1.2.0`.
