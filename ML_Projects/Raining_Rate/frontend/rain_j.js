const MODEL_API_ENDPOINT = "https://your-model-api.example.com/predict";
 
const ALL_FIELDS = [
  'timestamp','received_snr_db','carrier_frequency_ghz','elevation_angle_deg',
  'slant_range_km','fspl_db','gaseous_attenuation_db','excess_attenuation_db',
  'effective_path_length_km','specific_attenuation_db_per_km','rain_height_km',
  'frequency_ghz','itu_k','itu_alpha','station','climate','simulation_id',
  'rain_rate_mm_per_hr','rain_event','season_sin','season_cos','gs_latitude',
  'gs_humidity','gs_wv','itu_R001','itu_P_rain','snr_roll_mean_5min',
  'snr_roll_std_5min','snr_roll_max_5min','snr_roll_min_5min',
  'snr_roll_mean_30min','snr_roll_std_30min','attenuation_roll_mean',
  'attenuation_roll_std','attenuation_delta','snr_delta'
];
 
const PANEL_MAP = {
  meta: ['timestamp','station','climate','simulation_id'],
  geometry: ['carrier_frequency_ghz','frequency_ghz','elevation_angle_deg','slant_range_km','rain_height_km','effective_path_length_km'],
  signal: ['received_snr_db','fspl_db','gaseous_attenuation_db','excess_attenuation_db','specific_attenuation_db_per_km'],
  itu: ['itu_k','itu_alpha','itu_R001','itu_P_rain','rain_rate_mm_per_hr','rain_event'],
  env: ['gs_latitude','gs_humidity','gs_wv','season_sin','season_cos'],
  rolling: ['snr_roll_mean_5min','snr_roll_std_5min','snr_roll_max_5min','snr_roll_min_5min','snr_roll_mean_30min','snr_roll_std_30min','attenuation_roll_mean','attenuation_roll_std','attenuation_delta','snr_delta']
};
 
document.getElementById('totalCount').textContent = ALL_FIELDS.length;
 
/* ---------------- CLOCK ---------------- */
function tickClock(){
  document.getElementById('clockText').textContent =
    new Date().toLocaleTimeString('en-GB', { hour12:false });
}
tickClock();
setInterval(tickClock, 1000);
 
/* ---------------- AMBIENT RAINDROPS ---------------- */
const dropsHost = document.getElementById('bgDrops');
function spawnDrop(){
  const d = document.createElement('div');
  d.className = 'drop';
  d.textContent = '💧';
  d.style.left = `${Math.random()*100}%`;
  d.style.animationDuration = `${5 + Math.random()*5}s`;
  d.style.fontSize = `${10 + Math.random()*10}px`;
  dropsHost.appendChild(d);
  setTimeout(() => d.remove(), 11000);
}
setInterval(spawnDrop, 900);
for(let i=0;i<5;i++) setTimeout(spawnDrop, i*300);
 
/* ---------------- ACCORDION ---------------- */
document.querySelectorAll('.panel-toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const body = btn.closest('.panel').querySelector('.panel-body');
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!expanded));
    body.classList.toggle('is-collapsed', expanded);
  });
});
 
/* ---------------- PROGRESS TRACKING ---------------- */
function getFieldEl(name){ return document.getElementById(name); }
function isFilled(name){
  const el = getFieldEl(name);
  return !!el && el.value !== '' && el.value !== null;
}
 
function updateProgress(){
  let filled = 0;
  ALL_FIELDS.forEach(name => { if(isFilled(name)) filled++; });
  document.getElementById('filledCount').textContent = filled;
  document.getElementById('progressFill').style.width = `${(filled/ALL_FIELDS.length)*100}%`;
 
  Object.entries(PANEL_MAP).forEach(([panelKey, fields]) => {
    const done = fields.filter(isFilled).length;
    const badge = document.querySelector(`[data-count-for="${panelKey}"]`);
    if(badge){
      badge.textContent = `${done}/${fields.length}`;
      badge.classList.toggle('is-complete', done === fields.length);
    }
  });
 
  ALL_FIELDS.forEach(name => {
    const el = getFieldEl(name);
    if(el && el.tagName !== 'SELECT'){
      el.classList.toggle('is-filled', isFilled(name));
    }
  });
}
 
document.querySelectorAll('[data-field]').forEach(el => {
  el.addEventListener('input', updateProgress);
  el.addEventListener('change', updateProgress);
});
 
/* ---------------- RAIN EVENT TOGGLE ---------------- */
const rainToggle = document.getElementById('rain_event_toggle');
const rainHidden = document.getElementById('rain_event');
const rainLabel = document.getElementById('rain_event_label');
rainToggle.addEventListener('click', () => {
  const on = rainToggle.getAttribute('data-state') === '1';
  rainToggle.setAttribute('data-state', on ? '0' : '1');
  rainToggle.setAttribute('aria-checked', String(!on));
  rainHidden.value = on ? '0' : '1';
  rainToggle.querySelector('.toggle-knob').textContent = on ? '☀️' : '🌧️';
  rainLabel.textContent = on ? 'No / unknown' : 'Yes — rain detected';
  updateProgress();
});
 
/* ---------------- SEASON DERIVE ---------------- */
document.getElementById('deriveSeason').addEventListener('click', () => {
  const tsEl = document.getElementById('timestamp');
  const date = tsEl.value ? new Date(tsEl.value) : new Date();
  const start = new Date(date.getFullYear(), 0, 0);
  const dayOfYear = (date - start) / 86400000;
  const angle = (dayOfYear / 365.25) * 2 * Math.PI;
  document.getElementById('season_sin').value = Math.sin(angle).toFixed(4);
  document.getElementById('season_cos').value = Math.cos(angle).toFixed(4);
  updateProgress();
});
 
/* ---------------- SAMPLE DATA ---------------- */
document.getElementById('sampleBtn').addEventListener('click', () => {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  const sample = {
    timestamp: now.toISOString().slice(0,16),
    station: 'GS-07',
    climate: 'K',
    simulation_id: 'SIM-2026-0142',
    carrier_frequency_ghz: 20.2,
    frequency_ghz: 20.2,
    elevation_angle_deg: 42.5,
    slant_range_km: 38542,
    rain_height_km: 3.6,
    effective_path_length_km: 5.8,
    received_snr_db: 9.4,
    fspl_db: 210.6,
    gaseous_attenuation_db: 0.9,
    excess_attenuation_db: 4.7,
    specific_attenuation_db_per_km: 1.02,
    itu_k: 0.0751,
    itu_alpha: 1.099,
    itu_R001: 42,
    itu_P_rain: 0.31,
    rain_rate_mm_per_hr: 14.5,
    gs_latitude: 28.6139,
    gs_humidity: 88,
    gs_wv: 41.3,
    snr_roll_mean_5min: 10.1,
    snr_roll_std_5min: 1.4,
    snr_roll_max_5min: 12.8,
    snr_roll_min_5min: 8.6,
    snr_roll_mean_30min: 12.6,
    snr_roll_std_30min: 2.3,
    attenuation_roll_mean: 4.1,
    attenuation_roll_std: 1.1,
    attenuation_delta: 1.6,
    snr_delta: -2.4
  };
  Object.entries(sample).forEach(([key, val]) => {
    const el = document.getElementById(key);
    if(el) el.value = val;
  });
  rainToggle.setAttribute('data-state', '1');
  rainToggle.setAttribute('aria-checked', 'true');
  rainToggle.querySelector('.toggle-knob').textContent = '🌧️';
  rainHidden.value = '1';
  rainLabel.textContent = 'Yes — rain detected';
  updateProgress();
});
 
/* ---------------- RESET ---------------- */
document.getElementById('resetBtn').addEventListener('click', () => {
  document.getElementById('predictForm').reset();
  rainToggle.setAttribute('data-state','0');
  rainToggle.setAttribute('aria-checked','false');
  rainToggle.querySelector('.toggle-knob').textContent = '☀️';
  rainHidden.value = '0';
  rainLabel.textContent = 'No / unknown';
  showState('empty');
  updateProgress();
});
 
/* ---------------- INFERENCE: calls YOUR model's API ---------------- */
async function runInference(data){
  if(!MODEL_API_ENDPOINT || MODEL_API_ENDPOINT.includes('your-model-api.example.com')){
    const err = new Error('NOT_CONFIGURED');
    err.code = 'NOT_CONFIGURED';
    throw err;
  }
 
  const response = await fetch(MODEL_API_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
 
  if(!response.ok){
    const err = new Error(`Model API responded with ${response.status}`);
    err.code = 'BAD_RESPONSE';
    throw err;
  }
 
  const json = await response.json();
 
  // Flexible about response shape so this works with most APIs
  // (FastAPI, Flask, SageMaker...) without reshaping anything server-side.
  const rawLabel = json.prediction ?? json.label ?? json.result ?? json.class ?? '';
  const rawProb = json.probability ?? json.confidence ?? json.score ?? null;
 
  const isRain = /^(yes|1|true|rain)$/i.test(String(rawLabel).trim());
  const probability = rawProb !== null && Number.isFinite(parseFloat(rawProb))
    ? Math.max(0, Math.min(1, parseFloat(rawProb)))
    : (isRain ? 0.85 : 0.15);
 
  // Optional: your API can return per-feature explanations, e.g.
  // { "reasons": [["Rain rate","14.5 mm/hr"], ...] }
  const reasons = Array.isArray(json.reasons) ? json.reasons.slice(0, 5) : [];
 
  return { probability, label: isRain ? 'YES' : 'NO', reasons };
}
 
/* ---------------- RESULT STATES ---------------- */
function showState(state){
  document.getElementById('resultEmpty').classList.toggle('is-hidden', state !== 'empty');
  document.getElementById('resultLive').classList.toggle('is-hidden', state !== 'live');
  document.getElementById('resultError').classList.toggle('is-hidden', state !== 'error');
}
 
let fallInterval = null;
function spawnFallDrop(){
  const host = document.getElementById('fallDrops');
  if(!host) return;
  const d = document.createElement('span');
  d.textContent = '💧';
  d.style.left = `${20 + Math.random()*60}%`;
  d.style.animationDuration = `${0.8 + Math.random()*0.6}s`;
  host.appendChild(d);
  setTimeout(() => d.remove(), 1600);
}
 
function renderResult(result){
  showState('live');
  clearInterval(fallInterval);
 
  const character = document.getElementById('character');
  const word = document.getElementById('verdictWord');
  const conf = document.getElementById('verdictConf');
  const caption = document.getElementById('verdictCaption');
  const reasonsEl = document.getElementById('reasons');
  const fallDrops = document.getElementById('fallDrops');
 
  const isRain = result.label === 'YES';
  fallDrops.innerHTML = '';
 
  character.classList.remove('is-happy', 'is-rain');
  if(isRain){
    character.textContent = '🌧️';
    character.classList.add('is-rain');
    fallInterval = setInterval(spawnFallDrop, 150);
  } else {
    character.textContent = '😎';
    character.classList.add('is-happy');
  }
 
  word.style.color = isRain ? 'var(--blue)' : '#1a8f57';
  word.textContent = isRain ? "It's gonna rain! ☔" : 'Clear skies ahead! ✨';
  conf.textContent = `${Math.round(result.probability*100)}% confidence`;
  caption.textContent = isRain
    ? 'Your model expects an active rain-fade event on this link.'
    : 'Your model expects clear-sky conditions on this link.';
 
  reasonsEl.innerHTML = '';
  if(result.reasons.length){
    const header = document.createElement('p');
    header.className = 'reasons-header';
    header.textContent = 'WHY (from your model)';
    reasonsEl.appendChild(header);
    result.reasons.forEach(([label, value]) => {
      const row = document.createElement('div');
      row.className = 'reason-item';
      row.innerHTML = `<span>${label}</span><span>${value}</span>`;
      reasonsEl.appendChild(row);
    });
  }
}
 
function renderError(err){
  showState('error');
  clearInterval(fallInterval);
  const title = document.getElementById('errorTitle');
  const sub = document.getElementById('errorSub');
  if(err && err.code === 'NOT_CONFIGURED'){
    title.textContent = 'RainCast needs your model';
    sub.textContent = "Open script.js and set MODEL_API_ENDPOINT to your model's API URL.";
  } else {
    title.textContent = "Couldn't reach your model";
    sub.textContent = 'Check that the API is running and MODEL_API_ENDPOINT in script.js is correct. See the browser console for details.';
  }
  console.error('RainCast prediction failed:', err);
}
 
/* ---------------- FORM SUBMIT ---------------- */
document.getElementById('predictForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('predictBtn');
  btn.classList.add('is-loading');
  btn.disabled = true;
 
  const data = {};
  ALL_FIELDS.forEach(name => {
    const el = getFieldEl(name);
    data[name] = el ? el.value : '';
  });
 
  try{
    const result = await runInference(data);
    renderResult(result);
  } catch(err){
    renderError(err);
  } finally {
    btn.classList.remove('is-loading');
    btn.disabled = false;
  }
});
 
updateProgress();