const canvas = document.querySelector("#game");
const ctx = canvas.getContext("2d");
const scoreEl = document.querySelector("#score");
const livesEl = document.querySelector("#lives");
const levelEl = document.querySelector("#level");
const overlay = document.querySelector("#overlay");
const startButton = document.querySelector("#start-button");
const pauseButton = document.querySelector("#pause-button");
const resetButton = document.querySelector("#reset-button");

const keys = new Set();
const pointer = { active: false, x: canvas.width / 2 };

const game = {
  score: 0,
  lives: 3,
  level: 1,
  running: false,
  paused: false,
  launched: false,
  animationId: 0
};

const paddle = {
  width: 128,
  height: 16,
  x: canvas.width / 2 - 64,
  y: canvas.height - 48,
  speed: 9
};

const ball = {
  radius: 9,
  x: canvas.width / 2,
  y: paddle.y - 12,
  dx: 4,
  dy: -5,
  speed: 6.4
};

const brickLayout = {
  rows: 6,
  columns: 10,
  gap: 10,
  top: 70,
  side: 38,
  height: 24
};

let bricks = [];

const brickColors = ["#7cf7d4", "#43d5ff", "#a98bff", "#ffcc66", "#ff6b96", "#f884ff"];

function createBricks() {
  const availableWidth = canvas.width - brickLayout.side * 2;
  const width = (availableWidth - brickLayout.gap * (brickLayout.columns - 1)) / brickLayout.columns;

  bricks = [];

  for (let row = 0; row < brickLayout.rows; row++) {
    for (let column = 0; column < brickLayout.columns; column++) {
      const toughness = row < 2 && game.level > 1 ? 2 : 1;

      bricks.push({
        x: brickLayout.side + column * (width + brickLayout.gap),
        y: brickLayout.top + row * (brickLayout.height + brickLayout.gap),
        width,
        height: brickLayout.height,
        toughness,
        maxToughness: toughness,
        color: brickColors[row % brickColors.length],
        alive: true
      });
    }
  }
}

function resetBall() {
  game.launched = false;
  ball.x = paddle.x + paddle.width / 2;
  ball.y = paddle.y - ball.radius - 2;
  ball.speed = 6.2 + game.level * 0.25;
  ball.dx = (Math.random() > 0.5 ? 1 : -1) * (3.2 + game.level * 0.2);
  ball.dy = -Math.sqrt(Math.max(ball.speed ** 2 - ball.dx ** 2, 16));
}

function resetGame() {
  cancelAnimationFrame(game.animationId);
  game.score = 0;
  game.lives = 3;
  game.level = 1;
  game.running = false;
  game.paused = false;
  paddle.width = 128;
  paddle.x = canvas.width / 2 - paddle.width / 2;
  createBricks();
  resetBall();
  updateHud();
  showOverlay("Ready?", "Move with ← → or A/D. Press Space to launch.", "Start Game");
  draw();
}

function updateHud() {
  scoreEl.textContent = game.score;
  livesEl.textContent = game.lives;
  levelEl.textContent = game.level;
  pauseButton.textContent = game.paused ? "Resume" : "Pause";
}

function showOverlay(title, message, buttonLabel) {
  overlay.querySelector("h2").textContent = title;
  overlay.querySelector("p").textContent = message;
  startButton.textContent = buttonLabel;
  overlay.classList.remove("hidden");
}

function hideOverlay() {
  overlay.classList.add("hidden");
}

function startGame() {
  if (!game.running && game.lives <= 0) {
    resetGame();
  }
  if (game.running && game.paused) {
    game.paused = false;
    hideOverlay();
    updateHud();
    loop();
    return;
  }

  if (!game.running) {
    game.running = true;
    game.paused = false;
    game.launched = true;
    hideOverlay();
    updateHud();
    loop();
    return;
  }

  if (!game.launched) {
    game.launched = true;
    hideOverlay();
  }
}

function togglePause() {
  if (!game.running) {
    return;
  }

  game.paused = !game.paused;
  updateHud();

  if (game.paused) {
    cancelAnimationFrame(game.animationId);
    showOverlay("Paused", "Press Resume or Space to keep breaking bricks.", "Resume");
  } else {
    hideOverlay();
    loop();
  }
}

function movePaddle() {
  if (keys.has("ArrowLeft") || keys.has("KeyA")) {
    paddle.x -= paddle.speed;
  }

  if (keys.has("ArrowRight") || keys.has("KeyD")) {
    paddle.x += paddle.speed;
  }

  if (pointer.active) {
    paddle.x += (pointer.x - paddle.width / 2 - paddle.x) * 0.22;
  }

  paddle.x = Math.max(0, Math.min(canvas.width - paddle.width, paddle.x));

  if (!game.launched) {
    ball.x = paddle.x + paddle.width / 2;
    ball.y = paddle.y - ball.radius - 2;
  }
}

function updateBall() {
  if (!game.launched) {
    return;
  }

  ball.x += ball.dx;
  ball.y += ball.dy;

  if (ball.x - ball.radius <= 0 || ball.x + ball.radius >= canvas.width) {
    ball.dx *= -1;
    ball.x = Math.max(ball.radius, Math.min(canvas.width - ball.radius, ball.x));
  }

  if (ball.y - ball.radius <= 0) {
    ball.dy *= -1;
    ball.y = ball.radius;
  }

  if (
    ball.y + ball.radius >= paddle.y &&
    ball.y - ball.radius <= paddle.y + paddle.height &&
    ball.x >= paddle.x &&
    ball.x <= paddle.x + paddle.width &&
    ball.dy > 0
  ) {
    const hit = (ball.x - (paddle.x + paddle.width / 2)) / (paddle.width / 2);
    const angle = hit * Math.PI * 0.38;

    ball.dx = Math.sin(angle) * ball.speed;
    ball.dy = -Math.cos(angle) * ball.speed;
    ball.y = paddle.y - ball.radius - 1;
  }

  if (ball.y - ball.radius > canvas.height) {
    game.lives -= 1;
    updateHud();

    if (game.lives <= 0) {
      game.running = false;
      game.paused = false;
      cancelAnimationFrame(game.animationId);
      showOverlay("Game Over", `Final score: ${game.score}`, "Play Again");
      return;
    }

    resetBall();
    showOverlay("Life Lost", "Press Space when you're ready to launch again.", "Launch");
  }
}

function handleBrickCollisions() {
  for (const brick of bricks) {
    if (!brick.alive) {
      continue;
    }

    const closestX = Math.max(brick.x, Math.min(ball.x, brick.x + brick.width));
    const closestY = Math.max(brick.y, Math.min(ball.y, brick.y + brick.height));
    const distanceX = ball.x - closestX;
    const distanceY = ball.y - closestY;

    if (distanceX * distanceX + distanceY * distanceY <= ball.radius * ball.radius) {
      brick.toughness -= 1;

      if (brick.toughness <= 0) {
        brick.alive = false;
        game.score += 100 * game.level;
      } else {
        game.score += 35 * game.level;
      }

      if (Math.abs(distanceX) > Math.abs(distanceY)) {
        ball.dx *= -1;
      } else {
        ball.dy *= -1;
      }

      updateHud();
      break;
    }
  }

  if (bricks.every((brick) => !brick.alive)) {
    game.level += 1;
    game.score += 500;
    paddle.width = Math.max(86, paddle.width - 8);
    createBricks();
    resetBall();
    updateHud();
    showOverlay("Level Clear", `Level ${game.level} is ready.`, "Launch");
  }
}

function drawBackground() {
  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  gradient.addColorStop(0, "#0b1024");
  gradient.addColorStop(0.6, "#101a36");
  gradient.addColorStop(1, "#080c19");

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "rgba(255, 255, 255, 0.05)";

  for (let i = 0; i < 90; i++) {
    const x = (i * 97) % canvas.width;
    const y = (i * 53) % canvas.height;
    ctx.fillRect(x, y, 2, 2);
  }
}

function drawBricks() {
  for (const brick of bricks) {
    if (!brick.alive) {
      continue;
    }

    ctx.save();
    ctx.globalAlpha = brick.toughness / brick.maxToughness * 0.45 + 0.55;
    ctx.fillStyle = brick.color;
    roundRect(brick.x, brick.y, brick.width, brick.height, 8);
    ctx.fill();
    ctx.fillStyle = "rgba(255, 255, 255, 0.28)";
    roundRect(brick.x + 6, brick.y + 5, brick.width - 12, 5, 4);
    ctx.fill();
    ctx.restore();
  }
}

function drawPaddle() {
  const gradient = ctx.createLinearGradient(paddle.x, paddle.y, paddle.x + paddle.width, paddle.y);
  gradient.addColorStop(0, "#7cf7d4");
  gradient.addColorStop(1, "#43d5ff");
  ctx.fillStyle = gradient;
  roundRect(paddle.x, paddle.y, paddle.width, paddle.height, 999);
  ctx.fill();
}

function drawBall() {
  const glow = ctx.createRadialGradient(ball.x, ball.y, 2, ball.x, ball.y, ball.radius * 3);
  glow.addColorStop(0, "rgba(255, 255, 255, 0.95)");
  glow.addColorStop(0.24, "rgba(124, 247, 212, 0.9)");
  glow.addColorStop(1, "rgba(124, 247, 212, 0)");

  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(ball.x, ball.y, ball.radius * 3, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#f6f8ff";
  ctx.beginPath();
  ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
  ctx.fill();
}

function draw() {
  drawBackground();
  drawBricks();
  drawPaddle();
  drawBall();
}

function loop() {
  if (!game.running || game.paused) {
    return;
  }

  movePaddle();
  updateBall();
  handleBrickCollisions();
  draw();
  game.animationId = requestAnimationFrame(loop);
}

function roundRect(x, y, width, height, radius) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.arcTo(x + width, y, x + width, y + height, radius);
  ctx.arcTo(x + width, y + height, x, y + height, radius);
  ctx.arcTo(x, y + height, x, y, radius);
  ctx.arcTo(x, y, x + width, y, radius);
  ctx.closePath();
}

function canvasPoint(event) {
  const rect = canvas.getBoundingClientRect();
  const clientX = event.touches ? event.touches[0].clientX : event.clientX;
  return (clientX - rect.left) * (canvas.width / rect.width);
}

window.addEventListener("keydown", (event) => {
  keys.add(event.code);

  if (event.code === "Space") {
    event.preventDefault();

    if (!game.running || game.paused || !game.launched) {
      startGame();
    }
  }

  if (event.code === "KeyP") {
    togglePause();
  }
});

window.addEventListener("keyup", (event) => {
  keys.delete(event.code);
});

canvas.addEventListener("pointermove", (event) => {
  pointer.active = true;
  pointer.x = canvasPoint(event);
});

canvas.addEventListener("pointerleave", () => {
  pointer.active = false;
});

canvas.addEventListener("touchmove", (event) => {
  event.preventDefault();
  pointer.active = true;
  pointer.x = canvasPoint(event);
}, { passive: false });

startButton.addEventListener("click", startGame);
pauseButton.addEventListener("click", togglePause);
resetButton.addEventListener("click", resetGame);

resetGame();
