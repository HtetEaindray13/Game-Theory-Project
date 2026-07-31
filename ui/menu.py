from pathlib import Path

import pygame

import settings
from ui.sprites import PALETTE


class SelectionScreen:
    def __init__(self, title_font, heading_font, body_font):
        self.title_font = title_font
        self.heading_font = heading_font
        self.body_font = body_font
        source = pygame.image.load(str(Path(settings.TITLE_ART_PATH))).convert()
        self.background = pygame.transform.smoothscale(source, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.rabbit_rect = pygame.Rect(35, 460, 370, 184)
        self.wolf_rect = pygame.Rect(455, 460, 370, 184)
        self.lion_rect = pygame.Rect(875, 460, 370, 184)

    def draw(self, surface, hovered: str | None = None):
        surface.blit(self.background, (0, 0))
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((5, 14, 13, 36))
        pygame.draw.rect(shade, (5, 12, 16, 180), (0, 0, settings.SCREEN_WIDTH, 150))
        pygame.draw.rect(shade, (5, 12, 16, 130), (0, 400, settings.SCREEN_WIDTH, 320))
        surface.blit(shade, (0, 0))

        title = self.title_font.render("WILD BALANCE", False, (250, 239, 189))
        surface.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, 62)))
        subtitle = self.heading_font.render("CHOOSE YOUR LIFE IN THE ECOSYSTEM", False, (236, 244, 218))
        surface.blit(subtitle, subtitle.get_rect(center=(settings.SCREEN_WIDTH // 2, 118)))

        self._card(
            surface,
            self.rabbit_rect,
            "RABBIT",
            "Graze, hide, and escape every hunter.",
            "Swift  |  Fragile  |  E to graze",
            hovered == "Rabbit",
            (226, 235, 208),
        )
        self._card(
            surface,
            self.wolf_rect,
            "WOLF",
            "Hunt in a dangerous, competitive food web.",
            "Pack hunter  |  E to attack",
            hovered == "Wolf",
            (150, 164, 171),
        )
        self._card(
            surface,
            self.lion_rect,
            "LION",
            "Rule the savanna, but respect giants.",
            "Apex hunter  |  E to attack",
            hovered == "Lion",
            (225, 159, 55),
        )
        prompt = self.body_font.render("Click a path  |  R Rabbit  |  W Wolf  |  L Lion  |  Esc Quit", False, PALETTE["text"])
        surface.blit(prompt, prompt.get_rect(center=(settings.SCREEN_WIDTH // 2, 684)))

    def _card(self, surface, rect, title, description, traits, active, accent):
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((13, 23, 25, 225 if active else 205))
        surface.blit(panel, rect)
        pygame.draw.rect(surface, PALETTE["gold"] if active else accent, rect, 4 if active else 2)
        surface.blit(self.heading_font.render(title, False, accent), (rect.x + 24, rect.y + 20))
        surface.blit(self.body_font.render(description, False, PALETTE["text"]), (rect.x + 24, rect.y + 72))
        surface.blit(self.body_font.render(traits, False, PALETTE["muted"]), (rect.x + 24, rect.y + 110))
        label = self.body_font.render("BEGIN", False, (17, 30, 27))
        button = pygame.Rect(rect.x + 24, rect.bottom - 48, 116, 30)
        pygame.draw.rect(surface, accent, button)
        surface.blit(label, label.get_rect(center=button.center))

    def choice_at(self, pos) -> str | None:
        if self.rabbit_rect.collidepoint(pos):
            return "Rabbit"
        if self.wolf_rect.collidepoint(pos):
            return "Wolf"
        if self.lion_rect.collidepoint(pos):
            return "Lion"
        return None


class GameOverScreen:
    def __init__(self, title_font, heading_font, body_font):
        self.title_font = title_font
        self.heading_font = heading_font
        self.body_font = body_font

    def draw(self, surface, sim):
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((7, 12, 15, 215))
        surface.blit(overlay, (0, 0))
        title = self.title_font.render("THE WILD MOVES ON", False, PALETTE["gold"])
        surface.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, 215)))
        reason = sim.player_death_reason or "the ecosystem changed"
        message = self.heading_font.render(f"Your {sim.player_species.lower()} fell to {reason}.", False, PALETTE["text"])
        surface.blit(message, message.get_rect(center=(settings.SCREEN_WIDTH // 2, 310)))
        stats = self.body_font.render(
            f"Day {sim.day}   Score {sim.player_score()}   Steps {sim.player_steps}",
            False,
            PALETTE["muted"],
        )
        surface.blit(stats, stats.get_rect(center=(settings.SCREEN_WIDTH // 2, 362)))
        prompt = self.heading_font.render("ENTER  PLAY AGAIN     M  CHOOSE ANOTHER", False, PALETTE["text"])
        surface.blit(prompt, prompt.get_rect(center=(settings.SCREEN_WIDTH // 2, 475)))
