---
name: junit-testing
description: Write comprehensive JUnit 5 unit tests for Java code including assertions, mocking with Mockito, parameterized tests, and lifecycle hooks. Use when asked to write, add, or improve Java unit tests, test a class or method, set up a test suite, add Mockito mocks, or when the user mentions JUnit, test coverage, or unit testing in a Java project.
license: MIT
---

# JUnit Unit Testing

Write thorough, maintainable JUnit 5 tests. Favor clarity and isolation — each test should assert one logical concern and be readable without context.

## Dependencies

**Maven** (`pom.xml`):
```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.2</version>
    <scope>test</scope>
</dependency>
<!-- Mockito (add when mocking is needed) -->
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-junit-jupiter</artifactId>
    <version>5.11.0</version>
    <scope>test</scope>
</dependency>
```

**Gradle** (`build.gradle`):
```groovy
testImplementation 'org.junit.jupiter:junit-jupiter:5.10.2'
testImplementation 'org.mockito:mockito-junit-jupiter:5.11.0'
test { useJUnitPlatform() }
```

Check the project's existing `pom.xml` or `build.gradle` for the versions already in use before adding new dependencies.

## Test Structure

```java
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class OrderServiceTest {

    private OrderService service;

    @BeforeEach
    void setUp() {
        service = new OrderService();
    }

    @Test
    void placeOrder_withValidItems_returnsConfirmation() {
        var order = new Order(List.of(new Item("widget", 2)));
        var result = service.placeOrder(order);
        assertNotNull(result.confirmationId());
    }

    @Test
    void placeOrder_withEmptyItems_throwsIllegalArgument() {
        var order = new Order(List.of());
        assertThrows(IllegalArgumentException.class, () -> service.placeOrder(order));
    }
}
```

## Naming Convention

Use `methodUnderTest_scenario_expectedBehavior`:

```
calculateDiscount_withPremiumMember_returns20Percent
processPayment_whenCardDeclined_throwsPaymentException
findUser_withUnknownId_returnsEmpty
```

This makes failures self-documenting — the test name reads as a spec.

## Assertions

Prefer the most specific assertion available; it produces better failure messages.

```java
// Equality
assertEquals(expected, actual);
assertEquals(3.14, result, 0.001); // delta for doubles

// Nullability
assertNotNull(result);
assertNull(response.error());

// Exceptions
var ex = assertThrows(IllegalStateException.class, () -> sut.doThing());
assertTrue(ex.getMessage().contains("invalid state"));

// Collections
assertIterableEquals(expected, actual);
assertTrue(result.containsAll(expected));

// Multiple assertions without short-circuiting
assertAll(
    () -> assertEquals("Alice", user.name()),
    () -> assertEquals(30, user.age()),
    () -> assertTrue(user.isActive())
);
```

### AssertJ (recommended for richer assertions)

If AssertJ is on the classpath (`assertj-core`), prefer it for readability:

```java
import static org.assertj.core.api.Assertions.*;

assertThat(result).isEqualTo(42);
assertThat(list).hasSize(3).contains("foo", "bar");
assertThat(optional).isPresent().hasValue("expected");
assertThat(exception).isInstanceOf(ValidationException.class)
                      .hasMessageContaining("email");
```

## Mocking with Mockito

Use mocks to isolate the unit under test from its collaborators.

```java
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class NotificationServiceTest {

    @Mock
    private EmailClient emailClient;

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private NotificationService notificationService;

    @Test
    void sendWelcome_callsEmailClientWithCorrectAddress() {
        var user = new User("alice@example.com");
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        notificationService.sendWelcome(1L);

        verify(emailClient).send(eq("alice@example.com"), anyString());
    }

    @Test
    void sendWelcome_whenUserNotFound_doesNotSendEmail() {
        when(userRepository.findById(99L)).thenReturn(Optional.empty());

        notificationService.sendWelcome(99L);

        verifyNoInteractions(emailClient);
    }
}
```

**Key Mockito methods:**

| Purpose | Method |
|---|---|
| Stub return value | `when(mock.method()).thenReturn(value)` |
| Stub to throw | `when(mock.method()).thenThrow(new Ex())` |
| Verify called once | `verify(mock).method(arg)` |
| Verify N times | `verify(mock, times(2)).method(arg)` |
| Verify never called | `verify(mock, never()).method(arg)` |
| Capture argument | `ArgumentCaptor<T> captor = ArgumentCaptor.forClass(T.class)` |

Use `ArgumentCaptor` when you need to assert on a complex argument passed to a mock:

```java
ArgumentCaptor<EmailMessage> captor = ArgumentCaptor.forClass(EmailMessage.class);
verify(emailClient).send(captor.capture());
assertThat(captor.getValue().subject()).isEqualTo("Welcome!");
```

## Parameterized Tests

Use `@ParameterizedTest` to run the same assertion over multiple inputs:

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.*;

@ParameterizedTest
@ValueSource(strings = {"", "  ", "\t"})
void isBlank_withBlankStrings_returnsTrue(String input) {
    assertTrue(StringUtils.isBlank(input));
}

@ParameterizedTest
@CsvSource({
    "alice@example.com, true",
    "not-an-email,      false",
    "missing@dot,       false"
})
void isValidEmail(String email, boolean expected) {
    assertEquals(expected, validator.isValid(email));
}

@ParameterizedTest
@MethodSource("invalidOrders")
void placeOrder_withInvalidOrder_throws(Order order) {
    assertThrows(ValidationException.class, () -> service.placeOrder(order));
}

static Stream<Order> invalidOrders() {
    return Stream.of(
        new Order(null),
        new Order(List.of()),
        new Order(List.of(new Item(null, -1)))
    );
}
```

## Lifecycle Hooks

```java
@BeforeAll  static void initOnce()  { /* runs once before all tests in the class */ }
@AfterAll   static void tearDown()  { /* runs once after all tests in the class  */ }
@BeforeEach void setUp()            { /* runs before each test                   */ }
@AfterEach  void cleanUp()          { /* runs after each test                    */ }
```

Use `@BeforeEach` for object creation and `@BeforeAll` (static) for expensive setup like database connections or server startup.

## Test Isolation and Best Practices

- **One logical assertion per test.** Multiple `assert*` calls are fine when they verify one behavior (`assertAll` helps here). Don't combine unrelated checks.
- **Tests must not share mutable state.** Reinitialize objects in `@BeforeEach`, never as static fields.
- **Avoid logic in tests.** No `if`/`for`/`switch` — if you need multiple cases, use `@ParameterizedTest`.
- **Test behavior, not implementation.** Avoid asserting on private state; test through the public API. Only mock collaborators, not internals.
- **Keep tests fast.** Unit tests should run in milliseconds. Push slow I/O behind an interface and mock it.
- **Use `@DisplayName` for complex scenarios** where the method name would be unwieldy:
  ```java
  @Test
  @DisplayName("Order total includes tax when shipping to California")
  void test() { ... }
  ```

## Organizing Tests

Group related tests with `@Nested`:

```java
class UserServiceTest {

    @Nested
    class WhenCreatingUser {
        @Test void validInput_persistsUser() { ... }
        @Test void duplicateEmail_throwsConflict() { ... }
    }

    @Nested
    class WhenDeletingUser {
        @Test void existingUser_marksDeleted() { ... }
        @Test void unknownId_throwsNotFound() { ... }
    }
}
```

Tag tests for selective execution:

```java
@Tag("slow")
@Test
void heavyIntegrationTest() { ... }
```

Run tagged subset: `mvn test -Dgroups=slow` or configure in `build.gradle`.

## Running Tests

```bash
# Maven
mvn test
mvn test -Dtest=OrderServiceTest          # single class
mvn test -Dtest=OrderServiceTest#placeOrder_* # single method pattern

# Gradle
./gradlew test
./gradlew test --tests "com.example.OrderServiceTest"
./gradlew test --tests "*.OrderServiceTest.placeOrder_*"
```

## Common Pitfalls

- **Mocking concrete classes**: prefer mocking interfaces when possible; concrete class mocking can be brittle.
- **`@Mock` without `@ExtendWith(MockitoExtension.class)`**: mocks won't be injected. Always add the extension.
- **Asserting on `toString()` output**: fragile. Assert on the actual fields instead.
- **Relying on test execution order**: JUnit does not guarantee order. If state must carry over, use `@TestMethodOrder` deliberately and document why.
