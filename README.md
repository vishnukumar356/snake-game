# 🐍 Snake Game

A simple, fully playable Snake game built with **vanilla HTML, CSS and JavaScript** — no frameworks, no dependencies. Just open `index.html` in any browser and play!

---

## 🚀 How to Run

1. Clone or download this repository.
2. Open `index.html` in any modern web browser (Chrome, Firefox, Edge, Safari).
3. Click **▶ Start** and use the arrow keys (or on-screen buttons) to play.

---

## 🕹️ Controls

| Key / Button | Action |
|---|---|
| `Arrow Up / Down / Left / Right` | Change direction |
| `Space` | Pause / Resume |
| ▶ Start | Start a new game |
| ⏸ Pause | Pause / Resume |
| 🔄 Restart | Restart immediately |

---

## 📁 File Structure

```
snake-game/
├── index.html   ← Page structure (canvas, buttons, scoreboard)
├── style.css    ← Visual styling (dark theme, layout)
├── game.js      ← All game logic (heavily commented)
└── README.md    ← This file
```

---

## 🧠 Programming Concepts Explained

The source code in `game.js` is **heavily commented** to teach the key concepts. Here is a summary:

### 1. Canvas & 2D Rendering
The game draws every frame onto an HTML `<canvas>` element using the **Canvas 2D API** (`ctx.fillRect`, `ctx.arc`, etc.). The canvas is divided into a grid of 20×20 cells.

### 2. Game Loop
`setInterval(tick, 150)` calls the `tick()` function every 150 ms. Each tick:
- Updates the game state (`moveSnake`)
- Re-renders the canvas (`draw`)

This is the fundamental **game loop** pattern used in almost every game engine.

### 3. Snake as an Array
The snake is stored as an **array of `{x, y}` objects**:
```js
[ {x:10, y:10}, {x:9, y:10}, {x:8, y:10} ]
  ^--- HEAD
```
- **Move forward** → `unshift` a new head + `pop` the tail.
- **Eat food** → `unshift` a new head, skip the `pop` (snake grows).

### 4. Direction Buffering
A `nextDir` variable stores the player's latest key press. It is only applied at the **start of each tick**, preventing the snake from reversing into itself mid-tick.

### 5. Collision Detection
Two types are checked every tick:
- **Wall**: is the new head outside the grid boundaries?
- **Self**: does `Array.some()` find any segment matching the new head's coordinates?

### 6. Food Spawning
A random grid cell is picked in a `do...while` loop, retrying until the chosen cell does not overlap any snake segment.

### 7. Score & High Score
Score increases by 10 each time food is eaten. High score is kept in a variable for the whole browser session.

### 8. Game States
The game has four logical states managed with boolean flags:
`idle` → `running` ↔ `paused` → `game over` → `idle`

---

## 📸 Preview

> Dark-themed board with a teal snake and red food. Score and high-score are shown above the canvas.

---

## 📜 License

MIT — free to use, modify, and distribute.
