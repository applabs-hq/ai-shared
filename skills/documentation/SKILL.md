---
name: documentation
description: Records decisions and documentation. Use when making architectural decisions, changing public APIs, shipping features, or when you need to record context that future engineers and agents will need to understand the codebase.
---

# Documentation and ADRs

## Overview

Document decisions, not just code. The most valuable documentation captures the _why_ — the context, constraints, and trade-offs that led to a decision. Code shows _what_ was built; documentation explains _why it was built this way_ and _what alternatives were considered_. This context is essential for future humans and agents working in the codebase.

## When to Use

- Making a significant architectural decision
- Choosing between competing approaches
- Adding or changing a public API
- Shipping a feature that changes user-facing behavior
- Onboarding new team members (or agents) to the project
- When you find yourself explaining the same thing repeatedly

**When NOT to use:** Don't document obvious code. Don't add comments that restate what the code already says. Don't write docs for throwaway prototypes.

## Inline Documentation

### When to Comment

Comment the _why_, not the _what_:

```dart
// BAD: Restates the code
// Increment counter by 1
counter += 1;

// GOOD: Explains non-obvious intent
// Rate limit uses a sliding window — reset counter at window boundary,
// not on a fixed schedule, to prevent burst attacks at window edges
if (now - windowStart > WINDOW_SIZE_MS) {
  counter = 0;
  windowStart = now;
}
```

### When NOT to Comment

```dart
// Don't comment self-explanatory code
Money calculateTotal(List<CartItem> items) {
  return items.fold(
    Money.zero,
    (sum, item) => sum + item.price * item.quantity,
  );
}

// Don't leave TODO comments for things you should just do now
// TODO: add error handling  ← Just add it

// Don't leave commented-out code
// Future<void> oldImplementation() async { ... }  ← Delete it, git has history
```

### Document Known Gotchas

```dart
/// IMPORTANT: This must run before the first frame.
/// If called later, the app may briefly render with the wrong theme because
/// persisted settings have not been loaded into the provider graph yet.
///
/// See ADR-003 for the full design rationale.
Future<void> initializeTheme(ThemeMode themeMode) async {
  // ...
}
```

## API Documentation

For public APIs (REST, GraphQL, library interfaces):

### Dart API docs

```dart
/// Creates a new task.
///
/// [input] contains the task title and optional description.
/// Returns the created task with server-generated ID and timestamps.
///
/// Throws [ValidationException] if the title is empty or exceeds 200
/// characters. Throws [AuthenticationException] if the user is not
/// authenticated.
///
/// Example usage:
/// final task = await createTask(
///   const CreateTaskInput(title: 'Buy groceries'),
/// );
/// print(task.id);
Future<Task> createTask(CreateTaskInput input) async {
  // ...
}
```

### OpenAPI / Swagger for REST APIs

```yaml
paths:
  /api/tasks:
    post:
      summary: Create a task
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateTaskInput"
      responses:
        "201":
          description: Task created
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Task"
        "422":
          description: Validation error
```

## README Structure

Every project should have a README that covers:

```markdown
# Project Name

One-paragraph description of what this project does.

## Quick Start

1. Clone the repo
2. Install dependencies: `flutter pub get`
3. Set up environment: `cp .env.example .env`
4. Run the app: `flutter run`

## Commands

| Command           | Description          |
| ----------------- | -------------------- |
| `flutter run`     | Run the app          |
| `flutter test`    | Run tests            |
| `flutter analyze` | Run static analysis  |
| `dart format .`   | Format Dart code     |

## Architecture

Brief overview of the project structure and key design decisions.
Link to ADRs for details.

## Contributing

How to contribute, coding standards, PR process.
```

## Changelog Maintenance

For shipped features:

```markdown
# Changelog

## [1.2.0] - 2025-01-20

### Added

- Task sharing: users can share tasks with team members (#123)
- Email notifications for task assignments (#124)

### Fixed

- Duplicate tasks appearing when rapidly clicking create button (#125)

### Changed

- Task list now loads 50 items per page (was 20) for better UX (#126)
```

## Documentation for Agents

Special consideration for AI agent context:

- **AGENTS.md / rules files** — Document project conventions so agents follow them
- **Spec files** — Keep specs / contexts updated so agents build the right thing
- **ADRs** — Help agents understand why past decisions were made (prevents re-deciding)
- **Inline gotchas** — Prevent agents from falling into known traps

## Common Rationalizations

| Rationalization                            | Reality                                                                                               |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| "The code is self-documenting"             | Code shows what. It doesn't show why, what alternatives were rejected, or what constraints apply.     |
| "We'll write docs when the API stabilizes" | APIs stabilize faster when you document them. The doc is the first test of the design.                |
| "Nobody reads docs"                        | Agents do. Future engineers do. Your 3-months-later self does.                                        |
| "ADRs are overhead"                        | A 10-minute ADR prevents a 2-hour debate about the same decision six months later.                    |
| "Comments get outdated"                    | Comments on _why_ are stable. Comments on _what_ get outdated — that's why you only write the former. |

## Red Flags

- Architectural decisions with no written rationale
- Public APIs with no documentation or types
- README that doesn't explain how to run the project
- Commented-out code instead of deletion
- TODO comments that have been there for weeks
- No ADRs in a project with significant architectural choices
- Documentation that restates the code instead of explaining intent

## Verification

After documenting:

- [ ] ADRs exist for all significant architectural decisions
- [ ] README covers quick start, commands, and architecture overview
- [ ] API functions have parameter and return type documentation
- [ ] Known gotchas are documented inline where they matter
- [ ] No commented-out code remains
- [ ] Rules files (AGENTS.md etc.) are current and accurate
