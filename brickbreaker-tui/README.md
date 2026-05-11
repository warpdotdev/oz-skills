# Brickbreaker TUI

A small terminal Brick Breaker game written in Rust with `crossterm`.

## Run

```bash
cargo run --manifest-path brickbreaker-tui/Cargo.toml
```

The game uses the terminal alternate screen and raw mode while it is running.

## Controls

- `←` / `a`: move paddle left
- `→` / `d`: move paddle right
- `space`: pause or resume
- `r`: restart after winning or losing
- `q` / `Esc`: quit

## Test

```bash
cargo test --manifest-path brickbreaker-tui/Cargo.toml
```
