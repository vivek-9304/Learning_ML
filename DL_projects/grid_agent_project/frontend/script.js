/* ==========================================================================
   GRIDWATCH — frontend logic
   Talks to either the Flask (port 5000) or FastAPI (port 8000) backend,
   both of which expose the same /api/* routes. Switch backends live via
   the select box in the header.
   ========================================================================== */

const els = {
  apiBase: document.getElementById("apiBase"),
  connDot: document.getElementById("connDot"),
  grid: document.getElementById("grid"),
  stageStatus: document.getElementById("stageStatus"),
  stageCoords: document.getElementById("stageCoords"),
  logLine: document.getElementById("logLine"),

  cfgWidth: document.getElementById("cfgWidth"),
  cfgHeight: document.getElementById("cfgHeight"),
  cfgObstacle: document.getElementById("cfgObstacle"),
  cfgObstacleVal: document.getElementById("cfgObstacleVal"),
  cfgEpisodes: document.getElementById("cfgEpisodes"),

  btnReset: document.getElementById("btnReset"),
  btnTrain: document.getElementById("btnTrain"),
  btnPath: document.getElementById("btnPath"),

  statEpisodes: document.getElementById("statEpisodes"),
  statEpsilon: document.getElementById("statEpsilon"),
  statReward: document.getElementById("statReward"),
  statLastReward: document.getElementById("statLastReward"),
};

let state = null; // last known grid/agent state from the server

function apiBase() {
  return els.apiBase.value;
}

function log(msg) {
  els.logLine.textContent = msg;
}

async function api(path, options = {}) {
  const url = `${apiBase()}${path}`;
  try {
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    els.connDot.classList.remove("offline");
    els.connDot.classList.add("online");
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.error || body.detail || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    els.connDot.classList.remove("online");
    els.connDot.classList.add("offline");
    log(`error: ${err.message} — is the backend running at ${apiBase()}?`);
    throw err;
  }
}

/* ---------------------------------- rendering ---------------------------------- */
function renderGrid(s, trail = []) {
  state = s;
  els.grid.style.gridTemplateColumns = `repeat(${s.width}, 34px)`;
  els.grid.innerHTML = "";

  const obstacleSet = new Set(s.obstacles.map(([r, c]) => `${r},${c}`));
  const trailSet = new Set(trail.map(([r, c]) => `${r},${c}`));

  for (let r = 0; r < s.height; r++) {
    for (let c = 0; c < s.width; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      const key = `${r},${c}`;

      if (obstacleSet.has(key)) cell.classList.add("obstacle");
      if (r === s.start[0] && c === s.start[1]) cell.classList.add("start");
      if (r === s.goal[0] && c === s.goal[1]) cell.classList.add("goal");
      if (trailSet.has(key)) cell.classList.add("trail");
      if (r === s.agent[0] && c === s.agent[1]) cell.classList.add("agent");

      els.grid.appendChild(cell);
    }
  }

  els.stageCoords.textContent = `agent (${s.agent[0]},${s.agent[1]})`;
  els.statEpisodes.textContent = s.trained_episodes ?? 0;
  els.statEpsilon.textContent = (s.epsilon ?? 1).toFixed(3);
}

/* ---------------------------------- actions ---------------------------------- */
async function loadState() {
  const s = await api("/api/state");
  renderGrid(s);
  els.stageStatus.textContent = "idle — grid loaded";
  els.stageStatus.className = "stage-status";
}

async function resetGrid() {
  const body = {
    width: parseInt(els.cfgWidth.value, 10),
    height: parseInt(els.cfgHeight.value, 10),
    obstacle_ratio: parseFloat(els.cfgObstacle.value),
  };
  log("generating new grid…");
  const s = await api("/api/reset", { method: "POST", body: JSON.stringify(body) });
  renderGrid(s);
  els.statReward.textContent = "—";
  els.statLastReward.textContent = "—";
  els.stageStatus.textContent = "idle — new grid generated";
  els.stageStatus.className = "stage-status";
  log("grid generated.");
}

async function trainAgent() {
  const episodes = parseInt(els.cfgEpisodes.value, 10);
  els.stageStatus.textContent = `training — ${episodes} episodes…`;
  els.stageStatus.className = "stage-status active";
  log(`training for ${episodes} episodes…`);

  const result = await api("/api/train", {
    method: "POST",
    body: JSON.stringify({ episodes }),
  });

  els.statEpisodes.textContent = result.trained_episodes;
  els.statEpsilon.textContent = result.epsilon.toFixed(3);
  els.statReward.textContent =
    result.mean_last_20 !== null ? result.mean_last_20.toFixed(1) : "—";

  await loadState();
  els.stageStatus.textContent = "idle — training complete";
  log(`training complete. epsilon now ${result.epsilon.toFixed(3)}.`);
}

async function tracePath() {
  els.stageStatus.textContent = "replaying learned policy…";
  els.stageStatus.className = "stage-status active";
  log("fetching greedy path…");

  const { path } = await api("/api/path");
  if (!state) await loadState();

  for (let i = 0; i < path.length; i++) {
    const trailSoFar = path.slice(0, i);
    const stepState = { ...state, agent: path[i] };
    renderGrid(stepState, trailSoFar);
    await sleep(220);
  }

  const reached =
    path.length &&
    path[path.length - 1][0] === state.goal[0] &&
    path[path.length - 1][1] === state.goal[1];

  els.stageStatus.textContent = reached
    ? "goal reached"
    : "path did not reach goal — try training longer";
  els.stageStatus.className = reached ? "stage-status done" : "stage-status";
  log(`path replay finished (${path.length - 1} steps).`);
}

async function manualStep(action) {
  try {
    const result = await api("/api/step", {
      method: "POST",
      body: JSON.stringify({ action }),
    });
    if (!state) return;
    state.agent = result.agent;
    renderGrid(state);
    els.statLastReward.textContent = result.reward.toFixed(1);
    if (result.done) {
      els.stageStatus.textContent = "goal reached";
      els.stageStatus.className = "stage-status done";
      log("agent reached the goal.");
    } else {
      log(`step taken — reward ${result.reward.toFixed(1)}`);
    }
  } catch {
    /* error already logged by api() */
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/* ---------------------------------- wiring ---------------------------------- */
els.cfgObstacle.addEventListener("input", () => {
  els.cfgObstacleVal.textContent = parseFloat(els.cfgObstacle.value).toFixed(2);
});

els.btnReset.addEventListener("click", () => resetGrid().catch(() => {}));
els.btnTrain.addEventListener("click", () => trainAgent().catch(() => {}));
els.btnPath.addEventListener("click", () => tracePath().catch(() => {}));
els.apiBase.addEventListener("change", () => loadState().catch(() => {}));

document.querySelectorAll(".dpad-btn").forEach((btn) => {
  btn.addEventListener("click", () => manualStep(parseInt(btn.dataset.action, 10)));
});

document.addEventListener("keydown", (e) => {
  const map = { ArrowUp: 0, ArrowDown: 1, ArrowLeft: 2, ArrowRight: 3 };
  if (e.key in map) {
    e.preventDefault();
    manualStep(map[e.key]);
  }
});

/* ---------------------------------- boot ---------------------------------- */
loadState().catch(() => {
  log("no backend reachable yet — start app_flask.py or app_fastapi.py, then reload.");
});
