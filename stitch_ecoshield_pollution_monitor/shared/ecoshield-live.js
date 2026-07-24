/**
 * EcoShield shared live-demo layer (frontend only).
 * Backend collaborator: wire POST /api/ai-summary to replace Gemini direct call.
 */
(function (global) {
  'use strict';

  const COMPANIES = [
    { name: 'Ghantoot Group', sector: 'Construction', score: 28, trend: 'improving' },
    { name: 'Suntech', sector: 'Energy', score: 36, trend: 'stable' },
    { name: 'Proscape', sector: 'Landscaping', score: 48, trend: 'drifting' },
    { name: 'Depa Interiors', sector: 'Fit-out', score: 55, trend: 'stable' },
    { name: 'Emirates Neon', sector: 'Manufacturing', score: 62, trend: 'drifting' },
    { name: 'Al Naboodah', sector: 'Infrastructure', score: 71, trend: 'worsening' },
    { name: 'TechNoCity', sector: 'Infrastructure', score: 74, trend: 'worsening' },
    { name: 'Al Rostamani', sector: 'Logistics', score: 81, trend: 'worsening' },
    { name: 'Al Safa Industrial', sector: 'Manufacturing', score: 88, trend: 'critical' },
    { name: 'Infranet Corp', sector: 'Energy', score: 95, trend: 'critical' },
    { name: 'Bin Hamoodah', sector: 'Construction', score: 91, trend: 'critical' }
  ];

  const LIVE_EVENTS = [
    { company: 'Infranet Corp', sector: 'Energy / Sector 4' },
    { company: 'Al Safa Industrial', sector: 'Manufacturing / Coastal' },
    { company: 'Bin Hamoodah', sector: 'Construction / Abu Dhabi' },
    { company: 'TechNoCity', sector: 'Infrastructure / Sharjah' },
    { company: 'Al Naboodah', sector: 'Heavy Equipment / Dubai' }
  ];

  const MACHINE_DEFAULTS = [
    { machine: 'Excavator (Tier 2 Diesel)', smoke: 78, fuel: 98, carbon: 92, risk: 97, replacement: 'Electric Excavator (Tier 4 / Battery)' },
    { machine: 'Bulldozer (Tier 2 Diesel)', smoke: 71, fuel: 89, carbon: 85, risk: 91, replacement: 'Bulldozer (Tier 4 DEF/SCR)' },
    { machine: 'Diesel Generator', smoke: 65, fuel: 80, carbon: 74, risk: 83, replacement: 'Hybrid/Battery Generator' },
    { machine: 'Backhoe Loader', smoke: 58, fuel: 70, carbon: 66, risk: 74, replacement: 'Backhoe Loader (Tier 4)' },
    { machine: 'Concrete Mixer Truck', smoke: 40, fuel: 55, carbon: 48, risk: 52, replacement: 'Low-Emission variant' },
    { machine: 'Dump Truck', smoke: 34, fuel: 47, carbon: 41, risk: 44, replacement: null },
    { machine: 'Compactor/Roller', smoke: 20, fuel: 28, carbon: 25, risk: 27, replacement: null }
  ];

  /* 90-day synthetic trend: compliant early, drift mid-year, spike recently */
  function buildTrendSeries(days) {
    const points = [];
    const now = new Date();
    for (let i = days - 1; i >= 0; i--) {
      const d = new Date(now);
      d.setDate(d.getDate() - i);
      const t = 1 - i / days;
      let base = 38 + t * 28;
      if (t > 0.55) base += (t - 0.55) * 90;
      if (t > 0.82) base += (t - 0.82) * 120;
      const noise = Math.sin(i * 0.7) * 4 + Math.cos(i * 0.31) * 3;
      points.push({
        label: d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }),
        value: Math.max(20, Math.min(98, Math.round(base + noise)))
      });
    }
    return points;
  }

  function getRole() {
    return localStorage.getItem('ecoshield_role') || 'ministry';
  }

  function setRole(role) {
    localStorage.setItem('ecoshield_role', role);
    document.body.setAttribute('data-role', role);
    document.querySelectorAll('.es-role-toggle button').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.role === role);
    });
  }

  function ensureToastStack() {
    let stack = document.getElementById('es-toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.id = 'es-toast-stack';
      document.body.appendChild(stack);
    }
    return stack;
  }

  function showToast(event) {
    const stack = ensureToastStack();
    const el = document.createElement('div');
    el.className = 'es-toast';
    el.innerHTML =
      '<div class="es-toast-title">AI Detection · Live</div>' +
      '<div class="es-toast-body">New violation detected: <strong>' +
      event.company +
      '</strong>, ' +
      event.sector +
      '</div>' +
      '<div class="es-toast-meta">' +
      new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) +
      ' GST · confidence 94%</div>';
    stack.appendChild(el);
    setTimeout(() => {
      el.classList.add('es-toast-out');
      setTimeout(() => el.remove(), 400);
    }, 5500);
  }

  function startLiveDetections(intervalMs) {
    if (global.__esLiveStarted) return;
    global.__esLiveStarted = true;
    let i = 0;
    setTimeout(() => showToast(LIVE_EVENTS[0]), 2500);
    setInterval(() => {
      i = (i + 1) % LIVE_EVENTS.length;
      showToast(LIVE_EVENTS[i]);
    }, intervalMs || 15000);
  }

  function mountRoleToggle(container) {
    if (!container || container.querySelector('.es-role-toggle')) return;
    const wrap = document.createElement('div');
    wrap.className = 'es-role-toggle';
    wrap.innerHTML =
      '<button type="button" data-role="ministry">Ministry</button>' +
      '<button type="button" data-role="company">Company</button>';
    wrap.querySelectorAll('button').forEach((btn) => {
      btn.addEventListener('click', () => setRole(btn.dataset.role));
    });
    container.appendChild(wrap);
    setRole(getRole());
  }

  function scoreColor(score) {
    if (score >= 80) return '#f87171';
    if (score >= 60) return '#fb923c';
    if (score >= 40) return '#fbbf24';
    return '#34d399';
  }

  function getLeaderboardData() {
    const fines = JSON.parse(localStorage.getItem('ecoshield_fines') || '{}');
    return COMPANIES.map((c) => {
      const penalty = fines[c.name] || 0;
      return { ...c, score: Math.max(10, c.score - penalty) };
    }).sort((a, b) => a.score - b.score);
  }

  function renderLeaderboard(target) {
    if (!target) return;
    const rows = getLeaderboardData();
    target.innerHTML =
      '<div class="es-leaderboard"><h3>Compliance Leaderboard</h3>' +
      rows
        .map((c, idx) => {
          const color = scoreColor(c.score);
          const label = c.score < 40 ? 'GREEN' : c.score < 70 ? 'WATCH' : 'RISK';
          return (
            '<div class="es-lb-row">' +
            '<span class="es-lb-rank">#' +
            (idx + 1) +
            '</span>' +
            '<span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' +
            c.name +
            '</span>' +
            '<div class="es-lb-bar"><i style="width:' +
            c.score +
            '%;background:' +
            color +
            '"></i></div>' +
            '<span class="es-lb-score" style="color:' +
            color +
            '">' +
            c.score +
            ' · ' +
            label +
            '</span></div>'
          );
        })
        .join('') +
      '</div>';
  }

  function flashFineOverlay() {
    const flash = document.createElement('div');
    flash.className = 'es-fine-flash';
    document.body.appendChild(flash);
    setTimeout(() => flash.remove(), 750);
  }

  function recordFine(companyName, delta) {
    const fines = JSON.parse(localStorage.getItem('ecoshield_fines') || '{}');
    fines[companyName] = (fines[companyName] || 0) + (delta || 6);
    localStorage.setItem('ecoshield_fines', JSON.stringify(fines));
    const softened = JSON.parse(localStorage.getItem('ecoshield_softened_pins') || '[]');
    if (companyName && !softened.includes(companyName)) {
      softened.push(companyName);
      localStorage.setItem('ecoshield_softened_pins', JSON.stringify(softened));
    }
  }

  function animateRiskBadge(badgeEl) {
    if (!badgeEl) return;
    const text = badgeEl.textContent || '';
    const match = text.match(/(\d+)/);
    if (!match) return;
    let score = parseInt(match[1], 10);
    const next = Math.max(score - 8 - Math.floor(Math.random() * 5), 40);
    badgeEl.classList.add('es-risk-flash');
    const step = () => {
      if (score <= next) {
        const label = next >= 80 ? 'CRITICAL' : next >= 60 ? 'HIGH' : 'MODERATE';
        const cls =
          next >= 80
            ? 'bg-orange-100 text-orange-700'
            : next >= 60
              ? 'bg-amber-100 text-amber-700'
              : 'bg-amber-100 text-amber-700';
        badgeEl.className = cls + ' px-2 py-1 rounded text-xs font-bold es-risk-flash';
        badgeEl.textContent = next + '% ' + label;
        return;
      }
      score -= 1;
      badgeEl.textContent = score + '% ' + (score >= 80 ? 'CRITICAL' : 'HIGH');
      requestAnimationFrame(() => setTimeout(step, 28));
    };
    step();
  }

  function wireImposeFines(companyName) {
    document.querySelectorAll('button').forEach((btn) => {
      const label = (btn.textContent || '').trim().toUpperCase();
      if (label !== 'IMPOSE FINE') return;
      btn.classList.add('ministry-only');
      if (btn.dataset.esWired) return;
      btn.dataset.esWired = '1';
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        flashFineOverlay();
        const row = btn.closest('tr') || btn.closest('article');
        const badge = row
          ? row.querySelector('[class*="bg-red"], [class*="bg-orange"], [class*="CRITICAL"], span.font-bold')
          : null;
        const riskBadge =
          (row && row.querySelector('td:nth-child(5) span')) ||
          badge;
        animateRiskBadge(riskBadge);
        const name =
          companyName ||
          (row && row.querySelector('h2') && row.querySelector('h2').textContent.trim()) ||
          'Site operator';
        recordFine(name, 7);
        btn.textContent = 'FINE ISSUED';
        btn.disabled = true;
        btn.style.opacity = '0.7';
        showToast({
          company: name,
          sector: 'Enforcement action recorded'
        });
        const lb = document.getElementById('es-leaderboard-mount');
        if (lb) renderLeaderboard(lb);
      });
    });
  }

  function collectMachineTableData() {
    const rows = [];
    document.querySelectorAll('table tbody tr').forEach((tr) => {
      const cells = tr.querySelectorAll('td');
      if (cells.length < 5) return;
      const name = (cells[0].innerText || '').replace(/\s+/g, ' ').trim();
      const risk = (cells[4].innerText || '').trim();
      const repl = (cells[5].innerText || '').trim();
      rows.push({ name, risk, replacement: repl });
    });
    return rows.length ? rows : MACHINE_DEFAULTS.map((m) => ({
      name: m.machine,
      risk: m.risk + '%',
      replacement: m.replacement || 'None'
    }));
  }

  function getGeminiKey() {
    return (
      global.ECOSHIELD_GEMINI_KEY ||
      localStorage.getItem('ECOSHIELD_GEMINI_KEY') ||
      ''
    ).trim();
  }

  async function callBackendSummary(payload) {
    const res = await fetch('/api/ai-summary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('backend ' + res.status);
    const data = await res.json();
    return data.summary || data.text || '';
  }

  async function callGeminiSummary(payload) {
    const key = getGeminiKey();
    if (!key) throw new Error('no-key');
    const prompt =
      'You are EcoShield, a UAE environmental enforcement AI. Write a concise 2-3 sentence live site summary for ministry officers. Be specific with numbers from the data. No markdown.\n\n' +
      JSON.stringify(payload, null, 2);
    const url =
      'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' +
      encodeURIComponent(key);
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }]
      })
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error('gemini ' + res.status + ' ' + err.slice(0, 120));
    }
    const data = await res.json();
    return (
      data.candidates?.[0]?.content?.parts?.map((p) => p.text).join(' ') ||
      ''
    ).trim();
  }

  function localDataSummary(payload) {
    const top = payload.machines
      .slice()
      .sort((a, b) => parseInt(b.risk, 10) - parseInt(a.risk, 10))[0];
    return (
      payload.site +
      ' is emitting ~3× baseline NOx, driven primarily by an aging ' +
      (top?.name || 'Tier-2 excavator') +
      ' at ' +
      (top?.risk || '97%') +
      ' risk. Adopting the flagged replacements would cut site carbon footprint by ~34% and eliminate an estimated AED 0 in future fines if remediation completes within 30 days.'
    );
  }

  async function generateAiSummary(opts) {
    const site =
      opts?.site ||
      document.getElementById('site-detail-dynamic-title')?.textContent ||
      'Abu Dhabi Hub site';
    const machines = collectMachineTableData();
    const payload = {
      site,
      aqi: 156,
      noxKgDay: 210,
      pm25: 43,
      machines,
      flaggedReplacements: machines.filter((m) => m.replacement && !/no replacement/i.test(m.replacement)).length
    };

    try {
      const fromApi = await callBackendSummary(payload);
      if (fromApi) return { text: fromApi, source: 'live · /api/ai-summary' };
    } catch (_) {
      /* backend not ready — expected while collaborator builds it */
    }

    try {
      const fromGemini = await callGeminiSummary(payload);
      if (fromGemini) return { text: fromGemini, source: 'live · Gemini API' };
    } catch (err) {
      if (String(err.message).includes('no-key')) {
        return {
          text: localDataSummary(payload),
          source: 'telemetry-derived (set ECOSHIELD_GEMINI_KEY or wire /api/ai-summary for LLM)',
          needsKey: true
        };
      }
      return {
        text: localDataSummary(payload) + ' (LLM unreachable — showing telemetry summary.)',
        source: 'fallback · ' + err.message.slice(0, 60)
      };
    }

    return { text: localDataSummary(payload), source: 'telemetry-derived' };
  }

  function drawTrendChart(canvas, days) {
    if (!canvas) return;
    const series = buildTrendSeries(days || 90);
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth || 400;
    const h = canvas.clientHeight || 160;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, w, h);

    const pad = { t: 12, r: 12, b: 28, l: 32 };
    const plotW = w - pad.l - pad.r;
    const plotH = h - pad.t - pad.b;
    const minV = 0;
    const maxV = 100;

    ctx.strokeStyle = 'rgba(148,163,184,0.25)';
    ctx.lineWidth = 1;
    [25, 50, 75].forEach((v) => {
      const y = pad.t + plotH - ((v - minV) / (maxV - minV)) * plotH;
      ctx.beginPath();
      ctx.moveTo(pad.l, y);
      ctx.lineTo(pad.l + plotW, y);
      ctx.stroke();
      ctx.fillStyle = '#64748b';
      ctx.font = '10px JetBrains Mono, monospace';
      ctx.fillText(String(v), 4, y + 3);
    });

    // threshold line
    const thY = pad.t + plotH - ((80 - minV) / (maxV - minV)) * plotH;
    ctx.setLineDash([4, 4]);
    ctx.strokeStyle = 'rgba(248,113,113,0.6)';
    ctx.beginPath();
    ctx.moveTo(pad.l, thY);
    ctx.lineTo(pad.l + plotW, thY);
    ctx.stroke();
    ctx.setLineDash([]);

    const points = series.map((p, i) => {
      const x = pad.l + (i / (series.length - 1)) * plotW;
      const y = pad.t + plotH - ((p.value - minV) / (maxV - minV)) * plotH;
      return { x, y, ...p };
    });

    const grad = ctx.createLinearGradient(0, pad.t, 0, pad.t + plotH);
    grad.addColorStop(0, 'rgba(248,113,113,0.35)');
    grad.addColorStop(0.5, 'rgba(251,146,60,0.2)');
    grad.addColorStop(1, 'rgba(52,211,153,0.05)');

    ctx.beginPath();
    points.forEach((p, i) => (i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y)));
    ctx.lineTo(points[points.length - 1].x, pad.t + plotH);
    ctx.lineTo(points[0].x, pad.t + plotH);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    ctx.beginPath();
    points.forEach((p, i) => (i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y)));
    ctx.strokeStyle = '#4edea3';
    ctx.lineWidth = 2;
    ctx.stroke();

    // end point
    const last = points[points.length - 1];
    ctx.beginPath();
    ctx.arc(last.x, last.y, 4, 0, Math.PI * 2);
    ctx.fillStyle = '#f87171';
    ctx.fill();

    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px JetBrains Mono, monospace';
    ctx.fillText(series[0].label, pad.l, h - 8);
    ctx.fillText(series[series.length - 1].label, w - pad.r - 40, h - 8);
    ctx.fillStyle = '#f87171';
    ctx.fillText('critical threshold', pad.l + 8, thY - 6);
  }

  function exportPdfReport() {
    const title = document.getElementById('site-detail-dynamic-title')?.textContent || 'Site Report';
    const machines = collectMachineTableData();
    const summary =
      document.getElementById('es-ai-summary-text')?.textContent ||
      'Compliance report generated from live EcoShield telemetry.';

    const win = window.open('', '_blank');
    if (!win) {
      window.print();
      return;
    }
    win.document.write(`<!DOCTYPE html><html><head><title>EcoShield Report</title>
      <style>
        body{font-family:Geist,system-ui,sans-serif;color:#0f172a;padding:40px;max-width:800px;margin:0 auto}
        h1{color:#047857;margin:0 0 4px;font-size:28px}
        .meta{color:#64748b;font-size:12px;margin-bottom:24px;font-family:ui-monospace,monospace}
        .banner{background:#ecfdf5;border:1px solid #a7f3d0;padding:16px;border-radius:8px;margin-bottom:20px}
        .banner strong{font-size:28px;color:#047857}
        table{width:100%;border-collapse:collapse;margin-top:12px;font-size:13px}
        th,td{border-bottom:1px solid #e2e8f0;padding:10px 8px;text-align:left}
        th{color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:.06em}
        .ai{background:#0c1324;color:#dce1fb;padding:16px;border-radius:8px;margin:20px 0;font-size:14px;line-height:1.5}
        @media print{button{display:none}}
      </style></head><body>
      <h1>EcoShield Compliance Report</h1>
      <div class="meta">${title}<br/>Generated ${new Date().toLocaleString()} · Ministry of Climate Change & Environment</div>
      <div class="banner"><strong>–34%</strong> carbon footprint if flagged replacements adopted<br/>Future fines avoided: <strong>$0</strong> (remediation path)</div>
      <div class="ai"><div style="color:#4edea3;font-size:11px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px">AI Summary</div>${summary}</div>
      <h3>Machine Audit</h3>
      <table><thead><tr><th>Machine</th><th>Risk</th><th>Replacement</th></tr></thead><tbody>
      ${machines
        .map(
          (m) =>
            `<tr><td>${m.name || m.machine}</td><td>${m.risk}</td><td>${m.replacement || '—'}</td></tr>`
        )
        .join('')}
      </tbody></table>
      <p style="margin-top:32px;font-size:11px;color:#94a3b8">EcoShield Environmental Intelligence · Confidential</p>
      <button onclick="window.print()" style="margin-top:16px;padding:10px 16px;background:#10b981;color:#fff;border:0;border-radius:6px;cursor:pointer">Print / Save PDF</button>
      </body></html>`);
    win.document.close();
  }

  function applySoftenedPins() {
    const softened = JSON.parse(localStorage.getItem('ecoshield_softened_pins') || '[]');
    document.querySelectorAll('.group.absolute, .group.absolute.z-50').forEach((pin) => {
      const label = pin.querySelector('div.absolute, div:last-child');
      const name = (label && label.textContent.trim()) || '';
      const hit = softened.find((s) => name.includes(s) || s.includes(name));
      if (!hit) return;
      pin.classList.add('es-pin-soften');
      pin.querySelectorAll('path').forEach((p) => {
        p.setAttribute('fill', '#fb923c');
      });
      const ping = pin.querySelector('.animate-ping');
      if (ping) {
        ping.style.background = '#fb923c';
        ping.style.opacity = '0.35';
      }
    });
  }

  function wireThermalToggle(mapSection) {
    if (!mapSection) return;
    const existing = document.getElementById('es-thermal-toggle');
    if (existing) return;

    const overlay = document.createElement('div');
    overlay.className = 'es-thermal-overlay';
    overlay.id = 'es-thermal-overlay';
    mapSection.classList.add('es-map');
    mapSection.appendChild(overlay);

    const btn = document.createElement('button');
    btn.id = 'es-thermal-toggle';
    btn.type = 'button';
    btn.textContent = 'Thermal Overlay: OFF';
    btn.style.cssText =
      'position:absolute;top:16px;right:16px;z-index:60;padding:8px 14px;border-radius:6px;border:1px solid #34D399;background:rgba(20,32,43,0.92);color:#34D399;font-family:Courier New,monospace;font-size:12px;cursor:pointer;letter-spacing:0.04em';
    btn.addEventListener('click', () => {
      const on = overlay.classList.toggle('on');
      mapSection.classList.toggle('thermal-mode', on);
      btn.textContent = on ? 'Thermal Overlay: ON' : 'Thermal Overlay: OFF';
      btn.style.background = on ? 'rgba(127,29,29,0.85)' : 'rgba(20,32,43,0.92)';
      btn.style.color = on ? '#FCA5A5' : '#34D399';
      btn.style.borderColor = on ? '#F87171' : '#34D399';
    });
    mapSection.appendChild(btn);
  }

  function initSiteDetail() {
    const card = document.querySelector('.bg-white.rounded-xl');
    if (!card) return;

    // Impact banner
    if (!document.getElementById('es-impact-banner')) {
      const banner = document.createElement('div');
      banner.id = 'es-impact-banner';
      banner.className = 'es-impact-banner';
      banner.innerHTML =
        '<div><div class="es-impact-num">–34%</div><div class="es-impact-sub">Policy simulation · if all flagged replacements adopted</div></div>' +
        '<div class="es-impact-stats">' +
        '<div class="es-impact-stat"><strong>–34%</strong><span>Carbon footprint</span></div>' +
        '<div class="es-impact-stat"><strong>$0</strong><span>Future fines</span></div>' +
        '<div class="es-impact-stat company-only"><strong>4</strong><span>Upgrade paths</span></div>' +
        '</div>';
      const tableSection = card.querySelector('.overflow-x-auto');
      if (tableSection) card.insertBefore(banner, tableSection);
    }

    // AI Summary panel
    if (!document.getElementById('es-ai-panel')) {
      const panel = document.createElement('div');
      panel.id = 'es-ai-panel';
      panel.className = 'es-ai-panel';
      panel.innerHTML =
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">' +
        '<h3 style="margin:0">AI Summary</h3>' +
        '<button id="es-gen-summary" type="button" style="padding:8px 14px;border-radius:6px;border:1px solid rgba(78,222,163,0.5);background:rgba(78,222,163,0.15);color:#4edea3;font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:0.06em;cursor:pointer;text-transform:uppercase">Generate Live Summary</button>' +
        '</div>' +
        '<div class="es-ai-badge" id="es-ai-source" style="display:none"><span class="dot"></span><span></span></div>' +
        '<div class="es-ai-body" id="es-ai-summary-text">Click “Generate Live Summary” to analyze this site’s machine table with a live LLM call.</div>';
      const tableSection = card.querySelector('.overflow-x-auto');
      if (tableSection) card.insertBefore(panel, tableSection);

      document.getElementById('es-gen-summary')?.addEventListener('click', async () => {
        const btn = document.getElementById('es-gen-summary');
        const body = document.getElementById('es-ai-summary-text');
        const badge = document.getElementById('es-ai-source');
        btn.disabled = true;
        btn.textContent = 'Generating…';
        body.textContent = 'Reading machine telemetry and calling model…';
        const result = await generateAiSummary();
        body.textContent = result.text;
        badge.style.display = 'inline-flex';
        badge.querySelector('span:last-child').textContent = result.source;
        btn.disabled = false;
        btn.textContent = 'Regenerate';
        if (result.needsKey) {
          const key = prompt(
            'Optional: paste a Gemini API key for a real live LLM summary (stored only in this browser). Leave blank to keep telemetry summary.\n\nGet a key at https://aistudio.google.com/apikey'
          );
          if (key && key.trim()) {
            localStorage.setItem('ECOSHIELD_GEMINI_KEY', key.trim());
            btn.click();
          }
        }
      });
    }

    // Upgrade trend chart section
    const analytics = document.querySelector('.mt-8.grid');
    if (analytics && !document.getElementById('es-trend-canvas')) {
      const trendCard = document.createElement('div');
      trendCard.className = 'hud-glass p-6 rounded-xl md:col-span-2';
      trendCard.innerHTML =
        '<div class="flex justify-between items-center mb-2 flex-wrap gap-2">' +
        '<h3 class="font-label-caps text-primary uppercase text-xs">Pollution Trend (90 days)</h3>' +
        '<div class="flex gap-2">' +
        '<button type="button" data-days="30" class="es-trend-btn px-3 py-1 text-[10px] border border-outline-variant rounded text-on-surface-variant">30D</button>' +
        '<button type="button" data-days="90" class="es-trend-btn px-3 py-1 text-[10px] border border-primary bg-primary/10 text-primary rounded">90D</button>' +
        '</div></div>' +
        '<p class="text-xs text-on-surface-variant mb-3">Compliant through March → gradual drift in June → critical breach this month.</p>' +
        '<div class="es-trend-wrap"><canvas id="es-trend-canvas"></canvas></div>';
      analytics.appendChild(trendCard);
      const canvas = document.getElementById('es-trend-canvas');
      drawTrendChart(canvas, 90);
      trendCard.querySelectorAll('.es-trend-btn').forEach((b) => {
        b.addEventListener('click', () => {
          trendCard.querySelectorAll('.es-trend-btn').forEach((x) => {
            x.className =
              'es-trend-btn px-3 py-1 text-[10px] border border-outline-variant rounded text-on-surface-variant';
          });
          b.className =
            'es-trend-btn px-3 py-1 text-[10px] border border-primary bg-primary/10 text-primary rounded';
          drawTrendChart(canvas, parseInt(b.dataset.days, 10));
        });
      });
    }

    // PDF export
    const reportBtn = Array.from(document.querySelectorAll('button')).find((b) =>
      /Generate Full Compliance Report/i.test(b.textContent || '')
    );
    if (reportBtn && !reportBtn.dataset.esPdf) {
      reportBtn.dataset.esPdf = '1';
      reportBtn.addEventListener('click', (e) => {
        e.preventDefault();
        exportPdfReport();
      });
    }

    // Company-view replacement CTA on fine column
    document.querySelectorAll('tbody tr').forEach((tr) => {
      const action = tr.querySelector('td:last-child');
      if (!action) return;
      const fineBtn = action.querySelector('button');
      if (!fineBtn || !/Impose Fine/i.test(fineBtn.textContent || '')) return;
      const companyBtn = document.createElement('button');
      companyBtn.className =
        'company-only border-2 border-emerald-500 text-emerald-700 px-4 py-2 rounded font-bold text-xs hover:bg-emerald-50 transition-colors uppercase';
      companyBtn.textContent = 'Request Upgrade';
      companyBtn.type = 'button';
      companyBtn.addEventListener('click', () => {
        companyBtn.textContent = 'Requested';
        companyBtn.disabled = true;
        showToast({ company: 'Procurement', sector: 'Upgrade request filed with vendor' });
      });
      action.appendChild(companyBtn);
    });

    const params = new URLSearchParams(location.search);
    wireImposeFines(params.get('company') || 'Site operator');
  }

  function initAiSignals() {
    const main = document.querySelector('main');
    if (!main) return;

    // Leaderboard dock
    if (!document.getElementById('es-leaderboard-mount')) {
      const dock = document.createElement('div');
      dock.id = 'es-leaderboard-mount';
      dock.style.cssText =
        'position:absolute;top:72px;right:24px;width:300px;z-index:25;max-height:calc(100vh - 160px);overflow:auto';
      main.appendChild(dock);
      renderLeaderboard(dock);
    }

    wireImposeFines();
  }

  function initMap() {
    const mapArea = document.querySelector('.map-area');
    if (!mapArea) return;
    // MapTiler page has its own Terrain/Satellite/Heat controls
    if (!document.getElementById('es-maptiler')) {
      wireThermalToggle(mapArea);
    }
    applySoftenedPins();
  }

  function initCommon() {
    // inject CSS if needed
    if (!document.querySelector('link[href*="ecoshield-live.css"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = new URL('ecoshield-live.css', document.currentScript?.src || '../shared/ecoshield-live.js')
        .href.replace(/ecoshield-live\.js.*/, 'ecoshield-live.css');
      document.head.appendChild(link);
    }

    document.body.setAttribute('data-role', getRole());

    // Role toggle in header nav areas
    const headerRight =
      document.getElementById('es-header-actions') ||
      document.querySelector('header .flex.items-center.gap-4') ||
      document.querySelector('header .flex.items-center.space-x-4') ||
      document.querySelector('header .flex.items-center.gap-panel-gap') ||
      document.querySelector('nav.flex.gap-8')?.parentElement?.querySelector('.flex.items-center.gap-4') ||
      document.querySelector('header > div:last-child');
    if (headerRight) mountRoleToggle(headerRight);

    startLiveDetections(15000);

    const path = location.pathname;
    if (path.includes('site_detail')) initSiteDetail();
    if (path.includes('ai_signals')) initAiSignals();
    if (path.includes('uae_regional') || path.includes('geo_map')) initMap();

    // Dashboard also gets leaderboard teaser in side panel
    if (path.includes('ecoshield_dashboard')) {
      const aside = document.querySelector('aside.absolute');
      if (aside && !document.getElementById('es-leaderboard-mount')) {
        const mount = document.createElement('div');
        mount.id = 'es-leaderboard-mount';
        mount.style.cssText = 'padding:0 12px 12px';
        aside.insertBefore(mount, aside.querySelector('.p-3.border-t'));
        renderLeaderboard(mount);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCommon);
  } else {
    initCommon();
  }

  global.EcoShieldLive = {
    showToast,
    generateAiSummary,
    exportPdfReport,
    setRole,
    getRole,
    renderLeaderboard,
    drawTrendChart
  };
})(window);
