use std::env;
use std::io::{self, Read, Write};
use std::process::{Command, Stdio};
use std::sync::mpsc::{self, Receiver};
use std::thread;
use std::time::{Duration, Instant};

const DEFAULT_FIELD_WIDTH: usize = 70;
const DEFAULT_FIELD_HEIGHT: usize = 24;
const MIN_FIELD_WIDTH: usize = 46;
const MIN_FIELD_HEIGHT: usize = 18;
const MAX_FIELD_WIDTH: usize = 100;
const MAX_FIELD_HEIGHT: usize = 35;
const BRICK_ROWS: i32 = 5;
const BRICK_COLS: i32 = 10;
const BRICK_GAP: i32 = 1;
const PADDLE_WIDTH: i32 = 11;
const PADDLE_STEP: i32 = 3;

#[derive(Clone, Copy)]
struct Point {
    x: i32,
    y: i32,
}

#[derive(Clone, Copy)]
struct Ball {
    pos: Point,
    vel: Point,
}

#[derive(Clone)]
struct Brick {
    x: i32,
    y: i32,
    width: i32,
    alive: bool,
    points: u32,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Status {
    Playing,
    Paused,
    GameOver,
}

#[derive(Clone, Copy)]
enum Input {
    Left,
    Right,
    Pause,
    Restart,
    Quit,
}

struct GameState {
    width: usize,
    height: usize,
    paddle_x: i32,
    paddle_width: i32,
    ball: Ball,
    bricks: Vec<Brick>,
    score: u32,
    lives: u32,
    level: u32,
    tick: u64,
    status: Status,
    running: bool,
}

impl GameState {
    fn new(width: usize, height: usize) -> Self {
        let width = width.clamp(MIN_FIELD_WIDTH, MAX_FIELD_WIDTH);
        let height = height.clamp(MIN_FIELD_HEIGHT, MAX_FIELD_HEIGHT);
        let mut state = Self {
            width,
            height,
            paddle_x: 0,
            paddle_width: PADDLE_WIDTH,
            ball: Ball {
                pos: Point { x: 0, y: 0 },
                vel: Point { x: 1, y: -1 },
            },
            bricks: build_bricks(width, 1),
            score: 0,
            lives: 3,
            level: 1,
            tick: 0,
            status: Status::Playing,
            running: true,
        };
        state.reset_positions();
        state
    }

    fn handle_input(&mut self, receiver: &Receiver<Input>) {
        while let Ok(input) = receiver.try_recv() {
            match input {
                Input::Left => self.move_paddle(-PADDLE_STEP),
                Input::Right => self.move_paddle(PADDLE_STEP),
                Input::Pause => self.toggle_pause(),
                Input::Restart => {
                    *self = Self::new(self.width, self.height);
                }
                Input::Quit => {
                    self.running = false;
                }
            }
        }
    }

    fn update(&mut self) {
        if self.status != Status::Playing {
            return;
        }

        self.tick = self.tick.wrapping_add(1);
        if self.tick % self.ball_delay() == 0 {
            self.step_ball();
        }
    }

    fn render(&self, stdout: &mut impl Write) -> io::Result<()> {
        let mut board = vec![vec![' '; self.width]; self.height];
        self.draw_3d_arena(&mut board);

        for brick in self.bricks.iter().filter(|brick| brick.alive) {
            self.draw_3d_span(&mut board, brick.x, brick.x + brick.width - 1, brick.y + 1, '.');
            self.draw_3d_span(&mut board, brick.x, brick.x + brick.width - 1, brick.y, '#');
        }

        let paddle_y = self.paddle_y();
        self.draw_3d_span(
            &mut board,
            self.paddle_x,
            self.paddle_x + self.paddle_width - 1,
            paddle_y + 1,
            '-',
        );
        self.draw_3d_span(
            &mut board,
            self.paddle_x,
            self.paddle_x + self.paddle_width - 1,
            paddle_y,
            '=',
        );

        self.draw_3d_point(&mut board, self.ball.pos.x + 1, self.ball.pos.y + 1, '.');
        self.draw_3d_point(&mut board, self.ball.pos.x, self.ball.pos.y, 'O');

        let mut output = String::with_capacity((self.width + 1) * (self.height + 3));
        output.push_str("\x1b[H");
        output.push_str(&format!(
            "3D Brickbreaker  Score: {}  Lives: {}  Level: {}  Controls: a/d or arrows, p pause, r restart, q quit\n",
            self.score, self.lives, self.level
        ));

        for row in board {
            for cell in row {
                output.push(cell);
            }
            output.push('\n');
        }

        match self.status {
            Status::Playing => output.push_str("Perspective view: far bricks are smaller, near paddle is wider, shadows show depth.\n"),
            Status::Paused => output.push_str("Paused. Press p to resume, r to restart, or q to quit.\n"),
            Status::GameOver => output.push_str("Game over. Press r to restart or q to quit.\n"),
        }

        stdout.write_all(output.as_bytes())?;
        stdout.flush()
    }

    fn draw_3d_arena(&self, board: &mut [Vec<char>]) {
        for y in 0..self.height as i32 {
            let left = self.perspective_left(y);
            let right = self.perspective_right(y);
            let row = y as usize;

            Self::set_cell(board, left, row, '/');
            Self::set_cell(board, right, row, '\\');

            if y % 3 == 0 && y > 0 && y < self.height as i32 - 1 {
                for x in left + 1..right {
                    if x % 4 == 0 {
                        Self::set_cell(board, x, row, '.');
                    }
                }
            }

            for lane in 1..4 {
                let lane_x = self.projected_x((self.width as i32 * lane) / 4, y);
                if lane_x > left && lane_x < right && y % 2 == 0 {
                    Self::set_cell(board, lane_x, row, ':');
                }
            }
        }

        let top_y = 0;
        let top_left = self.perspective_left(top_y);
        let top_right = self.perspective_right(top_y);
        for x in top_left..=top_right {
            Self::set_cell(board, x, top_y as usize, '-');
        }
        Self::set_cell(board, top_left, top_y as usize, '+');
        Self::set_cell(board, top_right, top_y as usize, '+');

        let bottom_y = self.height as i32 - 1;
        let bottom_left = self.perspective_left(bottom_y);
        let bottom_right = self.perspective_right(bottom_y);
        for x in bottom_left..=bottom_right {
            Self::set_cell(board, x, bottom_y as usize, '=');
        }
        Self::set_cell(board, bottom_left, bottom_y as usize, '+');
        Self::set_cell(board, bottom_right, bottom_y as usize, '+');
    }

    fn draw_3d_span(&self, board: &mut [Vec<char>], start_x: i32, end_x: i32, y: i32, cell: char) {
        if y < 0 || y >= self.height as i32 {
            return;
        }

        let screen_start = self.projected_x(start_x, y);
        let screen_end = self.projected_x(end_x, y).max(screen_start);
        let row = y as usize;

        for x in screen_start..=screen_end {
            Self::set_cell(board, x, row, cell);
        }

        if cell == '#' || cell == '=' {
            Self::set_cell(board, screen_start, row, '[');
            Self::set_cell(board, screen_end, row, ']');
        }
    }

    fn draw_3d_point(&self, board: &mut [Vec<char>], x: i32, y: i32, cell: char) {
        if y < 0 || y >= self.height as i32 {
            return;
        }

        let screen_x = self.projected_x(x, y);
        Self::set_cell(board, screen_x, y as usize, cell);
    }

    fn projected_x(&self, x: i32, y: i32) -> usize {
        let y = y.clamp(0, self.height as i32 - 1);
        let left = self.perspective_left(y);
        let right = self.perspective_right(y);
        let span = right.saturating_sub(left).max(1);
        let x = x.clamp(0, self.width as i32 - 1) as usize;
        let logical_span = self.width.saturating_sub(1).max(1);

        left + x * span / logical_span
    }

    fn perspective_left(&self, y: i32) -> usize {
        let y = y.clamp(0, self.height as i32 - 1) as usize;
        let far_inset = (self.width / 4).min(16);
        let depth = self.height.saturating_sub(1).saturating_sub(y);

        far_inset * depth / self.height.saturating_sub(1).max(1)
    }

    fn perspective_right(&self, y: i32) -> usize {
        self.width.saturating_sub(1).saturating_sub(self.perspective_left(y))
    }

    fn set_cell(board: &mut [Vec<char>], x: usize, y: usize, cell: char) {
        if let Some(row) = board.get_mut(y) {
            if let Some(slot) = row.get_mut(x) {
                *slot = cell;
            }
        }
    }

    fn move_paddle(&mut self, delta: i32) {
        let max_x = self.width as i32 - self.paddle_width - 1;
        self.paddle_x = (self.paddle_x + delta).clamp(1, max_x);
    }

    fn toggle_pause(&mut self) {
        self.status = match self.status {
            Status::Playing => Status::Paused,
            Status::Paused => Status::Playing,
            Status::GameOver => Status::GameOver,
        };
    }

    fn step_ball(&mut self) {
        let mut next = Point {
            x: self.ball.pos.x + self.ball.vel.x,
            y: self.ball.pos.y + self.ball.vel.y,
        };

        if next.x <= 1 || next.x >= self.width as i32 - 2 {
            self.ball.vel.x *= -1;
            next.x = self.ball.pos.x + self.ball.vel.x;
        }

        if next.y <= 1 {
            self.ball.vel.y = 1;
            next.y = self.ball.pos.y + self.ball.vel.y;
        }

        if self.hits_paddle(next) {
            self.ball.vel.y = -1;
            self.ball.vel.x = self.paddle_deflection(next.x);
            next.y = self.paddle_y() - 1;
        }

        if let Some(hit_index) = self.hit_brick(next) {
            let points = self.bricks[hit_index].points;
            self.bricks[hit_index].alive = false;
            self.score += points;
            self.ball.vel.y *= -1;
            next.y = self.ball.pos.y + self.ball.vel.y;

            if self.bricks.iter().all(|brick| !brick.alive) {
                self.advance_level();
                return;
            }
        }

        if next.y >= self.height as i32 - 1 {
            self.lose_life();
            return;
        }

        self.ball.pos = next;
    }

    fn reset_positions(&mut self) {
        self.paddle_x = (self.width as i32 - self.paddle_width) / 2;
        self.ball = Ball {
            pos: Point {
                x: self.width as i32 / 2,
                y: self.paddle_y() - 1,
            },
            vel: Point {
                x: if self.level % 2 == 0 { -1 } else { 1 },
                y: -1,
            },
        };
        self.tick = 0;
    }

    fn advance_level(&mut self) {
        self.level += 1;
        self.bricks = build_bricks(self.width, self.level);
        self.reset_positions();
    }

    fn lose_life(&mut self) {
        self.lives = self.lives.saturating_sub(1);
        if self.lives == 0 {
            self.status = Status::GameOver;
        } else {
            self.reset_positions();
        }
    }

    fn ball_delay(&self) -> u64 {
        3_u64.saturating_sub(self.level as u64 / 2).max(1)
    }

    fn hits_paddle(&self, point: Point) -> bool {
        point.y == self.paddle_y()
            && point.x >= self.paddle_x
            && point.x < self.paddle_x + self.paddle_width
            && self.ball.vel.y > 0
    }

    fn paddle_deflection(&self, x: i32) -> i32 {
        let offset = x - self.paddle_x;
        if offset < self.paddle_width / 3 {
            -1
        } else if offset > self.paddle_width * 2 / 3 {
            1
        } else {
            self.ball.vel.x
        }
    }

    fn hit_brick(&self, point: Point) -> Option<usize> {
        self.bricks.iter().position(|brick| {
            brick.alive && point.y == brick.y && point.x >= brick.x && point.x < brick.x + brick.width
        })
    }

    fn paddle_y(&self) -> i32 {
        self.height as i32 - 3
    }

}

struct TerminalGuard {
    original_mode: Option<String>,
}

impl TerminalGuard {
    fn activate() -> io::Result<Self> {
        let original_mode = Command::new("stty")
            .arg("-g")
            .stdin(Stdio::inherit())
            .output()
            .ok()
            .filter(|output| output.status.success())
            .map(|output| String::from_utf8_lossy(&output.stdout).trim().to_owned());
        let status = Command::new("stty")
            .args(["raw", "-echo"])
            .stdin(Stdio::inherit())
            .status()?;
        if !status.success() {
            return Err(io::Error::new(
                io::ErrorKind::Other,
                "failed to enable raw terminal mode with stty",
            ));
        }

        let mut stdout = io::stdout();
        stdout.write_all(b"\x1b[?25l\x1b[2J\x1b[H")?;
        stdout.flush()?;

        Ok(Self { original_mode })
    }
}

impl Drop for TerminalGuard {
    fn drop(&mut self) {
        if let Some(original_mode) = &self.original_mode {
            let _ = Command::new("stty")
                .arg(original_mode)
                .stdin(Stdio::inherit())
                .status();
        }

        let mut stdout = io::stdout();
        let _ = stdout.write_all(b"\x1b[?25h\x1b[0m\x1b[2J\x1b[H");
        let _ = stdout.flush();
    }
}

fn main() -> io::Result<()> {
    let _terminal = TerminalGuard::activate()?;
    let input = spawn_input_thread();
    let mut stdout = io::stdout();
    let width = field_dimension(
        "COLUMNS",
        DEFAULT_FIELD_WIDTH,
        MIN_FIELD_WIDTH,
        MAX_FIELD_WIDTH,
    );
    let height = field_dimension(
        "LINES",
        DEFAULT_FIELD_HEIGHT,
        MIN_FIELD_HEIGHT,
        MAX_FIELD_HEIGHT,
    ) - 2;
    let mut game = GameState::new(width, height);
    let frame_duration = Duration::from_millis(33);

    while game.running {
        let frame_start = Instant::now();
        game.handle_input(&input);
        game.update();
        game.render(&mut stdout)?;

        let elapsed = frame_start.elapsed();
        if elapsed < frame_duration {
            thread::sleep(frame_duration - elapsed);
        }
    }

    Ok(())
}

fn spawn_input_thread() -> Receiver<Input> {
    let (sender, receiver) = mpsc::channel();

    thread::spawn(move || {
        let stdin = io::stdin();
        let mut stdin = stdin.lock();
        let mut byte = [0_u8; 1];

        while stdin.read_exact(&mut byte).is_ok() {
            let input = match byte[0] {
                b'a' | b'A' | b'h' | b'H' => Some(Input::Left),
                b'd' | b'D' | b'l' | b'L' => Some(Input::Right),
                b'p' | b'P' => Some(Input::Pause),
                b'r' | b'R' => Some(Input::Restart),
                b'q' | b'Q' | 3 => Some(Input::Quit),
                27 => read_arrow_key(&mut stdin),
                _ => None,
            };

            if let Some(input) = input {
                if sender.send(input).is_err() {
                    break;
                }
            }
        }
    });

    receiver
}

fn read_arrow_key(reader: &mut impl Read) -> Option<Input> {
    let mut sequence = [0_u8; 2];
    if reader.read_exact(&mut sequence).is_err() || sequence[0] != b'[' {
        return None;
    }

    match sequence[1] {
        b'D' => Some(Input::Left),
        b'C' => Some(Input::Right),
        _ => None,
    }
}

fn build_bricks(width: usize, level: u32) -> Vec<Brick> {
    let margin = 2;
    let available_width = width as i32 - margin * 2 - BRICK_GAP * (BRICK_COLS - 1);
    let brick_width = (available_width / BRICK_COLS).max(3);
    let row_width = brick_width * BRICK_COLS + BRICK_GAP * (BRICK_COLS - 1);
    let start_x = ((width as i32 - row_width) / 2).max(1);
    let rows = (BRICK_ROWS + level as i32 / 2).min(8);
    let mut bricks = Vec::with_capacity((rows * BRICK_COLS) as usize);

    for row in 0..rows {
        for col in 0..BRICK_COLS {
            bricks.push(Brick {
                x: start_x + col * (brick_width + BRICK_GAP),
                y: 3 + row,
                width: brick_width,
                alive: true,
                points: (row as u32 + 1) * 10 * level,
            });
        }
    }

    bricks
}

fn field_dimension(name: &str, default: usize, min: usize, max: usize) -> usize {
    env::var(name)
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(default)
        .clamp(min, max)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bricks_fit_inside_play_field() {
        let bricks = build_bricks(46, 1);

        assert!(!bricks.is_empty());
        assert!(bricks.iter().all(|brick| brick.x > 0));
        assert!(bricks.iter().all(|brick| brick.x + brick.width < 46));
    }

    #[test]
    fn paddle_movement_stays_in_bounds() {
        let mut game = GameState::new(50, 20);

        game.move_paddle(-100);
        assert_eq!(game.paddle_x, 1);

        game.move_paddle(100);
        assert_eq!(game.paddle_x, 50 - PADDLE_WIDTH - 1);
    }

    #[test]
    fn paddle_collision_bounces_ball_upward() {
        let mut game = GameState::new(50, 20);
        game.paddle_x = 20;
        game.ball = Ball {
            pos: Point {
                x: game.paddle_x + game.paddle_width / 2,
                y: game.paddle_y() - 1,
            },
            vel: Point { x: 1, y: 1 },
        };

        game.step_ball();

        assert_eq!(game.ball.vel.y, -1);
        assert_eq!(game.ball.pos.y, game.paddle_y() - 1);
    }

    #[test]
    fn missing_paddle_costs_one_life() {
        let mut game = GameState::new(50, 20);
        game.ball = Ball {
            pos: Point {
                x: 2,
                y: game.height as i32 - 2,
            },
            vel: Point { x: 0, y: 1 },
        };

        game.step_ball();

        assert_eq!(game.lives, 2);
        assert_eq!(game.status, Status::Playing);
    }

    #[test]
    fn perspective_projection_widens_toward_paddle() {
        let game = GameState::new(70, 24);
        let near_y = game.height as i32 - 1;

        assert!(game.perspective_left(0) > game.perspective_left(near_y));
        assert_eq!(game.perspective_left(near_y), 0);
        assert_eq!(game.projected_x(0, near_y), 0);
        assert!(game.projected_x(0, 0) > 0);
    }
}
