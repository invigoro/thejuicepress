(function () {
  "use strict";

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "text") n.textContent = attrs[k];
        else if (k === "html") n.innerHTML = attrs[k];
        else if (k === "className") n.className = attrs[k];
        else n.setAttribute(k, attrs[k]);
      });
    }
    (children || []).forEach(function (c) {
      if (c != null) n.appendChild(c);
    });
    return n;
  }

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
    return a;
  }

  function parseCfg() {
    var node = document.getElementById("quiz-data");
    if (!node || !node.textContent) return null;
    try {
      return JSON.parse(node.textContent.trim());
    } catch (e) {
      console.error("quiz-data JSON parse error", e);
      return null;
    }
  }

  function setHashSlug(slug) {
    var url = window.location.pathname + window.location.search + "#" + encodeURIComponent(slug);
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, "", url);
    } else {
      window.location.hash = slug;
    }
  }

  function clearHash() {
    var url = window.location.pathname + window.location.search;
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, "", url);
    } else {
      window.location.hash = "";
    }
  }

  function allQuestionsAnswered(cfg, selections) {
    for (var i = 0; i < cfg.questions.length; i++) {
      var qid = cfg.questions[i].id;
      if (!selections[qid]) return false;
    }
    return true;
  }

  function scrollToFirstUnanswered(questions, selections) {
    for (var i = 0; i < questions.length; i++) {
      if (!selections[questions[i].id]) {
        var node = document.getElementById("quiz-q-" + i);
        if (node) node.scrollIntoView({ behavior: "smooth", block: "start" });
        return;
      }
    }
  }

  function findResultBySlug(cfg, slug) {
    if (!slug) return null;
    try {
      slug = decodeURIComponent(slug);
    } catch (e) {}
    for (var i = 0; i < cfg.results.length; i++) {
      if (cfg.results[i].slug === slug) return cfg.results[i];
    }
    return null;
  }

  function computeWinner(cfg, selections) {
    var scores = {};
    cfg.results.forEach(function (r) {
      scores[r.id] = 0;
    });
    cfg.questions.forEach(function (q) {
      var aid = selections[q.id];
      if (!aid) return;
      var ans = null;
      q.answers.forEach(function (a) {
        if (String(a.id) === String(aid)) ans = a;
      });
      if (!ans || !ans.weights) return;
      Object.keys(ans.weights).forEach(function (rid) {
        var w = ans.weights[rid];
        var id = parseInt(rid, 10);
        if (!scores.hasOwnProperty(id)) scores[id] = 0;
        scores[id] += w;
      });
    });
    var bestId = null;
    var bestScore = -Infinity;
    cfg.results.forEach(function (r) {
      var s = scores[r.id] || 0;
      if (
        bestId === null ||
        s > bestScore ||
        (s === bestScore && r.id < bestId)
      ) {
        bestScore = s;
        bestId = r.id;
      }
    });
    if (bestId == null) return cfg.results[0];
    for (var j = 0; j < cfg.results.length; j++) {
      if (cfg.results[j].id === bestId) return cfg.results[j];
    }
    return cfg.results[0];
  }

  function renderResult(parent, res, showRetake) {
    var prev = parent.querySelector("#quiz-outcome");
    if (prev) prev.remove();
    var wrap = el("div", { className: "quiz-outcome", id: "quiz-outcome" });
    wrap.appendChild(el("h2", { className: "quiz-outcome-title", text: res.title }));
    var body = el("div", { className: "quiz-outcome-body" });
    body.innerHTML = res.contentHtml || "";
    wrap.appendChild(body);
    if (showRetake) {
      var p = el("p", { className: "quiz-retake-wrap" });
      var btn = el("button", {
        type: "button",
        className: "quiz-retake-button",
        text: "Take the quiz",
      });
      btn.addEventListener("click", function () {
        clearHash();
        window.location.reload();
      });
      p.appendChild(btn);
      wrap.appendChild(p);
    }
    parent.appendChild(wrap);
    wrap.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderIntro(container, cfg) {
    if (!cfg.introHtml) return;
    var intro = el("section", { className: "quiz-intro" });
    intro.innerHTML = cfg.introHtml;
    container.appendChild(intro);
  }

  function runSharedResultView(cfg, mount, slug) {
    mount.innerHTML = "";
    var res = findResultBySlug(cfg, slug);
    if (!res) {
      mount.appendChild(
        el("p", { text: "That quiz result was not found. Try removing the # from the URL." })
      );
      return;
    }
    renderIntro(mount, cfg);
    renderResult(mount, res, true);
  }

  function runInteractive(cfg, mount) {
    var questions = cfg.questions.slice();
    if (cfg.randomQuestionOrder) {
      questions = shuffle(questions);
    }

    renderIntro(mount, cfg);

    var selections = {};
    var formWrap = el("div", { className: "quiz-questions" });

    questions.forEach(function (q, idx) {
      var sec = el("section", {
        className: "quiz-question",
        id: "quiz-q-" + idx,
        "data-question-id": q.id,
      });
      sec.appendChild(el("h3", { className: "quiz-question-prompt", text: q.prompt }));
      var opts = el("div", { className: "quiz-answers", role: "group" });
      q.answers.forEach(function (a) {
        var b = el("button", {
          type: "button",
          className: "quiz-answer-button",
          "data-answer-id": a.id,
          text: a.label,
        });
        b.addEventListener("click", function () {
          selections[q.id] = String(a.id);
          opts.querySelectorAll(".quiz-answer-button").forEach(function (btn) {
            btn.classList.remove("is-selected");
          });
          b.classList.add("is-selected");

          if (!allQuestionsAnswered(cfg, selections)) {
            if (idx < questions.length - 1) {
              var next = document.getElementById("quiz-q-" + (idx + 1));
              if (next) next.scrollIntoView({ behavior: "smooth", block: "start" });
            } else {
              scrollToFirstUnanswered(questions, selections);
            }
            return;
          }

          var winner = computeWinner(cfg, selections);
          setHashSlug(winner.slug);
          renderResult(mount, winner, true);
        });
        opts.appendChild(b);
      });
      sec.appendChild(opts);
      formWrap.appendChild(sec);
    });

    mount.appendChild(formWrap);
  }

  function main() {
    var cfg = parseCfg();
    var mount = document.getElementById("quiz-app");
    if (!cfg || !mount) return;

    var hash = (window.location.hash || "").replace(/^#/, "");
    if (hash) {
      runSharedResultView(cfg, mount, hash);
    } else {
      runInteractive(cfg, mount);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }
})();
