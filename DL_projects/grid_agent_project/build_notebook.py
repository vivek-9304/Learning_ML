import json

def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}

def code(src):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": src.splitlines(keepends=True),
    }

cells = []

cells.append(md("""\
# Grid Agent — Q-Learning in a Grid World

This notebook builds and trains a small **tabular Q-learning agent** that learns to
navigate a randomly generated grid from a start cell to a goal cell while avoiding
obstacles.

The core logic lives in separate, reusable modules so it can also be driven by the
web frontend through either backend:

```
src/grid_env.py        -> GridWorld environment
src/agent.py            -> QLearningAgent
frontend/                -> HTML / CSS / JS control console
backend/app_flask.py     -> Flask REST API
backend/app_fastapi.py   -> FastAPI REST API
```

Run the cells below top to bottom to generate a grid, train the agent, visualize
the learning curve, and animate the learned path.
"""))

cells.append(code("""\
import sys, os
sys.path.insert(0, os.path.abspath(".."))  # ensure `src` is importable if run from notebooks/
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import animation
from IPython.display import HTML

from src.grid_env import GridWorld, ACTION_NAMES
from src.agent import QLearningAgent

plt.rcParams["figure.facecolor"] = "white"
"""))

cells.append(md("## 1. Create the environment\n\nA 10x10 grid with ~20% obstacle density, seeded for reproducibility."))

cells.append(code("""\
env = GridWorld(width=10, height=10, obstacle_ratio=0.2, seed=7)
print(env.render_ascii())
print()
print("start:", env.start, " goal:", env.goal, " obstacles:", len(env.obstacles))
"""))

cells.append(md("## 2. Visualize the empty grid"))

cells.append(code("""\
def draw_grid(env, path=None, ax=None, title=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(0, env.width)
    ax.set_ylim(0, env.height)
    ax.set_xticks(range(env.width + 1))
    ax.set_yticks(range(env.height + 1))
    ax.grid(True, color="#dddddd")
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticklabels([]); ax.set_yticklabels([])

    for (r, c) in env.obstacles:
        ax.add_patch(Rectangle((c, r), 1, 1, color="#333333"))

    sr, sc = env.start
    gr, gc = env.goal
    ax.add_patch(Rectangle((sc, sr), 1, 1, color="#9aa5a0"))
    ax.add_patch(Rectangle((gc, gr), 1, 1, color="#ffb454"))

    if path:
        xs = [c + 0.5 for r, c in path]
        ys = [r + 0.5 for r, c in path]
        ax.plot(xs, ys, color="#2fae72", linewidth=2, alpha=0.8)

    ar, ac = env.agent_pos
    ax.add_patch(plt.Circle((ac + 0.5, ar + 0.5), 0.3, color="#2fae72"))

    if title:
        ax.set_title(title)
    return ax

draw_grid(env, title="Initial grid (grey=start, amber=goal, dark=obstacle)")
plt.show()
"""))

cells.append(md("## 3. Train the Q-learning agent\n\nThe agent explores the grid, receiving `-1` per step, `-5` for bumping into a wall/obstacle, and `+100` for reaching the goal."))

cells.append(code("""\
agent = QLearningAgent(alpha=0.15, gamma=0.95, epsilon=1.0, epsilon_decay=0.995, seed=7)

EPISODES = 500
rewards = agent.train(env, episodes=EPISODES)

print(f"trained {EPISODES} episodes, final epsilon={agent.epsilon:.3f}")
print(f"mean reward (last 20 episodes): {np.mean(rewards[-20:]):.2f}")
"""))

cells.append(md("## 4. Learning curve"))

cells.append(code("""\
window = 20
smoothed = np.convolve(rewards, np.ones(window) / window, mode="valid")

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(rewards, color="#cccccc", linewidth=1, label="episode reward")
ax.plot(range(window - 1, len(rewards)), smoothed, color="#2fae72", linewidth=2, label=f"{window}-episode moving avg")
ax.set_xlabel("episode")
ax.set_ylabel("total reward")
ax.set_title("Training progress")
ax.legend()
plt.show()
"""))

cells.append(md("## 5. Roll out the learned (greedy) policy"))

cells.append(code("""\
path = agent.greedy_path(env)
reached_goal = path[-1] == env.goal
print(f"path length: {len(path) - 1} steps, reached goal: {reached_goal}")

draw_grid(env, path=path, title="Greedy rollout of the trained policy")
plt.show()
"""))

cells.append(md("## 6. Animate the rollout"))

cells.append(code("""\
fig, ax = plt.subplots(figsize=(5, 5))

def animate(i):
    ax.clear()
    env.agent_pos = path[i]
    draw_grid(env, path=path[: i + 1], ax=ax, title=f"step {i}/{len(path) - 1}")

anim = animation.FuncAnimation(fig, animate, frames=len(path), interval=250, repeat=False)
plt.close(fig)
HTML(anim.to_jshtml())
"""))

cells.append(md("""\
## 7. Save the trained policy

Persist the Q-table so the Flask / FastAPI backends (or a fresh notebook session)
can reuse the trained agent without retraining. The backends currently train
in-memory on demand via `/api/train`, but you can wire them up to load this file
instead if you want a pre-trained agent to ship with the app.
"""))

cells.append(code("""\
os.makedirs("../artifacts", exist_ok=True)
agent.save("../artifacts/q_table.json")
print("saved to artifacts/q_table.json")
"""))

cells.append(md("""\
## 8. Next steps

- Open `frontend/index.html` in a browser to drive the same simulation through a
  web console (start `backend/app_flask.py` or `backend/app_fastapi.py` first).
- Tune `alpha`, `gamma`, `epsilon_decay`, or the reward shaping in `src/grid_env.py`
  to see how the learning curve changes.
- Swap `QLearningAgent` for a different algorithm (SARSA, policy gradient, etc.)
  while keeping the same `GridWorld` environment and REST API contract.
"""))

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.11",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

with open("notebook.ipynb", "w") as f:
    json.dump(nb, f, indent=1)

print("wrote notebook.ipynb")
