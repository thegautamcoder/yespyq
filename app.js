// YESPYQ — question-bank browser (left filters + show-all). Compact data keys: i,q,o,a,s,c,y

const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

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
      { id: "maths", name: "Maths", icon: "➗" }
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
    exp: raw.exp || ""
  };
}

async function ensureExamBank(examId) {
  const meta = EXAM_META[examId];
  if (!meta) throw new Error("Unknown exam: " + examId);
  if (examId === "upsc") {
    return { questions: UPSC_QUESTIONS, subjects: UPSC_SUBJECTS };
  }
  if (bankCache[examId]) return bankCache[examId];
  const res = await fetch(meta.file);
  if (!res.ok) throw new Error("Failed to load " + meta.file);
  const raw = await res.json();
  const questions = (Array.isArray(raw) ? raw : [])
    .map(normalizeExamQ)
    .filter(isCleanQ);
  const bank = { questions, subjects: meta.subjects };
  bankCache[examId] = bank;
  return bank;
}

async function setExam(examId, opts) {
  opts = opts || {};
  const meta = EXAM_META[examId] || EXAM_META.upsc;
  const status = $("#qlist-title");
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
  if (typeof a !== "number" || a < 0 || a >= opts.length) return false;
  if (/\bOptions?\s*$/.test(qq)) return false;                 // truncated stem
  const BAD = /consider the following|incorrect\s*:|correct\s*:|\([a-d]\)\s|\(20\d\d\)|select the correct answer/i;
  for (let o of opts) {
    o = (o || "").trim();
    if (o.length < 1 || o.length > 180) return false;          // empty / explanation dumped in
    if (o.length <= 2 && !/^[a-z0-9]+$/i.test(o)) return false; // punctuation-only
    if (BAD.test(o)) return false;                              // embedded question/explanation
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
}

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
  const opts = q.o.map((opt, i) =>
    `<button class="option" data-opt="${i}"><span class="key">${String.fromCharCode(97 + i)}</span><span>${escapeHTML(opt)}</span></button>`).join("");
  return `<article class="qcard" data-qid="${q.i}">
      <div class="qtags">
        <span class="qnum">Q${serial}</span>
        <span class="qtag">${sub.icon} ${sub.name}</span>
        ${q.y ? `<span class="qtag">${q.y}</span>` : ""}
      </div>
      <div class="qtext">${formatBody(q.q, true)}</div>
      <div class="options">${opts}</div>
      <div class="explain hidden" data-exp></div>
    </article>`;
}

function renderMore() {
  const list = currentList();
  const gated = window.PAY && !PAY.isPaid();
  const cap = gated ? Math.min(list.length, PAY.freeQuestions()) : list.length;
  const next = list.slice(shown, Math.min(shown + PAGE, cap));
  const frag = document.createElement("div");
  frag.innerHTML = next.map((q, k) => cardHTML(q, shown + k + 1)).join("");
  const wrap = $("#qlist");
  while (frag.firstChild) wrap.appendChild(frag.firstChild);
  shown += next.length;
  const more = $("#load-more");
  if (gated && shown >= cap && cap < list.length) {
    more.classList.add("hidden");
    showUnlockStrip(list.length - cap);
  } else {
    removeUnlockStrip();
    more.classList.toggle("hidden", shown >= list.length);
    if (shown < list.length) more.textContent = `Show more (${list.length - shown} left)`;
  }
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
  const expl = q.exp || (window.EXP && window.EXP[q.i]) || "Explanation will appear here.";
  const ex = card.querySelector("[data-exp]");
  ex.innerHTML = `
    <div class="verdict ${correct ? "ok" : "no"}">${correct ? "✓ Correct" : "✗ Incorrect"} — Answer: ${String.fromCharCode(97 + q.a)}) ${escapeHTML(q.o[q.a])}</div>
    <div class="exp-body"><span class="lbl">Explanation</span>${formatBody(expl, false)}</div>
    ${(window.PAY && PAY.nudgeHTML) ? PAY.nudgeHTML() : ""}`;
  ex.classList.remove("hidden");
  if (correct && !answered.has(q.i)) {
    answered.add(q.i);
    earnXp(10);
    const r = opt.getBoundingClientRect();
    floatXp(r.right - 56, r.top, "+10 XP");
  }
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
    else showView(n);
    return;
  }
  if (e.target.closest("[data-action='start']")) { e.preventDefault(); openExamPicker("browse"); return; }
  const sc = e.target.closest("[data-subject]");
  if (sc) { openBrowse({ subject: sc.dataset.subject, year: null }); return; }
  const yc = e.target.closest("[data-year]");
  if (yc) { openBrowse({ subject: null, year: +yc.dataset.year }); return; }
  const fexam = e.target.closest("[data-fexam]");
  if (fexam) { setExam(fexam.dataset.fexam, { mode: "browse", subject: null, year: null }); return; }
  const fs = e.target.closest("[data-fsub]");
  if (fs) { openBrowse({ subject: fs.dataset.fsub || null, year: filter.year }); return; }
  const fy = e.target.closest("[data-fyear]");
  if (fy) { filter.year = fy.dataset.fyear ? +fy.dataset.fyear : null; renderFilters(); applyFilter(); return; }
  if (e.target.closest("#filter-toggle")) { $("#filters").classList.toggle("open"); return; }
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
  const sub = subjectMap[q.s] || { icon: "📘", name: q.s || "Subject" };
  $("#quiz-body").innerHTML = `
    <div class="quiz-card">
      <div class="quiz-meta">
        <span class="qtag">${sub.icon} ${sub.name}</span>
        ${q.y ? `<span class="qtag">${q.y}</span>` : ""}
        <span class="quiz-count">${quiz.idx + 1} / ${quiz.total}</span>
      </div>
      <div class="qtext quiz-q">${formatBody(q.q, true)}</div>
      <div class="options quiz-options">
        ${q.o.map((o, i) => `<button class="option" data-qa="${i}"><span class="key">${String.fromCharCode(97 + i)}</span><span>${escapeHTML(o)}</span></button>`).join("")}
      </div>
      <div class="explain hidden" data-exp></div>
      <div class="quiz-actions"><button class="btn btn-primary btn-lg hidden" data-quiz-next>Next →</button></div>
    </div>`;
  window.scrollTo({ top: 0 });
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
  const ex = body.querySelector("[data-exp]");
  ex.innerHTML = `
    <div class="verdict ${correct ? "ok" : "no"}">${correct ? "✓ Correct" : "✗ Incorrect"} — Answer: ${String.fromCharCode(97 + q.a)}) ${escapeHTML(q.o[q.a])}</div>
    <div class="exp-body"><span class="lbl">Explanation</span>${formatBody(expl, false)}</div>
    ${(window.PAY && PAY.nudgeHTML) ? PAY.nudgeHTML() : ""}`;
  ex.classList.remove("hidden");
  const next = body.querySelector("[data-quiz-next]");
  next.textContent = quiz.idx + 1 >= quiz.total ? "See results →" : "Next →";
  next.classList.remove("hidden");
  ex.querySelector(".verdict")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
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
  const els = $$(".subject-card,.year-card,.seo-links a,.exam-tile-card,.pp-teaser,.reveal-group > *,.reveal-land,.feat-card");
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

/* ---------- init ---------- */
// PYQs across the other exam sections (JEE/NEET/Board/Defence/SSC CGL),
// which live in separate static exam-data JSON, not loaded here — update
// this after each exam-data import so the homepage stat stays accurate.
const OTHER_EXAM_PYQS = 10078;
renderSubjects();
renderYears();
if (document.querySelector(".ticker-track")) initExamTickers();
revealOnScroll();
$("#year").textContent = new Date().getFullYear();
showView("home");
