# Pixel Game Fun

<img src="screenshots/main.png">

## Description

Pixel Game Fun is a 2D pixel art game developed using Python and the Pygame library. It features a western-themed adventure where players control a character named Leha, navigate platforms, interact with objects like a car, engage in combat by shooting bullets, and explore a scrolling environment filled with clouds and obstacles.

## Features

- **Character Movement**: Smooth left/right movement, jumping mechanics, and side-changing animations.
- **Combat System**: Attack animations and bullet shooting with reloading mechanics.
- **Vehicle Interaction**: Ability to enter and drive a car (BMW) for enhanced mobility.
- **Dynamic Environment**: Scrolling background, moving clouds, and interactive platforms.
- **Audio**: Background music with toggle functionality via an on-screen button.
- **Pixel Art Style**: Retro pixel graphics for characters, objects, and backgrounds.

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Ensure Python 3.x is installed on your system.
2. Clone or download the project repository.
3. Navigate to the project directory.
4. Install the required dependencies using pip:

   ```
   pip install -r requirements.txt
   ```

## How to Run

1. Open a terminal or command prompt.
2. Navigate to the project directory.
3. Run the game with the following command:

   ```
   python game.py
   ```

## Controls

- **Arrow Keys**:
  - Left/Right: Move the character left or right.
  - Up: Jump.
- **Enter**: Perform an attack animation.
- **Left Shift + Enter**: Shoot bullets (when attacking).
- **E**: Interact with the car (enter/exit).
- **Mouse Click**: Click the music button to play/pause background music.

## Project Structure

```
pixel-game-fun/
├── game.py                 # Main game script
├── requirements.txt        # Python dependencies
├── music/                  # Audio files
│   ├── Leha.mp3
│   ├── Leha.txt
│   └── western.mp3
└── textures/               # Game assets
    ├── actors/             # Character sprites
    │   ├── BMW/            # Car sprites
    │   ├── Leha/           # Player character sprites
    │   └── Sancho/         # Unused character sprites
    ├── objects/            # Object sprites (bullets, clouds, stones)
    └── static/             # Static assets (background, buttons, platforms)
```

## Game Mechanics

- **Platforms**: The game includes a main platform and randomly placed stone platforms for jumping and navigation.
- **Bullets**: Fired in pairs during attacks, with a reloading cooldown.
- **Car Driving**: Entering the car allows faster movement and scene scrolling.
- **Scene Scrolling**: The background and objects move when the player reaches screen edges, creating an infinite side-scrolling effect.
- **Clouds**: Randomly generated clouds that drift across the screen for ambiance.

## Credits

- Developed using Pygame.
- Pixel art assets sourced from various free resources.

## License

This project is for educational purposes. Please ensure compliance with asset licenses.
