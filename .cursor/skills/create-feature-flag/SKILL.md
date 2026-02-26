---
name: create-feature-flag
description: Creates a new feature flag defined in code and LaunchDarkly
---

# Create Feature Flag

This is a skill for creating new feature flag locally and in the LaunchDarkly service via script.

## Rules and Scope

- Your job is ONLY to define and create the feature flag, not use it.
- Do NOT update any other code or implement this feature flag in any control flow code paths.
- Do NOT read the app code to gather more context on where and what code the flag will be used, you are only creating the flag at the request of the user
- Make no assumptions about if this flag should be Client or Shared, always ASK before assuming

## When to Use

- Use this skill ONLY when instructed, never use this yourself
- This skill is helpful for creating feature flags to manage code visibility in production environments

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
- **Tag the flag with the project** in LaunchDarkly. Use the `--tags` option with a comma-separated list. Use the tag that matches the flag’s scope (e.g. `KIOSK` for kiosk-only, `SHARED` for platform-wide). You may include multiple tags if relevant.

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

- **Create the flag in LaunchDarkly** by running the scripts from the **ai-shared** repo root (the repo that contains this skill and `.cursor/`). Use `./` so pipx treats the path as a local script and installs inline deps. Prerequisites: `pipx` installed; env in `.cursor/.env` or `.cursor/.env/.env` with `LAUNCHDARKLY_API_KEY` and `LAUNCHDARKLY_PROJECT_KEY`.

  **List existing flags** (to confirm key is unique). Run from ai-shared:

  ```bash
  cd /path/to/ai-shared && pipx run ./.cursor/skills/create-feature-flag/scripts/list_flags.py
  ```

  **Create the new flag** (use the same `flagKey` and a matching display name/description). Tag with the project (e.g. `Kiosk`, `POS`, `API`, `Shared`) via `--tags`. Run from ai-shared:

  ```bash
  cd /path/to/ai-shared && pipx run ./.cursor/skills/create-feature-flag/scripts/create_flag.py FLAG_KEY "Display name" "Optional description"
  ```

  Or with options (include `--tags` for project tagging):

  ```bash
  cd /path/to/ai-shared && pipx run ./.cursor/skills/create-feature-flag/scripts/create_flag.py --key FLAG_KEY --name "Display name" --description "Optional description" --tags "Kiosk"
  ```

  Example with multiple tags: `--tags "Kiosk,Shared"`
  - Add the flag to the published flags list

## Completion Criteria

- Flag is prefixed and tagged correctly
- Run List existing flags script and confirm flag was created
- Flag has been added to the respective dart file
- No other code changes have been made to control flow
