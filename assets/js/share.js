(function () {
  "use strict";

  function el(tag, attrs) {
    var n = document.createElement(tag);
    Object.keys(attrs).forEach(function (k) {
      if (k === "text") n.textContent = attrs[k];
      else if (k === "className") n.className = attrs[k];
      else n.setAttribute(k, attrs[k]);
    });
    return n;
  }

  function shareTargets(url, text) {
    var u = encodeURIComponent(url);
    var t = encodeURIComponent(text);
    var both = encodeURIComponent(text + " " + url);
    return [
      ["Facebook", "https://www.facebook.com/sharer/sharer.php?u=" + u],
      ["X (Twitter)", "https://x.com/intent/post?text=" + t + "&url=" + u],
      ["Bluesky", "https://bsky.app/intent/compose?text=" + both],
      ["Threads", "https://www.threads.com/intent/post?text=" + both],
      ["Reddit", "https://www.reddit.com/submit?url=" + u + "&title=" + t],
      ["Tumblr", "https://www.tumblr.com/widgets/share/tool?canonicalUrl=" + u + "&title=" + t],
      ["WhatsApp", "https://wa.me/?text=" + both],
      ["Telegram", "https://t.me/share/url?url=" + u + "&text=" + t],
      ["LinkedIn", "https://www.linkedin.com/sharing/share-offsite/?url=" + u],
      ["Email", "mailto:?subject=" + t + "&body=" + encodeURIComponent(text + "\r\n\r\n" + url)],
    ];
  }

  var panelCount = 0;

  // Returns a share button and the hidden panel of share options it toggles.
  // opts: { label, url, text, title }
  function createShare(opts) {
    panelCount += 1;
    var panel = el("div", { className: "share-panel", id: "share-panel-" + panelCount });
    panel.hidden = true;

    var copyBtn = el("button", { type: "button", className: "share-link", text: "Copy link" });
    copyBtn.addEventListener("click", function () {
      function copied() {
        copyBtn.textContent = "Link copied!";
        setTimeout(function () {
          copyBtn.textContent = "Copy link";
        }, 2000);
      }
      function fallback() {
        window.prompt("Copy this link:", opts.url);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(opts.url).then(copied, fallback);
      } else {
        fallback();
      }
    });
    panel.appendChild(copyBtn);

    shareTargets(opts.url, opts.text).forEach(function (target) {
      var attrs = { className: "share-link", href: target[1], text: target[0] };
      if (target[1].indexOf("mailto:") !== 0) {
        attrs.target = "_blank";
        attrs.rel = "noopener noreferrer";
      }
      panel.appendChild(el("a", attrs));
    });

    if (navigator.share) {
      var moreBtn = el("button", { type: "button", className: "share-link", text: "More…" });
      moreBtn.addEventListener("click", function () {
        navigator.share({ title: opts.title, text: opts.text, url: opts.url }).catch(function () {});
      });
      panel.appendChild(moreBtn);
    }

    var button = el("button", {
      type: "button",
      className: "button",
      "aria-expanded": "false",
      "aria-controls": panel.id,
      text: opts.label,
    });
    button.addEventListener("click", function () {
      panel.hidden = !panel.hidden;
      button.setAttribute("aria-expanded", String(!panel.hidden));
    });

    return { button: button, panel: panel };
  }

  window.juicePressShare = createShare;

  // <div data-share-label="Share article" data-share-text="Headline"></div>
  // gets a share button and panel for the current page.
  function mountShares() {
    document.querySelectorAll("[data-share-label]").forEach(function (mount) {
      var text = mount.getAttribute("data-share-text");
      var share = createShare({
        label: mount.getAttribute("data-share-label"),
        url: window.location.origin + window.location.pathname,
        text: text,
        title: text,
      });
      mount.appendChild(share.button);
      mount.appendChild(share.panel);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountShares);
  } else {
    mountShares();
  }
})();
