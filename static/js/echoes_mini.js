/**
 * Echoes of Coherence — Mini Browser Edition
 * Semantic Coherence Dynamics (SCD) roguelite
 * Embedded alongside the TOT assessment.
 *
 * Click the canvas to activate. WASD to move. SPACE to interact.
 * Reach coherence ≥ 60%, collect 2 shards, then reach the Core (white tile).
 */
(function () {
  "use strict";

  const COLS = 20, ROWS = 13, CELL = 22;
  const CW = COLS * CELL, CH = ROWS * CELL;

  const T = { STABLE: 0, VOID: 1, CHAOS: 2, LANDMARK: 3, CORE: 4, FLUX: 5 };

  const TILE_BG = {
    [T.STABLE]:   "#0d2118",
    [T.VOID]:     "#0a1228",
    [T.CHAOS]:    "#1a0a28",
    [T.LANDMARK]: "#221800",
    [T.CORE]:     "#1a1a0d",
    [T.FLUX]:     "#111820",
  };
  const TILE_FG = {
    [T.STABLE]:   "#22c55e",
    [T.VOID]:     "#3b82f6",
    [T.CHAOS]:    "#a855f7",
    [T.LANDMARK]: "#eab308",
    [T.CORE]:     "#fafafa",
    [T.FLUX]:     "#475569",
  };
  const TILE_LABEL = {
    [T.STABLE]:   "Stable",
    [T.VOID]:     "Void",
    [T.CHAOS]:    "Chaos",
    [T.LANDMARK]: "Shard",
    [T.CORE]:     "Core",
    [T.FLUX]:     "Flux",
  };

  // SCD events: delta to [Order, Chaos, Unity, Void] per tile interaction
  const EVENTS = {
    [T.STABLE]:   [+0.14, -0.06, +0.04, -0.06],
    [T.VOID]:     [-0.12, +0.05, -0.07, +0.20],
    [T.CHAOS]:    [-0.07, +0.20, -0.05, +0.07],
    [T.LANDMARK]: [+0.05, -0.10, +0.18, -0.06],
    [T.FLUX]:     [+0.03, -0.02, +0.03, -0.02],
    [T.CORE]:     [0, 0, 0, 0],
  };
  const COSTS = {
    [T.STABLE]: -1, [T.VOID]: -10, [T.CHAOS]: -6,
    [T.LANDMARK]: 0, [T.CORE]: 0, [T.FLUX]: -1,
  };
  const MOVE_COSTS = {
    [T.STABLE]: 0, [T.VOID]: -3, [T.CHAOS]: -2,
    [T.LANDMARK]: 0, [T.CORE]: 0, [T.FLUX]: 0,
  };

  // Game state
  let world, player, mstar, budget, shards, messages, won, lost, active;
  let particles = [];
  let animFrame = null;
  let lastRender = 0;

  function init() {
    world = buildWorld();
    player = { x: 2, y: ROWS - 2, moved: false };
    // Clear spawn area
    for (let dy = -1; dy <= 1; dy++)
      for (let dx = -1; dx <= 1; dx++)
        if (inBounds(player.x + dx, player.y + dy))
          world[player.y + dy][player.x + dx] = T.STABLE;

    // Place core top-right
    world[1][COLS - 2] = T.CORE;
    // Guarantee 2 landmark shards reachable
    world[Math.floor(ROWS / 2)][Math.floor(COLS / 3)] = T.LANDMARK;
    world[Math.floor(ROWS / 3)][Math.floor(2 * COLS / 3)] = T.LANDMARK;

    mstar = [0.40, 0.20, 0.25, 0.15]; // [Order, Chaos, Unity, Void]
    budget = 100;
    shards = 0;
    messages = ["Move: WASD  Interact: SPACE  Goal: Core (top-right)"];
    won = false;
    lost = false;
    particles = [];
  }

  function buildWorld() {
    const g = [];
    for (let y = 0; y < ROWS; y++) {
      g[y] = [];
      for (let x = 0; x < COLS; x++) {
        const r = Math.random();
        if (r < 0.30)      g[y][x] = T.STABLE;
        else if (r < 0.48) g[y][x] = T.VOID;
        else if (r < 0.62) g[y][x] = T.CHAOS;
        else if (r < 0.70) g[y][x] = T.LANDMARK;
        else if (r < 0.82) g[y][x] = T.FLUX;
        else               g[y][x] = T.STABLE;
      }
    }
    // Carve a rough path from bottom-left to top-right
    let cx = 2, cy = ROWS - 2;
    while (cx < COLS - 2 || cy > 1) {
      g[cy][cx] = Math.random() < 0.7 ? T.STABLE : T.FLUX;
      if (cx < COLS - 2 && (cy <= 1 || Math.random() < 0.5)) cx++;
      else if (cy > 1) cy--;
    }
    return g;
  }

  function inBounds(x, y) {
    return x >= 0 && x < COLS && y >= 0 && y < ROWS;
  }

  function coherence() {
    return Math.max(...mstar);
  }

  function pushMsg(msg) {
    if (!msg) return;
    messages.unshift(msg);
    if (messages.length > 4) messages.pop();
  }

  function normalizeMstar() {
    const sum = mstar.reduce((a, b) => a + b, 0);
    if (sum > 0) mstar = mstar.map(v => v / sum);
  }

  function interact() {
    if (won || lost || !active) return;
    const tile = world[player.y][player.x];

    if (tile === T.CORE) {
      const c = coherence();
      if (c >= 0.60 && shards >= 2) {
        won = true;
        pushMsg("ASCENDED — You found coherence.");
        spawnParticles(player.x * CELL + CELL / 2, player.y * CELL + CELL / 2, "#5eead4", 20);
      } else {
        const missing = [];
        if (shards < 2) missing.push(`${2 - shards} more shard${2 - shards > 1 ? "s" : ""}`);
        if (c < 0.60) missing.push(`higher M* (need 60%, have ${Math.round(c * 100)}%)`);
        pushMsg("Not yet — need " + missing.join(" and "));
      }
      return;
    }

    const delta = EVENTS[tile] || [0, 0, 0, 0];
    for (let i = 0; i < 4; i++) mstar[i] = Math.max(0, mstar[i] + delta[i]);
    normalizeMstar();

    const cost = COSTS[tile] || 0;
    budget = Math.max(0, budget + cost);

    if (tile === T.LANDMARK) {
      shards++;
      world[player.y][player.x] = T.FLUX;
      pushMsg(`Shard collected! (${shards}/2) — Unity increases.`);
      spawnParticles(player.x * CELL + CELL / 2, player.y * CELL + CELL / 2, "#eab308", 12);
    } else {
      const msgs = {
        [T.STABLE]: "Stable ground — Order strengthens.",
        [T.VOID]:   `Void contact — frame destabilized. −${Math.abs(cost)} budget.`,
        [T.CHAOS]:  `Chaos floods your frame. −${Math.abs(cost)} budget.`,
        [T.FLUX]:   "Flux tile — minor adjustment.",
      };
      pushMsg(msgs[tile] || "");
    }

    if (budget <= 0) {
      lost = true;
      pushMsg("Budget depleted — frame collapsed.");
    }
    updateHUD();
  }

  function move(dx, dy) {
    if (won || lost || !active) return;
    const nx = player.x + dx, ny = player.y + dy;
    if (!inBounds(nx, ny)) return;
    player.x = nx;
    player.y = ny;
    player.moved = true;

    const tile = world[ny][nx];
    const cost = MOVE_COSTS[tile] || 0;
    if (cost) budget = Math.max(0, budget + cost);
    if (budget <= 0) { lost = true; pushMsg("Budget depleted."); }

    // Passive coherence shift from moving on tile
    const passive = {
      [T.VOID]:   [-0.02, +0.01, -0.01, +0.04],
      [T.CHAOS]:  [-0.01, +0.03, -0.01, +0.01],
      [T.STABLE]: [+0.01, -0.01, 0, 0],
    };
    if (passive[tile]) {
      for (let i = 0; i < 4; i++) mstar[i] = Math.max(0, mstar[i] + passive[tile][i]);
      normalizeMstar();
    }
    updateHUD();
  }

  // ── Particles ──────────────────────────────────────────────────────────────
  function spawnParticles(x, y, color, count) {
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const speed = 40 + Math.random() * 60;
      particles.push({
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: 1.0,
        color,
      });
    }
  }

  function updateParticles(dt) {
    particles = particles.filter(p => {
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.life -= dt * 2;
      return p.life > 0;
    });
  }

  // ── Rendering ──────────────────────────────────────────────────────────────
  function render(ctx, now) {
    const dt = Math.min((now - lastRender) / 1000, 0.1);
    lastRender = now;
    updateParticles(dt);

    ctx.fillStyle = "#0b1021";
    ctx.fillRect(0, 0, CW, CH);

    if (!active) {
      drawStartScreen(ctx);
      animFrame = requestAnimationFrame(t => render(ctx, t));
      return;
    }

    // World
    for (let y = 0; y < ROWS; y++) {
      for (let x = 0; x < COLS; x++) {
        const tile = world[y][x];
        const px = x * CELL, py = y * CELL;
        ctx.fillStyle = TILE_BG[tile] || "#111";
        ctx.fillRect(px, py, CELL, CELL);

        // Accent dot / gem
        if (tile === T.LANDMARK) {
          ctx.fillStyle = TILE_FG[tile];
          ctx.fillRect(px + 7, py + 7, 8, 8);
        } else if (tile === T.CORE) {
          ctx.strokeStyle = "#fafafa";
          ctx.lineWidth = 2;
          ctx.strokeRect(px + 3, py + 3, CELL - 6, CELL - 6);
          ctx.strokeStyle = "rgba(250,250,250,0.3)";
          ctx.lineWidth = 1;
          ctx.strokeRect(px + 6, py + 6, CELL - 12, CELL - 12);
        } else {
          ctx.fillStyle = TILE_FG[tile];
          ctx.globalAlpha = 0.25 + (Math.sin(now / 1200 + x + y) * 0.05);
          ctx.fillRect(px + 8, py + 8, 6, 6);
          ctx.globalAlpha = 1;
        }
      }
    }

    // Grid lines (subtle)
    ctx.strokeStyle = "rgba(255,255,255,0.03)";
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= COLS; x++) { ctx.beginPath(); ctx.moveTo(x * CELL, 0); ctx.lineTo(x * CELL, CH); ctx.stroke(); }
    for (let y = 0; y <= ROWS; y++) { ctx.beginPath(); ctx.moveTo(0, y * CELL); ctx.lineTo(CW, y * CELL); ctx.stroke(); }

    // Player
    const ppx = player.x * CELL + CELL / 2;
    const ppy = player.y * CELL + CELL / 2;
    const pulse = Math.sin(now / 400) * 2;

    ctx.beginPath();
    ctx.arc(ppx, ppy, 7 + pulse * 0.3, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(249,115,22,0.2)";
    ctx.fill();

    ctx.beginPath();
    ctx.arc(ppx, ppy, 7, 0, Math.PI * 2);
    ctx.fillStyle = "#f97316";
    ctx.fill();
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Coherence ring around player
    const c = coherence();
    ctx.beginPath();
    ctx.arc(ppx, ppy, 11, -Math.PI / 2, -Math.PI / 2 + c * Math.PI * 2);
    ctx.strokeStyle = c >= 0.6 ? "#5eead4" : "#38bdf8";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Particles
    for (const p of particles) {
      ctx.globalAlpha = p.life;
      ctx.fillStyle = p.color;
      ctx.fillRect(p.x - 2, p.y - 2, 4, 4);
    }
    ctx.globalAlpha = 1;

    // Overlays
    if (won || lost) {
      ctx.fillStyle = "rgba(11,16,33,0.88)";
      ctx.fillRect(0, 0, CW, CH);
      ctx.textAlign = "center";
      ctx.font = "bold 18px 'Space Grotesk', sans-serif";
      ctx.fillStyle = won ? "#5eead4" : "#ef4444";
      ctx.fillText(won ? "ASCENDED" : "COLLAPSED", CW / 2, CH / 2 - 12);
      ctx.font = "12px 'Space Grotesk', sans-serif";
      ctx.fillStyle = "#9fb0c5";
      ctx.fillText("Press R to restart", CW / 2, CH / 2 + 12);
      ctx.textAlign = "left";
    }

    animFrame = requestAnimationFrame(t => render(ctx, t));
  }

  function drawStartScreen(ctx) {
    const pulse = (Math.sin(Date.now() / 700) + 1) / 2;
    ctx.textAlign = "center";
    ctx.fillStyle = "#5eead4";
    ctx.font = "bold 15px 'Space Grotesk', sans-serif";
    ctx.fillText("Echoes of Coherence", CW / 2, CH / 2 - 28);
    ctx.fillStyle = "#9fb0c5";
    ctx.font = "11px 'Space Grotesk', sans-serif";
    ctx.fillText("A game of meaning and stability", CW / 2, CH / 2 - 10);
    ctx.fillStyle = `rgba(56,189,248,${0.6 + pulse * 0.4})`;
    ctx.font = "bold 13px 'Space Grotesk', sans-serif";
    ctx.fillText("Click to play", CW / 2, CH / 2 + 16);
    ctx.textAlign = "left";
  }

  function updateHUD() {
    const hud = document.getElementById("eoc-hud");
    if (!hud) return;
    const c = coherence();
    const cPct = Math.round(c * 100);
    const bPct = Math.round(budget);
    const labels = ["Order", "Chaos", "Unity", "Void"];
    const mstarBars = mstar.map((v, i) =>
      `<div class="eoc-mbar" title="${labels[i]}">
        <span class="eoc-mlabel">${labels[i][0]}</span>
        <div class="eoc-mfill" style="width:${Math.round(v * 100)}%;background:${["#38bdf8","#a855f7","#5eead4","#6b7280"][i]}"></div>
        <span class="eoc-mval">${Math.round(v * 100)}%</span>
      </div>`
    ).join("");

    hud.innerHTML = `
      <div class="eoc-stat-row">
        <div class="eoc-stat">
          <span class="eoc-label">M* ${cPct >= 60 ? "✓" : ""}</span>
          <div class="eoc-bar"><div class="eoc-fill" style="width:${cPct}%;background:${c >= 0.6 ? "#5eead4" : "#38bdf8"}"></div></div>
          <span class="eoc-val ${c >= 0.6 ? "eoc-val-good" : ""}">${cPct}%</span>
        </div>
        <div class="eoc-stat">
          <span class="eoc-label">Budget</span>
          <div class="eoc-bar"><div class="eoc-fill" style="width:${bPct}%;background:${bPct > 50 ? "#22c55e" : bPct > 25 ? "#f59e0b" : "#ef4444"}"></div></div>
          <span class="eoc-val">${bPct}</span>
        </div>
      </div>
      <div class="eoc-mstar">${mstarBars}</div>
      <div class="eoc-tags">
        <span class="eoc-tag ${shards >= 2 ? "eoc-tag-ok" : ""}">Shards ${shards}/2</span>
        <span class="eoc-tag ${c >= 0.6 ? "eoc-tag-ok" : ""}">M* ${cPct >= 60 ? "Ready" : cPct + "%"}</span>
        <span class="eoc-tag">Reach Core →</span>
      </div>
      <div class="eoc-msg">${messages[0] || ""}</div>
    `;
  }

  // ── Public init ────────────────────────────────────────────────────────────
  window.initEchoes = function (canvasId, hudId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    canvas.width = CW;
    canvas.height = CH;
    canvas.setAttribute("tabIndex", "0");
    canvas.style.outline = "none";
    canvas.style.cursor = "pointer";

    const ctx = canvas.getContext("2d");
    active = false;
    init();

    canvas.addEventListener("click", () => {
      if (!active) { active = true; canvas.style.cursor = "default"; }
    });

    canvas.addEventListener("keydown", e => {
      switch (e.key) {
        case "ArrowUp":    case "w": case "W": e.preventDefault(); move(0, -1); break;
        case "ArrowDown":  case "s": case "S": e.preventDefault(); move(0, 1);  break;
        case "ArrowLeft":  case "a": case "A": e.preventDefault(); move(-1, 0); break;
        case "ArrowRight": case "d": case "D": e.preventDefault(); move(1, 0);  break;
        case " ": e.preventDefault(); interact(); break;
        case "r": case "R": init(); active = true; break;
      }
      // Re-render immediately on input
      const now = performance.now();
      if (animFrame) cancelAnimationFrame(animFrame);
      render(ctx, now);
    });

    // Prevent scroll when game focused
    canvas.addEventListener("wheel", e => { if (active) e.preventDefault(); }, { passive: false });

    // Initial HUD
    updateHUD();

    // Start render loop
    animFrame = requestAnimationFrame(t => render(ctx, t));
  };
})();
