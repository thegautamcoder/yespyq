/* Reveals gated exam options/answers when window.PAY.isPaid().
   Free HTML only contains the question stem + unlock CTA.
   Options/explanation live in <script type="application/json" class="q-payload">. */
(function () {
  function renderPaid(qb, data) {
    var host = qb.querySelector("[data-opts-host]");
    var explain = qb.querySelector("[data-exp]");
    var gate = qb.querySelector(".answer-gate");
    if (!host || !data || !data.o) return;
    var html = "";
    var a = +data.a;
    for (var i = 0; i < data.o.length; i++) {
      var cls = "option" + (i === a ? " correct" : "");
      html += '<div class="' + cls + '"><span class="key">' + String.fromCharCode(97 + i) +
        '</span><span>' + data.o[i] + '</span></div>';
    }
    host.innerHTML = html;
    if (explain) {
      var letter = String.fromCharCode(97 + a);
      explain.innerHTML =
        '<div class="verdict ok">✓ Correct answer: ' + letter + ') ' + (data.o[a] || "") + '</div>' +
        '<div class="exp-body"><span class="lbl">Explanation</span>' + (data.exp || "") + '</div>';
      explain.classList.remove("hidden");
    }
    if (gate) gate.style.display = "none";
    qb.dataset.revealed = "1";
  }

  function renderFree(qb) {
    var host = qb.querySelector("[data-opts-host]");
    var explain = qb.querySelector("[data-exp]");
    var gate = qb.querySelector(".answer-gate");
    if (host) host.innerHTML = "";
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
