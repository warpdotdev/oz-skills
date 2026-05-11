use std::io::{stdout, Stdout, Write};
use std::thread;
use std::time::{Duration, Instant};

use crossterm::cursor::{Hide, MoveTo, Show};
use crossterm::event::{self, Event, KeyCode};
use crossterm::execute;
use crossterm::queue;
use crossterm::style::{Color, Print, ResetColor, SetForegroundColor};
use crossterm::terminal::{
    self, Clear, ClearType, EnterAlternateScreen, LeaveAlternateScreen,
};

const BOARD_WIDTH: i32 = 72;
const BOARD_HEIGHT: i32 = 24;
const FRAME_TIME: Duration = Duration::from_millis(33);
const PADDLE_WIDTH: f32 = 11.0;
const PADDLE_SPEED: f32 = 45.0;
const BALL_SPEED: f32 = 25.0;
const INITIAL_LIVES: u8 = 3;

type Result<T> = std::io::Result<T>;

#[derive(Clone, Copy, Debug)]
struct Vec2 {
    x: f32,
    y: f32,
}

impl Vec2 {
    const fn new(x: f32, y: f32) -> Self {
        Self { x, y }
    }
}

#[derive(Clone, Debug)]
struct Brick {
    x: i32,
    y: i32,
    width: i32,
    hits_left: u8,
}

impl Brick {
    fn contains(&self, point: Vec2) -> bool {
        let x = point.x.round() as i32;
        let y = point.y.round() as i32;

        y == self.y && x >= self.x && x < self.x + self.width
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Mode {
    Running,
    Paused,
    Won,
    GameOver,
}

#[derive(Debug)]
struct Game {
    ball: Vec2,
    velocity: Vec2,
    paddle_x: f32,
    bricks: Vec<Brick>,
    score: u32,
    lives: u8,
    mode: Mode,
}

impl Game {
    fn new() -> Self {
        Self {
            ball: Vec2::new(BOARD_WIDTH as f32 / 2.0, BOARD_HEIGHT as f32 - 6.0),
            velocity: Vec2::new(0.65, -1.0),
            paddle_x: (BOARD_WIDTH as f32 - PADDLE_WIDTH) / 2.0,
            bricks: build_bricks(),
            score: 0,
            lives: INITIAL_LIVES,
            mode: Mode::Running,
        }
    }

    fn restart(&mut self) {
        *self = Self::new();
    }

    fn toggle_pause(&mut self) {
        self.mode = match self.mode {
            Mode::Running => Mode::Paused,
            Mode::Paused => Mode::Running,
            ended => ended,
        };
    }

    fn move_paddle(&mut self, direction: f32, dt: f32) {
        if self.mode != Mode::Running {
            return;
        }

        self.paddle_x += direction * PADDLE_SPEED * dt;
        let max_x = BOARD_WIDTH as f32 - PADDLE_WIDTH - 1.0;
        self.paddle_x = self.paddle_x.clamp(1.0, max_x);
    }

    fn tick(&mut self, dt: f32) {
        if self.mode != Mode::Running {
            return;
        }

        self.ball.x += self.velocity.x * BALL_SPEED * dt;
        self.ball.y += self.velocity.y * BALL_SPEED * dt;

        self.collide_with_walls();
        self.collide_with_paddle();
        self.collide_with_bricks();
        self.check_round_state();
    }

    fn collide_with_walls(&mut self) {
        if self.ball.x <= 1.0 {
            self.ball.x = 1.0;
            self.velocity.x = self.velocity.x.abs();
        }

        if self.ball.x >= (BOARD_WIDTH - 2) as f32 {
            self.ball.x = (BOARD_WIDTH - 2) as f32;
            self.velocity.x = -self.velocity.x.abs();
        }

        if self.ball.y <= 1.0 {
            self.ball.y = 1.0;
            self.velocity.y = self.velocity.y.abs();
        }
    }

    fn collide_with_paddle(&mut self) {
        let paddle_y = (BOARD_HEIGHT - 3) as f32;
        let over_paddle = self.ball.x >= self.paddle_x
            && self.ball.x <= self.paddle_x + PADDLE_WIDTH;
        let touching_from_above = self.ball.y >= paddle_y - 0.3
            && self.ball.y <= paddle_y + 0.6
            && self.velocity.y > 0.0;

        if over_paddle && touching_from_above {
            let paddle_center = self.paddle_x + PADDLE_WIDTH / 2.0;
            let normalized_offset = ((self.ball.x - paddle_center) / (PADDLE_WIDTH / 2.0))
                .clamp(-1.0, 1.0);

            self.ball.y = paddle_y - 1.0;
            self.velocity.x = normalized_offset;
            self.velocity.y = -1.0;
            self.normalize_velocity();
        }
    }

    fn collide_with_bricks(&mut self) {
        let hit_index = self
            .bricks
            .iter()
            .position(|brick| brick.contains(self.ball));

        if let Some(index) = hit_index {
            self.velocity.y *= -1.0;
            self.score += 10;

            if self.bricks[index].hits_left > 1 {
                self.bricks[index].hits_left -= 1;
            } else {
                self.bricks.remove(index);
            }

            if self.bricks.is_empty() {
                self.mode = Mode::Won;
            }
        }
    }

    fn check_round_state(&mut self) {
        if self.ball.y <= BOARD_HEIGHT as f32 {
            return;
        }

        self.lives = self.lives.saturating_sub(1);

        if self.lives == 0 {
            self.mode = Mode::GameOver;
        } else {
            self.reset_ball_and_paddle();
        }
    }

    fn reset_ball_and_paddle(&mut self) {
        self.ball = Vec2::new(BOARD_WIDTH as f32 / 2.0, BOARD_HEIGHT as f32 - 6.0);
        self.velocity = Vec2::new(if self.lives % 2 == 0 { -0.65 } else { 0.65 }, -1.0);
        self.paddle_x = (BOARD_WIDTH as f32 - PADDLE_WIDTH) / 2.0;
        self.normalize_velocity();
    }

    fn normalize_velocity(&mut self) {
        let length = (self.velocity.x.powi(2) + self.velocity.y.powi(2)).sqrt();

        if length > 0.0 {
            self.velocity.x /= length;
            self.velocity.y /= length;
        }
    }
}

fn build_bricks() -> Vec<Brick> {
    let mut bricks = Vec::new();
    let rows = 5;
    let columns = 12;
    let brick_width = 5;
    let gap = 1;
    let total_width = columns * brick_width + (columns - 1) * gap;
    let start_x = (BOARD_WIDTH - total_width) / 2;

    for row in 0..rows {
        for column in 0..columns {
            bricks.push(Brick {
                x: start_x + column * (brick_width + gap),
                y: 3 + row * 2,
                width: brick_width,
                hits_left: if row < 2 { 2 } else { 1 },
            });
        }
    }

    bricks
}

fn main() -> Result<()> {
    let mut terminal = TerminalSession::start()?;
    let mut game = Game::new();
    let mut last_frame = Instant::now();

    loop {
        let now = Instant::now();
        let dt = now.duration_since(last_frame).as_secs_f32();
        last_frame = now;

        if handle_input(&mut game, dt)? {
            break;
        }

        game.tick(dt);
        render(&mut terminal.stdout, &game)?;

        let elapsed = now.elapsed();
        if elapsed < FRAME_TIME {
            thread::sleep(FRAME_TIME - elapsed);
        }
    }

    Ok(())
}

struct TerminalSession {
    stdout: Stdout,
}

impl TerminalSession {
    fn start() -> Result<Self> {
        terminal::enable_raw_mode()?;

        let mut stdout = stdout();
        execute!(stdout, EnterAlternateScreen, Hide)?;

        Ok(Self { stdout })
    }
}

impl Drop for TerminalSession {
    fn drop(&mut self) {
        let _ = execute!(self.stdout, Show, LeaveAlternateScreen);
        let _ = terminal::disable_raw_mode();
    }
}

fn handle_input(game: &mut Game, dt: f32) -> Result<bool> {
    while event::poll(Duration::from_millis(0))? {
        if let Event::Key(key) = event::read()? {
            match key.code {
                KeyCode::Esc | KeyCode::Char('q') => return Ok(true),
                KeyCode::Left | KeyCode::Char('a') => game.move_paddle(-1.0, dt.max(0.02)),
                KeyCode::Right | KeyCode::Char('d') => game.move_paddle(1.0, dt.max(0.02)),
                KeyCode::Char(' ') => game.toggle_pause(),
                KeyCode::Char('r') if matches!(game.mode, Mode::Won | Mode::GameOver) => {
                    game.restart()
                }
                _ => {}
            }
        }
    }

    Ok(false)
}

fn render(stdout: &mut Stdout, game: &Game) -> Result<()> {
    let (terminal_width, terminal_height) = terminal::size()?;

    queue!(stdout, Clear(ClearType::All), MoveTo(0, 0))?;

    if terminal_width < BOARD_WIDTH as u16 || terminal_height < (BOARD_HEIGHT + 3) as u16 {
        queue!(
            stdout,
            SetForegroundColor(Color::Red),
            Print(format!(
                "Terminal too small. Need at least {}x{}, current size is {}x{}.\r\n",
                BOARD_WIDTH,
                BOARD_HEIGHT + 3,
                terminal_width,
                terminal_height
            )),
            ResetColor
        )?;
        stdout.flush()?;
        return Ok(());
    }

    let mut cells = vec![vec![' '; BOARD_WIDTH as usize]; BOARD_HEIGHT as usize];
    draw_border(&mut cells);
    draw_bricks(&mut cells, &game.bricks);
    draw_paddle(&mut cells, game.paddle_x);
    put_cell(&mut cells, game.ball.x.round() as i32, game.ball.y.round() as i32, '●');

    queue!(
        stdout,
        SetForegroundColor(Color::White),
        Print(format!(
            "Score: {}  Lives: {}  Bricks: {}  {}\r\n",
            game.score,
            game.lives,
            game.bricks.len(),
            mode_label(game.mode)
        )),
        ResetColor
    )?;

    for row in cells {
        for cell in row {
            queue!(stdout, Print(cell))?;
        }
        queue!(stdout, Print("\r\n"))?;
    }

    queue!(
        stdout,
        SetForegroundColor(Color::DarkGrey),
        Print("Controls: ←/a and →/d move, space pauses, r restarts after ending, q quits"),
        ResetColor
    )?;

    stdout.flush()
}

fn draw_border(cells: &mut [Vec<char>]) {
    for x in 0..BOARD_WIDTH {
        put_cell(cells, x, 0, '═');
        put_cell(cells, x, BOARD_HEIGHT - 1, '═');
    }

    for y in 0..BOARD_HEIGHT {
        put_cell(cells, 0, y, '║');
        put_cell(cells, BOARD_WIDTH - 1, y, '║');
    }

    put_cell(cells, 0, 0, '╔');
    put_cell(cells, BOARD_WIDTH - 1, 0, '╗');
    put_cell(cells, 0, BOARD_HEIGHT - 1, '╚');
    put_cell(cells, BOARD_WIDTH - 1, BOARD_HEIGHT - 1, '╝');
}

fn draw_bricks(cells: &mut [Vec<char>], bricks: &[Brick]) {
    for brick in bricks {
        let glyph = if brick.hits_left > 1 { '▓' } else { '▒' };

        for offset in 0..brick.width {
            put_cell(cells, brick.x + offset, brick.y, glyph);
        }
    }
}

fn draw_paddle(cells: &mut [Vec<char>], paddle_x: f32) {
    let start = paddle_x.round() as i32;

    for offset in 0..PADDLE_WIDTH as i32 {
        put_cell(cells, start + offset, BOARD_HEIGHT - 3, '▄');
    }
}

fn put_cell(cells: &mut [Vec<char>], x: i32, y: i32, value: char) {
    if y >= 0 && y < BOARD_HEIGHT && x >= 0 && x < BOARD_WIDTH {
        cells[y as usize][x as usize] = value;
    }
}

fn mode_label(mode: Mode) -> &'static str {
    match mode {
        Mode::Running => "Playing",
        Mode::Paused => "Paused",
        Mode::Won => "You win! Press r to restart.",
        Mode::GameOver => "Game over. Press r to restart.",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn brick_hit_removes_single_hit_brick_and_scores() {
        let mut game = Game::new();
        game.bricks = vec![Brick {
            x: 10,
            y: 5,
            width: 5,
            hits_left: 1,
        }];
        game.ball = Vec2::new(12.0, 5.0);
        game.velocity = Vec2::new(0.0, -1.0);

        game.collide_with_bricks();

        assert!(game.bricks.is_empty());
        assert_eq!(game.score, 10);
        assert_eq!(game.mode, Mode::Won);
        assert!(game.velocity.y > 0.0);
    }

    #[test]
    fn strong_brick_takes_two_hits() {
        let mut game = Game::new();
        game.bricks = vec![Brick {
            x: 10,
            y: 5,
            width: 5,
            hits_left: 2,
        }];
        game.ball = Vec2::new(12.0, 5.0);

        game.collide_with_bricks();

        assert_eq!(game.bricks.len(), 1);
        assert_eq!(game.bricks[0].hits_left, 1);
        assert_eq!(game.score, 10);
    }

    #[test]
    fn paddle_collision_bounces_ball_upward() {
        let mut game = Game::new();
        game.paddle_x = 20.0;
        game.ball = Vec2::new(25.0, (BOARD_HEIGHT - 3) as f32);
        game.velocity = Vec2::new(0.0, 1.0);

        game.collide_with_paddle();

        assert!(game.velocity.y < 0.0);
        assert_eq!(game.ball.y, (BOARD_HEIGHT - 4) as f32);
    }

    #[test]
    fn missing_ball_costs_a_life_and_resets_round() {
        let mut game = Game::new();
        game.ball = Vec2::new(10.0, BOARD_HEIGHT as f32 + 1.0);

        game.check_round_state();

        assert_eq!(game.lives, INITIAL_LIVES - 1);
        assert_eq!(game.mode, Mode::Running);
        assert_eq!(game.ball.y, BOARD_HEIGHT as f32 - 6.0);
    }

    #[test]
    fn game_over_when_last_life_is_lost() {
        let mut game = Game::new();
        game.lives = 1;
        game.ball = Vec2::new(10.0, BOARD_HEIGHT as f32 + 1.0);

        game.check_round_state();

        assert_eq!(game.lives, 0);
        assert_eq!(game.mode, Mode::GameOver);
    }
}
