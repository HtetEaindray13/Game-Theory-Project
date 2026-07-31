import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

import settings
from audio import MusicManager, SoundManager
from camera import Camera
from simulation import Simulation
from ui.field_guide import FieldGuide
from ui.hud import HUD
from ui.menu import GameOverScreen, SelectionScreen
from ui.sprites import PALETTE, make_sprites
from ui.statistics_screen import StatisticsScreen
from ui.theory_panel import TheoryPanel


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("Wild Balance")
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("lucidaconsole", 54, bold=True)
        self.heading_font = pygame.font.SysFont("lucidaconsole", 23, bold=True)
        self.font = pygame.font.SysFont("lucidaconsole", 17, bold=True)
        self.small_font = pygame.font.SysFont("lucidaconsole", 14)
        self.sim = Simulation()
        self.audio = SoundManager()
        self.music = MusicManager()
        self.camera = Camera()
        self.sprites = make_sprites()
        self.hud = HUD(self.font, self.small_font)
        self.selection = SelectionScreen(self.title_font, self.heading_font, self.small_font)
        self.game_over = GameOverScreen(self.title_font, self.heading_font, self.font)
        self.stats_screen = StatisticsScreen(self.font, self.small_font)
        self.field_guide = FieldGuide(self.heading_font, self.font, self.small_font)
        self.theory_panel = TheoryPanel(self.font, self.small_font)
        self.state = "menu"
        self.accumulator = 0.0
        self.facing = {}
        self.paused = False
        self.hovered_choice = None
        self.show_theory = False

    def run(self) -> None:
        running = True
        while running:
            dt = min(0.1, self.clock.tick(settings.FPS) / 1000)
            running = self.handle_events()
            if self.state == "game" and not self.paused:
                self.accumulator += dt
                step_time = 1 / settings.SIM_STEPS_PER_SECOND
                while self.accumulator >= step_time:
                    self.advance_simulation(self.current_command())
                    self.accumulator -= step_time
            self.draw()
        self.sim.record_history()
        self.sim.save_csv()
        pygame.quit()

    def start_game(self, species: str) -> None:
        self.sim.reset("balanced")
        player = self.sim.start_player(species)
        self.facing = {animal.id: "down" for animal in self.sim.animals}
        self.accumulator = 0.0
        self.paused = False
        self.show_theory = False
        self.state = "game"
        self.camera = Camera()
        self.camera.follow(player)
        self.audio.play("select")
        self.audio.play_animal_call(species)

    def advance_simulation(self, command: str | None) -> None:
        previous = {animal.id: animal.pos for animal in self.sim.animals}
        self.sim.step(command)
        player = self.sim.player_animal()
        self.audio.play_events(self.sim.events, player)
        for animal in self.sim.animals:
            old = previous.get(animal.id)
            if old and old != animal.pos:
                dx, dy = animal.x - old[0], animal.y - old[1]
                if abs(dx) > abs(dy):
                    self.facing[animal.id] = "right" if dx > 0 else "left"
                else:
                    self.facing[animal.id] = "down" if dy > 0 else "up"
        self.camera.follow(self.sim.player_animal())
        if self.sim.tick % 28 == 0 and player:
            nearby = self.sim.nearby_animals(player, None, 7)
            if nearby:
                self.audio.play_animal_call(nearby[0][0].species)
        if self.sim.player_id is not None and self.sim.player_animal() is None:
            self.state = "game_over"

    def current_command(self) -> str | None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            return "interact"
        if keys[pygame.K_SPACE]:
            return "rest"
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            return "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            return "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            return "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            return "right"
        return None

    def handle_events(self) -> bool:
        self.hovered_choice = self.selection.choice_at(pygame.mouse.get_pos()) if self.state == "menu" else None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if not self.handle_key(event.key):
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
        return True

    def handle_key(self, key) -> bool:
        if self.state == "menu":
            if key == pygame.K_ESCAPE:
                return False
            if key == pygame.K_r:
                self.start_game("Rabbit")
            elif key == pygame.K_w:
                self.start_game("Wolf")
            elif key == pygame.K_l:
                self.start_game("Lion")
            return True
        if self.state == "game_over":
            if key == pygame.K_RETURN:
                self.start_game(self.sim.player_species or "Rabbit")
            elif key in (pygame.K_m, pygame.K_ESCAPE):
                self.state = "menu"
            return True
        if self.state in {"stats", "guide"}:
            if key in (pygame.K_TAB, pygame.K_ESCAPE, pygame.K_s, pygame.K_h):
                self.state = "game"
            return True
        if key == pygame.K_ESCAPE:
            if self.show_theory:
                self.show_theory = False
            else:
                self.paused = not self.paused
        elif key in (pygame.K_TAB, pygame.K_s):
            self.state = "stats"
        elif key == pygame.K_h:
            self.state = "guide"
        elif key == pygame.K_t:
            self.show_theory = not self.show_theory
        elif key == pygame.K_v:
            self.audio.toggle()
        elif key == pygame.K_b:
            self.music.toggle()
        elif key == pygame.K_m:
            self.state = "menu"
        elif key == pygame.K_p:
            self.paused = not self.paused
        elif key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
        return True

    def handle_click(self, pos) -> None:
        if self.state == "menu":
            choice = self.selection.choice_at(pos)
            if choice:
                self.start_game(choice)
            return
        if self.state != "game":
            return
        action = self.hud.button_at(pos)
        if action:
            self.audio.play("select")
        if action == "menu":
            self.state = "menu"
        elif action == "music":
            self.music.toggle()
        elif action == "theory":
            self.show_theory = not self.show_theory
        elif action == "pause":
            self.paused = not self.paused
        elif action == "stats":
            self.state = "stats"

    def draw(self) -> None:
        if self.state == "menu":
            self.selection.draw(self.screen, self.hovered_choice)
        elif self.state == "stats":
            self.stats_screen.draw(self.screen, self.sim)
        elif self.state == "guide":
            self.field_guide.draw(self.screen)
        else:
            self.draw_world()
            self.draw_atmosphere()
            self.hud.draw(
                self.screen,
                self.sim,
                sound_on=not self.audio.muted,
                music_on=self.music.playing,
            )
            self.draw_minimap()
            if self.show_theory:
                self.theory_panel.draw(self.screen, self.sim)
            if self.paused:
                self.draw_pause()
            if self.state == "game_over":
                self.game_over.draw(self.screen, self.sim)
        pygame.display.flip()

    def visible_bounds(self):
        left = max(0, int(-self.camera.x // settings.TILE_SIZE) - 2)
        right = min(settings.GRID_COLS, left + settings.SCREEN_WIDTH // settings.TILE_SIZE + 5)
        top = max(0, int(-self.camera.y // settings.TILE_SIZE) - 3)
        height = (settings.SCREEN_HEIGHT - settings.HUD_HEIGHT - settings.BOTTOM_BAR_HEIGHT) // settings.TILE_SIZE
        bottom = min(settings.GRID_ROWS, top + height + 7)
        return left, right, top, bottom

    def draw_world(self) -> None:
        self.screen.fill((23, 74, 46))
        map_rect = pygame.Rect(
            0,
            settings.HUD_HEIGHT,
            settings.SCREEN_WIDTH,
            settings.SCREEN_HEIGHT - settings.HUD_HEIGHT - settings.BOTTOM_BAR_HEIGHT,
        )
        old_clip = self.screen.get_clip()
        self.screen.set_clip(map_rect)
        left, right, top, bottom = self.visible_bounds()
        decorations = []
        for y in range(top, bottom):
            for x in range(left, right):
                sx, sy = self.camera.world_to_screen(x, y)
                terrain = self.sim.world.terrain[y][x]
                variant = (x * 17 + y * 31 + self.sim.config.seed) % 4
                if terrain == settings.TERRAIN_WATER:
                    self.screen.blit(self.sprites[f"water_{variant}"], (sx, sy))
                elif terrain in {
                    settings.TERRAIN_SAVANNA,
                    settings.TERRAIN_SAND,
                    settings.TERRAIN_MUD,
                    settings.TERRAIN_REEDS,
                }:
                    self.screen.blit(self.sprites[f"{terrain}_{variant}"], (sx, sy))
                else:
                    grassy = self.sim.world.grass_amount(x, y) >= 1
                    key = f"grass_{variant}" if grassy else f"ground_{variant}"
                    self.screen.blit(self.sprites[key], (sx, sy))
                    flower_roll = (x * 47 + y * 89 + self.sim.config.seed) % 97
                    if terrain == settings.TERRAIN_GROUND and flower_roll < 5:
                        self.screen.blit(self.sprites[f"flowers_{flower_roll % 2}"], (sx, sy))
                if terrain in {settings.TERRAIN_FOREST, settings.TERRAIN_BUSH, settings.TERRAIN_ROCK}:
                    decorations.append((y * 10 + 5, terrain, x, y, sx, sy))
                scenery_roll = (x * 71 + y * 43 + self.sim.config.seed) % 101
                if terrain == settings.TERRAIN_SAVANNA and scenery_roll < 7:
                    decorations.append((y * 10 + 5, "acacia", x, y, sx, sy))
                elif terrain == settings.TERRAIN_SAND and scenery_roll < 18:
                    decorations.append((y * 10 + 5, "dry_shrub", x, y, sx, sy))

        player = self.sim.player_animal()
        for animal in self.sim.animals:
            if left - 1 <= animal.x <= right and top - 1 <= animal.y <= bottom:
                sx, sy = self.camera.world_to_screen(animal.x, animal.y)
                decorations.append((animal.y * 10 + 6, "animal", animal, sx, sy))
        for corpse in self.sim.death_animations:
            if left - 1 <= corpse["x"] <= right and top - 1 <= corpse["y"] <= bottom:
                sx, sy = self.camera.world_to_screen(corpse["x"], corpse["y"])
                decorations.append((corpse["y"] * 10 + 4, "corpse", corpse, sx, sy))

        for item in sorted(decorations, key=lambda value: value[0]):
            if item[1] == "animal":
                _, _, animal, sx, sy = item
                if animal is player:
                    pygame.draw.ellipse(self.screen, (246, 209, 91), (sx + 2, sy + 22, 28, 9), 2)
                species = animal.species.lower()
                direction = self.facing.get(animal.id, "down")
                frame_rate = 1 if animal.animation == "run" else 2
                frame = (self.sim.tick // frame_rate + animal.id) % 2
                sprite = self.sprites[f"{species}_{direction}_{frame}"]
                draw_x = sx + settings.TILE_SIZE // 2 - sprite.get_width() // 2
                draw_y = sy + settings.TILE_SIZE - sprite.get_height()
                if animal.animation == "attack":
                    lunge = {"left": (-5, 0), "right": (5, 0), "up": (0, -5), "down": (0, 5)}[direction]
                    draw_x += lunge[0]
                    draw_y += lunge[1]
                if animal.animation == "hurt" and animal.animation_ticks % 2:
                    sprite = sprite.copy()
                    sprite.fill((110, 20, 20, 0), special_flags=pygame.BLEND_RGB_ADD)
                if animal.animation == "run":
                    pygame.draw.circle(self.screen, (184, 166, 116), (sx + 8, sy + 28), 2)
                    pygame.draw.circle(self.screen, (184, 166, 116), (sx + 4, sy + 30), 1)
                self.screen.blit(
                    sprite,
                    (draw_x, draw_y),
                )
                if animal.animation == "run" or animal.current_action in {"Flee danger", "Escape"}:
                    alert = self.font.render("!", False, (244, 55, 48))
                    self.screen.blit(alert, alert.get_rect(center=(sx + 16, draw_y - 7)))
            elif item[1] == "corpse":
                _, _, corpse, sx, sy = item
                key = f"{corpse['species'].lower()}_down_0"
                sprite = pygame.transform.rotate(self.sprites[key], 90)
                sprite.set_alpha(max(35, int(220 * corpse["ticks"] / 8)))
                self.screen.blit(
                    sprite,
                    (sx + 16 - sprite.get_width() // 2, sy + 30 - sprite.get_height() // 2),
                )
            else:
                _, terrain, x, y, sx, sy = item
                if terrain == settings.TERRAIN_FOREST:
                    sprite = self.sprites[f"forest_{(x + y) % 2}"]
                    self.screen.blit(sprite, (sx - 8, sy - 28))
                elif terrain == "acacia":
                    sprite = self.sprites[f"acacia_{(x + y) % 2}"]
                    self.screen.blit(sprite, (sx - 10, sy - 22))
                elif terrain == "dry_shrub":
                    self.screen.blit(self.sprites["dry_shrub"], (sx, sy))
                elif terrain == settings.TERRAIN_BUSH:
                    self.screen.blit(self.sprites[f"bush_{(x + y) % 2}"], (sx - 2, sy))
                else:
                    self.screen.blit(self.sprites["rock"], (sx - 2, sy))
        if player and left - 1 <= player.x <= right and top - 1 <= player.y <= bottom:
            sx, sy = self.camera.world_to_screen(player.x, player.y)
            bob = 2 if (pygame.time.get_ticks() // 260) % 2 else 0
            marker_y = sy - 26 - bob
            label = self.small_font.render("YOU", False, (20, 24, 20))
            label_rect = label.get_rect(center=(sx + 16, marker_y - 7))
            backing = label_rect.inflate(10, 5)
            pygame.draw.rect(self.screen, PALETTE["gold"], backing)
            pygame.draw.rect(self.screen, (255, 244, 174), backing, 1)
            self.screen.blit(label, label_rect)
            pygame.draw.polygon(
                self.screen,
                PALETTE["gold"],
                [(sx + 10, marker_y + 3), (sx + 22, marker_y + 3), (sx + 16, marker_y + 11)],
            )
        self.screen.set_clip(old_clip)

    def draw_minimap(self) -> None:
        width, height = 158, 104
        x = settings.SCREEN_WIDTH - width - 16
        y = settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT - height - 14
        mini = pygame.Surface((width, height))
        mini.fill((12, 28, 28))
        scale_x = width / settings.GRID_COLS
        scale_y = height / settings.GRID_ROWS
        colors = {
            settings.TERRAIN_WATER: PALETTE["water"],
            settings.TERRAIN_FOREST: (19, 84, 42),
            settings.TERRAIN_ROCK: (91, 94, 91),
            settings.TERRAIN_BUSH: (42, 121, 53),
            settings.TERRAIN_GROUND: (91, 168, 68),
            settings.TERRAIN_SAVANNA: (181, 157, 73),
            settings.TERRAIN_SAND: (199, 176, 109),
            settings.TERRAIN_MUD: (105, 88, 60),
            settings.TERRAIN_REEDS: (64, 112, 51),
        }
        for row in range(settings.GRID_ROWS):
            for col in range(settings.GRID_COLS):
                tile = pygame.Rect(
                    int(col * scale_x),
                    int(row * scale_y),
                    max(1, int((col + 1) * scale_x) - int(col * scale_x)),
                    max(1, int((row + 1) * scale_y) - int(row * scale_y)),
                )
                pygame.draw.rect(mini, colors[self.sim.world.terrain[row][col]], tile)
        for animal in self.sim.animals:
            colors_by_species = {
                "Rabbit": (246, 242, 215),
                "Mouse": (176, 164, 157),
                "Wolf": (108, 119, 127),
                "Snake": (160, 174, 65),
                "Zebra": (230, 227, 208),
                "Crocodile": (53, 112, 55),
                "Buffalo": (71, 57, 46),
                "Lion": (225, 159, 55),
                "Elephant": (145, 151, 151),
            }
            color = colors_by_species[animal.species]
            pygame.draw.circle(mini, color, (int(animal.x * scale_x), int(animal.y * scale_y)), 1)
        player = self.sim.player_animal()
        if player:
            pygame.draw.circle(mini, PALETTE["gold"], (int(player.x * scale_x), int(player.y * scale_y)), 3)
        self.screen.blit(mini, (x, y))
        pygame.draw.rect(self.screen, (224, 220, 184), (x - 2, y - 2, width + 4, height + 4), 2)

    def draw_atmosphere(self) -> None:
        t = self.sim.time_of_day
        night = max(0.0, abs(t - 0.5) * 2 - 0.55) / 0.45
        if night <= 0:
            return
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((12, 28, 66, int(92 * min(1, night))))
        self.screen.blit(overlay, (0, 0))

    def draw_pause(self) -> None:
        shade = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((5, 10, 12, 145))
        self.screen.blit(shade, (0, 0))
        text = self.title_font.render("PAUSED", False, PALETTE["text"])
        self.screen.blit(text, text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 20)))
        hint = self.font.render("ESC OR P TO RETURN", False, PALETTE["muted"])
        self.screen.blit(hint, hint.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 38)))


if __name__ == "__main__":
    try:
        Game().run()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
