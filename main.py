import pygame
import sys
import random
import math

# Pygame Setup
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Modern Arcade Edition")

FPS = 60
CLOCK = pygame.time.Clock()

# Neon Palette
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
CYAN = (0, 255, 240)
MAGENTA = (255, 0, 128)
YELLOW = (255, 255, 0)
RED = (255, 50, 80)
GREEN = (50, 255, 120)
PURPLE = (180, 50, 255)

# Fonts
FONT = pygame.font.SysFont("trebuchetms", 24, bold=True)
BIG_FONT = pygame.font.SysFont("trebuchetms", 52, bold=True)
TITLE_FONT = pygame.font.SysFont("trebuchetms", 60, bold=True)

# Animated Stars
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 3.0)
        self.size = random.randint(1, 3)
        self.color = random.choice([WHITE, CYAN, PURPLE])

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# Particle Explosion Effect
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.lifetime = random.randint(15, 30)
        self.radius = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# Player Ship
class Player:
    def __init__(self):
        self.width = 46
        self.height = 40
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 70
        self.speed = 8
        self.lasers = []
        self.cooldown = 0

    def move(self, keys):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 10:
            self.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < WIDTH - self.width - 10:
            self.x += self.speed

    def shoot(self):
        if self.cooldown == 0:
            self.lasers.append(Laser(self.x + self.width // 2, self.y))
            self.cooldown = 10

    def update_lasers(self):
        if self.cooldown > 0:
            self.cooldown += 1
            if self.cooldown > 10:
                self.cooldown = 0

        for laser in self.lasers[:]:
            laser.update()
            if laser.y < -20:
                self.lasers.remove(laser)

    def draw(self, surface):
        for laser in self.lasers:
            laser.draw(surface)

        # Thruster Flame Glow
        flame_h = random.randint(8, 16)
        flame_pts = [
            (self.x + self.width // 2 - 6, self.y + self.height - 4),
            (self.x + self.width // 2 + 6, self.y + self.height - 4),
            (self.x + self.width // 2, self.y + self.height + flame_h)
        ]
        pygame.draw.polygon(surface, MAGENTA, flame_pts)

        # Neon Wings & Cockpit
        ship_pts = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + 12, self.y + self.height - 8),
            (self.x + self.width - 12, self.y + self.height - 8),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(surface, CYAN, ship_pts)
        pygame.draw.polygon(surface, WHITE, ship_pts, 2)
        pygame.draw.ellipse(surface, WHITE, (self.x + self.width // 2 - 5, self.y + 12, 10, 15))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Laser Bolt
class Laser:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 14

    def update(self):
        self.y -= self.speed

    def draw(self, surface):
        pygame.draw.line(surface, YELLOW, (self.x, self.y), (self.x, self.y + 16), 4)
        pygame.draw.line(surface, WHITE, (self.x, self.y + 2), (self.x, self.y + 12), 2)

    def get_rect(self):
        return pygame.Rect(self.x - 2, self.y, 4, 16)

# Neon Alien Invader
class Enemy:
    def __init__(self, level):
        self.width = 44
        self.height = 30
        self.x = random.randint(30, WIDTH - 70)
        self.y = random.randint(-180, -40)
        self.speed = random.uniform(1.8, 3.2) + (level * 0.2)
        self.color = random.choice([RED, MAGENTA, PURPLE])

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        # UFO Saucer Body
        pygame.draw.ellipse(surface, self.color, (self.x, self.y + 8, self.width, 18))
        # Glass Dome
        pygame.draw.ellipse(surface, CYAN, (self.x + 12, self.y, 20, 16))
        # Glowing Lights
        pygame.draw.circle(surface, YELLOW, (int(self.x + 8), int(self.y + 18)), 3)
        pygame.draw.circle(surface, GREEN, (int(self.x + self.width // 2), int(self.y + 20)), 3)
        pygame.draw.circle(surface, YELLOW, (int(self.x + self.width - 8), int(self.y + 18)), 3)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Main Game Code
def main():
    running = True
    state = "START"  # START, PLAY, GAMEOVER

    player = Player()
    stars = [Star() for _ in range(90)]
    enemies = []
    particles = []

    score = 0
    lives = 3
    level = 1

    def spawn_enemies():
        return [Enemy(level) for _ in range(5 + level * 2)]

    enemies = spawn_enemies()

    while running:
        CLOCK.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if state == "START" and event.key == pygame.K_SPACE:
                    state = "PLAY"
                elif state == "GAMEOVER" and event.key == pygame.K_r:
                    main()
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "START":
                    state = "PLAY"
                elif state == "GAMEOVER":
                    main()
                    return

        # Stars Update
        for star in stars:
            star.update()

        # Particles Update
        for particle in particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                particles.remove(particle)

        # STATE: PLAYING
        if state == "PLAY":
            keys = pygame.key.get_pressed()
            player.move(keys)
            if keys[pygame.K_SPACE]:
                player.shoot()

            player.update_lasers()

            # Wave Level Check
            if len(enemies) == 0:
                level += 1
                enemies = spawn_enemies()

            # Enemy Behavior
            for enemy in enemies[:]:
                enemy.update()

                # Hit by Laser
                for laser in player.lasers[:]:
                    if enemy.get_rect().colliderect(laser.get_rect()):
                        # Particle Blast
                        for _ in range(18):
                            particles.append(Particle(enemy.x + 22, enemy.y + 15, enemy.color))
                        
                        score += 15
                        player.lasers.remove(laser)
                        enemies.remove(enemy)
                        break

                # Reaches Bottom
                if enemy.y > HEIGHT:
                    lives -= 1
                    enemies.remove(enemy)

                # Collides with Player
                elif enemy.get_rect().colliderect(player.get_rect()):
                    lives -= 1
                    for _ in range(20):
                        particles.append(Particle(enemy.x + 22, enemy.y + 15, RED))
                    enemies.remove(enemy)

            if lives <= 0:
                state = "GAMEOVER"

        # RENDER DRAWING
        WIN.fill(BLACK)

        # Background Stars
        for star in stars:
            star.draw(WIN)

        # Particles
        for particle in particles:
            particle.draw(WIN)

        if state == "START":
            title_txt = TITLE_FONT.render("SPACE INVADERS", 1, CYAN)
            sub_txt = FONT.render("Press SPACEBAR or CLICK to Start", 1, YELLOW)
            WIN.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 220))
            WIN.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, 320))

        elif state == "PLAY":
            player.draw(WIN)
            for enemy in enemies:
                enemy.draw(WIN)

            # Modern HUD Bar
            pygame.draw.rect(WIN, (20, 20, 40), (0, 0, WIDTH, 50))
            pygame.draw.line(WIN, CYAN, (0, 50), (WIDTH, 50), 2)

            score_txt = FONT.render(f"SCORE: {score}", 1, WHITE)
            level_txt = FONT.render(f"WAVE: {level}", 1, YELLOW)
            lives_txt = FONT.render(f"LIVES: {'❤️' * lives}", 1, RED)

            WIN.blit(score_txt, (20, 12))
            WIN.blit(level_txt, (WIDTH // 2 - level_txt.get_width() // 2, 12))
            WIN.blit(lives_txt, (WIDTH - 150, 12))

        elif state == "GAMEOVER":
            over_txt = BIG_FONT.render("GAME OVER", 1, RED)
            score_txt = FONT.render(f"Final Score: {score}  |  Waves Cleared: {level - 1}", 1, WHITE)
            restart_txt = FONT.render("Press 'R' or CLICK to Play Again", 1, GREEN)

            WIN.blit(over_txt, (WIDTH // 2 - over_txt.get_width() // 2, 200))
            WIN.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 280))
            WIN.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, 350))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()