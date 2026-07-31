import pygame

import settings
from ui.sprites import PALETTE


class HUD:
    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        self.buttons = {
            "music": pygame.Rect(settings.SCREEN_WIDTH - 436, 17, 84, 30),
            "theory": pygame.Rect(settings.SCREEN_WIDTH - 344, 17, 84, 30),
            "menu": pygame.Rect(settings.SCREEN_WIDTH - 252, 17, 66, 30),
            "pause": pygame.Rect(settings.SCREEN_WIDTH - 178, 17, 70, 30),
            "stats": pygame.Rect(settings.SCREEN_WIDTH - 100, 17, 76, 30),
        }

    def draw(self, surface, sim, sound_on=True, music_on=True):
        player = sim.player_animal()
        top = pygame.Surface((settings.SCREEN_WIDTH, settings.HUD_HEIGHT), pygame.SRCALPHA)
        top.fill((10, 18, 20, 235))
        surface.blit(top, (0, 0))
        pygame.draw.line(surface, (125, 150, 105), (0, settings.HUD_HEIGHT - 2), (settings.SCREEN_WIDTH, settings.HUD_HEIGHT - 2), 2)

        species = sim.player_species or "Observer"
        surface.blit(self.font.render(species.upper(), False, PALETTE["gold"]), (20, 10))
        surface.blit(self.small_font.render(f"DAY {sim.day}   SCORE {sim.player_score()}", False, PALETTE["text"]), (20, 36))
        if player:
            self._bar(surface, 170, 11, 235, 17, player.health / 100, PALETTE["health"], f"HEALTH {int(player.health)}")
            self._bar(surface, 170, 36, 235, 17, player.energy / player.max_energy, PALETTE["energy"], f"ENERGY {int(player.energy)}")

        stats = sim.current_stats()
        world_text = (
            f"R {stats['rabbits']}  W {stats['wolves']}  L {stats['lions']}  "
            f"CROC {stats['crocodiles']}  Z {stats['zebras']}  ELE {stats['elephants']}"
        )
        surface.blit(self.small_font.render(world_text, False, PALETTE["muted"]), (440, 14))
        status = player.status_summary() if player else "HEALTHY"
        status_color = PALETTE["danger"] if status != "HEALTHY" else PALETTE["text"]
        action = player.current_action.upper()[:24] if player else "WATCHING"
        surface.blit(
            self.small_font.render(f"{sim.ecosystem_status().upper()}  |  {status}  |  {action}", False, status_color),
            (440, 38),
        )
        for action, rect in self.buttons.items():
            pygame.draw.rect(surface, (37, 51, 51), rect)
            pygame.draw.rect(surface, PALETTE["line"], rect, 1)
            label = action.upper()
            if action == "music":
                label = "MUSIC ||" if music_on else "MUSIC >"
            surface.blit(self.small_font.render(label, False, PALETTE["text"]), self.small_font.render(label, False, PALETTE["text"]).get_rect(center=rect.center))

        y = settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT
        bottom = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA)
        bottom.fill((10, 18, 20, 230))
        surface.blit(bottom, (0, y))
        pygame.draw.line(surface, (125, 150, 105), (0, y), (settings.SCREEN_WIDTH, y), 2)
        objective, progress = sim.player_objective()
        current = int(sim.player_food) if sim.player_species == "Rabbit" else sim.player_hunts
        goal = 20 if sim.player_species == "Rabbit" else (4 if sim.player_species == "Lion" else 5)
        surface.blit(self.small_font.render(f"GOAL  {objective.upper()}  {current}/{goal}", False, PALETTE["text"]), (22, y + 12))
        self._bar(surface, 22, y + 36, 300, 13, progress, PALETTE["gold"], "")
        sound = "ON" if sound_on else "OFF"
        controls = f"MOVE WASD/ARROWS  E ACTION  SPACE REST/HEAL  T THEORY  B MUSIC  V SFX {sound}"
        surface.blit(self.small_font.render(controls, False, PALETTE["muted"]), (380, y + 26))

    def _bar(self, surface, x, y, width, height, value, color, label):
        pygame.draw.rect(surface, (12, 20, 21), (x, y, width, height))
        pygame.draw.rect(surface, color, (x + 2, y + 2, max(0, int((width - 4) * value)), height - 4))
        pygame.draw.rect(surface, (104, 123, 105), (x, y, width, height), 1)
        if label:
            surface.blit(self.small_font.render(label, False, PALETTE["text"]), (x + 7, y - 1))

    def button_at(self, pos):
        for action, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return action
        return None
