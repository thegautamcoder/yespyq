/* Reveals/hides gated exam-question answers based on window.PAY.isPaid().
   theme.js loads pay-config.js -> auth-pay.js asynchronously, after
   DOMContentLoaded already fired, so this polls briefly for window.PAY. */
(function () {
  function reveal(paid) {
    document.querySelectorAll(".qblock[data-gated]").forEach(function (qb) {
      var gate = qb.querySelector(".answer-gate");
      var explain = qb.querySelector(".explain");
      var opts = qb.querySelectorAll(".option");
      if (paid) {
        var a = +qb.dataset.a;
        if (opts[a]) opts[a].classList.add("correct");
        if (explain) explain.classList.remove("hidden");
        if (gate) gate.style.display = "none";
      } else {
        opts.forEach(function (o) { o.classList.remove("correct"); });
        if (explain) explain.classList.add("hidden");
        if (gate) gate.style.display = "";
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
