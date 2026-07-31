import pygame

import settings
from ai import payoff
from ui.sprites import PALETTE


def draw_wrapped(surface, font, text, color, x, y, width, line_height):
    words = text.split()
    line = ""
    for word in words:
        trial = f"{line} {word}".strip()
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


class TheoryPanel:
    WIDTH = 390

    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font

    def draw(self, surface, sim):
        player = sim.player_animal()
        if not player:
            return
        x = settings.SCREEN_WIDTH - self.WIDTH
        top = settings.HUD_HEIGHT
        height = settings.SCREEN_HEIGHT - settings.HUD_HEIGHT - settings.BOTTOM_BAR_HEIGHT
        panel = pygame.Surface((self.WIDTH, height), pygame.SRCALPHA)
        panel.fill((12, 20, 23, 244))
        surface.blit(panel, (x, top))
        pygame.draw.line(surface, PALETTE["gold"], (x, top), (x, top + height), 2)

        px, y = x + 18, top + 15
        surface.blit(self.font.render("LIVE GAME THEORY", False, PALETTE["gold"]), (px, y))
        y += 28
        surface.blit(
            self.small_font.render(f"{player.species.upper()}  |  {player.strategy.upper()}", False, PALETTE["text"]),
            (px, y),
        )
        y += 25

        profile = sim.profile_for(player)
        group_bonus = sim._group_bonus(player)
        threat, threat_distance = sim.nearest_threat(player)
        prey, prey_distance = sim.nearest_prey(player)
        lines = [
            f"Danger rank: {profile.danger:g}",
            f"Attack / defense: {profile.attack:g} / {profile.defense:g}",
            f"Group advantage: +{group_bonus:.1f}",
            f"Nearest threat: {threat.species if threat else 'none'}"
            + (f" ({threat_distance} tiles)" if threat else ""),
            f"Nearest opportunity: {prey.species if prey else 'none'}"
            + (f" ({prey_distance} tiles)" if prey else ""),
        ]
        for line in lines:
            surface.blit(self.small_font.render(line, False, PALETTE["muted"]), (px, y))
            y += 18

        y += 8
        surface.blit(self.font.render("PAYOFF CALCULATION", False, PALETTE["text"]), (px, y))
        y += 25
        breakdown = payoff.payoff_breakdown(player)
        for label, value in breakdown.items():
            color = PALETTE["danger"] if value < 0 else PALETTE["muted"]
            surface.blit(self.small_font.render(f"{label:<18} {value:>7.1f}", False, color), (px, y))
            y += 17
        total = sum(breakdown.values())
        pygame.draw.line(surface, PALETTE["line"], (px, y + 2), (x + self.WIDTH - 20, y + 2), 1)
        y += 8
        surface.blit(self.font.render(f"CURRENT PAYOFF  {total:.1f}", False, PALETTE["gold"]), (px, y))
        y += 31

        surface.blit(self.font.render("DECISION LOGIC", False, PALETTE["text"]), (px, y))
        y += 24
        logic = player.last_decision_reason or "Direct player control: your action replaces the AI best response."
        y = draw_wrapped(surface, self.small_font, logic, PALETTE["muted"], px, y, self.WIDTH - 36, 17)
        y += 6
        recommendation = self._recommendation(sim, player, threat, prey)
        surface.blit(self.small_font.render("RECOMMENDATION", False, PALETTE["gold"]), (px, y))
        y += 20
        y = draw_wrapped(surface, self.small_font, recommendation, PALETTE["text"], px, y, self.WIDTH - 36, 18)

        y += 8
        surface.blit(self.small_font.render("EQUILIBRIUM SIGNAL", False, PALETTE["gold"]), (px, y))
        y += 20
        y = draw_wrapped(surface, self.small_font, sim.ess_candidate, PALETTE["muted"], px, y, self.WIDTH - 36, 18)
        if player.species == "Wolf":
            move = settings.WOLF_STRATEGIES[player.strategy]["compete"]
            y += 5
            surface.blit(self.small_font.render(f"Hawk-Dove move: {move}", False, PALETTE["text"]), (px, y))

    def _recommendation(self, sim, player, threat, prey):
        energy_ratio = player.energy / player.max_energy
        own_danger = sim.profile_for(player).danger
        if threat and sim.profile_for(threat).danger > own_danger:
            return f"Avoid {threat.species.lower()}. Its danger rank is higher; attacking invites a damaging counter."
        if player.species == "Rabbit":
            if energy_ratio < 0.48:
                return "Seek nearby grass, but keep a shelter tile between you and the nearest predator."
            return "Preserve energy and stay near brush. Flee when a predator enters half your vision range."
        if energy_ratio < 0.38:
            return "Rest before hunting. Low energy reduces the value of a chase and raises starvation risk."
        if prey:
            prey_danger = sim.profile_for(prey).danger
            if prey_danger > own_danger * 0.75 and sim._group_bonus(player) < 2:
                return f"Wait for allies before attacking {prey.species.lower()}; expected retaliation is too costly."
            return f"{prey.species} is the current best opportunity. Close to one tile before attacking."
        return "Patrol preferred habitat and conserve energy until a favorable target enters vision."
