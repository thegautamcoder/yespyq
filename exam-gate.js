/* Reveals the gated answer key + explanation when window.PAY.isPaid().
   Options are always in the free HTML; only the correct-answer marking
   and explanation live in <script type="application/json" class="q-payload">. */
(function () {
  function renderPaid(qb, data) {
    var opts = qb.querySelectorAll(".qpage-options .option");
    var explain = qb.querySelector("[data-exp]");
    var gate = qb.querySelector(".answer-gate");
    if (!opts.length || !data) return;
    var a = +data.a;
    opts.forEach(function (o, i) { o.classList.toggle("correct", i === a); });
    if (explain) {
      var letter = String.fromCharCode(97 + a);
      var ansText = opts[a] ? opts[a].querySelector("span:last-child").textContent : "";
      explain.innerHTML =
        '<div class="verdict ok">✓ Correct answer: ' + letter + ') ' + ansText + '</div>' +
        '<div class="exp-body"><span class="lbl">Explanation</span>' + (data.exp || "") + '</div>';
      explain.classList.remove("hidden");
    }
    if (gate) gate.style.display = "none";
    qb.dataset.revealed = "1";
    // explanation is injected after KaTeX's one-time DOMContentLoaded pass,
    // so it never got auto-rendered — render it explicitly now.
    if (window.renderMathInElement) {
      renderMathInElement(qb, {
        delimiters: [
          {left: "$$", right: "$$", display: true},
          {left: "\\[", right: "\\]", display: true},
          {left: "\\(", right: "\\)", display: false}
        ],
        throwOnError: false
      });
    }
  }

  function renderFree(qb) {
    var opts = qb.querySelectorAll(".qpage-options .option");
    var explain = qb.querySelector("[data-exp]");
    var gate = qb.querySelector(".answer-gate");
    opts.forEach(function (o) { o.classList.remove("correct"); });
    if (explain) { explain.innerHTML = ""; explain.classList.add("hidden"); }
    if (gate) gate.style.display = "";
    delete qb.dataset.revealed;
  }

  function reveal(paid) {
    document.querySelectorAll(".qblock[data-gated]").forEach(function (qb) {
      if (paid) {
        if (qb.dataset.revealed === "1") return;
        var node = qb.querySelector("script.q-payload");
        if (!node) return;
        try { renderPaid(qb, JSON.parse(node.textContent)); } catch (e) {}
      } else {
        renderFree(qb);
      }
    });
  }

  function waitForPay(tries) {
    if (window.PAY) { reveal(PAY.isPaid()); return; }
    if (tries <= 0) return;
    setTimeout(function () { waitForPay(tries - 1); }, 100);
  }
  waitForPay(50);

  var prevOnPayChange = window.onPayChange;
  window.onPayChange = function () {
    if (typeof prevOnPayChange === "function") prevOnPayChange();
    if (window.PAY) reveal(PAY.isPaid());
  };
})();
