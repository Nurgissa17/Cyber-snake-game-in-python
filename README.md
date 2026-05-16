Cyber Snake: Data Escape
Data Escape is a neon cyber-style Snake game made with Python and Pygame.
The player controls a snake, collects food, avoids red traps, and tries to reach the maximum score.

## Requirements
- Python 3
- Pygame

Install Pygame if needed:
pip install pygame


## How To Run
Open the project folder and run:
python main.py

If `python` does not work on your computer, try:
py main.py


## Main Menu Controls

- `Enter` - Start game
- `L` - Open leaderboard
- `S` - Open settings
- `Esc` - Exit game

## Settings

The settings menu lets the player change:

- `Start Speed` - the snake speed at the beginning of the game
- `Food Speed +` - how much faster the snake becomes after eating food

Controls:

- `Up` / `Down` - Choose setting
- `Left` / `Right` - Change value
- `Backspace` - Return to main menu

## Gameplay Controls

- `Up`, `Down`, `Left`, `Right` - Move the snake
- `P` - Pause or unpause
- `Esc` - Exit game

## Food And Traps

- Blue food gives `+1` point
- Gold food gives `+5` points
- Red traps give `-3` points
- Food appears in a fixed cycle: 4 blue foods, then 1 gold food
- The game starts with 12 red traps
- Each blue food adds 2 red traps
- Each gold food adds 4 red traps

## Winning

The maximum score is `20` points.

When the player reaches the maximum score, the game ends with a congratulations screen:
CONGRATULATIONS!
YOU HAVE REACHED THE MAXIMUM POINTS!


Win screen controls:

- `R` - Restart
- `M` - Main menu
- `L` - Leaderboard
- `Esc` - Exit game

## Losing

The game ends if:

- The snake hits the playground border
- The snake hits itself
- The score becomes negative after touching red traps

Game over controls:

- `R` - Restart
- `M` - Main menu
- `L` - Leaderboard
- `Esc` - Exit game

## Leaderboard

The leaderboard saves scores in `scores.json`.

Controls:

- `Mouse wheel` - Scroll smoothly
- `Up` / `Down` - Scroll
- `D` - Clear leaderboard
- `Backspace` - Return

Leaderboard entries are shown as attempts, for example:
Attempt 1
Attempt 2
Attempt 3


## Project Files

- `main.py` - Starts the game
- `game.py` - Main game logic, menus, HUD, and screens
- `snake.py` - Snake movement and drawing
- `items.py` - Food and trap logic
- `score_manager.py` - Leaderboard save/load/clear logic
- `utils.py` - Shared constants and helper functions
- `scores.json` - Saved leaderboard data
