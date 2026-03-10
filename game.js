// ─────────────────────────────────────────────
//  Snake Game — game.js
//  Concepts covered (see comments throughout):
//    1. Canvas & rendering
//    2. Game loop with setInterval
//    3. Snake data structure (array of segments)
//    4. Movement & direction logic
//    5. Collision detection
//    6. Food spawning
//    7. Score & high-score tracking
//    8. Game states (idle / running / paused / over)
// ─────────────────────────────────────────────


// ── 1. CANVAS SETUP ──────────────────────────
// We draw everything on an HTML <canvas> element.
// Each "cell" in the grid is CELL_SIZE × CELL_SIZE pixels.
const canvas  = document.getElementById('gameCanvas');
const ctx     = canvas.getContext('2d');   // 2D drawing context

const CELL_SIZE  = 20;                          // pixels per grid cell
const COLS       = canvas.width  / CELL_SIZE;   // 20 columns
const ROWS       = canvas.height / CELL_SIZE;   // 20 rows
const SPEED_MS   = 150;                         // ms between each game tick


// ── UI ELEMENTS ───────────────────────────────
const scoreEl     = document.getElementById('score');
const highScoreEl = document.getElementById('high-score');
const startBtn    = document.getElementById('startBtn');
const pauseBtn    = document.getElementById('pauseBtn');
const restartBtn  = document.getElementById('restartBtn');


// ── 2. GAME STATE ─────────────────────────────
// These variables hold ALL the information about the current game.
let snake;        // array of {x, y} segments — index 0 is the HEAD
let direction;    // current movement direction: 'UP' | 'DOWN' | 'LEFT' | 'RIGHT'
let nextDir;      // buffered next direction (prevents double-reverse in one tick)
let food;         // {x, y} position of the current food item
let score;        // current score
let highScore = 0;
let gameLoop;     // reference to the setInterval timer
let isPaused = false;
let isRunning = false;


// ── 3. SNAKE DATA STRUCTURE ───────────────────
// The snake is an ARRAY of cell coordinates, e.g.:
//   [ {x:10, y:10}, {x:9, y:10}, {x:8, y:10} ]
//   Head ──────────^
// When the snake moves:
//   • A new head cell is added to the FRONT of the array (unshift)
//   • The tail cell is removed from the END            (pop)
// When food is eaten, we skip the pop → snake grows by 1.

function initGame() {
  // Place the snake in the middle of the board, 3 cells long, moving right
  const midX = Math.floor(COLS / 2);
  const midY = Math.floor(ROWS / 2);
  snake     = [
    { x: midX,     y: midY },
    { x: midX - 1, y: midY },
    { x: midX - 2, y: midY },
  ];
  direction = 'RIGHT';
  nextDir   = 'RIGHT';
  score     = 0;
  updateScoreDisplay();
  spawnFood();
}


// ── 4. MOVEMENT & DIRECTION ───────────────────
// Each tick we calculate where the head will be NEXT,
// then shift all segments forward.

function moveSnake() {
  direction = nextDir;   // apply buffered direction

  // Calculate the new head position based on current direction
  const head = snake[0];
  let newHead;

  if      (direction === 'UP')    newHead = { x: head.x,     y: head.y - 1 };
  else if (direction === 'DOWN')  newHead = { x: head.x,     y: head.y + 1 };
  else if (direction === 'LEFT')  newHead = { x: head.x - 1, y: head.y     };
  else                            newHead = { x: head.x + 1, y: head.y     };  // RIGHT

  // ── 5. COLLISION DETECTION ───────────────────
  // Wall collision — did we go outside the grid?
  if (newHead.x < 0 || newHead.x >= COLS ||
      newHead.y < 0 || newHead.y >= ROWS) {
    endGame();
    return;
  }

  // Self collision — did the new head land on any existing segment?
  // Array.some() returns true if ANY element satisfies the condition.
  const hitSelf = snake.some(seg => seg.x === newHead.x && seg.y === newHead.y);
  if (hitSelf) {
    endGame();
    return;
  }

  // Move forward: add new head at the front
  snake.unshift(newHead);

  // ── 6. FOOD LOGIC ────────────────────────────
  // Did the new head land on the food?
  if (newHead.x === food.x && newHead.y === food.y) {
    // Grow: do NOT remove the tail this tick
    score += 10;
    updateScoreDisplay();
    spawnFood();
  } else {
    // Normal move: remove the last tail segment
    snake.pop();
  }
}


// ── 6. FOOD SPAWNING ─────────────────────────
// Pick a random cell that is NOT occupied by the snake.

function spawnFood() {
  let candidate;
  do {
    candidate = {
      x: Math.floor(Math.random() * COLS),
      y: Math.floor(Math.random() * ROWS),
    };
  // Keep trying until the candidate cell is free
  } while (snake.some(seg => seg.x === candidate.x && seg.y === candidate.y));
  food = candidate;
}


// ── 7. SCORE DISPLAY ─────────────────────────
function updateScoreDisplay() {
  scoreEl.textContent = score;
  if (score > highScore) {
    highScore = score;
    highScoreEl.textContent = highScore;
  }
}


// ── 1. RENDERING ─────────────────────────────
// Called every tick to redraw the canvas.

function draw() {
  // Clear the whole canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw food — a red circle
  ctx.fillStyle = '#e94560';
  ctx.beginPath();
  ctx.arc(
    food.x * CELL_SIZE + CELL_SIZE / 2,   // center X
    food.y * CELL_SIZE + CELL_SIZE / 2,   // center Y
    CELL_SIZE / 2 - 2,                    // radius
    0, Math.PI * 2
  );
  ctx.fill();

  // Draw snake segments
  snake.forEach((seg, index) => {
    // Head is brighter than the body
    ctx.fillStyle = index === 0 ? '#4ecca3' : '#2eaf87';
    ctx.fillRect(
      seg.x * CELL_SIZE + 1,   // +1 creates a small gap between cells
      seg.y * CELL_SIZE + 1,
      CELL_SIZE - 2,
      CELL_SIZE - 2
    );
  });

  // Draw "PAUSED" overlay
  if (isPaused) {
    ctx.fillStyle = 'rgba(0,0,0,0.45)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#4ecca3';
    ctx.font = 'bold 36px Segoe UI';
    ctx.textAlign = 'center';
    ctx.fillText('PAUSED', canvas.width / 2, canvas.height / 2);
  }
}


// ── 2. GAME LOOP ─────────────────────────────
// setInterval calls our tick() function every SPEED_MS milliseconds.
// This is the heartbeat of the game.

function tick() {
  if (!isPaused) {
    moveSnake();   // update state
    draw();        // render new state
  }
}

function startGame() {
  if (isRunning) return;
  isRunning = true;
  isPaused  = false;
  initGame();
  draw();  // draw initial frame before first tick
  gameLoop = setInterval(tick, SPEED_MS);
  startBtn.disabled   = true;
  pauseBtn.disabled   = false;
  restartBtn.disabled = false;
}

function pauseGame() {
  if (!isRunning) return;
  isPaused = !isPaused;
  pauseBtn.textContent = isPaused ? '▶ Resume' : '⏸ Pause';
  if (isPaused) draw();  // show PAUSED overlay immediately
}

function restartGame() {
  clearInterval(gameLoop);
  isRunning = false;
  isPaused  = false;
  pauseBtn.textContent = '⏸ Pause';
  startGame();
}

function endGame() {
  clearInterval(gameLoop);
  isRunning = false;

  // Draw "GAME OVER" overlay
  ctx.fillStyle = 'rgba(0,0,0,0.55)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#e94560';
  ctx.font = 'bold 36px Segoe UI';
  ctx.textAlign = 'center';
  ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2 - 16);
  ctx.fillStyle = '#eaeaea';
  ctx.font = '20px Segoe UI';
  ctx.fillText(`Score: ${score}`, canvas.width / 2, canvas.height / 2 + 20);

  startBtn.disabled   = false;
  pauseBtn.disabled   = true;
  restartBtn.disabled = false;
}


// ── KEYBOARD INPUT ────────────────────────────
// We buffer the new direction in `nextDir` instead of applying it immediately,
// which prevents the snake from reversing into itself if two keys are
// pressed within the same tick.

document.addEventListener('keydown', (e) => {
  switch (e.key) {
    case 'ArrowUp':
      if (direction !== 'DOWN')  nextDir = 'UP';
      e.preventDefault();   // prevent page scrolling
      break;
    case 'ArrowDown':
      if (direction !== 'UP')    nextDir = 'DOWN';
      e.preventDefault();
      break;
    case 'ArrowLeft':
      if (direction !== 'RIGHT') nextDir = 'LEFT';
      e.preventDefault();
      break;
    case 'ArrowRight':
      if (direction !== 'LEFT')  nextDir = 'RIGHT';
      e.preventDefault();
      break;
    case ' ':
      pauseGame();
      e.preventDefault();
      break;
  }
});


// ── ON-SCREEN BUTTON INPUT ────────────────────
document.getElementById('btn-up').addEventListener('click',    () => { if (direction !== 'DOWN')  nextDir = 'UP';    });
document.getElementById('btn-down').addEventListener('click',  () => { if (direction !== 'UP')    nextDir = 'DOWN';  });
document.getElementById('btn-left').addEventListener('click',  () => { if (direction !== 'RIGHT') nextDir = 'LEFT';  });
document.getElementById('btn-right').addEventListener('click', () => { if (direction !== 'LEFT')  nextDir = 'RIGHT'; });


// ── CONTROL BUTTONS ───────────────────────────
startBtn.addEventListener('click',   startGame);
pauseBtn.addEventListener('click',   pauseGame);
restartBtn.addEventListener('click', restartGame);


// ── DRAW IDLE SCREEN ──────────────────────────
// Show a welcome message before the game starts.
(function drawIdleScreen() {
  ctx.fillStyle = '#4ecca3';
  ctx.font = 'bold 28px Segoe UI';
  ctx.textAlign = 'center';
  ctx.fillText('🐍 Snake Game', canvas.width / 2, canvas.height / 2 - 16);
  ctx.fillStyle = '#aaa';
  ctx.font = '18px Segoe UI';
  ctx.fillText('Press ▶ Start to play', canvas.width / 2, canvas.height / 2 + 20);
})();

