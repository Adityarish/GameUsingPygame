"""
games/car_game.py — Returns a self-contained HTML5 + JS Car Racing game string.
"""
from __future__ import annotations
import html


def get_car_html(player_name: str, high_score: int) -> str:
    safe_name = html.escape(player_name[:20])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Car Racing</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: #0E0E1A;
    display: flex; flex-direction: column;
    align-items: center; font-family: 'Segoe UI', sans-serif;
    color: #EAEAEA; padding: 10px; min-height: 100vh;
  }}
  h2 {{ color: #6C63FF; margin-bottom: 6px; font-size: 1.3rem; }}
  #wrap {{ display: flex; gap: 16px; align-items: flex-start; }}
  #hud {{
    display: flex; flex-direction: column; gap: 10px;
    background: #1A1A2E; padding: 14px; border-radius: 12px;
    min-width: 140px; border: 1px solid #6C63FF33;
  }}
  .hud-row {{ display: flex; flex-direction: column; }}
  .hud-label {{ font-size: 0.7rem; color: #888; text-transform: uppercase; }}
  .hud-val {{ font-size: 1.2rem; font-weight: 700; color: #6C63FF; }}
  #fuel-bar {{ width: 100%; height: 10px; background: #0E0E1A; border-radius: 5px; overflow: hidden; }}
  #fuel-fill {{ height: 100%; background: linear-gradient(90deg,#FF5252,#FFD740); border-radius: 5px; transition: width 0.2s; }}
  #lives {{ display: flex; gap: 4px; }}
  #lives span {{ font-size: 1.2rem; }}
  #nitro-indicator {{ color: #00E5FF; font-weight: bold; display: none; font-size: 0.85rem; }}
  #canvas-wrap {{ position: relative; }}
  #gameCanvas {{ border: 2px solid #6C63FF; border-radius: 8px; display: block; outline: none; box-shadow: 0 0 20px rgba(108,99,255,0.4); }}
  #overlay {{
    position: absolute; top:0; left:0; width:100%; height:100%;
    background: rgba(14,14,26,0.9); display: flex; flex-direction: column;
    align-items: center; justify-content: center; border-radius: 8px; gap: 12px;
  }}
  #overlay h3 {{ color: #6C63FF; font-size: 1.5rem; }}
  .btn {{ background: #6C63FF; color: #fff; border: none; padding: 10px 28px; border-radius: 24px; font-size: 1rem; cursor: pointer; font-weight: 600; transition: background 0.2s, transform 0.1s; }}
  .btn:hover {{ background: #857df7; transform: scale(1.04); }}
  .btn.secondary {{ background: #1A1A2E; border: 1px solid #6C63FF; color: #6C63FF; }}
  #ctrl-hint {{ color: #666; font-size: 0.78rem; text-align: center; margin-top: 6px; }}
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
  :fullscreen body {{ justify-content: center; align-items: center; }}
</style>
</head>
<body>
<h2>🏎 Car Racing</h2>
<div id="wrap">
  <div id="hud">
    <div class="hud-row"><span class="hud-label">Score</span><span class="hud-val" id="scoreDisp">0</span></div>
    <div class="hud-row"><span class="hud-label">Best</span><span class="hud-val" id="bestDisp">{high_score}</span></div>
    <div class="hud-row"><span class="hud-label">Level</span><span class="hud-val" id="levelDisp">1</span></div>
    <div class="hud-row"><span class="hud-label">Speed</span><span class="hud-val" id="speedDisp">0</span></div>
    <div class="hud-row">
      <span class="hud-label">Fuel</span>
      <div id="fuel-bar"><div id="fuel-fill" style="width:100%"></div></div>
    </div>
    <div class="hud-row"><span class="hud-label">Lives</span><div id="lives"><span>❤️</span><span>❤️</span><span>❤️</span></div></div>
    <div id="nitro-indicator">🔥 NITRO!</div>
    <div class="hud-row"><span class="hud-label">Player</span><span style="font-size:0.8rem;color:#aaa">{safe_name}</span></div>
  </div>
  <div id="canvas-wrap">
    <canvas id="gameCanvas" width="400" height="600" tabindex="0"></canvas>
    <div id="overlay">
      <h3>🏎 Car Racing</h3>
      <p style="color:#aaa">Dodge traffic, collect fuel & coins!</p>
      <p style="color:#888;font-size:0.8rem">← → Arrow Keys / A D to steer</p>
      <button class="btn" onclick="startGame()">▶ Start Race</button>
    </div>
  </div>
</div>
<button id="fsBtn" title="Toggle Fullscreen" onclick="toggleFS()">⛶</button>
<div id="ctrl-hint">← → / A D — Steer &nbsp;|&nbsp; Avoid crashes &nbsp;|&nbsp; Collect ⛽ fuel</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

// Road config
const ROAD_LEFT = 40, ROAD_RIGHT = 360, ROAD_W = 320;
const LANES = [100, 200, 300];  // lane centers
const PLAYER_W = 36, PLAYER_H = 64;
const ENEMY_W = 34, ENEMY_H = 60;

let score, highScore, level, lives, fuel, nitroActive, nitroTimer;
let playerX, playerInvincible, invTimer;
let roadOffset, roadSpeed, baseSpeed;
let enemies, coins, fuelPickups, particles;
let keys = {{}};
let gameRunning = false, paused = false;
let animId = null;
let dayNightTimer = 0, isNight = false;
let lastTime = 0;

const AudioCtx = window.AudioContext || window.webkitAudioContext;
let actx;
function getAudioCtx() {{ if (!actx) actx = new AudioCtx(); return actx; }}
function beep(f=440, d=0.08, t='square', v=0.08) {{
  try {{
    const ac = getAudioCtx(), osc = ac.createOscillator(), g = ac.createGain();
    osc.connect(g); g.connect(ac.destination);
    osc.type=t; osc.frequency.value=f;
    g.gain.setValueAtTime(v, ac.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, ac.currentTime+d);
    osc.start(); osc.stop(ac.currentTime+d);
  }} catch(e) {{}}
}}

function initState() {{
  score=0; level=1; lives=3; fuel=100; nitroActive=false; nitroTimer=0;
  playerX = W/2 - PLAYER_W/2;
  playerInvincible = false; invTimer = 0;
  roadOffset = 0; baseSpeed = 3; roadSpeed = baseSpeed;
  enemies = []; coins = []; fuelPickups = []; particles = [];
  dayNightTimer = 0; isNight = false;
  highScore = {high_score};
  spawnEnemy(); spawnCoin(); spawnFuel();
  updateHUD();
}}

function randLane() {{ return LANES[Math.floor(Math.random()*3)] - ENEMY_W/2; }}
function randCoin() {{ return LANES[Math.floor(Math.random()*3)]; }}

function spawnEnemy() {{ enemies.push({{x: randLane(), y: -ENEMY_H-10, color: randCarColor()}}); }}
function spawnCoin() {{ coins.push({{x: randCoin(), y: -30}}); }}
function spawnFuel() {{ fuelPickups.push({{x: LANES[Math.floor(Math.random()*3)], y: -40}}); }}
function randCarColor() {{
  const colors=['#FF5252','#FFD740','#69F0AE','#40C4FF','#E040FB','#FF6E40'];
  return colors[Math.floor(Math.random()*colors.length)];
}}

function startGame() {{
  document.getElementById('overlay').style.display='none';
  initState();
  gameRunning=true; paused=false;
  canvas.focus();
  if (animId) cancelAnimationFrame(animId);
  lastTime = performance.now();
  animId = requestAnimationFrame(gameFrame);
}}

function restartGame() {{
  if (animId) cancelAnimationFrame(animId);
  gameRunning=false;
  document.getElementById('overlay').style.display='none';
  initState();
  gameRunning=true; paused=false;
  canvas.focus();
  lastTime = performance.now();
  animId = requestAnimationFrame(gameFrame);
}}

function gameFrame(ts) {{
  if (!gameRunning) return;
  if (paused) {{ animId = requestAnimationFrame(gameFrame); return; }}
  const dt = Math.min((ts - lastTime)/16.67, 3); lastTime = ts;
  update(dt);
  draw();
  animId = requestAnimationFrame(gameFrame);
}}

function update(dt) {{
  // Input
  const moveSpeed = 4 * dt;
  const leftPressed = keys['ArrowLeft'] || keys['a'] || keys['A'];
  const rightPressed = keys['ArrowRight'] || keys['d'] || keys['D'];
  if (leftPressed && !rightPressed) playerX = Math.max(ROAD_LEFT+2, playerX - moveSpeed*2);
  if (rightPressed && !leftPressed) playerX = Math.min(ROAD_RIGHT - PLAYER_W - 2, playerX + moveSpeed*2);

  // Road scroll
  const currentSpeed = nitroActive ? roadSpeed * 2.2 : roadSpeed;
  roadOffset = (roadOffset + currentSpeed * dt) % 80;

  // Fuel drain
  fuel -= (nitroActive ? 0.3 : 0.1) * dt;
  if (fuel <= 0) {{ fuel = 0; if (nitroActive) {{ nitroActive=false; document.getElementById('nitro-indicator').style.display='none'; }} }}
  if (fuel <= 0 && lives <= 0) {{ gameOver(); return; }}
  if (fuel <= 0) {{
    lives--;
    fuel = 30;
    updateLivesHUD();
    if (lives <= 0) {{ gameOver(); return; }}
  }}

  // Nitro timer
  if (nitroActive) {{
    nitroTimer -= dt;
    if (nitroTimer <= 0) {{ nitroActive=false; document.getElementById('nitro-indicator').style.display='none'; }}
  }}

  // Day/night
  dayNightTimer += dt;
  if (dayNightTimer > 30*60) {{ dayNightTimer=0; isNight=!isNight; }}

  // Score
  score += Math.round(currentSpeed * 0.1 * dt);
  if (score > highScore) highScore = score;
  level = Math.floor(score/500)+1;
  roadSpeed = baseSpeed + (level-1)*0.5;

  // Enemies
  enemies.forEach(e => e.y += currentSpeed * 1.2 * dt);
  enemies = enemies.filter(e => {{
    if (e.y > H+ENEMY_H) return false;
    if (!playerInvincible && rectsCollide(playerX, H-PLAYER_H-20, PLAYER_W, PLAYER_H, e.x, e.y, ENEMY_W, ENEMY_H)) {{
      beep(150, 0.4, 'sawtooth', 0.2);
      spawnExplosion(playerX+PLAYER_W/2, H-PLAYER_H-20+PLAYER_H/2);
      lives--;
      updateLivesHUD();
      playerInvincible=true; invTimer=120;
      if (lives <= 0) {{ gameOver(); return false; }}
      return false;
    }}
    return true;
  }});
  if (Math.random() < 0.015 * dt) spawnEnemy();

  // Coins
  coins.forEach(c => c.y += currentSpeed * dt);
  coins = coins.filter(c => {{
    if (c.y > H+30) return false;
    if (circleRectCollide(c.x, c.y+15, 12, playerX, H-PLAYER_H-20, PLAYER_W, PLAYER_H)) {{
      score += 5; beep(1000, 0.05, 'sine', 0.07); return false;
    }}
    return true;
  }});
  if (Math.random() < 0.02 * dt) spawnCoin();

  // Fuel pickups
  fuelPickups.forEach(f2 => f2.y += currentSpeed * dt);
  fuelPickups = fuelPickups.filter(f2 => {{
    if (f2.y > H+40) return false;
    if (circleRectCollide(f2.x, f2.y+20, 16, playerX, H-PLAYER_H-20, PLAYER_W, PLAYER_H)) {{
      fuel = Math.min(100, fuel+35);
      beep(600, 0.1, 'triangle', 0.1);
      // Check for nitro (if fuel was already full → nitro)
      if (fuel >= 100 && !nitroActive) {{
        nitroActive=true; nitroTimer=120;
        document.getElementById('nitro-indicator').style.display='block';
        beep(1400, 0.15, 'triangle', 0.12);
      }}
      return false;
    }}
    return true;
  }});
  if (Math.random() < 0.008 * dt) spawnFuel();

  // Particles
  particles = particles.filter(p => {{
    p.x += p.vx*dt; p.y += p.vy*dt; p.life-=dt; p.vy+=0.3*dt;
    return p.life > 0;
  }});

  // Invincibility
  if (playerInvincible) {{ invTimer-=dt; if(invTimer<=0) playerInvincible=false; }}

  updateHUD();
}}

function rectsCollide(ax,ay,aw,ah, bx,by,bw,bh) {{
  return ax<bx+bw && ax+aw>bx && ay<by+bh && ay+ah>by;
}}
function circleRectCollide(cx,cy,cr, rx,ry,rw,rh) {{
  const nx=Math.max(rx,Math.min(cx,rx+rw)), ny=Math.max(ry,Math.min(cy,ry+rh));
  return (cx-nx)**2+(cy-ny)**2 < cr**2;
}}

function spawnExplosion(x,y) {{
  for(let i=0;i<20;i++) {{
    const a=Math.random()*Math.PI*2, s=Math.random()*4+1;
    particles.push({{x, y, vx:Math.cos(a)*s, vy:Math.sin(a)*s-2,
      life:30+Math.random()*30, color:`hsl(${{Math.random()*40+10}},100%,60%)`}});
  }}
}}

function draw() {{
  // Sky
  if (isNight) {{
    const skyGrad = ctx.createLinearGradient(0,0,0,H);
    skyGrad.addColorStop(0,'#050512'); skyGrad.addColorStop(1,'#0E0E2A');
    ctx.fillStyle=skyGrad;
  }} else {{
    const skyGrad = ctx.createLinearGradient(0,0,0,H/3);
    skyGrad.addColorStop(0,'#1a2a4a'); skyGrad.addColorStop(1,'#2a3a5a');
    ctx.fillStyle=skyGrad;
  }}
  ctx.fillRect(0,0,W,H);

  // Road
  ctx.fillStyle = isNight ? '#1a1a1a' : '#2a2a2a';
  ctx.fillRect(ROAD_LEFT,0,ROAD_W,H);

  // Road edges
  ctx.fillStyle = isNight ? '#888' : '#fff';
  ctx.fillRect(ROAD_LEFT,0,4,H);
  ctx.fillRect(ROAD_RIGHT-4,0,4,H);

  // Lane markings
  ctx.strokeStyle = isNight ? 'rgba(255,255,255,0.25)' : 'rgba(255,255,255,0.35)';
  ctx.setLineDash([40,40]); ctx.lineWidth=3;
  [150,250].forEach(lx => {{
    ctx.beginPath();
    for(let y=-80+roadOffset;y<H+80;y+=80) {{
      ctx.moveTo(lx,y); ctx.lineTo(lx,y+40);
    }}
    ctx.stroke();
  }});
  ctx.setLineDash([]);

  // Stars (night)
  if (isNight) {{
    ctx.fillStyle='#fff';
    for(let i=0;i<30;i++) {{
      ctx.beginPath(); ctx.arc(15+i*13, 20+(i%7)*18, 1, 0, Math.PI*2); ctx.fill();
    }}
  }}

  // Enemies
  enemies.forEach(e => drawCar(e.x,e.y,ENEMY_W,ENEMY_H,e.color,false));

  // Fuel pickups
  fuelPickups.forEach(f2 => {{
    ctx.fillStyle='#FFD740'; ctx.shadowBlur=10; ctx.shadowColor='#FFD740';
    ctx.beginPath(); ctx.roundRect(f2.x-18,f2.y,36,32,6); ctx.fill();
    ctx.shadowBlur=0;
    ctx.fillStyle='#0E0E1A'; ctx.font='bold 14px sans-serif'; ctx.textAlign='center';
    ctx.fillText('⛽',f2.x,f2.y+22);
  }});

  // Coins
  coins.forEach(c => {{
    ctx.fillStyle='#FFD740'; ctx.shadowBlur=8; ctx.shadowColor='#FFD740';
    ctx.beginPath(); ctx.arc(c.x,c.y+15,12,0,Math.PI*2); ctx.fill();
    ctx.shadowBlur=0;
    ctx.fillStyle='#0E0E1A'; ctx.font='bold 11px sans-serif'; ctx.textAlign='center';
    ctx.fillText('$',c.x,c.y+19);
  }});

  // Particles
  particles.forEach(p => {{
    ctx.globalAlpha = p.life/60;
    ctx.fillStyle=p.color;
    ctx.beginPath(); ctx.arc(p.x,p.y,4,0,Math.PI*2); ctx.fill();
  }});
  ctx.globalAlpha=1;

  // Player car
  if (!playerInvincible || Math.floor(invTimer)%8 > 3) {{
    drawCar(playerX, H-PLAYER_H-20, PLAYER_W, PLAYER_H, '#6C63FF', true);
    if (nitroActive) {{
      ctx.fillStyle='rgba(0,229,255,0.3)';
      ctx.fillRect(playerX-4, H-PLAYER_H-20, PLAYER_W+8, PLAYER_H);
    }}
  }}

  // Speed-o-meter
  drawSpeedometer(W-55, 55, 40, Math.min((roadSpeed/8)*100, 100));
}}

function drawCar(x,y,w,h,color,isPlayer) {{
  // Body
  const grad = ctx.createLinearGradient(x,y,x+w,y);
  grad.addColorStop(0, color);
  grad.addColorStop(1, shadeColor(color,-40));
  ctx.fillStyle=grad;
  ctx.beginPath(); ctx.roundRect(x,y+h*0.2,w,h*0.6,5); ctx.fill();

  // Top
  ctx.fillStyle=shadeColor(color,20);
  ctx.beginPath(); ctx.roundRect(x+4,y+h*0.05,w-8,h*0.35,4); ctx.fill();

  // Windows
  ctx.fillStyle='rgba(100,200,255,0.55)';
  ctx.beginPath(); ctx.roundRect(x+6,y+h*0.1,w-12,h*0.25,3); ctx.fill();

  // Wheels
  ctx.fillStyle='#111';
  [[x-4,y+h*0.2],[x+w-4,y+h*0.2],[x-4,y+h*0.65],[x+w-4,y+h*0.65]].forEach(([wx,wy]) => {{
    ctx.beginPath(); ctx.roundRect(wx,wy,8,16,3); ctx.fill();
    ctx.fillStyle='#444'; ctx.beginPath(); ctx.arc(wx+4,wy+8,4,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='#111';
  }});

  // Headlights / taillights
  if (isPlayer) {{
    ctx.fillStyle='rgba(255,255,200,0.9)'; ctx.shadowBlur=10; ctx.shadowColor='#ffffc0';
    ctx.beginPath(); ctx.ellipse(x+7,y+h*0.82,5,3,0,0,Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(x+w-7,y+h*0.82,5,3,0,0,Math.PI*2); ctx.fill();
  }} else {{
    ctx.fillStyle='rgba(255,80,80,0.9)'; ctx.shadowBlur=6; ctx.shadowColor='#ff5050';
    ctx.beginPath(); ctx.ellipse(x+6,y+h*0.15,5,3,0,0,Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(x+w-6,y+h*0.15,5,3,0,0,Math.PI*2); ctx.fill();
  }}
  ctx.shadowBlur=0;
}}

function drawSpeedometer(cx,cy,r,pct) {{
  ctx.strokeStyle='#333'; ctx.lineWidth=6;
  ctx.beginPath(); ctx.arc(cx,cy,r,Math.PI*0.75,Math.PI*2.25); ctx.stroke();
  const angle = Math.PI*0.75 + (pct/100)*Math.PI*1.5;
  const spGrad = ctx.createLinearGradient(cx-r,cy,cx+r,cy);
  spGrad.addColorStop(0,'#69F0AE'); spGrad.addColorStop(0.5,'#FFD740'); spGrad.addColorStop(1,'#FF5252');
  ctx.strokeStyle=spGrad; ctx.lineWidth=5;
  ctx.beginPath(); ctx.arc(cx,cy,r,Math.PI*0.75,angle); ctx.stroke();
  ctx.fillStyle='#EAEAEA'; ctx.font='bold 9px sans-serif'; ctx.textAlign='center';
  ctx.fillText(Math.round(pct)+'%',cx,cy+4);
}}

function shadeColor(col, amt) {{
  const n=parseInt(col.slice(1),16);
  const r=Math.min(255,Math.max(0,((n>>16)&0xff)+amt));
  const g=Math.min(255,Math.max(0,((n>>8)&0xff)+amt));
  const b=Math.min(255,Math.max(0,(n&0xff)+amt));
  return '#'+((r<<16)|(g<<8)|b).toString(16).padStart(6,'0');
}}

function updateHUD() {{
  document.getElementById('scoreDisp').textContent = score.toLocaleString();
  document.getElementById('bestDisp').textContent = highScore.toLocaleString();
  document.getElementById('levelDisp').textContent = level;
  document.getElementById('speedDisp').textContent = Math.round(roadSpeed*10);
  document.getElementById('fuel-fill').style.width = fuel+'%';
  document.getElementById('fuel-fill').style.background =
    fuel > 50 ? 'linear-gradient(90deg,#69F0AE,#00E5FF)' :
    fuel > 20 ? 'linear-gradient(90deg,#FFD740,#FF9800)' :
                'linear-gradient(90deg,#FF5252,#FF1744)';
}}

function updateLivesHUD() {{
  const el = document.getElementById('lives');
  el.innerHTML = '';
  for (let i=0;i<3;i++) el.innerHTML += `<span>${{i<lives?'❤️':'🖤'}}</span>`;
}}

function gameOver() {{
  gameRunning=false;
  if (animId) cancelAnimationFrame(animId);
  beep(150,0.5,'sawtooth',0.2);
  const ov=document.getElementById('overlay');
  ov.innerHTML=`
    <h3 style="color:#FF5252">💥 Game Over!</h3>
    <p>Score: <strong style="color:#6C63FF;font-size:1.4rem">${{score.toLocaleString()}}</strong></p>
    <p>Best: <strong>${{highScore.toLocaleString()}}</strong> | Level: <strong>${{level}}</strong></p>
    <button class="btn" onclick="sendScore()">💾 Save Score</button>
    <button class="btn secondary" onclick="restartGame()">🔄 Play Again</button>
  `;
  ov.style.display='flex';
}}

function sendScore() {{
  window.parent.postMessage({{type:'score',game:'car',value:score,player:'{safe_name}'}}, '*');
  document.querySelector('#overlay .btn').textContent='✅ Score Saved!';
  document.querySelector('#overlay .btn').disabled=true;
}}

// Keyboard
window.addEventListener('keydown', e => {{
  keys[e.key]=true;
  if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown',' '].includes(e.key)) e.preventDefault();
}});
window.addEventListener('keyup', e => {{ keys[e.key]=false; }});

// Tab/focus pause
window.addEventListener('blur', () => {{ paused=true; }});
window.addEventListener('focus', () => {{ if (gameRunning) {{ paused=false; }} }});

// Touch
let touchStartX=null;
canvas.addEventListener('touchstart', e=>{{ e.preventDefault(); touchStartX=e.touches[0].clientX; }}, {{passive:false}});
canvas.addEventListener('touchend', e=>{{
  e.preventDefault();
  if(!touchStartX) return;
  const dx=e.changedTouches[0].clientX-touchStartX;
  if (Math.abs(dx) < 10) {{ /* tap = nitro */ if(!nitroActive&&fuel>20){{nitroActive=true;nitroTimer=60;document.getElementById('nitro-indicator').style.display='block';}} }}
  else if (dx<0) keys['ArrowLeft']=true, setTimeout(()=>{{keys['ArrowLeft']=false;}},120);
  else keys['ArrowRight']=true, setTimeout(()=>{{keys['ArrowRight']=false;}},120);
  touchStartX=null;
}},{{passive:false}});

canvas.addEventListener('click',()=>canvas.focus());
highScore={high_score};

// ── Fullscreen ─────────────────────────────────────────────────────
function toggleFS() {{
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
</script>
</body>
</html>"""
