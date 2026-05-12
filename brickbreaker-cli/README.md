# Brickbreaker CLI

A dependency-free Rust terminal brick breaker game with a pseudo-3D perspective playfield.

## Run

```bash
cargo run --release
```

The game uses ANSI escape sequences and `stty` for raw keyboard input, so it is intended for Unix-like terminals. It renders the playfield as a trapezoid with depth lines, scaled far bricks, a wider near paddle, and shadows for a 3D-style terminal view.

## Controls

- `a`, `h`, or left arrow: move left
- `d`, `l`, or right arrow: move right
- `p`: pause or resume
- `r`: restart
- `q` or Ctrl-C: quit

Clear all bricks to advance to the next level. Each miss costs one life.
