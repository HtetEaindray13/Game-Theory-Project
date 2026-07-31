from __future__ import annotations

from dataclasses import dataclass, field
import random

import settings


_NEXT_ID = 1


def next_id() -> int:
    global _NEXT_ID
    value = _NEXT_ID
    _NEXT_ID += 1
    return value


def reset_ids() -> None:
    global _NEXT_ID
    _NEXT_ID = 1


@dataclass
class Animal:
    species: str
    x: int
    y: int
    strategy: str
    rng: random.Random
    id: int = field(default_factory=next_id)
    energy: float = 0
    max_energy: float = 100
    health: float = 100
    age: int = 0
    max_age: int = 1000
    speed: int = 1
    vision_range: int = 5
    current_action: str = "Wander"
    alive: bool = True
    reproduction_cooldown: int = 0
    target: tuple[int, int] | None = None
    last_decision_reason: str = ""
    last_action_scores: dict[str, float] = field(default_factory=dict)
    offspring_count: int = 0
    food_eaten: float = 0
    successful_hunts: int = 0
    successful_escapes: int = 0
    distance_travelled: int = 0
    energy_gained: float = 0
    wasted_energy: float = 0
    injury_count: int = 0
    death_reason: str = ""
    poison_ticks: int = 0
    poison_damage: float = 0
    bleeding_ticks: int = 0
    slowed_ticks: int = 0
    stunned_ticks: int = 0
    last_status: str = "Healthy"
    animation: str = "idle"
    animation_ticks: int = 0

    @property
    def pos(self) -> tuple[int, int]:
        return self.x, self.y

    def move_to(self, pos: tuple[int, int], cost: float) -> None:
        if pos != self.pos:
            self.x, self.y = pos
            self.energy -= cost
            self.wasted_energy += cost
            self.distance_travelled += 1

    def gain_energy(self, amount: float) -> None:
        before = self.energy
        self.energy = min(self.max_energy, self.energy + amount)
        self.energy_gained += max(0, self.energy - before)

    def lifecycle(self, metabolism: float) -> None:
        self.age += 1
        self.energy -= metabolism
        if self.poison_ticks > 0:
            self.health -= self.poison_damage
            self.poison_ticks -= 1
            self.slowed_ticks = max(self.slowed_ticks, self.poison_ticks)
            self.last_status = f"Venom {self.poison_ticks}"
        elif self.bleeding_ticks > 0:
            self.health -= 1.4
            self.bleeding_ticks -= 1
            self.last_status = f"Bleeding {self.bleeding_ticks}"
        else:
            self.last_status = "Healthy"
        if self.slowed_ticks > 0:
            self.slowed_ticks -= 1
        if self.stunned_ticks > 0:
            self.stunned_ticks -= 1
        if self.animation_ticks > 0:
            self.animation_ticks -= 1
        elif self.animation != "idle":
            self.animation = "idle"
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        if self.energy <= 0:
            self.die("starvation")
        elif self.health <= 0:
            self.die("venom" if self.last_status.startswith("Venom") else "injury")
        elif self.age >= self.max_age:
            self.die("old age")

    def die(self, reason: str) -> None:
        self.alive = False
        self.death_reason = reason
        self.animation = "dying"
        self.animation_ticks = 8

    def can_reproduce(self, sim) -> bool:
        return False

    def status_summary(self) -> str:
        effects = []
        if self.poison_ticks:
            effects.append(f"POISON {self.poison_ticks}")
        if self.bleeding_ticks:
            effects.append(f"BLEEDING {self.bleeding_ticks}")
        if self.slowed_ticks:
            effects.append("SLOWED")
        if self.stunned_ticks:
            effects.append("STUNNED")
        return " | ".join(effects) if effects else "HEALTHY"
