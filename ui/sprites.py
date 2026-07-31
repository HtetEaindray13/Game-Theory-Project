import random

import pygame

import settings


PALETTE = {
    "ui_bg": (13, 19, 24),
    "panel": (27, 35, 38),
    "line": (109, 128, 105),
    "text": (245, 239, 211),
    "muted": (177, 188, 163),
    "ground": (91, 168, 68),
    "ground_light": (111, 190, 78),
    "grass": (55, 140, 55),
    "grass_dark": (25, 96, 48),
    "forest": (23, 91, 50),
    "water": (32, 139, 178),
    "water_light": (86, 207, 213),
    "rock": (100, 106, 105),
    "bush": (37, 118, 55),
    "rabbit": (239, 230, 207),
    "wolf": (108, 119, 127),
    "danger": (220, 76, 67),
    "gold": (241, 202, 91),
    "energy": (240, 187, 63),
    "health": (91, 194, 99),
}


def _scale(surface: pygame.Surface, factor: int = 2) -> pygame.Surface:
    return pygame.transform.scale(surface, (surface.get_width() * factor, surface.get_height() * factor))


def _tile(seed: int, grassy: bool = False) -> pygame.Surface:
    rng = random.Random(seed)
    surf = pygame.Surface((16, 16))
    surf.fill(PALETTE["ground"] if seed % 2 else (85, 161, 64))
    for _ in range(11):
        x, y = rng.randrange(16), rng.randrange(16)
        color = PALETTE["ground_light"] if rng.random() < 0.45 else (62, 137, 57)
        surf.set_at((x, y), color)
    if grassy:
        for _ in range(6):
            x, y = rng.randrange(1, 15), rng.randrange(7, 15)
            pygame.draw.line(surf, PALETTE["grass_dark"], (x, y), (x, y - rng.randrange(2, 5)))
            if rng.random() < 0.35:
                surf.set_at((x + 1, y - 3), PALETTE["ground_light"])
    return _scale(surf)


def _water(seed: int) -> pygame.Surface:
    surf = pygame.Surface((16, 16))
    surf.fill(PALETTE["water"])
    offset = seed % 5
    pygame.draw.line(surf, (25, 109, 161), (0, 3 + offset), (6, 3 + offset))
    pygame.draw.line(surf, PALETTE["water_light"], (8, 10 - offset // 2), (15, 10 - offset // 2))
    pygame.draw.line(surf, (52, 172, 197), (2, 14), (10, 14))
    return _scale(surf)


def _biome_tile(seed: int, base, dark, light) -> pygame.Surface:
    rng = random.Random(seed)
    surf = pygame.Surface((16, 16))
    surf.fill(base)
    for _ in range(13):
        surf.set_at((rng.randrange(16), rng.randrange(16)), dark if rng.random() < 0.62 else light)
    return _scale(surf)


def _reeds(seed: int) -> pygame.Surface:
    surf = pygame.Surface((16, 16))
    surf.fill((92, 106, 60))
    rng = random.Random(seed)
    for _ in range(8):
        x = rng.randrange(1, 15)
        height = rng.randrange(5, 11)
        pygame.draw.line(surf, (35, 100, 45), (x, 15), (x, height))
        surf.set_at((min(15, x + 1), height), (179, 148, 63))
    return _scale(surf)


def _tree(seed: int) -> pygame.Surface:
    rng = random.Random(seed)
    surf = pygame.Surface((24, 30), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (15, 54, 35, 110), (3, 24, 18, 5))
    pygame.draw.rect(surf, (93, 62, 42), (10, 17, 4, 11))
    pygame.draw.rect(surf, (142, 88, 49), (11, 18, 2, 8))
    colors = [(17, 83, 49), (25, 112, 51), (43, 139, 53), (76, 157, 59)]
    circles = [(7, 15, 7), (16, 15, 7), (12, 8, 9), (5, 8, 6), (19, 8, 5)]
    for i, (x, y, radius) in enumerate(circles):
        pygame.draw.circle(surf, colors[(i + seed) % len(colors)], (x, y), radius)
    for _ in range(10):
        x, y = rng.randrange(4, 21), rng.randrange(3, 17)
        surf.set_at((x, y), (106, 184, 62))
    return _scale(surf)


def _acacia(seed: int) -> pygame.Surface:
    surf = pygame.Surface((26, 27), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (40, 46, 25, 90), (2, 23, 22, 4))
    pygame.draw.rect(surf, (91, 61, 35), (12, 11, 3, 15))
    pygame.draw.line(surf, (91, 61, 35), (13, 14), (6, 9), 2)
    pygame.draw.line(surf, (91, 61, 35), (14, 14), (20, 9), 2)
    pygame.draw.ellipse(surf, (44, 99, 37), (1, 3, 24, 10))
    pygame.draw.ellipse(surf, (74, 126, 42), (5, 1, 17, 8))
    return _scale(surf)


def _dry_shrub(seed: int) -> pygame.Surface:
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    color = (116, 91, 42)
    pygame.draw.line(surf, color, (8, 15), (8, 5), 2)
    pygame.draw.line(surf, color, (8, 9), (3, 6), 1)
    pygame.draw.line(surf, color, (8, 11), (13, 7), 1)
    pygame.draw.line(surf, (169, 137, 57), (3, 6), (1, 3), 1)
    pygame.draw.line(surf, (169, 137, 57), (13, 7), (15, 4), 1)
    return _scale(surf)


def _bush(seed: int) -> pygame.Surface:
    surf = pygame.Surface((18, 16), pygame.SRCALPHA)
    for x, y, c in ((5, 9, (22, 93, 47)), (12, 9, (39, 131, 54)), (9, 5, (54, 151, 59))):
        pygame.draw.circle(surf, c, (x, y), 5)
    berries = (218, 67, 73) if seed % 2 else (85, 139, 218)
    for point in ((5, 7), (10, 4), (13, 10)):
        pygame.draw.rect(surf, berries, (*point, 1, 1))
    return _scale(surf)


def _rock() -> pygame.Surface:
    surf = pygame.Surface((18, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (52, 65, 65, 100), (1, 12, 16, 4))
    pygame.draw.polygon(surf, (76, 82, 82), [(2, 13), (4, 5), (9, 2), (15, 7), (16, 13)])
    pygame.draw.polygon(surf, (127, 137, 132), [(4, 6), (9, 3), (12, 6), (8, 7)])
    pygame.draw.line(surf, (48, 57, 58), (11, 7), (9, 12))
    return _scale(surf)


def _flowers(seed: int) -> pygame.Surface:
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    colors = [(247, 213, 75), (237, 106, 141), (126, 171, 242), (245, 241, 217)]
    rng = random.Random(seed)
    for _ in range(5):
        x, y = rng.randrange(2, 15), rng.randrange(5, 15)
        pygame.draw.line(surf, (31, 111, 45), (x, y + 2), (x, y))
        pygame.draw.rect(surf, colors[rng.randrange(len(colors))], (x - 1, y - 1, 3, 2))
    return _scale(surf)


def _animal(species: str, direction: str, frame: int) -> pygame.Surface:
    surf = pygame.Surface((16, 18), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (9, 19, 19, 110), (2, 14, 13, 3))
    step = frame % 2
    if species == "rabbit":
        body, shade, inner = PALETTE["rabbit"], (188, 179, 166), (231, 145, 152)
        pygame.draw.ellipse(surf, shade, (3, 8, 11, 8))
        pygame.draw.ellipse(surf, body, (4, 7, 10, 8))
        pygame.draw.circle(surf, body, (9, 7), 5)
        pygame.draw.ellipse(surf, body, (6, 0, 3, 8))
        pygame.draw.ellipse(surf, body, (10, 0, 3, 8))
        pygame.draw.line(surf, inner, (7, 1), (7, 5))
        pygame.draw.line(surf, inner, (11, 1), (11, 5))
        eye_x = 11 if direction != "left" else 7
        pygame.draw.rect(surf, (31, 28, 30), (eye_x, 6, 1, 1))
        pygame.draw.rect(surf, body, (3 + step, 14, 4, 2))
        pygame.draw.circle(surf, (250, 247, 232), (3, 10), 2)
    elif species == "wolf":
        body, dark, light = PALETTE["wolf"], (57, 65, 72), (157, 163, 163)
        pygame.draw.ellipse(surf, dark, (2, 7, 13, 9))
        pygame.draw.polygon(surf, body, [(4, 8), (5, 2), (8, 6), (12, 2), (14, 9), (12, 14), (5, 14)])
        pygame.draw.polygon(surf, dark, [(5, 4), (6, 1), (8, 6)])
        pygame.draw.polygon(surf, dark, [(10, 6), (12, 1), (13, 7)])
        pygame.draw.polygon(surf, light, [(7, 11), (12, 10), (10, 14), (6, 14)])
        eye_x = 11 if direction != "left" else 6
        pygame.draw.rect(surf, (242, 191, 67), (eye_x, 7, 1, 1))
        pygame.draw.rect(surf, dark, (3 + step, 14, 3, 2))
        pygame.draw.rect(surf, dark, (10 - step, 14, 3, 2))
    elif species == "lion":
        pygame.draw.circle(surf, (91, 54, 27), (9, 7), 6)
        pygame.draw.circle(surf, (222, 153, 51), (9, 7), 4)
        pygame.draw.ellipse(surf, (201, 129, 42), (3, 9, 12, 7))
        pygame.draw.rect(surf, (105, 59, 27), (11, 6, 1, 1))
        pygame.draw.rect(surf, (180, 102, 35), (4 + step, 14, 3, 2))
        pygame.draw.line(surf, (105, 59, 27), (3, 11), (0, 7), 1)
    elif species == "mouse":
        pygame.draw.ellipse(surf, (111, 101, 96), (4, 9, 10, 6))
        pygame.draw.circle(surf, (148, 135, 126), (11, 9), 4)
        pygame.draw.circle(surf, (215, 154, 158), (9, 6), 2)
        pygame.draw.rect(surf, (18, 18, 18), (12, 8, 1, 1))
        pygame.draw.line(surf, (190, 136, 139), (4, 12), (0, 9), 1)
    elif species == "snake":
        pygame.draw.arc(surf, (52, 94, 35), (2, 7, 12, 9), 0, 6.0, 3)
        pygame.draw.circle(surf, (124, 142, 46), (11, 8), 3)
        pygame.draw.rect(surf, (234, 195, 65), (12, 7, 1, 1))
        pygame.draw.line(surf, (187, 58, 52), (14, 9), (15, 10), 1)
    elif species == "crocodile":
        pygame.draw.polygon(surf, (44, 91, 44), [(0, 11), (4, 7), (14, 7), (16, 10), (13, 14), (4, 14)])
        pygame.draw.rect(surf, (75, 124, 55), (4, 8, 10, 5))
        pygame.draw.rect(surf, (211, 194, 103), (13, 10, 3, 1))
        pygame.draw.rect(surf, (229, 191, 61), (12, 8, 1, 1))
    elif species == "zebra":
        pygame.draw.ellipse(surf, (235, 230, 210), (2, 7, 13, 8))
        for x in (4, 7, 10, 13):
            pygame.draw.line(surf, (35, 38, 39), (x, 8), (x - 1, 13), 1)
        pygame.draw.rect(surf, (235, 230, 210), (10, 3, 4, 7))
        pygame.draw.rect(surf, (35, 38, 39), (11, 4, 1, 5))
    elif species == "buffalo":
        pygame.draw.ellipse(surf, (57, 48, 42), (1, 7, 14, 9))
        pygame.draw.rect(surf, (83, 65, 49), (9, 4, 6, 8))
        pygame.draw.arc(surf, (213, 194, 149), (7, 1, 9, 7), 3.2, 6.1, 2)
        pygame.draw.arc(surf, (213, 194, 149), (11, 1, 7, 7), 0, 2.8, 2)
        pygame.draw.rect(surf, (28, 27, 25), (4 + step, 14, 3, 2))
    elif species == "elephant":
        pygame.draw.ellipse(surf, (126, 132, 132), (1, 6, 14, 10))
        pygame.draw.circle(surf, (149, 151, 148), (11, 8), 5)
        pygame.draw.circle(surf, (103, 110, 112), (8, 7), 4)
        pygame.draw.line(surf, (149, 151, 148), (14, 10), (14, 16), 2)
        pygame.draw.rect(surf, (235, 224, 191), (12, 10, 1, 4))
        pygame.draw.rect(surf, (44, 45, 45), (12, 7, 1, 1))
    if direction == "left":
        surf = pygame.transform.flip(surf, True, False)
    return _scale(surf)


def _lion(direction: str, frame: int) -> pygame.Surface:
    surf = pygame.Surface((24, 20), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.ellipse(surf, (18, 24, 20, 100), (2, 16, 20, 3))
    if direction in {"down", "up"}:
        # A broad frontal mane makes the species immediately recognizable.
        pygame.draw.ellipse(surf, (198, 132, 43), (7, 8, 10, 10))
        pygame.draw.rect(surf, (180, 108, 34), (7 + step, 14, 3, 5))
        pygame.draw.rect(surf, (180, 108, 34), (14 - step, 14, 3, 5))
        pygame.draw.circle(surf, (84, 48, 24), (12, 7), 8)
        pygame.draw.circle(surf, (126, 70, 27), (12, 7), 6)
        pygame.draw.circle(surf, (218, 151, 55), (12, 7), 4)
        pygame.draw.polygon(surf, (218, 151, 55), [(8, 4), (9, 0), (11, 4)])
        pygame.draw.polygon(surf, (218, 151, 55), [(13, 4), (15, 0), (16, 5)])
        pygame.draw.rect(surf, (35, 28, 22), (10, 6, 1, 1))
        pygame.draw.rect(surf, (35, 28, 22), (14, 6, 1, 1))
        pygame.draw.ellipse(surf, (238, 194, 112), (9, 8, 7, 4))
        pygame.draw.rect(surf, (42, 31, 25), (12, 8, 2, 1))
    else:
        # Long side profile with visible legs, muzzle, and tail.
        pygame.draw.ellipse(surf, (209, 143, 48), (3, 8, 15, 8))
        pygame.draw.rect(surf, (180, 108, 34), (5 + step, 13, 3, 5))
        pygame.draw.rect(surf, (180, 108, 34), (14 - step, 13, 3, 5))
        pygame.draw.circle(surf, (84, 48, 24), (18, 8), 7)
        pygame.draw.ellipse(surf, (218, 151, 55), (17, 5, 6, 7))
        pygame.draw.polygon(surf, (218, 151, 55), [(17, 5), (18, 1), (20, 5)])
        pygame.draw.rect(surf, (238, 194, 112), (20, 9, 4, 3))
        pygame.draw.rect(surf, (42, 31, 25), (23, 10, 1, 1))
        pygame.draw.rect(surf, (34, 28, 22), (20, 7, 1, 1))
        pygame.draw.lines(surf, (180, 108, 34), False, [(4, 11), (2, 8), (1, 5)], 2)
        pygame.draw.circle(surf, (84, 48, 24), (1, 4), 2)
        if direction == "left":
            surf = pygame.transform.flip(surf, True, False)
    if direction == "up":
        shade = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        shade.fill((24, 28, 35, 24))
        surf.blit(shade, (0, 0))
    return _scale(surf)


def _detailed_animal(species: str, direction: str, frame: int) -> pygame.Surface:
    surf = pygame.Surface((28, 20), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.ellipse(surf, (12, 20, 18, 100), (2, 16, 24, 3))

    if species == "mouse":
        pygame.draw.ellipse(surf, (119, 108, 102), (7, 9, 14, 8))
        pygame.draw.polygon(surf, (151, 137, 128), [(18, 10), (25, 12), (20, 16)])
        pygame.draw.circle(surf, (170, 153, 143), (18, 9), 4)
        pygame.draw.circle(surf, (218, 155, 160), (18, 8), 2)
        pygame.draw.rect(surf, (24, 23, 22), (22, 11, 1, 1))
        pygame.draw.rect(surf, (222, 174, 176), (25, 12, 1, 1))
        pygame.draw.lines(surf, (191, 137, 141), False, [(8, 13), (3, 11), (1, 7)], 1)
    elif species == "snake":
        body = (74, 111, 43)
        belly = (174, 155, 69)
        pygame.draw.lines(surf, (39, 73, 38), False, [(3, 15), (8, 10), (13, 15), (18, 10), (23, 13)], 5)
        pygame.draw.lines(surf, body, False, [(3, 14), (8, 9), (13, 14), (18, 9), (23, 12)], 3)
        pygame.draw.polygon(surf, body, [(21, 8), (27, 10), (24, 15), (20, 13)])
        pygame.draw.rect(surf, belly, (23, 12, 3, 1))
        pygame.draw.rect(surf, (232, 196, 65), (24, 10, 1, 1))
        pygame.draw.line(surf, (195, 55, 52), (27, 12), (28, 11 + step), 1)
    elif species == "wolf":
        body, dark, light = (111, 121, 129), (48, 57, 65), (171, 175, 172)
        pygame.draw.ellipse(surf, body, (5, 8, 17, 8))
        pygame.draw.polygon(surf, dark, [(6, 10), (1, 6), (4, 14), (9, 13)])
        pygame.draw.polygon(surf, body, [(18, 9), (21, 4), (26, 8), (27, 12), (21, 14)])
        pygame.draw.polygon(surf, dark, [(20, 5), (21, 1), (23, 6)])
        pygame.draw.polygon(surf, dark, [(23, 6), (25, 2), (26, 8)])
        pygame.draw.polygon(surf, light, [(21, 11), (27, 11), (24, 14), (20, 14)])
        pygame.draw.rect(surf, (236, 188, 65), (24, 8, 1, 1))
        pygame.draw.rect(surf, (31, 29, 28), (27, 11, 1, 1))
        pygame.draw.rect(surf, dark, (8 + step, 14, 3, 5))
        pygame.draw.rect(surf, dark, (18 - step, 14, 3, 5))
    elif species == "crocodile":
        dark, body, light = (35, 73, 39), (57, 108, 48), (102, 139, 63)
        pygame.draw.polygon(surf, dark, [(0, 13), (7, 8), (20, 7), (27, 10), (27, 15), (8, 16)])
        pygame.draw.polygon(surf, body, [(4, 12), (9, 8), (20, 8), (27, 10), (27, 13), (8, 14)])
        pygame.draw.rect(surf, (194, 184, 112), (21, 13, 6, 2))
        for x in (9, 13, 17):
            pygame.draw.polygon(surf, light, [(x, 8), (x + 1, 5), (x + 2, 8)])
        pygame.draw.rect(surf, (226, 191, 58), (24, 9, 1, 1))
        pygame.draw.rect(surf, dark, (8 + step, 15, 4, 2))
        pygame.draw.rect(surf, dark, (18 - step, 14, 4, 3))
    elif species == "zebra":
        white, black = (235, 232, 216), (35, 39, 40)
        pygame.draw.ellipse(surf, white, (4, 8, 17, 8))
        pygame.draw.polygon(surf, white, [(17, 10), (20, 3), (24, 4), (26, 9), (22, 12)])
        pygame.draw.polygon(surf, black, [(20, 4), (20, 1), (22, 4)])
        pygame.draw.polygon(surf, black, [(23, 4), (25, 2), (25, 6)])
        for x in (7, 11, 15, 19):
            pygame.draw.line(surf, black, (x, 9), (x - 1, 15), 2)
        pygame.draw.line(surf, black, (21, 5), (24, 8), 1)
        pygame.draw.rect(surf, black, (24, 6, 1, 1))
        pygame.draw.rect(surf, white, (7 + step, 14, 3, 6))
        pygame.draw.rect(surf, black, (7 + step, 18, 3, 2))
        pygame.draw.rect(surf, white, (17 - step, 14, 3, 6))
        pygame.draw.rect(surf, black, (17 - step, 18, 3, 2))
        pygame.draw.line(surf, black, (5, 11), (1, 7), 2)
    elif species == "buffalo":
        body, dark, horn = (67, 55, 45), (35, 32, 29), (214, 196, 151)
        pygame.draw.ellipse(surf, body, (3, 7, 19, 10))
        pygame.draw.ellipse(surf, dark, (5, 5, 10, 8))
        pygame.draw.rect(surf, body, (18, 8, 8, 8))
        pygame.draw.arc(surf, horn, (15, 2, 10, 9), 2.8, 5.8, 2)
        pygame.draw.arc(surf, horn, (21, 2, 8, 9), 0.4, 3.3, 2)
        pygame.draw.rect(surf, (23, 22, 21), (23, 10, 1, 1))
        pygame.draw.rect(surf, dark, (7 + step, 14, 4, 6))
        pygame.draw.rect(surf, dark, (18 - step, 14, 4, 6))
        pygame.draw.line(surf, dark, (4, 11), (1, 8), 2)

    if direction == "left":
        surf = pygame.transform.flip(surf, True, False)
    elif direction == "up":
        shade = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        shade.fill((20, 26, 34, 20))
        surf.blit(shade, (0, 0))
    return _scale(surf)


def make_sprites() -> dict[str, pygame.Surface]:
    sprites = {}
    for i in range(4):
        sprites[f"ground_{i}"] = _tile(i)
        sprites[f"grass_{i}"] = _tile(20 + i, grassy=True)
        sprites[f"water_{i}"] = _water(i)
        sprites[f"savanna_{i}"] = _biome_tile(i, (181, 157, 73), (148, 125, 58), (211, 185, 92))
        sprites[f"sand_{i}"] = _biome_tile(i + 10, (199, 176, 109), (169, 143, 85), (225, 204, 139))
        sprites[f"mud_{i}"] = _biome_tile(i + 20, (105, 88, 60), (76, 68, 51), (135, 112, 70))
        sprites[f"reeds_{i}"] = _reeds(i)
    sprites["forest_0"] = _tree(4)
    sprites["forest_1"] = _tree(9)
    sprites["acacia_0"] = _acacia(2)
    sprites["acacia_1"] = _acacia(7)
    sprites["dry_shrub"] = _dry_shrub(3)
    sprites["rock"] = _rock()
    sprites["bush_0"] = _bush(0)
    sprites["bush_1"] = _bush(1)
    sprites["flowers_0"] = _flowers(8)
    sprites["flowers_1"] = _flowers(19)
    for species in ("rabbit", "wolf", "lion", "mouse", "snake", "crocodile", "zebra", "buffalo", "elephant"):
        for direction in ("down", "up", "left", "right"):
            for frame in range(2):
                if species == "lion":
                    sprite = _lion(direction, frame)
                elif species in {"mouse", "snake", "wolf", "crocodile", "zebra", "buffalo"}:
                    sprite = _detailed_animal(species, direction, frame)
                else:
                    sprite = _animal(species, direction, frame)
                sizes = {
                    "mouse": (28, 24),
                    "snake": (36, 28),
                    "rabbit": (32, 36),
                    "wolf": (44, 34),
                    "zebra": (48, 38),
                    "lion": (48, 42),
                    "crocodile": (52, 30),
                    "buffalo": (50, 40),
                    "elephant": (50, 56),
                }
                sprites[f"{species}_{direction}_{frame}"] = pygame.transform.scale(sprite, sizes[species])
    return sprites
