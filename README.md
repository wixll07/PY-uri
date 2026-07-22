# PYuri

PYuri is an endless 2D platform game developed in Python with the Pygame library.
The player runs through procedurally generated platforms, collects coins, avoids enemies, and tries to beat the distance record.

## Features

- Endless side-scrolling gameplay
- Procedurally generated platforms
- Player animations: running, jumping, crouching, kicking and death
- Animated coins and enemies
- Double jump
- Score and distance record
- Sound effects and background music
- Pause and restart controls

## Controls

- **Up Arrow / Z**: jump
- **Down Arrow / S**: crouch or slide
- **Esc**: pause or resume
- **R**: restart the current game

## Installation

1. Install Python 3.10 or later.
2. Install the dependency:

```bash
pip install -r requirements.txt
```

3. Start the game:

```bash
python main.py
```

## Project structure

```text
PYuri/
├── main.py
├── assets/
│   ├── audio/
│   ├── images/
│   └── tiles/
├── drafts/
├── requirements.txt
└── README.md
```

The `drafts/` directory contains early experiments and development tests. It is kept separate from the playable version.

## Technologies

- Python
- Pygame

## What I learned

This project helped me practice object-oriented concepts, event handling, animation, collision detection, procedural generation, asset management and project organization.

## Copyright

Copyright © 2026 Wissal Laghmich. All rights reserved.
No license is granted for reuse, modification, distribution or commercial use of this source code or its assets without written permission.
