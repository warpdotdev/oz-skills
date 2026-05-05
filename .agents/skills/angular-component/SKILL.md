---
name: angular-component
description: Author idiomatic modern Angular components using standalone components, signals, the new control flow, and TypeScript with strong accessibility, RxJS, and testing defaults. Use when the user asks to create, scaffold, refactor, or review an Angular component, directive, pipe, service, or feature module.
license: MIT
---

# Angular Component Authoring

Write modern Angular components (Angular 17+) that are typed, accessible, signal-driven, and idiomatic. This skill captures the conventions to apply whenever generating new components or refactoring existing ones.

> Note on naming: today "Angular" means Angular 2+ (the TypeScript framework). The legacy 1.x framework ("AngularJS") is end-of-life. Default to modern Angular unless the repo clearly uses AngularJS — see the AngularJS section at the bottom for that case.

## When to Use

- The user asks for a new Angular component, directive, pipe, service, route, or feature module.
- The user wants an existing component refactored, split, typed, migrated to standalone, migrated to signals, or made accessible.
- A skill or task requires producing Angular code inside a CLI-based Angular project (Angular CLI, Nx, Analog).

## Workflow

1. **Detect project conventions.** Before writing code, inspect the repo to identify:
   - Angular major version (`package.json` → `@angular/core`). Capabilities differ across 14, 15, 16, 17, 18+.
   - Standalone vs. NgModule layout (`bootstrapApplication` in `main.ts` and `standalone: true` on components signal modern).
   - Signals vs. RxJS-only state (`signal`, `computed`, `effect` imports from `@angular/core`).
   - Control flow: legacy `*ngIf`/`*ngFor` vs. new `@if`/`@for`/`@switch` (Angular 17+).
   - Build setup: Angular CLI, Nx workspace, esbuild vs. Webpack, SSR (Angular Universal/Hydration).
   - Styling: component styles, SCSS, Tailwind, Angular Material, CDK, Spectrum, PrimeNG.
   - State libraries: NgRx (`@ngrx/store`, `@ngrx/signals`), NGXS, Akita, plain services with signals.
   - Testing: Karma + Jasmine (legacy) vs. Jest, Cypress/Playwright for E2E, `@testing-library/angular`.
2. **Match the existing style.** New code should look like it was written by the same author as the surrounding code. Do not introduce new libraries, formatters, or patterns without a reason.
3. **Design the component API first.** Decide inputs, outputs, content projection, exposed methods, and whether the component is presentational (dumb) or a smart container.
4. **Implement with standalone + signals.** On Angular 17+, default to standalone components, signal inputs/outputs/queries, and the new control flow.
5. **Wire up accessibility.** Use semantic HTML, ARIA where needed, and the Angular CDK a11y utilities (`FocusTrap`, `LiveAnnouncer`, `cdkTrapFocus`).
6. **Add tests** matching the project's framework.
7. **Validate.** Run the project's lint, type-check (`tsc --noEmit` via CLI build), and test commands (`ng test`, `ng lint`, `nx affected`, etc.).

## Component Guidelines

### File and Naming Layout

- Follow the Angular style guide: kebab-case file names with type suffixes — `user-card.component.ts`, `user-card.component.html`, `user-card.component.scss`, `user-card.component.spec.ts`.
- Class names are PascalCase with a type suffix: `UserCardComponent`, `AuthService`, `HighlightDirective`, `BytesPipe`.
- Selectors use a project-specific kebab-case prefix (`app-user-card`, `mw-user-card`); reuse the prefix already in the repo.
- One concern per file: a component, directive, pipe, or service per `.ts` file.
- Co-locate related files in a feature folder. Use `index.ts` barrels only if the repo already does.

### Standalone Components and Bootstrapping

- Default to standalone:

  ```ts path=null start=null
  @Component({
    selector: 'app-user-card',
    standalone: true,
    imports: [CommonModule, RouterLink, MatButtonModule],
    templateUrl: './user-card.component.html',
    styleUrls: ['./user-card.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
  })
  export class UserCardComponent { /* ... */ }
  ```

- Bootstrap with `bootstrapApplication(AppComponent, { providers: [...] })` and configure providers with `provideRouter`, `provideHttpClient(withFetch())`, `provideAnimationsAsync()`, etc.
- Only fall back to `NgModule` when the codebase still uses modules; even then, keep new components standalone where possible.
- Always set `changeDetection: ChangeDetectionStrategy.OnPush`. Combined with signals, it gives the best performance and predictability.

### Inputs, Outputs, Queries (Signals API, Angular 17.1+/17.3+)

- Use signal inputs and signal outputs:

  ```ts path=null start=null
  import { Component, computed, input, output } from '@angular/core';

  @Component({ /* ... */ })
  export class UserCardComponent {
    readonly userId = input.required<string>();
    readonly variant = input<'compact' | 'full'>('full');
    readonly selected = output<string>();

    readonly heading = computed(() => `User ${this.userId()}`);

    onPick() {
      this.selected.emit(this.userId());
    }
  }
  ```

- Use `viewChild`, `viewChildren`, `contentChild`, `contentChildren` (signal queries) instead of decorator-based `@ViewChild`/`@ContentChild` on Angular 17.2+.
- Use `model()` for two-way bindings (`[(value)]`) instead of pairing an `Input`/`Output`.
- Avoid mutating inputs. Mirror them into local signals via `linkedSignal` or a `computed` if you need derived state.

### Templates and Control Flow

- On Angular 17+, use the built-in control flow:

  ```html path=null start=null
  @if (user(); as u) {
    <article [attr.aria-labelledby]="'user-' + u.id">
      <h2 [id]="'user-' + u.id">{{ u.name }}</h2>
    </article>
  } @else {
    <p role="status">No user selected.</p>
  }

  @for (item of items(); track item.id) {
    <li>{{ item.label }}</li>
  } @empty {
    <li>No items.</li>
  }
  ```

- Always provide a `track` expression in `@for` (or `trackBy` in `*ngFor`); it is required by the new syntax and prevents needless DOM churn.
- Prefer the new `@switch` over chained `*ngIf` ladders.
- Use the `async` pipe (or the `toSignal`/`signal` pair) to consume observables instead of subscribing manually in components.

### Reactivity: Signals + RxJS

- Treat signals as the default for synchronous component state and derived values; treat RxJS as the default for async streams (HTTP, WebSockets, debounced inputs).
- Bridge with `toSignal(observable$, { initialValue })` and `toObservable(signalRef)` (from `@angular/core/rxjs-interop`).
- Prefer `computed` for derived state. Use `effect` only for side effects (logging, imperative DOM, focus); do not use `effect` to set other signals.
- Always unsubscribe from manual RxJS subscriptions: use `takeUntilDestroyed()` from `@angular/core/rxjs-interop` or scope work to `inject(DestroyRef)`.

### Dependency Injection and Services

- Inject via `inject(MyService)` inside class field initializers when on Angular 14+ — it's terser and works with abstract base classes.
- Mark stateless services with `@Injectable({ providedIn: 'root' })`; for feature-scoped services, provide them at the route or component level.
- Prefer small, focused services over giant facades. Keep components free of business logic; delegate to services or signal stores.

### State Management

- For component-local state: signals + computed.
- For feature-level shared state: a service that exposes signals (or `@ngrx/signals` `signalStore`).
- For app-wide complex flows (effects, time-travel debugging, large teams): NgRx Store + Effects, or Component Store for medium scope.
- Always treat state as immutable. Mutate via `signal.update(prev => ...)`, never by reassigning fields on the underlying object.

### Forms

- Use **Reactive Forms** (`FormGroup`, `FormControl`, `FormArray`) for non-trivial forms; use Template-Driven only for the simplest cases.
- Type forms with `FormGroup<{ email: FormControl<string>; ... }>` to get end-to-end type safety.
- Co-locate validators with the form definition; extract reusable ones into pure functions.
- Bind a single `ControlValueAccessor` per custom form input component.

### HTTP and Async

- Use `HttpClient` (configured via `provideHttpClient(withFetch())` for modern Fetch-based requests).
- Type response shapes; never leave HTTP calls returning `Observable<any>`.
- Debounce/cancel with `debounceTime`, `switchMap`, `exhaustMap` per the operation's semantics.
- Prefer Angular's `httpResource`/`resource` APIs (Angular 19+) when available for declarative async state.

### Accessibility

- Use semantic HTML first (`<button>`, `<a>`, `<nav>`, `<header>`, `<label>`, `<dialog>`).
- Lean on `@angular/cdk/a11y`: `FocusTrap`, `LiveAnnouncer`, `FocusMonitor`, `cdkTrapFocus`, `cdkAriaLive`.
- Bind ARIA attributes with `[attr.aria-...]`. Never set ARIA on a native element that already has the same semantic.
- Manage focus on route changes (use the Router's `scrollPositionRestoration` and a focus-management strategy) and on dialog open/close.
- Respect `prefers-reduced-motion`; gate Angular Animations accordingly or use the no-op animations provider.

### Performance

- Always use `OnPush` change detection.
- Track items in `@for`/`*ngFor`; never let Angular fall back to identity tracking on large lists.
- Use `@defer` blocks (Angular 17+) for non-critical UI to lazy-load components, with `@placeholder`, `@loading`, and `@error` slots.
- Use `provideExperimentalZonelessChangeDetection()` (or stable variants in newer versions) when the codebase has adopted zoneless.
- Lazy-load routes with `loadComponent` / `loadChildren`. Keep initial bundle small.
- Avoid `function` calls in templates that recompute heavy work each CD cycle; precompute into a `computed`/`signal`.

### Styling

- Match the repo's styling system (component styles, SCSS, Tailwind, Material theming).
- Default to component-scoped styles. Use `:host`, `:host-context()`, and `::ng-deep` only when piercing scope is genuinely needed (and prefer alternatives to `::ng-deep`, which is deprecated).
- For Angular Material, use the theming API (`mat.define-theme`, `mat.core`, `mat.all-component-themes`); do not override Material classes globally.

### Testing

- Mirror the project's framework. Common stacks:
  - **Karma + Jasmine** (default CLI) — `TestBed`, `ComponentFixture`, `@angular/common/testing` helpers.
  - **Jest** (Nx default) with `jest-preset-angular`.
  - **Vitest** for some Nx setups.
  - **`@testing-library/angular`** for behavior-first tests on top of any of the above.
  - **Cypress/Playwright** for E2E.
- Test behavior, not implementation: query by accessible role/name, simulate user events, assert on what users see.
- Cover the main happy path plus at least one edge case (loading, error, empty, disabled).
- For services and signal-based logic, write plain TS unit tests; reach for `TestBed` only when DI is genuinely needed.

## Example: Standalone Signal-Based Button

```ts path=null start=null
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  input,
  output,
} from '@angular/core';

type ButtonVariant = 'primary' | 'secondary' | 'ghost';

@Component({
  selector: 'app-button',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button
      type="button"
      [class]="classes()"
      [disabled]="disabled() || isLoading()"
      [attr.aria-busy]="isLoading() ? true : null"
      (click)="onClick($event)"
    >
      <ng-content select="[icon]" />
      <span class="btn__label">
        <ng-content />
      </span>
    </button>
  `,
  styleUrls: ['./button.component.scss'],
})
export class ButtonComponent {
  readonly variant = input<ButtonVariant>('primary');
  readonly isLoading = input(false);
  readonly disabled = input(false);
  readonly clicked = output<MouseEvent>();

  readonly classes = computed(() => `btn btn--${this.variant()}`);

  onClick(event: MouseEvent) {
    if (this.disabled() || this.isLoading()) return;
    this.clicked.emit(event);
  }
}
```

## Example: Data-Fetching Component With Signals + HttpClient

```ts path=null start=null
import { HttpClient } from '@angular/common/http';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  input,
} from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { catchError, map, of, startWith, switchMap } from 'rxjs';
import { toObservable } from '@angular/core/rxjs-interop';

interface User {
  id: string;
  name: string;
  email: string;
}

type LoadState =
  | { status: 'pending' }
  | { status: 'success'; user: User }
  | { status: 'error'; message: string };

@Component({
  selector: 'app-user-card',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @switch (state().status) {
      @case ('pending') {
        <p role="status">Loading user…</p>
      }
      @case ('error') {
        <div role="alert">
          <p>Couldn't load user: {{ state().message }}</p>
        </div>
      }
      @case ('success') {
        <article [attr.aria-labelledby]="'user-' + state().user.id">
          <h2 [id]="'user-' + state().user.id">{{ state().user.name }}</h2>
          <a [href]="'mailto:' + state().user.email">{{ state().user.email }}</a>
        </article>
      }
    }
  `,
})
export class UserCardComponent {
  private readonly http = inject(HttpClient);

  readonly userId = input.required<string>();

  private readonly userId$ = toObservable(this.userId);

  readonly state = toSignal<LoadState>(
    this.userId$.pipe(
      switchMap((id) =>
        this.http.get<User>(`/api/users/${id}`).pipe(
          map((user) => ({ status: 'success', user }) as LoadState),
          catchError((err) =>
            of({ status: 'error', message: err.message } as LoadState),
          ),
          startWith({ status: 'pending' } as LoadState),
        ),
      ),
    ),
    { initialValue: { status: 'pending' } as LoadState },
  );
}
```

## Example: Service + `takeUntilDestroyed`

```ts path=null start=null
import { DestroyRef, Injectable, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class TickerService {
  private readonly destroyRef = inject(DestroyRef);
  readonly seconds = signal(0);

  start() {
    interval(1000)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.seconds.update((s) => s + 1));
  }
}
```

## Anti-Patterns to Avoid

- Subscribing in components without `takeUntilDestroyed`/`async` pipe — leads to leaks.
- Using `*ngIf="obs | async as v"` chains everywhere instead of `toSignal` + `@if`.
- Mutating `@Input()`-bound objects in place; treat inputs as read-only.
- Putting business logic in components instead of services or signal stores.
- Calling functions in templates that do non-trivial work on every change detection cycle.
- Using `any` for HTTP response types.
- Reaching into child components with `@ViewChild` to drive state instead of `@Input`/`@Output`/`model`.
- Mixing NgModules and standalone for new components when the project has migrated.
- Forgetting `track` in `@for` (Angular 17+ requires it).
- Using `::ng-deep` for theming when component styling, CSS variables, or Material's theming API would do.

## Validation Checklist

Before finishing the change, confirm:

- Project builds and type-checks (`ng build`, `nx build`, or repo equivalent — never just `tsc --noEmit` for a project with Angular templates, which need the template type-checker).
- Lint passes (`ng lint`, `eslint`, or repo equivalent).
- Tests for the component pass and meaningfully exercise its behavior.
- Accessibility basics: keyboard reachable, labeled, no Angular dev-mode `aria-*` warnings, focus management for dialogs/routes.
- No new dependencies were added without justification.
- Public API (inputs, outputs, exposed methods) is documented via types and, where appropriate, JSDoc on non-obvious entries.

## AngularJS (1.x) — Legacy Note

If the project is genuinely AngularJS 1.x (look for `angular.module(...)`, `ng-app`, `ng-controller`, `$scope`, `angular.json` absent):

- Use `.component()` (not `.directive()` or `.controller()` with `$scope`) for new components.
- Define a `controller`, `bindings` (`<` for one-way, `&` for callbacks, `@` for strings), and a template.
- Keep components small; avoid `$scope` mutation outside the controller.
- Note that AngularJS reached end-of-life in January 2022. Recommend migrating to modern Angular before adding significant new features.

```js path=null start=null
angular.module('app').component('userCard', {
  bindings: {
    userId: '<',
    onSelect: '&',
  },
  controller: function () {
    const ctrl = this;
    ctrl.pick = () => ctrl.onSelect({ id: ctrl.userId });
  },
  template: `
    <article ng-attr-aria-labelledby="user-{{ $ctrl.userId }}">
      <h2 id="user-{{ $ctrl.userId }}">User {{ $ctrl.userId }}</h2>
      <button type="button" ng-click="$ctrl.pick()">Select</button>
    </article>
  `,
});
```
