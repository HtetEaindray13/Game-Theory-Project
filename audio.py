from array import array
import math
import random

import pygame

import settings


class SoundManager:
    def __init__(self):
        self.enabled = pygame.mixer.get_init() is not None
        self.muted = False
        self.last_played = {}
        self.sounds = {}
        if not self.enabled:
            return
        self.sounds = {
            "select": self._sound(520, 0.16, 0.20, sweep=260),
            "attack": self._sound(190, 0.11, 0.22, sweep=-100, noise=0.22),
            "hit": self._sound(95, 0.12, 0.28, sweep=-45, noise=0.42),
            "counter": self._sound(72, 0.18, 0.30, sweep=-25, noise=0.30),
            "venom": self._sound(650, 0.25, 0.15, sweep=-380, noise=0.50),
            "graze": self._sound(280, 0.10, 0.10, sweep=-70, noise=0.55),
            "death": self._sound(210, 0.42, 0.22, sweep=-170, noise=0.14),
        }
        calls = {
            "Rabbit": (760, 0.12, 180, 0.05),
            "Mouse": (980, 0.10, 260, 0.04),
            "Snake": (720, 0.30, -420, 0.65),
            "Wolf": (430, 0.45, -180, 0.08),
            "Zebra": (570, 0.24, 160, 0.10),
            "Crocodile": (78, 0.38, -18, 0.18),
            "Buffalo": (105, 0.32, -30, 0.14),
            "Lion": (135, 0.48, -55, 0.18),
            "Elephant": (88, 0.55, 70, 0.08),
        }
        for species, (frequency, duration, sweep, noise) in calls.items():
            self.sounds[f"call:{species}"] = self._sound(frequency, duration, 0.16, sweep=sweep, noise=noise)

    def _sound(self, frequency, duration, volume, sweep=0, noise=0.0):
        sample_rate = 44100
        count = int(sample_rate * duration)
        rng = random.Random(int(frequency * 100 + duration * 1000))
        samples = array("h")
        phase = 0.0
        for index in range(count):
            progress = index / max(1, count - 1)
            current = max(30, frequency + sweep * progress)
            phase += 2 * math.pi * current / sample_rate
            envelope = (1 - progress) ** 1.7
            tone = math.sin(phase) + 0.28 * math.sin(phase * 2.03)
            value = tone * (1 - noise) + rng.uniform(-1, 1) * noise
            samples.append(int(max(-1, min(1, value * envelope * volume)) * 32767))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name: str, cooldown_ms: int = 80) -> None:
        if not self.enabled or self.muted or name not in self.sounds:
            return
        now = pygame.time.get_ticks()
        if now - self.last_played.get(name, -10000) < cooldown_ms:
            return
        self.last_played[name] = now
        self.sounds[name].play()

    def play_events(self, events, player) -> None:
        if not self.enabled:
            return
        played = 0
        for event in events:
            distance = 0 if player is None else abs(event["x"] - player.x) + abs(event["y"] - player.y)
            if not event["player_related"] and distance > 8:
                continue
            kind = event["kind"]
            if kind in self.sounds:
                self.play(kind, 55 if event["player_related"] else 140)
                played += 1
            if played >= 2:
                break

    def play_animal_call(self, species: str) -> None:
        self.play(f"call:{species}", 2200)

    def toggle(self) -> bool:
        self.muted = not self.muted
        return not self.muted


class MusicManager:
    def __init__(self):
        self.available = pygame.mixer.get_init() is not None
        self.paused = False
        if not self.available:
            return
        try:
            pygame.mixer.music.load(settings.MUSIC_PATH)
            pygame.mixer.music.set_volume(0.99)
            pygame.mixer.music.play(-1)
        except pygame.error:
            self.available = False

    @property
    def playing(self) -> bool:
        return self.available and not self.paused

    def toggle(self) -> bool:
        if not self.available:
            return False
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.paused = not self.paused
        return not self.paused
