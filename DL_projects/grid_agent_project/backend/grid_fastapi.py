"""
app_fastapi.py
FastAPI server exposing the grid-agent simulation as a REST API.
Mirrors app_flask.py so either backend can drive the same frontend.

Run with:
    uvicorn backend.app_fastapi:app --reload --port 8000
Interactive docs are auto-generated at http://localhost:8000/docs
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.grid_env import GridWorld, ACTION_NAMES
from src.agent import QLearningAgent

app = FastAPI(title="Grid Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- in-memory simulation state -------------------------------------------------
env = GridWorld(width=10, height=10, seed=42)
agent = QLearningAgent(seed=42)
trained_episodes = 0


class ResetBody(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    obstacle_ratio: Optional[float] = None
    seed: Optional[int] = None


class StepBody(BaseModel):
    action: int


class TrainBody(BaseModel):
    episodes: int = 200


@app.get("/api/state")
def get_state():
    payload = env.to_dict()
    payload["trained_episodes"] = trained_episodes
    payload["epsilon"] = round(agent.epsilon, 3)
    return payload


@app.post("/api/reset")
def reset(body: ResetBody):
    global env, agent, trained_episodes
    width = body.width or env.width
    height = body.height or env.height
    obstacle_ratio = body.obstacle_ratio if body.obstacle_ratio is not None else env.obstacle_ratio

    env = GridWorld(width=width, height=height, obstacle_ratio=obstacle_ratio, seed=body.seed)
    agent = QLearningAgent(seed=body.seed)
    trained_episodes = 0
    return env.to_dict()


@app.post("/api/step")
def step(body: StepBody):
    if body.action not in ACTION_NAMES:
        raise HTTPException(status_code=400, detail="action must be one of 0(up),1(down),2(left),3(right)")

    pos, reward, done, info = env.step(body.action)
    return {"agent": list(pos), "reward": reward, "done": done, "info": info}


@app.post("/api/train")
def train(body: TrainBody):
    global trained_episodes
    rewards = agent.train(env, episodes=body.episodes)
    trained_episodes += body.episodes
    env.reset()
    return {
        "trained_episodes": trained_episodes,
        "epsilon": round(agent.epsilon, 3),
        "last_reward": rewards[-1] if rewards else None,
        "mean_last_20": sum(rewards[-20:]) / len(rewards[-20:]) if rewards else None,
    }


@app.get("/api/path")
def path():
    greedy_path: List = agent.greedy_path(env)
    return {"path": [list(p) for p in greedy_path]}
