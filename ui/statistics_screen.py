import pygame

import settings
from ai import payoff
from ui.sprites import PALETTE


class StatisticsScreen:
    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font

    def draw(self, surface, sim):
        surface.fill(PALETTE["ui_bg"])
        surface.blit(self.font.render("THE LIVING WORLD", False, PALETTE["gold"]), (26, 20))
        surface.blit(self.small_font.render("Tab, Escape, or S returns to your animal", False, PALETTE["muted"]), (26, 50))
        self._line_graph(surface, sim.history, "rabbits", (70, 92, 530, 170), (222, 214, 190), "Rabbits")
        self._line_graph(surface, sim.history, "wolves", (70, 300, 530, 170), (145, 154, 164), "Wolves")
        self._line_graph(surface, sim.history, "grass", (670, 92, 530, 170), PALETTE["grass"], "Grass tiles")
        self._line_graph(surface, sim.history, "successful_hunts", (670, 300, 530, 170), PALETTE["danger"], "Successful hunts")
        payoffs = payoff.average_payoffs(sim.animals, sim.dead_records)
        y = 510
        surface.blit(self.font.render("Strategy payoff and ESS analysis", False, PALETTE["text"]), (70, y))
        y += 30
        for key, value in sorted(payoffs.items())[:12]:
            surface.blit(self.small_font.render(f"{key}: {value:.1f}", False, PALETTE["text"]), (80, y))
            y += 18
        surface.blit(self.font.render(sim.ess_candidate, False, PALETTE["gold"]), (670, 520))
        stats = sim.current_stats()
        lines = [
            f"Rabbit births/deaths: {stats['rabbit_births']} / {stats['rabbit_deaths']}",
            f"Wolf births/deaths: {stats['wolf_births']} / {stats['wolf_deaths']}",
            f"Failed hunts: {stats['failed_hunts']}",
            f"Predation deaths: {stats['predation_deaths']}",
            f"Starvation deaths: {stats['starvation_deaths']}",
        ]
        yy = 560
        for line in lines:
            surface.blit(self.small_font.render(line, False, PALETTE["muted"]), (670, yy))
            yy += 20

    def _line_graph(self, surface, history, key, rect, color, title):
        pygame.draw.rect(surface, PALETTE["panel"], rect)
        pygame.draw.rect(surface, PALETTE["line"], rect, 2)
        x, y, w, h = rect
        surface.blit(self.small_font.render(title, False, PALETTE["text"]), (x + 10, y + 8))
        if len(history) < 2:
            return
        values = [row[key] for row in history[-80:]]
        high = max(values) or 1
        low = min(values)
        span = max(1, high - low)
        points = []
        for i, value in enumerate(values):
            px = x + 12 + i * (w - 24) / max(1, len(values) - 1)
            py = y + h - 16 - ((value - low) / span) * (h - 44)
            points.append((px, py))
        if len(points) >= 2:
            pygame.draw.lines(surface, color, False, points, 3)
        surface.blit(self.small_font.render(f"{values[-1]}", False, color), (x + w - 54, y + 8))
