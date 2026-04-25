# Asteroids+

Small arcade-style Asteroids clone built with Pygame.

## Features

- Rotating ship movement with primary shots and limited rockets
- Screen wrapping for the player and asteroids
- Projectiles expire off-screen instead of looping back into view
- Wave progression with increasing asteroid pressure
- Lives, respawn invulnerability, pause, and restart support
- Rocket pickups can drop from larger asteroid takedowns
- Visual refresh with gradient background, starfield, thrust flame, and improved HUD
- Persistent local high scores with player-name entry after each run
- Lightweight JSONL state and event logging for debugging

## Requirements

- Python 3.13+
- Pygame 2.6.1

## Run

```bash
python main.py
```

If you use `uv`, this also works:

```bash
uv run python main.py
```

## Controls

- `W`: thrust forward
- `S`: reverse thrust
- `A` / `D`: rotate
- `Space`: fire standard shot
- `N`: fire rocket
- `B`: fire pulse weapon
- `P`: pause or resume
- `R`: restart after game over

## Gameplay Notes

- You start with 3 lives.
- Clearing a wave starts the next wave after a short delay.
- Each new wave increases the spawn rate and adds at least one extra rocket.
- Larger asteroids can drop rocket pickups worth 2 rockets.
- Rare cyan pickups restore 1 pulse charge.
- After losing a life, the ship respawns in the center with a brief invulnerability window.
- When a run ends, enter a pilot name and press `Enter` to save the score locally.

## High Scores

- Scores are stored locally in `high_scores.json`.
- The game keeps the top 5 scores, ranked by score and then wave reached.

## Logs

Running the game writes debug data to:

- `game_state.jsonl`
- `game_events.jsonl`
