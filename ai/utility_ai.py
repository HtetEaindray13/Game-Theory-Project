import math

import settings


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def distance(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def rabbit_scores(rabbit, obs, world, sim) -> tuple[dict[str, float], str]:
    weights = settings.RABBIT_STRATEGIES[rabbit.strategy]
    hunger = 1 - rabbit.energy / rabbit.max_energy
    wolf_dist = obs["nearest_wolf_distance"]
    grass_dist = obs["nearest_grass_distance"]
    shelter_dist = obs["nearest_shelter_distance"]
    predator_risk = 0 if wolf_dist is None else clamp((rabbit.vision_range + 1 - wolf_dist) / rabbit.vision_range, 0, 1)
    food_signal = 0 if grass_dist is None else clamp((rabbit.vision_range + 1 - grass_dist) / rabbit.vision_range, 0, 1)
    shelter_signal = 0 if shelter_dist is None else clamp((rabbit.vision_range + 1 - shelter_dist) / rabbit.vision_range, 0, 1)
    ready = rabbit.can_reproduce(sim)
    mate_bonus = 1 if obs["nearby_mates"] else 0
    tile_has_grass = world.grass_amount(rabbit.x, rabbit.y) > 0

    scores = {
        "Eat grass": 72 * hunger * weights["food"] + 22 * tile_has_grass - 48 * predator_risk * weights["danger"],
        "Move toward grass": 54 * hunger * food_signal * weights["food"] - 36 * predator_risk * weights["danger"],
        "Hide": 74 * predator_risk * shelter_signal * weights["shelter"] - 20 * hunger,
        "Escape": 66 * predator_risk * weights["escape"] - 12 * shelter_signal - 8 * hunger,
        "Rest": 34 * (1 - hunger) - 26 * predator_risk,
        "Wander": 18 - 12 * predator_risk + 8 * rabbit.rng.random(),
        "Reproduce": 82 * ready * mate_bonus * weights["reproduce"] - 32 * hunger - 35 * predator_risk,
    }
    for action in list(scores):
        scores[action] = clamp(scores[action] + rabbit.rng.uniform(-2.5, 2.5))

    top = max(scores, key=scores.get)
    parts = []
    if wolf_dist is not None:
        parts.append(f"Wolf detected {wolf_dist} tiles away.")
    if grass_dist is not None:
        parts.append(f"Grass detected {grass_dist} tiles away.")
    if shelter_dist is not None:
        parts.append(f"Shelter detected {shelter_dist} tiles away.")
    if ready and mate_bonus:
        parts.append("Energy and cooldown allow reproduction.")
    if not parts:
        parts.append("No urgent nearby threats or food; using baseline strategy.")
    return scores, " ".join(parts) + f" Highest utility: {top}."


def wolf_scores(wolf, obs, world, sim) -> tuple[dict[str, float], str]:
    weights = settings.WOLF_STRATEGIES[wolf.strategy]
    hunger = 1 - wolf.energy / wolf.max_energy
    rabbit_dist = obs["nearest_rabbit_distance"]
    prey_signal = 0 if rabbit_dist is None else clamp((wolf.vision_range + 1 - rabbit_dist) / wolf.vision_range, 0, 1)
    catch_chance = 0 if rabbit_dist is None else estimated_hunt_chance(wolf, rabbit_dist)
    ready = wolf.can_reproduce(sim)
    mate_bonus = 1 if obs["nearby_mates"] else 0
    competition = clamp(obs["nearby_competitors"] / 3, 0, 1)

    scores = {
        "Hunt rabbit": 80 * hunger * catch_chance * weights["hunt"] - 10 * competition,
        "Chase rabbit": 68 * hunger * prey_signal * weights["hunt"] - 26 * (1 - wolf.energy / wolf.max_energy) * weights["energy"],
        "Move toward prey-rich territory": 34 * hunger * obs["prey_density"] - 9 * competition,
        "Rest": 42 * (1 - wolf.energy / wolf.max_energy) * weights["energy"] - 18 * prey_signal,
        "Wander": 18 - 8 * competition + wolf.rng.uniform(0, 8),
        "Reproduce": 76 * ready * mate_bonus * weights["reproduce"] - 30 * hunger,
    }
    for action in list(scores):
        scores[action] = clamp(scores[action] + wolf.rng.uniform(-2.0, 2.0))

    top = max(scores, key=scores.get)
    parts = []
    if rabbit_dist is not None:
        parts.append(f"Rabbit detected {rabbit_dist} tiles away; estimated catch chance {catch_chance:.2f}.")
    if competition:
        parts.append("Nearby wolf competition affects hunting payoff.")
    if ready and mate_bonus:
        parts.append("A compatible mate is nearby and cooldown is complete.")
    if not parts:
        parts.append("No reachable prey; conserving energy and scouting.")
    return scores, " ".join(parts) + f" Highest utility: {top}."


def estimated_hunt_chance(wolf, dist: int, rabbit_speed: int = 1) -> float:
    strategy_bonus = {"Aggressive": 0.1, "Balanced": 0.0, "Energy Saver": -0.05}[wolf.strategy]
    chance = (
        settings.HUNT_BASE_CHANCE
        - settings.HUNT_DISTANCE_PENALTY * max(0, dist - 1)
        - settings.HUNT_RABBIT_SPEED_PENALTY * rabbit_speed
        + settings.HUNT_ENERGY_BONUS * (wolf.energy / wolf.max_energy)
        + strategy_bonus
    )
    return clamp(chance, 0.05, 0.92)
