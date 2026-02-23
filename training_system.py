"""
TRAINING SYSTEM - Non-combat progression through training rooms
"""

from enum import Enum, auto
from typing import Dict, Callable, Optional
import time


class TrainingType(Enum):
    """Training room types"""
    HEAT_CHAMBER = auto()
    BALANCE_PILLARS = auto()
    STONE_POST = auto()
    FLOW_WATER = auto()
    MEDITATION = auto()
    IRON_SANDBOX = auto()


class TrainingRoom:
    """Training room definition"""
    
    def __init__(self, room_id: str, name: str, training_type: TrainingType,
                 stat_bonus: str, bonus_per_tick: float, max_bonus: float,
                 duration_seconds: int, description: str, icon: str = '🎯'):
        self.id = room_id
        self.name = name
        self.type = training_type
        self.stat_bonus = stat_bonus
        self.bonus_per_tick = bonus_per_tick
        self.max_bonus = max_bonus
        self.duration = duration_seconds
        self.description = description
        self.icon = icon
        
        # Player progress
        self.current_bonus = 0.0
        self.unlocked = False
    
    def train(self, seconds: float) -> Dict:
        """Train in this room"""
        if not self.unlocked:
            return {"success": False, "message": "Locked"}
        
        # Calculate bonus gained
        bonus_gained = self.bonus_per_tick * seconds
        self.current_bonus = min(self.max_bonus, self.current_bonus + bonus_gained)
        
        return {
            "success": True,
            "bonus_gained": bonus_gained,
            "total_bonus": self.current_bonus,
            "max_bonus": self.max_bonus,
            "progress": self.current_bonus / self.max_bonus
        }
    
    def get_stat_modifier(self) -> float:
        """Get current stat modifier"""
        return 1.0 + self.current_bonus


# ==================== TRAINING ROOMS DATABASE ====================
TRAINING_ROOMS: Dict[str, TrainingRoom] = {
    'heat_chamber': TrainingRoom(
        'heat_chamber', 'Heat Chamber', TrainingType.HEAT_CHAMBER,
        stat_bonus='fire_resist',
        bonus_per_tick=0.005,
        max_bonus=0.3,
        duration_seconds=60,
        description='Stand in the heat to gain fire resistance and fire damage bonus.',
        icon='🔥'
    ),
    'balance_pillars': TrainingRoom(
        'balance_pillars', 'Balance Pillars', TrainingType.BALANCE_PILLARS,
        stat_bonus='dodge_window',
        bonus_per_tick=0.003,
        max_bonus=0.2,
        duration_seconds=50,
        description='Dodge falling pillars to improve dodge timing window.',
        icon='🏃'
    ),
    'stone_post': TrainingRoom(
        'stone_post', 'Stone Post', TrainingType.STONE_POST,
        stat_bonus='combo_timing',
        bonus_per_tick=0.004,
        max_bonus=0.15,
        duration_seconds=40,
        description='Hit the post in rhythm to improve combo timing.',
        icon='👊'
    ),
    'flow_water': TrainingRoom(
        'flow_water', 'Flow Water', TrainingType.FLOW_WATER,
        stat_bonus='stamina_recovery',
        bonus_per_tick=0.003,
        max_bonus=0.2,
        duration_seconds=60,
        description='Walk in flowing water to improve stamina recovery.',
        icon='💧'
    ),
    'meditation': TrainingRoom(
        'meditation', 'Meditation', TrainingType.MEDITATION,
        stat_bonus='focus_growth',
        bonus_per_tick=0.004,
        max_bonus=0.25,
        duration_seconds=50,
        description='Meditate to increase focus gain from actions.',
        icon='🧘'
    ),
    'iron_sandbox': TrainingRoom(
        'iron_sandbox', 'Iron Sandbox', TrainingType.IRON_SANDBOX,
        stat_bonus='defense',
        bonus_per_tick=0.002,
        max_bonus=0.15,
        duration_seconds=45,
        description='Block incoming attacks to improve defense.',
        icon='🛡️'
    ),
}


class TrainingSystem:
    """Training room management"""
    
    def __init__(self, player):
        self.player = player
        self.current_room: Optional[TrainingRoom] = None
        self.session_start = 0
        self.total_trained = {k: 0.0 for k in TRAINING_ROOMS}
    
    def unlock_room(self, room_id: str) -> bool:
        """Unlock a training room"""
        if room_id in TRAINING_ROOMS:
            TRAINING_ROOMS[room_id].unlocked = True
            return True
        return False
    
    def enter_room(self, room_id: str) -> bool:
        """Enter a training room"""
        if room_id not in TRAINING_ROOMS:
            return False
        
        room = TRAINING_ROOMS[room_id]
        if not room.unlocked:
            return False
        
        self.current_room = room
        self.session_start = time.time()
        return True
    
    def exit_room(self) -> Dict:
        """Exit current training room"""
        if not self.current_room:
            return {"success": False}
        
        session_time = time.time() - self.session_start
        result = self.current_room.train(session_time)
        
        self.total_trained[self.current_room.id] += session_time
        
        self.current_room = None
        return result
    
    def update(self) -> Optional[Dict]:
        """Update training (called each frame)"""
        if not self.current_room:
            return None
        
        # Each second, apply training
        session_time = time.time() - self.session_start
        if session_time >= 1.0:  # Every second
            result = self.current_room.train(1.0)
            self.total_trained[self.current_room.id] += 1.0
            return result
        
        return None
    
    def get_bonus(self, stat_name: str) -> float:
        """Get bonus for a specific stat"""
        total = 1.0
        for room in TRAINING_ROOMS.values():
            if room.unlocked and room.stat_bonus == stat_name:
                total += room.current_bonus
        return total
    
    def get_training_progress(self) -> Dict:
        """Get progress for all training rooms"""
        return {
            room_id: {
                'unlocked': room.unlocked,
                'bonus': room.current_bonus,
                'max_bonus': room.max_bonus,
                'progress': room.current_bonus / room.max_bonus if room.unlocked else 0
            }
            for room_id, room in TRAINING_ROOMS.items()
        }


# ==================== MASTERS & ABILITIES ====================
class MasterAbility:
    """Master ability definition"""
    
    def __init__(self, ability_id: str, name: str, description: str,
                 unlock_cave: int, icon: str = '⭐'):
        self.id = ability_id
        self.name = name
        self.description = description
        self.unlock_cave = unlock_cave
        self.icon = icon
        self.unlocked = False
        self.level = 0


# ==================== MASTERS DATABASE ====================
MASTERS: Dict[str, MasterAbility] = {
    'dash': MasterAbility(
        'dash', 'Dash Master', 'Dash to cancel attacks and close distance',
        unlock_cave=1, icon='💨'
    ),
    'air': MasterAbility(
        'air', 'Air Master', 'Full air combat control with air combos',
        unlock_cave=2, icon='🌀'
    ),
    'parry': MasterAbility(
        'parry', 'Parry Master', 'Turn defense into offense with perfect parries',
        unlock_cave=3, icon='⚡'
    ),
    'clone': MasterAbility(
        'clone', 'Shadow Master', 'Summon shadow clones to fight',
        unlock_cave=4, icon='👥'
    ),
    'stance': MasterAbility(
        'stance', 'Void Master', 'Switch stances mid-combat',
        unlock_cave=5, icon='🔮'
    ),
}


class MasterSystem:
    """Master ability management"""
    
    def __init__(self, player):
        self.player = player
        self.unlocked_masters = ['basic']
    
    def unlock_master(self, master_id: str) -> bool:
        """Unlock a master"""
        if master_id in MASTERS:
            MASTERS[master_id].unlocked = True
            if master_id not in self.unlocked_masters:
                self.unlocked_masters.append(master_id)
            return True
        return False
    
    def is_unlocked(self, master_id: str) -> bool:
        """Check if master is unlocked"""
        return master_id in self.unlocked_masters
    
    def get_available_masters(self, cave_completed: int) -> list:
        """Get masters available to unlock"""
        available = []
        for master_id, master in MASTERS.items():
            if not master.unlocked and master.unlock_cave <= cave_completed:
                available.append(master)
        return available


# ==================== SKILL TREE ====================
class Skill:
    """Skill tree skill"""
    
    def __init__(self, skill_id: str, name: str, tree: str, tier: int,
                 cost: int, effect: Dict, description: str, icon: str = '✨'):
        self.id = skill_id
        self.name = name
        self.tree = tree
        self.tier = tier
        self.cost = cost
        self.effect = effect
        self.description = description
        self.icon = icon
        self.unlocked = False


# ==================== SKILLS DATABASE ====================
SKILLS: Dict[str, Skill] = {
    # Combat Tree
    'quick_strike': Skill('quick_strike', 'Quick Strike', 'combat', 1, 1,
                          {'startup_reduction': 0.05}, 'Reduce attack startup by 5%'),
    'heavy_hitter': Skill('heavy_hitter', 'Heavy Hitter', 'combat', 1, 2,
                          {'damage_bonus': 0.15}, 'Increase damage by 15%'),
    'flow_state': Skill('flow_state', 'Flow State', 'combat', 2, 3,
                        {'recovery_reduction': 0.1}, 'Reduce recovery frames by 10%'),
    'lethal_finisher': Skill('lethal_finisher', 'Lethal Finisher', 'combat', 2, 3,
                            {'finisher_bonus': 0.3}, 'Increase finisher damage by 30%'),
    'bloodlust': Skill('bloodlust', 'Bloodlust', 'combat', 3, 2,
                       {'damage_on_low_health': 0.2}, 'Deal 20% more damage when HP < 30%'),
    
    # Defense Tree
    'iron_skin': Skill('iron_skin', 'Iron Skin', 'defense', 1, 1,
                       {'defense_bonus': 0.1}, 'Increase defense by 10%'),
    'perfect_block': Skill('perfect_block', 'Perfect Block', 'defense', 1, 2,
                          {'block_efficiency': 0.2}, 'Improve blocking by 20%'),
    'counter_strike': Skill('counter_strike', 'Counter Strike', 'defense', 2, 3,
                            {'counter_damage': 0.5}, 'Counter attacks deal 50% damage'),
    'second_wind': Skill('second_wind', 'Second Wind', 'defense', 3, 2,
                         {'revive_once': True}, 'Revive once with 25% HP'),
    'damage_aura': Skill('damage_aura', 'Damage Aura', 'defense', 3, 3,
                         {'reflect_damage': 0.1}, 'Reflect 10% damage to attackers'),
    
    # Mobility Tree
    'swift_dodge': Skill('swift_dodge', 'Swift Dodge', 'mobility', 1, 1,
                         {'dodge_distance': 0.15}, 'Increase dodge distance by 15%'),
    'air_dancer': Skill('air_dancer', 'Air Dancer', 'mobility', 1, 2,
                       {'air_dodge_count': 1}, 'Add one extra air dodge'),
    'shadow_step': Skill('shadow_step', 'Shadow Step', 'mobility', 2, 3,
                         {'dodge_iframes': True}, 'Gain invincibility during dodge'),
    'wall_jump': Skill('wall_jump', 'Wall Jump', 'mobility', 2, 2,
                       {'wall_jump': True}, 'Can jump off walls'),
    'teleport': Skill('teleport', 'Teleport', 'mobility', 3, 3,
                      {'teleport_dodge': True}, 'Dodge teleports through enemies'),
    
    # Endurance Tree
    'vitality': Skill('vitality', 'Vitality', 'endurance', 1, 1,
                      {'health_bonus': 0.1}, 'Increase max HP by 10%'),
    'stamina_boost': Skill('stamina_boost', 'Stamina', 'endurance', 1, 1,
                          {'stamina_bonus': 0.15}, 'Increase max stamina by 15%'),
    'focus_boost': Skill('focus_boost', 'Focus', 'endurance', 1, 1,
                        {'focus_bonus': 0.15}, 'Increase max focus by 15%'),
    'regeneration': Skill('regeneration', 'Regeneration', 'endurance', 2, 2,
                          {'health_regen': 1}, 'Regenerate 1 HP per second'),
    'adrenaline': Skill('adrenaline', 'Adrenaline', 'endurance', 2, 2,
                        {'stamina_regen': 0.2}, 'Increase stamina regen by 20%'),
}


class SkillTreeSystem:
    """Skill tree management"""
    
    def __init__(self, player):
        self.player = player
        self.skill_points = 0
        self.unlocked_skills = []
    
    def add_skill_points(self, amount: int):
        """Add skill points"""
        self.skill_points += amount
    
    def unlock_skill(self, skill_id: str) -> bool:
        """Unlock a skill"""
        if skill_id not in SKILLS:
            return False
        
        skill = SKILLS[skill_id]
        
        if skill.unlocked:
            return False
        
        if self.skill_points < skill.cost:
            return False
        
        # Check prerequisites
        # (In a full implementation, check skill tree dependencies)
        
        self.skill_points -= skill.cost
        skill.unlocked = True
        self.unlocked_skills.append(skill_id)
        
        # Apply effect
        self.apply_skill_effect(skill)
        
        return True
    
    def apply_skill_effect(self, skill: Skill):
        """Apply skill effect to player"""
        effect = skill.effect
        
        if 'health_bonus' in effect:
            self.player.max_health = int(self.player.max_health * (1 + effect['health_bonus']))
            self.player.health = self.player.max_health
        
        if 'stamina_bonus' in effect:
            self.player.max_stamina = int(self.player.max_stamina * (1 + effect['stamina_bonus']))
            self.player.stamina = self.player.max_stamina
        
        if 'focus_bonus' in effect:
            self.player.max_focus = int(self.player.max_focus * (1 + effect['focus_bonus']))
            self.player.focus = self.player.max_focus
        
        if 'damage_bonus' in effect:
            self.player.attack_power = int(self.player.attack_power * (1 + effect['damage_bonus']))
        
        if 'defense_bonus' in effect:
            self.player.defense = int(self.player.defense * (1 + effect['defense_bonus']))
    
    def get_skill_tree(self, tree_name: str) -> Dict:
        """Get skills in a tree"""
        return {
            sid: skill for sid, skill in SKILLS.items()
            if skill.tree == tree_name
        }
    
    def get_available_skills(self) -> list:
        """Get skills that can be unlocked"""
        available = []
        for skill in SKILLS.values():
            if not skill.unlocked and self.skill_points >= skill.cost:
                available.append(skill)
        return available
