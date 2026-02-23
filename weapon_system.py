"""
WEAPON SYSTEM - Professional weapon and equipment system
"""

from enum import Enum, auto
from typing import Dict, List, Optional
import random


class WeaponType(Enum):
    """Weapon types"""
    FISTS = auto()
    SWORD = auto()
    DUAL_BLADES = auto()
    HEAVY_AXE = auto()
    CHAIN = auto()
    STAFF = auto()


class Weapon:
    """Weapon definition"""
    
    def __init__(self, weapon_id: str, name: str, weapon_type: WeaponType,
                 damage: int, speed: float, range_pixels: int, style: str,
                 special: str = 'none', description: str = ''):
        self.id = weapon_id
        self.name = name
        self.type = weapon_type
        self.damage = damage
        self.speed = speed
        self.range = range_pixels
        self.style = style
        self.special = special
        self.description = description
        
        # Unlocks
        self.unlocked = False
        self.unlock_cave = 0
    
    def __repr__(self):
        return f"Weapon({self.name}, DMG: {self.damage}, SPD: {self.speed})"


# ==================== WEAPON DATABASE ====================
WEAPONS: Dict[str, Weapon] = {
    'fists': Weapon(
        'fists', 'Fists', WeaponType.FISTS,
        damage=10, speed=1.2, range_pixels=50, style='balanced',
        special='grapple',
        description='Your bare fists. Balanced and reliable.'
    ),
    'sword': Weapon(
        'sword', 'Iron Sword', WeaponType.SWORD,
        damage=20, speed=1.0, range_pixels=120, style='precision',
        special='parry_strike',
        description='A well-crafted sword. Great for precision strikes.',
        unlock_cave=1
    ),
    'dual_blades': Weapon(
        'dual_blades', 'Dual Blades', WeaponType.DUAL_BLADES,
        damage=12, speed=1.5, range_pixels=80, style='speed',
        special='air_dance',
        description='Twin blades for lightning-fast combos.',
        unlock_cave=2
    ),
    'heavy_axe': Weapon(
        'heavy_axe', 'Heavy Axe', WeaponType.HEAVY_AXE,
        damage=35, speed=0.7, range_pixels=100, style='power',
        special='armor_break',
        description='Devastating axe that breaks defenses.',
        unlock_cave=3
    ),
    'chain': Weapon(
        'chain', 'Chain Whip', WeaponType.CHAIN,
        damage=15, speed=0.9, range_pixels=150, style='control',
        special='pull_enemy',
        description='Flexible chain for keeping enemies at bay.',
        unlock_cave=4
    ),
    'staff': Weapon(
        'staff', 'Mystic Staff', WeaponType.STAFF,
        damage=18, speed=1.1, range_pixels=140, style='technical',
        special='counter_attack',
        description='Staff that amplifies focus power.',
        unlock_cave=5
    ),
}


class WeaponSystem:
    """Weapon management system"""
    
    def __init__(self, player):
        self.player = player
        self.equipped: Weapon = WEAPONS['fists']
        self.unlocked_weapons = ['fists']
        
        # Weapon-specific combat modifiers
        self.damage_mod = 1.0
        self.speed_mod = 1.0
        self.range_mod = 1.0
    
    def equip(self, weapon_id: str) -> bool:
        """Equip a weapon"""
        if weapon_id not in WEAPONS:
            return False
        
        if weapon_id not in self.unlocked_weapons:
            return False
        
        self.equipped = WEAPONS[weapon_id]
        self.apply_mods()
        return True
    
    def unlock(self, weapon_id: str) -> bool:
        """Unlock a weapon"""
        if weapon_id in WEAPONS:
            WEAPONS[weapon_id].unlocked = True
            if weapon_id not in self.unlocked_weapons:
                self.unlocked_weapons.append(weapon_id)
            return True
        return False
    
    def apply_mods(self):
        """Apply weapon modifiers"""
        self.damage_mod = 1.0 + (self.equipped.damage - 10) / 50
        self.speed_mod = self.equipped.speed
        self.range_mod = self.equipped.range / 50
    
    def get_damage(self) -> int:
        """Get total damage with modifiers"""
        base = self.equipped.damage + self.player.attack_power
        return int(base * self.damage_mod)
    
    def get_attack_speed(self) -> float:
        """Get attack speed"""
        return self.equipped.speed * self.speed_mod
    
    def get_range(self) -> int:
        """Get attack range"""
        return int(self.equipped.range * self.range_mod)


# ==================== TRANSFORMATION SYSTEM ====================
class TransformationType(Enum):
    """Transformation types"""
    FIRE = auto()
    SHADOW = auto()
    LIGHT = auto()
    VOID = auto()


class Transformation:
    """Transformation definition"""
    
    def __init__(self, transform_id: str, name: str, transform_type: TransformationType,
                 attack_bonus: float = 0, defense_bonus: float = 0, speed_bonus: float = 0,
                 special_effect: str = 'none', activation: str = 'manual',
                 description: str = '', color: tuple = (255, 255, 255)):
        self.id = transform_id
        self.name = name
        self.type = transform_type
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.speed_bonus = speed_bonus
        self.special_effect = special_effect
        self.activation = activation
        self.description = description
        self.color = color
        
        # State
        self.unlocked = False
        self.level = 0
        self.active = False
        self.activation_timer = 0


# ==================== TRANSFORMATION DATABASE ====================
TRANSFORMATIONS: Dict[str, Transformation] = {
    'fire': Transformation(
        'fire', 'Inferno Form', TransformationType.FIRE,
        attack_bonus=0.5, defense_bonus=0.1,
        special_effect='burn', activation='health_below_30',
        description='Transform when health is low. Increases attack by 50%.',
        color=(255, 100, 0)
    ),
    'shadow': Transformation(
        'shadow', 'Shadow Form', TransformationType.SHADOW,
        attack_bonus=0.2, defense_bonus=0.2, speed_bonus=0.3,
        special_effect='iframe_dodge', activation='focus_full',
        description='Transform when focus is full. Grants dodge invincibility.',
        color=(80, 80, 120)
    ),
    'light': Transformation(
        'light', 'Light Form', TransformationType.LIGHT,
        attack_bonus=0.1, defense_bonus=0.4,
        special_effect='heal_parry', activation='perfect_parry',
        description='Transform on perfect parry. Heals and shields.',
        color=(255, 255, 200)
    ),
    'void': Transformation(
        'void', 'Void Form', TransformationType.VOID,
        attack_bonus=0.3, defense_bonus=0.3, speed_bonus=0.2,
        special_effect='time_slow', activation='focus_below_10',
        description='Transform when focus is depleted. Slows time.',
        color=(100, 0, 100)
    ),
}


class TransformationSystem:
    """Transformation management"""
    
    def __init__(self, player):
        self.player = player
        self.active_transformation: Optional[Transformation] = None
    
    def unlock(self, transform_id: str) -> bool:
        """Unlock a transformation"""
        if transform_id in TRANSFORMATIONS:
            TRANSFORMATIONS[transform_id].unlocked = True
            return True
        return False
    
    def try_activate(self, transform_id: str) -> bool:
        """Try to activate transformation"""
        if transform_id not in TRANSFORMATIONS:
            return False
        
        transform = TRANSFORMATIONS[transform_id]
        if not transform.unlocked:
            return False
        
        if self.active_transformation:
            self.deactivate()
        
        transform.active = True
        self.active_transformation = transform
        return True
    
    def try_auto_activate(self) -> bool:
        """Try to auto-activate based on conditions"""
        if self.active_transformation:
            return False
        
        for transform in TRANSFORMATIONS.values():
            if not transform.unlocked:
                continue
            
            should_activate = False
            
            if transform.activation == 'health_below_30':
                should_activate = self.player.health / self.player.max_health < 0.3
            elif transform.activation == 'focus_full':
                should_activate = self.player.focus >= self.player.max_focus
            elif transform.activation == 'focus_below_10':
                should_activate = self.player.focus / self.player.max_focus < 0.1
            
            if should_activate:
                return self.try_activate(transform.id)
        
        return False
    
    def deactivate(self):
        """Deactivate current transformation"""
        if self.active_transformation:
            self.active_transformation.active = False
            self.active_transformation = None
    
    def get_attack_bonus(self) -> float:
        """Get total attack bonus"""
        if self.active_transformation:
            return self.active_transformation.attack_bonus
        return 0
    
    def get_defense_bonus(self) -> float:
        """Get total defense bonus"""
        if self.active_transformation:
            return self.active_transformation.defense_bonus
        return 0
    
    def get_speed_bonus(self) -> float:
        """Get total speed bonus"""
        if self.active_transformation:
            return self.active_transformation.speed_bonus
        return 0


# ==================== COMBAT MODIFIERS ====================
class CombatModifiers:
    """Calculate combat modifiers from all sources"""
    
    def __init__(self, player, weapon_system, transformation_system):
        self.player = player
        self.weapon = weapon_system
        self.transformation = transformation_system
    
    def get_damage(self) -> int:
        """Calculate total damage"""
        # Base + weapon + transformation
        damage = self.player.attack_power + self.weapon.get_damage()
        damage *= (1 + self.transformation.get_attack_bonus())
        return int(damage)
    
    def get_defense(self) -> int:
        """Calculate total defense"""
        defense = self.player.defense
        defense *= (1 + self.transformation.get_defense_bonus())
        return int(defense)
    
    def get_speed(self) -> float:
        """Calculate total speed multiplier"""
        speed = self.weapon.get_attack_speed()
        speed *= (1 + self.transformation.get_speed_bonus())
        return speed
