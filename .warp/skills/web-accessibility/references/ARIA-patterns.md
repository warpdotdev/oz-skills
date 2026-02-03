# ARIA Patterns and Examples

Common ARIA patterns for accessible components. Prefer native HTML elements when possible.

## First Rule of ARIA

> **Use native HTML elements whenever possible**

```html
<!-- ❌ Don't use ARIA when native HTML works -->
<div role="button" tabindex="0">Click me</div>

<!-- ✅ Use native HTML -->
<button>Click me</button>
```

## Buttons

```html
<!-- Native button (preferred) -->
<button>Submit</button>

<!-- Icon button with label -->
<button aria-label="Close dialog">×</button>

<!-- Button with visually hidden text -->
<button>
  <svg aria-hidden="true"><!-- icon --></svg>
  <span class="visually-hidden">Open menu</span>
</button>
```

## Links

```html
<!-- Standard link -->
<a href="/page">Descriptive link text</a>

<!-- External link -->
<a href="https://external.com" target="_blank" rel="noopener">
  External site
  <span class="visually-hidden">(opens in new tab)</span>
</a>

<!-- Current page indicator -->
<a href="/" aria-current="page">Home</a>
```

## Form Fields

### Basic input with label
```html
<label for="email">Email address</label>
<input type="email" id="email" name="email" 
       autocomplete="email" required>
```

### Input with hint text
```html
<label for="email">Email</label>
<input type="email" id="email" aria-describedby="email-hint">
<p id="email-hint">We'll never share your email.</p>
```

### Input with error
```html
<label for="email">Email</label>
<input type="email" id="email" 
       aria-invalid="true" 
       aria-describedby="email-error">
<p id="email-error" role="alert">
  Please enter a valid email address.
</p>
```

### Password with requirements
```html
<label for="password">Password</label>
<input type="password" id="password" 
       aria-describedby="password-requirements">
<p id="password-requirements">
  Must be at least 8 characters with one number.
</p>
```

## Navigation

### Main navigation
```html
<nav aria-label="Main">
  <ul>
    <li><a href="/" aria-current="page">Home</a></li>
    <li><a href="/products">Products</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>
```

### Multiple navigation regions
```html
<!-- Each nav needs unique label -->
<nav aria-label="Main">...</nav>
<nav aria-label="Footer">...</nav>
<nav aria-label="Social media">...</nav>
```

## Modals/Dialogs

```html
<div role="dialog" 
     aria-modal="true" 
     aria-labelledby="dialog-title"
     aria-describedby="dialog-desc">
  <h2 id="dialog-title">Confirm Action</h2>
  <p id="dialog-desc">Are you sure you want to continue?</p>
  <button>Confirm</button>
  <button>Cancel</button>
</div>
```

### Focus trap implementation
```javascript
function openModal(modal) {
  const focusableElements = modal.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];
  
  // Trap focus within modal
  modal.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
    if (e.key === 'Escape') {
      closeModal();
    }
  });
  
  firstElement.focus();
}
```

## Tabs

```html
<div role="tablist" aria-label="Product information">
  <button role="tab" 
          id="tab-1" 
          aria-selected="true" 
          aria-controls="panel-1">
    Description
  </button>
  <button role="tab" 
          id="tab-2" 
          aria-selected="false" 
          aria-controls="panel-2" 
          tabindex="-1">
    Reviews
  </button>
</div>

<div role="tabpanel" 
     id="panel-1" 
     aria-labelledby="tab-1">
  <!-- Panel content -->
</div>

<div role="tabpanel" 
     id="panel-2" 
     aria-labelledby="tab-2" 
     hidden>
  <!-- Panel content -->
</div>
```

## Live Regions

### Polite announcements (waits for pause)
```html
<div aria-live="polite" aria-atomic="true" class="status">
  <!-- Content updates announced to screen readers -->
</div>
```

### Assertive alerts (interrupts immediately)
```html
<div role="alert" aria-live="assertive">
  <!-- Urgent notifications -->
</div>
```

### Status messages
```html
<div role="status" aria-live="polite">
  Loading complete
</div>
```

### Dynamic notification example
```javascript
function showNotification(message, type = 'polite') {
  const container = document.getElementById(`${type}-announcer`);
  container.textContent = ''; // Clear first
  requestAnimationFrame(() => {
    container.textContent = message;
  });
}
```

## Skip Links

```html
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <header><!-- navigation --></header>
  <main id="main-content" tabindex="-1">
    <!-- main content -->
  </main>
</body>
```

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px 16px;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

## Visually Hidden Text

For screen readers only (hidden visually but announced):

```css
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

Usage:
```html
<button>
  <svg aria-hidden="true"><!-- icon --></svg>
  <span class="visually-hidden">Delete item</span>
</button>
```

## Landmark Regions

```html
<header><!-- Banner landmark --></header>
<nav aria-label="Main"><!-- Navigation landmark --></nav>
<main><!-- Main landmark --></main>
<aside><!-- Complementary landmark --></aside>
<footer><!-- Contentinfo landmark --></footer>
```

## When to Use ARIA

✅ **Good use cases:**
- Custom widgets not available in HTML (tabs, accordions, complex menus)
- Live regions for dynamic content updates
- Complex application states
- Enhanced semantics for existing elements

❌ **Avoid ARIA for:**
- Standard form controls (use native HTML)
- Buttons and links (use `<button>` and `<a>`)
- Basic page structure (use semantic HTML5)
- Anything that can be done with native HTML

## ARIA Attributes Reference

### Common attributes
- `aria-label`: Provides accessible name
- `aria-labelledby`: References element ID(s) for name
- `aria-describedby`: References element ID(s) for description
- `aria-hidden`: Hides from assistive tech (use sparingly)
- `aria-live`: Announces dynamic content changes
- `aria-current`: Indicates current item in set

### State attributes
- `aria-expanded`: Collapsible element state
- `aria-selected`: Selection state
- `aria-checked`: Checkbox/radio state
- `aria-pressed`: Toggle button state
- `aria-invalid`: Form validation state
- `aria-disabled`: Disabled state

### Relationship attributes
- `aria-controls`: Element(s) this controls
- `aria-owns`: Element(s) this owns in DOM
- `aria-activedescendant`: Active child element
