---
name: junit-unit-testing
description: Write comprehensive JUnit 5 unit tests for Java code following AAA structure, idiomatic annotations, and Mockito mocking patterns. Use when asked to write, add, or improve Java unit tests, increase test coverage, test a Java class or method, or set up JUnit/Mockito in a Java project.
license: MIT
---

# JUnit Unit Testing

## When to Use

- Writing new unit tests for a Java class or method
- Improving or expanding existing test coverage
- Setting up JUnit 5 and Mockito in a project
- Explaining how to test edge cases, exceptions, or async behavior

## Project Setup

Check the build file before writing tests to confirm which versions and dependencies are already present.

**Maven** (`pom.xml`):
```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.11.0</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-junit-jupiter</artifactId>
    <version>5.12.0</version>
    <scope>test</scope>
</dependency>
```

**Gradle** (`build.gradle`):
```groovy
testImplementation 'org.junit.jupiter:junit-jupiter:5.11.0'
testImplementation 'org.mockito:mockito-junit-jupiter:5.12.0'
test { useJUnitPlatform() }
```

## Test Structure

Follow the **Arrange-Act-Assert (AAA)** pattern. Separate each phase with a blank line and keep each test focused on a single behavior.

```java
@Test
void transferFunds_sufficientBalance_updatesAccountBalances() {
    // Arrange
    Account source = new Account(1000.0);
    Account target = new Account(200.0);

    // Act
    source.transferTo(target, 300.0);

    // Assert
    assertAll(
        () -> assertEquals(700.0, source.getBalance()),
        () -> assertEquals(500.0, target.getBalance())
    );
}
```

### Naming

Use the pattern `methodName_condition_expectedBehavior`. This makes failures self-documenting without needing to read the body.

## Core Annotations

| Annotation | Purpose |
|---|---|
| `@Test` | Marks a test method |
| `@BeforeEach` / `@AfterEach` | Setup/teardown per test |
| `@BeforeAll` / `@AfterAll` | Setup/teardown once per class (must be `static`) |
| `@DisplayName` | Human-readable test name in reports |
| `@Nested` | Groups related tests in an inner class |
| `@Tag` | Labels for filtering (e.g., `@Tag("slow")`) |
| `@Disabled` | Skips a test with a reason |
| `@Timeout` | Fails if test exceeds duration |

## Assertions

Prefer `assertAll` when checking multiple properties of the same result — it reports all failures at once instead of stopping at the first.

```java
// Single assertion
assertEquals(expected, actual, "optional failure message");
assertTrue(result.isValid());
assertNull(value);
assertThrows(IllegalArgumentException.class, () -> service.process(null));

// Grouped assertions
assertAll("user",
    () -> assertEquals("Alice", user.getName()),
    () -> assertEquals(30, user.getAge()),
    () -> assertNotNull(user.getId())
);
```

For exception testing, capture the exception to assert on its message:
```java
var ex = assertThrows(ValidationException.class, () -> parser.parse("bad input"));
assertThat(ex.getMessage()).contains("invalid format");
```

## Parameterized Tests

Avoid copy-pasting nearly identical tests. Use `@ParameterizedTest` with an appropriate source:

```java
@ParameterizedTest
@ValueSource(strings = {"", " ", "\t", "\n"})
void isBlank_whitespaceInput_returnsTrue(String input) {
    assertTrue(StringUtils.isBlank(input));
}

@ParameterizedTest
@CsvSource({"1, 1, 2", "2, 3, 5", "10, -3, 7"})
void add_twoIntegers_returnsSum(int a, int b, int expected) {
    assertEquals(expected, calculator.add(a, b));
}

@ParameterizedTest
@MethodSource("provideInvalidEmails")
void validate_invalidEmail_throwsException(String email) {
    assertThrows(ValidationException.class, () -> validator.validate(email));
}

static Stream<String> provideInvalidEmails() {
    return Stream.of("notanemail", "@nodomain", "missing@");
}
```

## Mocking with Mockito

Use `@ExtendWith(MockitoExtension.class)` on the class — this wires `@Mock` and `@InjectMocks` automatically and validates unused stubs.

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    PaymentGateway paymentGateway;

    @Mock
    InventoryRepository inventoryRepository;

    @InjectMocks
    OrderService orderService;

    @Test
    void placeOrder_paymentSucceeds_savesOrder() {
        // Arrange
        var order = new Order("item-1", 2);
        when(inventoryRepository.isAvailable("item-1", 2)).thenReturn(true);
        when(paymentGateway.charge(any())).thenReturn(PaymentResult.success());

        // Act
        orderService.place(order);

        // Assert
        verify(inventoryRepository).reserve("item-1", 2);
        verify(paymentGateway).charge(any(ChargeRequest.class));
    }

    @Test
    void placeOrder_paymentFails_throwsOrderException() {
        when(inventoryRepository.isAvailable(any(), anyInt())).thenReturn(true);
        when(paymentGateway.charge(any())).thenThrow(new PaymentException("declined"));

        assertThrows(OrderException.class, () -> orderService.place(new Order("item-1", 1)));
    }
}
```

**Verification tips:**
- `verify(mock).method(args)` — assert it was called exactly once
- `verify(mock, times(n)).method(args)` — assert exact call count
- `verify(mock, never()).method(any())` — assert never called
- `verifyNoMoreInteractions(mock)` — assert no other calls were made (use sparingly)

## Nested Tests

Use `@Nested` to group tests by scenario or state. This produces structured output in test reports and avoids repetitive naming.

```java
class AccountTest {

    @Nested
    @DisplayName("when account is empty")
    class WhenEmpty {
        Account account = new Account(0.0);

        @Test
        void withdraw_anyAmount_throwsInsufficientFundsException() {
            assertThrows(InsufficientFundsException.class, () -> account.withdraw(1.0));
        }
    }

    @Nested
    @DisplayName("when account has funds")
    class WhenFunded {
        Account account = new Account(500.0);

        @Test
        void withdraw_lessThanBalance_succeeds() { ... }

        @Test
        void withdraw_moreThanBalance_throws() { ... }
    }
}
```

## What to Test

Focus tests on behavior, not implementation internals:

- **Happy path**: typical valid inputs produce the expected output
- **Boundaries**: off-by-one values, empty collections, zero, `Long.MAX_VALUE`
- **Invalid input**: nulls, empty strings, out-of-range values → expect specific exceptions
- **State transitions**: the object ends up in the right state after an operation
- **Side effects**: the right collaborators were called with the right arguments

Avoid testing private methods directly — if a private method needs its own test, consider whether it belongs in a separate class.

## Test Isolation

Each test must be independent — shared mutable state between tests causes flaky, order-dependent failures:

- Declare mutable state in `@BeforeEach`, not as a class field initializer
- Never rely on test execution order
- Avoid `static` mutable fields in test classes
- If integration-style setup is expensive (e.g., spinning up a database), use `@BeforeAll` with a truly stateless shared fixture

## Running Tests

```bash
# Maven
mvn test
mvn test -Dtest=OrderServiceTest          # single class
mvn test -Dtest=OrderServiceTest#placeOrder*  # single method (glob)

# Gradle
./gradlew test
./gradlew test --tests "com.example.OrderServiceTest"
./gradlew test --tests "*OrderService*"

# View report (Maven)
open target/surefire-reports/*.html
```
