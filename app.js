// YESPYQ — question-bank browser (left filters + show-all). Compact data keys: i,q,o,a,s,c,y

const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

const subjectMap = Object.fromEntries(SUBJECTS.map(s => [s.id, s]));
const byId = Object.fromEntries(QUESTIONS.map(q => [q.i, q]));
const YEARS = [...new Set(QUESTIONS.map(q => q.y))].filter(Boolean).sort((a, b) => b - a);
const PAGE = 15;

/* ---------- minimal gamification (header streak + XP) ---------- */
const GKEY = "yespyq_game_v1";
function loadGame() { try { return JSON.parse(localStorage.getItem(GKEY)) || {}; } catch { return {}; } }
function saveGame() { try { localStorage.setItem(GKEY, JSON.stringify(game)); } catch {} }
const game = Object.assign({ xp: 0, streak: 0, lastDay: null }, loadGame());
const today = () => new Date().toISOString().slice(0, 10);
function yesterday() { const d = new Date(); d.setDate(d.getDate() - 1); return d.toISOString().slice(0, 10); }
const answered = new Set();
function earnXp(n) {
  const t = today();
  if (game.lastDay !== t) { game.streak = (game.lastDay === yesterday()) ? game.streak + 1 : 1; game.lastDay = t; }
  game.xp += n; saveGame(); renderGameStats();
}
function renderGameStats() {
  $("#game-stats").innerHTML =
    `<div class="gs-item gs-streak" title="Day streak">🔥<b>${game.streak}</b></div>
     <div class="gs-item gs-xp" title="Total XP">⚡<b>${game.xp}</b></div>`;
}
function floatXp(x, y, t) {
  const el = document.createElement("div"); el.className = "xp-pop"; el.textContent = t;
  el.style.left = x + "px"; el.style.top = y + "px"; $("#fx-layer").appendChild(el);
  setTimeout(() => el.remove(), 1000);
}

/* ---------- navigation ---------- */
function showView(name) {
  $$(".view").forEach(v => v.classList.add("hidden"));
  $(`#view-${name}`)?.classList.remove("hidden");
  $$(".main-nav a").forEach(a => a.classList.toggle("active", a.dataset.nav === name));
  window.scrollTo({ top: 0 });
}

/* ---------- home grids ---------- */
const countBySubject = id => QUESTIONS.filter(q => q.s === id).length;
const countByYear = y => QUESTIONS.filter(q => q.y === y).length;

function subjectCardHTML(s) {
  return `<div class="subject-card" data-subject="${s.id}">
      <div class="ico">${s.icon}</div><h3>${s.name}</h3>
      <p>UPSC CSE Prelims PYQs</p>
      <span class="count">${countBySubject(s.id)} questions</span></div>`;
}
function renderSubjects() {
  const html = SUBJECTS.map(subjectCardHTML).join("");
  $("#home-subjects").innerHTML = html; $("#all-subjects").innerHTML = html;
}
function renderYears() {
  $("#home-years").innerHTML = YEARS.slice(0, 12).map(y =>
    `<div class="year-card" data-year="${y}"><b>${y}</b><span>${countByYear(y)} questions</span></div>`
  ).join("");
}

/* ============================================================
   BROWSE  (filters + show-all)
   ============================================================ */
const filter = { subject: null, year: null };
let shown = 0;

function currentList() {
  return QUESTIONS.filter(q =>
    (!filter.subject || q.s === filter.subject) && (!filter.year || q.y === filter.year));
}

function openBrowse(f) {
  filter.subject = f && "subject" in f ? f.subject : filter.subject;
  filter.year = f && "year" in f ? f.year : filter.year;
  showView("practice");
  renderFilters();
  applyFilter();
  $("#filters").classList.remove("open");
}

function renderFilters() {
  const subs = SUBJECTS.map(s =>
    `<button class="f-item ${filter.subject === s.id ? "active" : ""}" data-fsub="${s.id}">
       <span>${s.icon} ${s.name}</span><em>${countBySubject(s.id)}</em></button>`).join("");
  const yrs = YEARS.map(y =>
    `<button class="f-item ${filter.year === y ? "active" : ""}" data-fyear="${y}">
       <span>${y}</span><em>${countByYear(y)}</em></button>`).join("");
  $("#filters").innerHTML = `
    <div class="f-group">
      <h4>Subject</h4>
      <button class="f-item ${!filter.subject ? "active" : ""}" data-fsub=""><span>All subjects</span><em>${QUESTIONS.length}</em></button>
      ${subs}
    </div>
    <div class="f-group">
      <h4>Year</h4>
      <button class="f-item ${!filter.year ? "active" : ""}" data-fyear=""><span>All years</span></button>
      ${yrs}
    </div>`;
}

function applyFilter() {
  const list = currentList();
  const subName = filter.subject ? subjectMap[filter.subject].name : "All Questions";
  const yr = filter.year ? ` · ${filter.year}` : "";
  $("#qlist-title").textContent = subName + yr;
  $("#qlist-count").textContent = `${list.length} question${list.length === 1 ? "" : "s"}`;
  $("#qlist").innerHTML = "";
  shown = 0;
  renderMore();
  window.scrollTo({ top: 0 });
}

function cardHTML(q, serial) {
  const opts = q.o.map((opt, i) =>
    `<button class="option" data-opt="${i}"><span class="key">${String.fromCharCode(97 + i)}</span><span>${escapeHTML(opt)}</span></button>`).join("");
  return `<article class="qcard" data-qid="${q.i}">
      <div class="qtags">
        <span class="qnum">Q${serial}</span>
        <span class="qtag">${subjectMap[q.s].icon} ${subjectMap[q.s].name}</span>
        ${q.y ? `<span class="qtag">${q.y}</span>` : ""}
      </div>
      <div class="qtext">${formatBody(q.q)}</div>
      <div class="options">${opts}</div>
      <div class="explain hidden" data-exp></div>
    </article>`;
}

function renderMore() {
  const list = currentList();
  const next = list.slice(shown, shown + PAGE);
  const frag = document.createElement("div");
  frag.innerHTML = next.map((q, k) => cardHTML(q, shown + k + 1)).join("");
  const wrap = $("#qlist");
  while (frag.firstChild) wrap.appendChild(frag.firstChild);
  shown += next.length;
  const more = $("#load-more");
  more.classList.toggle("hidden", shown >= list.length);
  if (shown < list.length) more.textContent = `Show more (${list.length - shown} left)`;
}

/* reveal answer on option click (delegated) */
$("#qlist").addEventListener("click", e => {
  const opt = e.target.closest(".option");
  if (!opt) return;
  const card = opt.closest(".qcard");
  if (card.dataset.done) return;
  const q = byId[card.dataset.qid];
  const chosen = +opt.dataset.opt;
  const correct = chosen === q.a;
  card.dataset.done = "1";
  card.querySelectorAll(".option").forEach((o, i) => {
    o.classList.add("locked");
    if (i === q.a) o.classList.add("correct");
    else if (i === chosen) o.classList.add("wrong");
    else o.classList.add("dim");
  });
  const expl = (window.EXP && window.EXP[q.i]) || "Explanation will appear here.";
  const ex = card.querySelector("[data-exp]");
  ex.innerHTML = `
    <div class="verdict ${correct ? "ok" : "no"}">${correct ? "✓ Correct" : "✗ Incorrect"} — Answer: ${String.fromCharCode(97 + q.a)}) ${escapeHTML(q.o[q.a])}</div>
    <div class="exp-body"><span class="lbl">Explanation</span>${formatBody(expl)}</div>`;
  ex.classList.remove("hidden");
  if (correct && !answered.has(q.i)) {
    answered.add(q.i);
    earnXp(10);
    const r = opt.getBoundingClientRect();
    floatXp(r.right - 56, r.top, "+10 XP");
  }
});

/* ---------- global click routing ---------- */
document.addEventListener("click", e => {
  const nav = e.target.closest("[data-nav]");
  if (nav) { e.preventDefault(); const n = nav.dataset.nav; n === "practice" ? openBrowse({}) : showView(n); return; }
  if (e.target.closest("[data-action='start']")) { e.preventDefault(); openBrowse({ subject: null, year: null }); return; }
  const sc = e.target.closest("[data-subject]");
  if (sc) { openBrowse({ subject: sc.dataset.subject, year: null }); return; }
  const yc = e.target.closest("[data-year]");
  if (yc) { openBrowse({ subject: null, year: +yc.dataset.year }); return; }
  const fs = e.target.closest("[data-fsub]");
  if (fs) { filter.subject = fs.dataset.fsub || null; renderFilters(); applyFilter(); return; }
  const fy = e.target.closest("[data-fyear]");
  if (fy) { filter.year = fy.dataset.fyear ? +fy.dataset.fyear : null; renderFilters(); applyFilter(); return; }
  if (e.target.closest("#filter-toggle")) { $("#filters").classList.toggle("open"); return; }
  if (e.target.closest("#load-more")) { renderMore(); }
});

/* ---------- util ---------- */
function escapeHTML(str) { return String(str).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); }

/* Turn a flat run-on question/explanation string into readable, spaced lines:
   numbered statements (1. 2. 3.) each on their own line, and natural paragraph
   breaks before "Statement N ..." and the closing question/instruction.
   Guards against decimals (2.5) and initials (S.) — those need a space after
   the dot to break, which they never have. */
function formatBody(raw) {
  let t = escapeHTML(String(raw)).replace(/\s+/g, " ").trim();
  // break before an enumerated statement marker: " 1. " -> new line "1. "
  t = t.replace(/\s+(\d{1,2})\.\s+/g, "\n$1. ");
  // break before "Statement N" chunks in explanations
  t = t.replace(/\s+(Statement\s+\d+\b)/g, "\n$1");
  // break before the closing question / instruction of a stem
  t = t.replace(/\s+(How many of the |Which of the statements |Which of the above |Which one of the following |Select the correct answer |Consider the following codes |With reference to the above )/g, "\n$1");
  const lines = t.split("\n").map(s => s.trim()).filter(Boolean);
  return lines
    .map(line => `<span class="bline${/^\d{1,2}\.\s/.test(line) ? " stmt" : ""}">${line}</span>`)
    .join("");
}

/* ---------- init ---------- */
renderSubjects();
renderYears();
renderGameStats();
$("#year").textContent = new Date().getFullYear();
showView("home");
