---
name: hyperframes
description: Build video compositions, animations, title cards, overlays, captions, and scene transitions as HTML with GSAP timelines. Use when asked to create HTML-based video content, add captions synced to audio, generate animated text effects, or compose multi-scene video productions.
license: MIT
---

# HyperFrames

HTML is the source of truth for video. A composition is an HTML file with `data-*` attributes for timing, a GSAP timeline for animation, and CSS for appearance. The framework handles clip visibility, media playback, and timeline sync.

## Prerequisites

Install HyperFrames CLI:

```bash
npm install -g hyperframes
```

Key commands:
- `hyperframes init` — scaffold a new project
- `hyperframes lint` — validate structure and attributes
- `hyperframes validate` — WCAG contrast audit + structure checks
- `hyperframes preview` — browser preview with timeline scrubber
- `hyperframes render` — export to MP4/WebM

## Approach

Before writing HTML:

1. **What** — identify the narrative arc, key moments, emotional beats
2. **Structure** — how many compositions, which are sub-compositions vs inline, what tracks carry what
3. **Timing** — which clips drive duration, where transitions land, pacing
4. **Layout** — build the end-state first (see below)
5. **Animate** — then add motion

### Visual Identity Gate

Before writing ANY composition HTML, define a visual identity:

1. Check for a `DESIGN.md` in the project → use its colors, fonts, motion rules
2. Check for `visual-style.md` → apply its structured fields
3. User named a style? → generate a minimal DESIGN.md with colors, typography, anti-patterns
4. None of the above? → ask: mood (explosive/cinematic/technical/warm), light or dark canvas, brand colors?

Every composition must trace its palette and typography back to an explicit direction. If you're reaching for `#333`, `#3b82f6`, or `Roboto` — you skipped this step.

## Layout Before Animation

Position every element where it should be at its **most visible moment**. Write static HTML+CSS first. No GSAP yet.

1. **Identify the hero frame** — the moment when the most elements are simultaneously visible
2. **Write static CSS** for that frame using flex layout with padding
3. **Add entrances with `gsap.from()`** — animate FROM invisible TO the CSS position
4. **Add exits with `gsap.to()`** — only on the final scene

```css
/* scene-content fills the scene, padding positions content */
.scene-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 120px 160px;
  gap: 24px;
  box-sizing: border-box;
}
```

```js
// Animate INTO the CSS positions
tl.from(".title", { y: 60, opacity: 0, duration: 0.6, ease: "power3.out" }, 0.1);
tl.from(".subtitle", { y: 40, opacity: 0, duration: 0.5, ease: "power3.out" }, 0.3);
```

**WRONG** — hardcoded dimensions and absolute positioning on content containers. Use `width: 100%; height: 100%; padding: Npx;` with flex. Reserve `position: absolute` for decoratives only.

## Data Attributes

### All Clips

| Attribute | Required | Values |
|-----------|----------|--------|
| `id` | Yes | Unique identifier |
| `data-start` | Yes | Seconds or clip ID reference (`"el-1"`, `"intro + 2"`) |
| `data-duration` | Required for img/div/compositions | Seconds |
| `data-track-index` | Yes | Integer. Same-track clips cannot overlap |
| `data-media-start` | No | Trim offset into source (seconds) |
| `data-volume` | No | 0-1 (default 1) |

`data-track-index` does **not** affect visual layering — use CSS `z-index`.

### Composition Clips

| Attribute | Required | Values |
|-----------|----------|--------|
| `data-composition-id` | Yes | Unique composition ID |
| `data-start` | Yes | Start time (root: `"0"`) |
| `data-duration` | Yes | Takes precedence over GSAP timeline duration |
| `data-width` / `data-height` | Yes | Pixel dimensions (1920x1080 or 1080x1920) |
| `data-composition-src` | No | Path to external HTML file |

## Composition Structure

**Standalone compositions (main index.html)** put the `data-composition-id` div directly in `<body>`. Do NOT use `<template>` — it hides all content.

**Sub-compositions** loaded via `data-composition-src` use a `<template>` wrapper:

```html
<template id="my-comp-template">
  <div data-composition-id="my-comp" data-width="1920" data-height="1080">
    <!-- content -->
    <style>
      [data-composition-id="my-comp"] {
        /* scoped styles */
      }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      // tweens...
      window.__timelines["my-comp"] = tl;
    </script>
  </div>
</template>
```

Load in root: `<div id="el-1" data-composition-id="my-comp" data-composition-src="compositions/my-comp.html" data-start="0" data-duration="10" data-track-index="1"></div>`

## Video and Audio

Video must be `muted playsinline`. Audio is always a separate `<audio>` element:

```html
<video id="el-v" data-start="0" data-duration="30" data-track-index="0" src="video.mp4" muted playsinline></video>
<audio id="el-a" data-start="0" data-duration="30" data-track-index="2" src="video.mp4" data-volume="1"></audio>
```

## Timeline Contract

- All timelines start `{ paused: true }` — the player controls playback
- Register every timeline: `window.__timelines["<composition-id>"] = tl`
- Framework auto-nests sub-timelines — do NOT manually add them
- Duration comes from `data-duration`, not from GSAP timeline length
- Never create empty tweens to set duration

## Rules (Non-Negotiable)

**Deterministic:** No `Math.random()`, `Date.now()`, or time-based logic. Use a seeded PRNG if needed.

**GSAP:** Only animate visual properties (`opacity`, `x`, `y`, `scale`, `rotation`, `color`, `backgroundColor`, `borderRadius`, transforms). Do NOT animate `visibility`, `display`, or call `video.play()`/`audio.play()`.

**Animation conflicts:** Never animate the same property on the same element from multiple timelines simultaneously.

**No `repeat: -1`:** Infinite-repeat timelines break the capture engine. Calculate exact repeat count: `repeat: Math.ceil(duration / cycleDuration) - 1`.

**Synchronous timeline construction:** Never build timelines inside `async`/`await`, `setTimeout`, or Promises.

### Never Do

1. Forget `window.__timelines` registration
2. Use video for audio — always muted video + separate `<audio>`
3. Nest video inside a timed div — use a non-timed wrapper
4. Use `data-layer` (use `data-track-index`) or `data-end` (use `data-duration`)
5. Animate video element dimensions — animate a wrapper div
6. Call play/pause/seek on media — framework owns playback
7. Create a top-level container without `data-composition-id`
8. Use `repeat: -1` on any timeline or tween
9. Build timelines asynchronously
10. Use `gsap.set()` on clip elements from later scenes — use `tl.set(selector, vars, timePosition)` inside the timeline at or after the clip's `data-start` time
11. Use `<br>` in content text — let text wrap via `max-width` instead

## Scene Transitions (Non-Negotiable)

Every multi-scene composition MUST follow ALL of these rules:

1. **ALWAYS use transitions between scenes.** No jump cuts. No exceptions.
2. **ALWAYS use entrance animations on every scene.** Every element animates IN via `gsap.from()`. No element may appear fully-formed.
3. **NEVER use exit animations** except on the final scene. The transition IS the exit. The outgoing scene's content MUST be fully visible when the transition starts.
4. **Final scene only:** May fade elements out. This is the ONLY scene where `gsap.to(..., { opacity: 0 })` is allowed.

**WRONG — exit animation before transition:**
```js
// BANNED — empties the scene before the transition
tl.to("#s1-title", { opacity: 0, y: -40, duration: 0.4 }, 6.5);
```

**RIGHT — entrance only, transition handles exit:**
```js
tl.from("#s1-title", { y: 50, opacity: 0, duration: 0.7, ease: "power3.out" }, 0.3);
// NO exit tweens — transition at 7.2s handles the scene change
tl.from("#s2-heading", { x: -40, opacity: 0, duration: 0.6, ease: "expo.out" }, 8.0);
```

## Animation Guardrails

- Offset first animation 0.1-0.3s (not t=0)
- Vary eases across entrance tweens — at least 3 different eases per scene
- Don't repeat an entrance pattern within a scene
- Avoid full-screen linear gradients on dark backgrounds (H.264 banding)
- 60px+ headlines, 20px+ body, 16px+ data labels for rendered video
- `font-variant-numeric: tabular-nums` on number columns
- Every scene needs visual depth — background decoratives (radial glows, ghost text, accent lines) with slow ambient animation

## Typography

- Just write the `font-family` you want in CSS — the compiler embeds supported fonts automatically
- 700-900 weight for headlines, 300-400 for body
- Pair serif + sans (not two sans-serif families)
- Add `crossorigin="anonymous"` to external media
- For dynamic text overflow: `window.__hyperframes.fitTextFontSize(text, { maxWidth, fontFamily, fontWeight })`

## Captions

When adding captions synced to audio:

- Analyze tone to choose caption style (hype → scale-pop; corporate → fade+slide; tutorial → typewriter; storytelling → slow fade)
- Group words: 2-3 for energy, 3-5 conversational, 4-6 calm
- Position: bottom 80-120px (landscape), lower middle (portrait)
- One caption group visible at a time
- Every group must have a hard kill: `tl.set(groupEl, { opacity: 0, visibility: "hidden" }, group.end)`
- Use `fitTextFontSize()` to prevent overflow

## Quality Checks

### Contrast

`hyperframes validate` runs a WCAG contrast audit. It seeks to timestamps, screenshots the page, and computes contrast ratios. Failures appear as warnings. Fix by brightening (dark backgrounds) or darkening (light backgrounds) the failing color until it clears 4.5:1.

### Animation Map

After authoring animations, verify choreography:

```bash
npx hyperframes animation-map <composition-dir>
```

Check per-tween summaries, ASCII timeline, stagger detection, dead zones, element lifecycles, and flags (`offscreen`, `collision`, `invisible`).

## Environment Notes

- Prefer ASCII-only project/output paths when rendering; non-ASCII paths can break headless Chrome
- If MP4 encoding fails under Conda FFmpeg, force system FFmpeg: `export PATH=/usr/bin:$PATH`
- Verify visually by extracting frames with FFmpeg, not just by trusting a successful render exit code
- If the final video looks black, check whether a timed `.clip` container was hidden while only its children were animated
