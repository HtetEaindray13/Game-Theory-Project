# Wild Balance

A top-down pixel survival game and living ecosystem simulation built with Python and Pygame. Choose a rabbit, wolf, or lion, explore a scrolling wilderness, and survive inside a nine-species autonomous food web.

## Main Features

- Character-select title screen with three genuinely different play styles.
- Playable rabbit: graze, hide, rest, evade wolves, and survive.
- Playable wolf: hunt small prey, use pack strength, and avoid reckless fights with apex animals.
- Playable lion: stalk savanna prey, inflict bleeding, and challenge dangerous targets.
- Nine species: rabbit, mouse, snake, wolf, zebra, crocodile, buffalo, lion, and elephant.
- Procedural 64 x 42 scrolling world with forest, ponds, reeds, mud, sand, savanna, acacia trees, rocks, berry bushes, and flowers.
- Layered pixel scenery, animated creature frames, camera follow, minimap, day/night tint, score, goals, pause, and game-over screens.
- Detailed directional sprites for every species, with scale matching body size.
- Attack lunges, hurt flashes, running dust, danger alerts, and fading death animations.
- A persistent gold `YOU` marker makes the controlled animal unmistakable.
- Procedural sound effects for attacks, impacts, counters, venom, grazing, death, menus, and nearby animal calls.
- Rabbits eat grass, seek food, hide, escape, rest, wander, and reproduce.
- Wolves chase and hunt rabbits, rest, scout prey-rich areas, compete, and reproduce.
- Utility-based AI stores action scores and rule-based decision explanations.
- Cautious, Balanced, and Bold rabbit strategies.
- Aggressive, Balanced, and Energy Saver wolf strategies.
- Simplified Hawk-Dove competition between wolves targeting the same prey.
- Danger hierarchy with pack/herd bonuses, counterattacks, dodge, defense, and terrain advantages.
- Persistent venom, movement slowdown, bleeding, and impact stun effects.
- Food Web screen describing every species role, prey list, danger rank, and ability.
- Live Theory panel with the current payoff calculation, danger comparison, decision logic, ESS signal, and recommended move.
- Strategy payoff tracking and a cautious "Possible ESS candidate" label.
- Player-focused health and energy HUD plus a live ecosystem statistics screen.
- CSV recording to `data/simulation_results.csv`.
- Non-graphical tests for core simulation logic.

## Install On Windows PowerShell

Python 3.11 through 3.14 are supported. The project uses the community edition of Pygame, which is imported in code with the usual `import pygame`.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

If PowerShell blocks activation, use:

```powershell
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe main.py
```

## Controls

- Title screen: click Rabbit, Wolf, or Lion, or press `R`, `W`, or `L`.
- `WASD` or arrow keys: move your animal.
- `E`: graze as a rabbit, or hunt an adjacent rabbit as a wolf.
- `Space`: rest and recover a small amount of energy.
- `Tab` or `S`: open the living-world statistics.
- `H`: open the Food Web and danger hierarchy.
- `T`: toggle the live Game Theory and payoff panel.
- `V`: mute or unmute sound effects and animal calls.
- `B` or the `MUSIC` button: pause or resume background music independently from sound effects.
- `Escape` or `P`: pause.
- `M`: return to character selection.
- `F11`: toggle fullscreen.
- Mouse: use Menu, Pause, and Stats buttons.

## Play Styles

- Rabbit goal: eat 20 units of grass while staying alive. Bush and forest tiles provide shelter.
- Wolf goal: complete 5 successful hunts. Chasing costs energy, so missed attacks matter.
- Lion goal: complete 4 successful hunts. Lions are strong, but buffalo, crocodiles, and elephants can still punish bad attacks.
- Your score combines survival time with grazing or hunting success.
- The ecosystem continues independently around you and can become stable, scarce, or collapse.
- Resting gradually restores player health unless poison or bleeding is active.
- Rabbit reproduction uses a high energy requirement and long cooldown to prevent population explosions.

## AI Decisions

Each animal observes nearby terrain and agents, scores available actions, and picks the highest utility action. A small seeded randomness value prevents every animal from behaving identically while keeping decisions explainable.

Rabbit scoring considers hunger, grass distance, wolf distance, shelter distance, nearby mates, energy, cooldown, and strategy weights.

Wolf scoring considers hunger, prey distance, estimated catch chance, competition, nearby mates, energy conservation, and strategy weights.

The player uses direct controls. All unchosen animals continue using the same AI and inherited strategies, so each run remains a game-theory experiment.

The Theory panel uses the simulation's real payoff formula:

```text
payoff = survival + energy gained + offspring + hunts + escapes
         - energy spent - injuries
```

Recommendations compare current energy, nearby threats and prey, danger ranks, and pack/herd bonuses.

The supplied `videoplayback.weba` track is preserved in the project. A compatible OGG copy at
`assets/audio/background_music.ogg` loops automatically whenever the app starts.

## Wildlife Rules

- Mice and rabbits forage near brush and rely on high dodge.
- Snakes ambush mice and rabbits. Venom damages health and slows movement.
- Zebra graze in herds and can stun attackers with defensive kicks.
- Wolves gain attack strength from nearby pack members.
- Crocodiles gain an ambush bonus in water, mud, and reeds; their bites cause bleeding.
- Buffalo gain herd defense and counterattack with powerful horn charges.
- Lions gain pride strength and cause bleeding, but dangerous prey can retaliate.
- Elephants sit at the top of the danger hierarchy and deliver the strongest counterattack.
- Attacking an animal far above your danger rank forces a counterattack if it survives.

## Game Theory Concepts

The simulator models predator-prey strategic interaction through strategy-specific utility weights. Rabbit strategies change risk tolerance and food-seeking behavior. Wolf strategies change hunting aggression and energy conservation.

Wolf competition uses a simplified Hawk-Dove interaction:

- Hawk vs Hawk: both lose energy and may take injury.
- Hawk vs Dove: Hawk gets priority, Dove retreats.
- Dove vs Dove: both receive a smaller shared benefit.

The payoff model combines survival time, energy gained, offspring, hunts, escapes, wasted energy, and injury. The statistics screen shows average payoff by strategy. The ESS label is only a simulation-based candidate, not a mathematical proof.

## Project Structure

```text
main.py
settings.py
simulation.py
world.py
camera.py
agents/
ai/
ui/
assets/
data/
tests/
requirements.txt
README.md
```

## Run Tests

```powershell
python -m pytest
python -m compileall .
```

## Known Limitations

- Gameplay sprites and terrain are deterministic procedural pixel art; the ecosystem title scene is an original generated bitmap asset.
- Pathfinding uses simple local movement toward or away from targets.
- The ESS estimate is based on recent strategy dominance and payoff, not formal equilibrium proof.
- CSV is rewritten at recording intervals for simplicity.

## Future Improvements

- Add save slots, sound effects, music, and controller support.
- Add dens, burrows, weather, and seasonal food.
- Add optional graph export with Matplotlib.
- Add A* pathfinding around large ponds.
- Add more detailed academic reporting for strategy payoff over long runs.
