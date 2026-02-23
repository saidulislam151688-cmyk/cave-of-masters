# CAVE OF MASTERS

A deep offline combat-focused RPG where you explore mystical caves, defeat combat masters, learn new mechanics, and build your personalized warrior.

## Features

- **Deep Combat System**: Attack, dodge, block, parry, combos
- **5 Unique Caves**: Each with different themes and master bosses
- **Progression System**: Level up, unlock abilities, master combat
- **Enemy Variety**: Minions, Soldiers, Elites, Guardians, and Bosses
- **Save System**: Your progress is automatically saved
- **Touch Controls**: On-screen buttons for mobile play

## Controls

### Keyboard (Desktop)
- **A/D** or **Arrow Keys**: Move left/right
- **W** or **Space**: Jump
- **J** or **Z**: Light Attack
- **K** or **X**: Heavy Attack
- **L** or **C**: Kick
- **S** or **Down**: Dodge
- **Ctrl**: Block
- **P**: Parry
- **Enter**: Start/Select

### Touch (Mobile)
- Left side: Movement and Jump buttons
- Right side: Attack, Block, Dodge buttons

## Installation

### Option 1: Run in Termux (Recommended for Android)

```bash
# Install Python and dependencies
pkg update && pkg install python

# Install pygame
pip install pygame

# Download and run
git clone <this-repo>
cd cave_of_masters
python cave_of_masters.py
```

### Option 2: Build APK (Advanced)

```bash
# Install buildozer
pip install buildozer

# Build Android APK
cd android_project
buildozer android debug
```

## Gameplay

1. **Start Game**: Enter your name and begin your journey
2. **Hub World**: Prepare for cave exploration
3. **Enter Cave**: Fight through rooms of enemies
4. **Defeat Boss**: Unlock new abilities
5. **Progress**: Complete all 5 caves to become a legend

## Cave Progression

| Cave | Theme | Master | Reward |
|------|-------|--------|--------|
| 1 | Stone Temple | Stone Master | Dash Cancel |
| 2 | Wind Spiral | Wind Master | Air Combo |
| 3 | Flame Core | Fire Master | Perfect Parry |
| 4 | Shadow Realm | Shadow Master | Shadow Clone |
| 5 | Void Depths | Void Master | Stance Switch |

## Combat Tips

- **Combos**: Chain attacks by pressing attack buttons quickly
- **Parry**: Time your block right to parry enemy attacks
- **Dodge**: Use dodge to avoid damage and reposition
- **Focus**: Build focus by hitting enemies, use for special actions

## Requirements

- Python 3.7+
- Pygame 2 .0+
-100MB storage space
- Any modern device

## License

MIT License

## Credits

Developed with AI assistance
