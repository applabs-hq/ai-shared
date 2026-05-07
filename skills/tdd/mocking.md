# When to Mock

Follow the Flutter testing rule's preference order: **real implementation -> fake -> stub -> mock**. Mock at **system boundaries** only:

- Remote data sources and external APIs
- Routers in controller tests
- Platform channels
- Time/randomness
- File system or disk-backed cache when a fake is not enough

Don't mock:

- Your own services, repositories, controllers, or data sources when a real implementation can run in-process
- Internal collaborators
- Anything you control

## Designing for Mockability

At system boundaries, design interfaces that are easy to mock:

### 1. Use Dependency Injection

Read dependencies from Riverpod providers or accept them through constructors instead of creating them internally:

```dart
// Easy to mock
class PaymentService {
  const PaymentService(this.gateway);

  final PaymentGateway gateway;

  Future<PaymentResult> process(Order order) {
    return gateway.charge(order.total);
  }
}

// Hard to mock
class PaymentService {
  Future<PaymentResult> process(Order order) {
    final gateway = StripePaymentGateway(apiKey);
    return gateway.charge(order.total);
  }
}
```

### 2. Prefer SDK-Style Interfaces Over Generic Fetchers

Create specific methods for each external operation instead of one generic method with conditional logic:

```dart
// GOOD: Each method is independently mockable
abstract interface class OrdersRemoteDataSource {
  Future<OrderDTO> getOrder(String id);
  Future<List<OrderDTO>> getOrdersForCustomer(String customerId);
  Future<OrderDTO> createOrder(CreateOrderRequest request);
}

// BAD: Mocking requires conditional logic inside the mock.
abstract interface class ApiClient {
  Future<Object?> request(String path, {String method, Object? body});
}
```

The SDK approach means:

- Each mock returns one specific shape
- No conditional logic in test setup
- Easier to see which remote operation a test exercises
- Type safety per operation

## Flutter Test Setup

- Use `ProviderContainerBuilder` to override boundary providers.
- Prefer fake cache boxes over real Hive/disk.
- Prefer real services and repositories pulled from the container.
- Generate Mockito mocks module-locally unless the same mock is needed by multiple modules; shared mocks belong in shared test helpers.
