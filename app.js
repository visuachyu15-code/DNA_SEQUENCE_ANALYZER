// ============================================
// DNA Substring Analyzer — App Logic
// ============================================

// ─── Floating DNA Helix Background ───
(function initDNA() {
    const canvas = document.getElementById('dnaCanvas');
    const ctx = canvas.getContext('2d');

    let W, H;
    const strands = [];

    function resize() {
        W = canvas.width  = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }

    window.addEventListener('resize', resize);
    resize();

    const BASES = ['A', 'C', 'G', 'T'];
    const BASE_COLOR = { A: '#22d3ee', C: '#a78bfa', G: '#34d399', T: '#fb923c' };

    // Create several vertical DNA helix columns
    function createStrand(x) {
        return {
            x,
            offset: Math.random() * Math.PI * 2,
            speed: 0.003 + Math.random() * 0.003,
            spacing: 28 + Math.random() * 10,
            amplitude: 22 + Math.random() * 14,
            opacity: 0.12 + Math.random() * 0.18,
            bases: Array.from({ length: 30 }, () => BASES[Math.floor(Math.random() * 4)])
        };
    }

    function initStrands() {
        strands.length = 0;
        const count = Math.max(4, Math.floor(W / 160));
        for (let i = 0; i < count; i++) {
            strands.push(createStrand((i + 0.5) * (W / count)));
        }
    }

    initStrands();
    window.addEventListener('resize', initStrands);

    let t = 0;

    function draw() {
        ctx.clearRect(0, 0, W, H);
        t += 1;

        for (const s of strands) {
            const phase = t * s.speed + s.offset;
            const rows = Math.ceil(H / s.spacing) + 2;

            for (let i = 0; i < rows; i++) {
                const y = (i * s.spacing - (t * 0.35) % s.spacing + H) % H;
                const xLeft  = s.x + Math.sin(phase + i * 0.55) * s.amplitude;
                const xRight = s.x - Math.sin(phase + i * 0.55) * s.amplitude;
                const base = s.bases[i % s.bases.length];
                const col  = BASE_COLOR[base];

                // Backbone dots
                ctx.beginPath();
                ctx.arc(xLeft, y, 2.5, 0, Math.PI * 2);
                ctx.fillStyle = hexToRgba('#00d4aa', s.opacity * 0.6);
                ctx.fill();

                ctx.beginPath();
                ctx.arc(xRight, y, 2.5, 0, Math.PI * 2);
                ctx.fillStyle = hexToRgba('#7c6fcd', s.opacity * 0.6);
                ctx.fill();

                // Rung (bridge between strands)
                ctx.beginPath();
                ctx.moveTo(xLeft, y);
                ctx.lineTo(xRight, y);
                ctx.strokeStyle = hexToRgba(col, s.opacity * 0.35);
                ctx.lineWidth = 1;
                ctx.stroke();

                // Base letter
                ctx.font = '500 9px JetBrains Mono, monospace';
                ctx.fillStyle = hexToRgba(col, s.opacity * 0.8);
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(base, (xLeft + xRight) / 2, y);
            }

            // Backbone curves (smooth spine lines)
            ctx.beginPath();
            for (let i = 0; i < rows; i++) {
                const y = (i * s.spacing - (t * 0.35) % s.spacing + H) % H;
                const x = s.x + Math.sin(phase + i * 0.55) * s.amplitude;
                i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
            }
            ctx.strokeStyle = hexToRgba('#00d4aa', s.opacity * 0.25);
            ctx.lineWidth = 1.2;
            ctx.stroke();

            ctx.beginPath();
            for (let i = 0; i < rows; i++) {
                const y = (i * s.spacing - (t * 0.35) % s.spacing + H) % H;
                const x = s.x - Math.sin(phase + i * 0.55) * s.amplitude;
                i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
            }
            ctx.strokeStyle = hexToRgba('#7c6fcd', s.opacity * 0.25);
            ctx.lineWidth = 1.2;
            ctx.stroke();
        }

        requestAnimationFrame(draw);
    }

    draw();

    function hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r},${g},${b},${alpha})`;
    }
})();


// ─── Input handlers ───
const seq1El  = document.getElementById('seq1');
const seq2El  = document.getElementById('seq2');
const cnt1El  = document.getElementById('count1');
const cnt2El  = document.getElementById('count2');

seq1El.addEventListener('input', () => {
    seq1El.value = seq1El.value.toUpperCase().replace(/[^ACGT]/g, '');
    cnt1El.textContent = seq1El.value.length;
});
seq2El.addEventListener('input', () => {
    seq2El.value = seq2El.value.toUpperCase().replace(/[^ACGT]/g, '');
    cnt2El.textContent = seq2El.value.length;
});
seq1El.addEventListener('keydown', e => { if (e.key === 'Enter') analyze(); });
seq2El.addEventListener('keydown', e => { if (e.key === 'Enter') analyze(); });

function loadExample() {
    seq1El.value = 'ACGTAC'; cnt1El.textContent = 6;
    seq2El.value = 'TTACGA'; cnt2El.textContent = 6;
}

function clearAll() {
    seq1El.value = seq2El.value = '';
    cnt1El.textContent = cnt2El.textContent = '0';
    document.getElementById('results').classList.add('hidden');
    document.getElementById('errorMsg').classList.add('hidden');
}

// ─── Analyze ───
async function analyze() {
    const s1 = seq1El.value.trim().toUpperCase();
    const s2 = seq2El.value.trim().toUpperCase();
    const errEl = document.getElementById('errorMsg');
    const resEl = document.getElementById('results');
    const btn   = document.getElementById('analyzeBtn');

    errEl.classList.add('hidden');

    if (!s1 && !s2) { showErr('Please enter at least one DNA sequence.'); return; }

    btn.disabled = true;
    btn.style.opacity = '0.6';

    try {
        const res  = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ s1, s2 })
        });
        const data = await res.json();

        if (!res.ok) { showErr(data.error || 'Something went wrong.'); return; }

        render(data);
        resEl.classList.remove('hidden');
        resEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch {
        showErr('Cannot reach the server. Make sure it is running.');
    } finally {
        btn.disabled = false;
        btn.style.opacity = '1';
    }
}

function showErr(msg) {
    const el = document.getElementById('errorMsg');
    el.textContent = msg;
    el.classList.remove('hidden');
}

// ─── Render results ───
function render(data) {
    document.getElementById('resSubstring').textContent = data.substring || 'None';
    document.getElementById('resLength').textContent    = data.length;

    renderSeq('vizS1', data.s1, data.substring);
    renderSeq('vizS2', data.s2, data.substring);
    renderDP(data.s1, data.s2, data.dp_table, data.length);
}

function renderSeq(id, seq, match) {
    const el = document.getElementById(id);
    el.innerHTML = '';
    if (!seq) {
        const s = document.createElement('span');
        s.className = 'ch'; s.textContent = '∅'; s.style.color = '#334155';
        el.appendChild(s); return;
    }
    const startIdx = match ? seq.indexOf(match) : -1;
    const endIdx   = startIdx >= 0 ? startIdx + match.length : -1;

    for (let i = 0; i < seq.length; i++) {
        const span = document.createElement('span');
        span.className = `ch ${seq[i]}`;
        if (startIdx >= 0 && i >= startIdx && i < endIdx) span.classList.add('lit');
        span.textContent = seq[i];
        span.style.animationDelay = (i * 0.03) + 's';
        el.appendChild(span);
    }
}

function renderDP(s1, s2, dp, maxLen) {
    const tbl = document.getElementById('dpTable');
    tbl.innerHTML = '';
    if (!dp || !dp.length) return;

    const n = s1.length, m = s2.length;

    // Header row
    const hdr = tbl.insertRow();
    addTh(hdr, '');
    addTh(hdr, 'ε', '');
    for (let j = 0; j < m; j++) {
        const th = document.createElement('th');
        th.textContent = s2[j]; th.className = 'ch-hdr'; hdr.appendChild(th);
    }

    for (let i = 0; i <= n; i++) {
        const tr = tbl.insertRow();
        const rh = document.createElement('th');
        rh.textContent = i === 0 ? 'ε' : s1[i - 1];
        rh.className = 'rw-hdr'; tr.appendChild(rh);

        for (let j = 0; j <= m; j++) {
            const td = tr.insertCell();
            const v  = dp[i][j];
            td.textContent = v;
            if (v === maxLen && maxLen > 0) td.className = 'peak';
            else if (v > 0)                td.className = 'nonzero';
        }
    }
}

function addTh(row, text, cls) {
    const th = document.createElement('th');
    th.textContent = text;
    if (cls !== undefined) th.className = cls;
    row.appendChild(th);
}
