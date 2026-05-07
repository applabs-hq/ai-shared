# Good and Bad Tests

Use these examples together with `rules/flutter-testing.mdc`. The shared defaults are: per-module tests, state-based assertions, DAMP test bodies, and real implementations before fakes, stubs, or mocks.

## Good Tests

**Integration-style**: Test through real interfaces, not mocks of internal parts.

```dart
// GOOD: Tests observable behavior through the public service API.
test('creates an order from a valid cart', () async {
  final container = ProviderContainerBuilder()
      .withSingleBox(FakeCacheBox<OrderDTO>())
      .build();
  addTearDown(container.dispose);

  final service = container.read(OrdersDI.service);

  final order = await service.createOrder(validCart);

  expect(order.status, OrderStatus.confirmed);
});
```

Characteristics:

- Tests behavior users/callers care about
- Uses public API, provider, controller, or service only
- Survives internal refactors
- Describes WHAT, not HOW
- One assertion per concept
- Uses real implementations where practical, backed by fakes for local I/O

## Bad Tests

**Implementation-detail tests**: Coupled to internal structure.

```dart
// BAD: Tests an internal interaction instead of the resulting order state.
test('calls payment gateway with cart total', () async {
  await service.createOrder(validCart);

  verify(mockPaymentGateway.charge(validCart.total)).called(1);
});
```

Red flags:

- Mocking internal collaborators
- Testing private methods
- Asserting on call counts/order
- Test breaks when refactoring without behavior change
- Test name describes HOW not WHAT
- Verifying through external means instead of interface

```dart
// BAD: Bypasses the module interface to verify persistence.
test('saveCustomer writes to cache', () async {
  await service.saveCustomer(customer);

  final dto = fakeCustomerBox.get(customer.id);
  expect(dto, isNotNull);
});

// GOOD: Verifies through the module interface.
test('saveCustomer makes the customer retrievable', () async {
  await service.saveCustomer(customer);

  final saved = await service.getCustomer(customer.id);
  expect(saved.name, 'Alice');
});
```
