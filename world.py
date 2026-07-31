import random
from collections import deque

import settings


class World:
    def __init__(self, seed: int, grass_coverage: float, grass_growth_rate: float):
        self.seed = seed
        self.rng = random.Random(seed)
        self.grass_growth_rate = grass_growth_rate
        self.terrain = [
            [settings.TERRAIN_GROUND for _ in range(settings.GRID_COLS)]
            for _ in range(settings.GRID_ROWS)
        ]
        self.grass = [
            [0.0 for _ in range(settings.GRID_COLS)]
            for _ in range(settings.GRID_ROWS)
        ]
        self.generate(grass_coverage)

    def generate(self, grass_coverage: float) -> None:
        # Broad, overlapping patches make the map read like a designed landscape.
        water_centers = [
            (self.rng.randrange(6, settings.GRID_COLS - 6), self.rng.randrange(5, settings.GRID_ROWS - 5), self.rng.randint(3, 6))
            for _ in range(5)
        ]
        forest_centers = [
            (self.rng.randrange(settings.GRID_COLS), self.rng.randrange(settings.GRID_ROWS), self.rng.randint(4, 8))
            for _ in range(7)
        ]
        for y in range(settings.GRID_ROWS):
            for x in range(settings.GRID_COLS):
                edge = min(x, y, settings.GRID_COLS - 1 - x, settings.GRID_ROWS - 1 - y)
                water = any(((x - cx) / radius) ** 2 + ((y - cy) / max(2, radius - 1)) ** 2 < 1 for cx, cy, radius in water_centers)
                forest = any((x - cx) ** 2 + (y - cy) ** 2 < radius ** 2 for cx, cy, radius in forest_centers)
                roll = self.rng.random()
                if water and roll < 0.82:
                    self.terrain[y][x] = settings.TERRAIN_WATER
                elif edge < 3 and roll < 0.28:
                    self.terrain[y][x] = settings.TERRAIN_FOREST
                elif forest and roll < 0.21:
                    self.terrain[y][x] = settings.TERRAIN_FOREST
                elif roll < 0.045:
                    self.terrain[y][x] = settings.TERRAIN_ROCK
                elif roll < 0.13:
                    self.terrain[y][x] = settings.TERRAIN_BUSH
                elif x > settings.GRID_COLS * 0.50 and self.rng.random() < 0.72:
                    self.terrain[y][x] = settings.TERRAIN_SAVANNA
                else:
                    self.terrain[y][x] = settings.TERRAIN_GROUND

                if self.is_suitable_for_grass(x, y) and self.rng.random() < grass_coverage:
                    self.grass[y][x] = self.rng.randint(2, settings.GRASS_MAX)
        self._shape_biome_edges()
        self._clear_spawn_area()

    def _shape_biome_edges(self) -> None:
        original = [row[:] for row in self.terrain]
        for y in range(settings.GRID_ROWS):
            for x in range(settings.GRID_COLS):
                if original[y][x] in {settings.TERRAIN_WATER, settings.TERRAIN_ROCK, settings.TERRAIN_FOREST}:
                    continue
                near_water = any(
                    0 <= x + dx < settings.GRID_COLS
                    and 0 <= y + dy < settings.GRID_ROWS
                    and original[y + dy][x + dx] == settings.TERRAIN_WATER
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                )
                if near_water:
                    self.terrain[y][x] = settings.TERRAIN_REEDS if self.rng.random() < 0.42 else settings.TERRAIN_MUD
                elif original[y][x] == settings.TERRAIN_SAVANNA and self.rng.random() < 0.12:
                    self.terrain[y][x] = settings.TERRAIN_SAND

    def _clear_spawn_area(self) -> None:
        cx, cy = settings.GRID_COLS // 2, settings.GRID_ROWS // 2
        for y in range(cy - 4, cy + 5):
            for x in range(cx - 7, cx + 8):
                if self.in_bounds(x, y):
                    self.terrain[y][x] = settings.TERRAIN_GROUND
                    if self.rng.random() < 0.5:
                        self.grass[y][x] = self.rng.randint(2, settings.GRASS_MAX)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < settings.GRID_COLS and 0 <= y < settings.GRID_ROWS

    def is_blocked(self, x: int, y: int) -> bool:
        return (not self.in_bounds(x, y)) or self.terrain[y][x] in settings.BLOCKED_TERRAINS

    def is_suitable_for_grass(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.terrain[y][x] in {
            settings.TERRAIN_GROUND,
            settings.TERRAIN_FOREST,
            settings.TERRAIN_BUSH,
            settings.TERRAIN_SAVANNA,
            settings.TERRAIN_MUD,
            settings.TERRAIN_REEDS,
        }

    def is_shelter(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.terrain[y][x] in settings.SHELTER_TERRAINS

    def is_blocked_for(self, species: str, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return True
        terrain = self.terrain[y][x]
        if species == "Crocodile":
            return terrain == settings.TERRAIN_ROCK
        if species == "Elephant" and terrain == settings.TERRAIN_WATER:
            return False
        return terrain in settings.BLOCKED_TERRAINS

    def neighbors(self, x: int, y: int, include_self: bool = False):
        if include_self:
            yield x, y
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny) and not self.is_blocked(nx, ny):
                yield nx, ny

    def neighbors_for(self, species: str, x: int, y: int, include_self: bool = False):
        if include_self:
            yield x, y
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny) and not self.is_blocked_for(species, nx, ny):
                yield nx, ny

    def random_empty_position(self, occupied: set[tuple[int, int]] | None = None) -> tuple[int, int]:
        occupied = occupied or set()
        for _ in range(2000):
            x = self.rng.randrange(settings.GRID_COLS)
            y = self.rng.randrange(settings.GRID_ROWS)
            if not self.is_blocked(x, y) and (x, y) not in occupied:
                return x, y
        for y in range(settings.GRID_ROWS):
            for x in range(settings.GRID_COLS):
                if not self.is_blocked(x, y) and (x, y) not in occupied:
                    return x, y
        return settings.GRID_COLS // 2, settings.GRID_ROWS // 2

    def random_habitat_position(self, species: str, occupied: set[tuple[int, int]]) -> tuple[int, int]:
        habitat = settings.SPECIES_PROFILES[species].habitat
        for _ in range(2500):
            x = self.rng.randrange(settings.GRID_COLS)
            y = self.rng.randrange(settings.GRID_ROWS)
            if (
                (x, y) not in occupied
                and self.terrain[y][x] in habitat
                and not self.is_blocked_for(species, x, y)
            ):
                return x, y
        return self.random_empty_position(occupied)

    def valid_adjacent_position(self, x: int, y: int, occupied: set[tuple[int, int]]) -> tuple[int, int] | None:
        choices = list(self.neighbors(x, y, include_self=True))
        self.rng.shuffle(choices)
        for pos in choices:
            if pos not in occupied:
                return pos
        return None

    def grow_grass(self) -> None:
        for y in range(settings.GRID_ROWS):
            for x in range(settings.GRID_COLS):
                if not self.is_suitable_for_grass(x, y):
                    continue
                current = self.grass[y][x]
                if current <= 0 and self.rng.random() < self.grass_growth_rate * 0.25:
                    self.grass[y][x] = 1
                elif current > 0:
                    capacity_factor = 1 - current / settings.GRASS_MAX
                    self.grass[y][x] = min(settings.GRASS_MAX, current + self.grass_growth_rate * capacity_factor)

    def grass_amount(self, x: int, y: int) -> float:
        return float(self.grass[y][x]) if self.in_bounds(x, y) else 0.0

    def eat_grass(self, x: int, y: int, amount: float) -> float:
        eaten = min(self.grass_amount(x, y), amount)
        self.grass[y][x] -= eaten
        return eaten

    def total_grass(self) -> int:
        return sum(1 for row in self.grass for amount in row if amount >= 1)

    def nearest_tile(self, start: tuple[int, int], predicate, max_range: int) -> tuple[tuple[int, int] | None, int | None]:
        queue = deque([(start, 0)])
        visited = {start}
        while queue:
            (x, y), dist = queue.popleft()
            if dist > max_range:
                continue
            if dist > 0 and predicate(x, y):
                return (x, y), dist
            for nx, ny in self.neighbors(x, y):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), dist + 1))
        return None, None

    def step_toward(self, start: tuple[int, int], target: tuple[int, int] | None) -> tuple[int, int]:
        if target is None or start == target:
            return start
        sx, sy = start
        tx, ty = target
        choices = list(self.neighbors(sx, sy))
        if not choices:
            return start
        return min(choices, key=lambda pos: abs(pos[0] - tx) + abs(pos[1] - ty))

    def step_away(self, start: tuple[int, int], threat: tuple[int, int] | None) -> tuple[int, int]:
        if threat is None:
            return start
        sx, sy = start
        choices = list(self.neighbors(sx, sy))
        if not choices:
            return start
        return max(choices, key=lambda pos: abs(pos[0] - threat[0]) + abs(pos[1] - threat[1]))
