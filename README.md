# 🐍 Snake Game

A simple, fully playable Snake game built with **Python** and **pygame** — no web browser needed. Run it directly from your terminal!

---

## 🚀 How to Run

### 1. Install Python
Make sure you have **Python 3.8 or newer** (including 3.14+) installed from [python.org](https://www.python.org/downloads/).

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the game
```bash
python snake.py
```

---

## 🕹️ Controls

| Key          | Action          |
|--------------|-----------------|
| `Arrow Keys` | Change direction|
| `Space`      | Pause / Resume  |
| `Enter`      | Start / Restart |
| `Q` / `Esc`  | Quit the game   |

---

## 📁 File Structure

```
snake-game/
├── snake.py          ← All game logic (heavily commented)
├── requirements.txt  ← Python dependencies (pygame)
└── README.md         ← This file
```

---

## 🧠 Programming Concepts Explained

The source code in `snake.py` is **heavily commented** to teach the key concepts:

### 1. pygame Setup & Window
`pygame.init()` starts all pygame sub-systems. A window is created with `pygame.display.set_mode()`.

### 2. Game Loop
A `while True` loop runs continuously. `clock.tick(FPS)` caps the speed to a fixed number of frames per second.

### 3. Snake Data Structure
The snake is a **Python list** of `(col, row)` tuples. Index `0` is always the head:
```python
snake = [(10, 10), (9, 10), (8, 10)]
#         ^--- HEAD
```

### 4. Movement Logic
Every tick:
- Calculate new head from current direction
- `insert(0, new_head)` — add new head at the front
- `pop()` — remove the tail (skip this step when food is eaten → snake grows)

### 5. Collision Detection
- **Wall collision** — head goes outside grid bounds → Game Over
- **Self collision** — head position exists elsewhere in the list → Game Over

### 6. Food Spawning
`random.choice()` picks a free grid cell that is not occupied by the snake.

### 7. Score & High Score
Score increases each time food is eaten. High score is tracked in memory for the session.

### 8. Game States
The game uses simple string constants as state names:
```python
STATE_START    = 'START'
STATE_RUNNING  = 'RUNNING'
STATE_PAUSED   = 'PAUSED'
STATE_GAME_OVER= 'GAME_OVER'
```

### 9. Drawing / Rendering
`pygame.draw.rect()` draws every grid cell. The snake head, body, food, and UI panels are all drawn each frame.

### 10. Keyboard Input
`pygame.event.get()` collects all events each frame. `KEYDOWN` events are checked to handle direction changes and state transitions.

---

## 📦 Requirements

| Package   | Version  |
|-----------|----------|
| pygame-ce | >= 2.5.0 |

Install via:
```bash
pip install pygame-ce
```
