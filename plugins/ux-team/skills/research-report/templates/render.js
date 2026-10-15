const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const chev = '<svg aria-hidden="true"><use href="#chev"/></svg>';
const bm = '<svg aria-hidden="true"><use href="#bm"/></svg>';

function answer(q, r) {
  if (!r) return '<p class="follow">답하지 않음</p>';
  if (r.seq) {
    return `<div class="seq">${r.seq.map((k, i) => `<span class="step"><span class="chip"><b>${k}</b>${esc(q.opts[k])}</span>${i < r.seq.length - 1 ? chev : ''}</span>`).join('')}</div>`;
  }
  let html = Array.isArray(r.a)
    ? `<div class="chips">${r.a.map((c) => `<span class="chip">${esc(c)}</span>`).join('')}${r.o ? `<span class="chip other">${esc(r.o)}</span>` : ''}</div>`
    : `<p class="text">${esc(r.a)}</p>`;
  if (r.x) html += `${q.xq ? `<p class="follow">${esc(q.xq)}</p>` : ''}<p class="text">${esc(r.x)}</p>`;
  return html;
}

function row(q, inner) {
  return `<div class="row">
    <div class="num">${q.n}${q.star ? bm : ''}</div>
    <div><p class="q">${esc(q.q)}</p>${inner}</div>
  </div>`;
}

function renderSolo(id, key) {
  let html = '';
  let group = '';
  for (const q of QS) {
    if (q.g !== group) {
      group = q.g;
      if (q.g) html += `<h3 class="qa-head">${esc(GROUPS[q.g])}</h3>`;
    }
    html += row(q, `<div class="a">${answer(q, q[key])}</div>`);
  }
  document.getElementById(id).innerHTML = html;
}

function renderPairs(id) {
  const [a, b] = PEOPLE;
  const names = `<div class="names" aria-hidden="true"><span></span><div class="duo"><div class="col"><i class="mk p1"></i>${esc(a.name)}</div><div class="col"><i class="mk p2"></i>${esc(b.name)}</div></div></div>`;
  let html = '';
  let group = '';
  for (const q of QS) {
    if (q.g !== group) {
      group = q.g;
      if (q.g) html += `<h3 class="qa-head">${esc(GROUPS[q.g])}</h3>`;
      html += names;
    }
    html += row(q, `<div class="pair duo">
      <div class="col" data-who="${esc(a.name)}">${answer(q, q[a.key])}</div>
      <div class="col" data-who="${esc(b.name)}">${answer(q, q[b.key])}</div>
    </div>`);
  }
  document.getElementById(id).innerHTML = html;
}
