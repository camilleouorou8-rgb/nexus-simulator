import pygame
import numpy as np
import random
import itertools
from collections import deque

# --- Configuration Initiale ⭐ ---
WIDTH, HEIGHT = 1200, 800
FPS = 60
STAR_COUNT = 60
TRAIL_LENGTH = 40

BLACK = (5, 5, 12)
WHITE = (255, 255, 255)

class Star:
    def __init__(self, x, y, mass, vel_x=0.0, vel_y=0.0):
        self.mass = mass
        self.pos = np.array([float(x), float(y)])
        self.vel = np.array([float(vel_x), float(vel_y)])
        self.acc = np.array([0.0, 0.0])
        self.trail = deque(maxlen=TRAIL_LENGTH)
        self.update_properties()

    def update_properties(self):
        self.radius = max(2, int(np.sqrt(self.mass) * 1.2))
        
        # Changement de couleur selon la masse ⭐
        if self.mass >= 800:
            self.color = (255, 50, 255) # Magenta (Instable, proche Supernova)
        elif self.mass >= 300:
            self.color = (100, 150, 255) # Bleu (Géante massive)
        elif self.mass >= 100:
            self.color = (255, 255, 255) # Blanc
        else:
            self.color = (255, random.randint(150, 220), 50) # Jaune/Orange

    def update(self):
        self.vel += self.acc
        self.pos += self.vel
        self.acc.fill(0)
        self.trail.append(tuple(self.pos.astype(int)))

    def draw(self, screen):
        if len(self.trail) > 1:
            pygame.draw.lines(screen, self.color, False, self.trail, 1)
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Nexus Simulator - Version Complète ⭐")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18, bold=True)

    # Variables de contrôle de l'univers ⭐
    G = 0.5  
    paused = False
    stars = []

    def spawn_galaxy(cx, cy):
        # Création d'un mini-système : 1 corps massif + petits corps en orbite ⭐
        stars.append(Star(cx, cy, mass=1000, vel_x=0, vel_y=0)) # Supermassif
        for _ in range(30):
            angle = random.uniform(0, 2 * np.pi)
            dist = random.uniform(80, 250)
            speed = np.sqrt(G * 1000 / dist) # Vitesse orbitale théorique v = sqrt(GM/r)
            
            x = cx + np.cos(angle) * dist
            y = cy + np.sin(angle) * dist
            vx = -np.sin(angle) * speed
            vy = np.cos(angle) * speed
            stars.append(Star(x, y, random.randint(5, 15), vx, vy))

    # Peuplement initial
    for _ in range(STAR_COUNT):
        stars.append(Star(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100), 
                          random.randint(10, 40), random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5)))

    running = True
    while running:
        screen.fill(BLACK)
        stars_to_remove = set()
        stars_to_add = []

        # --- Gestion des Événements et UI ⭐ ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if event.button == 1: # Clic Gauche : Étoile standard
                    stars.append(Star(mx, my, mass=random.randint(50, 150)))
                elif event.button == 3: # Clic Droit : Trou noir géant
                    stars.append(Star(mx, my, mass=500))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_UP:
                    G += 0.1 # Augmenter la gravité
                elif event.key == pygame.K_DOWN:
                    G -= 0.1 # Diminuer la gravité
                elif event.key == pygame.K_g:
                    mx, my = pygame.mouse.get_pos()
                    spawn_galaxy(mx, my) # Créer galaxie sous la souris

        if not paused:
            # --- Moteur Physique & Collisions ⭐ ---
            for s1, s2 in itertools.combinations(stars, 2):
                if s1 in stars_to_remove or s2 in stars_to_remove:
                    continue

                dist_vec = s2.pos - s1.pos
                distance = np.linalg.norm(dist_vec)

                # Collision
                if distance < (s1.radius + s2.radius) * 0.8:
                    new_mass = s1.mass + s2.mass
                    new_vel = (s1.vel * s1.mass + s2.vel * s2.mass) / new_mass
                    
                    if s1.mass >= s2.mass:
                        s1.mass, s1.vel = new_mass, new_vel
                        s1.update_properties()
                        stars_to_remove.add(s2)
                    else:
                        s2.mass, s2.vel = new_mass, new_vel
                        s2.update_properties()
                        stars_to_remove.add(s1)
                    continue

                # Gravité
                if distance > 2:
                    force_mag = G * (s1.mass * s2.mass) / (distance**2)
                    force_vec = (dist_vec / distance) * force_mag
                    s1.acc += force_vec / s1.mass
                    s2.acc -= force_vec / s2.mass 

            # --- Mécanique de Supernova ⭐ ---
            for s in stars:
                if s.mass > 1200 and s not in stars_to_remove:
                    stars_to_remove.add(s)
                    # Explosion : crée 12 débris qui partent dans toutes les directions
                    for i in range(12):
                        angle = (i / 12) * 2 * np.pi
                        speed = random.uniform(3, 7)
                        debris_vx = s.vel[0] + np.cos(angle) * speed
                        debris_vy = s.vel[1] + np.sin(angle) * speed
                        stars_to_add.append(Star(s.pos[0], s.pos[1], mass=random.randint(20, 50), 
                                                 vel_x=debris_vx, vel_y=debris_vy))

            # Mise à jour des listes
            if stars_to_remove:
                stars = [s for s in stars if s not in stars_to_remove]
            if stars_to_add:
                stars.extend(stars_to_add)

            for s in stars:
                s.update()

        # --- Affichage ⭐ ---
        for s in stars:
            s.draw(screen)

        # Affichage de l'interface (HUD) ⭐
        ui_texts = [
            f"Étoiles : {len(stars)}",
            f"Gravité (G) : {G:.1f} (Flèches Haut/Bas)",
            f"Statut : {'EN PAUSE' if paused else 'ACTIF'} (Espace)",
            "Clic G: Étoile | Clic D: Trou Noir | Touche G: Générer Galaxie"
        ]
        for i, text in enumerate(ui_texts):
            img = font.render(text, True, WHITE)
            screen.blit(img, (10, 10 + i * 25))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()