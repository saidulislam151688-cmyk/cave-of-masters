#!/bin/bash
# CAVE OF MASTERS - Android Launcher Script
# Run this in Termux to play the game

echo "======================================"
echo "  CAVE OF MASTERS - Android Launcher"
echo "======================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    pkg update && pkg install python
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    pkg install python-pip
fi

# Install pygame
echo "Installing pygame..."
pip install --user pygame

# Download game if not exists
GAME_DIR="$HOME/cave_of_masters"
if [ ! -d "$GAME_DIR" ]; then
    echo "Downloading game..."
    mkdir -p "$GAME_DIR"
    # Copy from current location if available
    if [ -f "/root/cave_of_masters/cave_of_masters.py" ]; then
        cp /root/cave_of_masters/cave_of_masters.py "$GAME_DIR/"
    fi
fi

# Check for touchscreen support
echo ""
echo "Starting game with touch controls..."
echo "Use on-screen buttons to play"
echo ""

# Run the game
cd "$GAME_DIR"
python3 cave_of_masters.py

echo ""
echo "Game closed. Thanks for playing!"
