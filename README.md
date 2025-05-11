# 🎮 Cute Territory Game

A colorful, grid-based territory capture game with power-ups, built using Pygame!

![Cute Territory Game](./Demo.mp4)

## 🌟 Features

- **Dual Game Modes**: Human vs AI or AI vs AI gameplay
- **Adjustable Difficulty**: Normal or Hard AI opponents
- **Power-ups System**: Freeze opponents or collect bonus points
- **Color Customization**: Choose your player colors from various options
- **Pink Aesthetic Design**: Cute visual style with animated backgrounds
- **Territory-based Scoring**: Capture cells to earn points and dominate the grid

## 🎯 How to Play

### Basic Rules
1. Blue and Green players take turns moving around the grid
2. Each player claims territories by moving over cells
3. Players can steal territories from opponents
4. The player with the most territory (points) when the timer runs out wins!

### Controls
- **Human Player**: Arrow keys (↑, ↓, ←, →)
- **Menu Navigation**: Mouse clicks or Enter/Escape keys
- **Exit Game**: Escape key from main menu

### Power-ups
- **❄️ Freeze (Blue)**: Temporarily prevents your opponent from moving
- **⭐ Points (Gold)**: Instantly gives you bonus points

## 🛠️ Installation

### Requirements
- Python 3.x
- Pygame library

### Setup
```bash
# Clone this repository
git clone https://github.com/0xUsmanGhani/Territory-Game.git

# Navigate to the project directory
cd Territory-Game

# Install Pygame if you don't have it
pip install pygame

# Run the game
python game.py
```

### Optional: Custom Background Music
For the full experience, add your own background music file:
- Name it `background.mp3`
- Place it in the same directory as `game.py`

## 🎨 Game Design

### Grid System
- 20x20 grid with customizable player colors
- Each cell can be unclaimed or owned by a player
- Info panel shows scores, time, and power-up legend

### AI Behavior
- AI prioritizes collecting power-ups
- Next priority is capturing unclaimed or opponent cells
- AI smartness varies by difficulty level

### Game Flow
1. Start at main menu
2. Select game mode (Human vs AI or AI vs AI)
3. Choose difficulty (Normal or Hard)
4. Play for 60 seconds
5. The player with the most territory wins!

## 🔧 Customization Options

- **Player Colors**: Choose from 5 color options for each player
- **Game Speed**: Adjusts automatically based on difficulty

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📝 Future Enhancements

- Additional game modes (2-player human mode)
- More power-up types
- Custom map layouts
- Sound effects for actions
- Settings for game time and grid size
- High score system

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
Made with ❤️ and Pygame