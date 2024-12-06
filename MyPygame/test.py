import pygame
import random

# Initialize Pygame
pygame.init()

# Load background music
pygame.mixer.music.load("background-music-224633.mp3")  # Replace with your music file path
pygame.mixer.music.set_volume(0.5)  # Set volume (0.0 to 1.0)
pygame.mixer.music.play(-1)  # Play the music indefinitely

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 5  # Bullet speed for enemy
MAX_HEALTH = 5
LEVEL_THRESHOLDS = [200, 400]  # Score thresholds for levels 2 and 3

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Initialize level and score
level = 1
score = 0

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sky Barrage")

# Load images and sounds
player_image = pygame.image.load("test.png")
player_image = pygame.transform.scale(player_image, (50, 50))
player_bullet_image = pygame.image.load("real_bullet.png")
player_bullet_image = pygame.transform.scale(player_bullet_image, (10, 20))
background_image = pygame.image.load("dessert.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
enemy_image = pygame.image.load("enemy3-1.png")
enemy_image = pygame.transform.scale(enemy_image, (50, 50))

# Load enemy bullet image
enemy_bullet_image = pygame.image.load("enemy_bullet.png")
enemy_bullet_image = pygame.transform.scale(enemy_bullet_image, (30, 20))

# Load power-up images
health_pack_image = pygame.image.load("health_pack.png")
health_pack_image = pygame.transform.scale(health_pack_image, (30, 30))
bullet_trajectory_image = pygame.image.load("bullet_powerup.png")
bullet_trajectory_image = pygame.transform.scale(bullet_trajectory_image, (30, 30))

shoot_sound = pygame.mixer.Sound("small-explosion-103779.wav")
hit_sound = pygame.mixer.Sound("bullet-hit-metal-84818.wav")
damage_sound = pygame.mixer.Sound("grenade-explosion-14-190266.wav")
game_over_sound = pygame.mixer.Sound("big-explosion-41783.wav")

# Initialize font
font = pygame.font.Font(None, 36)

# Game state variables
running = True
game_over = False
game_frozen = False

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.health = MAX_HEALTH
        self.blink_time = 0  # Track the blink time
        self.is_blinking = False  # Track whether the player is blinking
        self.blink_interval = 250  # Interval for blinking (in ms)
        self.blink_duration = 2500  # Duration of blinking (in ms)
        self.has_trajectory_powerup = False  # Track if the player has the bullet trajectory power-up

    def update(self):
        if not game_over:
            # Handle blinking effect
            if self.is_blinking:
                current_time = pygame.time.get_ticks()
                if current_time - self.blink_time < self.blink_duration:
                    if (current_time // self.blink_interval) % 2 == 0:
                        self.image = player_image  # Make the player visible
                    else:
                        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)  # Transparent surface (invisible)
                else:
                    self.is_blinking = False
                    self.image = player_image  # Reset the image after blinking

            # Handle player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.rect.left > 0:
                self.rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
                self.rect.x += PLAYER_SPEED

    def reduce_health(self):
        self.health -= 1
        damage_sound.play()
        if self.health <= 0:
            self.kill()
            game_over_sound.play()
            game_over_screen()

    def start_blinking(self):
        self.is_blinking = True
        self.blink_time = pygame.time.get_ticks()  # Set the time when the blink started

    def collect_health_pack(self):
        if self.health < MAX_HEALTH:
            self.health += 1

    def collect_bullet_trajectory(self):
        self.has_trajectory_powerup = True

# Bullet class for player with trajectory power-up (shooting two bullets)
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_bullet_image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        if not game_over:
            self.rect.y -= BULLET_SPEED
            if self.rect.bottom < 0:
                self.kill()

# Bullet class for enemy
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_bullet_image  # Use the enemy bullet image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        if not game_over:
            self.rect.y += ENEMY_BULLET_SPEED
            if self.rect.top > HEIGHT:
                self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), 0))
        self.player = player

    def update(self):
        if not game_over:
            self.rect.y += ENEMY_SPEED
            if self.rect.top > HEIGHT:
                self.rect.x = random.randint(0, WIDTH)
                self.rect.y = 0

# Health Pack class (power-up)
class HealthPack(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = health_pack_image
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -30))

    def update(self):
        if not game_over:
            self.rect.y += 3
            if self.rect.top > HEIGHT:
                self.kill()

# Bullet Trajectory Power-up class
class BulletTrajectoryPowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bullet_trajectory_image
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -30))

    def update(self):
        if not game_over:
            self.rect.y += 3
            if self.rect.top > HEIGHT:
                self.kill()

# Reset game function
def reset_game():
    global player, enemies, bullets, enemy_bullets, all_sprites, health_packs, bullet_trajectory_powerups, score, game_frozen, level
    player = Player()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()  # Track enemy bullets
    health_packs = pygame.sprite.Group()
    bullet_trajectory_powerups = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    for _ in range(4):
        enemy = Enemy(player)
        enemies.add(enemy)
        all_sprites.add(enemy)
    score = 0
    game_frozen = False
    level = 1  # Reset level to 1
    adjust_difficulty()

# Game Over Screen function
def game_over_screen():
    global game_over
    game_over = True
    global game_frozen
    game_frozen = True  # Freeze the game state

# Adjust difficulty to include enemy bullet speed
def adjust_difficulty():
    global ENEMY_SPEED, ENEMY_BULLET_SPEED, ENEMY_FIRE_RATE
    if level == 1:
        ENEMY_SPEED = 2
        ENEMY_BULLET_SPEED = 5
        ENEMY_FIRE_RATE = 1500  # Fire every 1.5 seconds
    elif level == 2:
        ENEMY_SPEED = 3
        ENEMY_BULLET_SPEED = 7
        ENEMY_FIRE_RATE = 1000  # Fire every 1 second
    elif level == 3:
        ENEMY_SPEED = 4
        ENEMY_BULLET_SPEED = 9
        ENEMY_FIRE_RATE = 800  # Fire every 0.8 seconds

# Game setup
reset_game()
clock = pygame.time.Clock()
last_enemy_fire_time = 0  # Time tracking for enemy firing

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over and not game_frozen:
                # When the player has the power-up, shoot two bullets
                if player.has_trajectory_powerup:
                    bullet1 = Bullet(player.rect.centerx - 15, player.rect.top)  # Left bullet
                    bullet2 = Bullet(player.rect.centerx + 15, player.rect.top)  # Right bullet
                    bullets.add(bullet1, bullet2)
                    all_sprites.add(bullet1, bullet2)
                else:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    bullets.add(bullet)
                    all_sprites.add(bullet)
                shoot_sound.play()
            if event.key == pygame.K_r and game_over:
                reset_game()
                game_over = False
                game_frozen = False

    if not game_frozen:
        # Update sprites
        all_sprites.update()

        # Enemy shooting logic
        current_time = pygame.time.get_ticks()
        if current_time - last_enemy_fire_time > ENEMY_FIRE_RATE:
            last_enemy_fire_time = current_time
            for enemy in enemies:
                enemy_bullet = EnemyBullet(enemy.rect.centerx, enemy.rect.bottom)
                enemy_bullets.add(enemy_bullet)
                all_sprites.add(enemy_bullet)

        # Check collisions between player and enemy bullets
        for bullet in enemy_bullets:
            if pygame.sprite.collide_rect(bullet, player):
                bullet.kill()
                player.reduce_health()
                player.start_blinking()  # Start blinking when hit

        # Check collisions between bullets and enemies
        for bullet in bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, True)
            for enemy in hit_enemies:
                bullet.kill()
                score += 10
                hit_sound.play()
                new_enemy = Enemy(player)
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)

        # Check for level progression
        if score >= LEVEL_THRESHOLDS[0] and level == 1:
            level = 2
            adjust_difficulty()
        elif score >= LEVEL_THRESHOLDS[1] and level == 2:
            level = 3
            adjust_difficulty()

        # Randomly spawn health packs and bullet trajectory power-ups
        if random.randint(0, 100) < 2:
            health_pack = HealthPack()
            health_packs.add(health_pack)
            all_sprites.add(health_pack)
        
        if random.randint(0, 100) < 2:
            bullet_trajectory_powerup = BulletTrajectoryPowerUp()
            bullet_trajectory_powerups.add(bullet_trajectory_powerup)
            all_sprites.add(bullet_trajectory_powerup)

        # Check collisions between health packs and the player
        for health_pack in health_packs:
            if pygame.sprite.collide_rect(health_pack, player):
                health_pack.kill()
                player.collect_health_pack()

        # Check collisions between bullet trajectory power-ups and the player
        for powerup in bullet_trajectory_powerups:
            if pygame.sprite.collide_rect(powerup, player):
                powerup.kill()
                player.collect_bullet_trajectory()

    # Draw everything
    screen.blit(background_image, (0, 0))
    all_sprites.draw(screen)

    # Draw health bar
    pygame.draw.rect(screen, RED, (10, 10, 100, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, (player.health / MAX_HEALTH) * 100, 20))

    # Draw score and level
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 40))
    screen.blit(level_text, (10, 70))

    if game_over:
        game_over_text = font.render("GAME OVER! Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 200, HEIGHT // 2 - 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
