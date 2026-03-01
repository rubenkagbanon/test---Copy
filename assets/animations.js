(() => {
  let rpsObserverStarted = false;
  const rootDoc = (() => {
    try {
      if (window.parent && window.parent.document) return window.parent.document;
    } catch (_) {}
    return document;
  })();

  // determine color based on score and whether item is in reversed category
  const getColorForScore = (score, reversed = false) => {
    if (!reversed) {
      if (score <= 33) {
        return "#2eaf5d"; // Vert
      } else if (score <= 66) {
        return "#f2b636"; // Jaune
      } else {
        return "#e04f5f"; // Rouge
      }
    } else {
      if (score <= 33) {
        return "#e04f5f"; // Rouge
      } else if (score <= 66) {
        return "#f2b636"; // Jaune
      } else {
        return "#2eaf5d"; // Vert
      }
    }
  };

  const animateRpsGauges = () => {
    const gauges = rootDoc.querySelectorAll("[data-gauge-score]");
    gauges.forEach((el) => {
      const scoreRaw = el.dataset.gaugeScore || "0";
      const score = Number(scoreRaw);
      if (!Number.isFinite(score)) return;

      const fill = el.querySelector(".rps-gauge-fill");
      if (!fill) return;

      const label = el.dataset.gaugeLabel || "";
      const reversed = [
        "Charge de travail",
        "Rythme de travail",
        "Exigences cognitive",
        "Exigence emotionnelle",
        "Stress",
        "Epuisement",
        "Insecurite professionnelle",
        "Conflit de roles",
      ].includes(label);

      const color = getColorForScore(score, reversed);
      fill.style.backgroundColor = color;

      // Update CSS variable for animation
      el.style.setProperty("--gauge-score", `${score}%`);
    });
  };

  const animateRpsScores = () => {
    const scores = rootDoc.querySelectorAll("[data-rps-score='true']");
    scores.forEach((el, idx) => {
      const targetRaw = el.dataset.rpsTarget || "0";
      const target = Number(targetRaw);
      const decimals = Number(el.dataset.rpsDecimals || "1");
      const suffix = el.dataset.rpsSuffix ?? "";
      const finalText = el.dataset.rpsFinal || "";
      if (!Number.isFinite(target)) return;
      if (el.dataset.rpsAnimating === "1") return;
      if (
        el.dataset.rpsAnimated === "1" &&
        el.dataset.rpsLastTarget === targetRaw &&
        (el.dataset.rpsLastDecimals || "") === String(decimals) &&
        (el.dataset.rpsLastSuffix || "") === suffix
      ) {
        return;
      }

      const duration = Math.min(1500, 700 + idx * 80);
      const startAt = performance.now();
      el.dataset.rpsAnimating = "1";

      // Find parent gauge and update color during animation
      const gaugeEl = el.closest(".rps-line-group")?.querySelector(".rps-gauge");

      const step = (now) => {
        const t = Math.min(1, (now - startAt) / duration);
        const eased = 1 - Math.pow(1 - t, 3);
        const current = target * eased;
        el.textContent = `${current.toFixed(decimals)}${suffix}`;

        // Update gauge fill color and width progressively
        if (gaugeEl) {
          const fill = gaugeEl.querySelector(".rps-gauge-fill");
          if (fill) {
            const label = gaugeEl.dataset.gaugeLabel || "";
            const reversed = [
              "Charge de travail",
              "Rythme de travail",
              "Exigences cognitive",
              "Exigence emotionnelle",
              "Stress",
              "Epuisement",
              "Insecurite professionnelle",
              "Conflit de roles",
            ].includes(label);
            const color = getColorForScore(current, reversed);
            fill.style.backgroundColor = color;
            gaugeEl.style.setProperty("--gauge-score", `${current}%`);
          }
        }

        if (t < 1) {
          requestAnimationFrame(step);
          return;
        }

        el.textContent = finalText || `${target.toFixed(decimals)}${suffix}`;
        el.dataset.rpsAnimated = "1";
        el.dataset.rpsLastTarget = targetRaw;
        el.dataset.rpsLastDecimals = String(decimals);
        el.dataset.rpsLastSuffix = suffix;
        el.dataset.rpsAnimating = "0";

        // Final color update
        if (gaugeEl) {
          const fill = gaugeEl.querySelector(".rps-gauge-fill");
          if (fill) {
            const label = gaugeEl.dataset.gaugeLabel || "";
            const reversed = [
              "Charge de travail",
              "Rythme de travail",
              "Exigences cognitive",
              "Exigence emotionnelle",
              "Stress",
              "Epuisement",
              "Insecurite professionnelle",
              "Conflit de roles",
            ].includes(label);
            fill.style.backgroundColor = getColorForScore(target, reversed);
            gaugeEl.style.setProperty("--gauge-score", `${target}%`);
          }
        }
      };

      requestAnimationFrame(step);
    });
  };

  const init = () => {
    const revealTargets = document.querySelectorAll(
      ".rps-line-group, .stPlotlyChart, [data-testid='stMetric']"
    );
    const revealTargetsParent = rootDoc.querySelectorAll(
      ".rps-line-group, .stPlotlyChart, [data-testid='stMetric']"
    );
    const targets = revealTargetsParent.length ? revealTargetsParent : revealTargets;

    if (!("IntersectionObserver" in window)) {
      targets.forEach((el) => {
        el.style.opacity = "1";
        el.style.transform = "translateY(0)";
      });
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const el = entry.target;
          el.style.transition = "opacity 420ms ease, transform 420ms ease";
          el.style.opacity = "1";
          el.style.transform = "translateY(0)";
          observer.unobserve(el);
        });
      },
      { threshold: 0.12 }
    );

    targets.forEach((el, idx) => {
      el.style.opacity = "0";
      el.style.transform = "translateY(10px)";
      el.style.transitionDelay = `${Math.min(idx * 30, 240)}ms`;
      observer.observe(el);
    });

    animateRpsScores();
    animateRpsGauges();
    [120, 350, 700].forEach((ms) => window.setTimeout(() => { animateRpsScores(); animateRpsGauges(); }, ms));

    if (!rpsObserverStarted && "MutationObserver" in window) {
      const mo = new MutationObserver(() => {
        animateRpsScores();
        animateRpsGauges();
      });
      const obsBody = rootDoc.body || document.body;
      if (obsBody) {
        mo.observe(obsBody, { childList: true, subtree: true });
      }
      rpsObserverStarted = true;
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
