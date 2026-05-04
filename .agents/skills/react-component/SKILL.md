---
name: react-component
description: Author idiomatic, type-safe React components that follow modern best practices around composition, hooks, accessibility, and performance. Use when the user asks to create, scaffold, refactor, or review a React component, page, or UI primitive.
license: MIT
---

# React Component Authoring

Write modern React components that are typed, accessible, composable, and performant. This skill captures the conventions to apply whenever generating new components or refactoring existing ones.

## When to Use

- The user asks for a new React component, page, layout, hook, or context provider.
- The user wants an existing component refactored, split, typed, or made accessible.
- A skill or task requires producing JSX/TSX inside a React (Next.js, Remix, Vite, CRA) project.

## Workflow

1. **Detect project conventions.** Before writing code, inspect the repo to identify:
   - Language: JavaScript vs. TypeScript (`tsconfig.json`, `.tsx` files).
   - Framework: Next.js (App Router vs. Pages), Remix, Vite, CRA, React Native.
   - Styling: CSS Modules, Tailwind, styled-components, vanilla-extract, Emotion.
   - State libraries: Redux Toolkit, Zustand, Jotai, React Query, SWR, Apollo.
   - Existing component patterns (file names, default vs. named exports, folder layout, prop typing style, test framework).
2. **Match the existing style.** New code should look like it was written by the same author as the surrounding code. Do not introduce new libraries, formatters, or patterns without a reason.
3. **Design the component API first.** Decide props, defaults, ref forwarding, polymorphism, and whether the component is controlled, uncontrolled, or both. Prefer narrow, explicit prop types over loose `any`/`object` shapes.
4. **Implement with hooks and composition.** Use function components plus hooks; only use class components if the codebase already does.
5. **Wire up accessibility.** Use semantic HTML, labels, roles, and keyboard handling from the start instead of bolting them on later.
6. **Add tests and stories** when the project has them. Match the existing test framework (Jest, Vitest, Testing Library, Playwright, Cypress) and Storybook setup.
7. **Validate.** Run the project's lint, type-check, and test commands before declaring the change done.

## Component Guidelines

### File and Naming Layout

- One component per file; file name matches component name (`UserCard.tsx` exports `UserCard`).
- Co-locate styles, tests, and stories: `Button/Button.tsx`, `Button/Button.module.css`, `Button/Button.test.tsx`, `Button/Button.stories.tsx`.
- Use `index.ts` only when the project already does; avoid deep barrel files that hurt tree-shaking.
- Use PascalCase for components, camelCase for hooks (`useThing`), and kebab/camel case for non-component utility files following the existing repo.

### Props and Types

- Prefer TypeScript. Define `Props` as a named type or interface next to the component.
- Extend native element props when the component renders a single DOM element:

  ```tsx path=null start=null
  type ButtonProps = React.ComponentPropsWithoutRef<"button"> & {
    variant?: "primary" | "secondary" | "ghost";
    isLoading?: boolean;
  };
  ```

- Forward refs whenever the component renders a focusable or measurable DOM node:

  ```tsx path=null start=null
  export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    function Button({ variant = "primary", isLoading, children, ...rest }, ref) {
      return (
        <button ref={ref} data-variant={variant} aria-busy={isLoading} {...rest}>
          {children}
        </button>
      );
    },
  );
  ```

- Avoid boolean prop explosions. Group related options into a discriminated union or a single `variant`/`size` prop.
- Default props via destructuring defaults, not `defaultProps` (deprecated for function components).
- Do not type children as `React.FC` (it has been discouraged); use explicit `children: React.ReactNode` when needed.

### Hooks

- Always call hooks at the top level; never inside conditions, loops, or callbacks.
- Keep effects narrow. Each `useEffect` should have one job and an accurate dependency array.
- Reach for these hooks in this order before writing custom abstractions: `useState`, `useReducer`, `useMemo`, `useCallback`, `useRef`, `useEffect`, `useLayoutEffect`, `useId`, `useSyncExternalStore`.
- Extract reusable behavior into `useFoo` hooks once it's shared between two components or hard to test inline.
- Avoid `useEffect` for derived state—compute values during render or with `useMemo`.

### State Management

- Start with local `useState`/`useReducer`. Lift state only when two siblings need it.
- For server state, prefer the project's data-fetching library (React Query, SWR, RTK Query, Apollo) instead of ad-hoc `useEffect` + `fetch`.
- For cross-cutting client state, use Context with care: split contexts by update frequency to avoid re-rendering unrelated subtrees.
- Memoize context values with `useMemo` and stable callbacks with `useCallback` when the consumer tree is large.

### Rendering and Performance

- Provide stable, unique `key` props on lists; never use array index when items can reorder.
- Avoid creating new object/array/function literals in JSX when they're passed to memoized children.
- Reach for `React.memo`, `useMemo`, and `useCallback` only when profiling or props shape suggests a real re-render problem—not by default.
- Use code-splitting (`React.lazy` + `Suspense`, dynamic imports) for large, route-level components.
- Use `useTransition` / `useDeferredValue` for expensive, non-urgent updates in React 18+ projects.

### Server vs. Client Components (Next.js App Router)

- Default to Server Components. Add `"use client"` only when the file uses state, effects, refs, browser APIs, or event handlers.
- Keep client components small and leaf-level; pass server-rendered children through as props/`children` instead of converting parents to client.
- Never import server-only modules (e.g., `fs`, secrets) from a client component.

### Styling

- Match the repo's styling system. Don't introduce a new one without an explicit ask.
- For Tailwind: keep class lists readable, extract repeated combinations into a component or a `cva`/`clsx` helper rather than ad-hoc string concat.
- For CSS Modules / styled-components: keep selectors scoped to the component; avoid global styles outside of explicit reset/theme files.

### Accessibility

- Use semantic HTML first (`button`, `a`, `nav`, `header`, `label`, `dialog`).
- Every interactive non-button element needs a role, `tabIndex`, and keyboard handlers; prefer just using `<button>` instead.
- Associate every form control with a `<label>` (or `aria-labelledby`/`aria-label`).
- Manage focus for dialogs, menus, and route changes; trap focus in modals and restore it on close.
- Provide `alt` text for meaningful images and `alt=""` for decorative ones.
- Respect `prefers-reduced-motion` for animations.
- See the `web-accessibility-audit` skill for deeper WCAG guidance.

### Error and Loading States

- Render explicit loading, empty, and error states; do not leave components blank while data is pending.
- Wrap risky subtrees in an Error Boundary (class component or library like `react-error-boundary`).
- Surface user-facing error messages from a single source; avoid duplicating retry logic in every component.

### Testing

- Mirror the project's framework. Most modern repos use **React Testing Library** + Jest/Vitest.
- Test behavior, not implementation: query by accessible role/name, simulate user events with `@testing-library/user-event`, and assert on what users see.
- Cover the main happy path plus at least one edge case (loading, error, empty, disabled).
- For hooks, use `renderHook` from `@testing-library/react`.

## Example: Typed, Accessible Button

```tsx path=null start=null
import * as React from "react";
import clsx from "clsx";

type ButtonVariant = "primary" | "secondary" | "ghost";

type ButtonProps = React.ComponentPropsWithoutRef<"button"> & {
  variant?: ButtonVariant;
  isLoading?: boolean;
  leadingIcon?: React.ReactNode;
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(
    {
      variant = "primary",
      isLoading = false,
      leadingIcon,
      className,
      children,
      disabled,
      ...rest
    },
    ref,
  ) {
    return (
      <button
        ref={ref}
        className={clsx("btn", `btn--${variant}`, className)}
        disabled={disabled || isLoading}
        aria-busy={isLoading || undefined}
        {...rest}
      >
        {leadingIcon ? (
          <span aria-hidden="true" className="btn__icon">
            {leadingIcon}
          </span>
        ) : null}
        <span className="btn__label">{children}</span>
      </button>
    );
  },
);
```

## Example: Data-Fetching Component With React Query

```tsx path=null start=null
import { useQuery } from "@tanstack/react-query";

type User = { id: string; name: string; email: string };

async function fetchUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error("Failed to load user");
  return res.json();
}

export function UserCard({ userId }: { userId: string }) {
  const { data, isPending, isError, error, refetch } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => fetchUser(userId),
  });

  if (isPending) return <p role="status">Loading user…</p>;
  if (isError) {
    return (
      <div role="alert">
        <p>Couldn't load user: {error.message}</p>
        <button type="button" onClick={() => refetch()}>
          Try again
        </button>
      </div>
    );
  }

  return (
    <article aria-labelledby={`user-${data.id}-name`}>
      <h2 id={`user-${data.id}-name`}>{data.name}</h2>
      <a href={`mailto:${data.email}`}>{data.email}</a>
    </article>
  );
}
```

## Example: Custom Hook

```tsx path=null start=null
import * as React from "react";

export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = React.useState(value);

  React.useEffect(() => {
    const handle = window.setTimeout(() => setDebounced(value), delayMs);
    return () => window.clearTimeout(handle);
  }, [value, delayMs]);

  return debounced;
}
```

## Anti-Patterns to Avoid

- Using array indexes as `key` for reorderable lists.
- Mutating state directly (`state.items.push(x)`) instead of producing new values.
- Putting derived data in `useState` and syncing it via `useEffect`.
- Wrapping every component in `React.memo` "just in case".
- Spreading unknown props onto DOM nodes (`<div {...props} />`) without a typed allow-list.
- Hand-rolling clickable `<div>`s instead of `<button>` or `<a>`.
- Mixing data fetching, business logic, and presentation in one mega-component—split into container/presenter or extract hooks.
- Importing from deep relative paths (`../../../../`) when path aliases exist.

## Validation Checklist

Before finishing the change, confirm:

- Component compiles and type-checks (`tsc --noEmit` or the repo's script).
- Lint passes (`eslint`, `biome`, etc., per the repo).
- Tests for the component pass and meaningfully exercise its behavior.
- Accessibility basics: keyboard reachable, labeled, no role/aria warnings in dev tools.
- No new dependencies were added without justification.
- Public API (props, exports) is documented via types and, where appropriate, JSDoc on non-obvious props.
