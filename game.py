import pgzrun
import math
import os
from pygame import Rect

# --- VS CODE TRICK ---
try:
    from pgzero.builtins import Actor, keyboard, keys, sounds, music, screen
except ImportError:
    pass

# --- CONFIGURATION ---
WIDTH = 1200
HEIGHT = 550
TITLE = "Magic Cave"
TILE_SIZE = 50
gravity = 1

# States: 'menu', 'instructions', 'game', 'game_over', 'win'
game_state = "menu"
current_level = 1 
sound_enabled = True 

# Map Data
map_data = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,1], 
    [1,0,0,0,0,0,0,0,1,1,2,2,1,1,0,0,0,0,0,0,9,0,0,1], 
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]  
]

class Entity(Actor):
    def __init__(self, img_base, pos):
        super().__init__(f"{img_base}_idle1", pos)
        self.img_base = img_base
        self.timer = 0
        self.frame = 0
        self.state = "idle"
        self.vx = 0
        self.vy = 0 
        self.direction = "right" 
        
    def animate(self, dt):
        self.timer += dt
        if self.timer > 0.15: 
            self.timer = 0
            self.frame = (self.frame + 1) % 2
            
            prefix = ""
            if self.direction == "left": prefix = "left_"
            
            if self.state == "idle": 
                nome_imagem = f"{self.img_base}_{prefix}idle{self.frame + 1}"
            else: 
                nome_imagem = f"{self.img_base}_{prefix}walk{self.frame + 1}"
            
            try: self.image = nome_imagem
            except: self.image = f"{self.img_base}_idle1"

class Player(Entity):
    def __init__(self, pos):
        super().__init__("hero", pos)
        self.speed = 5
        self.jump_power = -17
        self.on_ground = False
        self.lives = 3
        self.invulnerable_timer = 0
        self.attack_cooldown = 0

    def attack(self, enemies_list):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = 0.5 
            atk_x = self.x + 20
            if self.direction == "left": atk_x = self.x - 20
            
            hitbox_ataque = Rect(int(atk_x - 30), int(self.y - 40), 60, 80)
            
            hit_alguem = False
            for enemy in enemies_list[:]: 
                if hitbox_ataque.colliderect(enemy._rect):
                    enemies_list.remove(enemy) 
                    hit_alguem = True
            
            if hit_alguem and sound_enabled:
                try: sounds.zombie_attack.play()
                except: pass

    # Modificado para receber a lista de inimigos (para checar se todos morreram)
    def update_player(self, dt, walls, hazards, door, enemies_list):
        if self.invulnerable_timer > 0: self.invulnerable_timer -= dt
        if self.attack_cooldown > 0: self.attack_cooldown -= dt

        if keyboard.left:
            self.vx = -self.speed
            self.state = "walk"
            self.direction = "left" 
        elif keyboard.right:
            self.vx = self.speed
            self.state = "walk"
            self.direction = "right" 
        else:
            self.vx = 0
            self.state = "idle"
            
        # Footsteps Sound
        if self.state == "walk" and self.on_ground and sound_enabled:
            try:
                if getattr(sounds, 'passos', None) and sounds.passos.get_num_channels() == 0:
                    sounds.passos.play()
            except: pass
        else:
            try: sounds.passos.stop()
            except: pass

        if (keyboard.up or keyboard.space) and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False

        self.vy += gravity
        self.y += self.vy
        
        # Physics & Collision
        for wall in walls:
            if self.colliderect(wall):
                if self.vy > 0: 
                    self.bottom = wall.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0: 
                    self.top = wall.bottom
                    self.vy = 0
        
        self.x += self.vx
        for wall in walls:
            if self.colliderect(wall):
                if self.vx > 0: self.right = wall.left
                elif self.vx < 0: self.left = wall.right
        
        hitbox_justa = self._rect.inflate(-40, -20)
        for hazard in hazards:
            if hitbox_justa.colliderect(hazard._rect):
                self.take_damage()
                
        if self.y > HEIGHT + 50: self.lives = 0

        # --- PORTA (SÓ ABRE SE NÃO TIVER INIMIGOS) ---
        if door and self.colliderect(door):
            if keyboard.up and self.on_ground:
                if len(enemies_list) == 0: # Verifica se todos morreram
                    return "next_level"
                else:
                    print(f"KILL ALL ENEMIES! Left: {len(enemies_list)}")
                
        return "playing"

    def take_damage(self):
        if self.invulnerable_timer <= 0:
            self.lives -= 1
            self.vy = -10
            self.invulnerable_timer = 2
            
    def draw(self):
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 10) % 2 == 0:
                return 
        super().draw()

class Enemy(Entity):
    def __init__(self, pos, target):
        super().__init__("orc", pos)
        self.target = target
        self.speed = 2
        self.on_ground = False
        self.jump_power = -15
    
    def update_enemy(self, dt, walls):
        dist_x = self.x - self.target.x
        
        # Chase Logic
        if abs(dist_x) < 400 and abs(self.y - self.target.y) < 100:
            self.state = "walk"
            if self.x < self.target.x: 
                self.vx = self.speed
                self.direction = "right"
            else: 
                self.vx = -self.speed
                self.direction = "left"
        else:
            self.state = "idle"
            self.vx = 0

        # Jump Logic
        if self.on_ground and self.vx != 0:
            look_ahead = 40 if self.direction == "right" else -40
            sensor_buraco = Rect(int(self.x + look_ahead), int(self.y + 40), 10, 10)
            
            tem_chao_na_frente = False
            for wall in walls:
                if wall.colliderect(sensor_buraco):
                    tem_chao_na_frente = True
                    break
            
            if not tem_chao_na_frente:
                self.vy = self.jump_power
                self.on_ground = False

        self.vy += gravity
        self.y += self.vy
        self.on_ground = False
        
        for wall in walls:
            if self.colliderect(wall):
                if self.vy > 0:
                    self.bottom = wall.top
                    self.vy = 0
                    self.on_ground = True
        
        self.x += self.vx
        self.animate(dt)

# --- GAME SETUP ---
walls = []
hazards = []
door_actor = None
player = None
enemies = [] 

# Menu Buttons
btn_start = Actor("tile5", center=(WIDTH//2, 220))
btn_instr = Actor("tile5", center=(WIDTH//2, 290))
btn_sound = Actor("tile5", center=(WIDTH//2, 360))
btn_exit = Actor("tile5", center=(WIDTH//2, 430))

def build_level(level_num):
    global walls, hazards, door_actor, player, enemies
    walls = []
    hazards = []
    enemies = [] 
    
    player = Player((100, 200)) 
    
    if level_num == 1:
        enemies.append(Enemy((800, 200), player))
        enemies.append(Enemy((500, 200), player)) 
        enemies.append(Enemy((1000, 200), player)) 
    elif level_num == 2:
        enemies.append(Enemy((600, 200), player))
        enemies.append(Enemy((900, 200), player))
    elif level_num == 3:
        enemies.append(Enemy((400, 200), player))
        enemies.append(Enemy((600, 200), player))
        enemies.append(Enemy((800, 200), player))
        enemies.append(Enemy((1000, 200), player))
    
    for r, row in enumerate(map_data):
        for c, tile in enumerate(row):
            x = c * TILE_SIZE
            y = r * TILE_SIZE
            if tile == 1: walls.append(Actor("tile5", topleft=(x, y)))
            elif tile == 2: hazards.append(Actor("lava1", topleft=(x, y)))
            elif tile == 9: door_actor = Actor("door", topleft=(x, y-50))

build_level(current_level)

def draw():
    screen.clear()
    
    # --- MAIN MENU (COM MÚSICA TOCANDO) ---
    if game_state == "menu":
        screen.fill((30, 30, 30))
        try: screen.blit("menu_fundo", (0,0))
        except: pass
        
        screen.draw.text("MAGIC CAVE", center=(WIDTH//2, 100), fontsize=60, color="yellow", shadow=(2,2))
        
        btn_start.draw()
        btn_instr.draw()
        btn_sound.draw()
        btn_exit.draw()
        
        screen.draw.text("START", center=btn_start.pos, fontsize=30, color="white")
        screen.draw.text("INSTRUCTIONS", center=btn_instr.pos, fontsize=30, color="white")
        txt_som = "SOUND: ON" if sound_enabled else "SOUND: OFF"
        screen.draw.text(txt_som, center=btn_sound.pos, fontsize=30, color="white")
        screen.draw.text("EXIT", center=btn_exit.pos, fontsize=30, color="white")

    elif game_state == "instructions":
        screen.fill((20, 0, 40))
        screen.draw.text("HOW TO PLAY", center=(WIDTH//2, 80), fontsize=60, color="cyan")
        texto = (
            "GOAL: Reach the brown door without dying.\n\n"
            "CONTROLS:\n"
            "[ARROWS] - Move and Jump\n"
            "[SPACE] - Jump\n"
            "[X] - Attack\n"
            "[A] - Skip Level\n"
            "[O] - Mute Sound\n\n"
            "IMPORTANT: You must kill ALL enemies to open the door!"
        )
        screen.draw.text(texto, center=(WIDTH//2, 300), fontsize=35, color="white")
        screen.draw.text("[CLICK TO RETURN]", center=(WIDTH//2, 530), fontsize=30, color="orange")

    elif game_state == "game":
        try: screen.blit("back", (0,0))
        except: screen.fill((50,50,80))
        
        if door_actor: door_actor.draw()
        for w in walls: w.draw()
        for h in hazards: h.draw()
        for e in enemies: e.draw()
        player.draw()

        screen.draw.text(f"Lives: {player.lives} | Level: {current_level}", (20, 20), fontsize=30, color="white")
        
       
        cor_texto = "red" if len(enemies) > 0 else "green"
        screen.draw.text(f"Enemies Left: {len(enemies)}", (WIDTH - 250, 20), fontsize=30, color=cor_texto)
        
        screen.draw.text("[X] Attack   [A] Skip", (20, 50), fontsize=20, color="yellow")
            
    elif game_state == "game_over":
        screen.fill("white") 
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=80, color="red")
        screen.draw.text("[R] Restart   [M] Menu", center=(WIDTH//2, HEIGHT//2 + 80), fontsize=30, color="black")

    elif game_state == "win":
        screen.fill("gold")
        screen.draw.text("YOU WIN!", center=(WIDTH//2, HEIGHT//2), fontsize=80, color="blue")
        screen.draw.text("[R] Restart   [M] Menu", center=(WIDTH//2, HEIGHT//2 + 80), fontsize=30, color="white")

def update(dt):
    global game_state, current_level
    
    # --- MUSIC CONTROLLER ---
    if sound_enabled:
        try:
            # Menu Music Logic
            if game_state in ["menu", "instructions", "game_over"]:
               
                if not music.is_playing('menu'): 
                    music.play('menu')
            elif game_state in ["game", "win"]:
                music.stop()
        except Exception as e: 
            pass 
    else:
        music.stop()

    if game_state == "game":
        player.animate(dt)
        player_hitbox = player._rect.inflate(-50, -20)
        
        for e in enemies:
            e.update_enemy(dt, walls)
            if player_hitbox.colliderect(e._rect):
                player.take_damage()
        
        
        result = player.update_player(dt, walls, hazards, door_actor, enemies)
        
        if player.lives <= 0: 
            game_state = "game_over"
            try: sounds.passos.stop()
            except: pass
        elif result == "next_level":
            passar_de_fase()

def passar_de_fase():
    global current_level, game_state
    try: sounds.passos.stop()
    except: pass
    
    if current_level == 1:
        current_level = 2
        build_level(current_level)
    elif current_level == 2:
        current_level = 3
        build_level(current_level)
    else:
        game_state = "win"
        if sound_enabled:
            try: sounds.vitoria.play() 
            except: pass

def on_mouse_down(pos):
    global game_state, sound_enabled, current_level
    
    if game_state == "menu":
        if btn_start.collidepoint(pos):
            current_level = 1
            build_level(current_level)
            game_state = "game"
        elif btn_instr.collidepoint(pos):
            game_state = "instructions"
        elif btn_sound.collidepoint(pos):
            sound_enabled = not sound_enabled
        elif btn_exit.collidepoint(pos):
            quit()
            
    elif game_state == "instructions":
        game_state = "menu"

def on_key_down(key):
    global game_state, current_level, sound_enabled
    
    if key == keys.O:
        sound_enabled = not sound_enabled
        if not sound_enabled: 
            music.stop()
            try: sounds.passos.stop()
            except: pass

    if (game_state == "game_over" or game_state == "win"):
        if key == keys.R:
            current_level = 1
            build_level(current_level)
            game_state = "game"
        if key == keys.M:
            game_state = "menu"
        
    if game_state == "game":
        if key == keys.X:
            player.attack(enemies)
        if key == keys.A:
            
            enemies.clear() 
            passar_de_fase()

pgzrun.go()