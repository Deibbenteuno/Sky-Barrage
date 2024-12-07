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
ENEMY_BULLET_SPEED = 3  # Bullet speed for enemy
MAX_HEALTH = 5
LEVEL_THRESHOLDS = [500, 1000]  # Score thresholds for levels 2 and 3

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
enemy_bullet_image = pygame.transform.scale(enemy_bullet_image, (50, 40))

# Load power-up images
health_pack_image = pygame.image.load("health_pack.png")
health_pack_image = pygame.transform.scale(health_pack_image, (30, 30))
bullet_trajectory_image = pygame.image.load("bullet_powerup.png")
bullet_trajectory_image = pygame.transform.scale(bullet_trajectory_image, (30, 30))
# Load shield images
shield_powerup_image = pygame.image.load("shield1.png")  # Image for shield power-up
shield_active_image = pygame.image.load("shield2.png")    # Image for active shield
shield_powerup_image = pygame.transform.scale(shield_powerup_image, (30, 30))  # Adjust size as needed
shield_active_image = pygame.transform.scale(shield_active_image, (70, 70))    # Adjust size as needed
main_menu_background_image = pygame.image.load("background.png")  # Replace with your main menu image path
main_menu_background_image = pygame.transform.scale(main_menu_background_image, (WIDTH, HEIGHT))

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
in_main_menu = True  # Track if in main menu
level_up_message = ""  # Message to display when leveling up
level_up_time = 0  # Time when the level-up message was set
level_up_duration = 2000  # Duration to show the message in milliseconds

# Background class for moving background
class Background:
    def __init__(self, image):
        self.image = image
        self.y1 = 0  # First position of the background
        self.y2 = -HEIGHT  # Second position of the background (off-screen)

    def update(self):
        # Move the background down
        self.y1 += 1  # Speed of the background movement
        self.y2 += 1  # Speed of the background movement

        # Reset the background position when it goes off-screen
        if self.y1 >= HEIGHT:
            self.y1 = -HEIGHT
        if self.y2 >= HEIGHT:
            self.y2 = -HEIGHT

    def draw(self, screen):
        # Draw the two images to create a seamless scrolling effect
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))

class MenuBackground:
    def __init__(self, image):
        self.image = image
        self.y1 = 0  # First position of the background
        self.y2 = -HEIGHT  # Second position of the background (off-screen)

    def update(self):
        # Move the background down
        self.y1 += 0.5  # Speed of the background movement
        self.y2 += 0.5  # Speed of the background movement

        # Reset the background position when it goes off-screen
        if self.y1 >= HEIGHT:
            self.y1 = -HEIGHT
        if self.y2 >= HEIGHT:
            self.y2 = -HEIGHT

    def draw(self, screen):
        # Draw the two images to create a seamless scrolling effect
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.health = MAX_HEALTH
        self.blink_time = 0  # Track the blink time
        self.is_blinking = False  # Track whether the player is blinking
        self.blink_interval = 150  # Interval for blinking (in ms)
        self.blink_duration = 1500  # Duration of blinking (in ms)
        self.has_trajectory_powerup = False  # Track if the player has the bullet trajectory power-up
        self.shield_active = False  # Track if the shield is active
        self.shield_start_time = 0  # Track when the shield was activated
        self.shield_duration = 10000  # Shield duration in milliseconds

    def update(self):
        if not game_over:
            # Handle shield effect
            if self.shield_active:
                current_time = pygame.time.get_ticks()
                if current_time - self.shield_start_time > self.shield_duration:
                    self.shield_active = False  # Deactivate shield after duration

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
        if not self.shield_active:  # Only reduce health if shield is not active
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

    def activate_shield(self):
        self.shield_active = True
        self.shield_start_time = pygame.time.get_ticks()  # Set the time when the shield was activated

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
        self.horizontal_speed = random.choice([-1, 1])  # Start moving left or right
        self.change_direction_chance = 0.02  # Chance to change direction

    def update(self):
        if not game_over:
            # Move downwards
            self.rect.y += ENEMY_SPEED
            
            # Randomly change horizontal direction
            if random.random() < self.change_direction_chance:
                self.horizontal_speed *= -1  # Reverse direction

            # Move horizontally
            self.rect.x += self.horizontal_speed

            # Keep the enemy within the screen bounds
            if self.rect.left < 0:
                self.rect.left = 0
                self.horizontal_speed *= -1  # Reverse direction
            elif self.rect.right > WIDTH:
                self.rect.right = WIDTH
                self.horizontal_speed *= -1  # Reverse direction

            # Reset position if it goes off the bottom of the screen
            if self.rect.top > HEIGHT:
                self.rect.x = random.randint(0, WIDTH)
                self.rect.y = 0

    def drop_power_up(self):
        if random.choice([True, False]):  # Randomly decide if a power-up drops
            power_up_type = random.choice(['health', 'bullet_trajectory', 'shield'])  # Choose a power-up type
            if power_up_type == 'health':
                power_up = HealthPack()
            elif power_up_type == 'bullet_trajectory':
                power_up = BulletTrajectoryPowerUp()
            else:
                power_up = ShieldPowerUp()
            power_up.rect.center = self.rect.center  # Position the power-up at the enemy's location
            return power_up
        return None

# Health Pack class (power-up)
class HealthPack(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = health_pack_image
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -30))

    def update(self):
        if not game_over:
            self.rect.y += 2  # Move down the screen
            if self.rect.top > HEIGHT:
                self.kill()  # Remove if it goes off-screen

# Bullet Trajectory Power-up class
class BulletTrajectoryPowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bullet_trajectory_image
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -30))

    def update(self):
        if not game_over:
            self.rect.y += 2
            if self.rect.top > HEIGHT:
                self.kill()

# Shield Power-up class
class ShieldPowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = shield_powerup_image  # Use the shield power-up image
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -30))

    def update(self):
        if not game_over:
            self.rect.y += 2
            if self.rect.top > HEIGHT:
                self.kill()

# Reset game function
def reset_game():
    global player, enemies, bullets, enemy_bullets, all_sprites, health_packs, bullet_trajectory_powerups, shield_powerups, score, game_frozen, level, level_up_message, level_up_time
    player = Player()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()  # Track enemy bullets
    health_packs = pygame.sprite.Group()
    bullet_trajectory_powerups = pygame.sprite.Group()
    shield_powerups = pygame.sprite.Group()  # Track shield power-ups
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    for _ in range(4):
        enemy = Enemy(player)
        enemies.add(enemy)
        all_sprites.add(enemy)
    score = 0
    game_frozen = False
    level = 1  # Reset level to 1
    level_up_message = ""  # Reset level up message
    level_up_time = 0  # Reset level up time
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
        ENEMY_BULLET_SPEED = 3
        ENEMY_FIRE_RATE = 1500  # Fire every 1.5 seconds
    elif level == 2:
        ENEMY_SPEED = 3
        ENEMY_BULLET_SPEED = 7
        ENEMY_FIRE_RATE = 1000  # Fire every 1 second
    elif level == 3:
        ENEMY_SPEED = 4
        ENEMY_BULLET_SPEED = 9
        ENEMY_FIRE_RATE = 800  # Fire every 0.8 seconds
    elif level >= 3:
        ENEMY_SPEED = 6
        ENEMY_BULLET_SPEED = 11
        ENEMY_FIRE_RATE = 1000

menu_background = MenuBackground(main_menu_background_image)

# Main Menu function
def main_menu():
    global in_main_menu
    
    # Load the logo image
    logo_image = pygame.image.load("logo-final.png")  # Load the image
    logo_rect = logo_image.get_rect(center=(WIDTH // 2, HEIGHT // 3))  # Center the image

    # Button text
    start_text = font.render("Press ENTER to Start", True, WHITE)
    quit_text = font.render("Press ESC to Quit", True, WHITE)

    # Button rectangles for collision detection
    start_button_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))  # Move down by 100 pixels
    quit_button_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))    # Move down by 150 pixels

    while in_main_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if start_button_rect.collidepoint(event.pos):
                        in_main_menu = False  # Exit the main menu
                    elif quit_button_rect.collidepoint(event.pos):
                        pygame.quit()
                        quit()
        
        # Update the background
        menu_background.update()

        # Render main menu
        menu_background.draw(screen)  # Draw the moving background
        
        # Draw the logo image instead of text
        screen.blit(logo_image, logo_rect)  # Blit the logo image
        
        # Draw buttons
        screen.blit(start_text, start_button_rect)  # Blit the start button text
        screen.blit(quit_text, quit_button_rect)    # Blit the quit button text
        
        # Highlight buttons on hover
        mouse_pos = pygame.mouse.get_pos()
        if start_button_rect.collidepoint(mouse_pos):
            start_text = font.render("Press ENTER to Start", True, (255, 255, 0))  # Change color on hover
        else:
            start_text = font.render("Press ENTER to Start", True, WHITE)

        if quit_button_rect.collidepoint(mouse_pos):
            quit_text = font.render("Press ESC to Quit", True, (255, 255, 0))  # Change color on hover
        else:
            quit_text = font.render("Press ESC to Quit", True, WHITE)

        pygame.display.update()

        # Check for keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            in_main_menu = False  # Exit the main menu
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            quit()
        
        # Update the background
        menu_background.update()

        # Render main menu
        menu_background.draw(screen)  # Draw the moving background
        
        # Draw the logo image instead of text
        screen.blit(logo_image, logo_rect)  # Blit the logo image
        
        # Draw buttons
        screen.blit(start_text, start_button_rect)  # Blit the start button text
        screen.blit(quit_text, quit_button_rect)    # Blit the quit button text
        
        # Highlight buttons on hover
        mouse_pos = pygame.mouse.get_pos()
        if start_button_rect.collidepoint(mouse_pos):
            start_text = font.render("Press ENTER to Start", True, (255, 255, 0))  # Change color on hover
        else:
            start_text = font.render("Press ENTER to Start", True, WHITE)

        if quit_button_rect.collidepoint(mouse_pos):
            quit_text = font.render("Press ESC to Quit", True, (255, 255, 0))  # Change color on hover
        else:
            quit_text = font.render("Press ESC to Quit", True, WHITE)

        pygame.display.update()

        # Check for keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            in_main_menu = False  # Exit the main menu
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            quit()

# Show main menu
main_menu()

# Create a Background instance
background = Background(background_image)

# Game loop (starts after main menu)
reset_game()  # Reset the game before starting
clock = pygame.time.Clock()
last_enemy_fire_time = 0  # Time tracking for enemy firing

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
        # Update the background
        background.update()

        all_sprites.update()
        health_packs.update()  # Update health packs
        bullet_trajectory_powerups.update()  # Update bullet trajectory power-ups
        shield_powerups.update()  # Update shield power-ups

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

        # Check for collisions between player and power-ups
        for power_up in health_packs:
            if pygame.sprite.collide_rect(power_up, player):
                player.collect_health_pack()  # Call the method to collect health
                power_up.kill()  # Remove the power-up from the game

        # Check for collisions between player and bullet trajectory power-ups
        for power_up in bullet_trajectory_powerups:
            if pygame.sprite.collide_rect(power_up, player):
                player.collect_bullet_trajectory()  # Call the method to collect bullet trajectory power-up
                power_up.kill()  # Remove the power-up from the game

        # Check for collisions between player and shield power-ups
        for power_up in shield_powerups:
            if pygame.sprite.collide_rect(power_up, player):
                player.activate_shield()  # Call the method to activate the shield
                power_up.kill()  # Remove the power-up from the game

        # Check collisions between bullets and enemies
        for bullet in bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                bullet.kill()
                score += 10
                hit_sound.play()
                power_up = enemy.drop_power_up()  # Check if the enemy drops a power-up
                if power_up:
                    all_sprites.add(power_up)  # Add the power-up to the sprite group
                    if isinstance(power_up, HealthPack):
                        health_packs.add(power_up)
                    elif isinstance(power_up, BulletTrajectoryPowerUp):
                        bullet_trajectory_powerups.add(power_up)
                    elif isinstance(power_up, ShieldPowerUp):
                        shield_powerups.add(power_up)
                enemy.kill()  # Remove the enemy after it is hit
                new_enemy = Enemy(player)
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)

        # Check for level progression
        if score >= LEVEL_THRESHOLDS[0] and level == 1:
            level = 2
            level_up_message = "Level 2!"
            level_up_time = pygame.time.get_ticks()  # Set the time when the message is displayed
            adjust_difficulty()
        elif score >= LEVEL_THRESHOLDS[1] and level == 2:
            level = 3
            level_up_message = "Level 3!"
            level_up_time = pygame.time.get_ticks()  # Set the time when the message is displayed
            adjust_difficulty()
        elif score >= LEVEL_THRESHOLDS[1] and level == 3:
            level_up_message = "Congratulations! You have reached the Endless Round"
            level_up_time = pygame.time.get_ticks()  # Set the time when the message is displayed
            adjust_difficulty()

        # Check if the level-up message should be cleared
        if level_up_message and pygame.time.get_ticks() - level_up_time > level_up_duration:
            level_up_message = ""  # Clear the message after 2 seconds

    # Draw everything
    background.draw(screen)  # Draw the moving background
    all_sprites.draw(screen)

    # Draw the player
    screen.blit(player.image, player.rect)

    # Draw the shield if active
    if player.shield_active:
        shield_x = player.rect.centerx - 35  # Move 10 pixels to the left
        shield_y = player.rect.centery - 40    # Move 10 pixels up
        screen.blit(shield_active_image, (shield_x, shield_y))  # Draw the shield at the adjusted position

    # Draw health bar
    pygame.draw.rect(screen, RED, (10, 10, 100, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, (player.health / MAX_HEALTH) * 100, 20))

    # Draw score and level
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 40))
    screen.blit(level_text, (10, 70))

    # Draw level up message if it exists
    if level_up_message:
        level_up_text = font.render(level_up_message, True, WHITE)
        screen.blit(level_up_text, (WIDTH // 2 - level_up_text.get_width() // 2, HEIGHT // 2))

    if game_over:
        game_over_text = font.render("GAME OVER! Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 200, HEIGHT // 2 - 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()