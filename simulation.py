from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
import random

import settings
from agents.animal import reset_ids
from agents.rabbit import Rabbit
from agents.wildlife import WildAnimal
from agents.wolf import Wolf
from ai import payoff, strategies, utility_ai
from world import World


CSV_COLUMNS = [
    "tick",
    "day",
    "seed",
    "wolves",
    "rabbits",
    "grass",
    "wolf_births",
    "rabbit_births",
    "wolf_deaths",
    "rabbit_deaths",
    "starvation_deaths",
    "predation_deaths",
    "successful_hunts",
    "failed_hunts",
    "average_wolf_energy",
    "average_rabbit_energy",
    "cautious_rabbits",
    "balanced_rabbits",
    "bold_rabbits",
    "aggressive_wolves",
    "balanced_wolves",
    "energy_saver_wolves",
    "lions",
    "crocodiles",
    "mice",
    "snakes",
    "buffalo",
    "zebras",
    "elephants",
]


class Simulation:
    def __init__(self, config: settings.SimulationConfig | None = None):
        self.config = config or settings.SimulationConfig()
        self.reset(self.config.preset_key)

    def reset(self, preset_key: str | None = None) -> None:
        if preset_key:
            self.config.preset_key = preset_key
            self.config.preset = settings.PRESETS[preset_key]
        reset_ids()
        self.rng = random.Random(self.config.seed)
        self.world = World(self.config.seed, self.config.preset.grass_coverage, self.config.preset.grass_growth_rate)
        self.tick = 0
        self.paused = False
        self.animals = []
        self.dead_records = []
        self.events = []
        self.death_animations = []
        self.selected_id = None
        self.player_id = None
        self.player_species = None
        self.player_food = 0
        self.player_hunts = 0
        self.player_steps = 0
        self.player_death_reason = ""
        self.history = []
        self.births = Counter()
        self.deaths = Counter()
        self.death_causes = Counter()
        self.successful_hunts = 0
        self.failed_hunts = 0
        self.ess_candidate = "Insufficient history"
        occupied = set()
        for _ in range(self.config.preset.rabbits):
            pos = self.world.random_empty_position(occupied)
            occupied.add(pos)
            self.animals.append(Rabbit(*pos, rng=self.rng))
        for _ in range(self.config.preset.wolves):
            pos = self.world.random_empty_position(occupied)
            occupied.add(pos)
            self.animals.append(Wolf(*pos, rng=self.rng))
        for species, count in settings.WILDLIFE_COUNTS.items():
            for _ in range(count):
                pos = self.world.random_habitat_position(species, occupied)
                occupied.add(pos)
                self.animals.append(WildAnimal(species, *pos, rng=self.rng))
        self.record_history(force=True)

    @property
    def day(self) -> int:
        return self.tick // settings.DAY_LENGTH + 1

    @property
    def time_of_day(self) -> float:
        return (self.tick % settings.DAY_LENGTH) / settings.DAY_LENGTH

    def start_player(self, species: str):
        choices = self.animals_by_species(species)
        if not choices:
            return None
        cx, cy = settings.GRID_COLS // 2, settings.GRID_ROWS // 2
        player = min(choices, key=lambda animal: abs(animal.x - cx) + abs(animal.y - cy))
        self.player_id = player.id
        self.player_species = species
        self.selected_id = player.id
        player.energy = player.max_energy
        player.health = 100
        player.current_action = "Ready"
        player.last_decision_reason = "You control this animal."
        return player

    def player_animal(self):
        if self.player_id is None:
            return None
        for animal in self.animals:
            if animal.id == self.player_id and animal.alive:
                return animal
        return None

    def animals_by_species(self, species: str):
        return [animal for animal in self.animals if animal.alive and animal.species == species]

    def count_species(self, species: str) -> int:
        return len(self.animals_by_species(species))

    def occupied_positions(self) -> set[tuple[int, int]]:
        return {animal.pos for animal in self.animals if animal.alive}

    def spatial_lookup(self) -> dict[tuple[int, int], list]:
        lookup = defaultdict(list)
        for animal in self.animals:
            if animal.alive:
                lookup[animal.pos].append(animal)
        return lookup

    def nearby_animals(self, animal, species: str | None, max_range: int):
        result = []
        ax, ay = animal.pos
        for other in self.animals:
            if not other.alive or other is animal:
                continue
            if species and other.species != species:
                continue
            dist = abs(other.x - ax) + abs(other.y - ay)
            if dist <= max_range:
                result.append((other, dist))
        return sorted(result, key=lambda item: item[1])

    def profile_for(self, animal):
        return settings.SPECIES_PROFILES[animal.species]

    def is_predator_of(self, predator, target) -> bool:
        return target.species in self.profile_for(predator).prey

    def nearest_prey(self, predator):
        candidates = []
        px, py = predator.pos
        for other in self.animals:
            if not other.alive or other is predator or not self.is_predator_of(predator, other):
                continue
            distance = abs(other.x - px) + abs(other.y - py)
            if distance <= predator.vision_range:
                candidates.append((other, distance))
        if not candidates:
            return None, None
        predator_danger = self.profile_for(predator).danger
        return min(
            candidates,
            key=lambda item: item[1] + max(0.0, self.profile_for(item[0]).danger - predator_danger * 0.62) * 3,
        )

    def nearest_threat(self, animal):
        candidates = []
        own_danger = self.profile_for(animal).danger
        ax, ay = animal.pos
        for other in self.animals:
            if not other.alive or other is animal:
                continue
            other_profile = self.profile_for(other)
            is_threat = self.is_predator_of(other, animal) or (
                other_profile.danger > own_danger * 1.25 and other.species != animal.species
            )
            if not is_threat:
                continue
            distance = abs(other.x - ax) + abs(other.y - ay)
            if distance <= animal.vision_range:
                candidates.append((other, distance))
        if not candidates:
            return None, None
        return min(candidates, key=lambda item: item[1])

    def nearest_habitat_tile(self, animal):
        habitat = self.profile_for(animal).habitat
        tile, _ = self.world.nearest_tile(
            animal.pos,
            lambda x, y: self.world.terrain[y][x] in habitat and not self.world.is_blocked_for(animal.species, x, y),
            animal.vision_range * 2,
        )
        return tile

    def observe(self, animal) -> dict:
        obs = {
            "nearest_grass": None,
            "nearest_grass_distance": None,
            "nearest_shelter": None,
            "nearest_shelter_distance": None,
            "nearest_wolf": None,
            "nearest_wolf_distance": None,
            "nearest_rabbit": None,
            "nearest_rabbit_distance": None,
            "nearby_mates": [],
            "nearby_competitors": 0,
            "prey_density": 0.0,
            "prey_hotspot": None,
        }
        if animal.species == "Rabbit":
            grass, grass_dist = self.world.nearest_tile(animal.pos, lambda x, y: self.world.grass_amount(x, y) >= 1, animal.vision_range)
            shelter, shelter_dist = self.world.nearest_tile(animal.pos, self.world.is_shelter, animal.vision_range)
            threat, threat_distance = self.nearest_threat(animal)
            mates = [mate for mate, dist in self.nearby_animals(animal, "Rabbit", 1) if mate.strategy == animal.strategy or mate.energy > 45]
            obs.update(
                nearest_grass=grass,
                nearest_grass_distance=grass_dist,
                nearest_shelter=shelter,
                nearest_shelter_distance=shelter_dist,
                nearest_wolf=threat.pos if threat else None,
                nearest_wolf_distance=threat_distance,
                nearby_mates=mates,
            )
        else:
            rabbits = self.nearby_animals(animal, "Rabbit", animal.vision_range)
            wolves = self.nearby_animals(animal, "Wolf", animal.vision_range)
            prey, prey_distance = self.nearest_prey(animal)
            obs.update(
                nearest_rabbit=prey.pos if prey else None,
                nearest_rabbit_distance=prey_distance,
                nearby_mates=[wolf for wolf, dist in self.nearby_animals(animal, "Wolf", 1) if wolf.energy > 80],
                nearby_competitors=len([wolf for wolf, dist in wolves if dist <= 3]),
                prey_density=min(1.0, len(rabbits) / 6),
                prey_hotspot=self._prey_hotspot(rabbits),
            )
        return obs

    def _prey_hotspot(self, rabbits):
        if not rabbits:
            return None
        x = round(sum(rabbit.x for rabbit, _ in rabbits) / len(rabbits))
        y = round(sum(rabbit.y for rabbit, _ in rabbits) / len(rabbits))
        return x, y

    def nearest_rabbit(self, wolf, max_range: int):
        rabbits = self.nearby_animals(wolf, "Rabbit", max_range)
        return rabbits[0][0] if rabbits else None

    def rabbit_at_distance(self, pos: tuple[int, int], max_dist: int):
        px, py = pos
        candidates = []
        for rabbit in self.animals_by_species("Rabbit"):
            dist = abs(rabbit.x - px) + abs(rabbit.y - py)
            if dist <= max_dist:
                candidates.append((rabbit, dist))
        return min(candidates, key=lambda item: item[1])[0] if candidates else None

    def random_neighbor(self, animal):
        choices = list(self.world.neighbors_for(animal.species, animal.x, animal.y, include_self=True))
        self.rng.shuffle(choices)
        occupied = self.occupied_positions() - {animal.pos}
        for pos in choices:
            if pos not in occupied:
                return pos
        return animal.pos

    def step_toward_for(self, animal, target):
        if target is None or animal.pos == target:
            return animal.pos
        choices = list(self.world.neighbors_for(animal.species, animal.x, animal.y))
        if not choices:
            return animal.pos
        occupied = self.occupied_positions() - {animal.pos}
        free = [pos for pos in choices if pos not in occupied]
        choices = free or choices
        return min(choices, key=lambda pos: abs(pos[0] - target[0]) + abs(pos[1] - target[1]))

    def step_away_for(self, animal, threat):
        if threat is None:
            return animal.pos
        choices = list(self.world.neighbors_for(animal.species, animal.x, animal.y))
        if not choices:
            return animal.pos
        occupied = self.occupied_positions() - {animal.pos}
        free = [pos for pos in choices if pos not in occupied]
        choices = free or choices
        return max(choices, key=lambda pos: abs(pos[0] - threat[0]) + abs(pos[1] - threat[1]))

    def step(self, player_command: str | None = None) -> None:
        self.events = []
        for corpse in self.death_animations:
            corpse["ticks"] -= 1
        self.death_animations = [corpse for corpse in self.death_animations if corpse["ticks"] > 0]
        self.tick += 1
        self.world.grow_grass()
        living = [animal for animal in self.animals if animal.alive]
        self.rng.shuffle(living)
        for animal in living:
            if animal.alive and animal.id != self.player_id:
                animal.decide(self)
                if animal.current_action in {"Flee danger", "Escape"}:
                    animal.animation = "run"
                    animal.animation_ticks = 3
        self.resolve_hawk_dove()
        for animal in living:
            if not animal.alive:
                continue
            if animal.id == self.player_id:
                self.act_player(animal, player_command)
            elif self.tick % 4 == 0:
                animal.current_action = "Watching"
                animal.lifecycle(self.profile_for(animal).metabolism)
            else:
                animal.act(self)
        self.resolve_territorial_encounters()
        self.collect_dead()
        if self.tick % settings.CSV_WRITE_INTERVAL == 0:
            self.record_history()
        self.update_ess_candidate()

    def resolve_territorial_encounters(self) -> None:
        territorial = {"Wolf", "Lion", "Crocodile"}
        handled = set()
        for animal in self.animals:
            if not animal.alive or animal.species not in territorial or animal.id == self.player_id:
                continue
            for other, distance in self.nearby_animals(animal, None, 1):
                pair = tuple(sorted((animal.id, other.id)))
                if pair in handled or other.species not in territorial or other.species == animal.species:
                    continue
                handled.add(pair)
                if self.rng.random() < 0.012:
                    self.try_attack(animal, other)

    def act_player(self, animal, command: str | None) -> None:
        profile = self.profile_for(animal)
        directions = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }
        if animal.stunned_ticks > 0:
            animal.current_action = "Stunned by impact"
            animal.lifecycle(profile.metabolism)
            return
        if animal.slowed_ticks > 0 and self.tick % 2 and command in directions:
            animal.current_action = "Venom slows your movement"
            animal.lifecycle(profile.metabolism)
            return
        if command in directions:
            dx, dy = directions[command]
            target = animal.x + dx, animal.y + dy
            occupied = self.occupied_positions() - {animal.pos}
            if not self.world.is_blocked_for(animal.species, *target) and target not in occupied:
                animal.move_to(target, profile.walk_cost)
                self.player_steps += 1
                animal.current_action = f"Travel {command}"
                animal.animation = "run"
                animal.animation_ticks = 2
            else:
                animal.current_action = "Path blocked"
        elif command == "interact":
            if animal.species == "Rabbit":
                eaten = self.world.eat_grass(animal.x, animal.y, settings.GRASS_EAT_AMOUNT)
                if eaten:
                    animal.food_eaten += eaten
                    animal.gain_energy(eaten * settings.RABBIT_EAT_GAIN)
                    self.player_food += eaten
                    animal.current_action = "Graze"
                    self.emit_event("graze", animal)
                elif self.world.is_shelter(animal.x, animal.y):
                    animal.gain_energy(1.2)
                    animal.current_action = "Hide and rest"
                else:
                    animal.current_action = "Nothing to eat"
            else:
                prey = self.adjacent_attack_target(animal)
                if prey and self.try_attack(animal, prey):
                    self.player_hunts += 1
                    animal.current_action = f"Defeated {prey.species.lower()}"
                elif prey:
                    animal.current_action = f"{prey.species} resisted"
                else:
                    animal.current_action = "No animal in reach"
        elif command == "rest":
            animal.gain_energy(1.1)
            if animal.poison_ticks <= 0 and animal.bleeding_ticks <= 0 and animal.health < 100:
                animal.health = min(100, animal.health + 0.45)
                animal.current_action = "Rest and recover"
            else:
                animal.current_action = "Rest"
        else:
            animal.current_action = "Watching"
        animal.last_decision_reason = "Your movement and survival choices determine this action."
        animal.lifecycle(profile.metabolism)

    def emit_event(self, kind: str, animal, target=None) -> None:
        self.events.append(
            {
                "kind": kind,
                "species": animal.species,
                "animal_id": animal.id,
                "target_id": target.id if target else None,
                "x": animal.x,
                "y": animal.y,
                "player_related": animal.id == self.player_id or (target is not None and target.id == self.player_id),
            }
        )

    def player_score(self) -> int:
        survival = self.tick * 2
        hunt_value = 300 if self.player_species == "Lion" else 250
        species_bonus = int(self.player_food * 12) if self.player_species == "Rabbit" else self.player_hunts * hunt_value
        return survival + species_bonus

    def player_objective(self) -> tuple[str, float]:
        if self.player_species == "Rabbit":
            return "Grass eaten", min(1.0, self.player_food / 20)
        goal = 4 if self.player_species == "Lion" else 5
        return "Successful hunts", min(1.0, self.player_hunts / goal)

    def try_reproduce(self, animal) -> bool:
        if not animal.can_reproduce(self):
            return False
        mates = self.observe(animal)["nearby_mates"]
        if not mates:
            return False
        occupied = self.occupied_positions()
        pos = self.world.valid_adjacent_position(animal.x, animal.y, occupied)
        if pos is None:
            return False
        if animal.species == "Rabbit":
            child_strategy = strategies.inherited_strategy(animal.strategy, "Rabbit", self.rng)
            child = Rabbit(*pos, rng=self.rng, strategy=child_strategy)
            child.energy = settings.RABBIT.offspring_energy
            animal.energy -= settings.RABBIT.reproduce_cost
            animal.reproduction_cooldown = settings.RABBIT.reproduce_cooldown
        else:
            child_strategy = strategies.inherited_strategy(animal.strategy, "Wolf", self.rng)
            child = Wolf(*pos, rng=self.rng, strategy=child_strategy)
            child.energy = settings.WOLF.offspring_energy
            animal.energy -= settings.WOLF.reproduce_cost
            animal.reproduction_cooldown = settings.WOLF.reproduce_cooldown
        child.reproduction_cooldown = animal.reproduction_cooldown
        animal.offspring_count += 1
        self.births[animal.species] += 1
        self.animals.append(child)
        return True

    def adjacent_attack_target(self, attacker):
        candidates = []
        for other in self.animals:
            if not other.alive or other is attacker or other.species == attacker.species:
                continue
            distance = abs(other.x - attacker.x) + abs(other.y - attacker.y)
            if distance <= 1:
                edible = 0 if self.is_predator_of(attacker, other) else 1
                candidates.append((edible, self.profile_for(other).danger, other))
        return min(candidates, key=lambda item: (item[0], item[1]))[2] if candidates else None

    def _group_bonus(self, animal) -> float:
        nearby = len(self.nearby_animals(animal, animal.species, 2))
        if animal.species == "Wolf":
            return min(6.0, nearby * 1.8)
        if animal.species == "Lion":
            return min(5.0, nearby * 1.5)
        if animal.species in {"Buffalo", "Zebra", "Elephant"}:
            return min(7.0, nearby * 1.4)
        return 0.0

    def try_attack(self, attacker, target) -> bool:
        if not attacker.alive or not target.alive:
            return False
        attacker_profile = self.profile_for(attacker)
        target_profile = self.profile_for(target)
        distance = abs(attacker.x - target.x) + abs(attacker.y - target.y)
        if distance > 1:
            return False

        attack_power = attacker_profile.attack + self._group_bonus(attacker)
        if attacker.species == "Crocodile" and self.world.terrain[attacker.y][attacker.x] in {
            settings.TERRAIN_WATER,
            settings.TERRAIN_MUD,
            settings.TERRAIN_REEDS,
        }:
            attack_power += 8
        hit_chance = max(0.18, min(0.94, 0.72 + (attacker_profile.danger - target_profile.danger) * 0.035 - target_profile.dodge))
        attacker.energy -= max(1.0, attacker_profile.walk_cost * 2)
        attacker.wasted_energy += max(1.0, attacker_profile.walk_cost * 2)
        attacker.animation = "attack"
        attacker.animation_ticks = 3
        self.emit_event("attack", attacker, target)
        hit = self.rng.random() < hit_chance

        if hit:
            target.animation = "hurt"
            target.animation_ticks = 3
            self.emit_event("hit", target, attacker)
            damage = max(3.0, attack_power - target_profile.defense * 0.48 + self.rng.uniform(-2, 3))
            easy_prey = target_profile.danger <= attacker_profile.danger * 0.45 and self.is_predator_of(attacker, target)
            target.health -= damage
            if easy_prey:
                target.health = 0
            if attacker.species == "Snake":
                resistance = 0.35 if target.species == "Snake" else 1.0
                target.poison_ticks = max(target.poison_ticks, int(12 * resistance))
                target.poison_damage = max(target.poison_damage, 2.2 * resistance)
                target.slowed_ticks = max(target.slowed_ticks, int(12 * resistance))
                target.last_status = "Venom is slowing movement"
                self.emit_event("venom", attacker, target)
            elif attacker.species == "Crocodile":
                target.bleeding_ticks = max(target.bleeding_ticks, 8)
                target.slowed_ticks = max(target.slowed_ticks, 4)
            elif attacker.species == "Lion":
                target.bleeding_ticks = max(target.bleeding_ticks, 5)

        # Large or dangerous targets always retaliate against a reckless weaker attacker.
        must_counter = target.alive and target.health > 0 and target_profile.danger >= attacker_profile.danger * 1.18
        defensive_species = {"Zebra", "Buffalo", "Elephant", "Lion", "Crocodile", "Snake"}
        can_counter = target.alive and target.health > 0 and target.species in defensive_species and (must_counter or self.rng.random() < 0.42)
        if can_counter:
            counter = max(2.0, target_profile.attack * 0.62 + self._group_bonus(target) - attacker_profile.defense * 0.38)
            attacker.health -= counter
            attacker.injury_count += 1
            target.animation = "attack"
            target.animation_ticks = 3
            attacker.animation = "hurt"
            attacker.animation_ticks = 3
            self.emit_event("counter", target, attacker)
            if target.species == "Snake":
                attacker.poison_ticks = max(attacker.poison_ticks, 10)
                attacker.poison_damage = max(attacker.poison_damage, 2.0)
                attacker.slowed_ticks = max(attacker.slowed_ticks, 10)
            if target.species in {"Zebra", "Buffalo", "Elephant"}:
                attacker.stunned_ticks = max(attacker.stunned_ticks, 2 if target.species == "Zebra" else 3)
            if attacker.health <= 0:
                attacker.die("combat")

        if target.health <= 0 and target.alive:
            target.die("predation" if self.is_predator_of(attacker, target) else "combat")
            attacker.successful_hunts += 1
            attacker.gain_energy(attacker_profile.food_gain)
            self.successful_hunts += 1
            self.emit_event("death", target, attacker)
            return True
        if not hit:
            self.failed_hunts += 1
        return False

    def try_hunt(self, wolf, rabbit) -> bool:
        dist = abs(wolf.x - rabbit.x) + abs(wolf.y - rabbit.y)
        chance = utility_ai.estimated_hunt_chance(wolf, dist, rabbit.speed)
        wolf.energy -= settings.WOLF.chase_cost
        wolf.wasted_energy += settings.WOLF.chase_cost
        wolf.animation = "attack"
        wolf.animation_ticks = 3
        self.emit_event("attack", wolf, rabbit)
        if self.rng.random() < chance:
            rabbit.die("predation")
            wolf.successful_hunts += 1
            wolf.gain_energy(settings.WOLF_HUNT_GAIN)
            self.successful_hunts += 1
            self.emit_event("death", rabbit, wolf)
            return True
        self.failed_hunts += 1
        return False

    def resolve_hawk_dove(self) -> None:
        targeters = defaultdict(list)
        for wolf in self.animals_by_species("Wolf"):
            if wolf.current_action in {"Hunt rabbit", "Chase rabbit"}:
                prey = self.nearest_rabbit(wolf, wolf.vision_range)
                if prey:
                    targeters[prey.id].append(wolf)
        for wolves in targeters.values():
            if len(wolves) < 2:
                continue
            first, second = wolves[0], wolves[1]
            a = settings.WOLF_STRATEGIES[first.strategy]["compete"]
            b = settings.WOLF_STRATEGIES[second.strategy]["compete"]
            delta_a, delta_b = settings.HAWK_DOVE_PAYOFFS[(a, b)]
            first.energy += delta_a
            second.energy += delta_b
            if delta_a < -5:
                first.health -= 4
                first.injury_count += 1
            if delta_b < -5:
                second.health -= 4
                second.injury_count += 1

    def collect_dead(self) -> None:
        survivors = []
        for animal in self.animals:
            if animal.alive:
                survivors.append(animal)
                continue
            self.deaths[animal.species] += 1
            self.death_causes[animal.death_reason] += 1
            self.dead_records.append(
                {
                    "species": animal.species,
                    "strategy": animal.strategy,
                    "payoff": payoff.calculate_animal_payoff(animal),
                    "age": animal.age,
                    "offspring": animal.offspring_count,
                }
            )
            self.death_animations.append(
                {
                    "species": animal.species,
                    "x": animal.x,
                    "y": animal.y,
                    "ticks": 8,
                    "reason": animal.death_reason,
                }
            )
            if not any(event["kind"] == "death" and event["animal_id"] == animal.id for event in self.events):
                self.emit_event("death", animal)
            if animal.id == self.player_id:
                self.player_death_reason = animal.death_reason
        self.animals = survivors
        if self.selected_id and not any(animal.id == self.selected_id for animal in self.animals):
            self.selected_id = None

    def select_at_tile(self, x: int, y: int):
        for animal in reversed(self.animals):
            if animal.alive and animal.x == x and animal.y == y:
                self.selected_id = animal.id
                return animal
        self.selected_id = None
        return None

    def selected_animal(self):
        for animal in self.animals:
            if animal.id == self.selected_id and animal.alive:
                return animal
        return None

    def current_stats(self) -> dict:
        rabbits = self.animals_by_species("Rabbit")
        wolves = self.animals_by_species("Wolf")
        r_strats = Counter(a.strategy for a in rabbits)
        w_strats = Counter(a.strategy for a in wolves)
        return {
            "tick": self.tick,
            "day": self.day,
            "seed": self.config.seed,
            "wolves": len(wolves),
            "rabbits": len(rabbits),
            "grass": self.world.total_grass(),
            "wolf_births": self.births["Wolf"],
            "rabbit_births": self.births["Rabbit"],
            "wolf_deaths": self.deaths["Wolf"],
            "rabbit_deaths": self.deaths["Rabbit"],
            "starvation_deaths": self.death_causes["starvation"],
            "predation_deaths": self.death_causes["predation"],
            "successful_hunts": self.successful_hunts,
            "failed_hunts": self.failed_hunts,
            "average_wolf_energy": round(sum(a.energy for a in wolves) / len(wolves), 2) if wolves else 0,
            "average_rabbit_energy": round(sum(a.energy for a in rabbits) / len(rabbits), 2) if rabbits else 0,
            "cautious_rabbits": r_strats["Cautious"],
            "balanced_rabbits": r_strats["Balanced"],
            "bold_rabbits": r_strats["Bold"],
            "aggressive_wolves": w_strats["Aggressive"],
            "balanced_wolves": w_strats["Balanced"],
            "energy_saver_wolves": w_strats["Energy Saver"],
            "lions": self.count_species("Lion"),
            "crocodiles": self.count_species("Crocodile"),
            "mice": self.count_species("Mouse"),
            "snakes": self.count_species("Snake"),
            "buffalo": self.count_species("Buffalo"),
            "zebras": self.count_species("Zebra"),
            "elephants": self.count_species("Elephant"),
        }

    def ecosystem_status(self) -> str:
        stats = self.current_stats()
        if stats["rabbits"] == 0 or stats["wolves"] == 0:
            return "Extinction risk"
        wildlife = [stats["lions"], stats["crocodiles"], stats["snakes"], stats["buffalo"], stats["zebras"], stats["elephants"]]
        if sum(value > 0 for value in wildlife) < 4:
            return "Biodiversity loss"
        if stats["grass"] < 80:
            return "Food shortage"
        if stats["wolves"] > max(12, stats["rabbits"] * 0.35):
            return "Wolf overpopulation"
        if stats["rabbits"] < 10:
            return "Prey collapse"
        if stats["wolves"] < 2:
            return "Predator collapse"
        if len(self.history) > 3 and stats["rabbits"] > self.history[-3]["rabbits"] + 8:
            return "Rabbit growth"
        return "Stable"

    def record_history(self, force: bool = False) -> None:
        row = self.current_stats()
        self.history.append(row)
        if force:
            return
        self.save_csv()

    def save_csv(self) -> None:
        path = Path(self.config.data_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows({key: row.get(key, 0) for key in CSV_COLUMNS} for row in self.history)

    def update_ess_candidate(self) -> None:
        if len(self.history) < 8:
            self.ess_candidate = "Insufficient history"
            return
        payoffs = payoff.average_payoffs(self.animals, self.dead_records)
        candidates = []
        rabbits = self.animals_by_species("Rabbit")
        wolves = self.animals_by_species("Wolf")
        for species, group in (("Rabbit", rabbits), ("Wolf", wolves)):
            if not group:
                continue
            counts = Counter(a.strategy for a in group)
            total = len(group)
            for strategy, count in counts.items():
                freq = count / total
                avg = payoffs.get(f"{species}:{strategy}", 0)
                if freq >= 0.42 and avg >= 0:
                    candidates.append((avg, f"Possible ESS candidate: {strategy} {species}"))
        self.ess_candidate = max(candidates)[1] if candidates else "No ESS candidate yet"
