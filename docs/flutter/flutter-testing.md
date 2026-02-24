# Flutter Testing Rules

This document defines how we test Flutter. Tests are **per-module**, and favour **real implementations** over mocks where it makes sense.

---

## 1. Structure and scope

### Per-module tests

- Tests are organised **by feature module** under `app_name/test/modules/<module_name>/`.
- Mirror the module’s `src/` layout where helpful (e.g. `*_service_test.dart`, `*_controller_test.dart`, `*_sync_handler_test.dart`).
- One test file per logical unit (service, controller, handler, etc.).

### What we focus on

- **Unit tests** that exercise as many **real** layers as possible: real repositories, real data sources
- **No real I/O**: use **fake cache boxes** (e.g. `FakeCacheBox<T>`) instead of real Hive/disk so tests stay fast and deterministic.
- **Mockito** is used **sparingly**, mainly for:
  - **Remote data sources** (e.g. `MockAddressBookRemoteDataSource`) so we don’t hit the network.
- **Widget tests** are **out of scope** for feature logic. Use them only for:
  - **UI components** and **JumpUI design library** (presentation, layout, interactions).
  - Not for full screens or flows; prefer unit tests for behaviour.

---

## 2. ProviderContainerBuilder and Riverpod

### Prefer Riverpod and the builder

- **Prefer testing through Riverpod** so the app’s dependency graph is used.
- Use **`ProviderContainerBuilder`** (from `test/helpers`) to build a test `ProviderContainer` with the right overrides instead of manually constructing repositories, data sources, or services.
- The builder lets you:
  - Stub **HiveCacheService** with **fake boxes** (`withSingleBox`, `withNamedBox`).
  - Add **custom overrides** with `withCustomOverride` for module-specific needs (e.g. a sync handler that uses a mock remote).
- **Do not** manually build `*Impl` classes for repos, data sources, or services unless the test has a very specific reason; pull them from the container via the same providers the app uses (e.g. `AddressBookDI.service`, `InternalAddressBookDI.repository`).

### Extending the builder

- If a pattern (e.g. “real outbox + custom registry”) is needed in **multiple test modules**, add a reusable method or option to **`ProviderContainerBuilder`** in `app/test/helpers/src/provider_container.builder.dart` rather than duplicating setup in each test.

---

## 3. Testing with real layers

### Services and repositories

- Test **services** with **real repositories** and **real local data sources**, backed by **fake cache boxes** only.
- Example: address book service tests use `UserRepositoryImpl` and `UserLocalDataSource` with `FakeCacheBox<UserDTO>`; no real Hive.
- Use **`container.read(ModuleDI.service)`** (or the relevant provider) so the real DI chain is exercised.

---

## 4. Controller testing

**Prefer controller tests** to cover real user interactions, loading state, and UI state. They are among the highest-value tests because a single test can exercise the full stack: controller → service → repository → data sources, with only the lowest-level I/O faked (e.g. fake cache boxes) and remotes mocked where needed.

### Why controller tests

- They assert **real interactions**: user actions, loading flags, error state, and the exact state the UI would read.
- They go **as far down the stack as possible** with real implementations—same services, repos, and local data sources the app uses—so integration-style coverage without leaving the test process.
- One test can validate that “toggle dark mode” or “load address book” flows correctly from the controller through to persistence or sync, including stream emissions and state transitions.

### How to test controllers

- Build a **`ProviderContainer`** with **`ProviderContainerBuilder`** (same as for service tests: fake boxes, real or mock sync, etc.).
- Use **`container.listen(ControllerProvider, (_, __) {})`** and **`subscription.read()`** (or **`readNext()`** after an async tick) to assert on the controller’s state (e.g. loading, data, error).
- Trigger actions via **`container.read(ControllerProvider.notifier).someMethod()`** and then assert on the resulting state.

### Mocking the router

- When a controller depends on a router (e.g. to navigate after save), **mock the module’s router**. Each module defines its own router, which is a small, easy-to-mock boundary.
- Override the router provider in the container with **`withCustomOverride(ModuleRouter.provider.overrideWith((_) => mockRouter))`** so controller tests stay focused on behaviour without real navigation.

---

## 5. Riverpod: listening and reading state

- Many providers are **auto-dispose**; to keep them alive and read current state, **listen** to the provider.
- Use **`container.listen(SomeProvider, (prev, next) {})`** to get a **`ProviderSubscription`**. Use **`subscription.read()`** to get the **current value**.
- For streams or async updates, subscribe (e.g. to a service’s stream) and use **`addTearDown(sub.cancel)`** so the subscription is cancelled when the test ends.

Example (listening to a provider and reading current value):

```dart
final subscription = container.listen(AppSettingsController.provider, (_, _) {});
final result = subscription.read().settings;
```

Example (listening to a service stream and cleaning up):

```dart
final sub = addressBookService.addressBookStream.listen((_) {});
addTearDown(sub.cancel);
// ... later: use addressBookService.addressBook or stream events
```

- For “next value after an async tick”, use the helper **`subscription.readNext()`** (from `provider_test.helpers.dart`), which does `Future.delayed(Duration.zero)` then `read()`.

---

## 6. Async and waiting in tests

- **`Future.delayed(Duration.zero)`** – use to yield to the next event-loop tick when you need a state update or a microtask to run (e.g. after a repository write or stream emission).
- **Mockito `untilCalled`** – use with a timeout to wait for a specific mock call (e.g. `await untilCalled(mockRemote.upsert(any))`) instead of arbitrary sleeps.
- Prefer **deterministic waits** (zero delay, `untilCalled`, or waiting on a stream/future) over fixed durations.

---

## 7. Mocks: where and when

### Module-local mocks

- A **test module** can define its **own mocks** (e.g. `address_book.mockito.dart` with `@GenerateNiceMocks([MockSpec<AddressBookRemoteDataSource>(), ...])`) for types used only in that module’s tests.

### Shared mocks

- Mocks that are used **across multiple test modules** (e.g. `MockHiveCacheService`, `MockOutbox`, `MockSyncCoordinator`) belong in the **shared test helpers** and are generated from `app/test/helpers/src/helpers.mockito.dart` (and re-exported via `test_helpers.api.dart`).
- Add new shared mocks there when a second module needs the same mock; avoid duplicating mock definitions.

---

## 8. Quick reference

| Goal                        | Approach                                                                                                                                                                                             |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Test a controller           | `ProviderContainerBuilder` + `container.listen(ControllerProvider)` + `subscription.read()` / `readNext()`; mock router with `withCustomOverride(ModuleRouter.provider.overrideWith(...))` if needed |
| Test a service              | `ProviderContainerBuilder` + fake boxes + `container.read(ModuleDI.service)`                                                                                                                         |
| Multiple cache boxes        | `withNamedBox(boxName, FakeCacheBox<T>())` per box                                                                                                                                                   |
| Single cache box            | `withSingleBox(FakeCacheBox<T>())`                                                                                                                                                                   |
| Custom provider override    | `withCustomOverride(SomeProvider.overrideWith(...))`                                                                                                                                                 |
| Read current provider state | `container.listen(provider, (_,__){}).read()` or `subscription.readNext()`                                                                                                                           |
| Wait for next async tick    | `Future.delayed(Duration.zero)` or `subscription.readNext()`                                                                                                                                         |
| Wait for mock call          | `await untilCalled(mock.method(any))` (optionally with timeout)                                                                                                                                      |
| Widget tests                | Only for UI / JumpUI components; not for feature behaviour currently                                                                                                                                 |
