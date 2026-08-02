// YESPYQ — question-bank browser (left filters + show-all). Compact data keys: i,q,o,a,s,c,y

const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

/* JEE/NEET/Board content carries LaTeX (\(...\) / \[...\]); KaTeX is
   loaded lazily (see loadKatex()) the first time any such content is
   about to render, then re-run on every dynamic re-render. */
let katexLoading = null;
function loadKatex() {
  if (window.renderMathInElement) return Promise.resolve();
  if (katexLoading) return katexLoading;
  const css = document.createElement("link");
  css.rel = "stylesheet"; css.href = "/assets/katex/katex.min.css";
  document.head.appendChild(css);
  katexLoading = new Promise(resolve => {
    const s1 = document.createElement("script");
    s1.src = "/assets/katex/katex.min.js";
    s1.onload = () => {
      const s2 = document.createElement("script");
      s2.src = "/assets/katex/auto-render.min.js";
      s2.onload = resolve;
      s2.onerror = resolve;
      document.head.appendChild(s2);
    };
    s1.onerror = resolve;
    document.head.appendChild(s1);
  });
  return katexLoading;
}
function renderMath(el) {
  if (!el) return;
  loadKatex().then(() => {
    if (!window.renderMathInElement) return;
    renderMathInElement(el, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "\\[", right: "\\]", display: true },
        { left: "\\(", right: "\\)", display: false }
      ],
      throwOnError: false
    });
  });
}

/* ---------- multi-exam banks ---------- */
const UPSC_SUBJECTS = SUBJECTS.slice();
const UPSC_QUESTIONS = QUESTIONS.slice();

const EXAM_META = {
  upsc: {
    id: "upsc", name: "UPSC", full: "UPSC (CSE Prelims)", quiz: true, file: null,
    subjects: UPSC_SUBJECTS
  },
  jee: {
    id: "jee", name: "JEE", full: "JEE (Main & Advanced)", quiz: false, file: "/exam-data/jee.json",
    subjects: [
      { id: "physics", name: "Physics", icon: "🧲" },
      { id: "chemistry", name: "Chemistry", icon: "🧪" },
      { id: "maths", name: "Maths", icon: "➗" }
    ]
  },
  neet: {
    id: "neet", name: "NEET", full: "NEET-UG", quiz: false, file: "/exam-data/neet.json",
    subjects: [
      { id: "physics", name: "Physics", icon: "🧲" },
      { id: "chemistry", name: "Chemistry", icon: "🧪" },
      { id: "biology", name: "Biology", icon: "🧬" }
    ]
  },
  "ssc-cgl": {
    id: "ssc-cgl", name: "SSC CGL", full: "SSC CGL", quiz: false, file: "/exam-data/ssc-cgl.json",
    subjects: [
      { id: "english", name: "English", icon: "🔤" },
      { id: "history", name: "History", icon: "🏛️" },
      { id: "economy", name: "Economy", icon: "📈" },
      { id: "aptitude", name: "Quantitative Aptitude", icon: "🔢" },
      { id: "reasoning", name: "Reasoning", icon: "🧩" },
      { id: "computer", name: "Computer", icon: "💻" },
      { id: "geography", name: "Geography", icon: "🌍" },
      { id: "science", name: "Science", icon: "🔬" },
      { id: "gk", name: "General Knowledge", icon: "🌐" },
      { id: "polity", name: "Polity", icon: "⚖️" }
    ]
  },
  board: {
    id: "board", name: "Boards", full: "Board Exams", quiz: false, file: "/exam-data/board.json",
    subjects: [
      { id: "physics", name: "Physics", icon: "🧲" },
      { id: "chemistry", name: "Chemistry", icon: "🧪" },
      { id: "maths", name: "Maths", icon: "➗" },
      { id: "biology", name: "Biology", icon: "🧬" },
      { id: "english", name: "English", icon: "🔤" },
      { id: "hindi", name: "Hindi", icon: "🪔" },
      { id: "history", name: "History", icon: "🏛️" },
      { id: "geography", name: "Geography", icon: "🌍" },
      { id: "polity", name: "Political Science", icon: "⚖️" },
      { id: "economics", name: "Economics", icon: "📈" },
      { id: "accountancy", name: "Accountancy", icon: "📒" },
      { id: "business-studies", name: "Business Studies", icon: "💼" },
      { id: "social-studies", name: "Social Studies", icon: "🌏" },
      { id: "psychology", name: "Psychology", icon: "🧠" },
      { id: "sociology", name: "Sociology", icon: "👥" },
      { id: "general", name: "General", icon: "📘" }
    ]
  },
  defence: {
    id: "defence", name: "Defence", full: "Defence Exams", quiz: false, file: "/exam-data/defence.json",
    subjects: [
      { id: "staticgk", name: "Static GK", icon: "🌐" },
      { id: "currentaff", name: "Current Affairs", icon: "🗞️" },
      { id: "economy", name: "Economics", icon: "📈" },
      { id: "history", name: "History", icon: "🏛️" },
      { id: "polity", name: "Polity", icon: "⚖️" },
      { id: "english", name: "English", icon: "🔤" },
      { id: "geography", name: "Geography", icon: "🌍" }
    ]
  }
};

let currentExam = "upsc";
let subjectMap = Object.fromEntries(SUBJECTS.map(s => [s.id, s]));
let byId = Object.fromEntries(QUESTIONS.map(q => [q.i, q]));
let YEARS = [...new Set(QUESTIONS.map(q => q.y))].filter(Boolean).sort((a, b) => b - a);
const bankCache = {};
const PAGE = 15;

function rebuildIndexes() {
  subjectMap = Object.fromEntries(SUBJECTS.map(s => [s.id, s]));
  byId = Object.fromEntries(QUESTIONS.map(q => [q.i, q]));
  YEARS = [...new Set(QUESTIONS.map(q => q.y))].filter(Boolean).sort((a, b) => b - a);
}

function normalizeExamQ(raw) {
  return {
    i: raw.i,
    q: raw.q,
    o: raw.o,
    a: raw.a,
    s: raw.s || raw.subject,
    c: raw.c || raw.chapter || "",
    y: raw.y || null,
    exp: raw.exp || "",
    fmt: raw.fmt || null
  };
}

/* mock-pool.json holds ONLY the same ~10% free-preview questions that are
   fully visible on the static /exams/<exam>/ pages — never the full gated
   bank. One shared fetch, filtered client-side per exam. (The old code
   fetched /exam-data/<exam>.json directly, which contained every answer
   for every question, gated or not — that file is no longer public.) */
let mockPoolPromise = null;
function ensureMockPool() {
  if (!mockPoolPromise) {
    mockPoolPromise = fetch("/mock-pool.json").then(res => {
      if (!res.ok) throw new Error("Failed to load mock-pool.json");
      return res.json();
    });
  }
  return mockPoolPromise;
}

async function ensureExamBank(examId) {
  const meta = EXAM_META[examId];
  if (!meta) throw new Error("Unknown exam: " + examId);
  if (examId === "upsc") {
    return { questions: UPSC_QUESTIONS, subjects: UPSC_SUBJECTS };
  }
  if (bankCache[examId]) return bankCache[examId];
  const pool = await ensureMockPool();
  const questions = pool.filter(x => x.exam === examId).map(normalizeExamQ).filter(isCleanQ);
  const bank = { questions, subjects: meta.subjects };
  bankCache[examId] = bank;
  return bank;
}

async function setExam(examId, opts) {
  opts = opts || {};
  const meta = EXAM_META[examId] || EXAM_META.upsc;
  const status = $("#qlist-title");
  // Switch to the practice view and show a visible loading state RIGHT
  // AWAY, before the (possibly slow, ~490KB) exam-bank fetch — otherwise
  // the click does nothing on screen until the fetch resolves, which reads
  // as "the button doesn't work" rather than "it's loading".
  if (opts.mode !== "quiz" && opts.showLoading !== false) {
    showView("practice");
    const list = $("#qlist");
    if (list) list.innerHTML = '<p class="qlist-loading">Loading questions…</p>';
    const count = $("#qlist-count");
    if (count) count.textContent = "";
  }
  if (status && opts.showLoading !== false) status.textContent = "Loading " + meta.full + "…";
  try {
    const bank = await ensureExamBank(meta.id);
    currentExam = meta.id;
    SUBJECTS.length = 0;
    SUBJECTS.push(...bank.subjects);
    QUESTIONS.length = 0;
    QUESTIONS.push(...bank.questions);
    rebuildIndexes();
    filter.subject = ("subject" in opts) ? opts.subject : null;
    filter.year = ("year" in opts) ? opts.year : null;
    if (opts.mode === "quiz" && meta.quiz) {
      openQuizSetup();
    } else {
      openBrowse({ subject: filter.subject, year: filter.year });
    }
  } catch (err) {
    console.error(err);
    if (status) status.textContent = "Could not load exam bank";
    alert("Could not load " + meta.full + " questions. Please try again.");
  }
}

/* Drop questions whose source OCR is corrupted — truncated stems ending in
   "Option", options carrying explanation text / embedded sub-questions, or
   punctuation-only options. Keeps the visible bank trustworthy. */
function isCleanQ(x) {
  const qq = (x.q || "").trim(), opts = x.o || [], a = x.a;
  if (opts.length !== 4 || qq.length < 12) return false;
  // Single-correct MCQ only
  if (Array.isArray(a) || (x && x.kind === "multi")) return false;
  if (typeof a !== "number" || a < 0 || a >= opts.length) return false;
  const plainQ = qq.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  if (/\bOptions?\s*$/.test(plainQ)) return false;             // truncated stem
  const BAD = /consider the following|incorrect\s*:|correct\s*:|\([a-d]\)\s|\(20\d\d\)|select the correct answer/i;
  const maxOpt = x.fmt === "html" ? 600 : 180;
  for (let o of opts) {
    const raw = (o || "").trim();
    const plain = raw.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
    if (plain.length < 1 || plain.length > maxOpt) return false;
    if (plain.length <= 2 && !/^[a-z0-9]+$/i.test(plain)) return false;
    if (BAD.test(plain)) return false;
  }
  return true;
}
if (typeof QUESTIONS !== "undefined" && Array.isArray(QUESTIONS)) {
  const clean = QUESTIONS.filter(isCleanQ);
  if (clean.length && clean.length < QUESTIONS.length) { QUESTIONS.length = 0; QUESTIONS.push(...clean); }
  UPSC_QUESTIONS.length = 0;
  UPSC_QUESTIONS.push(...QUESTIONS);
  rebuildIndexes();
}

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
  const xpEl = $(".gs-xp"); if (xpEl) { xpEl.classList.remove("bump"); void xpEl.offsetWidth; xpEl.classList.add("bump"); }
}
function renderGameStats() {
  const el = $("#game-stats");
  if (!el) return;               // header streak/XP pills were cut (confusing at 0 for new visitors);
                                  // streak/XP still tracked and shown via floatXp() during a quiz
  el.innerHTML =
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
  if (name !== "exam" && typeof examState !== "undefined" && examState && examState.timerId) stopExamTimer();
  $$(".view").forEach(v => v.classList.add("hidden"));
  $(`#view-${name}`)?.classList.remove("hidden");
  $$(".main-nav a").forEach(a => a.classList.toggle("active", a.dataset.nav === name));
  document.body.classList.toggle("in-quiz", name === "quiz");
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
  const home = $("#home-subjects"), all = $("#all-subjects");
  if (home) home.innerHTML = html;
  if (all) all.innerHTML = html;
}
function renderYears() {
  const el = $("#home-years");
  if (!el) return;
  el.innerHTML = YEARS.slice(0, 12).map(y =>
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
  document.body.classList.remove("filters-open");
}

function setFiltersOpen(on) {
  const el = $("#filters");
  if (!el) return;
  el.classList.toggle("open", !!on);
  document.body.classList.toggle("filters-open", !!on);
}
function closeFilters() { setFiltersOpen(false); }

function renderFilters() {
  const exams = Object.values(EXAM_META).map(ex =>
    `<button class="f-item ${currentExam === ex.id ? "active" : ""}" data-fexam="${ex.id}">
       <span>${ex.name}</span></button>`).join("");
  const subs = SUBJECTS.map(s =>
    `<button class="f-item ${filter.subject === s.id ? "active" : ""}" data-fsub="${s.id}">
       <span>${s.icon} ${s.name}</span><em>${countBySubject(s.id)}</em></button>`).join("");
  const yearBlock = YEARS.length ? `
    <div class="f-group">
      <h4>Year</h4>
      <button class="f-item ${!filter.year ? "active" : ""}" data-fyear=""><span>All years</span></button>
      ${YEARS.map(y =>
        `<button class="f-item ${filter.year === y ? "active" : ""}" data-fyear="${y}">
           <span>${y}</span><em>${countByYear(y)}</em></button>`).join("")}
    </div>` : "";
  $("#filters").innerHTML = `
    <div class="f-panel-top">
      <strong>Filters</strong>
      <button type="button" class="f-close" id="filter-close" aria-label="Close filters">✕</button>
    </div>
    <div class="f-group">
      <h4>Exam</h4>
      ${exams}
    </div>
    <div class="f-group">
      <h4>Subject</h4>
      <button class="f-item ${!filter.subject ? "active" : ""}" data-fsub=""><span>All subjects</span><em>${QUESTIONS.length}</em></button>
      ${subs}
    </div>
    ${yearBlock}`;
}

function applyFilter() {
  const list = currentList();
  const examName = (EXAM_META[currentExam] || EXAM_META.upsc).name;
  const subName = filter.subject && subjectMap[filter.subject]
    ? subjectMap[filter.subject].name
    : "All subjects";
  const yr = filter.year ? ` · ${filter.year}` : "";
  $("#qlist-title").textContent = `${examName} · ${subName}${yr}`;
  $("#qlist-count").textContent = `${list.length} question${list.length === 1 ? "" : "s"}`;
  $("#qlist").innerHTML = "";
  shown = 0;
  renderMore();
  window.scrollTo({ top: 0 });
}

function cardHTML(q, serial) {
  const sub = subjectMap[q.s] || { icon: "📘", name: q.s || "Subject" };
  const qBody = q.fmt === "html" ? q.q : formatBody(q.q, true);
  // Options are always free to see; only the correct answer + explanation
  // are Pass-gated (for UPSC's unpaid users — see the #qlist click handler).
  const opts = q.o.map((opt, i) => {
    const body = q.fmt === "html" ? opt : escapeHTML(opt);
    return `<button class="option" data-opt="${i}"><span class="key">${String.fromCharCode(97 + i)}</span><span>${body}</span></button>`;
  }).join("");
  const optsBlock = `<div class="options">${opts}</div>`;
  return `<article class="qcard" data-qid="${q.i}">
      <div class="qtags">
        <span class="qnum">Q${serial}</span>
        <span class="qtag">${sub.icon} ${sub.name}</span>
        ${q.y ? `<span class="qtag">${q.y}</span>` : ""}
      </div>
      <div class="qtext">${qBody}</div>
      ${optsBlock}
      <div class="explain hidden" data-exp></div>
    </article>`;
}

function renderMore() {
  const list = currentList();
  // Free users can browse every question stem; options/explanations stay Pass-gated.
  const next = list.slice(shown, shown + PAGE);
  const frag = document.createElement("div");
  frag.innerHTML = next.map((q, k) => cardHTML(q, shown + k + 1)).join("");
  const wrap = $("#qlist");
  while (frag.firstChild) wrap.appendChild(frag.firstChild);
  shown += next.length;
  const more = $("#load-more");
  removeUnlockStrip();
  more.classList.toggle("hidden", shown >= list.length);
  if (shown < list.length) more.textContent = `Show more (${list.length - shown} left)`;
  if (next.some(q => q.fmt === "html")) renderMath(wrap);
}

/* premium lock strip shown when a free user hits the preview limit */
function showUnlockStrip(locked) {
  removeUnlockStrip();
  if (window.PAY && PAY.track) PAY.track("content_locked", { locked: locked, subject: filter.subject, year: filter.year });
  const strip = document.createElement("div");
  strip.id = "unlock-strip";
  strip.className = "unlock-strip";
  strip.innerHTML =
    `<div class="us-fade"></div>
     <div class="us-body">
       <div class="us-lock">🔒</div>
       <h3>${locked.toLocaleString()} more questions locked</h3>
       <p>Every PYQ, every explanation, unlimited quizzes — <b>₹149</b> once, full year of access.</p>
       <button class="btn btn-primary btn-lg btn-glow" data-unlock="browse">✨ Unlock everything · ₹149</button>
       <span class="us-mini">Secure via Razorpay · Instant access · No subscription</span>
     </div>`;
  const wrap = $("#qlist");
  wrap.parentNode.insertBefore(strip, wrap.nextSibling);
}
function removeUnlockStrip() { const s = $("#unlock-strip"); if (s) s.remove(); }

/* ---------- free-quiz daily limit ---------- */
function quizAllowed() {
  if (!window.PAY || PAY.isPaid()) return true;
  const used = +(localStorage.getItem("yespyq_quiz_" + today()) || 0);
  return used < PAY.freeQuizzesPerDay();
}
function noteQuizStart() {
  if (!window.PAY || PAY.isPaid()) return;
  const k = "yespyq_quiz_" + today();
  localStorage.setItem(k, (+(localStorage.getItem(k) || 0)) + 1);
}

/* re-render when payment/login state changes (called by auth-pay.js) */
window.onPayChange = function () {
  try {
    if (typeof PAY !== "undefined" && PAY.isPaid()) removeUnlockStrip();
    const pv = $("#view-practice");
    if (pv && !pv.classList.contains("hidden")) applyFilter();
  } catch (e) {}
};

/* reveal answer on option click (delegated) */
$("#qlist").addEventListener("click", e => {
  if (e.target.closest("[data-unlock]")) return; // Pass CTA inside a gated answer box
  const opt = e.target.closest(".option");
  if (!opt) return;
  const card = opt.closest(".qcard");
  if (!card || card.dataset.done) return;
  const q = byId[card.dataset.qid];
  const chosen = +opt.dataset.opt;
  card.dataset.done = "1";
  // Options are always free; only UPSC's answer key + explanation are
  // Pass-gated for unpaid users (other exams' browse data is already the
  // free ~10% preview pool, so never gated here — see EXAM_META/ensureExamBank).
  const gated = currentExam === "upsc" && window.PAY && !PAY.isPaid();
  const ex = card.querySelector("[data-exp]");
  if (gated) {
    card.querySelectorAll(".option").forEach((o, i) => {
      o.classList.add("locked");
      if (i === chosen) o.classList.add("picked");
    });
    if (typeof PAY.track === "function") PAY.track("premium_click", { source: "browse-answer" });
    ex.innerHTML = `
      <div class="answer-gate" data-unlock="browse-answer">
        <span class="ag-lock">🔒</span>
        <div><b>Answer &amp; explanation — PYQ Pass</b><p>You picked ${String.fromCharCode(97 + chosen)}). Unlock the correct answer and full explanation with Pass.</p></div>
        <span class="btn btn-primary btn-sm" data-unlock="browse-answer">Unlock · ₹149</span>
      </div>`;
    ex.classList.remove("hidden");
    return;
  }
  const correct = chosen === q.a;
  card.querySelectorAll(".option").forEach((o, i) => {
    o.classList.add("locked");
    if (i === q.a) o.classList.add("correct");
    else if (i === chosen) o.classList.add("wrong");
    else o.classList.add("dim");
  });
  const expl = q.exp || (window.EXP && window.EXP[q.i]) || "Explanation will appear here.";
  const ansText = q.fmt === "html" ? q.o[q.a] : escapeHTML(q.o[q.a]);
  const expBody = q.fmt === "html" ? expl : formatBody(expl, false);
  ex.innerHTML = `
    <div class="verdict ${correct ? "ok" : "no"}">${correct ? "✓ Correct" : "✗ Incorrect"} — Answer: ${String.fromCharCode(97 + q.a)}) ${ansText}</div>
    <div class="exp-body"><span class="lbl">Explanation</span>${expBody}</div>
    ${(window.PAY && PAY.nudgeHTML) ? PAY.nudgeHTML() : ""}`;
  ex.classList.remove("hidden");
  if (correct && !answered.has(q.i)) {
    answered.add(q.i);
    earnXp(10);
    const r = opt.getBoundingClientRect();
    floatXp(r.right - 56, r.top, "+10 XP");
  }
  renderMath(ex);
});

/* ---------- exam picker (asked before assuming UPSC) ---------- */
// Only UPSC has this interactive quiz/practice mode; other exams live as a
// static question bank at /exams/<exam>/. Ask which exam before jumping in,
// rather than silently defaulting every "Start Practice" click to UPSC.
let pendingPickerAction = null;
function openExamPicker(action) {
  pendingPickerAction = action;
  const el = $("#exam-picker");
  if (!el) return;
  el.classList.remove("hidden");
  el.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}
function closeExamPicker() {
  const el = $("#exam-picker");
  if (!el) return;
  el.classList.add("hidden");
  el.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  pendingPickerAction = null;
}
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && !$("#exam-picker")?.classList.contains("hidden")) closeExamPicker();
});

/* ---------- global click routing ---------- */
document.addEventListener("click", e => {
  // ----- exam picker (checked first — decides where quiz/browse CTAs go) -----
  const picker = e.target.closest("[data-exam-picker]");
  if (picker) { e.preventDefault(); openExamPicker(picker.dataset.examPicker); return; }
  if (e.target.closest("[data-picker-close]") || e.target === $("#exam-picker")) {
    e.preventDefault(); closeExamPicker(); return;
  }
  const examTile = e.target.closest("#exam-picker [data-exam]");
  if (examTile) {
    e.preventDefault();
    const examId = examTile.dataset.exam;
    const action = pendingPickerAction;
    closeExamPicker();
    setExam(examId, { mode: action === "quiz" ? "quiz" : "browse", subject: null, year: null });
    return;
  }

  // ----- quiz routing (checked first) -----
  if (e.target.closest("[data-quiz-setup]")) { e.preventDefault(); setExam(currentExam, { mode: "quiz" }); return; }
  const qStart = e.target.closest("[data-quiz-start]");
  if (qStart) { e.preventDefault(); const d = qStart.dataset; startQuiz({ size: 10, subject: d.subject || null, year: d.year ? +d.year : null }); return; }
  if (e.target.closest("[data-quiz-exit]")) { e.preventDefault(); showView("home"); return; }
  const qa = e.target.closest("[data-qa]");
  if (qa) { if (!qa.closest(".quiz-options").querySelector(".locked")) answerQuiz(qa); return; }
  if (e.target.closest("[data-quiz-next]")) { nextQuiz(); return; }
  if (e.target.closest("[data-quiz-again]")) { startQuiz({ size: 10, subject: quiz && quiz.subject, year: quiz && quiz.year, label: quiz && quiz.label }); return; }
  if (e.target.closest("[data-quiz-review]")) { renderReview(); return; }
  if (e.target.closest("[data-share]")) { e.preventDefault(); shareResult(); return; }

  const nav = e.target.closest("[data-nav]");
  if (nav) {
    e.preventDefault();
    const n = nav.dataset.nav;
    if (n === "practice") setExam(currentExam || "upsc", { mode: "browse" });
    else if (n === "mock") openMockSetup();
    else showView(n);
    return;
  }

  // ----- Smart PYQ Mock setup -----
  const mExam = e.target.closest("[data-mock-exam]");
  if (mExam) {
    e.preventDefault();
    const id = mExam.dataset.mockExam;
    if (mockState.exams.has(id)) { if (mockState.exams.size > 1) mockState.exams.delete(id); }
    else mockState.exams.add(id);
    mockState.subjects.clear();
    renderMockSetup();
    return;
  }
  const mSubject = e.target.closest("[data-mock-subject]");
  if (mSubject) {
    e.preventDefault();
    const name = mSubject.dataset.mockSubject;
    if (mockState.subjects.has(name)) mockState.subjects.delete(name); else mockState.subjects.add(name);
    renderMockSetup();
    return;
  }
  const mCount = e.target.closest("[data-mock-count]");
  if (mCount) {
    e.preventDefault();
    mockState.count = +mCount.dataset.mockCount;
    $$("#mock-counts [data-mock-count]").forEach(b => b.classList.toggle("active", b === mCount));
    renderMockSetup();
    return;
  }
  const mMode = e.target.closest("[data-mock-mode]");
  if (mMode) {
    e.preventDefault();
    mockState.mode = mMode.dataset.mockMode;
    $$("#mock-modes [data-mock-mode]").forEach(b => b.classList.toggle("active", b === mMode));
    return;
  }
  if (e.target.closest("#mock-generate")) { e.preventDefault(); generateMock(); return; }

  // ----- Timed Exam Mode -----
  const eJump = e.target.closest("[data-exam-jump]");
  if (eJump) { e.preventDefault(); examJumpTo(+eJump.dataset.examJump); return; }
  const eOpt = e.target.closest("[data-exam-opt]");
  if (eOpt) { e.preventDefault(); examAnswer(eOpt); return; }
  if (e.target.closest("[data-exam-flag]")) {
    e.preventDefault();
    const i = examState.idx;
    if (examState.flagged.has(i)) examState.flagged.delete(i); else examState.flagged.add(i);
    renderExamMode();
    return;
  }
  if (e.target.closest("[data-exam-prev]")) { e.preventDefault(); examJumpTo(examState.idx - 1); return; }
  if (e.target.closest("[data-exam-next]")) { e.preventDefault(); examJumpTo(examState.idx + 1); return; }
  if (e.target.closest("[data-exam-submit]")) { e.preventDefault(); finishExamMode(); return; }
  if (e.target.closest("[data-exam-exit]")) {
    e.preventDefault();
    if (examState.timerId && !confirm("Exit now? Your timed exam progress will be lost.")) return;
    stopExamTimer();
    showView("home");
    return;
  }
  if (e.target.closest("[data-action='start']")) { e.preventDefault(); openExamPicker("browse"); return; }
  const sc = e.target.closest("[data-subject]");
  if (sc) { openBrowse({ subject: sc.dataset.subject, year: null }); return; }
  const yc = e.target.closest("[data-year]");
  if (yc) { openBrowse({ subject: null, year: +yc.dataset.year }); return; }
  const fexam = e.target.closest("[data-fexam]");
  if (fexam) { closeFilters(); setExam(fexam.dataset.fexam, { mode: "browse", subject: null, year: null }); return; }
  const fs = e.target.closest("[data-fsub]");
  if (fs) { closeFilters(); openBrowse({ subject: fs.dataset.fsub || null, year: filter.year }); return; }
  const fy = e.target.closest("[data-fyear]");
  if (fy) { filter.year = fy.dataset.fyear ? +fy.dataset.fyear : null; closeFilters(); renderFilters(); applyFilter(); return; }
  if (e.target.closest("#filter-toggle")) { setFiltersOpen(!$("#filters").classList.contains("open")); return; }
  if (e.target.closest("#filter-close")) { closeFilters(); return; }
  if (document.body.classList.contains("filters-open") && !e.target.closest("#filters") && !e.target.closest("#filter-toggle")) {
    closeFilters(); return;
  }
  if (e.target.closest("#load-more")) { renderMore(); }
});

/* ============================================================
   QUIZ MODE — one question at a time (Duolingo-style loop)
   ============================================================ */
let quiz = null;
function shuffle(a) { for (let i = a.length - 1; i > 0; i--) { const j = Math.random() * (i + 1) | 0; [a[i], a[j]] = [a[j], a[i]]; } return a; }

/* Setup screen — choose a mixed quiz, or focus by subject or year */
function openQuizSetup() { showView("quiz"); renderQuizSetup(); }
function renderQuizSetup() {
  $("#quiz-bar").style.width = "0%";
  $("#quiz-combo").innerHTML = "";
  const meta = EXAM_META[currentExam] || EXAM_META.upsc;
  if (!meta.quiz) {
    const subs = SUBJECTS.map(s =>
      `<button class="rchip" data-fsub="${s.id}">${s.icon} ${s.name}</button>`).join("");
    $("#quiz-body").innerHTML = `
      <div class="quiz-setup">
        <h2 class="setup-title">${meta.full}</h2>
        <p class="setup-sub">Interactive quiz is available for UPSC. For ${meta.name}, browse the solved question bank by subject.</p>
        <button class="btn btn-primary btn-lg setup-mixed" data-nav="practice">Browse ${meta.name} PYQs</button>
        <h3 class="setup-h">Or jump to a subject</h3>
        <div class="result-chips">${subs}</div>
        <h3 class="setup-h">Switch exam</h3>
        <div class="result-chips">
          ${Object.values(EXAM_META).map(ex =>
            `<button class="rchip ${ex.id === currentExam ? "active" : ""}" data-fexam="${ex.id}">${ex.name}</button>`
          ).join("")}
        </div>
      </div>`;
    window.scrollTo({ top: 0 });
    return;
  }
  const exams = Object.values(EXAM_META).map(ex =>
    `<button class="rchip ${ex.id === currentExam ? "active" : ""}" data-fexam="${ex.id}">${ex.name}</button>`
  ).join("");
  const subs = SUBJECTS.map(s => `<button class="rchip" data-quiz-start data-subject="${s.id}">${s.icon} ${s.name}</button>`).join("");
  const yrs = YEARS.slice(0, 12).map(y => `<button class="rchip" data-quiz-start data-year="${y}">${y}</button>`).join("");
  $("#quiz-body").innerHTML = `
    <div class="quiz-setup">
      <h2 class="setup-title">Start a 10-question UPSC quiz</h2>
      <p class="setup-sub">Mixed set, or focus on one subject or exam year. Switch exam below to browse other banks.</p>
      <button class="btn btn-primary btn-lg setup-mixed" data-quiz-start>Mixed quiz — 10 random PYQs</button>
      <h3 class="setup-h">Exam</h3>
      <div class="result-chips">${exams}</div>
      <h3 class="setup-h">Practice by subject</h3>
      <div class="result-chips">${subs}</div>
      <h3 class="setup-h">Practice by year</h3>
      <div class="result-chips">${yrs}</div>
    </div>`;
  window.scrollTo({ top: 0 });
}

function startQuiz(opts = {}) {
  if (!quizAllowed()) { if (window.PAY && PAY.track) PAY.track("quiz_limit_hit", {}); if (window.PAY) PAY.openUnlock("quiz"); return; }
  noteQuizStart();
  const size = opts.size || 10;
  let pool = QUESTIONS.filter(q => (!opts.subject || q.s === opts.subject) && (!opts.year || q.y === opts.year));
  if (pool.length < 4) pool = QUESTIONS.slice();
  const queue = shuffle(pool.slice()).slice(0, Math.min(size, pool.length));
  quiz = {
    queue, idx: 0, correct: 0, total: queue.length, xp: 0, combo: 0, bestCombo: 0, results: [],
    subject: opts.subject || null, year: opts.year || null,
    label: opts.label || (opts.subject ? (subjectMap[opts.subject]||{}).name || opts.subject : opts.year ? `UPSC ${opts.year}` : "Quick Quiz"),
  };
  showView("quiz");
  renderQuizQuestion();
}

function renderQuizQuestion() {
  const q = quiz.queue[quiz.idx];
  $("#quiz-bar").style.width = (quiz.idx / quiz.total) * 100 + "%";
  $("#quiz-combo").innerHTML = quiz.combo >= 2 ? `🔥 ${quiz.combo}` : "";
  const sub = q._sub || subjectMap[q.s] || { icon: "📘", name: q.s || "Subject" };
  $("#quiz-body").innerHTML = `
    <div class="quiz-card">
      <div class="quiz-meta">
        <span class="qtag">${sub.icon} ${sub.name}</span>
        ${q.y ? `<span class="qtag">${q.y}</span>` : ""}
        <span class="quiz-count">${quiz.idx + 1} / ${quiz.total}</span>
      </div>
      <div class="qtext quiz-q">${q.fmt === "html" ? q.q : formatBody(q.q, true)}</div>
      <div class="options quiz-options">
        ${q.o.map((o, i) => `<button class="option" data-qa="${i}"><span class="key">${String.fromCharCode(97 + i)}</span><span>${q.fmt === "html" ? o : escapeHTML(o)}</span></button>`).join("")}
      </div>
      <div class="explain hidden" data-exp></div>
      <div class="quiz-actions"><button class="btn btn-primary btn-lg hidden" data-quiz-next>Next →</button></div>
    </div>`;
  window.scrollTo({ top: 0 });
  renderMath($("#quiz-body"));
}

function answerQuiz(btn) {
  const i = +btn.dataset.qa, q = quiz.queue[quiz.idx], correct = i === q.a;
  const body = $("#quiz-body");
  body.querySelectorAll(".option").forEach((o, k) => {
    o.classList.add("locked");
    if (k === q.a) o.classList.add("correct");
    else if (k === i) o.classList.add("wrong");
    else o.classList.add("dim");
  });
  quiz.results.push({ q, chosen: i, correct });
  if (correct) {
    quiz.correct++; quiz.combo++; quiz.bestCombo = Math.max(quiz.bestCombo, quiz.combo);
    const gain = 10 + (quiz.combo - 1) * 2;           // combo bonus = more XP for streaks
    quiz.xp += gain; earnXp(gain);
    const r = btn.getBoundingClientRect(); floatXp(r.right - 56, r.top, `+${gain} XP`);
    if (quiz.combo >= 3) burstConfetti();
  } else {
    quiz.combo = 0;
  }
  $("#quiz-combo").innerHTML = quiz.combo >= 2 ? `🔥 ${quiz.combo}` : "";
  const expl = q.exp || (window.EXP && window.EXP[q.i]) || "Explanation coming soon.";
  const ansText = q.fmt === "html" ? q.o[q.a] : escapeHTML(q.o[q.a]);
  const expBody = q.fmt === "html" ? expl : formatBody(expl, false);
  const ex = body.querySelector("[data-exp]");
  ex.innerHTML = `
    <div class="verdict ${correct ? "ok" : "no"}">${correct ? "✓ Correct" : "✗ Incorrect"} — Answer: ${String.fromCharCode(97 + q.a)}) ${ansText}</div>
    <div class="exp-body"><span class="lbl">Explanation</span>${expBody}</div>
    ${(window.PAY && PAY.nudgeHTML) ? PAY.nudgeHTML() : ""}`;
  ex.classList.remove("hidden");
  const next = body.querySelector("[data-quiz-next]");
  next.textContent = quiz.idx + 1 >= quiz.total ? "See results →" : "Next →";
  next.classList.remove("hidden");
  ex.querySelector(".verdict")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  renderMath(ex);
}

function nextQuiz() {
  if (quiz.idx + 1 >= quiz.total) return renderResult();
  quiz.idx++; renderQuizQuestion();
}

function renderResult() {
  $("#quiz-bar").style.width = "100%";
  $("#quiz-combo").innerHTML = "";
  const pct = Math.round((quiz.correct / quiz.total) * 100);
  const msg = pct >= 80 ? "Outstanding! 🏆" : pct >= 60 ? "Strong work! 💪" : pct >= 40 ? "Keep pushing! 📈" : "Every attempt counts 🌱";
  $("#quiz-body").innerHTML = `
    <div class="result">
      <div class="result-ring" style="--pct:${pct}"><span class="result-score">${quiz.correct}<small>/ ${quiz.total}</small></span></div>
      <h2 class="result-msg">${msg}</h2>
      <p class="result-sub">${quiz.label} · You earned <b>+${quiz.xp} XP</b></p>
      <div class="result-stats">
        <div><b>${pct}%</b><span>Accuracy</span></div>
        <div><b>+${quiz.xp}</b><span>XP earned</span></div>
        <div><b>🔥 ${quiz.bestCombo}</b><span>Best combo</span></div>
      </div>
      <div class="result-cta">
        <button class="btn btn-primary btn-lg" data-quiz-again>Next 10 questions →</button>
        <button class="btn btn-ghost btn-lg" data-quiz-review>Review answers</button>
      </div>
      <p class="result-more">Or keep going:</p>
      <div class="result-chips">
        <button class="rchip" data-quiz-start data-mix="1">🎲 Mixed quiz</button>
        ${SUBJECTS.slice(0, 6).map(s => `<button class="rchip" data-quiz-start data-subject="${s.id}">${s.icon} ${s.name.split(" ")[0]}</button>`).join("")}
        <a class="rchip" href="#" data-nav="home">📚 By year / subject</a>
      </div>
      <button class="share-btn" data-share>📲 Share my score on WhatsApp</button>
    </div>`;
  burstConfetti();
  window.scrollTo({ top: 0 });
}

function renderReview() {
  const rows = quiz.results.map((r, n) => `
    <div class="rev-row ${r.correct ? "ok" : "no"}">
      <div class="rev-head"><span>${r.correct ? "✓" : "✗"} Q${n + 1}</span><span class="qtag">${(subjectMap[r.q.s]||{icon:"📘",name:r.q.s}).icon} ${(subjectMap[r.q.s]||{name:r.q.s}).name}${r.q.y ? " · " + r.q.y : ""}</span></div>
      <div class="qtext rev-q">${formatBody(r.q.q, true)}</div>
      <div class="rev-ans"><b>Correct:</b> ${String.fromCharCode(97 + r.q.a)}) ${escapeHTML(r.q.o[r.q.a])}${r.correct ? "" : ` &nbsp;·&nbsp; <span class="rev-you">You: ${String.fromCharCode(97 + r.chosen)}) ${escapeHTML(r.q.o[r.chosen])}</span>`}</div>
    </div>`).join("");
  $("#quiz-body").innerHTML = `
    <div class="review">
      <h2>Review · ${quiz.correct}/${quiz.total} correct</h2>
      ${rows}
      <div class="result-cta">
        <button class="btn btn-primary btn-lg" data-quiz-again>Next 10 questions →</button>
        <a class="btn btn-ghost btn-lg" href="#" data-nav="home">Back to home</a>
      </div>
    </div>`;
  window.scrollTo({ top: 0 });
}

/* ============================================================
   SMART PYQ MOCK — mix exams/subjects/years into one custom set,
   run it as a practice quiz or a timed exam.
   ============================================================ */
const mockState = { exams: new Set(["upsc"]), subjects: new Set(), count: 10, mode: "practice" };
const MOCK_FREE_CAP = 20; // unpaid users can try any mix, capped at 20 questions — never blocked outright

function mockSubjectOptions() {
  // de-duped by display name, so "Physics" in JEE/NEET/Board is one chip
  const byName = new Map();
  mockState.exams.forEach(examId => {
    const meta = EXAM_META[examId];
    if (!meta) return;
    meta.subjects.forEach(s => { if (!byName.has(s.name)) byName.set(s.name, s.icon || "📘"); });
  });
  return [...byName.entries()];
}

async function renderMockSetup() {
  const examsEl = $("#mock-exams");
  examsEl.innerHTML = Object.values(EXAM_META).map(ex => `
    <button class="mock-exam-chip ${mockState.exams.has(ex.id) ? "active" : ""}" data-mock-exam="${ex.id}">
      ${ex.name}
    </button>`).join("");

  const subs = mockSubjectOptions();
  const subsEl = $("#mock-subjects");
  subsEl.innerHTML = subs.length
    ? subs.map(([name, icon]) => `
        <button class="rchip ${mockState.subjects.has(name) ? "active" : ""}" data-mock-subject="${escapeHTML(name)}">
          ${icon} ${escapeHTML(name)}
        </button>`).join("")
    : `<span class="mock-hint">Pick an exam above to see its subjects</span>`;

  $("#mock-pool-note").textContent = "Checking how many questions match…";
  try {
    const pool = await buildMockPool();
    const paid = !window.PAY || PAY.isPaid();
    const n = Math.min(paid ? mockState.count : Math.min(mockState.count, MOCK_FREE_CAP), pool.length);
    if (!pool.length) {
      $("#mock-pool-note").textContent = "No free-preview questions match this combination yet. Try another exam or subject.";
    } else if (!paid && mockState.count > MOCK_FREE_CAP) {
      $("#mock-pool-note").textContent = `${pool.length.toLocaleString()} questions match — free preview uses ${n}. Unlock PYQ Pass for the full ${Math.min(mockState.count, pool.length)}.`;
    } else {
      $("#mock-pool-note").textContent = `${pool.length.toLocaleString()} questions match — mock will use ${n}.`;
    }
    $("#mock-generate").disabled = pool.length === 0;
  } catch (err) {
    console.error(err);
    $("#mock-pool-note").textContent = "Couldn't load the question pool. Please try again.";
  }
}

function openMockSetup() { showView("mock"); renderMockSetup(); }

/* Gathers the eligible pool for the current mockState selections.
   UPSC comes from the already-loaded pyq.js bank (all of it, same as
   normal browse/quiz); every other exam comes from mock-pool.json,
   which — by construction — only ever holds the free ~10% preview. */
async function buildMockPool() {
  const subjectNames = mockState.subjects.size ? mockState.subjects : null;
  let pool = [];
  for (const examId of mockState.exams) {
    const meta = EXAM_META[examId];
    if (!meta) continue;
    const bank = await ensureExamBank(examId);
    const subOf = sid => bank.subjects.find(x => x.id === sid);
    const matched = bank.questions.filter(q => !subjectNames || subjectNames.has((subOf(q.s) || {}).name));
    pool = pool.concat(matched.map(q => ({ ...q, _exam: examId, _sub: subOf(q.s) })));
  }
  return pool;
}

function startCustomMock(queue, label) {
  quiz = {
    queue, idx: 0, correct: 0, total: queue.length, xp: 0, combo: 0, bestCombo: 0, results: [],
    subject: null, year: null, label,
  };
  showView("quiz");
  renderQuizQuestion();
}

async function generateMock() {
  const btn = $("#mock-generate");
  btn.disabled = true; btn.textContent = "Generating…";
  try {
    const pool = await buildMockPool();
    if (!pool.length) { $("#mock-pool-note").textContent = "No questions match — try another combination."; return; }
    const paid = !window.PAY || PAY.isPaid();
    const size = Math.min(paid ? mockState.count : Math.min(mockState.count, MOCK_FREE_CAP), pool.length);
    const queue = shuffle(pool.slice()).slice(0, size);
    const label = `Smart Mock · ${[...mockState.exams].map(id => (EXAM_META[id] || {}).name).join(" + ")}`;
    if (mockState.mode === "exam") startExamMode(queue, label);
    else startCustomMock(queue, label);
  } finally {
    btn.disabled = false; btn.textContent = "Generate mock →";
  }
}

/* ============================================================
   REAL EXAM MODE — timed, distraction-free, question grid to jump
   around, no per-question reveal; ends in a full result report.
   ============================================================ */
const SEC_PER_Q = 72;               // ~1.2 min/question, matches real exam pacing
const EXAM_MIN_SEC = 10 * 60, EXAM_MAX_SEC = 90 * 60;
let examState = null;

function startExamMode(queue, label) {
  const totalSec = Math.min(EXAM_MAX_SEC, Math.max(EXAM_MIN_SEC, queue.length * SEC_PER_Q));
  examState = {
    queue, idx: 0, total: queue.length, label,
    answers: new Array(queue.length).fill(null),
    flagged: new Set(),
    timeLeftSec: totalSec, totalSec, timerId: null,
  };
  showView("exam");
  renderExamMode();
  startExamTimer();
}

function startExamTimer() {
  stopExamTimer();
  examState.timerId = setInterval(() => {
    examState.timeLeftSec--;
    updateExamTimerUI();
    if (examState.timeLeftSec <= 0) finishExamMode();
  }, 1000);
}
function stopExamTimer() {
  if (examState && examState.timerId) { clearInterval(examState.timerId); examState.timerId = null; }
}
function updateExamTimerUI() {
  const el = $("#exam-timer");
  if (!el || !examState) return;
  const t = Math.max(0, examState.timeLeftSec);
  const m = String(Math.floor(t / 60)).padStart(2, "0"), s = String(t % 60).padStart(2, "0");
  el.textContent = `${m}:${s}`;
  el.classList.toggle("low", t <= 60);
}

function examGridHTML() {
  return examState.queue.map((q, i) => {
    const cls = ["exam-nav-cell"];
    if (i === examState.idx) cls.push("current");
    if (examState.answers[i] != null) cls.push("answered");
    if (examState.flagged.has(i)) cls.push("flagged");
    return `<button class="${cls.join(" ")}" data-exam-jump="${i}">${i + 1}</button>`;
  }).join("");
}

function renderExamMode() {
  const q = examState.queue[examState.idx];
  const sub = q._sub || { icon: "📘", name: q.s || "Subject" };
  const answered = examState.answers.filter(a => a != null).length;
  $("#exam-wrap").innerHTML = `
    <div class="exam-top">
      <div class="exam-top-left">
        <b>${escapeHTML(examState.label)}</b>
        <span class="exam-progress-note">${answered} / ${examState.total} answered</span>
      </div>
      <div class="exam-timer" id="exam-timer">--:--</div>
      <button class="btn btn-ghost" data-exam-exit>Exit</button>
    </div>
    <div class="exam-body">
      <div class="exam-nav-grid" id="exam-grid">${examGridHTML()}</div>
      <div class="exam-card">
        <div class="quiz-meta">
          <span class="qtag">${sub.icon} ${sub.name}</span>
          ${q.y ? `<span class="qtag">${q.y}</span>` : ""}
          <span class="quiz-count">Q${examState.idx + 1} / ${examState.total}</span>
          <button class="exam-flag ${examState.flagged.has(examState.idx) ? "active" : ""}" data-exam-flag>🚩 ${examState.flagged.has(examState.idx) ? "Flagged" : "Flag for review"}</button>
        </div>
        <div class="qtext quiz-q">${q.fmt === "html" ? q.q : formatBody(q.q, true)}</div>
        <div class="options exam-options">
          ${q.o.map((o, i) => `<button class="option ${examState.answers[examState.idx] === i ? "picked" : ""}" data-exam-opt="${i}"><span class="key">${String.fromCharCode(97 + i)}</span><span>${q.fmt === "html" ? o : escapeHTML(o)}</span></button>`).join("")}
        </div>
        <div class="exam-nav">
          <button class="btn btn-ghost" data-exam-prev ${examState.idx === 0 ? "disabled" : ""}>← Prev</button>
          ${examState.idx + 1 >= examState.total
            ? `<button class="btn btn-primary btn-lg" data-exam-submit>Submit exam →</button>`
            : `<button class="btn btn-primary" data-exam-next>Next →</button>`}
        </div>
      </div>
    </div>`;
  window.scrollTo({ top: 0 });
  renderMath($("#exam-wrap"));
  updateExamTimerUI();
}

function examAnswer(btn) {
  examState.answers[examState.idx] = +btn.dataset.examOpt;
  renderExamMode();
}

function examJumpTo(i) {
  if (i < 0 || i >= examState.total) return;
  examState.idx = i;
  renderExamMode();
}

function finishExamMode() {
  stopExamTimer();
  const results = examState.queue.map((q, i) => ({ q, chosen: examState.answers[i], correct: examState.answers[i] === q.a }));
  const correct = results.filter(r => r.correct).length;
  const attempted = results.filter(r => r.chosen != null).length;
  const total = examState.total;
  const pct = Math.round((correct / total) * 100);
  const xp = correct * 8;
  earnXp(xp);
  const msg = pct >= 80 ? "Outstanding! 🏆" : pct >= 60 ? "Strong work! 💪" : pct >= 40 ? "Keep pushing! 📈" : "Every attempt counts 🌱";
  $("#exam-wrap").innerHTML = `
    <div class="result">
      <div class="result-ring" style="--pct:${pct}"><span class="result-score">${correct}<small>/ ${total}</small></span></div>
      <h2 class="result-msg">${msg}</h2>
      <p class="result-sub">${escapeHTML(examState.label)} · Timed Exam · Attempted ${attempted}/${total} · +${xp} XP</p>
      <div class="result-stats">
        <div><b>${pct}%</b><span>Accuracy</span></div>
        <div><b>${attempted}</b><span>Attempted</span></div>
        <div><b>${total - attempted}</b><span>Skipped</span></div>
      </div>
      <div class="result-cta">
        <button class="btn btn-primary btn-lg" data-exam-review>Review answers</button>
        <a class="btn btn-ghost btn-lg" href="#" data-nav="home">Back to home</a>
      </div>
      <div class="exam-review hidden" id="exam-review">
        ${results.map((r, i) => `
          <div class="review-item ${r.correct ? "ok" : r.chosen == null ? "skip" : "no"}">
            <div class="review-q">Q${i + 1}. ${r.q.fmt === "html" ? r.q.q : escapeHTML(r.q.q)}</div>
            <div class="review-a">Your answer: ${r.chosen != null ? String.fromCharCode(97 + r.chosen) : "— skipped —"} &nbsp;·&nbsp; Correct: ${String.fromCharCode(97 + r.q.a)}) ${r.q.fmt === "html" ? r.q.o[r.q.a] : escapeHTML(r.q.o[r.q.a])}</div>
          </div>`).join("")}
      </div>
    </div>`;
  window.scrollTo({ top: 0 });
  renderMath($("#exam-wrap"));
  const reviewBtn = $("#exam-wrap [data-exam-review]");
  if (reviewBtn) reviewBtn.addEventListener("click", e => {
    e.preventDefault();
    $("#exam-review").classList.remove("hidden");
    reviewBtn.classList.add("hidden");
  });
}

function shareResult() {
  const score = quiz ? `${quiz.correct}/${quiz.total}` : "";
  const txt = `I scored ${score} on a UPSC Prelims PYQ quiz on YESPYQ! 🎯 Practice free, one question at a time:`;
  const url = "https://yespyq.com/";
  if (navigator.share) { navigator.share({ title: "YESPYQ — UPSC PYQ Quiz", text: txt, url }).catch(() => {}); }
  else { window.open(`https://wa.me/?text=${encodeURIComponent(txt + " " + url)}`, "_blank"); }
}

function burstConfetti() {
  const c = $("#confetti"); if (!c) return;
  const ctx = c.getContext("2d"); c.width = innerWidth; c.height = innerHeight; c.style.display = "block";
  const cols = ["#2563eb", "#16a34a", "#f59e0b", "#ef4444", "#8b5cf6"];
  const P = Array.from({ length: 90 }, () => ({ x: innerWidth / 2, y: innerHeight * .28, vx: (Math.random() - .5) * 13, vy: Math.random() * -13 - 3, g: .42, s: Math.random() * 6 + 3, c: cols[Math.random() * cols.length | 0] }));
  let f = 0;
  (function anim() {
    ctx.clearRect(0, 0, c.width, c.height);
    P.forEach(p => { p.vy += p.g; p.x += p.vx; p.y += p.vy; ctx.fillStyle = p.c; ctx.fillRect(p.x, p.y, p.s, p.s); });
    if (f++ < 75) requestAnimationFrame(anim); else { ctx.clearRect(0, 0, c.width, c.height); c.style.display = "none"; }
  })();
}

/* ---------- util ---------- */
function escapeHTML(str) { return String(str).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); }

/* Render a flat run-on question/explanation string as readable, spaced lines.
   Questions: List–I/II headers, A./B./C./D. and 1./2./3. items, "Codes:" and the
   closing instruction each get their own line. Explanations: bullet (•) and
   "Statement N" markers break, then each sentence goes on its own line.
   Sentence splitting guards initials (Dr. B.R. Ambedkar, S. Radhakrishnan),
   decimals (2.5) and common abbreviations so they never break mid-phrase. */
const ABBR = new Set(["Dr","Mr","Mrs","Ms","Smt","Shri","Sh","Prof","Rev","Hon","St","Lt","Col","Gen","Capt","Sgt","Ex","No","Art","Sec","Fig","Vol","Rs","vs","etc","Pvt","Ltd","Co","viz","Mt","Govt","Deptt"]);
function breakSentences(t) {
  return t.replace(/([.?!])\s+(?=[A-Z0-9"(])/g, (m, p, off, str) => {
    if (p === ".") {
      const wm = str.slice(0, off).match(/(\S+)$/);
      const core = wm ? wm[1] : "";
      if (/^(?:[A-Za-z]\.)*[A-Za-z]$/.test(core)) return m;   // initials: S, B.R, U.S.A, i.e
      if (/^\d+$/.test(core)) return m;                        // numbers / decimals
      if (ABBR.has(core.replace(/[^A-Za-z]/g, ""))) return m;  // Dr, Mr, etc.
    }
    return p + "\n";
  });
}
function formatBody(raw, isQuestion) {
  // mis-encoded bullets / C1 control chars are used as item separators -> break
  let t = String(raw).replace(/[\x80-\x9F•‣▪●·]+/g, " \n ");
  t = escapeHTML(t).replace(/[^\S\n]+/g, " ");                 // collapse spaces, keep breaks
  if (isQuestion) {
    t = t.replace(/(^|\s)([A-E])\.\s+(?=[A-Z])/g, "$1\n$2. "); // A. B. C. D. E. markers
    t = t.replace(/[^\S\n]*(\d{1,2})\.\s+/g, "\n$1. ");        // 1. 2. 3. markers
    t = t.replace(/\s*(Codes?\s*:)/g, "\n$1");                 // Codes:
    t = t.replace(/\s*(How many of the |Which of the statements |Which of the above |Which one of the following |Select the correct answer |Consider the following codes )/g, "\n$1");
  } else {
    t = t.replace(/\s*(Statement\s+\d+\b)/g, "\n$1");          // Statement 1 / Statement 2 …
    t = t.replace(/[^\S\n]*(\d{1,2})\.\s+/g, "\n$1. ");
    t = breakSentences(t);
  }
  return t.split("\n").map(s => s.trim()).filter(Boolean)
    .map(line => `<span class="bline${/^(?:\d{1,2}|[A-E])\.\s/.test(line) ? " stmt" : ""}">${line}</span>`)
    .join("");
}

/* ---------- entrance animation helpers ---------- */
function countUp(el, target) {
  if (!el) return;
  const dur = 1000, t0 = performance.now();
  (function step(now) {
    const p = Math.min(1, (now - t0) / dur);
    el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))).toLocaleString();
    if (p < 1) requestAnimationFrame(step);
  })(t0);
}
function countUpTile(countEl) {
  const m = countEl.textContent.match(/^([\d,]+)(.*)$/);
  if (!m) return;
  const target = +m[1].replace(/,/g, ""), suffix = m[2];
  const dur = 900, t0 = performance.now();
  (function step(now) {
    const p = Math.min(1, (now - t0) / dur);
    countEl.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))).toLocaleString() + suffix;
    if (p < 1) requestAnimationFrame(step);
  })(t0);
}
function revealOnScroll() {
  if (!("IntersectionObserver" in window)) return;
  const els = $$(".subject-card,.year-card,.seo-links a,.exam-tile-card,.pp-teaser,.reveal-group > *,.reveal-land,.feat-card,.member-pass");
  els.forEach((el, i) => {
    if (!el.classList.contains("reveal-land") && !el.classList.contains("feat-card")) {
      el.classList.add("reveal");
    }
    el.style.setProperty("--reveal-i", i % 6);
  });
  const io = new IntersectionObserver(ents => {
    ents.forEach(e => {
      if (!e.isIntersecting) return;
      e.target.classList.add("reveal-in");
      e.target.classList.add("in");
      const count = e.target.querySelector(".count");
      if (count) countUpTile(count);
      io.unobserve(e.target);
    });
  }, { threshold: 0.12 });
  els.forEach(el => io.observe(el));
}

function initExamTickers() {
  document.documentElement.classList.add("js");
  document.querySelectorAll(".ticker-track").forEach(function (track) {
    var set = track.querySelector(".ticker-set");
    if (!set) return;
    // Avoid re-cloning on soft navigations
    if (track.dataset.ready === "1") return;
    var width = set.getBoundingClientRect().width;
    var target = Math.max(window.innerWidth, 600);
    while (width < target) {
      var filler = set.cloneNode(true);
      filler.setAttribute("aria-hidden", "true");
      track.appendChild(filler);
      width += filler.getBoundingClientRect().width;
    }
    Array.prototype.slice.call(track.children).forEach(function (child) {
      var clone = child.cloneNode(true);
      clone.setAttribute("aria-hidden", "true");
      track.appendChild(clone);
    });
    track.dataset.ready = "1";
  });
}

/* Homepage phone demo — cycles real-feeling PYQs across exams */
const DEMO_QS = [
  {
    pill: "UPSC", exam: "UPSC Prelims 2020", subject: "Indian Polity", tag: "Civil Services",
    q: "Which of the following is NOT a Fundamental Duty under the Indian Constitution?",
    opts: ["Uphold the sovereignty of India", "Pay taxes honestly", "Vote in elections", "Protect the natural environment"],
    correct: 2, why: "Voting is a constitutional right, not listed among the Fundamental Duties in Article 51A."
  },
  {
    pill: "JEE", exam: "JEE Main 2023", subject: "Physics", tag: "Engineering",
    q: "The SI unit of electric field is?",
    opts: ["Newton", "Volt / metre", "Coulomb", "Joule / second"],
    correct: 1, why: "Electric field is force per unit charge, which equals volt per metre."
  },
  {
    pill: "NEET", exam: "NEET-UG 2022", subject: "Biology", tag: "Medical",
    q: "Which organelle is called the powerhouse of the cell?",
    opts: ["Ribosome", "Golgi apparatus", "Mitochondrion", "Lysosome"],
    correct: 2, why: "Mitochondria produce ATP through cellular respiration."
  },
  {
    pill: "SSC", exam: "SSC CGL 2021", subject: "Reasoning", tag: "Staff Selection",
    q: "Complete the series: 2, 6, 12, 20, ?",
    opts: ["28", "30", "32", "36"],
    correct: 1, why: "Add consecutive even numbers: +4, +6, +8, then +10 → 30."
  },
  {
    pill: "Boards", exam: "Class 12 Boards", subject: "Chemistry", tag: "School boards",
    q: "pH of a neutral aqueous solution at 25°C is?",
    opts: ["0", "7", "14", "1"],
    correct: 1, why: "At 25°C, [H+] equals [OH−], so pH is 7."
  }
];

function initPhoneDemo() {
  const phone = $("#demo-phone");
  if (!phone) return;
  const body = $("#demo-body");
  const optsEl = $("#demo-opts");
  const exp = $("#demo-exp");
  const dots = $("#demo-dots");
  const pill = $("#demo-pill");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let i = 0;
  let timers = [];

  function clearTimers() {
    timers.forEach(clearTimeout);
    timers = [];
  }
  function later(fn, ms) {
    timers.push(setTimeout(fn, ms));
  }

  dots.innerHTML = DEMO_QS.map((_, idx) => `<i${idx === 0 ? ' class="on"' : ""}></i>`).join("");

  function render(idx, animate) {
    const item = DEMO_QS[idx];
    const keys = ["A", "B", "C", "D"];
    $("#demo-exam").textContent = item.exam;
    $("#demo-subj").textContent = item.subject;
    $("#demo-tag").textContent = item.tag;
    $("#demo-q").textContent = item.q;
    $("#demo-qnum").textContent = `Q ${idx + 1} / ${DEMO_QS.length}`;
    $("#demo-why").textContent = item.why;
    $("#demo-verdict").innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12.5 10 18 20 6"/></svg> Correct · Option ${keys[item.correct]}`;
    pill.textContent = item.pill;
    pill.classList.remove("swap");
    optsEl.innerHTML = item.opts.map((label, oi) => (
      `<div class="opt" data-i="${oi}"><span class="opt-key">${keys[oi]}</span><span class="opt-label">${label}</span><span class="check-badge" aria-hidden="true">✓</span></div>`
    )).join("");
    exp.hidden = false;
    exp.classList.remove("show");
    $$("#demo-dots i").forEach((d, di) => d.classList.toggle("on", di === idx));

    if (reduce) {
      $$("#demo-opts .opt").forEach(o => o.classList.add("show"));
      const correct = optsEl.querySelector(`[data-i="${item.correct}"]`);
      if (correct) correct.classList.add("is-correct");
      exp.classList.add("show");
      return;
    }

    if (animate) {
      body.classList.remove("out");
      body.classList.add("in");
      requestAnimationFrame(() => {
        body.classList.remove("in");
      });
    }

    $$("#demo-opts .opt").forEach((o, oi) => {
      later(() => o.classList.add("show"), 120 + oi * 90);
    });

    later(() => {
      const target = optsEl.querySelector(`[data-i="${item.correct}"]`);
      if (!target) return;
      target.classList.add("is-tap");
      later(() => {
        target.classList.remove("is-tap");
        target.classList.add("is-correct");
        exp.classList.add("show");
      }, 280);
    }, 1600);
  }

  function next() {
    if (reduce) {
      i = (i + 1) % DEMO_QS.length;
      render(i, false);
      later(next, 5000);
      return;
    }
    body.classList.add("out");
    pill.classList.add("swap");
    later(() => {
      clearTimers();
      i = (i + 1) % DEMO_QS.length;
      render(i, true);
      later(next, 7200);
    }, 380);
  }

  render(0, false);
  if (!reduce) later(next, 7200);
  else later(next, 5000);
}

/* ---------- init ---------- */
// PYQs across the other exam sections (JEE/NEET/Board/Defence/SSC CGL),
// which live in separate static exam-data JSON, not loaded here — update
// this after each exam-data import so the homepage stat stays accurate.
// Marketing total shown on the homepage counter (keep in sync with copy: 20,000+).
const DISPLAY_PYQ_TOTAL = 20000;
renderSubjects();
renderYears();
document.body.classList.add("anim-ready");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const countDelay = reduceMotion ? 0 : 520;
setTimeout(() => {
  countUp($("#stat-q"), DISPLAY_PYQ_TOTAL);
  countUp($("#stat-f"), 6);
  countUp($("#stat-y"), YEARS.length);
  $$(".exams-hero .stat-row .stat").forEach(s => s.classList.add("is-live"));
}, countDelay);
initExamTickers();
initPhoneDemo();
revealOnScroll();
$("#year").textContent = new Date().getFullYear();
showView("home");

// mock-pool.json (~490KB gzipped) backs every non-UPSC "Practice"/Smart
// Mock click. Warm it in idle time after the page is interactive so that
// click feels instant instead of stalling on a cold fetch.
(function prefetchMockPool() {
  const start = () => ensureMockPool().catch(() => {});
  if ("requestIdleCallback" in window) requestIdleCallback(start, { timeout: 4000 });
  else setTimeout(start, 2000);
})();
