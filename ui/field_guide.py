import pygame

import settings
from ui.sprites import PALETTE


class FieldGuide:
    def __init__(self, heading_font, font, small_font):
        self.heading_font = heading_font
        self.font = font
        self.small_font = small_font

    def draw(self, surface):
        surface.fill(PALETTE["ui_bg"])
        surface.blit(self.heading_font.render("FOOD WEB AND DANGER HIERARCHY", False, PALETTE["gold"]), (34, 25))
        surface.blit(self.small_font.render("H, Escape, or Tab returns to the wild", False, PALETTE["muted"]), (36, 61))
        pygame.draw.line(surface, PALETTE["line"], (34, 86), (1246, 86), 2)

        species = sorted(settings.SPECIES_PROFILES, key=lambda name: settings.SPECIES_PROFILES[name].danger, reverse=True)
        y = 105
        for rank, name in enumerate(species, 1):
            profile = settings.SPECIES_PROFILES[name]
            rect = pygame.Rect(36, y, 565, 52)
            color = (49, 61, 58) if rank % 2 else (38, 50, 48)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, PALETTE["line"], rect, 1)
            surface.blit(self.font.render(f"{rank}. {name.upper()}", False, PALETTE["text"]), (50, y + 8))
            role = f"DANGER {profile.danger:g}  |  {profile.role.upper()}  |  ATK {profile.attack:g}  DEF {profile.defense:g}"
            surface.blit(self.small_font.render(role, False, PALETTE["muted"]), (245, y + 11))
            prey = ", ".join(profile.prey) if profile.prey else "grass and plants"
            surface.blit(self.small_font.render(f"Food: {prey}", False, PALETTE["gold"]), (50, y + 31))
            y += 59

        x = 645
        surface.blit(self.font.render("SPECIES ABILITIES", False, PALETTE["gold"]), (x, 111))
        abilities = [
            ("Elephant", "Massive counterattack; trampling stun."),
            ("Lion", "High damage, bleeding claws, pride bonus."),
            ("Buffalo", "Herd defense and punishing horn charge."),
            ("Crocodile", "Water ambush bonus, bleeding bite."),
            ("Wolf", "Pack attack bonus; must avoid apex animals."),
            ("Zebra", "Fast dodge and stunning defensive kick."),
            ("Snake", "Venom deals damage and slows movement."),
            ("Rabbit", "High dodge; hides in brush and reeds."),
            ("Mouse", "Small target with the highest dodge."),
        ]
        yy = 151
        for name, description in abilities:
            surface.blit(self.font.render(name, False, PALETTE["text"]), (x, yy))
            surface.blit(self.small_font.render(description, False, PALETTE["muted"]), (x + 125, yy + 2))
            yy += 42

        surface.blit(self.font.render("COMBAT RULE", False, PALETTE["danger"]), (x, 555))
        rules = [
            "Attacking above your danger rank triggers a counterattack.",
            "Groups strengthen wolves, lions, zebra, buffalo, and elephants.",
            "Terrain strengthens crocodile ambushes and provides rabbit shelter.",
            "Venom, bleeding, and stun continue after the original attack.",
        ]
        yy = 590
        for rule in rules:
            surface.blit(self.small_font.render(rule, False, PALETTE["text"]), (x, yy))
            yy += 25
