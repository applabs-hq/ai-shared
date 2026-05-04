---
name: module-documentation
description: Creates and maintains MODULE.md for feature modules—purpose, boundaries, lifecycle, ports/adapters, drift checks, and developer-confirmed business rules (never assumed). Use when adding or changing a feature module, wiring AppModule/DI/handlers, subscribing to AppEvents, reducing ad-hoc Riverpod side effects, or when the user asks for module docs or doc/code alignment.
---

# Feature MODULE.md

## When to use this skill

- **Create:** New feature folder under `lib/features/` with an `AppModule` (or equivalent entry).
- **Update:** Behaviour, wiring, event subscriptions, boundaries, or lifecycle-relevant state changes.
- **Drift pass:** After edits, reconcile `[VERIFY]` sections and behavioural tables with code.

## Principles

1. **Self-contained modules** — Document how the module initializes itself (typically `AppModule.initialize` + DI). Prefer **explicit domain events** (`AppEventBus`, typed events) as documented *ports* over undocumented Riverpod `listen` / stream side effects. If the code still uses streams, document the *behavioural* trigger (what domain fact changed), not every provider.
2. **Documentation tracks the core story** — When purpose, boundaries, lifecycle, ports, or outgoing adapters change, **update MODULE.md in the same change** (or immediately after).
3. **Scope of MODULE.md** — **Domain and below:** module wiring, handlers, use cases, DI, domain-side effects. **Do not** document UI folders, widgets, or screens here. (Future: optional `FEATURE.md` per feature for UI; out of scope for this skill.)
4. **Dependencies in prose** — List **behavioural** integrations (e.g. `CartService`, fee events, other feature API contracts). Omit boilerplate (logger, generic `Ref`, `JumpLogSink`) unless the logging or lifecycle is part of the module’s contract.
5. **Paths** — **Only** the **Entry points [VERIFY]** table and the **Progressive disclosure** list may cite concrete repo paths. Elsewhere use type names, package/feature names, and conceptual locations (`jump_core` cart layer, `kiosk` auth API barrel).
6. **Business rules — developer-owned** — **Never invent or assume** product or domain rules (fees, surcharges, auth, eligibility, money, compliance, channel-specific behaviour). Those belong in **## Business rules [VERIFY]** only when they are **explicitly stated or confirmed by a developer** (in chat, ticket, or code review). If the user has not supplied a rule, **ask** or **leave the section out**—do not fill gaps with plausible guesses. Treat `[VERIFY]` on that section as: *confirmed by a human; drift if code changes without updating the table.*

## Business rules (MODULE.md)

- **When to add:** The feature has non-obvious constraints that engineers must not get wrong (e.g. “POS never persists X from location”, “this handler only applies on channel Y”).
- **When to omit:** No special rules, or none have been confirmed—do not fabricate a table “to be helpful”.
- **Format:** A **## Business rules [VERIFY]** section with a short table: **Rule** | **Behaviour** (or equivalent). Link to code/handler names in prose only (no new path rules—use progressive disclosure for file pointers).
- **Agent behaviour:** If implementing or documenting behaviour that implies a business rule, **stop and ask** unless the user already stated it. After confirmation, add or update the table the same change as the code.

## File location

- One `MODULE.md` per feature, at **`lib/features/<feature>/MODULE.md`** (sibling to the feature’s `*.api.dart` barrel when present).

## Drift control

- Sections tagged **`[VERIFY]`** must stay aligned with code: entry barrels, DI types, module class, any listed ports/adapters, and **business rules** once recorded (rules must remain true in code or be updated with developer agreement).
- Optional footer: **`Last verified: YYYY-MM-DD`** after substantive doc edits.
- **Changelog (doc)** table: one row for meaningful doc updates (not every typo).

## Workflow: create

1. Add `MODULE.md` using the template in [reference.md](reference.md).
2. Fill **At a glance**, **Purpose & boundaries**, **Lifecycle** (or N/A with one-line reason).
3. List **Ports (incoming)** — typed events, explicit callbacks, or rare stream triggers; map each to handler/use case **by type name** (no file paths here).
4. List **Adapters (outgoing)** — services/repos/events published to other layers **by contract name** only.
5. **Side effects** — What observable or persistent changes occur (cart updated, bus publish, etc.).
6. **Business rules [VERIFY]** — Only if a developer has confirmed specific rules; otherwise skip (see **Business rules (MODULE.md)** above).
7. **Entry points [VERIFY]** — Only section with **paths**: public barrel, DI, module implementation.
8. **Progressive disclosure** — Numbered list with **paths** to handlers, DI, module, then cross-package domain types (pathless references OK for packages).
9. Add HTML comment block at top (from template) for convention + drift hints.

## Workflow: update (trigger list)

Update MODULE.md when any of the following change:

| Change | Update these sections |
|--------|------------------------|
| New/removed event subscription or handler | Ports, Adapters, Side effects, Progressive disclosure if new files |
| AppModule init/dispose behaviour | At a glance, Entry points if providers change |
| What the module owns vs delegates | Purpose & boundaries |
| Auth/session/connectivity affecting behaviour | Lifecycle & operational states |
| Observable log/analytics names part of contract | Side effects (brief) |
| Developer-confirmed business rule added, changed, or removed | **Business rules [VERIFY]**; Purpose & boundaries if scope shifts |

Do **not** expand MODULE.md for pure UI refactors with no domain wiring change.

## Anti-patterns

- **Assuming or inventing business rules** — plausible domain behaviour without developer confirmation; filling **Business rules** from inference or other products’ behaviour.
- Duplicating every `ref.watch` or listing `Logger` / `JumpLogSink` without behavioural meaning.
- Pasting full folder trees or every import.
- Documenting `ui/` or screen flows in MODULE.md (defer to future FEATURE.md).

## Related

- Blank copy-paste template: [reference.md](reference.md)
