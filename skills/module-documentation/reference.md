# MODULE.md blank template

Copy the **Template body** into `lib/features/{feature}/MODULE.md`. Replace `{placeholders}`; remove unused table rows.

---

## Template body

# {Human-readable module title}

<!--
  Canonical summary for this feature folder. Target: orient in <2 minutes; detail lives in code and shared packages.

  Drift: keep [VERIFY] sections and behavioural tables aligned when wiring, events, or entry points change.
  Optional: Last verified: YYYY-MM-DD after substantive edits.
-->

## At a glance

- **Role:** {one sentence: what domain outcome this module ensures}
- **App surface:** {AppModule class name} — {how it starts; routes/settings if any}
- **Core dependency:** {primary domain API, e.g. jump_core service}

## Purpose & boundaries

| In scope | Out of scope |
|----------|----------------|
| {bullets} | {bullets} |

## Lifecycle & operational states

<!--
  For auth, connectivity, checkout steps, etc., list states that change behaviour.
  If not applicable: one row N/A with short rationale.
-->

| State | Relevance to this module |
|-------|---------------------------|
| … | … |

## Business rules [VERIFY]

<!--
  Optional. Add only when a developer has explicitly confirmed rules (fees, channels, compliance, money).
  Do not invent rows to sound complete. If none confirmed, delete this section.
-->

| Rule | Behaviour |
|------|-----------|
| … | … |

## Entry points [VERIFY]

| Kind | Location |
|------|----------|
| Public barrel | `{feature}.api.dart` → `{AppModuleClass}` |
| DI | `src/module/{feature}.di.dart` |
| Module | `src/module/{feature}.module.dart` |

## Ports (incoming)

Ports are stimuli this module reacts to. Map each to the adapter (handler / use case) by **type name**.

| Port | Type | Source / contract | Adapter |
|------|------|-------------------|---------|
| … | `AppEvent` / … | `{EventOrContract}` | `{Handler}` — {what it does} |

## Adapters (outgoing)

Capabilities this module uses. Prefer cross-feature access via `*.api.dart` barrels per repo rules.

| Capability | Resolved via |
|------------|----------------|
| … | `{ServiceOrApi}` — {methods or role} |

## Side effects & downstream effects

- {Observable outcomes: state updates, events emitted, persistence}

## Related modules & packages

- {package or feature name}: {types or contracts; no file paths except progressive disclosure}

## Progressive disclosure (where to read next)

1. **Behaviour:** `src/handlers/...`
2. **Wiring:** `src/module/...`
3. **Domain:** {package} {layer} (e.g. jump_core …)

## Changelog (doc)

| Date | Note |
|------|------|
| … | … |

---

## Agent notes

- **Paths** appear only in **Entry points [VERIFY]** and **Progressive disclosure**, per project convention.
- **Business rules:** never assume—only document rules **confirmed by a developer**; see skill `SKILL.md`.
- **Ports:** prefer typed **AppEvents**; if wiring is still Riverpod/stream-based, document the **domain trigger**, not every provider.
- **Do not** document UI folders or screens here (future optional `FEATURE.md`).
- Omit boilerplate dependencies (logger, generic `Ref`) unless they define behaviour.
