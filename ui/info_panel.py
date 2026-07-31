import pygame

import settings
from ui.sprites import PALETTE


def draw_wrapped(surface, font, text, color, x, y, width, line_height):
    words = text.split()
    line = ""
    for word in words:
        trial = (line + " " + word).strip()
        if font.size(trial)[0] <= width:
            line = trial
        else:
            surface.blit(font.render(line, False, color), (x, y))
            y += line_height
            line = word
    if line:
        surface.blit(font.render(line, False, color), (x, y))
        y += line_height
    return y


class InfoPanel:
    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font

    def draw(self, surface, sim):
        x = settings.SCREEN_WIDTH - settings.PANEL_WIDTH
        pygame.draw.rect(surface, PALETTE["panel"], (x, settings.HUD_HEIGHT, settings.PANEL_WIDTH, settings.SCREEN_HEIGHT - settings.HUD_HEIGHT - settings.BOTTOM_BAR_HEIGHT))
        pygame.draw.line(surface, PALETTE["line"], (x, settings.HUD_HEIGHT), (x, settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT), 2)
        animal = sim.selected_animal()
        px = x + 16
        y = settings.HUD_HEIGHT + 16
        if not animal:
            surface.blit(self.font.render("SELECTED ANIMAL", False, PALETTE["text"]), (px, y))
            y += 34
            y = draw_wrapped(surface, self.small_font, "Click a rabbit or wolf on the map to inspect its energy, action scores, and AI reasoning.", PALETTE["muted"], px, y, 260, 18)
            y += 12
            for line in ["Presets: press B, W, G, or Q", "Escape deselects or quits", "CSV saved to data folder"]:
                surface.blit(self.small_font.render(line, False, PALETTE["text"]), (px, y))
                y += 22
            return
        title = f"{animal.species.upper()} #{animal.id:03d}"
        surface.blit(self.font.render(title, False, PALETTE["gold"]), (px, y))
        y += 28
        fields = [
            f"Strategy: {animal.strategy}",
            f"Age: {animal.age}",
            f"Energy: {int(animal.energy)}/{int(animal.max_energy)}",
            f"Health: {int(animal.health)}/100",
            f"Current action: {animal.current_action}",
            f"Target: {animal.target if animal.target else 'None'}",
        ]
        for line in fields:
            surface.blit(self.small_font.render(line, False, PALETTE["text"]), (px, y))
            y += 20
        obs = sim.observe(animal)
        y += 8
        surface.blit(self.font.render("NEARBY", False, PALETTE["text"]), (px, y))
        y += 24
        if animal.species == "Rabbit":
            near = [
                f"Wolves: {len(sim.nearby_animals(animal, 'Wolf', animal.vision_range))}",
                f"Rabbits: {len(sim.nearby_animals(animal, 'Rabbit', animal.vision_range))}",
                f"Grass target: {obs['nearest_grass_distance'] if obs['nearest_grass_distance'] is not None else 'none'}",
            ]
        else:
            near = [
                f"Rabbits: {len(sim.nearby_animals(animal, 'Rabbit', animal.vision_range))}",
                f"Wolves: {len(sim.nearby_animals(animal, 'Wolf', animal.vision_range))}",
                f"Prey density: {obs['prey_density']:.2f}",
            ]
        for line in near:
            surface.blit(self.small_font.render(line, False, PALETTE["muted"]), (px, y))
            y += 18
        y += 8
        surface.blit(self.font.render("ACTION SCORES", False, PALETTE["text"]), (px, y))
        y += 24
        for action, score in list(animal.last_action_scores.items())[:7]:
            surface.blit(self.small_font.render(f"{action}: {score:5.1f}", False, PALETTE["text"]), (px, y))
            y += 18
        y += 8
        surface.blit(self.font.render("REASON", False, PALETTE["text"]), (px, y))
        y += 24
        draw_wrapped(surface, self.small_font, animal.last_decision_reason, PALETTE["muted"], px, y, 260, 18)
