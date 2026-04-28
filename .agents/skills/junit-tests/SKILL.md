---
name: junit-tests
description: Write focused JUnit tests for Java projects. Use when creating, reviewing, or improving JUnit 4 or JUnit 5 tests, including assertions, fixtures, parameterized tests, mocks, and build-tool test commands.
license: MIT
---

# JUnit Testing

Write tests that document observable behavior and fail for useful reasons. Prefer small, deterministic tests that exercise public APIs over tests that mirror implementation details.

## Workflow

1. Identify the project’s test stack before editing:
   - Check `pom.xml`, `build.gradle`, `build.gradle.kts`, or existing tests for JUnit 4 vs. JUnit 5.
   - Reuse the project’s assertion library, mocking library, package layout, naming conventions, and test-source root.
   - If both JUnit versions are present, match nearby tests unless the task explicitly asks for migration.
2. Pick the narrowest behavior to test:
   - Cover the success path, important edge cases, and failure behavior.
   - Prefer one behavioral reason to fail per test.
   - Avoid testing private methods directly; test through public behavior.
3. Arrange test data clearly:
   - Use builders, fixtures, or helper methods when setup noise hides the behavior.
   - Keep shared setup minimal so each test remains readable in isolation.
   - Use `@BeforeEach` or `@Before` only for setup that is genuinely common to every test.
4. Assert outcomes precisely:
   - Assert returned values, state changes, thrown exceptions, and relevant interactions.
   - Avoid weak assertions such as only checking non-null values when exact values are known.
   - Include assertion messages only when they clarify a non-obvious failure.
5. Run the smallest relevant test command first, then broaden if needed:
   - Maven: `mvn test -Dtest=ClassNameTest`
   - Gradle: `./gradlew test --tests 'com.example.ClassNameTest'`
   - If targeted commands are unavailable, use the project’s documented test command.

## JUnit 5 Patterns

Use JUnit Jupiter imports for new JUnit 5 tests:

```java
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class PriceCalculatorTest {
    @Test
    void appliesDiscountToEligibleCustomer() {
        PriceCalculator calculator = new PriceCalculator();

        Money total = calculator.totalFor(new Customer(true), Money.of("10.00"));

        assertEquals(Money.of("9.00"), total);
    }

    @Test
    void rejectsNegativeSubtotal() {
        PriceCalculator calculator = new PriceCalculator();

        IllegalArgumentException thrown = assertThrows(
            IllegalArgumentException.class,
            () -> calculator.totalFor(new Customer(false), Money.of("-1.00"))
        );

        assertEquals("subtotal must be non-negative", thrown.getMessage());
    }
}
```

For parameterized coverage, use `@ParameterizedTest` when the same behavior should hold for multiple inputs:

```java
import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class SlugifierTest {
    @ParameterizedTest
    @CsvSource({
        "Hello World, hello-world",
        " multiple   spaces , multiple-spaces",
        "Already-Slugged, already-slugged"
    })
    void normalizesTitles(String title, String expectedSlug) {
        assertEquals(expectedSlug, Slugifier.slugify(title));
    }
}
```

## JUnit 4 Patterns

Use JUnit 4 imports only when the project is already on JUnit 4:

```java
import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class PriceCalculatorTest {
    @Test
    public void appliesDiscountToEligibleCustomer() {
        PriceCalculator calculator = new PriceCalculator();

        Money total = calculator.totalFor(new Customer(true), Money.of("10.00"));

        assertEquals(Money.of("9.00"), total);
    }
}
```

Prefer `ExpectedException` or explicit try/catch assertions only if that is the existing project style. Otherwise use `assertThrows` when available.

## Mocking and Interaction Tests

- Mock external systems, clocks, network clients, repositories, and slow collaborators.
- Do not mock simple value objects or the class under test.
- Verify interactions only when the interaction is the behavior, such as publishing an event or calling an external gateway.
- Prefer dependency injection over static/global state changes.

```java
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.Test;

class InvoiceServiceTest {
    @Test
    void publishesInvoiceCreatedEvent() {
        InvoiceRepository repository = mock(InvoiceRepository.class);
        EventPublisher publisher = mock(EventPublisher.class);
        InvoiceService service = new InvoiceService(repository, publisher);
        Invoice invoice = new Invoice("inv-123");

        when(repository.save(invoice)).thenReturn(invoice);

        service.create(invoice);

        verify(publisher).publish(new InvoiceCreated("inv-123"));
    }
}
```

## Naming Guidance

Use the naming style already present in nearby tests. If there is no local convention, prefer descriptive method names such as:

- `returnsEmptyListWhenNoOrdersExist`
- `throwsWhenEmailIsMalformed`
- `preservesExistingMetadataDuringUpdate`

Avoid vague names like `testCreate`, `validInput`, or `shouldWork`.

## Common Pitfalls

- Mixing JUnit 4 and JUnit 5 imports in the same test class.
- Adding sleeps instead of controlling time with a fake clock or await utility.
- Asserting implementation details that make refactors unnecessarily expensive.
- Overusing shared mutable fixtures that make test order matter.
- Leaving generated tests unrun or running only the full suite when a targeted command would reveal failures faster.
