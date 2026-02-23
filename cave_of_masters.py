#!/usr/bin/env python3
"""
CAVE OF MASTERS - Complete Professional Game
============================================
A deep offline combat-focused RPG
Optimized for Android with touch controls
"""

import pygame
import random
import math
import time
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto

# ==================== INITIALIZATION ====================
pygame.init()

# ==================== CONSTANTS ====================
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920
TARGET_FPS = 60

# Colors
COLORS = {
    'bg_dark': (12, 12, 24),
    'bg_medium': (24, 24, 48),
    'bg_light': (36, 36, 72),
    'primary': (147, 51, 234),
    'primary_light': (168, 85, 247),
    'secondary': (245, 158, 11),
    'accent': (6, 182, 212),
    'health': (239, 68, 68),
    'health_dark': (185, 28, 28),
    'stamina': (34, 197, 94),
    'stamina_dark': (22, 101, 52),
    'focus': (59, 130, 246),
    'focus_dark': (29, 78, 216),
    'text': (255, 255, 255),
    'text_dim': (160, 160, 180),
    'text_gold': (251, 191, 36),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'fire': (255, 100, 0),
    'ice': (100, 200, 255),
    'shadow': (80, 80, 120),
    'light': (255, 255, 200),
    'void': (100, 0, 100),
    'player': (100, 200, 255),
    'enemy': (255, 100, 100),
    'boss': (150, 50, 150),
    'hit_spark': (255, 255, 150),
    'block_spark': (150, 200, 255),
    'parry_spark': (255, 255, 255),
}

# Physics
GRAVITY = 0.7
MAX_FALL_SPEED = 25
GROUND_Y = SCREEN_HEIGHT - 250
PLAYER_WALK_SPEED = 6
PLAYER_RUN_SPEED = 10
PLAYER_JUMP_FORCE = -20
PLAYER_FRICTION = 0.85

# Combat
HIT_STOP_FRAMES = 8
HIT_FREEZE_FRAMES = 3

# ==================== SAVE SYSTEM ====================
SAVE_DIR = os.path.expanduser("~/.cave_of_masters")
SAVE_FILE = os.path.join(SAVE_DIR, "save_data.json")


def ensure_save_dir():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def create_default_save():
    return {
        "version": "1.0.0",
        "player": {
            "name": "Warrior",
            "level": 1,
            "xp": 0,
            "xp_to_next": 100,
            "max_health": 100,
            "health": 100,
            "max_stamina": 50,
            "stamina": 50,
            "max_focus": 30,
            "focus": 30,
            "attack": 10,
            "defense": 5,
        },
        "progression": {
            "caves_completed": [],
            "current_cave": 1,
            "unlocked_caves": [1],
            "unlocked_masters": ["basic"],
            "unlocked_weapons": ["fists"],
            "training_bonus": {},
        },
    }


def save_game(player, cave_num):
    ensure_save_dir()
    save_data = create_default_save()
    
    if player:
        save_data["player"]["level"] = player.level
        save_data["player"]["xp"] = player.xp
        save_data["player"]["xp_to_next"] = player.xp_to_next
        save_data["player"]["max_health"] = player.max_health
        save_data["player"]["health"] = player.health
        save_data["player"]["max_stamina"] = player.max_stamina
        save_data["player"]["stamina"] = player.stamina
        save_data["player"]["max_focus"] = player.max_focus
        save_data["player"]["focus"] = player.focus
        save_data["player"]["attack"] = player.attack_power
        save_data["player"]["defense"] = player.defense
    
    save_data["progression"]["current_cave"] = cave_num
    
    with open(SAVE_FILE, 'w') as f:
        json.dump(save_data, f, indent=2)


def load_game():
    ensure_save_dir()
    if not os.path.exists(SAVE_FILE):
        return create_default_save()
    try:
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    except:
        return create_default_save()


# ==================== PARTICLE SYSTEM ====================
class ParticleSystem:
    def __init__(self, max_particles=500):
        self.particles = []
        self.max_particles = max_particles
    
    def emit(self, x, y, count, config):
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            angle = config.get('angle', random.uniform(0, math.pi * 2))
            spread = config.get('spread', math.pi)
            angle = angle + random.uniform(-spread/2, spread/2)
            speed = random.uniform(config.get('min_speed', 1), config.get('max_speed', 5))
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.randint(config.get('min_life', 20), config.get('max_life', 40))
            size = random.uniform(config.get('min_size', 2), config.get('max_size', 8))
            color = config.get('color', COLORS['white'])
            
            self.particles.append({
                'x': x, 'y': y, 'vx': vx, 'vy': vy,
                'life': life, 'max_life': life, 'size': size,
                'color': color, 'gravity': config.get('gravity', 0)
            })
    
    def update(self):
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += p['gravity']
            p['life'] -= 1
        self.particles = [p for p in self.particles if p['life'] > 0]
    
    def draw(self, surface, camera_x=0):
        for p in self.particles:
            alpha = int(255 * (p['life'] / p['max_life']))
            if alpha <= 0:
                continue
            screen_x = int(p['x'] - camera_x)
            screen_y = int(p['y'])
            size = int(p['size'] * (p['life'] / p['max_life']))
            if size > 0:
                pygame.draw.circle(surface, (*p['color'][:3], alpha), (screen_x, screen_y), size)


# ==================== ENUMS ====================
class State(Enum):
    IDLE = auto()
    WALK = auto()
    RUN = auto()
    JUMP = auto()
    FALL = auto()
    ATTACK = auto()
    BLOCK = auto()
    DODGE = auto()
    HIT = auto()
    STUN = auto()
    DOWN = auto()
    DEAD = auto()


class CombatState(Enum):
    NONE = auto()
    STARTUP = auto()
    ACTIVE = auto()
    RECOVERY = auto()


# ==================== ATTACK DATA ====================
@dataclass
class Attack:
    name: str
    startup: int
    active: int
    recovery: int
    damage: int
    knockback: float
    hitstun: int
    stamina_cost: int
    focus_gain: int
    knockback_x: float = 10
    knockback_y: float = -5


# ==================== ATTACKS DATABASE ====================
ATTACKS = {
    'light': Attack('Punch', 4, 4, 8, 12, 6, 15, 5, 5),
    'heavy': Attack('Uppercut', 8, 5, 18, 25, 12, 25, 12, 10, 15, -8),
    'kick': Attack('Kick', 5, 4, 12, 18, 10, 20, 8, 8, 12, -3),
    'air': Attack('Air Kick', 3, 4, 10, 15, 8, 15, 3, 5, 8, -2),
    'finisher': Attack('Finisher', 10, 6, 25, 40, 18, 40, 20, 20, 20, -10),
}


# ==================== ENTITY ====================
class Entity:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.state = State.IDLE
        self.facing_right = True
        self.color = color
        self.flash_timer = 0
        self.flash_color = None
        
        # Stats
        self.max_health = 100
        self.health = 100
        self.max_stamina = 50
        self.stamina = 50
        self.max_focus = 30
        self.focus = 30
        self.attack_power = 10
        self.defense = 5
        
        # Combat
        self.current_attack: Optional[Attack] = None
        self.combat_state = CombatState.NONE
        self.attack_frame = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.blocking = False
        self.parrying = False
        self.parry_window = 0
        self.invincible = False
        self.invincible_timer = 0
        
        # Timers
        self.stun_timer = 0
        self.down_timer = 0
        self.dodge_timer = 0
        
        # Hitbox for attacks
        self.attack_hitbox = None
    
    def update(self):
        # Gravity
        if not self.on_ground:
            self.vy += GRAVITY
            if self.vy > MAX_FALL_SPEED:
                self.vy = MAX_FALL_SPEED
        
        # Friction
        self.vx *= PLAYER_FRICTION
        
        # Move
        self.x += self.vx
        self.y += self.vy
        
        # Ground collision
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Timers
        if self.stun_timer > 0:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.state = State.IDLE
        
        if self.down_timer > 0:
            self.down_timer -= 1
            if self.down_timer <= 0:
                self.state = State.IDLE
        
        if self.dodge_timer > 0:
            self.dodge_timer -= 1
            if self.dodge_timer <= 0:
                self.state = State.IDLE
        
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        if self.parry_window > 0:
            self.parry_window -= 1
            if self.parry_window <= 0:
                self.parrying = False
        
        if self.flash_timer > 0:
            self.flash_timer -= 1
        
        # Combat
        self.update_combat()
        
        # Regen
        if self.stun_timer <= 0 and self.down_timer <= 0:
            self.stamina = min(self.max_stamina, self.stamina + 0.15)
            self.focus = min(self.max_focus, self.focus + 0.05)
        
        # Combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo_count = 0
    
    def update_combat(self):
        if self.current_attack:
            self.attack_frame += 1
            
            if self.combat_state == CombatState.STARTUP:
                if self.attack_frame >= self.current_attack.startup:
                    self.combat_state = CombatState.ACTIVE
                    self.attack_frame = 0
                    # Set hitbox
                    self.attack_hitbox = pygame.Rect(
                        int(self.x - 20) if not self.facing_right else int(self.x + self.width - 10),
                        int(self.y + 30),
                        50, 50
                    )
            
            elif self.combat_state == CombatState.ACTIVE:
                if self.attack_frame >= self.current_attack.active:
                    self.combat_state = CombatState.RECOVERY
                    self.attack_frame = 0
                    self.attack_hitbox = None
            
            elif self.combat_state == CombatState.RECOVERY:
                if self.attack_frame >= self.current_attack.recovery:
                    self.current_attack = None
                    self.combat_state = CombatState.NONE
                    self.attack_frame = 0
                    self.attack_hitbox = None
    
    def start_attack(self, attack_name: str):
        if self.combat_state not in [CombatState.NONE, CombatState.RECOVERY]:
            return
        
        if attack_name not in ATTACKS:
            return
        
        attack = ATTACKS[attack_name]
        
        if self.stamina < attack.stamina_cost:
            return
        
        self.stamina -= attack.stamina_cost
        self.current_attack = attack
        self.combat_state = CombatState.STARTUP
        self.attack_frame = 0
        
        if self.combo_timer <= 0:
            self.combo_count = 0
    
    def take_damage(self, damage, knockback=0, hitstun=0, knockdown=False):
        if self.invincible:
            return 0
        
        # Block check
        if self.blocking:
            damage = int(damage * 0.3)
            knockback = knockback * 0.3
            hitstun = hitstun * 0.5
        
        # Parry check
        if self.parry_window > 0:
            damage = 0
            self.create_parry_effect()
            return -1
        
        # Apply damage
        final_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - final_damage)
        
        # Effects
        if knockback > 0:
            direction = -1 if self.facing_right else 1
            self.vx = direction * knockback
            self.vy = -5
            self.set_state(State.HIT)
        
        if knockdown:
            self.set_state(State.DOWN)
            self.down_timer = 90
        elif hitstun > 0:
            self.set_state(State.STUN)
            self.stun_timer = hitstun
        
        self.flash_timer = 5
        self.flash_color = COLORS['white']
        
        return final_damage
    
    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
    
    def jump(self):
        if self.on_ground and self.stamina >= 5:
            self.stamina -= 5
            self.vy = PLAYER_JUMP_FORCE
            self.on_ground = False
            self.set_state(State.JUMP)
            return True
        return False
    
    def move(self, direction, running=False):
        if self.stun_timer > 0 or self.down_timer > 0:
            return
        speed = PLAYER_RUN_SPEED if running else PLAYER_WALK_SPEED
        self.vx = direction * speed
        self.facing_right = direction > 0
        if self.on_ground:
            self.set_state(State.RUN if running else State.WALK)
    
    def dodge(self, direction):
        if self.stamina >= 15:
            self.stamina -= 15
            self.invincible = True
            self.invincible_timer = 12
            self.vx = direction * 18
            self.set_state(State.DODGE)
            self.dodge_timer = 15
            return True
        return False
    
    def parry(self):
        if self.focus >= 10:
            self.focus -= 10
            self.parrying = True
            self.parry_window = 8
            return True
        return False
    
    def create_parry_effect(self):
        pass
    
    def draw(self, surface, camera_x=0):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y)
        
        # Shadow
        shadow_y = GROUND_Y - 10
        shadow_size = int(self.width * 0.8)
        pygame.draw.ellipse(surface, (0, 0, 0, 50),
                           (screen_x + (self.width - shadow_size)//2, shadow_y, shadow_size, 15))
        
        # Body color
        draw_color = self.color
        if self.flash_timer > 0 and self.flash_color:
            draw_color = self.flash_color
        elif self.invincible:
            draw_color = (150, 150, 200)
        
        # Draw body
        body_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(surface, draw_color, body_rect)
        
        # Highlight
        highlight_rect = pygame.Rect(body_rect.x, body_rect.y, body_rect.width, body_rect.height // 3)
        highlight_color = tuple(min(255, c + 50) for c in draw_color[:3])
        pygame.draw.rect(surface, highlight_color, highlight_rect)
        
        # Eyes
        eye_offset = 10 if self.facing_right else -10
        eye_y = body_rect.y + 20
        pygame.draw.circle(surface, COLORS['white'], (body_rect.centerx + eye_offset, eye_y), 6)
        pygame.draw.circle(surface, COLORS['black'], (body_rect.centerx + eye_offset, eye_y), 3)
        
        # Attack hitbox visualization
        if self.combat_state == CombatState.ACTIVE and self.attack_hitbox:
            hb = pygame.Rect(
                self.attack_hitbox.x - camera_x,
                self.attack_hitbox.y,
                self.attack_hitbox.width,
                self.attack_hitbox.height
            )
            pygame.draw.rect(surface, COLORS['hit_spark'], hb, 2)
        
        # Block shield
        if self.blocking:
            shield_rect = pygame.Rect(screen_x - 20, screen_y - 10, self.width + 40, self.height + 20)
            pygame.draw.rect(surface, (*COLORS['focus'], 100), shield_rect, 3)


# ==================== PLAYER ====================
class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 64, 128, COLORS['player'])
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        self.masters_unlocked = ['basic']
        self.abilities = ['light', 'heavy', 'kick']
    
    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next
        self.xp_to_next = int(self.xp_to_next * 1.5)
        self.max_health += 10
        self.health = self.max_health
        self.max_stamina += 3
        self.stamina = self.max_stamina
        self.max_focus += 2
        self.focus = self.max_focus
        self.attack_power += 2
        self.defense += 1


# ==================== ENEMY ====================
class Enemy(Entity):
    def __init__(self, x, y, enemy_type='soldier', level=1):
        color = {
            'minion': (150, 100, 100),
            'soldier': (180, 80, 80),
            'elite': (200, 50, 50),
            'guardian': (120, 120, 80),
            'boss': (150, 50, 150),
        }.get(enemy_type, (180, 80, 80))
        
        width, height = (64, 128) if enemy_type != 'boss' else (96, 160)
        super().__init__(x, y, width, height, color)
        
        self.enemy_type = enemy_type
        self.level = level
        
        stats = {
            'minion': (30, 5, 2),
            'soldier': (50, 10, 3),
            'elite': (80, 15, 4),
            'guardian': (150, 8, 1),
            'boss': (500, 20, 3),
        }.get(enemy_type, (50, 10, 3))
        
        self.max_health = stats[0] + level * 5
        self.health = self.max_health
        self.damage = stats[1] + level * 2
        self.speed = stats[2]
        
        self.ai_state = 'idle'
        self.ai_timer = 0
        self.attack_cooldown = 0
        self.target = None
    
    def update_ai(self, player: Player, dt):
        if self.health <= 0:
            return
        
        if self.stun_timer > 0 or self.down_timer > 0:
            super().update()
            return
        
        self.target = player
        
        if not self.target:
            return
        
        dx = self.target.x - self.x
        distance = abs(dx)
        
        self.facing_right = dx > 0
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if distance > 300:
            direction = 1 if dx > 0 else -1
            self.vx = direction * self.speed
            if self.on_ground:
                self.set_state(State.WALK)
        
        elif distance > 80:
            if self.attack_cooldown <= 0:
                direction = 1 if dx > 0 else -1
                self.vx = direction * (self.speed * 0.7)
                if self.on_ground:
                    self.set_state(State.WALK)
            else:
                self.set_state(State.IDLE)
        
        elif distance <= 80 and self.attack_cooldown <= 0:
            self.set_state(State.ATTACK)
            self.start_attack('light')
            self.attack_cooldown = 60 + random.randint(-20, 20)
        
        super().update()
    
    @property
    def xp_value(self):
        return {
            'minion': 10,
            'soldier': 20,
            'elite': 40,
            'guardian': 60,
            'boss': 200,
        }.get(self.enemy_type, 20) + self.level * 5


# ==================== BOSS ====================
class Boss(Enemy):
    def __init__(self, x, y, boss_type='stone', level=1):
        color = {
            'stone': (120, 120, 120),
            'wind': (100, 200, 255),
            'fire': (255, 100, 0),
            'shadow': (80, 80, 120),
            'void': (100, 0, 100),
        }.get(boss_type, (150, 50, 150))
        
        super().__init__(x, y, 'boss', level)
        self.boss_type = boss_type
        self.color = color
        self.max_health = 500 + level * 20
        self.health = self.max_health
        self.phase = 1
        self.max_phase = 3
    
    def on_phase_change(self):
        self.flash_timer = 30
        self.flash_color = COLORS['white']
        self.health = min(self.max_health, self.health + self.max_health * 0.2)
        self.attack_cooldown = 30
    
    def update_ai(self, player: Player, dt):
        if self.health <= 0:
            return
        
        # Phase change check
        if self.health < (self.max_health / self.max_phase) * (self.max_phase - self.phase):
            self.phase += 1
            self.on_phase_change()
        
        super().update_ai(player, dt)


# ==================== CAMERA ====================
class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.width = width
        self.height = height
        self.smoothing = 0.1
        self.shake = 0
    
    def set_target(self, target):
        self.target_x = target.x - self.width // 2
        self.target_y = target.y - self.height // 2
    
    def update(self):
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing
        
        if self.shake > 0:
            self.x += random.uniform(-self.shake, self.shake)
            self.y += random.uniform(-self.shake, self.shake)
            self.shake *= 0.9
    
    def get_offset(self):
        return int(self.x)


# ==================== UI ====================
class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
    
    def draw_bar(self, x, y, width, height, current, maximum, color, color_dark, label=''):
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (20, 20, 40), bg_rect)
        pygame.draw.rect(self.screen, (60, 60, 80), bg_rect, 2)
        
        if maximum > 0:
            fill_width = int(width * (current / maximum))
            fill_rect = pygame.Rect(x + 2, y + 2, fill_width - 4, height - 4)
            pygame.draw.rect(self.screen, color, fill_rect)
            
            shine_rect = pygame.Rect(x + 2, y + 2, fill_width - 4, height // 3)
            shine_color = tuple(min(255, c + 40) for c in color[:3])
            pygame.draw.rect(self.screen, shine_color, shine_rect)
        
        if label:
            text = self.font_tiny.render(label, True, COLORS['text'])
            self.screen.blit(text, (x + 5, y + height // 2 - text.get_height() // 2))
    
    def draw_player_hud(self, player: Player):
        bar_width = 300
        bar_height = 30
        x = 30
        y = SCREEN_HEIGHT - 200
        
        self.draw_bar(x, y, bar_width, bar_height, player.health, player.max_health,
                     COLORS['health'], COLORS['health_dark'], 'HP')
        self.draw_bar(x, y + bar_height + 10, bar_width, bar_height * 0.7,
                     player.stamina, player.max_stamina, COLORS['stamina'], COLORS['stamina_dark'], 'ST')
        self.draw_bar(x, y + bar_height * 1.7 + 20, bar_width, bar_height * 0.7,
                     player.focus, player.max_focus, COLORS['focus'], COLORS['focus_dark'], 'FX')
        
        level_text = self.font_medium.render(f'LV.{player.level}', True, COLORS['text_gold'])
        self.screen.blit(level_text, (x + bar_width + 20, y))
        
        if player.combo_count > 1:
            combo_text = self.font_large.render(f'{player.combo_count}HIT!', True, COLORS['secondary'])
            self.screen.blit(combo_text, (x + bar_width + 20, y + 50))
    
    def draw_enemy_health(self, enemy: Enemy):
        bar_width = 200
        bar_height = 20
        x = enemy.x - self.camera_x - bar_width // 2
        y = enemy.y - 40
        
        pygame.draw.rect(self.screen, (40, 0, 0), (x, y, bar_width, bar_height))
        
        if enemy.max_health > 0:
            fill_width = int(bar_width * (enemy.health / enemy.max_health))
            pygame.draw.rect(self.screen, enemy.color, (x, y, fill_width, bar_height))
        
        pygame.draw.rect(self.screen, (100, 0, 0), (x, y, bar_width, bar_height), 2)
    
    def set_camera(self, camera):
        self.camera = camera
    
    def draw_controls(self):
        control_y = SCREEN_HEIGHT - 150
        
        # Movement (left side)
        for cx, cy, size in [(100, control_y, 50), (60, control_y - 60, 40), (140, control_y - 60, 40), (60, control_y + 60, 40)]:
            pygame.draw.circle(self.screen, (*COLORS['bg_light'], 180), (cx, cy), size)
        
        # Actions (right side)
        for cx, cy, size, color in [
            (SCREEN_WIDTH - 80, control_y, 45, COLORS['accent']),
            (SCREEN_WIDTH - 150, control_y + 40, 40, COLORS['focus']),
            (SCREEN_WIDTH - 150, control_y - 40, 45, COLORS['health']),
            (SCREEN_WIDTH - 80, control_y - 80, 35, COLORS['secondary']),
        ]:
            pygame.draw.circle(self.screen, (*color, 180), (cx, cy), size)
        
        # Labels
        font = self.font_tiny
        labels = [
            ('◄', 60, control_y),
            ('▲', 100, control_y - 60),
            ('▼', 100, control_y + 60),
            ('ATK', SCREEN_WIDTH - 150, control_y - 40),
            ('BLK', SCREEN_WIDTH - 150, control_y + 40),
            ('DOD', SCREEN_WIDTH - 80, control_y),
            ('JMP', SCREEN_WIDTH - 80, control_y - 80),
        ]
        
        for text, cx, cy in labels:
            surf = font.render(str(text), True, COLORS['text'])
            self.screen.blit(surf, (cx - surf.get_width() // 2, cy - surf.get_height() // 2))


# ==================== MAIN GAME ====================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("CAVE OF MASTERS")
        self.clock = pygame.time.Clock()
        
        self.state = 'MENU'
        self.running = True
        
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui = UI(self.screen)
        self.ui.set_camera(self.camera)
        
        self.player: Optional[Player] = None
        self.enemies: List[Enemy] = []
        self.boss: Optional[Boss] = None
        
        self.particles = ParticleSystem()
        
        self.current_cave = 1
        self.current_room = 0
        self.room_types = ['combat', 'combat', 'combat', 'elite', 'boss']
        
        self.screen_shake = 0
        self.keys = {}
        
        self.save_data = load_game()
    
    def start_new_game(self):
        save = self.save_data
        self.player = Player(SCREEN_WIDTH // 2, GROUND_Y - 128)
        self.player.level = save['player']['level']
        self.player.xp = save['player']['xp']
        self.player.xp_to_next = save['player']['xp_to_next']
        self.player.max_health = save['player']['max_health']
        self.player.health = save['player']['health']
        self.player.max_stamina = save['player']['max_stamina']
        self.player.stamina = save['player']['stamina']
        self.player.max_focus = save['player']['max_focus']
        self.player.focus = save['player']['focus']
        self.player.attack_power = save['player']['attack']
        self.player.defense = save['player']['defense']
        
        self.current_cave = save['progression']['current_cave']
        self.enemies = []
        self.boss = None
        self.particles.clear()
        self.state = 'HUB'
    
    def enter_cave(self):
        self.state = 'CAVE'
        self.current_room = 0
        self.enemies = []
        self.boss = None
        self.spawn_room_enemies()
    
    def spawn_room_enemies(self):
        room_type = self.room_types[min(self.current_room, len(self.room_types) - 1)]
        
        if room_type == 'boss' and not self.boss:
            bosses = ['stone', 'wind', 'fire', 'shadow', 'void']
            boss_type = bosses[min(self.current_cave - 1, 4)]
            self.boss = Boss(SCREEN_WIDTH - 150, GROUND_Y - 160, boss_type, self.current_cave * 2)
        
        elif room_type in ['combat', 'elite']:
            enemy_count = 2 + self.current_room + (1 if room_type == 'elite' else 0)
            enemy_types = ['minion', 'soldier']
            
            if self.current_cave >= 2:
                enemy_types.append('elite')
            if self.current_cave >= 3:
                enemy_types.append('guardian')
            
            for i in range(enemy_count):
                enemy_type = random.choice(enemy_types)
                x = random.randint(100, SCREEN_WIDTH - 200)
                enemy = Enemy(x, GROUND_Y - 128, enemy_type, self.current_cave)
                self.enemies.append(enemy)
    
    def update(self):
        dt = 1
        self.particles.update()
        
        if self.state == 'MENU':
            pass
        elif self.state == 'HUB':
            self.update_hub()
        elif self.state == 'CAVE':
            self.update_cave()
        
        if self.player:
            self.camera.set_target(self.player)
            self.camera.update()
        
        if self.screen_shake > 0:
            self.screen_shake *= 0.9
    
    def update_hub(self):
        if not self.player:
            return
        
        direction = 0
        if self.keys.get(pygame.K_LEFT) or self.keys.get(ord('a')):
            direction = -1
        elif self.keys.get(pygame.K_RIGHT) or self.keys.get(ord('d')):
            direction = 1
        
        if direction != 0:
            self.player.move(direction)
        else:
            self.player.vx *= 0.9
            if abs(self.player.vx) < 0.5:
                self.player.set_state(State.IDLE)
        
        self.player.update()
        
        if self.keys.get(pygame.K_RETURN) or self.keys.get(pygame.K_SPACE):
            self.enter_cave()
    
    def update_cave(self):
        if not self.player:
            return
        
        # Check room completion
        all_dead = all(e.health <= 0 for e in self.enemies) and (self.boss is None or self.boss.health <= 0)
        
        if all_dead and self.current_room < len(self.room_types) - 1:
            self.current_room += 1
            self.enemies = []
            self.boss = None
            self.spawn_room_enemies()
        
        elif all_dead and self.current_room >= len(self.room_types) - 1:
            # Victory!
            self.save_data['progression']['current_cave'] = min(5, self.current_cave + 1)
            self.save_data['progression']['unlocked_caves'].append(min(5, self.current_cave + 1))
            save_game(self.player, self.current_cave)
            self.state = 'VICTORY'
            return
        
        # Player input
        self.handle_combat_input()
        self.player.update()
        
        # Enemies
        for enemy in self.enemies:
            if enemy.health > 0:
                enemy.update_ai(self.player, 1)
                
                if enemy.combat_state == CombatState.ACTIVE and enemy.attack_hitbox:
                    player_rect = pygame.Rect(self.player.x - 32, self.player.y, 64, 128)
                    if enemy.attack_hitbox.colliderect(player_rect):
                        damage = enemy.damage + random.randint(-3, 5)
                        self.player.take_damage(damage)
                        enemy.combat_state = CombatState.RECOVERY
        
        # Boss
        if self.boss and self.boss.health > 0:
            self.boss.update_ai(self.player, 1)
            
            if self.boss.combat_state == CombatState.ACTIVE and self.boss.attack_hitbox:
                player_rect = pygame.Rect(self.player.x - 32, self.player.y, 64, 128)
                if self.boss.attack_hitbox.colliderect(player_rect):
                    damage = self.boss.damage + random.randint(-5, 10)
                    self.player.take_damage(damage)
                    self.boss.combat_state = CombatState.RECOVERY
        
        # Player attacks
        self.check_player_hits()
        
        # Death check
        if self.player.health <= 0:
            self.state = 'GAME_OVER'
    
    def check_player_hits(self):
        if not self.player or self.player.combat_state != CombatState.ACTIVE:
            return
        
        hitbox = self.player.attack_hitbox
        if not hitbox:
            return
        
        for enemy in self.enemies:
            if enemy.health <= 0:
                continue
            
            enemy_rect = pygame.Rect(enemy.x - enemy.width//2, enemy.y, enemy.width, enemy.height)
            
            if hitbox.colliderect(enemy_rect):
                damage = self.player.attack_power + self.player.current_attack.damage
                is_crit = random.random() < 0.1
                if is_crit:
                    damage = int(damage * 1.5)
                
                knockback = self.player.current_attack.knockback_x
                hitstun = self.player.current_attack.hitstun
                
                actual = enemy.take_damage(damage, knockback, hitstun)
                
                if actual >= 0:
                    self.player.combo_count += 1
                    self.player.combo_timer = 30
                    self.player.focus = min(self.player.max_focus, self.player.focus + self.player.current_attack.focus_gain)
                    
                    self.screen_shake = 5
                    self.particles.emit(enemy.x, enemy.y + 50, 10, {
                        'color': COLORS['hit_spark'],
                        'angle': random.uniform(0, math.pi * 2),
                        'spread': math.pi,
                        'min_speed': 3, 'max_speed': 8,
                        'min_life': 10, 'max_life': 20,
                        'gravity': 0.2,
                    })
                    
                    if enemy.health <= 0:
                        self.player.xp += enemy.xp_value
        
        # Boss hit
        if self.boss and self.boss.health > 0:
            boss_rect = pygame.Rect(self.boss.x - self.boss.width//2, self.boss.y,
                                  self.boss.width, self.boss.height)
            
            if hitbox.colliderect(boss_rect):
                damage = self.player.attack_power + self.player.current_attack.damage
                is_crit = random.random() < 0.1
                if is_crit:
                    damage = int(damage * 1.5)
                
                knockback = self.player.current_attack.knockback_x * 0.5
                hitstun = self.player.current_attack.hitstun
                
                actual = self.boss.take_damage(damage, knockback, hitstun)
                
                if actual >= 0:
                    self.player.combo_count += 1
                    self.player.combo_timer = 30
                    self.screen_shake = 8
                    
                    if self.boss.health <= 0:
                        self.player.xp += self.boss.xp_value
        
        # Level up
        if self.player.xp >= self.player.xp_to_next:
            self.player.level_up()
    
    def handle_combat_input(self):
        if not self.player or not self.player.state not in [State.STUN, State.DOWN]:
            return
        
        if self.player.stun_timer > 0 or self.player.down_timer > 0:
            return
        
        # Movement
        direction = 0
        if self.keys.get(pygame.K_LEFT) or self.keys.get(ord('a')):
            direction = -1
        elif self.keys.get(pygame.K_RIGHT) or self.keys.get(ord('d')):
            direction = 1
        
        running = self.keys.get(pygame.K_LSHIFT) or self.keys.get(pygame.K_RSHIFT)
        
        if direction != 0:
            self.player.move(direction, running)
        else:
            self.player.vx *= 0.9
            if abs(self.player.vx) < 0.5 and self.player.on_ground:
                self.player.set_state(State.IDLE)
        
        # Jump
        if self.keys.get(pygame.K_UP) or self.keys.get(ord('w')) or self.keys.get(ord(' ')):
            self.player.jump()
        
        # Attacks
        if self.keys.get(ord('j')) or self.keys.get(pygame.K_z):
            if self.player.combat_state == CombatState.NONE:
                self.player.start_attack('light')
            elif self.player.combat_state == CombatState.RECOVERY:
                if random.random() > 0.5:
                    self.player.start_attack('heavy')
        
        if self.keys.get(ord('k')) or self.keys.get(pygame.K_x):
            if self.player.combat_state == CombatState.NONE:
                self.player.start_attack('heavy')
        
        if self.keys.get(ord('l')) or self.keys.get(pygame.K_c):
            if self.player.combat_state == CombatState.NONE:
                self.player.start_attack('kick')
        
        # Dodge
        if self.keys.get(ord('s')) or self.keys.get(pygame.K_DOWN):
            if self.player.combat_state == CombatState.NONE:
                dir = 1 if self.player.facing_right else -1
                self.player.dodge(dir)
        
        # Block
        self.player.blocking = self.keys.get(pygame.K_LCTRL) or self.keys.get(pygame.K_RCTRL)
        
        # Parry
        if self.keys.get(ord('p')):
            self.player.parry()
    
    def draw(self):
        self.screen.fill(COLORS['bg_dark'])
        
        shake_x = random.randint(-int(self.screen_shake), int(self.screen_shake))
        shake_y = random.randint(-int(self.screen_shake), int(self.screen_shake))
        
        if self.state == 'MENU':
            self.draw_menu(shake_x, shake_y)
        elif self.state == 'HUB':
            self.draw_hub(shake_x, shake_y)
        elif self.state in ['CAVE', 'VICTORY']:
            self.draw_cave(shake_x, shake_y)
        elif self.state == 'GAME_OVER':
            self.draw_game_over()
        
        self.particles.draw(self.screen, self.camera.get_offset() + shake_x)
        
        self.ui.draw_controls()
        
        pygame.display.flip()
    
    def draw_menu(self, shake_x=0, shake_y=0):
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color = (int(12 + (y / SCREEN_HEIGHT) * 10), int(12 + (y / SCREEN_HEIGHT) * 10), int(24 + (y / SCREEN_HEIGHT) * 20))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        title = self.ui.font_large.render('CAVE OF MASTERS', True, COLORS['secondary'])
        subtitle = self.ui.font_medium.render('The Path to Inner Legend', True, COLORS['text_dim'])
        
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2 + shake_x, 300 + shake_y))
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2 + shake_x, 380 + shake_y))
        
        if pygame.time.get_ticks() % 1000 < 500:
            start = self.ui.font_medium.render('Press ENTER to Start', True, COLORS['text'])
            self.screen.blit(start, (SCREEN_WIDTH // 2 - start.get_width() // 2 + shake_x, 600 + shake_y))
        
        controls = [
            'CONTROLS:', 'A/D - Move', 'W/Space - Jump', 'J/Z - Light Attack',
            'K/X - Heavy Attack', 'L/C - Kick', 'S/Down - Dodge',
            'Ctrl - Block', 'P - Parry',
        ]
        
        y = 800
        for line in controls:
            text = self.ui.font_small.render(line, True, COLORS['text_dim'])
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2 + shake_x, y + shake_y))
            y += 35
    
    def draw_hub(self, shake_x=0, shake_y=0):
        # Background
        for y in range(SCREEN_HEIGHT):
            color = (int(12 + (y / SCREEN_HEIGHT) * 10), int(12 + (y / SCREEN_HEIGHT) * 10), int(24 + (y / SCREEN_HEIGHT) * 20))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        pygame.draw.rect(self.screen, (40, 30, 50), (0, GROUND_Y + 20, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        
        # Cave portal
        portal_rect = pygame.Rect(SCREEN_WIDTH - 250, GROUND_Y - 200, 150, 220)
        pygame.draw.rect(self.screen, (*COLORS['void'], 150), portal_rect)
        pygame.draw.rect(self.screen, COLORS['void'], portal_rect, 3)
        
        portal_text = self.ui.font_small.render('ENTER CAVE', True, COLORS['text'])
        self.screen.blit(portal_text, (portal_rect.centerx - portal_text.get_width() // 2 + shake_x, portal_rect.centery + shake_y))
        
        # Training
        train_rect = pygame.Rect(50, GROUND_Y - 150, 100, 120)
        pygame.draw.rect(self.screen, (*COLORS['secondary'], 100), train_rect)
        
        if self.player:
            self.player.draw(self.screen, self.camera.get_offset() + shake_x)
            self.ui.draw_player_hud(self.player)
    
    def draw_cave(self, shake_x=0, shake_y=0):
        # Cave background
        for i in range(5):
            alpha = 30 + i * 10
            x = i * 100
            pygame.draw.rect(self.screen, (*COLORS['bg_dark'], alpha), (x, 0, 100, SCREEN_HEIGHT))
            pygame.draw.rect(self.screen, (*COLORS['bg_dark'], alpha), (SCREEN_WIDTH - x - 100, 0, 100, SCREEN_HEIGHT))
        
        pygame.draw.rect(self.screen, (50, 40, 40), (0, GROUND_Y + 20, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        
        if self.player:
            self.player.draw(self.screen, self.camera.get_offset() + shake_x)
        
        for enemy in self.enemies:
            if enemy.health > 0:
                enemy.draw(self.screen, self.camera.get_offset() + shake_x)
                self.ui.draw_enemy_health(enemy)
        
        if self.boss and self.boss.health > 0:
            self.boss.draw(self.screen, self.camera.get_offset() + shake_x)
            self.ui.draw_enemy_health(self.boss)
            
            boss_name = f"{self.boss.boss_type.upper()} MASTER"
            name_text = self.ui.font_medium.render(boss_name, True, COLORS['secondary'])
            self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2 + shake_x, 50 + shake_y))
        
        if self.player:
            self.ui.draw_player_hud(self.player)
        
        room_text = f"Room {self.current_room + 1}/{len(self.room_types)}"
        room_surf = self.ui.font_small.render(room_text, True, COLORS['text_dim'])
        self.screen.blit(room_surf, (SCREEN_WIDTH - room_surf.get_width() - 20 + shake_x, 20 + shake_y))
        
        if self.state == 'VICTORY':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            victory = self.ui.font_large.render('CAVE COMPLETE!', True, COLORS['secondary'])
            self.screen.blit(victory, (SCREEN_WIDTH // 2 - victory.get_width() // 2 + shake_x, SCREEN_HEIGHT // 2 - 50 + shake_y))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((80, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        game_over = self.ui.font_large.render('DEFEATED', True, COLORS['health'])
        self.screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        
        if pygame.time.get_ticks() % 1000 < 500:
            retry = self.ui.font_medium.render('Press ENTER to retry', True, COLORS['text'])
            self.screen.blit(retry, (SCREEN_WIDTH // 2 - retry.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        
        elif event.type == pygame.KEYDOWN:
            self.keys[event.key] = True
            
            if event.key == pygame.K_ESCAPE:
                self.running = False
            
            if self.state == 'MENU':
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.start_new_game()
            
            elif self.state == 'HUB':
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.enter_cave()
            
            elif self.state in ['VICTORY', 'GAME_OVER']:
                if event.key == pygame.K_RETURN:
                    self.start_new_game()
        
        elif event.type == pygame.KEYUP:
            self.keys[event.key] = False
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            
            self.update()
            self.draw()
            
            self.clock.tick(TARGET_FPS)
        
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
