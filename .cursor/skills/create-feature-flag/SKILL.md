---
name: create-feature-flag
description: Creates a new feature flag defined in Flutter code and in LaunchDarkly via the LaunchDarkly Feature Management MCP tools
---

# Create Feature Flag

This is a skill for creating a new feature flag in code and in the LaunchDarkly service using the **LaunchDarkly Feature Management** MCP server (not shell scripts).

## Rules and Scope

- Your job is ONLY to define and create the feature flag (including LaunchDarkly **targeting** for boolean flags as specified below), not wire it into app logic.
- Do NOT update any other code or implement this feature flag in any control flow code paths.
- Do NOT read the app code to gather more context on where and what code the flag will be used, you are only creating the flag at the request of the user
- Make no assumptions about if this flag should be Client or Shared, always ASK before assuming

## When to Use

- Use this skill when undertaking a significantly-sized feature or large complex refactor
- This skill is helpful for creating feature flags to manage code visibility in production environments

## Prerequisites (MCP)

- **LaunchDarkly Feature Management** MCP server must be enabled in Cursor.
- If tools fail with an auth error, run **`mcp_auth`** with `{}` for server **`plugin-launchdarkly-LaunchDarkly Feature Management`** once, then retry.

## Instructions

- Ask the user whether this is a feature flag for the client application or for the wider platform.
- Ask the user for the purpose and scope of the feature flag so you can name it better

### Flag Naming Conventions

Flag names should read as an instructional sentence that begins with an action and concludes with a subject.

The action describes purpose and behavior of the flag. This should be a single verb and an optional category, followed by a colon. Some example actions are “Release:” and “Release Mobile:”.

The subject describes the target and scope of the flag. Some example subjects are “Widget” and “Homepage banner color.”

You should be able to read the name as a sentence that describes the purpose and scope of a flag. For example:

- MUST have a verb
- Verb MUST be followed by colon :

“Rollout: New feature”
“Configure: Setting A”
“Allow: Action”
“Enable: Entitlement”
“Show: Offer”

- Choose a suitable UpperCamelCase key name for the flag, it must be unique. The key should accurately reflect the display name
- ALWAYS Namespace flags with underscore prefixes. Client name for apps, i.e. `KIOSK_`, and `SHARED_` for global flags.
- i.e. `KIOSK_EnableNewCheckout`
- **Tag the flag with the project** in LaunchDarkly. Pass a `tags` array on create (e.g. `["Kiosk"]`, `["POS"]`, `["Shared"]`). Use tags that match the flag’s scope; you may include multiple tags if relevant.

### Possible Tag and Prefix Values

- `KIOSK`
- `POS`
- `ORDERING`
- `PORTAL`
- `API`
- `SHARED`

- Look for `features.dart` (global) or `[CLIENT]_features.dart` or `[CLIENT].features.dart`, i.e. `kiosk_features.dart`. Choose the scope the user chose earlier
- Create a new feature definition in code like the following, you may choose the emojis

```dart
static const JumpFeatureFlag enableNewCheckout = JumpFeatureFlag(
    flagKey: "KIOSK_EnableNewCheckout",
    displayName: "Enable new checkout 2.0 experience 🤑🤑",
    defaultValue: false,
);
```

```dart
static const List<JumpFeatureFlag> publishedFlags = [
    ...,
    enableNewCheckout,
];
```

### Project key

- Resolve **`projectKey`** before calling MCP tools: read `LAUNCHDARKLY_PROJECT_KEY` from the workspace **`.cursor/.env/.env`** or **`.cursor/.env`** if present. If unset, ask the user for the LaunchDarkly project key (often `default`).

### LaunchDarkly: list and create (MCP)

Use the **LaunchDarkly Feature Management** server: **`plugin-launchdarkly-LaunchDarkly Feature Management`**.

1. **Confirm the key is unused** — call **`list-flags`** with at least `projectKey`. Use `query` set to the planned flag key (or a distinctive substring) to narrow results. If a matching flag already exists, choose a different key.

2. **Create the flag** — call **`create-flag`** with:

   - **`projectKey`**: from the step above (required).
   - **`key`**: the Dart `flagKey` string (required).
   - **`name`**: human-readable name aligned with the display name (required).
   - **`description`**: optional; short purpose/scope text.
   - **`tags`**: string array, e.g. `["Kiosk"]` or `["POS", "Shared"]`.
   - **`kind`**: omit or `"boolean"` for standard on/off flags.
   - **`temporary`**: set `true` or `false` per team convention (temporary vs permanent); default MCP behavior is a boolean temporary flag if unspecified—match product expectations.

   **`create-flag`** creates the flag **OFF in all environments** with no rules yet.

3. **Mandatory targeting for boolean flags (after `create-flag`)** — For every **boolean** flag, configure LaunchDarkly so **internal beta** can exercise the feature while everyone else stays off. Do this **for each environment** where the flag is evaluated (typically **test**, **staging**, and **production**), unless the user explicitly narrows the list.

   **Standard segment (do not rename or substitute unless the user says otherwise):**

   - **Segment key:** `internal-beta-users` (LaunchDarkly segment; this is the canonical “internal beta” group for targeting rules).

   **Intended evaluation result:**

   - Users in segment **`internal-beta-users`** → serve **`true`** (the “on” variation).
   - Everyone else → serve **`false`** (fallthrough / default for non-matching contexts).

   **Apply per environment** (repeat for `test`, `staging`, `production` as appropriate):

   1. **`toggle-flag`** — set **`on`: `true`** so rules and fallthrough are evaluated (if the flag is off, only `offVariation` is served and segment rules never run).
   2. **`update-rollout`** — set the **fallthrough** default to the **`false`** variation (for typical boolean flags, variation index **`1`** is `false` when index **`0`** is `true`; use **`get-flag`** after create to confirm indices and variation `_id`s if unsure).
   3. **`update-targeting-rules`** — **`addRule`** with a **segment match** clause on **`internal-beta-users`** that serves the **`true`** variation (same clause shape as other POS flags: `contextKind` **`user`**, **`segmentMatch`** / values **`["internal-beta-users"]`**).

   If an environment returns an error such as **unknown segment** for `internal-beta-users`, document it in your summary and leave that environment for **manual** LaunchDarkly UI follow-up (segment must exist for that environment / project).

4. **Verify** — call **`list-flags`** again with `query` set to the new key and confirm it appears; optionally **`get-flag`** per environment to confirm **`on`**, fallthrough **`false`**, and one rule targeting **`internal-beta-users`** → **`true`**.

- Add the flag to the published flags list in Dart.

## Completion Criteria

- Flag is prefixed and tagged correctly
- `list-flags` confirms the flag exists in LaunchDarkly for the chosen `projectKey`
- For **boolean** flags, targeting is applied per the **Mandatory targeting** section: segment **`internal-beta-users`** → **`true`**, fallthrough **`false`**, in each configured environment (or user is told what failed and what to fix in the UI)
- Flag has been added to the respective dart file
- No other code changes have been made to control flow
