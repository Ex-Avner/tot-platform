/**
 * Echoes of Coherence — Campaign Edition
 * A game of semantic stability set in the world of Triaxial Orientation Theory.
 *
 * Five levels. A story. Clear rules.
 * Click canvas to activate · WASD/Arrows move · SPACE interact · R restart level
 */
(function () {
  "use strict";

  // ─── Layout ────────────────────────────────────────────────────────────────
  const COLS = 20, ROWS = 13, CELL = 22;
  const CW = COLS * CELL, CH = ROWS * CELL; // 440 × 286

  // ─── Tile Definitions ──────────────────────────────────────────────────────
  const T = { STABLE:0, FLUX:1, CHAOS:2, VOID:3, ECHO:4, ANCHOR:5, NEXUS:6, WALL:7 };
  const CHAR_MAP = {
    '.':T.STABLE, '~':T.FLUX, 'X':T.CHAOS, 'V':T.VOID,
    '*':T.ECHO,   'A':T.ANCHOR,'N':T.NEXUS, '#':T.WALL
  };

  const TILE_BG = {
    [T.STABLE]:'#091a10', [T.FLUX]:'#0c111e', [T.CHAOS]:'#160720',
    [T.VOID]:  '#04060d', [T.ECHO]: '#160e00', [T.ANCHOR]:'#001414',
    [T.NEXUS]: '#0a0a06', [T.WALL]: '#050507'
  };
  const TILE_FG = {
    [T.STABLE]:'#22c55e', [T.FLUX]:'#334155', [T.CHAOS]:'#a855f7',
    [T.VOID]:  '#3b82f6', [T.ECHO]: '#eab308', [T.ANCHOR]:'#5eead4',
    [T.NEXUS]: '#f8fafc', [T.WALL]: '#1a1f30'
  };
  const TILE_NAME = {
    [T.STABLE]:'Stable', [T.FLUX]:'Flux', [T.CHAOS]:'Chaos',
    [T.VOID]:  'Void',   [T.ECHO]: 'Echo', [T.ANCHOR]:'Axis Point',
    [T.NEXUS]: 'Nexus',  [T.WALL]: 'Wall'
  };

  // Frame (HP) cost on entering tile
  const STEP_COST = {
    [T.STABLE]:0, [T.FLUX]:0, [T.CHAOS]:-3, [T.VOID]:-5,
    [T.ECHO]:0, [T.ANCHOR]:0, [T.NEXUS]:0, [T.WALL]:0
  };

  // M* delta [Order, Chaos, Unity, Void] on entering tile
  const STEP_MSTAR = {
    [T.STABLE]: [+0.05,-0.02,+0.01,-0.02],
    [T.FLUX]:   [0,0,0,0],
    [T.CHAOS]:  [-0.04,+0.09,-0.02,+0.02],
    [T.VOID]:   [-0.06,+0.01,-0.04,+0.12],
    [T.ECHO]:   [+0.02,-0.04,+0.10,-0.04],
    [T.ANCHOR]: [+0.06,-0.03,+0.03,-0.04],
    [T.NEXUS]:  [0,0,0,0],
    [T.WALL]:   [0,0,0,0],
  };

  // ─── Campaign ──────────────────────────────────────────────────────────────
  const CAMPAIGN = [
    {
      title: 'Level 1 · The Stable Fields',
      intro: [
        'The world did not break physically.',
        'It broke semantically — and everyone',
        'lost their axis of meaning.',
        '',
        'You are a Wayfarer, trained in Triaxial',
        'Orientation. The Stable Fields still hold',
        'the memory of order.',
        '',
        'Find the Nexus. Hold your frame together.',
        '',
        '— SPACE or ENTER to begin —',
      ],
      outro: [
        'The Stable Fields are behind you.',
        '',
        'You can hear the Void humming',
        'at the edges. It has been waiting.',
        '',
        '— SPACE or ENTER to continue —',
      ],
      bonus: 800,
      map: [
        '....................',
        '..*........*........',
        '....................',
        '......XXX...........',
        '......X.X...........',
        '......XXX...........',
        '....*..........VVVV.',
        '.........A.....VVVV.',
        '....................',
        '....*...............',
        '....................',
        '@...................',
        '..................N.',
      ],
    },
    {
      title: 'Level 2 · The Void Corridor',
      intro: [
        'The Void Corridor — channels where',
        'meaning once flowed, now drained',
        'to silence.',
        '',
        'Void tiles cost 5 Frame each step.',
        'Plan your route. Use the Axis Points.',
        '',
        'The silence in there is not emptiness.',
        'It is waiting for something to fill it.',
        '',
        '— SPACE or ENTER to begin —',
      ],
      outro: [
        'You crossed the Void Labyrinth.',
        'Others did not.',
        '',
        'What you carried across was yours.',
        'What you left behind was never yours.',
        '',
        '— SPACE or ENTER to continue —',
      ],
      bonus: 1000,
      map: [
        '..................N.',
        'VVVVVVVVVVVV........',
        '...*........V.......',
        'VVVVVV.....AV.......',
        'V....V..............',
        'V....VVVVVVVVVV.....',
        'V..............V....',
        'VVVVV.......*..V....',
        '.....V.........V....',
        '.....VVVVVVVVVV.....',
        '...*....*...........',
        '@...................',
        '....................',
      ],
    },
    {
      title: 'Level 3 · The Chaos Storm',
      intro: [
        'Chaos does not destroy coherence.',
        'It tests it.',
        '',
        'The Storm breaks most Wayfarers —',
        'not because Chaos is strong,',
        'but because they forget what',
        'they are trying to hold.',
        '',
        'Anchor Points are your refuge.',
        'The Nexus is on the far side.',
        '',
        '— SPACE or ENTER to begin —',
      ],
      outro: [
        'The Chaos Storm is behind you.',
        '',
        'You have learned something:',
        'what you carry cannot be taken.',
        'It can only be abandoned.',
        '',
        '— SPACE or ENTER to continue —',
      ],
      bonus: 1200,
      map: [
        'XXXXXXXXXXXXXXXXXXXX',
        'X..................X',
        'X...*.......A......X',
        'X..................X',
        'XXXXXX.....XXXXXXXXX',
        '.......X............',
        '.......X...*........',
        '.......X..A.........',
        '.......XXXXXXXXXXXXX',
        '....*...............',
        '....................',
        '@...................',
        '.................N..',
      ],
    },
    {
      title: 'Level 4 · The Mirror Maze',
      intro: [
        'This is where Wayfarers lose themselves.',
        '',
        'Flux tiles look safe. Some are not.',
        'Your only guide is your Frame:',
        'if it drains faster than expected,',
        'you have wandered into Chaos.',
        '',
        'The maze does not lie.',
        'It just reflects.',
        '',
        '— SPACE or ENTER to begin —',
      ],
      outro: [
        'The Mirror Maze almost had you.',
        '',
        'Everything looked familiar.',
        'But familiar is not the same as true.',
        '',
        '— SPACE or ENTER to continue —',
      ],
      bonus: 1400,
      map: [
        '~~~~~~~~~~~~~~~~~~..',
        '~XXXX~~XXXXXX~~~~~N.',
        '~X..~~~~X...*~~~..~.',
        '~X.A~~~~X~~~~~~~~~..',
        '~XXXXXX~X~~~~~~~~~..',
        '~~~~~~~~X~~~XXXXXX..',
        '~..*~~~~X~~~X....X..',
        '~~~~~~~~X~~~X.A..X..',
        '~XXXXXX~X~~~XXXXXX..',
        '~X..*~~~X~~~~~~~~~~~',
        '~X~~~~~~X~~~~~~~~~~~',
        '@X~~~~~~X~~~~~~~~~~~',
        '~XXXXXXXXX~~~~~~~~~~',
      ],
    },
    {
      title: 'Level 5 · The Axis Heart',
      intro: [
        'You are here.',
        '',
        'The Axis Heart — the origin point.',
        'Where the three orientations intersect.',
        '',
        'Void surrounds it. Chaos guards',
        'the approaches. But Echoes of the old',
        'coherence remain in the field.',
        '',
        'This is the last Nexus.',
        'What you carry out is yours.',
        '',
        '— SPACE or ENTER to begin —',
      ],
      outro: [  // victory screen — rendered separately
        '',
        'CAMPAIGN COMPLETE',
        '',
        'You reached the Axis Heart.',
        '',
        'The coordinates are clear now.',
        'You did not find meaning here —',
        'you brought it.',
        '',
        '— Press R to play again —',
      ],
      bonus: 2000,
      map: [
        'VVVVVXXXXXVVVVVXXXXX',
        'V.......X.V.......XV',
        'V..A....X.V....A..XV',
        'V.......X.V.......XV',
        'VVVVVXXXXX...*....XV',
        '..........*......X..',
        '..VVVV..........XXXX',
        '..V..V......*...X..X',
        '..VVVV..A.......XXXX',
        '....................',
        '....*.......*.......',
        '@...................',
        '.................N..',
      ],
    },
  ];

  // ─── State ────────────────────────────────────────────────────────────────
  // Possible values: 'title' | 'intro' | 'play' | 'outro' | 'victory' | 'gameover'
  let gameState, levelIdx, score, totalEchoes;
  let world, usedAnchors, player, mstar, frame, echoes, msg;
  let particles = [], animFrame = null, lastT = 0, active = false;

  // ─── Map Parsing ──────────────────────────────────────────────────────────
  function parseMap(rows) {
    const grid = [];
    let startX = 1, startY = ROWS - 2;
    for (let y = 0; y < ROWS; y++) {
      const row = (rows[y] || '').padEnd(COLS, '.');
      grid[y] = [];
      for (let x = 0; x < COLS; x++) {
        const ch = row[x];
        if (ch === '@') { startX = x; startY = y; grid[y][x] = T.STABLE; }
        else grid[y][x] = CHAR_MAP[ch] !== undefined ? CHAR_MAP[ch] : T.STABLE;
      }
    }
    return { grid, startX, startY };
  }

  // ─── Level Init ──────────────────────────────────────────────────────────
  function startLevel(idx) {
    levelIdx = idx;
    const { grid, startX, startY } = parseMap(CAMPAIGN[idx].map);
    world = grid;
    usedAnchors = new Set();
    player = { x: startX, y: startY };
    mstar = [0.40, 0.20, 0.25, 0.15]; // [Order, Chaos, Unity, Void]
    frame = 100;
    echoes = 0;
    msg = 'WASD move · SPACE interact with tile · R restart level';
    particles = [];
  }

  // ─── Game Boot ───────────────────────────────────────────────────────────
  function boot() {
    levelIdx = 0;
    score = 0;
    totalEchoes = 0;
    gameState = 'title';
  }

  // ─── Helpers ─────────────────────────────────────────────────────────────
  function inBounds(x, y) { return x >= 0 && x < COLS && y >= 0 && y < ROWS; }

  function normMstar() {
    const s = mstar.reduce((a, b) => a + b, 0);
    if (s > 0) mstar = mstar.map(v => Math.max(0, v / s));
  }

  function applyMstar(delta) {
    for (let i = 0; i < 4; i++) mstar[i] = Math.max(0, mstar[i] + delta[i]);
    normMstar();
  }

  function coherence() { return Math.max(...mstar); }

  function spawnParticles(px, py, color, n) {
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2;
      const spd = 35 + Math.random() * 55;
      particles.push({ x: px, y: py, vx: Math.cos(a)*spd, vy: Math.sin(a)*spd, life: 1, color });
    }
  }

  // ─── Movement ─────────────────────────────────────────────────────────────
  function move(dx, dy) {
    if (gameState !== 'play') return;
    const nx = player.x + dx, ny = player.y + dy;
    if (!inBounds(nx, ny)) return;
    const tile = world[ny][nx];
    if (tile === T.WALL) { msg = 'Impassable.'; updateHUD(); return; }

    player.x = nx;
    player.y = ny;

    // Frame cost
    const cost = STEP_COST[tile] || 0;
    frame = Math.max(0, frame + cost);

    // M* shift
    applyMstar(STEP_MSTAR[tile] || [0,0,0,0]);

    // Auto-collect echo
    if (tile === T.ECHO) {
      world[ny][nx] = T.STABLE;
      echoes++;
      totalEchoes++;
      frame = Math.min(100, frame + 20);
      msg = `Echo collected (+20 Frame, +Unity). Total: ${echoes}`;
      spawnParticles(nx * CELL + CELL/2, ny * CELL + CELL/2, '#eab308', 10);
    } else {
      const tileMsg = {
        [T.CHAOS]: `Chaos tile (−3 Frame).`,
        [T.VOID]:  `Void tile (−5 Frame).`,
        [T.ANCHOR]: usedAnchors.has(`${nx},${ny}`) ? 'Axis Point (used).' : 'Axis Point — press SPACE to restore Frame.',
        [T.NEXUS]: 'Nexus reached — press SPACE to advance.',
        [T.STABLE]: '',
        [T.FLUX]: '',
      };
      const m = tileMsg[tile];
      if (m) msg = m;
    }

    if (frame <= 0) {
      gameState = 'gameover';
      msg = 'Frame collapsed.';
    }
    updateHUD();
  }

  // ─── Interact ─────────────────────────────────────────────────────────────
  function interact() {
    if (gameState !== 'play') return;
    const tile = world[player.y][player.x];
    const key = `${player.x},${player.y}`;

    if (tile === T.NEXUS) {
      // Advance
      const lvl = CAMPAIGN[levelIdx];
      const bonus = lvl.bonus;
      const frameBonus = Math.round(frame * 8);
      const echoBonus = echoes * 50;
      score += bonus + frameBonus + echoBonus;
      spawnParticles(player.x*CELL+CELL/2, player.y*CELL+CELL/2, '#5eead4', 20);
      if (levelIdx >= CAMPAIGN.length - 1) {
        gameState = 'victory';
      } else {
        gameState = 'outro';
      }
      updateHUD();
      return;
    }

    if (tile === T.STABLE) {
      frame = Math.min(100, frame + 6);
      applyMstar([+0.10,-0.05,+0.02,-0.05]);
      msg = 'Grounded — Order strengthens. (+6 Frame)';
      spawnParticles(player.x*CELL+CELL/2, player.y*CELL+CELL/2, '#22c55e', 6);
      updateHUD();
      return;
    }

    if (tile === T.ANCHOR) {
      if (usedAnchors.has(key)) {
        msg = 'This Axis Point is spent.';
      } else {
        usedAnchors.add(key);
        frame = Math.min(100, frame + 30);
        applyMstar([+0.12,-0.06,+0.06,-0.10]);
        world[player.y][player.x] = T.FLUX; // spent
        msg = 'Axis Point restored. (+30 Frame, +Order)';
        spawnParticles(player.x*CELL+CELL/2, player.y*CELL+CELL/2, '#5eead4', 14);
      }
      updateHUD();
      return;
    }

    if (tile === T.CHAOS) {
      frame = Math.max(0, frame - 10);
      applyMstar([-0.06,+0.04,+0.18,-0.04]);
      msg = 'Pressed into Chaos. (−10 Frame, Unity rises sharply)';
      spawnParticles(player.x*CELL+CELL/2, player.y*CELL+CELL/2, '#a855f7', 10);
      if (frame <= 0) gameState = 'gameover';
      updateHUD();
      return;
    }

    msg = 'Nothing to interact with here.';
    updateHUD();
  }

  // ─── Rendering ────────────────────────────────────────────────────────────
  function render(ctx, now) {
    const dt = Math.min((now - lastT) / 1000, 0.05);
    lastT = now;

    // Update particles
    particles = particles.filter(p => {
      p.x += p.vx * dt; p.y += p.vy * dt; p.life -= dt * 2.2;
      return p.life > 0;
    });

    ctx.clearRect(0, 0, CW, CH);
    ctx.fillStyle = '#0b1021';
    ctx.fillRect(0, 0, CW, CH);

    if (!active) { drawScreen(ctx, now, 'title'); animFrame = requestAnimationFrame(t => render(ctx, t)); return; }

    switch (gameState) {
      case 'title':    drawScreen(ctx, now, 'title');   break;
      case 'intro':    drawScreen(ctx, now, 'intro');   break;
      case 'outro':    drawScreen(ctx, now, 'outro');   break;
      case 'victory':  drawScreen(ctx, now, 'victory'); break;
      case 'gameover': drawGame(ctx, now); drawOverlay(ctx, false); break;
      case 'play':     drawGame(ctx, now); break;
    }

    animFrame = requestAnimationFrame(t => render(ctx, t));
  }

  function drawGame(ctx, now) {
    // Tiles
    for (let y = 0; y < ROWS; y++) {
      for (let x = 0; x < COLS; x++) {
        const tile = world[y][x];
        const px = x * CELL, py = y * CELL;
        ctx.fillStyle = TILE_BG[tile] || '#111';
        ctx.fillRect(px, py, CELL, CELL);
        drawTileSymbol(ctx, tile, px, py, now, x, y);
      }
    }

    // Subtle grid
    ctx.strokeStyle = 'rgba(255,255,255,0.025)';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= COLS; x++) { ctx.beginPath(); ctx.moveTo(x*CELL,0); ctx.lineTo(x*CELL,CH); ctx.stroke(); }
    for (let y = 0; y <= ROWS; y++) { ctx.beginPath(); ctx.moveTo(0,y*CELL); ctx.lineTo(CW,y*CELL); ctx.stroke(); }

    // Player
    const ppx = player.x * CELL + CELL/2, ppy = player.y * CELL + CELL/2;
    const pulse = Math.sin(now / 380) * 1.5;
    ctx.beginPath(); ctx.arc(ppx, ppy, 8+pulse*0.3, 0, Math.PI*2);
    ctx.fillStyle = 'rgba(249,115,22,0.18)'; ctx.fill();
    ctx.beginPath(); ctx.arc(ppx, ppy, 7, 0, Math.PI*2);
    ctx.fillStyle = '#f97316'; ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5; ctx.stroke();

    // Coherence ring
    const c = coherence();
    ctx.beginPath();
    ctx.arc(ppx, ppy, 11, -Math.PI/2, -Math.PI/2 + c * Math.PI * 2);
    ctx.strokeStyle = c >= 0.6 ? '#5eead4' : '#38bdf8';
    ctx.lineWidth = 2; ctx.stroke();

    // Particles
    for (const p of particles) {
      ctx.globalAlpha = Math.max(0, p.life);
      ctx.fillStyle = p.color;
      ctx.fillRect(p.x - 2, p.y - 2, 4, 4);
    }
    ctx.globalAlpha = 1;
  }

  function drawTileSymbol(ctx, tile, px, py, now, x, y) {
    const cx = px + CELL/2, cy = py + CELL/2;
    const t2 = now / 1000;

    switch (tile) {
      case T.STABLE:
        ctx.fillStyle = 'rgba(34,197,94,0.18)';
        ctx.fillRect(px+2, py+2, CELL-4, CELL-4);
        ctx.fillStyle = 'rgba(34,197,94,0.12)';
        ctx.fillRect(px+5, py+5, CELL-10, CELL-10);
        break;
      case T.FLUX:
        ctx.fillStyle = `rgba(71,85,105,${0.15 + Math.sin(t2+x+y)*0.05})`;
        ctx.fillRect(px+6, py+6, CELL-12, CELL-12);
        break;
      case T.CHAOS:
        ctx.fillStyle = `rgba(168,85,247,${0.25 + Math.sin(t2*2.3+x*0.7+y*1.1)*0.12})`;
        ctx.fillRect(px+3, py+3, CELL-6, CELL-6);
        ctx.fillStyle = `rgba(168,85,247,${0.12 + Math.sin(t2*1.7+x)*0.08})`;
        ctx.fillRect(px+7, py+7, CELL-14, CELL-14);
        break;
      case T.VOID:
        ctx.fillStyle = `rgba(59,130,246,${0.08 + Math.sin(t2*0.8+x*0.5)*0.04})`;
        ctx.fillRect(px+2, py+2, CELL-4, CELL-4);
        ctx.fillStyle = `rgba(59,130,246,${0.15})`;
        ctx.fillRect(px+8, py+8, CELL-16, CELL-16);
        break;
      case T.ECHO:
        ctx.fillStyle = `rgba(234,179,8,${0.8 + Math.sin(t2*3+x+y)*0.2})`;
        drawDiamond(ctx, cx, cy, 5);
        ctx.fillStyle = 'rgba(234,179,8,0.3)';
        drawDiamond(ctx, cx, cy, 7 + Math.sin(t2*2)*1);
        break;
      case T.ANCHOR:
        ctx.strokeStyle = `rgba(94,234,212,${0.7 + Math.sin(t2*2)*0.2})`;
        ctx.lineWidth = 2;
        ctx.strokeRect(px+4, py+4, CELL-8, CELL-8);
        ctx.strokeStyle = 'rgba(94,234,212,0.35)';
        ctx.lineWidth = 1;
        ctx.strokeRect(px+7, py+7, CELL-14, CELL-14);
        break;
      case T.NEXUS: {
        const glow = 0.5 + Math.sin(t2*1.8)*0.3;
        ctx.strokeStyle = `rgba(248,250,252,${glow})`;
        ctx.lineWidth = 2;
        ctx.strokeRect(px+3, py+3, CELL-6, CELL-6);
        ctx.strokeStyle = `rgba(248,250,252,${glow*0.5})`;
        ctx.lineWidth = 1;
        ctx.strokeRect(px+6, py+6, CELL-12, CELL-12);
        // N label
        ctx.fillStyle = `rgba(248,250,252,${glow})`;
        ctx.font = `bold 9px monospace`;
        ctx.textAlign = 'center';
        ctx.fillText('N', cx, cy+3);
        ctx.textAlign = 'left';
        break;
      }
      case T.WALL:
        ctx.fillStyle = 'rgba(30,42,66,0.7)';
        ctx.fillRect(px, py, CELL, CELL);
        break;
    }
  }

  function drawDiamond(ctx, cx, cy, r) {
    ctx.beginPath();
    ctx.moveTo(cx, cy - r);
    ctx.lineTo(cx + r, cy);
    ctx.lineTo(cx, cy + r);
    ctx.lineTo(cx - r, cy);
    ctx.closePath();
    ctx.fill();
  }

  function drawOverlay(ctx, won) {
    ctx.fillStyle = 'rgba(11,16,33,0.88)';
    ctx.fillRect(0, 0, CW, CH);
    ctx.textAlign = 'center';
    ctx.font = "bold 20px 'Space Grotesk', sans-serif";
    ctx.fillStyle = won ? '#5eead4' : '#ef4444';
    ctx.fillText(won ? 'NEXUS REACHED' : 'FRAME COLLAPSED', CW/2, CH/2 - 18);
    ctx.font = "12px 'Space Grotesk', sans-serif";
    ctx.fillStyle = '#9fb0c5';
    if (!won) ctx.fillText('Your interpretive frame could not hold.', CW/2, CH/2 + 4);
    ctx.fillText('Press R to restart this level', CW/2, CH/2 + 22);
    ctx.textAlign = 'left';
  }

  // ─── Non-play screens drawn on canvas ────────────────────────────────────
  function drawScreen(ctx, now, type) {
    const pal = { bg:'rgba(11,16,33,0.95)', accent:'#5eead4', sub:'#9fb0c5', text:'#e8ecf5' };

    if (type === 'title') {
      // Animated background dots
      for (let i = 0; i < 30; i++) {
        const bx = ((i * 47 + now * 0.012) % CW);
        const by = ((i * 31 + now * 0.008) % CH);
        ctx.fillStyle = `rgba(94,234,212,${0.04 + (i%3)*0.02})`;
        ctx.fillRect(bx, by, 2, 2);
      }

      ctx.textAlign = 'center';
      ctx.fillStyle = pal.accent;
      ctx.font = "bold 18px 'Space Grotesk', sans-serif";
      ctx.fillText('ECHOES OF COHERENCE', CW/2, 52);

      ctx.fillStyle = pal.sub;
      ctx.font = "11px 'Space Grotesk', sans-serif";
      ctx.fillText('A game of semantic stability', CW/2, 70);

      // Rules box
      const rules = [
        '─── HOW TO PLAY ───',
        '',
        'You are a Wayfarer navigating a world that',
        'has lost its axis of meaning. Cross 5 levels,',
        'preserve your Frame, and reach each Nexus.',
        '',
        'STABLE tiles (.): safe ground · SPACE to anchor (+Frame)',
        'CHAOS tiles (X): cost 3 Frame/step · risky SPACE for Unity',
        'VOID tiles (V): cost 5 Frame/step · drains Order',
        'ECHO tiles (★): collect to restore +20 Frame · +Unity',
        'AXIS POINT (▣): SPACE for +30 Frame (one use)',
        'NEXUS (N): SPACE to advance to next level',
        '',
        '★  Collect Echoes · reach the Nexus · survive ★',
      ];

      ctx.font = "10px 'Space Grotesk', sans-serif";
      rules.forEach((line, i) => {
        if (line.startsWith('─')) ctx.fillStyle = pal.accent;
        else if (line.startsWith('STABLE') || line.startsWith('CHAOS') || line.startsWith('VOID') || line.startsWith('ECHO') || line.startsWith('AXIS') || line.startsWith('NEXUS')) ctx.fillStyle = '#e8ecf5';
        else if (line.startsWith('★')) ctx.fillStyle = '#eab308';
        else ctx.fillStyle = pal.sub;
        ctx.fillText(line, CW/2, 96 + i * 12);
      });

      const pulse = (Math.sin(now/600) + 1) / 2;
      ctx.fillStyle = `rgba(56,189,248,${0.7 + pulse*0.3})`;
      ctx.font = "bold 12px 'Space Grotesk', sans-serif";
      ctx.fillText('Click canvas · then SPACE to begin', CW/2, 270);
      ctx.textAlign = 'left';
      return;
    }

    if (type === 'intro' || type === 'outro' || type === 'victory') {
      // Draw faint game map in background for intro/outro
      if (type === 'intro' && world) {
        ctx.globalAlpha = 0.12;
        for (let y = 0; y < ROWS; y++)
          for (let x = 0; x < COLS; x++) {
            ctx.fillStyle = TILE_FG[world[y][x]] || '#333';
            ctx.fillRect(x*CELL+7, y*CELL+7, 8, 8);
          }
        ctx.globalAlpha = 1;
      }

      ctx.fillStyle = 'rgba(11,16,33,0.88)';
      ctx.fillRect(0, 0, CW, CH);

      const lvl = CAMPAIGN[levelIdx];
      const lines = (type === 'outro' || type === 'victory') ? lvl.outro : lvl.intro;

      ctx.textAlign = 'center';

      // Level title
      ctx.fillStyle = pal.accent;
      ctx.font = "bold 13px 'Space Grotesk', sans-serif";
      ctx.fillText(lvl.title, CW/2, 30);

      // Separator
      ctx.strokeStyle = 'rgba(94,234,212,0.3)';
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(CW/2 - 100, 38); ctx.lineTo(CW/2 + 100, 38); ctx.stroke();

      // Story lines
      const startY = type === 'victory' ? 56 : 52;
      lines.forEach((line, i) => {
        if (line === 'CAMPAIGN COMPLETE') {
          ctx.fillStyle = '#eab308';
          ctx.font = "bold 16px 'Space Grotesk', sans-serif";
          ctx.fillText(line, CW/2, startY + i * 14);
          ctx.font = "11px 'Space Grotesk', sans-serif";
        } else if (line.startsWith('—')) {
          const pulse = (Math.sin(now/600) + 1) / 2;
          ctx.fillStyle = `rgba(56,189,248,${0.7 + pulse*0.3})`;
          ctx.font = "bold 11px 'Space Grotesk', sans-serif";
          ctx.fillText(line, CW/2, startY + i * 14);
          ctx.font = "11px 'Space Grotesk', sans-serif";
        } else {
          ctx.fillStyle = line === '' ? 'transparent' : pal.sub;
          ctx.font = "11px 'Space Grotesk', sans-serif";
          ctx.fillText(line, CW/2, startY + i * 14);
        }
      });

      if (type === 'victory') {
        ctx.fillStyle = '#eab308';
        ctx.font = "bold 12px 'Space Grotesk', sans-serif";
        ctx.fillText(`Final Score: ${score.toLocaleString()}`, CW/2, CH - 28);
        ctx.fillStyle = pal.sub;
        ctx.font = "10px 'Space Grotesk', sans-serif";
        ctx.fillText(`${totalEchoes} Echoes collected across all levels`, CW/2, CH - 14);
      }

      ctx.textAlign = 'left';
    }
  }

  // ─── HUD ──────────────────────────────────────────────────────────────────
  function updateHUD() {
    const hud = document.getElementById('eoc-hud');
    if (!hud) return;

    const c = coherence();
    const cPct = Math.round(c * 100);
    const fPct = Math.round(frame);
    const MSTAR_LABELS = ['Order','Chaos','Unity','Void'];
    const MSTAR_COLORS = ['#38bdf8','#a855f7','#5eead4','#6b7280'];

    const mBars = mstar.map((v, i) => {
      const pct = Math.round(v * 100);
      return `<div class="eoc-mbar">
        <span class="eoc-mlabel">${MSTAR_LABELS[i][0]}</span>
        <div class="eoc-mfill" style="width:${pct}%;background:${MSTAR_COLORS[i]}"></div>
        <span class="eoc-mval">${pct}%</span>
      </div>`;
    }).join('');

    let statusHtml = '';
    if (gameState === 'play') {
      const lvl = CAMPAIGN[levelIdx];
      statusHtml = `
        <div class="eoc-stat-row">
          <div class="eoc-stat">
            <span class="eoc-label">Frame</span>
            <div class="eoc-bar"><div class="eoc-fill" style="width:${fPct}%;background:${fPct>50?'#22c55e':fPct>25?'#f59e0b':'#ef4444'}"></div></div>
            <span class="eoc-val ${fPct<=25?'eoc-val-warn':''}">${fPct}</span>
          </div>
          <div class="eoc-stat">
            <span class="eoc-label">Coherence</span>
            <div class="eoc-bar"><div class="eoc-fill" style="width:${cPct}%;background:#5eead4"></div></div>
            <span class="eoc-val">${cPct}%</span>
          </div>
        </div>
        <div class="eoc-mstar">${mBars}</div>
        <div class="eoc-tags">
          <span class="eoc-tag">${lvl.title}</span>
          <span class="eoc-tag ${echoes>0?'eoc-tag-ok':''}">★ ${echoes}</span>
          <span class="eoc-tag">Score: ${score.toLocaleString()}</span>
        </div>
        <div class="eoc-msg">${msg}</div>
      `;
    } else {
      statusHtml = `<div class="eoc-msg" style="text-align:center;padding:0.4rem 0">${
        gameState === 'title' ? 'Click the canvas to start.' :
        gameState === 'gameover' ? 'Frame collapsed — press R to retry.' :
        gameState === 'victory' ? `Campaign complete! Score: ${score.toLocaleString()}` :
        'Press SPACE or ENTER to continue.'
      }</div>`;
    }

    hud.innerHTML = statusHtml;
  }

  // ─── Input ────────────────────────────────────────────────────────────────
  function handleKey(e) {
    // Advance through text screens
    if (gameState === 'title' && (e.key === ' ' || e.key === 'Enter')) {
      e.preventDefault();
      startLevel(0);
      gameState = 'intro';
      updateHUD();
      return;
    }
    if (gameState === 'intro' && (e.key === ' ' || e.key === 'Enter')) {
      e.preventDefault();
      gameState = 'play';
      msg = 'WASD move · SPACE interact · R restart level';
      updateHUD();
      return;
    }
    if (gameState === 'outro' && (e.key === ' ' || e.key === 'Enter')) {
      e.preventDefault();
      const next = levelIdx + 1;
      if (next < CAMPAIGN.length) {
        startLevel(next);
        gameState = 'intro';
      }
      updateHUD();
      return;
    }
    if (gameState === 'victory' && (e.key === 'r' || e.key === 'R')) {
      boot();
      gameState = 'title';
      updateHUD();
      return;
    }
    if (gameState === 'gameover' && (e.key === 'r' || e.key === 'R')) {
      startLevel(levelIdx);
      gameState = 'play';
      msg = 'WASD move · SPACE interact · R restart level';
      updateHUD();
      return;
    }
    if (gameState === 'play') {
      switch (e.key) {
        case 'ArrowUp':    case 'w': case 'W': e.preventDefault(); move(0,-1); break;
        case 'ArrowDown':  case 's': case 'S': e.preventDefault(); move(0,+1); break;
        case 'ArrowLeft':  case 'a': case 'A': e.preventDefault(); move(-1,0); break;
        case 'ArrowRight': case 'd': case 'D': e.preventDefault(); move(+1,0); break;
        case ' ': e.preventDefault(); interact(); break;
        case 'r': case 'R': startLevel(levelIdx); msg = 'Level restarted.'; updateHUD(); break;
      }
    }
  }

  // ─── Public Init ──────────────────────────────────────────────────────────
  window.initEchoes = function (canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    canvas.width = CW;
    canvas.height = CH;
    canvas.setAttribute('tabIndex', '0');
    canvas.style.outline = 'none';
    canvas.style.cursor = 'pointer';

    const ctx = canvas.getContext('2d');

    boot();
    updateHUD();

    canvas.addEventListener('click', () => {
      if (!active) {
        active = true;
        canvas.style.cursor = 'default';
        canvas.focus();
      }
    });

    canvas.addEventListener('keydown', handleKey);
    canvas.addEventListener('wheel', e => { if (active) e.preventDefault(); }, { passive: false });

    if (animFrame) cancelAnimationFrame(animFrame);
    lastT = performance.now();
    animFrame = requestAnimationFrame(t => render(ctx, t));
  };

})();
