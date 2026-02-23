"""
SAVE SYSTEM - Professional save/load functionality
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

SAVE_DIR = os.path.expanduser("~/.cave_of_masters")
SAVE_FILE = os.path.join(SAVE_DIR, "save_data.json")


def ensure_save_dir():
    """Ensure save directory exists"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def create_default_save() -> Dict[str, Any]:
    """Create default save data"""
    return {
        "version": "1.0.0",
        "created": datetime.now().isoformat(),
        "last_played": datetime.now().isoformat(),
        "player": {
            "name": "Warrior",
            "level": 1,
            "xp": 0,
            "xp_to_next": 100,
            "stats": {
                "max_health": 100,
                "health": 100,
                "max_stamina": 50,
                "stamina": 50,
                "max_focus": 30,
                "focus": 30,
                "attack": 10,
                "defense": 5,
                "speed": 100
            },
            "build": {
                "style": "balanced",
                "masters": ["basic"],
                "abilities": ["light", "heavy", "kick"],
                "weapons": ["fists"],
                "current_weapon": "fists",
                "stances": ["normal"]
            }
        },
        "progression": {
            "caves_completed": [],
            "current_cave": 1,
            "total_enemies_killed": 0,
            "total_damage_dealt": 0,
            "total_damage_taken": 0,
            "best_combo": 0,
            "survival_best": 0,
            "training": {
                "heat_chamber": 0,
                "balance_pillars": 0,
                "stone_post": 0,
                "flow_water": 0,
                "meditation": 0,
                "iron_sandbox": 0
            }
        },
        "unlocks": {
            "caves": [1],
            "masters": ["basic"],
            "weapons": ["fists"],
            "skills": [],
            "training_rooms": ["heat_chamber"],
            "transformations": []
        },
        "settings": {
            "difficulty": "normal",
            "music_volume": 0.7,
            "sfx_volume": 1.0,
            "vibration": True,
            "show_fps": False
        },
        "stats": {
            "total_playtime": 0,
            "games_played": 0,
            "victories": 0,
            "defeats": 0
        }
    }


def save_game(player, game_state, settings=None):
    """Save game data"""
    ensure_save_dir()
    
    save_data = create_default_save()
    
    # Update player data
    if player:
        save_data["player"]["name"] = player.name if hasattr(player, 'name') else "Warrior"
        save_data["player"]["level"] = player.level
        save_data["player"]["xp"] = player.xp
        save_data["player"]["xp_to_next"] = player.xp_to_next
        
        if hasattr(player, 'max_health'):
            save_data["player"]["stats"]["max_health"] = player.max_health
            save_data["player"]["stats"]["health"] = player.health
            save_data["player"]["stats"]["max_stamina"] = player.max_stamina
            save_data["player"]["stats"]["stamina"] = player.stamina
            save_data["player"]["stats"]["max_focus"] = player.max_focus
            save_data["player"]["stats"]["focus"] = player.focus
            save_data["player"]["stats"]["attack"] = player.attack_power
            save_data["player"]["stats"]["defense"] = player.defense
        
        if hasattr(player, 'masters_unlocked'):
            save_data["player"]["build"]["masters"] = player.masters_unlocked
        if hasattr(player, 'abilities'):
            save_data["player"]["build"]["abilities"] = player.abilities
        if hasattr(player, 'fighting_style'):
            save_data["player"]["build"]["style"] = player.fighting_style
    
    # Update game state
    if game_state:
        save_data["progression"]["current_cave"] = game_state.get('current_cave', 1)
    
    # Update settings
    if settings:
        save_data["settings"].update(settings)
    
    # Save to file
    with open(SAVE_FILE, 'w') as f:
        json.dump(save_data, f, indent=2)
    
    return True


def load_game() -> Dict[str, Any]:
    """Load game data"""
    ensure_save_dir()
    
    if not os.path.exists(SAVE_FILE):
        return create_default_save()
    
    try:
        with open(SAVE_FILE, 'r') as f:
            save_data = json.load(f)
        
        # Handle version migration
        if save_data.get("version", "1.0.0") < "1.0.0":
            # Migration logic here
            pass
        
        return save_data
    except Exception as e:
        print(f"Error loading save: {e}")
        return create_default_save()


def delete_save():
    """Delete save file"""
    ensure_save_dir()
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


def save_exists() -> bool:
    """Check if save exists"""
    return os.path.exists(SAVE_FILE)


# ==================== AUTO-SAVE ====================
class AutoSave:
    """Auto-save manager"""
    
    def __init__(self, interval_seconds=60):
        self.interval = interval_seconds
        self.last_save = 0
        self.dirty = False
    
    def mark_dirty(self):
        """Mark data as needing save"""
        self.dirty = True
    
    def should_save(self, current_time) -> bool:
        """Check if should auto-save"""
        if current_time - self.last_save >= self.interval and self.dirty:
            return True
        return False
    
    def did_save(self, current_time):
        """Mark save complete"""
        self.last_save = current_time
        self.dirty = False
