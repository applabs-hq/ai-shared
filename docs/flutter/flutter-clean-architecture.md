# Flutter Frontend Clean Architecture

## Folder Structure

```
core/
    env/
    navigaiton/
    util/
features/
    auth/
        src/
            data/
                repos/
                models/
                mappers/
                sources/
            domain/
                entities/
                value_objects/
                repos/
                services/
                handlers/
                events/
            ui/
                features/
                    login/
                        login.form.dart
                        login.fd.dart
                        login.fd.mapper.dart
                        login.page.dart
                        login.controller.dart
                    signup/
                    forgot_password/
                widgets/
                auth.ui.constants.dart
                auth.providers.dart
                auth.router.dart
            module/
                auth.di.dart
                auth.module.dart

        test/
        auth.api.dart
```

## Domain Layer

The domain layer also encapsulates the application layer in this structure.

### Entities & Value Objects

- Follow clean architecture principles here, entities usually have an ID. Value Objects are smaller composable parts, enums, etc. I.e. Name class that holds first and last name.
- Entities are immutable and use freezed for generation.
- Entities should be equatable.
- Entities should expose a copy with
- Entity behaviour, i.e. cart.addItem should be added as extensions on the entity (in the same file)
- Naming should follow \*.entity.dart for entities and \*.dart for value objects

### Repos

- Standard repo abstract interface definitions.
- NEVER to be exported through \*.api.dart or accessed in UI or outside the module, repos may only pass through services / usecases.
- Naming is \*.repo.dart

### Handlers

- A domain handler can be an event handler that handles incoming events off the bus. e.g. CartUpdatedHandler
- A handler can also be listening to a stream from the repository or service and converting that into an event or performing side effects / calling services / business logic.
- Naming is \*.handler.dart

### Events

- Event source definitions for domain level events or user analytic events.
- Naming is \*.event.dart

### Services

- These are the "use cases" of this entire architecture. Individual use case files results in too many files to manage as features scale. Services keep this cleaner and more contained.
- A service is the external gateway into a feature, this should expose all possible business logic, data streams passed through / mapped from the repos, and be exported through \*.api.dart
- Repos should encapsulate basic CRUD, and entities should have majority of business logic inside their extension functions. Services perform things like the lookup, editing, and saving of an entity, as well as any other encapsulated logic. They are essentially orchestrators with logic.
- All streams should be passed through services from the repo as it's public gateway.
- Services can access other services exported through other modules apis.
- The logger should be injected here and logs should be sent for majority of logic.
- Naming should be \*.service.dart

---

## Data Layer

### Models

- Majority of all DTOs and models should be defined in either the main flutter app or the shared project.
- Immutable, generated with Freezed and have to / from json
- Naming should be \*.dto.dart or \*.record.dart for pure cache records. Class naming should be `SomeModelDTO`

### Mappers

- Mappers are extensions on DTOs, server enums, Entities, and Value Objects that map between layers
- One file can have the `toDto` and `toDomain` and `toRecord` etc for the same representative type. No need to separate files here.
- Naming should be \*.mapper.dart

### Repos

- Try/catch all calls that can fail here
- Use BehaviorSubject from rxDart, do NOT use native stream controllers.
- Provide at least a `entityStream` and `entity` getter for each entity

```dart
abstract interface class UserRepo {
    Stream<User> get userStream;

    User? get user;

    // OR, if stream was seeded with a value

    User get user;
}
```

- Use rxdart for this entity getter

```dart
User get user => userSubject.value;

// OR if not seeded

User? get user => userSubject.valueOrNull;
```

- Define a dispose method and always dispose of resources safely.
- Inject the logger class and technical log happy and sad paths from here.

### Sources

- Any data source accessed by a repo.
- Remote datasources should use the JumpNetworkService to access the network
- Local datasources should extend the `LocalDataSource<T>` class to implement. This allows access to all of the cache access methods, but requires injecting the cache into the source.
- Local datasources get their own hive box currently. You can either provide a to and from json (not preferred), or use Hive CE generator to do it. Add the type(s) to `hive_types.dart` and run build runner and hive will generate a type adapter for you and register it automatically. This is the preferred method of local object storage.
- Do not log any thing from data sources.
- Naming is \*.remote.ds.dart and \*.local.ds.dart

---

## Module Layer

- Contains the module.di.dart file, responsible for creating and providing all basic DI for the module internally and externally.
- Riverpod is used for DI.
- The public DI should be an abstract final class called `ModuleDI`.
- The private internal DI (i.e. a repo, or any data layer class) should be an abstract final class called `InternalModuleDI` which is made visible for testing.
- All DI defintions should be static final providers on these classes.
- Do NOT append the word `Provider` on the end, `InternalAuthDI.authRepository` is fine.
- Internal providers are anything not allowed to be exposed through the \*.api.dart file
- Do NOT use anything except providers in these definitions. No other provider type may be defined, i.e. No Notifiers, StreamProviders, FutureProviders, or AsyncNotifierProvider. Just pure provider access here, the UI layer is responsible for those other provider defintions.
- All providers should be autoDispose by default. STOP IMMEDIATELY and report back if you believe it should be singleton, do NOT make this singleton decision yourself.
- Inject EVERYTHING in this layer, nothing in the domain or data layer should have access to the riverpod Ref object to pull their own dependencies. All of this should be managed here. UI layer may also access riverpod.
- \*.module.dart file is for defining an intializer for each module, these are registered in app orchestrator files to initialize on app launch. Starting side effects (i.e. polling) and eager initialization should be managed here

## UI Layer / View Layer

### Models & Mappers

- Form data should always be typed to a model. Use Freezed to generate the JSON. Mappers can be defined here to map to entity if possible, or at least passed to a function in a controller then sent as params. \*.fd.dart, \*.fd.mapper.dart
- Enums to support any UI state, use this sparingly, this should usually come from riverpod.
- Extensions on Enums to define constants, icons or colors for example. PaymentMethod.constants.dart can be exported. module.ui.constants is also fine

### Widgets

- Widgets shared across features

### Features

- UI split inside the module, i.e. login, signup, forgot_password
- Features usually contain at least one page / dialog / view and one controller.
- A controller is basically a view model + presenter for that feature, it reacts to user input, is a state machine, handles failures and maps them to error messages in the controllers state, calls the router, etc. It is usually a riverpod Notifier or an AsyncNotifier.
- Naming is \*.page.dart, \*.controller.dart, \*.dialog.dart, \*.form.dart, \*.field.dart, etc

### Router and Routing

- Routes are either implemented with the AutoRoute or GoRouter package. There is a navigation folder in core with an AppRouter class that contains all routes in the app.
- New autoroutes are added by decorating a widget with @RoutePage and then running build runner to generate it, after that the route can be registered in the router.dart file.
- New GoRoutes are defined with static string routes and route parts on the widget
- Routing with the router is done via riverpod, not context. i.e. `ref.read(AppRouter.provider).push(RoutePage)`
- Showing sheets and dialogs is also owned by the app router, i.e. `ref.read(AppRouter.provider).showDialog(...)`
- \*.router.dart is a class that contains all app router calls in the whole module. This is so we can mock this router class in tests separately from the controller, and encapsulate all routing in one file if we swap router packages.
- Keeping this file allows us to test all side effects triggered by the controller by mocking this router.

```dart
abstract interface class AuthRouter {
    static final provider = Provider<AuthRouter>...
    ...
}

final class _AuthRouterImpl implements AuthRouter {
    const _AuthRouterImpl(this.ref);

    final Ref ref;

    ...
}
```

### Design System

- The design system is JumpUI
- It is a classic library of UI components, using a mix of material and ShadCN
- A lot of constants exist here, breakpoints, corner radius, spacing. Do not use magic spacing numbers, use `Spacing.xs.value` for example.
- Do not use Sized Box spacing, prefer `const HorizontalSpacing.xs()` or vertical counterpart

### Responsive Design

- Always design with a responsive mindset.
- There is a `Breakpoint` enum and helper methods, i.e. `context.breakpoint`
- There is breakpoint aware reponsive classes to build `ResponsiveLayout` and `ResponsiveBuilder`. Use these at the top most page level to define different layouts, then have widgets underneath like \_SmallView or \_LargeView, or \_MobileView and \_DesktopView
- Do NOT use media query yourself to read width, use breakpoints
- Prefer LayoutBuilder for reading available space and setting width/height rather than using percentages of entire width/height

## \*.api.dart Files and Inter-module Communication

### API Files

- api files are purely for exporting, no definitions.
- Do NOT export repos, they should pass through services or handlers.
- The rest of the domain layer is fine to export.
- Do NOT export anything from the data layer. Mappers needed in other classes should be reimplemented there. DTOs should come from the serverpod client, and thus shared between modules inherently.
- Some widgets, dialogs, etc can be exported if needed across modules.
- Routes are automatically generated and stored in a generated file for the app, so we do not need to explicitly export routes or pages if they are not needed.
- Think of these as package definition files, export the minimum required to allow functionality.

### Inter-module Communication

- Modules may ONLY import other modules \*.api.dart file, no direct imports are allowed.
- If something is not in the api file, reference that in your summary, do not break previous rules to add exports you think you need access to, stick to the architecture.
- The entry way for most features is handled through services, these are the use cases. The service should already be built for you and exported as a provider in _.di.dart, available from the _.api.dart file.

## Util & External Libraries

- Most of this can be handled with a single SomeService class to wrap a library and not expose it's internals
- Shared util extensions should all live in an `extensions/` folder in a \*.ext.dart file
- Clean architecture is still fine here, but if a data or domain layer is not needed, then a service is fine

```
logger/
    src/
        strategies/
            log_source.strategy.dart
            sentry_log_source.strategy.dart
        models/
            log_event.dart
        logger.dart
    logger.api.dart
```

## General Coding Conventions

- Class Implementations should be ClassNameImpl with Impl on the end
- Use proper class decorators, i.e. interface, abstract, final, etc
- Always be critical of my own and your work
- Ask questions when you are unsure, do not make things up to fill gaps
- Explore multiple options when solutionizing, choose the easiest to test and extend
- Always stick to the projects architecture, when you cannot, stop and say that
- Do not add external libraries at a whim, take into account open issues and PRs, commit frequency, CHANGELOG, code quality, and Dart version support
