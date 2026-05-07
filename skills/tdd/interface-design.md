# Interface Design for Testability

Good interfaces make testing natural:

1. **Accept dependencies, don't create them**

   ```dart
   // Testable
   class OrderService {
     const OrderService(this.paymentGateway);

     final PaymentGateway paymentGateway;

     Future<Order> processOrder(Order order) async {
       // ...
     }
   }

   // Hard to test
   class OrderService {
     Future<Order> processOrder(Order order) async {
       final gateway = StripeGateway();
       // ...
     }
   }
   ```

2. **Return results, don't produce side effects**

   ```dart
   // Testable
   Discount calculateDiscount(Cart cart) {
     // ...
   }

   // Hard to test
   void applyDiscount(Cart cart) {
     cart.total -= calculateDiscount(cart).amount;
   }
   ```

3. **Small surface area**
   - Fewer methods = fewer tests needed
   - Fewer params = simpler test setup

4. **Test through providers when available**
   - Expose module entry points through Riverpod providers/DI.
   - In tests, read controllers and services from `ProviderContainerBuilder`.
   - Override only boundary providers such as remotes, routers, platform channels, or clocks.
