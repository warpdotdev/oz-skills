---
name: vue-component
description: Author idiomatic Vue 3 single-file components using the Composition API, `<script setup>`, and TypeScript with strong accessibility, composability, and testing defaults. Use when the user asks to create, scaffold, refactor, or review a Vue component, page, composable, or UI primitive.
license: MIT
---

# Vue Component Authoring

Write modern Vue 3 single-file components (SFCs) that are typed, accessible, composable, and idiomatic. This skill captures the conventions to apply whenever generating new components or refactoring existing ones.

## When to Use

- The user asks for a new Vue component, page, layout, composable, or store module.
- The user wants an existing component refactored, split, typed, migrated from Options API to Composition API, or made accessible.
- A skill or task requires producing `.vue` SFCs inside a Vue 3 (Vite, Nuxt 3, Quasar, VitePress) project.

## Workflow

1. **Detect project conventions.** Before writing code, inspect the repo to identify:
   - Vue version: 3.x (Composition API) vs. legacy 2.x (Options API).
   - Language: JavaScript vs. TypeScript (`tsconfig.json`, `lang="ts"` in SFCs).
   - Framework: Vite, Nuxt 3, Quasar, VitePress, Vue CLI.
   - Styling: scoped `<style>`, CSS Modules, Tailwind, UnoCSS, SCSS/Sass, Pinia-styled component libraries.
   - State libraries: Pinia (preferred for Vue 3), Vuex (legacy), VueUse, TanStack Query (`@tanstack/vue-query`).
   - Existing component patterns (file naming case, default vs. named export style, folder layout, prop typing, test framework).
2. **Match the existing style.** New code should look like it was written by the same author as the surrounding code. Do not introduce new libraries, formatters, or patterns without a reason.
3. **Design the component API first.** Decide props, emits, slots, exposed methods, and whether the component is controlled (`v-model`), uncontrolled, or both. Prefer narrow, explicit prop types over loose `any`/`object` shapes.
4. **Implement with `<script setup>` and Composition API.** Only fall back to the Options API if the codebase already uses it.
5. **Wire up accessibility.** Use semantic HTML, labels, roles, and keyboard handling from the start.
6. **Add tests and stories** when the project has them. Match the existing test framework (Vitest, Jest, Vue Test Utils, Cypress, Playwright) and Storybook/Histoire setup.
7. **Validate.** Run the project's lint, type-check (`vue-tsc --noEmit`), and test commands before declaring the change done.

## Component Guidelines

### File and Naming Layout

- Use multi-word, PascalCase component file names (`UserCard.vue`), per the official Vue style guide. Avoid single-word names like `Card.vue` for shared components.
- Co-locate related files: `UserCard/UserCard.vue`, `UserCard/UserCard.test.ts`, `UserCard/UserCard.stories.ts`.
- Match the repo's casing in templates: PascalCase in `<template>` for SFCs (e.g., `<UserCard />`) is preferred; kebab-case (`<user-card />`) is fine if the existing code uses it consistently.
- Prefer named exports of `defineComponent`/composables and rely on the SFC's default export for the component itself.

### `<script setup>` and Composition API

- Default to `<script setup lang="ts">`. It removes the boilerplate of `setup()` and gives better TS inference.
- Use `defineProps`, `defineEmits`, `defineSlots`, `defineModel`, `defineExpose`, and `withDefaults` (Vue 3.3+ supports `defineModel`).
- Do not destructure reactive objects (`reactive(...)`) or props in older Vue versions; in Vue 3.5+, prop destructuring is reactive — match the version in use.
- Type props with a generic on `defineProps`:

  ```vue path=null start=null
  <script setup lang="ts">
  type ButtonVariant = 'primary' | 'secondary' | 'ghost'

  const props = withDefaults(
    defineProps<{
      variant?: ButtonVariant
      isLoading?: boolean
    }>(),
    { variant: 'primary', isLoading: false },
  )

  const emit = defineEmits<{
    (e: 'click', event: MouseEvent): void
  }>()
  </script>
  ```

- Type emits with the call-signature form so payloads are checked at the call site.
- Use `defineModel` for two-way binding instead of manual `modelValue` / `update:modelValue` plumbing when the project's Vue version supports it.

### Reactivity

- Reach for primitives in this order before custom abstractions: `ref`, `computed`, `reactive`, `shallowRef`, `watch`, `watchEffect`, `toRefs`, `toRef`.
- Prefer `ref` over `reactive` for simple values; use `reactive` for tightly grouped object state.
- Use `computed` for derived state — never recompute it inside `watch`/`watchEffect`.
- Use `watchEffect` for "run side effects when reactive deps change"; use `watch` when you need before/after values or lazy execution.
- Avoid mutating props. If a prop must drive local state, mirror it into a `ref` and `watch` the prop.
- Reach for VueUse (`@vueuse/core`) for common patterns (`useDebounce`, `useLocalStorage`, `useEventListener`, `useFocusTrap`) instead of hand-rolling them.

### Composables

- Extract reusable logic into `useFoo` composables under `src/composables/` (or the repo's equivalent) once it's shared between two components or hard to test inline.
- Composables return refs/reactive objects and computeds; avoid returning plain values that lose reactivity.
- Always clean up side effects (`addEventListener`, intervals, subscriptions) with `onScopeDispose` or `onBeforeUnmount`.

### Slots, Props, Emits

- Prefer slots over prop-driven content for layout flexibility (`<slot />`, named slots, scoped slots).
- Type scoped slots with `defineSlots<{ default(props: { item: Item }): any }>()`.
- Emit names should be kebab-case in templates and match emits-options exactly.
- Validate enum-like props with a TypeScript union or a `validator` function; document allowed values.

### State Management

- Start with local `ref`/`reactive`. Lift state via `provide`/`inject` only when two siblings need it within a subtree.
- For app-wide client state, use **Pinia** (Vue 3 default). Define stores with `defineStore` + setup syntax for ergonomics that match `<script setup>`.
- For server state, prefer the project's data-fetching library (TanStack Query for Vue, Nuxt's `useFetch`/`useAsyncData`, VueUse's `useFetch`) instead of ad-hoc `onMounted` + `fetch`.
- Inside Pinia stores, expose a small, explicit API (state, getters, actions); avoid leaking refs that callers can mutate directly.

### Performance

- Use stable, unique `:key` values on `v-for`; never use array index when items can reorder.
- Combine `v-for` and `v-if` on the same element only when filtering can't be done via a `computed` — Vue 3 evaluates `v-if` first, which usually means you should filter in a `computed` instead.
- Use `v-once`, `v-memo`, and `defineAsyncComponent` (with `Suspense`) for expensive subtrees and route-level code splitting.
- Reach for `shallowRef`/`shallowReactive` when storing large, externally-owned objects (e.g., chart instances, Mapbox handles) to avoid deep reactivity overhead.
- Use `<KeepAlive>` deliberately; it preserves component state across route changes but holds memory.

### Nuxt 3 Specifics

- Default to **server components / universal rendering**. Use `<ClientOnly>` to gate components that depend on `window`/`document`.
- Use auto-imports (`useFetch`, `useAsyncData`, `useState`, `useRuntimeConfig`) instead of manual imports unless the repo disables auto-import.
- Place components in `components/` for auto-registration; respect Nuxt's directory conventions (`pages/`, `layouts/`, `composables/`, `server/`).
- Never reach for `process.client`/`process.server` when `import.meta.client`/`import.meta.server` is available in the project's Nuxt version.

### Styling

- Match the repo's styling system. Don't introduce a new one without an explicit ask.
- Prefer `<style scoped>` for component-local CSS; use `:deep()` sparingly when piercing scope is required.
- For Tailwind/UnoCSS: keep class lists readable; extract repeated combinations into a component or a `cva`/`tv`/`clsx` helper rather than ad-hoc string concat.
- Avoid global selectors outside of explicit reset/theme files.

### Accessibility

- Use semantic HTML first (`button`, `a`, `nav`, `header`, `label`, `dialog`).
- Every interactive non-button element needs a role, `tabindex`, and keyboard handlers; prefer just using `<button>` or `<a>`.
- Associate every form control with a `<label>` (or `aria-labelledby`/`aria-label`).
- Manage focus for dialogs, menus, and route changes; trap focus in modals (e.g., `useFocusTrap` from VueUse) and restore it on close.
- Provide `alt` text for meaningful images and `alt=""` for decorative ones.
- Respect `prefers-reduced-motion` for transitions; gate `<Transition>` animations accordingly.

### Error and Loading States

- Render explicit loading, empty, and error states in templates; do not leave components blank while data is pending.
- Use `<Suspense>` with `defineAsyncComponent` for async setup boundaries; provide a fallback slot.
- Wrap risky subtrees with `onErrorCaptured` or a project-wide error boundary component.
- Surface user-facing error messages from a single source; avoid duplicating retry logic in every component.

### Testing

- Mirror the project's framework. Most modern repos use **Vitest** + **Vue Test Utils** (`@vue/test-utils`) and/or **Testing Library** (`@testing-library/vue`).
- Test behavior, not implementation: query by accessible role/name with Testing Library, simulate user events with `@testing-library/user-event`, and assert on what users see.
- Cover the main happy path plus at least one edge case (loading, error, empty, disabled).
- For composables, test them inside a tiny mounted component or with `withSetup` helpers; do not call lifecycle hooks outside of a component scope.
- For E2E, use Playwright or Cypress per the repo.

## Example: Typed, Accessible Button (`<script setup>`)

```vue path=null start=null
<script setup lang="ts">
type ButtonVariant = 'primary' | 'secondary' | 'ghost'

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariant
    isLoading?: boolean
    disabled?: boolean
  }>(),
  { variant: 'primary', isLoading: false, disabled: false },
)

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

function onClick(event: MouseEvent) {
  if (props.disabled || props.isLoading) return
  emit('click', event)
}
</script>

<template>
  <button
    type="button"
    :class="['btn', `btn--${variant}`]"
    :disabled="disabled || isLoading"
    :aria-busy="isLoading || undefined"
    @click="onClick"
  >
    <span v-if="$slots.icon" aria-hidden="true" class="btn__icon">
      <slot name="icon" />
    </span>
    <span class="btn__label">
      <slot />
    </span>
  </button>
</template>

<style scoped>
.btn { /* ... */ }
</style>
```

## Example: Data-Fetching Component With TanStack Query

```vue path=null start=null
<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { toRefs } from 'vue'

interface User {
  id: string
  name: string
  email: string
}

const props = defineProps<{ userId: string }>()
const { userId } = toRefs(props)

async function fetchUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`)
  if (!res.ok) throw new Error('Failed to load user')
  return res.json()
}

const { data, isPending, isError, error, refetch } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId.value),
})
</script>

<template>
  <p v-if="isPending" role="status">Loading user…</p>

  <div v-else-if="isError" role="alert">
    <p>Couldn't load user: {{ error?.message }}</p>
    <button type="button" @click="refetch()">Try again</button>
  </div>

  <article v-else-if="data" :aria-labelledby="`user-${data.id}-name`">
    <h2 :id="`user-${data.id}-name`">{{ data.name }}</h2>
    <a :href="`mailto:${data.email}`">{{ data.email }}</a>
  </article>
</template>
```

## Example: Composable

```ts path=null start=null
import { ref, watch, onScopeDispose, type Ref } from 'vue'

export function useDebouncedRef<T>(source: Ref<T>, delayMs: number): Ref<T> {
  const debounced = ref(source.value) as Ref<T>
  let handle: number | undefined

  const stop = watch(source, (value) => {
    if (handle !== undefined) window.clearTimeout(handle)
    handle = window.setTimeout(() => {
      debounced.value = value
    }, delayMs)
  })

  onScopeDispose(() => {
    if (handle !== undefined) window.clearTimeout(handle)
    stop()
  })

  return debounced
}
```

## Example: Pinia Store (Setup Style)

```ts path=null start=null
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubled = computed(() => count.value * 2)

  function increment() {
    count.value += 1
  }

  return { count, doubled, increment }
})
```

## Anti-Patterns to Avoid

- Mixing Options API and `<script setup>` in the same file.
- Mutating props directly instead of emitting an event or using `defineModel`.
- Using array index as `:key` for reorderable lists.
- Putting derived data in `ref`/`reactive` and syncing via `watch` instead of using `computed`.
- Combining `v-for` and `v-if` on the same element to filter — filter in a `computed` instead.
- Reaching into child components with `ref`/`defineExpose` to drive state instead of using props/emits/`v-model`.
- Hand-rolling clickable `<div>`s instead of `<button>` or `<a>`.
- Importing from deep relative paths (`../../../../`) when path aliases (`@/`, `~/`) are configured.
- Calling Vue lifecycle hooks (`onMounted`, etc.) inside a regular function instead of a component or composable scope.

## Validation Checklist

Before finishing the change, confirm:

- SFC compiles and type-checks (`vue-tsc --noEmit` or the repo's script).
- Lint passes (`eslint`, `oxlint`, `biome`, etc., per the repo).
- Tests for the component pass and meaningfully exercise its behavior.
- Accessibility basics: keyboard reachable, labeled, no role/aria warnings in dev tools.
- No new dependencies were added without justification.
- Public API (props, emits, slots, exposed methods) is documented via types and, where appropriate, JSDoc on non-obvious entries.
