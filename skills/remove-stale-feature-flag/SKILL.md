---
name: remove-stale-feature-flag
description: Removes a launched or stale LaunchDarkly feature flag from Dart flag definitions, published flag lists, and call sites while preserving the winning product behavior. Use when retiring a flag after rollout, cleaning up dead flag code, or when the user asks to remove a stale flag from the codebase and LaunchDarkly.
---

# Remove Stale Feature Flag

Retire a feature flag end-to-end: **Dart** (`JumpFeatureFlag` definitions, `publishedFlags` entries, and all usages) and **LaunchDarkly** (archive or delete when agreed).

## Use with LaunchDarkly Flag Cleanup

This repo skill stays focused on **Jump** conventions (Dart files, `publishedFlags`, package imports). The **`launchdarkly-flag-cleanup`** skill (LaunchDarkly plugin) is the canonical workflow for **LaunchDarkly**: `check-removal-readiness`, using **`get-flag`** to pick the **forward value** from real env config (never guess), optional **`archive-flag`** / **`delete-flag`**, and verification.

**How to combine them**

1. Follow **`launchdarkly-flag-cleanup`** for Steps 1–3 (explore references, removal readiness, forward value from LD) and Step 7 (verify). Treat `JumpFeatureFlag` / `featureManager.getValue` / `PosFeatureFlags.*` as the “wrapper/SDK” patterns when searching.
2. Apply the **Dart-specific steps below** when editing `*_features.dart` and collapsing branches, instead of the plugin’s TypeScript-oriented examples.
3. If the LaunchDarkly MCP in this workspace does not expose **`archive-flag`** / **`delete-flag`**, fall back to the manual UI step in **§3. LaunchDarkly** below.

## Non-negotiable: confirm once before removing

**Do not delete or edit anything until the user gives one explicit confirmation.**

1. Gather the **flag key**, **forward behavior** (what stays in code when the flag is gone), and a **short plan**: which files change, whether LaunchDarkly will be archived, deleted, or left for manual cleanup.
2. Present that plan and ask for **a single yes/no (or scoped) confirmation**, e.g. “Confirm: remove flag `X` from code and archive it in LaunchDarkly?”
3. **Only after an affirmative answer**, apply code edits and LaunchDarkly actions.

If the user only wants code removed but not LaunchDarkly, or the opposite, honor that in the confirmation step.

## Prerequisites

- **LaunchDarkly Feature Management** MCP (`plugin-launchdarkly-LaunchDarkly Feature Management`). Run **`mcp_auth`** with `{}` if tools fail for auth.
- Resolve **`projectKey`** from `.cursor/.env/.env` or `.cursor/.env` (`LAUNCHDARKLY_PROJECT_KEY`), or ask the user.

## Workflow

### 1. Understand usage and forward value

- Search the repo for the **flag key string** and for the **Dart symbol** (e.g. `PosFeatureFlags.enableFoo`).
- Identify branches: what runs when the flag is true vs false. **Keep the behavior that matches production intent** (often the “on” path after full rollout); remove the flag and collapse branches.
- Optionally call **`check-removal-readiness`** (`projectKey`, `flagKey`, `env` for a representative environment) and **`get-flag`** to align with LaunchDarkly state. If the verdict is `blocked`, stop and surface blockers; if `caution`, show warnings in the confirmation summary.

### 2. Dart edits (this project)

- Open the feature file (e.g. `lib/pos_features.dart` or `*_features.dart`): remove the **`static const JumpFeatureFlag ...`** for this flag.
- Remove its entry from **`publishedFlags`** (and any similar aggregate lists).
- Remove all **usages** (conditionals, parameters, tests). Follow **package imports** for cross-feature access per project rules.
- Run analyzer/tests as appropriate for the change size.

### 3. LaunchDarkly (after confirmation only)

- Prefer **archive** over **delete** unless the user explicitly wants permanent deletion.
- Use the MCP tools exposed by the server for that project (e.g. archive/delete if available). If no such tool is available, **tell the user** to archive or delete the flag in the LaunchDarkly UI and list the **exact flag key** and project.

### 4. Optional discovery

- **`find-stale-flags`** (`projectKey`, `env`) can suggest cleanup candidates when the user has not named a flag yet.

## Completion criteria

- User was asked once and confirmed before destructive removal.
- Flag definition and `publishedFlags` entry removed; call sites collapsed to the chosen forward behavior.
- LaunchDarkly updated as confirmed, or user instructed with key/project for manual step.
