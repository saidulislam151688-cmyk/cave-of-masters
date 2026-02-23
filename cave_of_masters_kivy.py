#!/usr/bin/env python3
"""
Cave of Masters - Kivy Version
Optimized for Android with touch controls
"""

import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
import random
import math

# Set window size for testing
Window.size = (1080, 1920)

# Colors
COLORS = {
    'bg_dark': (0.05, 0.05, 0.1, 1),
    'primary': (0.58, 0.2, 0.92, 1),
    'secondary': (0.96, 0.62, 0.04, 1),
    'health': (0.94, 0.27, 0.27, 1),
    'stamina': (0.13, 0.77, 0.37, 1),
    'focus': (0.23, 0.51, 0.96, 1),
    'text': (1, 1, 1, 1),
    'enemy': (1, 0.4, 0.4, 1),
    'boss': (0.6, 0.2, 0.6, 1),
}


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state = 'MENU'
        self.player = None
        self.enemies = []
        self.ground_y = 1400
        
        # Build UI
        self.build_menu()
        
    def build_menu(self):
        self.clear_widgets()
        
        with self.canvas:
            Color(*COLORS['bg_dark'])
            Rectangle(size=Window.size)
        
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        title = Label(text='CAVE OF MASTERS', font_size=72, color=COLORS['secondary'])
        subtitle = Label(text='The Path to Inner Legend', font_size=32, color=(0.7, 0.7, 0.8, 1))
        
        start_btn = Button(text='START GAME', size_hint_y=None, height=100,
                          background_color=COLORS['primary'], font_size=32)
        start_btn.bind(on_press=self.start_game)
        
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(start_btn)
        
        self.add_widget(layout)
        
        # Controls info
        controls = Label(text='Controls:\nA/D - Move\nW/Space - Jump\nJ/Z - Attack\nS - Dodge\nCtrl - Block',
                        font_size=24, color=(0.6, 0.6, 0.7, 1), pos=(50, 300))
        self.add_widget(controls)
    
    def start_game(self, instance):
        self.player = {
            'x': 540, 'y': self.ground_y,
            'vx': 0, 'vy': 0,
            'health': 100, 'max_health': 100,
            'stamina': 50, 'max_stamina': 50,
            'focus': 30, 'max_focus': 30,
            'level': 1, 'xp': 0, 'xp_next': 100,
            'on_ground': True, 'facing_right': True,
            'state': 'idle', 'attacking': False,
            'attack_timer': 0, 'combo': 0,
            'block': False, 'dodge_timer': 0,
            'invincible': False, 'color': (0.4, 0.8, 1, 1)
        }
        
        self.enemies = []
        self.game_state = 'PLAYING'
        self.cave_level = 1
        self.room = 0
        
        self.spawn_enemies()
        self.build_game_ui()
    
    def spawn_enemies(self):
        self.enemies = []
        count = 2 + self.room
        for i in range(count):
            self.enemies.append({
                'x': 200 + i * 300,
                'y': self.ground_y,
                'vx': 0, 'vy': 0,
                'health': 30 + self.cave_level * 10,
                'max_health': 30 + self.cave_level * 10,
                'damage': 8 + self.cave_level * 2,
                'speed': 2 + self.cave_level * 0.5,
                'type': 'soldier' if self.cave_level < 3 else 'elite',
                'on_ground': True,
                'facing_right': False,
                'state': 'idle',
                'attack_cooldown': 0,
                'color': COLORS['enemy']
            })
    
    def build_game_ui(self):
        self.clear_widgets()
        
        # Game area
        game_layout = BoxLayout(orientation='vertical')
        
        # Top bar (enemy health bars - would be added dynamically)
        self.top_bar = BoxLayout(size_hint_y=None, height=50, padding=10)
        self.add_widget(self.top_bar)
        
        # Game canvas (main play area)
        self.game_canvas = BoxLayout()
        self.add_widget(self.game_canvas)
        
        # Bottom controls
        controls = self.build_controls()
        self.add_widget(controls)
        
        # Start game loop
        Clock.schedule_interval(self.update, 1/60)
    
    def build_controls(self):
        controls = BoxLayout(size_hint_y=None, height=250, padding=20)
        
        # Left side - movement
        left_layout = BoxLayout(orientation='vertical', size_hint_x=0.4)
        
        # Jump button
        jump_btn = Button(text='↑', font_size=40, background_color=(0.3, 0.3, 0.4, 1))
        jump_btn.bind(on_press=self.jump)
        left_layout.add_widget(jump_btn)
        
        # Left/Right buttons
        move_layout = BoxLayout(size_hint_y=None, height=80)
        left_btn = Button(text='←', font_size=40, background_color=(0.3, 0.3, 0.4, 1),
                         on_press=lambda x: self.set_move(-1))
        right_btn = Button(text='→', font_size=40, background_color=(0.3, 0.3, 0.4, 1),
                          on_press=lambda x: self.set_move(1))
        move_layout.add_widget(left_btn)
        move_layout.add_widget(right_btn)
        left_layout.add_widget(move_layout)
        
        controls.add_widget(left_layout)
        
        # Right side - actions
        right_layout = GridLayout(cols=2, size_hint_x=0.6, padding=10, spacing=10)
        
        attack_btn = Button(text='ATTACK', font_size=28, background_color=COLORS['health'],
                           on_press=self.attack)
        dodge_btn = Button(text='DODGE', font_size=28, background_color=COLORS['primary'],
                          on_press=self.dodge)
        block_btn = Button(text='BLOCK', font_size=28, background_color=COLORS['focus'],
                         on_press=self.start_block, on_release=self.stop_block)
        
        right_layout.add_widget(attack_btn)
        right_layout.add_widget(dodge_btn)
        right_layout.add_widget(block_btn)
        
        controls.add_widget(right_layout)
        
        return controls
    
    def jump(self, instance):
        if self.player and self.player['on_ground']:
            self.player['vy'] = -25
            self.player['on_ground'] = False
    
    def set_move(self, direction):
        if self.player:
            self.player['vx'] = direction * 8
            self.player['facing_right'] = direction > 0
    
    def attack(self, instance):
        if not self.player or self.player['attacking']:
            return
        
        self.player['attacking'] = True
        self.player['attack_timer'] = 20
        self.player['combo'] += 1
        
        # Check hits
        attack_x = self.player['x'] + (60 if self.player['facing_right'] else -60)
        
        for enemy in self.enemies:
            if abs(enemy['x'] - attack_x) < 80:
                damage = 10 + self.player.get('combo', 1) * 2
                enemy['health'] -= damage
                enemy['vx'] = 10 if self.player['facing_right'] else -10
    
    def dodge(self, instance):
        if not self.player or self.player['dodge_timer'] > 0:
            return
        
        if self.player['stamina'] >= 15:
            self.player['stamina'] -= 15
            self.player['dodge_timer'] = 30
            self.player['invincible'] = True
            self.player['vx'] = 20 if self.player['facing_right'] else -20
    
    def start_block(self, instance):
        if self.player:
            self.player['block'] = True
    
    def stop_block(self, instance):
        if self.player:
            self.player['block'] = False
    
    def update(self, dt):
        if self.game_state != 'PLAYING' or not self.player:
            return
        
        p = self.player
        
        # Physics
        p['vy'] += 0.8  # Gravity
        p['y'] += p['vy']
        p['x'] += p['vx']
        
        # Ground collision
        if p['y'] <= self.ground_y:
            p['y'] = self.ground_y
            p['vy'] = 0
            p['on_ground'] = True
        
        # Friction
        p['vx'] *= 0.9
        
        # Bounds
        p['x'] = max(50, min(1030, p['x']))
        
        # Timers
        if p['attack_timer'] > 0:
            p['attack_timer'] -= 1
            if p['attack_timer'] <= 0:
                p['attacking'] = False
        
        if p['dodge_timer'] > 0:
            p['dodge_timer'] -= 1
            if p['dodge_timer'] <= 15:
                p['invincible'] = False
        
        # Regen
        p['stamina'] = min(p['max_stamina'], p['stamina'] + 0.2)
        p['focus'] = min(p['max_focus'], p['focus'] + 0.1)
        
        # Update enemies
        for enemy in self.enemies[:]:
            if enemy['health'] <= 0:
                self.enemies.remove(enemy)
                p['xp'] += 20
                continue
            
            # AI
            dx = p['x'] - enemy['x']
            dist = abs(dx)
            
            if dist > 200:
                enemy['vx'] = enemy['speed'] if dx > 0 else -enemy['speed']
            elif dist > 60 and enemy['attack_cooldown'] <= 0:
                enemy['vx'] = 0
                enemy['attack_cooldown'] = 60
            
            enemy['x'] += enemy['vx']
            enemy['x'] = max(50, min(1030, enemy['x']))
            
            if enemy['attack_cooldown'] > 0:
                enemy['attack_cooldown'] -= 1
            
            # Check attack hit
            if enemy['attack_cooldown'] == 30 and dist < 80:
                if not p['block'] and not p['invincible']:
                    p['health'] -= enemy['damage']
                elif p['block']:
                    p['health'] -= enemy['damage'] * 0.3
        
        # Check room complete
        if len(self.enemies) == 0:
            self.room += 1
            if self.room >= 5:
                self.victory()
            else:
                self.spawn_enemies()
        
        # Check death
        if p['health'] <= 0:
            self.game_over()
        
        # Level up
        if p['xp'] >= p['xp_next']:
            p['level'] += 1
            p['xp'] -= p['xp_next']
            p['xp_next'] = int(p['xp_next'] * 1.5)
            p['max_health'] += 10
            p['health'] = p['max_health']
        
        # Redraw
        self.draw_game()
    
    def draw_game(self):
        self.clear_widgets()
        
        # Background
        with self.canvas:
            Color(*COLORS['bg_dark'])
            Rectangle(size=Window.size)
        
        # Ground
        with self.canvas:
            Color(0.15, 0.12, 0.15, 1)
            Rectangle(pos=(0, self.ground_y - 50), size=(1080, 200))
        
        # Player
        if self.player:
            p = self.player
            with self.canvas:
                Color(*p['color'])
                Rectangle(pos=(p['x'] - 30, p['y']), size=(60, 120))
                # Eyes
                Color(1, 1, 1, 1)
                eye_x = p['x'] + (15 if p['facing_right'] else -25)
                Rectangle(pos=(eye_x, p['y'] + 90), size=(10, 10))
            
            # Health bar
            self.draw_bar(p['x'] - 40, p['y'] + 130, 80, 10, 
                         p['health'], p['max_health'], COLORS['health'])
            # Stamina bar
            self.draw_bar(p['x'] - 40, p['y'] + 145, 80, 8,
                         p['stamina'], p['max_stamina'], COLORS['stamina'])
            # Focus bar
            self.draw_bar(p['x'] - 40, p['y'] + 156, 80, 6,
                         p['focus'], p['max_focus'], COLORS['focus'])
        
        # Enemies
        for enemy in self.enemies:
            with self.canvas:
                Color(*enemy['color'])
                Rectangle(pos=(enemy['x'] - 30, enemy['y']), size=(60, 120))
            
            # Health bar
            self.draw_bar(enemy['x'] - 30, enemy['y'] + 130, 60, 8,
                         enemy['health'], enemy['max_health'], (0.8, 0.2, 0.2, 1))
        
        # UI Overlay
        self.draw_ui()
    
    def draw_bar(self, x, y, w, h, current, max_val, color):
        with self.canvas:
            Color(0.2, 0.2, 0.2, 1)
            Rectangle(pos=(x, y), size=(w, h))
            if max_val > 0:
                Color(*color)
                Rectangle(pos=(x, y), size=(w * (current / max_val), h))
    
    def draw_ui(self):
        # Player stats
        if self.player:
            p = self.player
            
            # Level
            level_text = Label(text=f"LV.{p['level']}", pos=(50, 1800),
                             color=COLORS['secondary'], font_size=32)
            self.add_widget(level_text)
            
            # XP bar
            xp_text = Label(text=f"XP: {p['xp']}/{p['xp_next']}", pos=(50, 1750),
                           color=COLORS['text'], font_size=24)
            self.add_widget(xp_text)
            
            # Combo
            if p['combo'] > 1:
                combo_text = Label(text=f"{p['combo']} HIT!", pos=(500, 1700),
                                 color=COLORS['secondary'], font_size=40)
                self.add_widget(combo_text)
            
            # Room info
            room_text = Label(text=f"Room {self.room + 1}/5", pos=(950, 1800),
                             color=(0.6, 0.6, 0.7, 1), font_size=28)
            self.add_widget(room_text)
    
    def victory(self):
        self.game_state = 'VICTORY'
        self.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=100, spacing=30)
        layout.add_widget(Label(text='VICTORY!', font_size=72, color=COLORS['secondary']))
        layout.add_widget(Label(text='Cave Complete!', font_size=36, color=COLORS['text']))
        
        btn = Button(text='Continue', size_hint_y=None, height=80,
                    background_color=COLORS['primary'], font_size=28)
        btn.bind(on_press=lambda x: self.build_menu())
        layout.add_widget(btn)
        
        self.add_widget(layout)
    
    def game_over(self):
        self.game_state = 'GAMEOVER'
        self.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=100, spacing=30)
        layout.add_widget(Label(text='DEFEATED', font_size=72, color=COLORS['health']))
        
        btn = Button(text='Try Again', size_hint_y=None, height=80,
                    background_color=COLORS['primary'], font_size=28)
        btn.bind(on_press=self.start_game)
        layout.add_widget(btn)
        
        self.add_widget(layout)


class CaveOfMastersApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(GameScreen(name='game'))
        return sm


if __name__ == '__main__':
    CaveOfMastersApp().run()
