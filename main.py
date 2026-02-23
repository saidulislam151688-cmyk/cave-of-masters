#!/usr/bin/env python3
"""
CAVE OF MASTERS - Professional 2.5D Combat Game
Advanced combat-focused RPG with stunning visuals
"""

import pygame
import random
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum, auto
import numpy as np

# ==================== INITIALIZATION ====================
pygame.init()

# ==================== CONSTANTS ====================
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920
TARGET_FPS = 60

# Colors - Professional Palette
COLORS = {
    # UI Colors
    'bg_dark': (12, 12, 24),
    'bg_medium': (24, 24, 48),
    'bg_light': (36, 36, 72),
    'primary': (147, 51, 234),      # Purple
    'primary_light': (168, 85, 247),
    'secondary': (245, 158, 11),    # Gold
    'accent': (6, 182, 212),        # Cyan
    
    # Health/Stamina/Focus
    'health': (239, 68, 68),        # Red
    'health_dark': (185, 28, 28),
    'stamina': (34, 197, 94),       # Green
    'stamina_dark': (22, 101, 52),
    'focus': (59, 130, 246),        # Blue
    'focus_dark': (29, 78, 216),
    
    # Text
    'text': (255, 255, 255),
    'text_dim': (160, 160, 180),
    'text_gold': (251, 191, 36),
    
    # Effects
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'transparent': (0, 0, 0, 0),
    'fire': (255, 100, 0),
    'ice': (100, 200, 255),
    'shadow': (80, 80, 120),
    
    # Entities
    'player': (100, 200, 255),
    'enemy': (255, 100, 100),
    'boss': (150, 50, 150),
    
    # Combat
    'hit_spark': (255, 255, 150),
    'block_spark': (150, 200, 255),
    'parry_spark': (255, 255, 255),
    'light': (255, 255, 200),
    'void': (100, 0, 100),
    
    # Combat
    'hit_spark': (255, 255, 150),
    'block_spark': (150, 200, 255),
    'parry_spark': (255, 255, 255),
    'dodge_trail': (200, 200, 255, 100),
}

# Physics
GRAVITY = 0.7
MAX_FALL_SPEED = 25
GROUND_Y = SCREEN_HEIGHT - 250

# Player Settings
PLAYER_WALK_SPEED = 6
PLAYER_RUN_SPEED = 10
PLAYER_JUMP_FORCE = -20
PLAYER_FRICTION = 0.85

# Combat Settings
HIT_STOP_FRAMES = 8
HIT_FREEZE_FRAMES = 3
KNOCKBACK_BASE = 12
KNOCKDOWN_FRAMES = 90
STUN_FRAMES = 60

# ==================== ADVANCED PARTICLE SYSTEM ====================
class Particle:
    """High-performance particle for effects"""
    __slots__ = ['x', 'y', 'vx', 'vy', 'life', 'max_life', 'size', 'color', 'gravity', 'fade', 'rotation', 'rot_speed', 'shape']
    
    def __init__(self, x, y, vx, vy, life, size, color, gravity=0, fade=True, rotation=0, rot_speed=0, shape='circle'):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.gravity = gravity
        self.fade = fade
        self.rotation = rotation
        self.rot_speed = rot_speed
        self.shape = shape
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.rotation += self.rot_speed
        return self.life > 0
    
    def get_alpha(self):
        if self.fade:
            return int(255 * (self.life / self.max_life))
        return 255
    
    def draw(self, surface, camera_x=0):
        alpha = self.get_alpha()
        if alpha <= 0:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y)
        
        if self.shape == 'circle':
            pygame.draw.circle(surface, (*self.color[:3], alpha), (screen_x, screen_y), max(1, int(self.size * (self.life / self.max_life))))
        elif self.shape == 'line':
            length = self.size
            end_x = screen_x + math.cos(self.rotation) * length
            end_y = screen_y + math.sin(self.rotation) * length
            pygame.draw.line(surface, (*self.color[:3], alpha), (screen_x, screen_y), (end_x, end_y), max(1, int(self.size / 4)))


class ParticleSystem:
    """Professional particle system with pooling"""
    
    def __init__(self, max_particles=1000):
        self.max_particles = max_particles
        self.particles: List[Particle] = []
        self.pool: List[Particle] = []
        
    def emit(self, x, y, count, config):
        """Emit particles with configuration"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
                
            angle = config.get('angle', random.uniform(0, math.pi * 2))
            spread = config.get('spread', math.pi)
            angle = angle + random.uniform(-spread/2, spread/2)
            
            speed = random.uniform(config.get('min_speed', 1), config.get('max_speed', 5))
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            if config.get('gravity'):
                vy += random.uniform(-2, 0)
            
            life = random.randint(config.get('min_life', 20), config.get('max_life', 40))
            size = random.uniform(config.get('min_size', 2), config.get('max_size', 8))
            
            if isinstance(config.get('color'), tuple):
                color = config['color']
            else:
                color = random.choice(config.get('colors', [COLORS['white']]))
            
            p = Particle(
                x, y, vx, vy, life, size, color,
                gravity=config.get('gravity', 0),
                fade=config.get('fade', True),
                rotation=random.uniform(0, math.pi * 2),
                rot_speed=random.uniform(-0.2, 0.2),
                shape=config.get('shape', 'circle')
            )
            self.particles.append(p)
    
    def update(self):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface, camera_x=0):
        """Draw all particles"""
        for p in self.particles:
            p.draw(surface, camera_x)
    
    def clear(self):
        self.particles.clear()


# ==================== SPRITE & ANIMATION SYSTEM ====================
class AnimationFrame:
    """Single animation frame"""
    def __init__(self, duration, rect, offset=(0, 0)):
        self.duration = duration  # frames
        self.rect = rect          # pygame Rect
        self.offset = offset      # draw offset

class Animation:
    """Professional animation system"""
    def __init__(self, name, frames, loop=True, speed=1.0):
        self.name = name
        self.frames = frames
        self.loop = loop
        self.speed = speed
        self.current_frame = 0
        self.timer = 0
        self.playing = False
        self.finished = False
    
    def reset(self):
        self.current_frame = 0
        self.timer = 0
        self.finished = False
    
    def play(self):
        self.playing = True
        self.reset()
    
    def stop(self):
        self.playing = False
        self.reset()
    
    def update(self):
        if not self.playing or self.finished:
            return
        
        self.timer += self.speed
        if self.timer >= self.frames[self.current_frame].duration:
            self.timer = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
    
    def get_current_rect(self):
        if self.frames:
            return self.frames[self.current_frame].rect
        return None
    
    def get_current_offset(self):
        if self.frames:
            return self.frames[self.current_frame].offset
        return (0, 0)


class SpriteSheet:
    """Sprite sheet manager with procedural generation fallback"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = None
        self.frames: Dict[str, List[AnimationFrame]] = {}
        
    def generate_procedural(self):
        """Generate placeholder sprites procedurally"""
        self.image = pygame.Surface((self.width * 10, self.height * 10), pygame.SRCALPHA)
        
        # Generate different colored "characters"
        colors = [
            (100, 180, 255),  # Player - Blue
            (255, 100, 100),  # Enemy - Red
            (200, 100, 200),  # Boss - Purple
            (100, 200, 100),  # Ally - Green
        ]
        
        for row, color in enumerate(colors):
            for col in range(10):
                x = col * self.width
                y = row * self.height
                
                # Body
                pygame.draw.rect(self.image, color, (x + 10, y + 20, self.width - 20, self.height - 40))
                # Head
                pygame.draw.circle(self.image, (*color, 50), (x + self.width//2, y + 25), 20)
                # Eyes
                pygame.draw.circle(self.image, COLORS['white'], (x + self.width//2 - 8, y + 22), 5)
                pygame.draw.circle(self.image, COLORS['white'], (x + self.width//2 + 8, y + 22), 5)
                pygame.draw.circle(self.image, COLORS['black'], (x + self.width//2 - 8, y + 22), 2)
                pygame.draw.circle(self.image, COLORS['black'], (x + self.width//2 + 8, y + 22), 2)
        
        return self.image
    
    def create_animations(self):
        """Create animation definitions"""
        # Player animations (simplified)
        self.frames = {
            'idle': [AnimationFrame(15, pygame.Rect(0, 0, 64, 128))],
            'walk': [AnimationFrame(8, pygame.Rect(64, 0, 64, 128)),
                    AnimationFrame(8, pygame.Rect(128, 0, 64, 128))],
            'run': [AnimationFrame(5, pygame.Rect(192, 0, 64, 128)),
                   AnimationFrame(5, pygame.Rect(256, 0, 64, 128))],
            'jump': [AnimationFrame(20, pygame.Rect(320, 0, 64, 128))],
            'fall': [AnimationFrame(10, pygame.Rect(384, 0, 64, 128))],
            'enemy_idle': [AnimationFrame(20, pygame.Rect(0, 128, 64, 128))],
            'enemy_walk': [AnimationFrame(10, pygame.Rect(64, 128, 64, 128)),
                          AnimationFrame(10, pygame.Rect(128, 128, 64, 128))],
            'enemy_attack': [AnimationFrame(8, pygame.Rect(192, 128, 64, 128)),
                            AnimationFrame(8, pygame.Rect(256, 128, 64, 128)),
                            AnimationFrame(8, pygame.Rect(320, 128, 64, 128))],
            'boss_idle': [AnimationFrame(30, pygame.Rect(0, 256, 128, 192))],
            'boss_attack': [AnimationFrame(15, pygame.Rect(128, 256, 128, 192)),
                           AnimationFrame(15, pygame.Rect(256, 256, 128, 192))],
        }


# ==================== STATE MACHINE ====================
class State(Enum):
    """Entity states"""
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
    """Combat states for attacks"""
    NONE = auto()
    STARTUP = auto()
    ACTIVE = auto()
    RECOVERY = auto()
    HIT_STUN = auto()


# ==================== COMBAT SYSTEM ====================
@dataclass
class Hitbox:
    """Attack hitbox"""
    x: float
    y: float
    width: float
    height: float
    damage: int = 10
    knockback: float = 8
    hitstun: int = 20
    priority: int = 0
    elemental: str = 'none'
    can_crit: bool = True
    can_block: bool = True
    
    def get_rect(self, owner_x, owner_y, facing_right):
        if facing_right:
            return pygame.Rect(int(owner_x + self.x), int(owner_y + self.y), int(self.width), int(self.height))
        return pygame.Rect(int(owner_x - self.x - self.width), int(owner_y + self.y), int(self.width), int(self.height))


@dataclass
class Attack:
    """Attack definition"""
    name: str
    startup: int      # frames before active
    active: int      # frames of active hitbox
    recovery: int    # frames after hitbox
    damage: int
    knockback: float
    hitstun: int
    hitbox: Hitbox
    stamina_cost: int
    focus_gain: int
    chain_to: List[str] = field(default_factory=list)
    can_air: bool = False
    can_cancel: bool = False
    special: str = 'none'


class CombatComponent:
    """Professional combat system"""
    
    def __init__(self, owner):
        self.owner = owner
        self.current_attack: Optional[Attack] = None
        self.combat_state = CombatState.NONE
        self.attack_frame = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.last_hit_time = 0
        self.blocking = False
        self.parrying = False
        self.parry_window = 0
        self.invincible = False
        self.invincible_timer = 0
        self.hitstop = 0
        self.hitfreeze = 0
        
        self.attacks: Dict[str, Attack] = {}
        self.setup_attacks()
    
    def setup_attacks(self):
        """Define all attacks"""
        # Basic Light Attack
        light_hitbox = Hitbox(30, 40, 50, 60, damage=12, knockback=6, hitstun=15, priority=1)
        self.attacks['light'] = Attack(
            'Light Punch', 4, 4, 8, 12, 6, 15, light_hitbox, 5, 5,
            chain_to=['heavy', 'kick', 'light']
        )
        
        # Heavy Attack
        heavy_hitbox = Hitbox(40, 30, 60, 70, damage=25, knockback=12, hitstun=25, priority=2)
        self.attacks['heavy'] = Attack(
            'Heavy Punch', 8, 5, 18, 25, 12, 25, heavy_hitbox, 12, 10,
            chain_to=['finisher', 'light']
        )
        
        # Kick
        kick_hitbox = Hitbox(50, 50, 55, 50, damage=18, knockback=10, hitstun=20, priority=1)
        self.attacks['kick'] = Attack(
            'Kick', 5, 4, 12, 18, 10, 20, kick_hitbox, 8, 8,
            chain_to=['sweep', 'light'], can_air=True
        )
        
        # Air Attack
        air_hitbox = Hitbox(30, 30, 55, 55, damage=15, knockback=8, hitstun=15, priority=1)
        self.attacks['air'] = Attack(
            'Air Kick', 3, 4, 10, 15, 8, 15, air_hitbox, 3, 5,
            can_air=True
        )
        
        # Finisher
        finisher_hitbox = Hitbox(50, 20, 70, 80, damage=40, knockback=18, hitstun=40, priority=3)
        self.attacks['finisher'] = Attack(
            'Finisher', 10, 6, 25, 40, 18, 40, finisher_hitbox, 20, 20,
            special='knockdown'
        )
        
        # Dash Attack
        dash_hitbox = Hitbox(40, 40, 60, 60, damage=20, knockback=10, hitstun=20, priority=2)
        self.attacks['dash'] = Attack(
            'Dash Strike', 2, 6, 15, 20, 10, 20, dash_hitbox, 15, 10,
            can_cancel=False
        )
    
    def start_attack(self, attack_name: str):
        """Start an attack"""
        if self.combat_state not in [CombatState.NONE, CombatState.RECOVERY]:
            return
        
        if attack_name not in self.attacks:
            return
        
        attack = self.attacks[attack_name]
        
        # Check stamina
        if hasattr(self.owner, 'stamina') and self.owner.stamina < attack.stamina_cost:
            return
        
        # Check air eligibility
        if attack.can_air or self.owner.on_ground:
            self.current_attack = attack
            self.combat_state = CombatState.STARTUP
            self.attack_frame = 0
            
            # Deduct stamina
            if hasattr(self.owner, 'stamina'):
                self.owner.stamina -= attack.stamina_cost
            
            # Reset combo if too long since last hit
            if self.combo_timer <= 0:
                self.combo_count = 0
    
    def update(self):
        """Update combat state"""
        # Update timers
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo_count = 0
        
        # Update invincibility
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Update parry window
        if self.parry_window > 0:
            self.parry_window -= 1
            if self.parry_window <= 0:
                self.parrying = False
        
        # Update hitstop/hitfreeze
        if self.hitstop > 0:
            self.hitstop -= 1
            return  # Don't update other combat during hitstop
        
        if self.hitfreeze > 0:
            self.hitfreeze -= 1
        
        # Update attack state
        if self.current_attack:
            self.attack_frame += 1
            
            if self.combat_state == CombatState.STARTUP:
                if self.attack_frame >= self.current_attack.startup:
                    self.combat_state = CombatState.ACTIVE
                    self.attack_frame = 0
            
            elif self.combat_state == CombatState.ACTIVE:
                # Check for hits
                if self.attack_frame >= self.current_attack.active:
                    self.combat_state = CombatState.RECOVERY
                    self.attack_frame = 0
            
            elif self.combat_state == CombatState.RECOVERY:
                if self.attack_frame >= self.current_attack.recovery:
                    self.end_attack()
    
    def end_attack(self):
        """End current attack"""
        self.current_attack = None
        self.combat_state = CombatState.NONE
        self.attack_frame = 0
    
    def get_hitbox_rect(self):
        """Get current attack hitbox"""
        if self.current_attack and self.combat_state == CombatState.ACTIVE:
            return self.current_attack.hitbox.get_rect(
                self.owner.x, self.owner.y, self.owner.facing_right
            )
        return None
    
    def try_chain(self):
        """Try to chain to next attack"""
        if self.current_attack and self.current_attack.chain_to:
            return random.choice(self.current_attack.chain_to) if random.random() > 0.3 else self.current_attack.chain_to[0]
        return None
    
    def hit_confirm(self, damage, is_crit=False):
        """Called when attack hits"""
        self.combo_count += 1
        self.combo_timer = 30
        self.last_hit_time = pygame.time.get_ticks()
        
        # Gain focus
        if hasattr(self.owner, 'focus'):
            focus_gain = self.current_attack.focus_gain if self.current_attack else 5
            if is_crit:
                focus_gain *= 2
            self.owner.focus = min(self.owner.max_focus, self.owner.focus + focus_gain)
        
        return damage
    
    def take_damage(self, damage, knockback=0, hitstun=0, knockdown=False):
        """Take damage"""
        if self.invincible:
            return 0
        
        # Check block
        if self.blocking and self.owner.facing_toward is not None:
            damage = int(damage * 0.3)
            knockback = knockback * 0.3
            hitstun = hitstun * 0.5
            self.owner.create_block_effect()
            return damage
        
        # Check parry
        if self.parry_window > 0:
            damage = 0
            self.owner.create_parry_effect()
            return -1  # Parry indicator
        
        # Apply damage
        final_damage = damage
        if hasattr(self.owner, 'defense'):
            final_damage = max(1, damage - self.owner.defense)
        
        if hasattr(self.owner, 'health'):
            self.owner.health = max(0, self.owner.health - final_damage)
            
            # Knockback
            if knockback > 0:
                dir = -1 if self.owner.facing_right else 1
                self.owner.vx = dir * knockback
                self.owner.vy = -5
                self.owner.set_state(State.HIT)
            
            # Knockdown
            if knockdown:
                self.owner.set_state(State.DOWN)
                self.owner.down_timer = KNOCKDOWN_FRAMES
            
            # Hitstun
            elif hitstun > 0:
                self.owner.set_state(State.STUN)
                self.owner.stun_timer = hitstun
        
        return final_damage
    
    def dodge(self, direction):
        """Execute dodge"""
        if hasattr(self.owner, 'stamina') and self.owner.stamina >= 15:
            self.owner.stamina -= 15
            self.invincible = True
            self.invincible_timer = 12
            self.owner.vx = direction * 18
            self.owner.set_state(State.DODGE)
            self.owner.dodge_timer = 15
            self.owner.create_dodge_effect()
            return True
        return False
    
    def parry(self):
        """Execute parry"""
        if hasattr(self.owner, 'focus') and self.owner.focus >= 10:
            self.owner.focus -= 10
            self.parrying = True
            self.parry_window = 8
            self.owner.create_parry_start_effect()
            return True
        return False


# ==================== ENTITY BASE ====================
class Entity:
    """Base entity class with physics and rendering"""
    
    def __init__(self, x, y, width, height):
        # Position & Physics
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        
        # State
        self.state = State.IDLE
        self.facing_right = True
        self.facing_toward = None  # Position being faced
        
        # Combat
        self.combat = CombatComponent(self)
        
        # Stats
        self.max_health = 100
        self.health = 100
        self.max_stamina = 50
        self.stamina = 50
        self.max_focus = 30
        self.focus = 30
        self.attack_power = 10
        self.defense = 5
        
        # Timers
        self.stun_timer = 0
        self.down_timer = 0
        self.dodge_timer = 0
        self.hit_timer = 0
        
        # Visual
        self.color = COLORS['player']
        self.size_mod = 1.0
        self.flash_timer = 0
        self.flash_color = None
        
        # Animation
        self.animation: Optional[Animation] = None
        self.anim_timer = 0
        
        # Effects
        self.particles: List[Callable] = []
        
    def update(self, dt):
        """Update entity"""
        # Apply gravity
        if not self.on_ground:
            self.vy += GRAVITY
            if self.vy > MAX_FALL_SPEED:
                self.vy = MAX_FALL_SPEED
        
        # Apply friction
        self.vx *= PLAYER_FRICTION
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Ground collision
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Update state timers
        if self.stun_timer > 0:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.set_state(State.IDLE)
        
        if self.down_timer > 0:
            self.down_timer -= 1
            if self.down_timer <= 0:
                self.set_state(State.IDLE)
        
        if self.dodge_timer > 0:
            self.dodge_timer -= 1
            if self.dodge_timer <= 0:
                self.set_state(State.IDLE)
        
        if self.flash_timer > 0:
            self.flash_timer -= 1
        
        # Update combat
        self.combat.update()
        
        # Update animation
        if self.animation:
            self.animation.update()
        
        # Auto face player if enemy
        if hasattr(self, 'is_enemy') and self.is_enemy:
            self.update_ai_facing()
    
    def set_state(self, new_state):
        """Change state"""
        if self.state != new_state:
            self.state = new_state
            self.on_state_change()
    
    def on_state_change(self):
        """Called when state changes"""
        pass
    
    def update_ai_facing(self):
        """Update facing direction for AI"""
        pass
    
    def jump(self):
        """Jump"""
        if self.on_ground and self.stamina >= 5:
            self.stamina -= 5
            self.vy = PLAYER_JUMP_FORCE
            self.on_ground = False
            self.set_state(State.JUMP)
            return True
        return False
    
    def move(self, direction, running=False):
        """Move left/right"""
        if self.stun_timer > 0 or self.down_timer > 0:
            return
        
        speed = PLAYER_RUN_SPEED if running else PLAYER_WALK_SPEED
        self.vx = direction * speed
        self.facing_right = direction > 0
        self.facing_toward = direction
        
        if self.on_ground:
            if running:
                self.set_state(State.RUN)
            else:
                self.set_state(State.WALK)
    
    def draw(self, surface, camera_x=0):
        """Draw entity"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y)
        
        # Get draw position
        draw_x = screen_x
        draw_y = screen_y
        
        # Handle facing
        if not self.facing_right:
            draw_x = screen_x + self.width
        
        # Draw shadow
        shadow_y = GROUND_Y - 10
        shadow_size = int(self.width * 0.8)
        pygame.draw.ellipse(surface, (0, 0, 0, 50), 
                           (screen_x + (self.width - shadow_size)//2, shadow_y, shadow_size, 15))
        
        # Determine color (flash if hit)
        draw_color = self.color
        if self.flash_timer > 0 and self.flash_color:
            draw_color = self.flash_color
        elif self.combat.invincible:
            draw_color = (*COLORS['white'], 150)
        
        # Draw body
        body_rect = pygame.Rect(draw_x - self.width // 2, draw_y, self.width, self.height)
        
        # Draw with gradient effect
        pygame.draw.rect(surface, draw_color, body_rect)
        
        # Draw highlight
        highlight_rect = pygame.Rect(body_rect.x, body_rect.y, body_rect.width, body_rect.height // 3)
        highlight_color = tuple(min(255, c + 50) for c in draw_color[:3])
        pygame.draw.rect(surface, highlight_color, highlight_rect)
        
        # Draw eyes indicating direction
        eye_offset = 8 if self.facing_right else -8
        eye_y = body_rect.y + 20
        pygame.draw.circle(surface, COLORS['white'], (body_rect.centerx + eye_offset, eye_y), 6)
        pygame.draw.circle(surface, COLORS['black'], (body_rect.centerx + eye_offset, eye_y), 3)
        
        # Draw attack effects
        if self.combat.combat_state == CombatState.ACTIVE:
            hitbox = self.combat.get_hitbox_rect()
            if hitbox:
                hb_x = hitbox.x - camera_x
                hb_y = hitbox.y
                
                # Draw hitbox with glow
                glow_surf = pygame.Surface((hitbox.width + 20, hitbox.height + 20), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*COLORS['hit_spark'], 100), 
                                (10, 10, hitbox.width, hitbox.height))
                surface.blit(glow_surf, (hb_x - 10, hb_y - 10))
                
                pygame.draw.rect(surface, COLORS['hit_spark'], 
                                (hb_x, hb_y, hitbox.width, hitbox.height), 2)
        
        # Draw block shield
        if self.combat.blocking:
            shield_rect = pygame.Rect(screen_x - 20, screen_y - 10, self.width + 40, self.height + 20)
            pygame.draw.rect(surface, (*COLORS['focus'], 100), shield_rect, 3)
        
        # Draw parry indicator
        if self.combat.parry_window > 0:
            parry_rect = pygame.Rect(screen_x - 30, screen_y - 30, self.width + 60, self.height + 60)
            pygame.draw.rect(surface, COLORS['white'], parry_rect, 3)
    
    def create_block_effect(self):
        """Create block spark effect"""
        pass
    
    def create_parry_effect(self):
        """Create parry effect"""
        pass
    
    def create_parry_start_effect(self):
        """Create parry start effect"""
        pass
    
    def create_dodge_effect(self):
        """Create dodge trail effect"""
        pass


# ==================== PLAYER CLASS ====================
class Player(Entity):
    """Player entity with full controls"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 64, 128)
        self.color = COLORS['player']
        
        # Level & Progression
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        
        # Masters & Abilities
        self.masters_unlocked = ['basic']
        self.abilities = ['light', 'heavy', 'kick']
        
        # Build
        self.fighting_style = 'balanced'
        
        # Input
        self.input_enabled = True
    
    def update(self, dt):
        super().update(dt)
        
        # Auto-regenerate
        if self.stun_timer <= 0 and self.down_timer <= 0:
            # Stamina regen
            if self.stamina < self.max_stamina:
                self.stamina += 0.15
                self.stamina = min(self.stamina, self.max_stamina)
            
            # Focus regen
            if self.focus < self.max_focus:
                self.focus += 0.05
                self.focus = min(self.focus, self.max_focus)
            
            # Update state if idle
            if self.state in [State.WALK, State.RUN] and abs(self.vx) < 0.5:
                self.set_state(State.IDLE)
    
    def on_state_change(self):
        """Handle state changes"""
        if self.state == State.JUMP:
            self.create_jump_effect()
        elif self.state == State.IDLE:
            pass
    
    def create_jump_effect(self):
        """Jump dust effect"""
        if hasattr(self, 'particles'):
            self.particles.append({
                'type': 'jump',
                'x': self.x,
                'y': GROUND_Y,
                'timer': 10
            })
    
    def create_block_effect(self):
        """Block spark effect"""
        pass
    
    def create_parry_effect(self):
        """Parry effect - big flash"""
        pass
    
    def create_parry_start_effect(self):
        """Parry ready effect"""
        pass
    
    def create_dodge_effect(self):
        """Dodge trail effect"""
        pass
    
    def level_up(self):
        """Level up"""
        self.level += 1
        self.xp -= self.xp_to_next
        self.xp_to_next = int(self.xp_to_next * 1.5)
        
        # Stat increases
        self.max_health += 10
        self.health = self.max_health
        self.max_stamina += 3
        self.stamina = self.max_stamina
        self.max_focus += 2
        self.focus = self.max_focus
        self.attack_power += 2
        self.defense += 1


# ==================== ENEMY CLASS ====================
class Enemy(Entity):
    """Enemy with AI"""
    
    def __init__(self, x, y, enemy_type='soldier', level=1):
        super().__init__(x, y, 64, 128)
        
        self.is_enemy = True
        self.enemy_type = enemy_type
        self.level = level
        
        # Type-specific stats
        type_stats = {
            'minion': {'health': 30, 'damage': 5, 'speed': 2, 'color': (150, 100, 100)},
            'soldier': {'health': 50, 'damage': 10, 'speed': 3, 'color': (180, 80, 80)},
            'elite': {'health': 80, 'damage': 15, 'speed': 4, 'color': (200, 50, 50)},
            'guardian': {'health': 150, 'damage': 8, 'speed': 1, 'color': (120, 120, 80)},
            'boss': {'health': 500, 'damage': 20, 'speed': 3, 'color': (150, 50, 150), 'width': 96, 'height': 160},
        }
        
        stats = type_stats.get(enemy_type, type_stats['soldier'])
        self.color = stats['color']
        if 'width' in stats:
            self.width = stats['width']
        if 'height' in stats:
            self.height = stats['height']
        
        self.max_health = stats['health'] + level * 5
        self.health = self.max_health
        self.damage = stats['damage'] + level * 2
        self.speed = stats['speed']
        
        # AI State
        self.ai_state = 'idle'
        self.ai_timer = 0
        self.attack_cooldown = 0
        self.target: Optional[Entity] = None
    
    def update_ai(self, player: Player, dt):
        """Update AI"""
        if self.health <= 0:
            return
        
        if self.stun_timer > 0 or self.down_timer > 0:
            super().update(dt)
            return
        
        # Set target
        if not self.target:
            self.target = player
        
        # Calculate distance
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = abs(dx)
        
        # Face target
        self.facing_right = dx > 0
        self.facing_toward = 1 if dx > 0 else -1
        
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # AI Behavior
        if distance > 300:
            # Far - approach
            self.ai_state = 'approach'
            direction = 1 if dx > 0 else -1
            self.vx = direction * self.speed
            
            if self.on_ground:
                self.set_state(State.WALK)
                
        elif distance > 80:
            # Medium - move closer carefully
            if self.attack_cooldown <= 0:
                self.ai_state = 'approach'
                direction = 1 if dx > 0 else -1
                self.vx = direction * (self.speed * 0.7)
                
                if self.on_ground:
                    self.set_state(State.WALK)
            else:
                self.set_state(State.IDLE)
                
        elif distance <= 80 and self.attack_cooldown <= 0:
            # In range - attack
            self.ai_state = 'attack'
            self.attack()
            
        # Random dodge
        if random.random() < 0.005 and self.stamina >= 15:
            direction = -1 if dx > 0 else 1
            self.combat.dodge(direction)
        
        super().update(dt)
    
    def attack(self):
        """Enemy attack"""
        if self.attack_cooldown > 0:
            return
        
        self.set_state(State.ATTACK)
        self.combat.start_attack('light')
        self.attack_cooldown = 60 + random.randint(-20, 20)
    
    def take_damage(self, damage, knockback=0, hitstun=0, knockdown=False):
        """Enemy takes damage"""
        result = super().take_damage(damage, knockback, hitstun, knockdown)
        
        if result >= 0 and self.health > 0:
            # Flash white
            self.flash_timer = 5
            self.flash_color = COLORS['white']
            
            # Knockback toward player if not blocking
            if self.combat.blocking:
                self.vx = 0
            else:
                dir = -1 if self.target and self.target.x > self.x else 1
                self.vx = dir * (knockback if knockback > 0 else 5)
        
        return result
    
    def die(self):
        """Enemy death"""
        return self.xp_value
    
    @property
    def xp_value(self):
        """XP given on death"""
        base_xp = {
            'minion': 10,
            'soldier': 20,
            'elite': 40,
            'guardian': 60,
            'boss': 200,
        }
        return base_xp.get(self.enemy_type, 20) + self.level * 5


# ==================== BOSS CLASS ====================
class Boss(Enemy):
    """Boss enemy with phases"""
    
    def __init__(self, x, y, boss_type='stone', level=1):
        super().__init__(x, y, 'boss', level)
        
        self.boss_type = boss_type
        self.phase = 1
        self.max_phase = 3
        
        # Phase-specific
        phase_health = {
            'stone': {'color': (120, 120, 120), 'health': 500},
            'wind': {'color': (100, 200, 255), 'health': 450},
            'fire': {'color': (255, 100, 0), 'health': 550},
            'shadow': {'color': (80, 80, 120), 'health': 600},
            'void': {'color': (100, 0, 100), 'health': 700},
        }
        
        stats = phase_health.get(boss_type, phase_health['stone'])
        self.color = stats['color']
        self.max_health = stats['health'] + level * 20
        self.health = self.max_health
        
        # Special abilities
        self.special_attack_timer = 0
        self.phase_change_threshold = self.max_health / self.max_phase
    
    def update_ai(self, player: Player, dt):
        """Boss AI with phases"""
        if self.health <= 0:
            return
        
        # Check phase change
        if self.health < self.phase_change_threshold * (self.max_phase - self.phase):
            self.phase += 1
            self.on_phase_change()
        
        # Special attacks
        self.special_attack_timer += 1
        
        super().update_ai(player, dt)
    
    def on_phase_change(self):
        """Called when phase changes"""
        # Visual effect
        self.flash_timer = 30
        self.flash_color = COLORS['white']
        
        # Heal slightly
        self.health = min(self.max_health, self.health + self.max_health * 0.2)
        
        # Reset cooldowns
        self.attack_cooldown = 30


# ==================== CAMERA SYSTEM ====================
class Camera:
    """Professional camera with smooth follow"""
    
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.width = width
        self.height = height
        self.smoothing = 0.1
        self.shake = 0
        self.shake_decay = 0.9
        
        # Bounds
        self.min_x = 0
        self.max_x = float('inf')
    
    def set_target(self, target, follow_x=True, follow_y=True):
        """Set camera target"""
        if follow_x:
            self.target_x = target.x - self.width // 2
        if follow_y:
            self.target_y = target.y - self.height // 2
    
    def update(self):
        """Update camera position"""
        # Smooth follow
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing
        
        # Clamp to bounds
        self.x = max(self.min_x, min(self.x, self.max_x - self.width))
        
        # Screen shake
        if self.shake > 0:
            self.x += random.uniform(-self.shake, self.shake)
            self.y += random.uniform(-self.shake, self.shake)
            self.shake *= self.shake_decay
    
    def shake_screen(self, amount):
        """Trigger screen shake"""
        self.shake = amount
    
    def get_offset(self):
        """Get camera offset"""
        return int(self.x)


# ==================== UI SYSTEM ====================
class UI:
    """Professional UI system"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        # Animations
        self.damage_popups: List[Dict] = []
        self.screen_fade = 0
        self.screen_flash = 0
    
    def draw_bar(self, x, y, width, height, current, maximum, color, color_dark, label=''):
        """Draw health/stamina bar with background"""
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (20, 20, 40), bg_rect)
        pygame.draw.rect(self.screen, (60, 60, 80), bg_rect, 2)
        
        # Fill
        if maximum > 0:
            fill_width = int(width * (current / maximum))
            fill_rect = pygame.Rect(x + 2, y + 2, fill_width - 4, height - 4)
            pygame.draw.rect(self.screen, color, fill_rect)
            
            # Shine effect
            shine_rect = pygame.Rect(x + 2, y + 2, fill_width - 4, height // 3)
            shine_color = tuple(min(255, c + 40) for c in color[:3])
            pygame.draw.rect(self.screen, shine_color, shine_rect)
        
        # Label
        if label:
            text = self.font_tiny.render(label, True, COLORS['text'])
            self.screen.blit(text, (x + 5, y + height // 2 - text.get_height() // 2))
    
    def draw_player_hud(self, player: Player):
        """Draw player HUD"""
        bar_width = 300
        bar_height = 30
        
        # Position
        x = 30
        y = SCREEN_HEIGHT - 200
        
        # Health bar
        self.draw_bar(x, y, bar_width, bar_height, 
                     player.health, player.max_health,
                     COLORS['health'], COLORS['health_dark'], 'HP')
        
        # Stamina bar
        self.draw_bar(x, y + bar_height + 10, bar_width, bar_height * 0.7,
                     player.stamina, player.max_stamina,
                     COLORS['stamina'], COLORS['stamina_dark'], 'ST')
        
        # Focus bar
        self.draw_bar(x, y + bar_height * 1.7 + 20, bar_width, bar_height * 0.7,
                     player.focus, player.max_focus,
                     COLORS['focus'], COLORS['focus_dark'], 'FX')
        
        # Level
        level_text = self.font_medium.render(f'LV.{player.level}', True, COLORS['text_gold'])
        self.screen.blit(level_text, (x + bar_width + 20, y))
        
        # Combo
        if player.combat.combo_count > 1:
            combo_text = self.font_large.render(f'{player.combat.combo_count}HIT!', True, COLORS['secondary'])
            self.screen.blit(combo_text, (x + bar_width + 20, y + 50))
        
        # XP bar (below bars)
        xp_y = y + bar_height * 2.5 + 30
        xp_width = bar_width + 100
        self.draw_bar(x, xp_y, xp_width, 15, player.xp, player.xp_to_next,
                     COLORS['primary'], COLORS['primary_light'], 'XP')
    
    def draw_enemy_health(self, enemy: Enemy):
        """Draw enemy health bar"""
        bar_width = 200
        bar_height = 20
        
        x = enemy.x - self.camera_x - bar_width // 2
        y = enemy.y - 40
        
        # Background
        pygame.draw.rect(self.screen, (40, 0, 0), (x, y, bar_width, bar_height))
        
        # Health
        if enemy.max_health > 0:
            fill_width = int(bar_width * (enemy.health / enemy.max_health))
            pygame.draw.rect(self.screen, enemy.color, (x, y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(self.screen, (100, 0, 0), (x, y, bar_width, bar_height), 2)
    
    def draw_damage_popup(self, x, y, damage, is_crit=False):
        """Draw damage popup"""
        color = COLORS['secondary'] if is_crit else COLORS['text']
        size = 48 if is_crit else 32
        
        font = pygame.font.Font(None, size)
        text = font.render(str(damage), True, color)
        
        # Float up animation
        y_offset = pygame.time.get_ticks() % 30
        
        self.screen.blit(text, (x, y - y_offset))
    
    def draw_combat_text(self, text, x, y, color=COLORS['secondary'], size=48):
        """Draw combat text (PARRY!, etc.)"""
        font = pygame.font.Font(None, size)
        surf = font.render(text, True, color)
        
        # Pulse effect
        scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.01)
        w = int(surf.get_width() * scale)
        h = int(surf.get_height() * scale)
        surf = pygame.transform.scale(surf, (w, h))
        
        self.screen.blit(surf, (x - w // 2, y - h // 2))
    
    def draw_controls(self):
        """Draw mobile touch controls"""
        # Bottom controls area
        control_y = SCREEN_HEIGHT - 150
        
        # Movement buttons (left side)
        pygame.draw.circle(self.screen, (*COLORS['bg_light'], 180), (100, control_y), 50)
        pygame.draw.circle(self.screen, (*COLORS['bg_light'], 180), (60, control_y - 60), 40)
        pygame.draw.circle(self.screen, (*COLORS['bg_light'], 180), (140, control_y - 60), 40)
        pygame.draw.circle(self.screen, (*COLORS['bg_light'], 180), (60, control_y + 60), 40)
        
        # Action buttons (right side)
        # Dodge
        pygame.draw.circle(self.screen, (*COLORS['accent'], 180), (SCREEN_WIDTH - 80, control_y), 45)
        
        # Block
        pygame.draw.circle(self.screen, (*COLORS['focus'], 180), (SCREEN_WIDTH - 150, control_y + 40), 40)
        
        # Attack
        pygame.draw.circle(self.screen, (*COLORS['health'], 180), (SCREEN_WIDTH - 150, control_y - 40), 45)
        
        # Jump (top right)
        pygame.draw.circle(self.screen, (*COLORS['secondary'], 180), (SCREEN_WIDTH - 80, control_y - 80), 35)
        
        # Labels
        font = pygame.font.Font(None, 24)
        
        labels = [
            ('◄', 60, control_y),
            ('▲', 100, control_y - 60),
            ('▼', 100, control_y + 60),
            ('ATK', SCREEN_WIDTH - 150, control_y - 40),
            ('BLK', SCREEN_WIDTH - 150, control_y + 40),
            ('DOD', SCREEN_WIDTH - 80, control_y),
            ('JMP', SCREEN_WIDTH - 80, control_y - 80),
        ]
        
        for text, x, y in labels:
            surf = font.render(str(text), True, COLORS['text'])
            self.screen.blit(surf, (x - surf.get_width() // 2, y - surf.get_height() // 2))
    
    def set_camera(self, camera):
        """Set camera for UI"""
        self.camera = camera


# ==================== MAIN GAME CLASS ====================
class Game:
    """Main game class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("CAVE OF MASTERS")
        self.clock = pygame.time.Clock()
        
        # State
        self.state = 'MENU'  # MENU, HUB, CAVE, COMBAT, GAME_OVER
        self.running = True
        
        # Camera
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # UI
        self.ui = UI(self.screen)
        self.ui.set_camera(self.camera)
        
        # Entities
        self.player: Optional[Player] = None
        self.enemies: List[Enemy] = []
        self.boss: Optional[Boss] = None
        
        # Particles
        self.particles = ParticleSystem(500)
        
        # Background
        self.backgrounds = self.generate_backgrounds()
        
        # Input
        self.keys = {}
        self.touch_buttons = {}
        
        # Game data
        self.current_cave = 1
        self.current_room = 0
        self.room_enemies = []
        
        # Room types
        self.room_types = ['combat', 'combat', 'combat', 'elite', 'boss']
        
        # Screenshake
        self.screen_shake = 0
    
    def generate_backgrounds(self):
        """Generate parallax backgrounds"""
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Dark gradient
        for y in range(SCREEN_HEIGHT):
            color = (
                int(12 + (y / SCREEN_HEIGHT) * 10),
                int(12 + (y / SCREEN_HEIGHT) * 10),
                int(24 + (y / SCREEN_HEIGHT) * 20)
            )
            pygame.draw.line(bg, color, (0, y), (SCREEN_HEIGHT, y))
        
        # Add some atmospheric particles/lights
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(1, 3)
            alpha = random.randint(20, 60)
            pygame.draw.circle(bg, (*COLORS['primary'], alpha), (x, y), size)
        
        return bg
    
    def start_new_game(self):
        """Start new game"""
        self.player = Player(SCREEN_WIDTH // 2, GROUND_Y - 128)
        self.current_cave = 1
        self.current_room = 0
        self.enemies = []
        self.boss = None
        self.state = 'HUB'
        self.particles.clear()
    
    def enter_cave(self):
        """Enter cave"""
        self.state = 'CAVE'
        self.current_room = 0
        self.enemies = []
        self.boss = None
        self.spawn_room_enemies()
    
    def spawn_room_enemies(self):
        """Spawn enemies for current room"""
        room_type = self.room_types[min(self.current_room, len(self.room_types) - 1)]
        
        if room_type == 'boss' and not self.boss:
            # Spawn boss
            cave_bosses = ['stone', 'wind', 'fire', 'shadow', 'void']
            boss_type = cave_bosses[min(self.current_cave - 1, 4)]
            self.boss = Boss(SCREEN_WIDTH - 150, GROUND_Y - 160, boss_type, self.current_cave * 2)
        
        elif room_type in ['combat', 'elite']:
            # Spawn enemies
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
        """Update game"""
        dt = 1  # Fixed timestep
        
        # Update particles
        self.particles.update()
        
        if self.state == 'MENU':
            self.update_menu()
        elif self.state == 'HUB':
            self.update_hub()
        elif self.state == 'CAVE':
            self.update_cave()
        
        # Update camera
        if self.player:
            self.camera.set_target(self.player)
            self.camera.update()
        
        # Update screenshake
        if self.screen_shake > 0:
            self.screen_shake *= 0.9
    
    def update_menu(self):
        """Update menu"""
        # Auto-start for now
        self.start_new_game()
    
    def update_hub(self):
        """Update hub"""
        if not self.player:
            return
        
        # Player movement in hub
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
        
        self.player.update(1)
        
        # Check for cave entry
        if self.keys.get(pygame.K_RETURN) or self.keys.get(pygame.K_SPACE):
            self.enter_cave()
    
    def update_cave(self):
        """Update cave combat"""
        if not self.player:
            return
        
        # Check room completion
        all_dead = all(e.health <= 0 for e in self.enemies) and (self.boss is None or self.boss.health <= 0)
        
        if all_dead and self.current_room < len(self.room_types) - 1:
            # Next room
            self.current_room += 1
            self.enemies = []
            self.boss = None
            self.spawn_room_enemies()
        
        elif all_dead and self.current_room >= len(self.room_types) - 1:
            # Cave complete!
            self.state = 'VICTORY'
            return
        
        # Player input
        self.handle_combat_input()
        
        # Update player
        self.player.update(1)
        
        # Update enemies
        for enemy in self.enemies:
            if enemy.health > 0:
                enemy.update_ai(self.player, 1)
                
                # Check collision with player
                if enemy.combat.combat_state == CombatState.ACTIVE:
                    hitbox = enemy.combat.get_hitbox_rect()
                    player_rect = pygame.Rect(self.player.x - self.player.width//2, 
                                             self.player.y, 
                                             self.player.width, self.player.height)
                    if hitbox and hitbox.colliderect(player_rect):
                        damage = enemy.damage + random.randint(-3, 5)
                        self.player.combat.take_damage(damage)
                        enemy.combat.combat_state = CombatState.RECOVERY
        
        # Update boss
        if self.boss and self.boss.health > 0:
            self.boss.update_ai(self.player, 1)
            
            if self.boss.combat.combat_state == CombatState.ACTIVE:
                hitbox = self.boss.combat.get_hitbox_rect()
                player_rect = pygame.Rect(self.player.x - self.player.width//2,
                                          self.player.y,
                                          self.player.width, self.player.height)
                if hitbox and hitbox.colliderect(player_rect):
                    damage = self.boss.damage + random.randint(-5, 10)
                    self.player.combat.take_damage(damage)
                    self.boss.combat.combat_state = CombatState.RECOVERY
        
        # Check player attacks hitting enemies
        self.check_player_hits()
        
        # Check player death
        if self.player.health <= 0:
            self.state = 'GAME_OVER'
    
    def check_player_hits(self):
        """Check player attack hits"""
        if not self.player or self.player.combat.combat_state != CombatState.ACTIVE:
            return
        
        hitbox = self.player.combat.get_hitbox_rect()
        if not hitbox:
            return
        
        # Check enemies
        for enemy in self.enemies:
            if enemy.health <= 0:
                continue
            
            enemy_rect = pygame.Rect(enemy.x - enemy.width//2, enemy.y,
                                     enemy.width, enemy.height)
            
            if hitbox.colliderect(enemy_rect):
                damage = self.player.attack_power + self.player.combat.current_attack.damage
                is_crit = random.random() < 0.1
                if is_crit:
                    damage = int(damage * 1.5)
                
                knockback = self.player.combat.current_attack.knockback
                hitstun = self.player.combat.current_attack.hitstun
                knockdown = self.player.combat.current_attack.special == 'knockdown'
                
                actual_damage = enemy.take_damage(damage, knockback, hitstun, knockdown)
                
                if actual_damage >= 0:
                    self.player.combat.hit_confirm(damage, is_crit)
                    
                    # Effects
                    self.screen_shake = 5
                    self.particles.emit(enemy.x, enemy.y + enemy.height // 2, 10, {
                        'color': COLORS['hit_spark'],
                        'angle': random.uniform(0, math.pi * 2),
                        'spread': math.pi,
                        'min_speed': 3,
                        'max_speed': 8,
                        'min_life': 10,
                        'max_life': 20,
                        'gravity': 0.2,
                    })
                    
                    # Kill enemy
                    if enemy.health <= 0:
                        self.player.xp += enemy.xp_value
        
        # Check boss
        if self.boss and self.boss.health > 0:
            boss_rect = pygame.Rect(self.boss.x - self.boss.width//2, self.boss.y,
                                  self.boss.width, self.boss.height)
            
            if hitbox.colliderect(boss_rect):
                damage = self.player.attack_power + self.player.combat.current_attack.damage
                is_crit = random.random() < 0.1
                if is_crit:
                    damage = int(damage * 1.5)
                
                knockback = self.player.combat.current_attack.knockback * 0.5
                hitstun = self.player.combat.current_attack.hitstun
                
                actual_damage = self.boss.take_damage(damage, knockback, hitstun)
                
                if actual_damage >= 0:
                    self.player.combat.hit_confirm(damage, is_crit)
                    self.screen_shake = 8
                    
                    if self.boss.health <= 0:
                        self.player.xp += self.boss.xp_value
    
    def handle_combat_input(self):
        """Handle combat input"""
        if not self.player or not self.player.input_enabled:
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
            if self.player.combat.combat_state == CombatState.NONE:
                self.player.combat.start_attack('light')
            elif self.player.combat.combat_state == CombatState.RECOVERY:
                chain = self.player.combat.try_chain()
                if chain:
                    self.player.combat.start_attack(chain)
        
        if self.keys.get(ord('k')) or self.keys.get(pygame.K_x):
            if self.player.combat.combat_state == CombatState.NONE:
                self.player.combat.start_attack('heavy')
        
        if self.keys.get(ord('l')) or self.keys.get(pygame.K_c):
            if self.player.combat.combat_state == CombatState.NONE:
                self.player.combat.start_attack('kick')
        
        # Dodge
        if self.keys.get(ord('s')) or self.keys.get(pygame.K_DOWN):
            if self.player.combat.combat_state == CombatState.NONE:
                dir = 1 if self.player.facing_right else -1
                self.player.combat.dodge(dir)
        
        # Block
        self.player.combat.blocking = self.keys.get(pygame.K_LCTRL) or self.keys.get(pygame.K_RCTRL)
        
        # Parry
        if self.keys.get(ord('p')):
            self.player.combat.parry()
        
        # Level up check
        if self.player.xp >= self.player.xp_to_next:
            self.player.level_up()
    
    def draw(self):
        """Draw game"""
        # Clear screen
        self.screen.fill(COLORS['bg_dark'])
        
        # Apply screenshake
        shake_x = random.randint(-int(self.screen_shake), int(self.screen_shake))
        shake_y = random.randint(-int(self.screen_shake), int(self.screen_shake))
        
        if self.state == 'MENU':
            self.draw_menu()
        elif self.state == 'HUB':
            self.draw_hub(shake_x, shake_y)
        elif self.state in ['CAVE', 'VICTORY']:
            self.draw_cave(shake_x, shake_y)
        elif self.state == 'GAME_OVER':
            self.draw_game_over()
        
        # Draw particles (with shake)
        self.particles.draw(self.screen, self.camera.get_offset() + shake_x)
        
        # Draw UI
        self.ui.draw_controls()
        
        # Draw FPS
        if DEBUG.get('show_fps', False):
            fps = self.clock.get_fps()
            fps_text = self.ui.font_small.render(f'FPS: {int(fps)}', True, COLORS['text'])
            self.screen.blit(fps_text, (10, 10))
        
        pygame.display.flip()
    
    def draw_menu(self, shake_x=0, shake_y=0):
        """Draw menu"""
        # Background
        self.screen.blit(self.backgrounds, (shake_x, shake_y))
        
        # Title
        title = self.ui.font_large.render('CAVE OF MASTERS', True, COLORS['secondary'])
        subtitle = self.ui.font_medium.render('The Path to Inner Legend', True, COLORS['text_dim'])
        
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        subtitle_x = SCREEN_WIDTH // 2 - subtitle.get_width() // 2
        
        self.screen.blit(title, (title_x + shake_x, 300 + shake_y))
        self.screen.blit(subtitle, (subtitle_x + shake_x, 380 + shake_y))
        
        # Start prompt
        if pygame.time.get_ticks() % 1000 < 500:
            start = self.ui.font_medium.render('Press ENTER to Start', True, COLORS['text'])
            start_x = SCREEN_WIDTH // 2 - start.get_width() // 2
            self.screen.blit(start, (start_x + shake_x, 600 + shake_y))
        
        # Controls info
        controls = [
            'CONTROLS:',
            'A/D or Arrows - Move',
            'W/Space - Jump',
            'J/Z - Light Attack',
            'K/X - Heavy Attack',
            'L/C - Kick',
            'S/Down - Dodge',
            'Ctrl - Block',
            'P - Parry',
        ]
        
        y = 800
        for line in controls:
            text = self.ui.font_small.render(line, True, COLORS['text_dim'])
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2 + shake_x, y + shake_y))
            y += 35
    
    def draw_hub(self, shake_x=0, shake_y=0):
        """Draw hub"""
        # Background
        self.screen.blit(self.backgrounds, (shake_x, shake_y))
        
        # Ground
        pygame.draw.rect(self.screen, (40, 30, 50), (0, GROUND_Y + 20, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        
        # Hub buildings/portals
        # Cave portal
        portal_rect = pygame.Rect(SCREEN_WIDTH - 250, GROUND_Y - 200, 150, 220)
        pygame.draw.rect(self.screen, (*COLORS['void'], 150), portal_rect)
        pygame.draw.rect(self.screen, COLORS['void'], portal_rect, 3)
        
        portal_text = self.ui.font_small.render('ENTER CAVE', True, COLORS['text'])
        self.screen.blit(portal_text, (portal_rect.centerx - portal_text.get_width() // 2 + shake_x, 
                                       portal_rect.centery + shake_y))
        
        # Training sign
        train_rect = pygame.Rect(50, GROUND_Y - 150, 100, 120)
        pygame.draw.rect(self.screen, (*COLORS['secondary'], 100), train_rect)
        
        train_text = self.ui.font_small.render('TRAINING', True, COLORS['bg_dark'])
        self.screen.blit(train_text, (train_rect.centerx - train_text.get_width() // 2 + shake_x,
                                       train_rect.centery + shake_y))
        
        # Draw player
        if self.player:
            self.player.draw(self.screen, self.camera.get_offset() + shake_x)
        
        # Draw HUD
        if self.player:
            self.ui.draw_player_hud(self.player)
    
    def draw_cave(self, shake_x=0, shake_y=0):
        """Draw cave"""
        # Cave background
        cave_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Cave walls effect
        for i in range(5):
            alpha = 30 + i * 10
            x = i * 100
            pygame.draw.rect(cave_bg, (*COLORS['bg_dark'], alpha), (x, 0, 100, SCREEN_HEIGHT))
            pygame.draw.rect(cave_bg, (*COLORS['bg_dark'], alpha), (SCREEN_WIDTH - x - 100, 0, 100, SCREEN_HEIGHT))
        
        self.screen.blit(cave_bg, (shake_x, shake_y))
        
        # Ground
        pygame.draw.rect(self.screen, (50, 40, 40), (0, GROUND_Y + 20, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        
        # Cave decorations based on cave type
        self.draw_cave_decorations(shake_x, shake_y)
        
        # Draw player
        if self.player:
            self.player.draw(self.screen, self.camera.get_offset() + shake_x)
        
        # Draw enemies
        for enemy in self.enemies:
            if enemy.health > 0:
                enemy.draw(self.screen, self.camera.get_offset() + shake_x)
                self.ui.draw_enemy_health(enemy)
        
        # Draw boss
        if self.boss and self.boss.health > 0:
            self.boss.draw(self.screen, self.camera.get_offset() + shake_x)
            self.ui.draw_enemy_health(self.boss)
            
            # Boss name
            boss_name = f"{self.boss.boss_type.upper()} MASTER"
            name_text = self.ui.font_medium.render(boss_name, True, COLORS['secondary'])
            self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2 + shake_x, 50 + shake_y))
        
        # Draw HUD
        if self.player:
            self.ui.draw_player_hud(self.player)
        
        # Room indicator
        room_text = f"Room {self.current_room + 1}/{len(self.room_types)}"
        room_surf = self.ui.font_small.render(room_text, True, COLORS['text_dim'])
        self.screen.blit(room_surf, (SCREEN_WIDTH - room_surf.get_width() - 20 + shake_x, 20 + shake_y))
        
        # Victory screen
        if self.state == 'VICTORY':
            self.draw_victory(shake_x, shake_y)
    
    def draw_cave_decorations(self, shake_x=0, shake_y=0):
        """Draw cave-specific decorations"""
        cave_colors = {
            1: (80, 80, 90),    # Stone - Gray
            2: (100, 180, 200), # Wind - Light blue
            3: (200, 100, 50),  # Fire - Orange
            4: (60, 60, 90),    # Shadow - Dark purple
            5: (80, 50, 80),    # Void - Dark purple
        }
        
        color = cave_colors.get(self.current_cave, (80, 80, 90))
        
        # Draw some rock formations
        for i in range(5):
            x = 50 + i * 200
            y = GROUND_Y - 50 - i * 20
            
            # Rocks
            pygame.draw.polygon(self.screen, color, [
                (x + shake_x, y + 50 + shake_y),
                (x + 30 + shake_x, y + shake_y),
                (x + 60 + shake_x, y + 50 + shake_y),
            ])
    
    def draw_victory(self, shake_x=0, shake_y=0):
        """Draw victory screen"""
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Victory text
        victory = self.ui.font_large.render('CAVE COMPLETE!', True, COLORS['secondary'])
        self.screen.blit(victory, (SCREEN_WIDTH // 2 - victory.get_width() // 2 + shake_x, 
                                    SCREEN_HEIGHT // 2 - 50 + shake_y))
        
        # Continue prompt
        if pygame.time.get_ticks() % 1000 < 500:
            cont = self.ui.font_medium.render('Press ENTER to continue', True, COLORS['text'])
            self.screen.blit(cont, (SCREEN_WIDTH // 2 - cont.get_width() // 2 + shake_x,
                                    SCREEN_HEIGHT // 2 + 50 + shake_y))
    
    def draw_game_over(self):
        """Draw game over screen"""
        # Red overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((80, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over = self.ui.font_large.render('DEFEATED', True, COLORS['health'])
        self.screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2,
                                      SCREEN_HEIGHT // 2 - 50))
        
        # Retry prompt
        if pygame.time.get_ticks() % 1000 < 500:
            retry = self.ui.font_medium.render('Press ENTER to retry', True, COLORS['text'])
            self.screen.blit(retry, (SCREEN_WIDTH // 2 - retry.get_width() // 2,
                                      SCREEN_HEIGHT // 2 + 50))
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.QUIT:
            self.running = False
        
        elif event.type == pygame.KEYDOWN:
            self.keys[event.key] = True
            
            if event.key == pygame.K_ESCAPE:
                self.running = False
            
            # Menu controls
            if self.state == 'MENU':
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.start_new_game()
            
            # Hub controls
            elif self.state == 'HUB':
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.enter_cave()
            
            # Victory/Game Over
            elif self.state in ['VICTORY', 'GAME_OVER']:
                if event.key == pygame.K_RETURN:
                    self.start_new_game()
        
        elif event.type == pygame.KEYUP:
            self.keys[event.key] = False
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Event handling
            for event in pygame.event.get():
                self.handle_event(event)
            
            # Update
            self.update()
            
            # Draw
            self.draw()
            
            # Cap framerate
            self.clock.tick(TARGET_FPS)
        
        pygame.quit()


# ==================== DEBUG ====================
DEBUG = {
    'show_fps': True,
}


# ==================== ENTRY POINT ====================
if __name__ == '__main__':
    game = Game()
    game.run()
