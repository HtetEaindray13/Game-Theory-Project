from dataclasses import dataclass, field


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 32
GRID_COLS = 64
GRID_ROWS = 42
MAP_WIDTH = GRID_COLS * TILE_SIZE
MAP_HEIGHT = GRID_ROWS * TILE_SIZE
HUD_HEIGHT = 64
BOTTOM_BAR_HEIGHT = 68
PANEL_WIDTH = 0
FPS = 60
SIM_STEPS_PER_SECOND = 4
RANDOM_SEED = 4242
CSV_WRITE_INTERVAL = 25
DAY_LENGTH = 144
PLAYER_MOVE_REPEAT_MS = 115
TITLE_ART_PATH = "assets/wild_balance_ecosystem.png"
MUSIC_PATH = "assets/audio/background_music.ogg"

SPEEDS = [1, 2, 4, 8]

TERRAIN_GROUND = "ground"
TERRAIN_GRASS = "grass"
TERRAIN_FOREST = "forest"
TERRAIN_WATER = "water"
TERRAIN_ROCK = "rock"
TERRAIN_BUSH = "bush"
TERRAIN_SAVANNA = "savanna"
TERRAIN_SAND = "sand"
TERRAIN_MUD = "mud"
TERRAIN_REEDS = "reeds"
BLOCKED_TERRAINS = {TERRAIN_WATER, TERRAIN_ROCK}
SHELTER_TERRAINS = {TERRAIN_FOREST, TERRAIN_BUSH, TERRAIN_REEDS}


@dataclass(frozen=True)
class Preset:
    name: str
    wolves: int
    rabbits: int
    grass_coverage: float
    grass_growth_rate: float


PRESETS = {
    "balanced": Preset("Balanced ecosystem", wolves=4, rabbits=32, grass_coverage=0.34, grass_growth_rate=0.035),
    "wolves": Preset("Wolf overpopulation", wolves=13, rabbits=32, grass_coverage=0.34, grass_growth_rate=0.035),
    "shortage": Preset("Grass shortage", wolves=4, rabbits=32, grass_coverage=0.16, grass_growth_rate=0.014),
    "decline": Preset("Rabbit decline", wolves=6, rabbits=12, grass_coverage=0.34, grass_growth_rate=0.035),
}
DEFAULT_PRESET = "balanced"


@dataclass
class AnimalConfig:
    max_energy: float
    max_age: int
    speed: int
    vision_range: int
    metabolism: float
    walk_cost: float
    chase_cost: float
    rest_gain: float
    reproduce_energy: float
    reproduce_cost: float
    reproduce_cooldown: int
    offspring_energy: float
    max_population: int


RABBIT = AnimalConfig(
    max_energy=100,
    max_age=1200,
    speed=1,
    vision_range=6,
    metabolism=0.22,
    walk_cost=0.72,
    chase_cost=2.1,
    rest_gain=0.18,
    reproduce_energy=90,
    reproduce_cost=45,
    reproduce_cooldown=320,
    offspring_energy=40,
    max_population=60,
)

WOLF = AnimalConfig(
    max_energy=150,
    max_age=1650,
    speed=1,
    vision_range=8,
    metabolism=0.40,
    walk_cost=1.18,
    chase_cost=3.2,
    rest_gain=0.12,
    reproduce_energy=104,
    reproduce_cost=42,
    reproduce_cooldown=150,
    offspring_energy=74,
    max_population=45,
)

GRASS_MAX = 5
GRASS_EAT_AMOUNT = 2
RABBIT_EAT_GAIN = 17
WOLF_HUNT_GAIN = 58
MUTATION_PROBABILITY = 0.02


@dataclass(frozen=True)
class SpeciesProfile:
    role: str
    danger: float
    max_energy: float
    max_age: int
    vision: int
    metabolism: float
    walk_cost: float
    attack: float
    defense: float
    dodge: float
    food_gain: float
    habitat: tuple[str, ...]
    prey: tuple[str, ...] = ()


SPECIES_PROFILES = {
    "Mouse": SpeciesProfile(
        "herbivore", 1.0, 48, 680, 5, 0.16, 0.35, 2, 1, 0.36, 8,
        (TERRAIN_GROUND, TERRAIN_FOREST, TERRAIN_BUSH),
    ),
    "Rabbit": SpeciesProfile(
        "herbivore", 2.0, RABBIT.max_energy, RABBIT.max_age, RABBIT.vision_range,
        RABBIT.metabolism, RABBIT.walk_cost, 4, 2, 0.30, RABBIT_EAT_GAIN,
        (TERRAIN_GROUND, TERRAIN_FOREST, TERRAIN_BUSH),
    ),
    "Snake": SpeciesProfile(
        "ambush", 3.5, 72, 1100, 6, 0.20, 0.55, 8, 2, 0.24, 24,
        (TERRAIN_ROCK, TERRAIN_SAND, TERRAIN_SAVANNA, TERRAIN_BUSH),
        ("Mouse", "Rabbit"),
    ),
    "Zebra": SpeciesProfile(
        "herbivore", 4.5, 140, 1800, 8, 0.30, 0.75, 11, 8, 0.20, 14,
        (TERRAIN_SAVANNA, TERRAIN_GROUND),
    ),
    "Wolf": SpeciesProfile(
        "predator", 5.5, WOLF.max_energy, WOLF.max_age, WOLF.vision_range,
        WOLF.metabolism, WOLF.walk_cost, 19, 8, 0.17, WOLF_HUNT_GAIN,
        (TERRAIN_GROUND, TERRAIN_FOREST, TERRAIN_SAVANNA),
        ("Rabbit", "Mouse", "Zebra"),
    ),
    "Crocodile": SpeciesProfile(
        "ambush", 7.5, 180, 2400, 7, 0.30, 0.68, 28, 16, 0.08, 68,
        (TERRAIN_WATER, TERRAIN_MUD, TERRAIN_REEDS),
        ("Rabbit", "Mouse", "Zebra", "Buffalo"),
    ),
    "Buffalo": SpeciesProfile(
        "herbivore", 8.0, 190, 2200, 7, 0.34, 0.82, 27, 20, 0.08, 17,
        (TERRAIN_SAVANNA, TERRAIN_MUD, TERRAIN_GROUND),
    ),
    "Lion": SpeciesProfile(
        "predator", 8.5, 200, 2150, 10, 0.42, 1.0, 31, 17, 0.14, 76,
        (TERRAIN_SAVANNA, TERRAIN_GROUND),
        ("Rabbit", "Mouse", "Zebra", "Buffalo"),
    ),
    "Elephant": SpeciesProfile(
        "herbivore", 10.0, 260, 3000, 8, 0.38, 0.88, 38, 30, 0.04, 19,
        (TERRAIN_SAVANNA, TERRAIN_MUD, TERRAIN_GROUND),
    ),
}

WILDLIFE_COUNTS = {
    "Lion": 3,
    "Crocodile": 3,
    "Mouse": 12,
    "Snake": 6,
    "Buffalo": 5,
    "Zebra": 10,
    "Elephant": 4,
}

HUNT_BASE_CHANCE = 0.56
HUNT_DISTANCE_PENALTY = 0.13
HUNT_RABBIT_SPEED_PENALTY = 0.07
HUNT_ENERGY_BONUS = 0.18

RABBIT_STRATEGIES = {
    "Cautious": {"danger": 1.55, "food": 0.82, "shelter": 1.42, "escape": 1.45, "reproduce": 0.84},
    "Balanced": {"danger": 1.0, "food": 1.0, "shelter": 1.0, "escape": 1.0, "reproduce": 1.0},
    "Bold": {"danger": 0.62, "food": 1.35, "shelter": 0.62, "escape": 0.72, "reproduce": 1.16},
}

WOLF_STRATEGIES = {
    "Aggressive": {"hunt": 1.35, "energy": 0.72, "compete": "Hawk", "reproduce": 1.06},
    "Balanced": {"hunt": 1.0, "energy": 1.0, "compete": "Dove", "reproduce": 1.0},
    "Energy Saver": {"hunt": 0.78, "energy": 1.45, "compete": "Dove", "reproduce": 0.9},
}

HAWK_DOVE_PAYOFFS = {
    ("Hawk", "Hawk"): (-9, -9),
    ("Hawk", "Dove"): (8, -4),
    ("Dove", "Hawk"): (-4, 8),
    ("Dove", "Dove"): (3, 3),
}

PAYOFF_WEIGHTS = {
    "survival": 0.08,
    "energy_gain": 0.22,
    "offspring": 24,
    "hunt": 18,
    "escape": 7,
    "wasted_energy": -0.18,
    "injury": -10,
}


@dataclass
class SimulationConfig:
    seed: int = RANDOM_SEED
    preset_key: str = DEFAULT_PRESET
    ess_window: int = 160
    data_path: str = "data/simulation_results.csv"
    speed_index: int = 0
    debug: bool = False
    preset: Preset = field(init=False)

    def __post_init__(self) -> None:
        self.preset = PRESETS[self.preset_key]
