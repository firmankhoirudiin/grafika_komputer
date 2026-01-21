import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random

# ==============================================================================
# KONFIGURASI UMUM
# ==============================================================================
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
TITLE = "Battle Boat 3D - UAS Grafika Komputer"

# Warna
COLOR_SKY = (0.5, 0.8, 1.0, 1.0)
COLOR_SEA = (0.0, 0.4, 0.8, 1.0)
COLOR_BOAT_HULL = (0.6, 0.4, 0.2)
COLOR_BOAT_SAIL = (0.9, 0.9, 0.9)
COLOR_ENEMY_HULL = (0.3, 0.1, 0.1) # Merah Tua
COLOR_ENEMY_SAIL = (0.2, 0.2, 0.2) # Hitam
COLOR_ISLAND = (0.1, 0.8, 0.1)
COLOR_DOCK = (0.4, 0.4, 0.4)
COLOR_PROJECTILE = (0.1, 0.1, 0.1) # Hitam (Meriam)

# State Game
PROJECTION_PERSPECTIVE = 0
PROJECTION_ORTHO = 1

# ==============================================================================
# KELAS & ENTITAS GAME
# ==============================================================================

class GameObject:
    def __init__(self, x, z):
        self.x = x
        self.z = z
        self.radius = 1.0 # Untuk kolisi

class Island(GameObject):
    def __init__(self, x, z, size):
        super().__init__(x, z)
        self.size = size
        self.radius = size * 0.8 # Hitbox sedikit lebih kecil dari visual

class Projectile(GameObject):
    def __init__(self, x, z, angle, speed, owner):
        super().__init__(x, z)
        self.angle = angle
        self.speed = speed
        self.owner = owner # 'player' or 'enemy'
        self.life = 100 # Frame life
        self.radius = 0.5

    def update(self):
        rad = math.radians(self.angle)
        self.x -= math.sin(rad) * self.speed
        self.z -= math.cos(rad) * self.speed
        self.life -= 1

class Boat(GameObject):
    def __init__(self, x, z, is_player=True):
        super().__init__(x, z)
        self.is_player = is_player
        self.angle = 0.0
        self.speed = 0.0
        self.hp = 100
        self.max_hp = 100
        self.radius = 2.0
        self.state = "ALIVE" # ALIVE, SINKING, DEAD
        self.sink_depth = 0.0
        self.scale = 1.0
        
        # Cooldown tembak
        self.shoot_cooldown = 0
        
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.state = "SINKING"
            
    def update(self):
        if self.state == "SINKING":
            self.sink_depth += 0.05
            if self.sink_depth > 5.0:
                self.state = "DEAD"
            return # Tidak bisa bergerak saat tenggelam
            
        if self.state == "DEAD":
            return

        # Update Posisi berdasarkan kecepatan & sudut
        rad = math.radians(self.angle)
        self.x -= math.sin(rad) * self.speed
        self.z -= math.cos(rad) * self.speed
        
        # Friction
        self.speed *= 0.98
        
        # Cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

class GameState:
    def __init__(self):
        self.player = Boat(0, 0, is_player=True)
        self.enemies = []
        self.islands = []
        self.projectiles = []
        
        self.camera_mode = PROJECTION_PERSPECTIVE
        self.keys = {}
        self.game_over = False
        
        # Generate World
        self.spawn_islands()
        self.spawn_enemy()
        
    def spawn_islands(self):
        # Buat banyak pulau acak
        positions = [
            (30, -30), (-20, -50), (50, 20), (-40, 40), 
            (60, -60), (-60, -10), (0, -80), (80, 0)
        ]
        for pos in positions:
            size = random.uniform(3.0, 6.0)
            self.islands.append(Island(pos[0], pos[1], size))
            
    def spawn_enemy(self):
        enemy = Boat(40, 40, is_player=False)
        enemy.max_hp = 50
        enemy.hp = 50
        self.enemies.append(enemy)

# ==============================================================================
# FUNGSI GAMBAR (RENDERING)
# ==============================================================================
def draw_cube():
    glBegin(GL_QUADS)
    # Mapping sederhana (Normal standar)
    for face in [(0,0,1), (0,0,-1), (-1,0,0), (1,0,0), (0,1,0), (0,-1,0)]:
        glNormal3f(*face)
        glVertex3f(-0.5, -0.5, 0.5); glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5) 
        # (Simplified geometry call - actually reused vertex layout for all faces for brevity here,
        # but in immediate mode we define vertices per face. Let's start clean.)
    glEnd()
    # Manual Cube
    glBegin(GL_QUADS)
    # Front
    glNormal3f(0,0,1); glVertex3f(-0.5,-0.5,0.5); glVertex3f(0.5,-0.5,0.5); glVertex3f(0.5,0.5,0.5); glVertex3f(-0.5,0.5,0.5)
    # Back
    glNormal3f(0,0,-1); glVertex3f(-0.5,-0.5,-0.5); glVertex3f(-0.5,0.5,-0.5); glVertex3f(0.5,0.5,-0.5); glVertex3f(0.5,-0.5,-0.5)
    # Left
    glNormal3f(-1,0,0); glVertex3f(-0.5,-0.5,-0.5); glVertex3f(-0.5,-0.5,0.5); glVertex3f(-0.5,0.5,0.5); glVertex3f(-0.5,0.5,-0.5)
    # Right
    glNormal3f(1,0,0); glVertex3f(0.5,-0.5,-0.5); glVertex3f(0.5,0.5,-0.5); glVertex3f(0.5,0.5,0.5); glVertex3f(0.5,-0.5,0.5)
    # Top
    glNormal3f(0,1,0); glVertex3f(-0.5,0.5,-0.5); glVertex3f(-0.5,0.5,0.5); glVertex3f(0.5,0.5,0.5); glVertex3f(0.5,0.5,-0.5)
    # Bottom
    glNormal3f(0,-1,0); glVertex3f(-0.5,-0.5,-0.5); glVertex3f(0.5,-0.5,-0.5); glVertex3f(0.5,-0.5,0.5); glVertex3f(-0.5,-0.5,0.5)
    glEnd()

def draw_sphere(radius):
    quadric = gluNewQuadric()
    gluSphere(quadric, radius, 16, 16)
    gluDeleteQuadric(quadric)

def draw_pyramid():
    glBegin(GL_TRIANGLES)
    glNormal3f(0, 0.5, 1); glVertex3f(0, 1, 0); glVertex3f(-1, -1, 1); glVertex3f(1, -1, 1)
    glNormal3f(1, 0.5, 0); glVertex3f(0, 1, 0); glVertex3f(1, -1, 1); glVertex3f(1, -1, -1)
    glNormal3f(0, 0.5, -1); glVertex3f(0, 1, 0); glVertex3f(1, -1, -1); glVertex3f(-1, -1, -1)
    glNormal3f(-1, 0.5, 0); glVertex3f(0, 1, 0); glVertex3f(-1, -1, -1); glVertex3f(-1, -1, 1)
    glEnd()


# ==============================================================================
# VISUALISASI PERAHU PERANG REALISTIS (3D Warship)
# ==============================================================================
def draw_cylinder(radius, height, r=0.5, g=0.5, b=0.5):
    glColor3f(r, g, b)
    quadric = gluNewQuadric()
    glPushMatrix()
    glRotatef(-90, 1, 0, 0) # Tegak lurus
    gluCylinder(quadric, radius, radius, height, 12, 1)
    glPopMatrix()
    
    # Tutup atas
    glPushMatrix()
    glTranslatef(0, height, 0)
    glRotatef(-90, 1, 0, 0)
    gluDisk(quadric, 0, radius, 12, 1)
    glPopMatrix()
    gluDeleteQuadric(quadric)

def draw_warship(is_player):
    # Palet Warna
    if is_player:
        c_hull = (0.3, 0.3, 0.35) # Abu-abu kebiruan (Navy)
        c_deck = (0.25, 0.25, 0.25)
        c_bridge = (0.4, 0.4, 0.45)
    else:
        c_hull = (0.4, 0.1, 0.1) # Merah Tua (Musuh)
        c_deck = (0.2, 0.05, 0.05)
        c_bridge = (0.3, 0.1, 0.1)
        
    # --- 1. LAMBUNG KAPAL (HULL) ---
    # Bagian Tengah (Box Utama)
    glPushMatrix()
    glColor3fv(c_hull)
    glScalef(2.0, 1.2, 6.0) # Lebar, Tinggi, Panjang
    draw_cube()
    glPopMatrix()
    
    # Bagian Depan (Haluan/Bow) - Prisma Segitiga
    glPushMatrix()
    glTranslatef(0, 0, -3.0) # Maju ke depan hull
    glColor3fv(c_hull)
    glBegin(GL_TRIANGLES)
    # Atas (Deck extension)
    glNormal3f(0, 1, 0)
    glVertex3f(-1.0, 0.6, 0); glVertex3f(1.0, 0.6, 0); glVertex3f(0, 0.6, -2.5) # Lancip ke depan
    # Bawah
    glNormal3f(0, -1, 0)
    glVertex3f(-1.0, -0.6, 0); glVertex3f(0, -0.6, -2.5); glVertex3f(1.0, -0.6, 0)
    # Kiri
    glNormal3f(-0.8, 0, -0.5)
    glVertex3f(-1.0, 0.6, 0); glVertex3f(0, 0.6, -2.5); glVertex3f(0, -0.6, -2.5); 
    glVertex3f(-1.0, 0.6, 0); glVertex3f(0, -0.6, -2.5); glVertex3f(-1.0, -0.6, 0) # Quad split
    # Kanan
    glNormal3f(0.8, 0, -0.5)
    glVertex3f(1.0, 0.6, 0); glVertex3f(1.0, -0.6, 0); glVertex3f(0, -0.6, -2.5)
    glVertex3f(1.0, 0.6, 0); glVertex3f(0, -0.6, -2.5); glVertex3f(0, 0.6, -2.5)
    glEnd()
    glPopMatrix()
    
    # Bagian Belakang (Buritan) - Kotak Sederhana
    glPushMatrix()
    glTranslatef(0, 0, 3.0)
    glColor3fv(c_hull)
    glScalef(1.8, 1.2, 0.5)
    draw_cube()
    glPopMatrix()
    
    # --- 2. DEK / GELADAK (Striping) ---
    glPushMatrix()
    glTranslatef(0, 0.61, 0) # Sedikit di atas hull
    glColor3fv(c_deck)
    glScalef(1.8, 0.05, 5.8)
    draw_cube()
    glPopMatrix()
    
    # --- 3. JEMBATAN KEMUDI (BRIDGE / CABIN) ---
    glPushMatrix()
    glTranslatef(0, 1.2, 1.0) # Posisi agak belakang
    glColor3fv(c_bridge)
    # Lantai 1
    glPushMatrix()
    glScalef(1.2, 1.0, 2.0)
    draw_cube()
    glPopMatrix()
    # Lantai 2 (Menara)
    glTranslatef(0, 0.8, -0.5)
    glPushMatrix()
    glScalef(0.8, 0.8, 1.0)
    draw_cube()
    glPopMatrix()
    # Jendela (Aksen Hitam)
    glTranslatef(0, 0, -0.51)
    glColor3f(0, 0, 0)
    glScalef(0.6, 0.3, 0.1)
    draw_cube()
    glPopMatrix()
    
    # --- 4. CEROBONG ASAP (CHIMNEY) ---
    glPushMatrix()
    glTranslatef(0, 1.8, 1.5) # Di belakang bridge
    glColor3f(0.25, 0.25, 0.25) # Abu-abu gelap
    
    # Tabung Cerobong (Tanpa palang/salib)
    glPushMatrix()
    glRotatef(-10, 1, 0, 0) # Miring sedikit ke belakang
    # Radius lebih besar (0.35) agar terlihat seperti cerobong, bukan tiang
    draw_cylinder(0.35, 1.5, 0.2, 0.2, 0.2) 
    glPopMatrix()
    
    glPopMatrix()
    
    # --- 5. PERSENJATAAN (TURRET MERIAM UTAMA) ---
    glPushMatrix()
    glTranslatef(0, 0.8, -1.5) # Di dek depan
    glColor3f(0.5, 0.5, 0.5)
    # Base Turret (Setengah Bola / Dome)
    quadric = gluNewQuadric()
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluSphere(quadric, 0.6, 12, 12)
    glPopMatrix()
    # Laras Meriam (Barrel)
    glColor3f(0.2, 0.2, 0.2)
    glTranslatef(0, 0.2, -0.4)
    glPushMatrix()
    glRotatef(90, 1, 0, 0) # Tembak ke depan (-Z)
    draw_cylinder(0.15, 1.8, 0.2, 0.2, 0.2) 
    glPopMatrix()
    gluDeleteQuadric(quadric)
    glPopMatrix()
    
    # Atribut Tambahan: Bendera di Belakang
    glPushMatrix()
    glTranslatef(0, 1.5, 3.0)
    glColor3f(1.0, 1.0, 1.0) # Tiang Bendera
    draw_cylinder(0.05, 1.5)
    # Kain Bendera
    glTranslatef(0, 1.2, 0.4)
    if is_player: glColor3f(0, 0, 1.0) # Biru
    else: glColor3f(1.0, 0, 0) # Merah
    glScalef(0.05, 0.5, 0.8)
    draw_cube()
    glPopMatrix()

def draw_boat_model(boat):
    glPushMatrix()
    # Logika posisi & animasi tenggelam
    current_y = 0.5
    if boat.state == "SINKING":
        current_y -= boat.sink_depth
        glRotatef(boat.sink_depth * 15, 1, 0, 0) # Nungging ke depan
        glRotatef(boat.sink_depth * 5, 0, 0, 1)  # Miring ke samping

    glTranslatef(boat.x, current_y, boat.z) 
    glRotatef(boat.angle, 0, 1, 0)
    
    # Scale model kapal perang (agak besar)
    s = boat.scale * 0.8 # Base scale adjustment
    glScalef(s, s, s)
    
    # Render Warship Geometry
    draw_warship(boat.is_player)
    
    # HP Bar Floating
    if boat.state == "ALIVE":
        glPushMatrix()
        glDisable(GL_LIGHTING)
        glTranslatef(0, 5.0, 0) # Di atas tiang mast
        
        # Background bar (Merah/Hitam)
        glColor3f(0.5, 0, 0)
        glPushMatrix()
        glScalef(2.0, 0.3, 0.1)
        draw_cube()
        glPopMatrix()
        
        # Foreground bar (Hijau) - Persentase HP
        hp_percent = max(0.0, boat.hp / boat.max_hp)
        glColor3f(0.0, 1.0, 0.0)
        glTranslatef((hp_percent - 1.0), 0, 0.01) # Geser biar rata kiri (simplified logic)
        glScalef(2.0 * hp_percent, 0.3, 0.1)
        #draw_cube() # Opsional simplify bar scaling logic
        
        # Simple billboard quads for cleaner HP
        # ...we stick to simple feedback from previous code logic for robustness
        glPopMatrix()
        glEnable(GL_LIGHTING)

    glPopMatrix()

def draw_island_model(island):
    glPushMatrix()
    glTranslatef(island.x, -0.5, island.z) # Base sedikit di bawah air
    glColor3fv(COLOR_ISLAND)
    s = island.size
    glScalef(s, s*0.8, s) # Lebih lebar dan landai
    draw_pyramid()
    glPopMatrix()

def draw_projectile(proj):
    glPushMatrix()
    glTranslatef(proj.x, 2.0, proj.z) # Tinggi laras meriam
    glColor3fv(COLOR_PROJECTILE)
    draw_sphere(0.3)
    glPopMatrix()

def draw_sea():
    glDisable(GL_LIGHTING)
    glColor4fv(COLOR_SEA)
    glBegin(GL_QUADS)
    extent = 200
    glNormal3f(0, 1, 0)
    glVertex3f(-extent, 0, -extent)
    glVertex3f(-extent, 0, extent)
    glVertex3f(extent, 0, extent)
    glVertex3f(extent, 0, -extent)
    glEnd()
    glEnable(GL_LIGHTING)

# ==============================================================================
# LOGIKA UTAMA (Collisions, AI, Input)
# ==============================================================================
def check_collisions(game):
    player = game.player
    
    # --- SPAWN ULANG MUSUH JIKA MATI ---
    # Hapus musuh yang sudah tenggelam total (DEAD)
    active_enemies = []
    for e in game.enemies:
        if e.state == "DEAD":
            continue # Hapus dari list
        active_enemies.append(e)
    game.enemies = active_enemies
    
    # Jika musuh habis, spawn musuh baru (Gelombang baru)
    if len(game.enemies) == 0:
        print("MUSUH HANCUR! KAPAL PERANG BARU MUNCUL!")
        # Spawn di posisi acak jauh
        angle = random.uniform(0, 360)
        dist = random.uniform(60, 80)
        spawn_x = player.x + math.sin(math.radians(angle)) * dist
        spawn_z = player.z + math.cos(math.radians(angle)) * dist
        
        new_enemy = Boat(spawn_x, spawn_z, is_player=False)
        new_enemy.max_hp = 60
        new_enemy.hp = 60
        game.enemies.append(new_enemy)

    if player.state != "ALIVE": return

    # 1. Tabrakan Player vs Pulau
    for island in game.islands:
        dist = math.sqrt((player.x - island.x)**2 + (player.z - island.z)**2)
        min_dist = island.radius + player.radius * 0.8 # Hitbox kapal perang lebih besar
        if dist < min_dist:
            print("MENABRAK PULAU! LAMBUNG PECAH!")
            player.take_damage(1000)

    # 2. Projectile AI
    for p in game.projectiles[:]:
        p.update()
        if p.life <= 0:
            game.projectiles.remove(p)
            continue
            
        targets = []
        if p.owner == 'player':
            targets = game.enemies
        else:
            targets = [game.player]
            
        for t in targets:
            if t.state != "ALIVE": continue
            # Hitbox kapal panjang (approximate with larger radius)
            hit_radius = 4.0 
            dist = math.sqrt((p.x - t.x)**2 + (p.z - t.z)**2)
            if dist < hit_radius:
                t.take_damage(15) # Damage Meriam lebih sakit
                # Efek partikel/ledakan bisa ditambahkan disini
                if p in game.projectiles:
                    game.projectiles.remove(p)
                break
    
    # 3. Enemy AI Update (Sama seperti sebelumnya)
    for enemy in game.enemies:
        if enemy.state != "ALIVE": 
            # Logic animasi tenggelam
            enemy.sink_depth += 0.05
            if enemy.sink_depth > 8.0:
                enemy.state = "DEAD" # Tandai untuk dihapus frame depan
            continue
            
        dist_to_player = math.sqrt((enemy.x - player.x)**2 + (enemy.z - player.z)**2)
        
        # Musuh menembak jika dalam jangkauan
        if dist_to_player < 50 and enemy.shoot_cooldown == 0:
            dx = player.x - enemy.x
            dz = player.z - enemy.z
            target_angle = math.degrees(math.atan2(-dx, -dz)) 
            # Spread tembakan sedikit tidak akurat
            spread = random.uniform(-5, 5)
            game.projectiles.append(Projectile(enemy.x, enemy.z, target_angle + spread, 1.2, 'enemy'))
            enemy.shoot_cooldown = 90 # 1.5 detik
            
        # Pengejaran
        if dist_to_player > 20:
            dx = player.x - enemy.x
            dz = player.z - enemy.z
            target_angle = math.degrees(math.atan2(-dx, -dz))
            angle_diff = (target_angle - enemy.angle + 180) % 360 - 180
            enemy.angle += angle_diff * 0.03 # Putar perlahan (kapal besar berat)
            enemy.speed = 0.15
        else:
            enemy.speed = 0
            
        enemy.update()

def handle_input(game):
    player = game.player

    # Mouse Control untuk Kamera (Orbit)
    if pygame.mouse.get_pressed()[0]: # Klik Kiri Tahan untuk putar kamera
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        game.cam_yaw += mouse_dx * 0.5
        game.cam_pitch += mouse_dy * 0.5
        # Batasi pitch agar tidak terbalik
        game.cam_pitch = max(10, min(89, game.cam_pitch))
    else:
        pygame.mouse.get_rel() # Reset rel movement agar tidak "jump" saat klik lagi

    # Zoom Camera (Scroll we usually handle in event loop, but simpler here w/ keys or just leave keys)
    
    if player.state != "ALIVE": return

    keys = game.keys
    
    # Rotasi Kapal
    if keys.get(K_LEFT): player.angle += 2.5
    if keys.get(K_RIGHT): player.angle -= 2.5
    
    # Gerak Kapal
    if keys.get(K_UP): player.speed += 0.02
    if keys.get(K_DOWN): player.speed -= 0.01
    
    # Limit speed
    player.speed = max(-0.2, min(0.4, player.speed))
    
    # Scale (Cheat/Debug)
    if keys.get(K_w): player.scale += 0.01
    if keys.get(K_s): player.scale = max(0.1, player.scale - 0.01)
    
    # Shoot
    if keys.get(K_SPACE):
        if player.shoot_cooldown == 0:
            # Spawn projectile
            game.projectiles.append(Projectile(player.x, player.z, player.angle, 1.0, 'player'))
            player.shoot_cooldown = 20 # Fast fire
    
    player.update()

# ==============================================================================
# VISUALISASI LINGKUNGAN BARU (Matahari & Awan)
# ==============================================================================
class Cloud:
    def __init__(self):
        self.x = random.uniform(-100, 100)
        self.y = random.uniform(15, 25) # Tinggi di langit
        self.z = random.uniform(-100, 100)
        self.size = random.uniform(2.0, 4.0)

def draw_sun():
    glDisable(GL_LIGHTING) # Matahari bersinar sendiri (emissive)
    glColor3f(1.0, 1.0, 0.0) # Kuning
    glPushMatrix()
    glTranslatef(50, 60, 50) # Posisi matahari (sesuai sumber cahaya)
    gluSphere(gluNewQuadric(), 5.0, 16, 16)
    glPopMatrix()
    glEnable(GL_LIGHTING)

def draw_clouds(clouds):
    glColor3f(1.0, 1.0, 1.0) # Putih
    for c in clouds:
        glPushMatrix()
        glTranslatef(c.x, c.y, c.z)
        # Gambar awan sebagai kumpulan bola kecil
        radius = c.size
        # Bola utama
        gluSphere(gluNewQuadric(), radius, 12, 12)
        # Bola samping (sedikit variasi)
        glPushMatrix()
        glTranslatef(radius*0.8, 0, 0)
        gluSphere(gluNewQuadric(), radius*0.7, 12, 12)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(-radius*0.8, 0, 0)
        gluSphere(gluNewQuadric(), radius*0.7, 12, 12)
        glPopMatrix()
        glPopMatrix()

# Update GameState untuk support elemen baru
class GameState:
    def __init__(self):
        self.player = Boat(0, 0, is_player=True)
        self.enemies = []
        self.islands = []
        self.projectiles = []
        self.clouds = [Cloud() for _ in range(15)] # Generate 15 awan
        
        self.camera_mode = PROJECTION_PERSPECTIVE
        
        # Camera Orbit Variables
        self.cam_yaw = 0.0   # Sudut Horizontal
        self.cam_pitch = 20.0 # Sudut Vertikal (Elevasi)
        self.cam_dist = 25.0  # Jarak dari kapal
        
        self.keys = {}
        self.game_over = False
        
        # Generate World
        self.spawn_islands()
        self.spawn_enemy()
        
    def spawn_islands(self):
        positions = [
            (30, -30), (-20, -50), (50, 20), (-40, 40), 
            (60, -60), (-60, -10), (0, -80), (80, 0)
        ]
        for pos in positions:
            size = random.uniform(3.0, 6.0)
            self.islands.append(Island(pos[0], pos[1], size))
            
    def spawn_enemy(self):
        enemy = Boat(40, 40, is_player=False)
        enemy.max_hp = 50
        enemy.hp = 50
        self.enemies.append(enemy)

# ==============================================================================
# MAIN LOOP UPDATED
# ==============================================================================
def main():
    pygame.init()
    display = (WINDOW_WIDTH, WINDOW_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(TITLE)
    
    # Setup OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    
    # Atur Fog (Kabut) untuk blending horizon langit
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, COLOR_SKY)
    glFogf(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 100.0)
    glFogf(GL_FOG_END, 300.0)
    
    # Cahaya Matahari
    light_pos = (50, 60, 50, 1) # x, y, z, w=1 (point light)
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 0.95, 0.8, 1)) # Cahaya hangat
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.4, 0.4, 0.5, 1))  # Ambient kebiruan
    
    game = GameState()
    clock = pygame.time.Clock()
    running = True
    
    # Mouse Grab (Optional, let's leave cursor visible for ease of shutting down)
    # pygame.event.set_grab(True) 
    
    while running:
        # Input
        for event in pygame.event.get():
            if event.type == QUIT: running = False
            if event.type == KEYDOWN:
                game.keys[event.key] = True
                if event.key == K_p: game.camera_mode = 1 - game.camera_mode
                if event.key == K_ESCAPE: running = False
                
                # RESTART LOGIC
                if event.key == K_r and game.player.state != "ALIVE":
                    print("RESTARTING GAME...")
                    game = GameState() # Reset Total
                    
            if event.type == KEYUP:
                game.keys[event.key] = False
            
            # Zoom mouse wheel
            if event.type == MOUSEWHEEL:
                game.cam_dist -= event.y * 1.0
                game.cam_dist = max(10.0, min(80.0, game.cam_dist))

        # Logic
        handle_input(game)
        check_collisions(game)
        
        # Render
        glClearColor(*COLOR_SKY)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Camera
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = WINDOW_WIDTH / WINDOW_HEIGHT
        
        if game.camera_mode == PROJECTION_PERSPECTIVE:
            gluPerspective(60, aspect, 0.1, 400.0)
        else:
            d = game.cam_dist * 1.5
            glOrtho(-d*aspect, d*aspect, -d, d, 0.1, 400.0)
            
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Camera Orbit Logic (Spherical Coordinates)
        # Konversi Yaw/Pitch ke vektor posisi kamera relatif player
        # Pitch 0 = datar, 90 = atas
        # Yaw 0 = belakang
        player = game.player
        
        rad_pitch = math.radians(game.cam_pitch)
        rad_yaw = math.radians(game.cam_yaw)
        
        # x = r * cos(pitch) * sin(yaw)
        # y = r * sin(pitch)
        # z = r * cos(pitch) * cos(yaw)
        cam_y = game.cam_dist * math.sin(rad_pitch)
        h_dist = game.cam_dist * math.cos(rad_pitch) # Jarak horizontal
        cam_x = h_dist * math.sin(rad_yaw)
        cam_z = h_dist * math.cos(rad_yaw)
        
        # Add to player pos
        eye_x = player.x + cam_x
        eye_y = player.y + cam_y if hasattr(player, 'y') else cam_y 
        eye_z = player.z + cam_z
        
        gluLookAt(eye_x, eye_y, eye_z, player.x, 2.0, player.z, 0, 1, 0)
        
        # Draw Entities
        draw_sun()
        draw_clouds(game.clouds)
        draw_sea()
        
        for island in game.islands:
            draw_island_model(island)
            
        draw_boat_model(game.player)
        
        for enemy in game.enemies:
            draw_boat_model(enemy)
            
        for proj in game.projectiles:
            draw_projectile(proj)
            
        # Status Text
        status = f"HP: {player.hp}/{player.max_hp}"
        if player.state != "ALIVE": 
            status = "GAME OVER! TEKAN [R] UNTUK RESTART"
        
        enemy_count = len([e for e in game.enemies if e.state == "ALIVE"])
        enemy_stat = f"Lawan Hidup: {enemy_count}"
        
        pygame.display.set_caption(f"{TITLE} | {status} | {enemy_stat} | [KLIK+DRAG]=Cam [R]=Restart")
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()
