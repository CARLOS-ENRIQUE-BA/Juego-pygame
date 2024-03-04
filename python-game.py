import pygame
import random
import sys

# Inicializar Pygame
pygame.init()

# Definir constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 300  # Reducir la altura a la mitad
PLATFORM_WIDTH = 50
PLATFORM_HEIGHT = 20
PLAYER_SIZE = 30
ENEMY_SIZE = 30
COIN_SIZE = 20
PLATFORM_COLOR = (0, 255, 0)
PLAYER_COLOR = (255, 0, 0)
ENEMY_COLOR = (0, 0, 255)
COIN_COLOR = (255, 255, 0)
PROJECTILE_COLOR = (255, 0, 255) # Color del proyectil del enemigo
SHIELD_COLOR = (0, 255, 255) # Color del escudo del jugador
BACKGROUND_COLOR = (255, 255, 255)
FPS = 60
GRAVITY = 0.6
JUMP_HEIGHT = -15
PLAYER_SPEED = 5
SHIELD_DURATION = FPS  # Duración del escudo en segundos (FPS fotogramas por segundo)

# Definir clases
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed_x = 0
        self.speed_y = 0
        self.coins = 0
        self.shielded = False
        self.shield_timer = 0

    def update(self):
        self.speed_y += GRAVITY
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Mantener al jugador dentro de la pantalla
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Comprobar si el jugador está en el suelo
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.speed_y = 0

        # Actualizar el temporizador del escudo
        if self.shielded:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.toggle_shield()

    def jump(self):
        if self.rect.bottom == SCREEN_HEIGHT:
            self.speed_y = JUMP_HEIGHT

    def toggle_shield(self):
        self.shielded = not self.shielded
        if self.shielded:
            self.image.fill(SHIELD_COLOR)
            self.shield_timer = SHIELD_DURATION
        else:
            self.image.fill(PLAYER_COLOR)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(150, 300 - ENEMY_SIZE)  # Ajustar la altura
        self.speed = random.randint(3, 7)
        self.fire_rate = 60  # Frecuencia de disparo en frames
        self.fire_cooldown = 0

    def update(self):
        self.rect.x -= self.speed
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

    def fire_projectile(self):
        if self.fire_cooldown == 0:
            projectile = Projectile(self.rect.centerx, self.rect.centery)
            all_sprites.add(projectile)
            projectiles.add(projectile)
            self.fire_cooldown = self.fire_rate

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))  # Tamaño del proyectil
        self.image.fill(PROJECTILE_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10  # Velocidad del proyectil

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:  # Eliminar proyectil cuando sale de la pantalla
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((COIN_SIZE, COIN_SIZE))
        self.image.fill(COIN_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - COIN_SIZE)
        self.rect.y = 150  # Ajustar la altura

# Configurar la pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Juego de esquivar enemigos")

# Crear los sprites
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Loop principal del juego
clock = pygame.time.Clock()
running = True
enemy_spawn_timer = 0
coin_spawn_timer = 0

while running:
    clock.tick(FPS)
    
    # Procesar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            elif event.key == pygame.K_x:
                player.toggle_shield()

    # Movimiento del jugador
    keys = pygame.key.get_pressed()
    player.speed_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED

    # Actualizar los sprites
    all_sprites.update()

    # Crear nuevos enemigos
    if enemy_spawn_timer <= 0:
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        enemy_spawn_timer = random.randint(60, 120)  # Nuevos enemigos cada 1-2 segundos
    else:
        enemy_spawn_timer -= 1

    # Crear nuevas monedas
    if coin_spawn_timer <= 0:
        coin = Coin()
        all_sprites.add(coin)
        coins.add(coin)
        coin_spawn_timer = random.randint(120, 180)  # Nuevas monedas cada 2-3 segundos
    else:
        coin_spawn_timer -= 1

    # Disparar proyectiles desde los enemigos
    for enemy in enemies:
        enemy.fire_projectile()

    # Verificar colisiones entre proyectiles y el jugador
    hits = pygame.sprite.spritecollide(player, projectiles, True)
    if hits and not player.shielded:
        running = False

    # Verificar colisiones con los enemigos
    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits and not player.shielded:
        running = False

    # Verificar colisiones con las monedas
    coin_hits = pygame.sprite.spritecollide(player, coins, True)
    player.coins += len(coin_hits)

    # Dibujar la pantalla
    screen.fill(BACKGROUND_COLOR)
    all_sprites.draw(screen)

    # Mostrar el contador de monedas
    font = pygame.font.Font(None, 36)
    text = font.render(f"Monedas: {player.coins}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    # Actualizar la pantalla
    pygame.display.flip()

pygame.quit()
sys.exit()
