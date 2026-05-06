"""
games/snake_game.py — Returns a self-contained HTML5 + JS Snake game string.
"""
from __future__ import annotations
import html


def get_snake_html(player_name: str, high_score: int) -> str:
    safe_name = html.escape(player_name[:20])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Snake Game</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #0E0E1A;
    display: flex; flex-direction: column;
    align-items: center; justify-content: flex-start;
    min-height: 100vh;
    font-family: 'Segoe UI', sans-serif;
    color: #EAEAEA;
    padding: 10px;
  }}
  h2 {{ color: #6C63FF; margin-bottom: 6px; font-size: 1.3rem; }}
  #hud {{
    display: flex; gap: 20px; align-items: center;
    margin-bottom: 8px; font-size: 0.9rem;
  }}
  .hud-item {{ background: #1A1A2E; padding: 4px 12px; border-radius: 8px; }}
  .hud-item span {{ color: #6C63FF; font-weight: bold; font-size: 1rem; }}
  #canvas-wrap {{ position: relative; }}
  #gameCanvas {{
    border: 2px solid #6C63FF;
    border-radius: 8px;
    display: block;
    outline: none;
    cursor: none;
    box-shadow: 0 0 20px rgba(108,99,255,0.4);
  }}
  #overlay {{
    position: absolute; top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(14,14,26,0.88);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    border-radius: 8px;
    gap: 10px;
  }}
  #overlay h3 {{ color: #6C63FF; font-size: 1.6rem; }}
  #overlay p {{ font-size: 0.95rem; color: #aaa; }}
  .btn {{
    background: #6C63FF; color: #fff;
    border: none; padding: 10px 28px;
    border-radius: 24px; font-size: 1rem;
    cursor: pointer; font-weight: 600;
    transition: background 0.2s, transform 0.1s;
  }}
  .btn:hover {{ background: #857df7; transform: scale(1.04); }}
  .btn.secondary {{ background: #1A1A2E; border: 1px solid #6C63FF; color: #6C63FF; }}
  #controls {{ display: flex; gap: 10px; margin-top: 8px; flex-wrap: wrap; justify-content: center; }}
  #powerup-bar {{ height: 20px; display: flex; align-items: center; gap: 8px; margin-bottom: 4px; font-size: 0.8rem; }}
  #powerup-bar div {{ background: #1A1A2E; padding: 2px 10px; border-radius: 12px; display: none; }}
  /* ── Fullscreen button ── */
  #fsBtn {{
    position: fixed; top: 12px; right: 12px; z-index: 999;
    background: rgba(108,99,255,0.85); color: #fff;
    border: none; border-radius: 8px;
    width: 36px; height: 36px; font-size: 1rem;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    backdrop-filter: blur(4px);
    transition: background 0.2s, transform 0.15s;
    box-shadow: 0 2px 10px rgba(0,0,0,0.4);
  }}
  #fsBtn:hover {{ background: #857df7; transform: scale(1.1); }}
  /* Fullscreen canvas fill */
  :fullscreen #canvas-wrap {{ display: flex; align-items: center; justify-content: center; }}
  :fullscreen body {{ justify-content: center; }}
</style>
</head>
<body>
<h2>🐍 Snake Game</h2>
<div id="hud">
  <div class="hud-item">Score: <span id="scoreDisplay">0</span></div>
  <div class="hud-item">Best: <span id="highDisplay">{high_score}</span></div>
  <div class="hud-item">Level: <span id="levelDisplay">1</span></div>
  <div class="hud-item">Player: <span>{safe_name}</span></div>
</div>
<div id="powerup-bar">
  <div id="pu-speed" style="color:#FFD700;">⚡ Speed</div>
  <div id="pu-shield" style="color:#4FC3F7;">🛡 Shield</div>
  <div id="pu-double" style="color:#69F0AE;">2x Pts</div>
</div>
<div id="canvas-wrap">
  <canvas id="gameCanvas" width="600" height="500" tabindex="0"></canvas>
  <div id="overlay">
    <h3>🐍 Snake Game</h3>
    <p>Player: <strong>{safe_name}</strong> | High Score: <strong>{high_score}</strong></p>
    <p style="color:#888; font-size:0.8rem;">Arrow Keys / WASD to move • P to pause</p>
    <button class="btn" onclick="startGame()">▶ Start Game</button>
  </div>
</div>
<button id="fsBtn" title="Toggle Fullscreen" onclick="toggleFS()">⛶</button>
<div id="controls">
  <button class="btn secondary" onclick="togglePause()" id="pauseBtn">⏸ Pause</button>
  <button class="btn secondary" onclick="toggleWalls()" id="wallBtn">🧱 Walls: OFF</button>
  <button class="btn secondary" onclick="restartGame()">🔄 Restart</button>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const CELL = 20;
const COLS = canvas.width / CELL;   // 30
const ROWS = canvas.height / CELL;  // 25
const BASE_FPS = 10;
const MAX_FPS = 20;

let snake, dir, nextDir, food, superFood, powerUps;
let score, highScore, level, combo;
let gameLoop, fps, gameRunning, paused, wallsOn;
let powerUpTimers = {{speed: 0, shield: 0, double: 0}};
let dirQueue = [];
let lastDir = {{x:1, y:0}};

// Audio
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let actx;
function getAudioCtx() {{
  if (!actx) actx = new AudioCtx();
  return actx;
}}
function beep(freq=440, dur=0.08, type='square', vol=0.1) {{
  try {{
    const ac = getAudioCtx();
    const osc = ac.createOscillator();
    const gain = ac.createGain();
    osc.connect(gain); gain.connect(ac.destination);
    osc.type = type; osc.frequency.value = freq;
    gain.gain.setValueAtTime(vol, ac.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + dur);
    osc.start(); osc.stop(ac.currentTime + dur);
  }} catch(e) {{}}
}}

function initState() {{
  snake = [{{x:15, y:12}}, {{x:14, y:12}}, {{x:13, y:12}}];
  dir = {{x:1, y:0}}; lastDir = {{x:1, y:0}};
  nextDir = null; dirQueue = [];
  score = 0; level = 1; combo = 0; fps = BASE_FPS;
  powerUpTimers = {{speed:0, shield:0, double:0}};
  powerUps = [];
  wallsOn = document.getElementById('wallBtn').textContent.includes('ON');
  spawnFood(); superFood = null;
  updateHUD();
}}

function spawnFood() {{
  let pos;
  do {{ pos = {{x: randInt(0,COLS-1), y: randInt(0,ROWS-1)}}; }}
  while (onSnake(pos) || (superFood && samePos(pos, superFood)));
  food = pos;
}}

function spawnSuperFood() {{
  let pos;
  do {{ pos = {{x: randInt(0,COLS-1), y: randInt(0,ROWS-1)}}; }}
  while (onSnake(pos) || samePos(pos, food));
  superFood = {{...pos, flash: 0, ttl: fps * 8}};
}}

function spawnPowerUp(type) {{
  let pos;
  let tries = 0;
  do {{ pos = {{x: randInt(0,COLS-1), y: randInt(0,ROWS-1)}}; tries++; }}
  while (tries < 50 && (onSnake(pos) || samePos(pos, food) || powerUps.some(p => samePos(p, pos))));
  powerUps.push({{...pos, type, ttl: fps * 10}});
}}

function onSnake(pos) {{ return snake.some(s => samePos(s, pos)); }}
function samePos(a, b) {{ return a && b && a.x === b.x && a.y === b.y; }}
function randInt(min, max) {{ return Math.floor(Math.random()*(max-min+1))+min; }}

function startGame() {{
  document.getElementById('overlay').style.display = 'none';
  initState();
  gameRunning = true; paused = false;
  canvas.focus();
  scheduleLoop();
}}

function scheduleLoop() {{
  if (gameLoop) clearTimeout(gameLoop);
  if (!gameRunning || paused) return;
  const delay = 1000 / fps;
  gameLoop = setTimeout(() => {{ tick(); scheduleLoop(); }}, delay);
}}

function restartGame() {{
  clearTimeout(gameLoop);
  gameRunning = false;
  document.getElementById('overlay').style.display = 'none';
  initState();
  gameRunning = true; paused = false;
  canvas.focus();
  scheduleLoop();
}}

function togglePause() {{
  if (!gameRunning) return;
  paused = !paused;
  document.getElementById('pauseBtn').textContent = paused ? '▶ Resume' : '⏸ Pause';
  if (!paused) scheduleLoop();
  else {{ clearTimeout(gameLoop); drawPauseScreen(); }}
}}

function toggleWalls() {{
  wallsOn = !wallsOn;
  document.getElementById('wallBtn').textContent = '🧱 Walls: ' + (wallsOn ? 'ON' : 'OFF');
}}

function tick() {{
  // Consume direction queue
  if (dirQueue.length > 0) {{
    const candidate = dirQueue.shift();
    if (candidate.x !== -lastDir.x || candidate.y !== -lastDir.y) {{
      dir = candidate; lastDir = candidate;
    }}
  }}

  // Move
  const head = {{x: snake[0].x + dir.x, y: snake[0].y + dir.y}};

  // Wall check
  if (wallsOn) {{
    if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS) {{ gameOver(); return; }}
  }} else {{
    head.x = (head.x + COLS) % COLS;
    head.y = (head.y + ROWS) % ROWS;
  }}

  // Self collision
  if (onSnake(head)) {{ gameOver(); return; }}

  snake.unshift(head);

  let grew = false;
  let pts = 0;

  // Normal food
  if (samePos(head, food)) {{
    pts = powerUpTimers.double > 0 ? 20 : 10;
    combo++;
    beep(600, 0.06, 'square', 0.08);
    spawnFood();
    if (score % 50 === 0) spawnSuperFood();
    if (Math.random() < 0.2) {{
      const types = ['speed','shield','double'];
      spawnPowerUp(types[randInt(0,2)]);
    }}
    grew = true;
  }}

  // Super food
  if (superFood && samePos(head, superFood)) {{
    pts = powerUpTimers.double > 0 ? 60 : 30;
    combo += 2;
    beep(880, 0.1, 'sine', 0.12);
    superFood = null;
    grew = true;
  }}

  // Power-ups
  powerUps = powerUps.filter(p => {{
    if (samePos(head, p)) {{
      powerUpTimers[p.type] = fps * 5;
      beep(1200, 0.08, 'triangle', 0.1);
      updatePowerUpBar();
      return false;
    }}
    return true;
  }});

  // Power-up TTL
  powerUps = powerUps.map(p => ({{...p, ttl: p.ttl - 1}})).filter(p => p.ttl > 0);
  Object.keys(powerUpTimers).forEach(k => {{
    if (powerUpTimers[k] > 0) {{
      powerUpTimers[k]--;
      if (powerUpTimers[k] === 0) updatePowerUpBar();
    }}
  }});

  // Super food TTL
  if (superFood) {{
    superFood.ttl--;
    superFood.flash++;
    if (superFood.ttl <= 0) superFood = null;
  }}

  if (!grew) snake.pop();

  if (pts) {{
    score += pts * (combo >= 3 ? Math.floor(combo/3) : 1);
    if (score > highScore) highScore = score;
    // Level up
    level = Math.floor(score / 100) + 1;
    fps = Math.min(BASE_FPS + level - 1, MAX_FPS);
    updateHUD();
  }}

  draw();
}}

function draw() {{
  // Background
  ctx.fillStyle = '#0E0E1A';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Grid dots
  ctx.fillStyle = 'rgba(108,99,255,0.06)';
  for (let x = 0; x < COLS; x++) for (let y = 0; y < ROWS; y++) {{
    ctx.fillRect(x*CELL+CELL/2-1, y*CELL+CELL/2-1, 2, 2);
  }}

  // Snake
  snake.forEach((seg, i) => {{
    const alpha = powerUpTimers.shield > 0 ? 0.5 : 1;
    ctx.globalAlpha = alpha;
    const g = ctx.createRadialGradient(
      seg.x*CELL+CELL/2, seg.y*CELL+CELL/2, 2,
      seg.x*CELL+CELL/2, seg.y*CELL+CELL/2, CELL/2
    );
    if (i === 0) {{
      g.addColorStop(0, '#6C63FF'); g.addColorStop(1, '#857df7');
    }} else {{
      const fade = 1 - i/snake.length*0.6;
      g.addColorStop(0, `rgba(108,99,255,${{fade}})`);
      g.addColorStop(1, `rgba(60,52,180,${{fade*0.7}})`);
    }}
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.roundRect(seg.x*CELL+1, seg.y*CELL+1, CELL-2, CELL-2, 4);
    ctx.fill();
    ctx.globalAlpha = 1;
  }});

  // Eyes on head
  const h = snake[0];
  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.arc(h.x*CELL+6+dir.x*2, h.y*CELL+6+dir.y*2, 3, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(h.x*CELL+14+dir.x*2, h.y*CELL+6+dir.y*2, 3, 0, Math.PI*2); ctx.fill();
  ctx.fillStyle = '#0E0E1A';
  ctx.beginPath(); ctx.arc(h.x*CELL+6+dir.x*3, h.y*CELL+6+dir.y*3, 1.5, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(h.x*CELL+14+dir.x*3, h.y*CELL+6+dir.y*3, 1.5, 0, Math.PI*2); ctx.fill();

  // Food
  ctx.fillStyle = '#FF5252';
  ctx.shadowBlur = 12; ctx.shadowColor = '#FF5252';
  ctx.beginPath();
  ctx.arc(food.x*CELL+CELL/2, food.y*CELL+CELL/2, CELL/2-2, 0, Math.PI*2);
  ctx.fill();
  ctx.shadowBlur = 0;

  // Super food (flashing)
  if (superFood && superFood.flash % 6 < 4) {{
    ctx.fillStyle = '#FF1744';
    ctx.shadowBlur = 18; ctx.shadowColor = '#FF1744';
    ctx.beginPath();
    ctx.arc(superFood.x*CELL+CELL/2, superFood.y*CELL+CELL/2, CELL/2, 0, Math.PI*2);
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 10px sans-serif'; ctx.textAlign = 'center';
    ctx.fillText('★', superFood.x*CELL+CELL/2, superFood.y*CELL+CELL/2+4);
  }}

  // Power-ups
  powerUps.forEach(p => {{
    const colors = {{speed:'#FFD700', shield:'#4FC3F7', double:'#69F0AE'}};
    const icons = {{speed:'⚡', shield:'🛡', double:'2x'}};
    ctx.fillStyle = colors[p.type];
    ctx.shadowBlur = 10; ctx.shadowColor = colors[p.type];
    ctx.beginPath();
    ctx.roundRect(p.x*CELL+1, p.y*CELL+1, CELL-2, CELL-2, 6);
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.font = '11px sans-serif'; ctx.textAlign = 'center';
    ctx.fillText(icons[p.type], p.x*CELL+CELL/2, p.y*CELL+CELL/2+4);
  }});
}}

function drawPauseScreen() {{
  draw();
  ctx.fillStyle = 'rgba(14,14,26,0.7)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#6C63FF';
  ctx.font = 'bold 2rem Segoe UI';
  ctx.textAlign = 'center';
  ctx.fillText('⏸ PAUSED', canvas.width/2, canvas.height/2);
  ctx.fillStyle = '#888';
  ctx.font = '1rem Segoe UI';
  ctx.fillText('Press P or click Resume', canvas.width/2, canvas.height/2+36);
}}

function gameOver() {{
  clearTimeout(gameLoop);
  gameRunning = false;
  beep(200, 0.3, 'sawtooth', 0.15);

  const ov = document.getElementById('overlay');
  ov.innerHTML = `
    <h3 style="color:#FF5252">💀 Game Over!</h3>
    <p>Score: <strong style="color:#6C63FF;font-size:1.4rem">${{score.toLocaleString()}}</strong></p>
    <p>High Score: <strong>${{highScore.toLocaleString()}}</strong></p>
    <p style="color:#888;font-size:0.8rem">Level ${{level}} reached</p>
    <button class="btn" onclick="sendScore()">💾 Save Score</button>
    <button class="btn secondary" onclick="restartGame()">🔄 Play Again</button>
  `;
  ov.style.display = 'flex';
}}

function sendScore() {{
  window.parent.postMessage({{type:'score', game:'snake', value: score, player:'{safe_name}'}}, '*');
  document.querySelector('#overlay .btn').textContent = '✅ Score Saved!';
  document.querySelector('#overlay .btn').disabled = true;
}}

function updateHUD() {{
  document.getElementById('scoreDisplay').textContent = score.toLocaleString();
  document.getElementById('highDisplay').textContent = highScore.toLocaleString();
  document.getElementById('levelDisplay').textContent = level;
}}

function updatePowerUpBar() {{
  ['speed','shield','double'].forEach(k => {{
    const el = document.getElementById('pu-'+k);
    el.style.display = powerUpTimers[k] > 0 ? 'block' : 'none';
  }});
}}

// Keyboard
document.addEventListener('keydown', e => {{
  const map = {{
    ArrowUp:    {{x:0,y:-1}}, w: {{x:0,y:-1}}, W: {{x:0,y:-1}},
    ArrowDown:  {{x:0,y:1}},  s: {{x:0,y:1}},  S: {{x:0,y:1}},
    ArrowLeft:  {{x:-1,y:0}}, a: {{x:-1,y:0}}, A: {{x:-1,y:0}},
    ArrowRight: {{x:1,y:0}},  d: {{x:1,y:0}},  D: {{x:1,y:0}},
  }};
  if (map[e.key]) {{
    e.preventDefault();
    if (gameRunning && !paused) dirQueue.push(map[e.key]);
  }}
  if (e.key === 'p' || e.key === 'P') togglePause();
}});

// Touch swipe
let touchStart = null;
canvas.addEventListener('touchstart', e => {{ e.preventDefault(); touchStart = e.touches[0]; }}, {{passive:false}});
canvas.addEventListener('touchend', e => {{
  e.preventDefault();
  if (!touchStart) return;
  const dx = e.changedTouches[0].clientX - touchStart.clientX;
  const dy = e.changedTouches[0].clientY - touchStart.clientY;
  if (Math.abs(dx) > Math.abs(dy)) dirQueue.push(dx > 0 ? {{x:1,y:0}} : {{x:-1,y:0}});
  else dirQueue.push(dy > 0 ? {{x:0,y:1}} : {{x:0,y:-1}});
  touchStart = null;
}}, {{passive:false}});

// Click to focus
canvas.addEventListener('click', () => canvas.focus());

// ── Fullscreen ────────────────────────────────────────────────────────────
function toggleFS() {{
  const btn = document.getElementById('fsBtn');
  if (!document.fullscreenElement) {{
    document.documentElement.requestFullscreen().catch(() => {{}});
  }} else {{
    document.exitFullscreen().catch(() => {{}});
  }}
}}
document.addEventListener('fullscreenchange', () => {{
  const btn = document.getElementById('fsBtn');
  if (document.fullscreenElement) {{
    btn.textContent = '✕';
    btn.title = 'Exit Fullscreen';
    canvas.focus();
  }} else {{
    btn.textContent = '⛶';
    btn.title = 'Toggle Fullscreen';
  }}
}});

// Init variables
highScore = {high_score};
</script>
</body>
</html>"""
