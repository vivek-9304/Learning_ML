# Grid Agent

A tabular Q-learning agent that navigates a randomly generated grid from a
start cell to a goal cell while avoiding obstacles — with a notebook for
training/experiments, a standalone frontend console, and **two** interchangeable
backends (Flask and FastAPI) exposing the same REST API.

```
grid_agent_project/
├── notebook.ipynb          # train the agent, plot the learning curve, animate the rollout
├── build_notebook.py        # regenerates notebook.ipynb (not needed unless you edit it)
├── requirements.txt
├── src/
│   ├── grid_env.py          # GridWorld environment (state, step, reward)
│   └── agent.py             # QLearningAgent (train, greedy_path, save/load)
├── frontend/                 # plain HTML/CSS/JS control console (no build step)
│   ├── index.html
│   ├── style.css
│   └── script.js
└── backend/
    ├── app_flask.py          # Flask implementation of the REST API
    └── app_fastapi.py        # FastAPI implementation of the same REST API
```

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Train the agent in the notebook

```bash
jupyter notebook notebook.ipynb
```

Run the cells top to bottom: it builds a `GridWorld`, trains a `QLearningAgent`,
plots the learning curve, and animates the greedy rollout.

## 3. Run a backend

Either backend works standalone and exposes the same routes, so you can pick
whichever framework you prefer:

**Flask** (http://localhost:5000)
```bash
python backend/app_flask.py
```

**FastAPI** (http://localhost:8000, interactive docs at `/docs`)
```bash
uvicorn backend.app_fastapi:app --reload --port 8000
```

### API routes (identical on both backends)

| Method | Route         | Body                              | Description                          |
|--------|---------------|------------------------------------|---------------------------------------|
| GET    | `/api/state`  | —                                   | current grid + agent state            |
| POST   | `/api/reset`  | `{width, height, obstacle_ratio, seed}` (all optional) | generate a fresh grid |
| POST   | `/api/step`   | `{action}` (0=up,1=down,2=left,3=right) | move the agent one cell         |
| POST   | `/api/train`  | `{episodes}`                        | run Q-learning for N episodes         |
| GET    | `/api/path`   | —                                   | the agent's current greedy path       |

## 4. Open the frontend

`frontend/index.html` is a static page — just open it in a browser (no build
step required). Use the **API TARGET** dropdown in the header to point it at
either `http://localhost:8000` (FastAPI) or `http://localhost:5000` (Flask).

From the console you can:
- generate a new grid with a chosen size / obstacle density
- run training for N episodes and watch the stats update
- replay the agent's learned (greedy) path as an animated trace
- manually drive the agent with the D-pad or arrow keys

> Note: if you open `index.html` directly via `file://`, most browsers still
> allow the `fetch()` calls to `localhost`, but if you run into CORS issues,
> serve the frontend folder with a tiny static server instead:
> `python -m http.server 8080 --directory frontend`
