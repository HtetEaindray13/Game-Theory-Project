from collections import defaultdict

import settings


def calculate_animal_payoff(animal) -> float:
    return sum(payoff_breakdown(animal).values())


def payoff_breakdown(animal) -> dict[str, float]:
    weights = settings.PAYOFF_WEIGHTS
    return {
        "Survival": animal.age * weights["survival"],
        "Energy gained": animal.energy_gained * weights["energy_gain"],
        "Offspring": animal.offspring_count * weights["offspring"],
        "Successful hunts": animal.successful_hunts * weights["hunt"],
        "Escapes": animal.successful_escapes * weights["escape"],
        "Energy spent": animal.wasted_energy * weights["wasted_energy"],
        "Injuries": animal.injury_count * weights["injury"],
    }


def average_payoffs(animals, dead_records):
    totals = defaultdict(float)
    counts = defaultdict(int)
    for animal in animals:
        key = f"{animal.species}:{animal.strategy}"
        totals[key] += calculate_animal_payoff(animal)
        counts[key] += 1
    for record in dead_records:
        key = f"{record['species']}:{record['strategy']}"
        totals[key] += record["payoff"]
        counts[key] += 1
    return {key: totals[key] / counts[key] for key in counts}
