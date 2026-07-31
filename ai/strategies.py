import random

import settings


def random_rabbit_strategy(rng: random.Random) -> str:
    return rng.choice(list(settings.RABBIT_STRATEGIES))


def random_wolf_strategy(rng: random.Random) -> str:
    return rng.choice(list(settings.WOLF_STRATEGIES))


def inherited_strategy(parent_strategy: str, species: str, rng: random.Random) -> str:
    if rng.random() > settings.MUTATION_PROBABILITY:
        return parent_strategy
    choices = list(settings.RABBIT_STRATEGIES if species == "Rabbit" else settings.WOLF_STRATEGIES)
    return rng.choice([name for name in choices if name != parent_strategy] or choices)
