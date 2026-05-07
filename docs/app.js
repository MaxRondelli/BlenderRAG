(() => {
  const HF = window.HF_BASE;
  const DATA = window.DATASET;
  const N = window.VARIANTS_PER_CATEGORY;

  const explorerView = document.getElementById("explorerView");
  const sceneFilters = document.getElementById("sceneFilters");
  const shuffleBtn = document.getElementById("shuffleBtn");

  const modal = document.getElementById("modal");
  const modalImg = document.getElementById("modalImg");
  const modalMv = document.getElementById("modalMv");
  const modalImgWrap = document.getElementById("modalImgWrap");
  const modalSpin = document.getElementById("modalSpin");

  // Local mesh root (relative to site)
  const MESHES = "meshes";
  const meshUrl = (scene, cat, i) => `${MESHES}/${scene}/${cat}/${i}.glb`;
  const imageUrl = (scene, cat, i) => `${HF}/${scene}/${cat}/image${i}.png`;
  const modalTitle = document.getElementById("modalTitle");
  const modalDesc = document.getElementById("modalDesc");
  const modalCode = document.getElementById("modalCode");
  const modalImgDl = document.getElementById("modalImgDl");
  const modalCodeDl = document.getElementById("modalCodeDl");
  const modalCopy = document.getElementById("modalCopy");
  const modalClose = document.getElementById("modalClose");

  let currentScene = "all";
  const SAMPLE_SIZE = 24;

  // Variants whose mesh failed to generate — exclude from explorer/marquee.
  const BROKEN = new Set([
    "outdoor/cactus/6", "outdoor/cactus/7",
    "outdoor/hedge/2",
    "outdoor/tree/3", "outdoor/tree/5",
  ]);
  const BROKEN_CATS = new Set(["outdoor/grass"]); // entirely missing

  const isBroken = (scene, category, idx) =>
    BROKEN_CATS.has(`${scene}/${category}`) || BROKEN.has(`${scene}/${category}/${idx}`);

  // ---- helpers ----
  const titleCase = (s) => s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  const allVariants = () => {
    const list = [];
    for (const cat of DATA.indoor) for (let i = 1; i <= N; i++) {
      if (!isBroken("indoor", cat, i)) list.push({ scene: "indoor", category: cat, idx: i });
    }
    for (const cat of DATA.outdoor) for (let i = 1; i <= N; i++) {
      if (!isBroken("outdoor", cat, i)) list.push({ scene: "outdoor", category: cat, idx: i });
    }
    return list;
  };

  const sample = (n) => {
    const pool = allVariants().filter((v) => currentScene === "all" || v.scene === currentScene);
    // pick n distinct random items, avoiding duplicate categories where possible
    const byCat = new Map();
    for (const v of pool) {
      if (!byCat.has(v.category)) byCat.set(v.category, []);
      byCat.get(v.category).push(v);
    }
    const cats = [...byCat.keys()].sort(() => Math.random() - 0.5);
    const picks = [];
    for (const c of cats) {
      const arr = byCat.get(c);
      picks.push(arr[Math.floor(Math.random() * arr.length)]);
      if (picks.length >= n) break;
    }
    // if we still need more (small filter), fill with random from pool
    while (picks.length < n && pool.length > picks.length) {
      const v = pool[Math.floor(Math.random() * pool.length)];
      if (!picks.find((p) => p.scene === v.scene && p.category === v.category && p.idx === v.idx)) picks.push(v);
    }
    return picks;
  };

  const renderSample = () => {
    explorerView.innerHTML = "";
    const grid = document.createElement("div");
    grid.className = "variant-grid";
    sample(SAMPLE_SIZE).forEach(({ scene, category, idx }) => {
      const v = document.createElement("div");
      v.className = "variant";
      const wrap = document.createElement("div");
      wrap.className = "img-wrap";
      wrap.appendChild(make3DCard(scene, category, idx, "25deg"));
      const meta = document.createElement("div");
      meta.className = "meta";
      meta.innerHTML = `<strong style="text-transform:capitalize;">${titleCase(category)}</strong><span>${scene}</span>`;
      v.appendChild(wrap); v.appendChild(meta);
      v.addEventListener("click", () => openVariant(scene, category, idx));
      grid.appendChild(v);
    });
    explorerView.appendChild(grid);
  };

  const openVariant = async (scene, category, idx) => {
    const imgUrl = `${HF}/${scene}/${category}/image${idx}.png`;
    const codeUrl = `${HF}/${scene}/${category}/code${idx}.py`;
    const txtUrl = `${HF}/${scene}/${category}/txt${idx}.txt`;

    modalImg.src = imgUrl;
    modalMv.setAttribute("src", meshUrl(scene, category, idx));
    modalTitle.textContent = `${titleCase(category)} — Variant ${idx}`;
    modalDesc.textContent = "Loading description…";
    modalCode.textContent = "Loading code…";
    modalCode.removeAttribute("data-highlighted");
    modalCode.className = "language-python";
    modalImgDl.href = imgUrl;
    modalCodeDl.href = codeUrl;
    modal.classList.add("open");
    document.body.style.overflow = "hidden";
    // ensure rotation is on when variant is opened
    modalMv.setAttribute("auto-rotate", "");
    modalSpin.textContent = "⏸ Pause rotation";

    // Fetch description and code in parallel
    try {
      const [descRes, codeRes] = await Promise.all([fetch(txtUrl), fetch(codeUrl)]);
      modalDesc.textContent = descRes.ok ? (await descRes.text()).trim() : "(description unavailable)";
      modalCode.textContent = codeRes.ok ? await codeRes.text() : "// failed to load code";
    } catch (e) {
      modalDesc.textContent = "(failed to load — check your connection)";
      modalCode.textContent = "// network error";
    }
    if (window.hljs) {
      try { window.hljs.highlightElement(modalCode); } catch {}
    }
  };

  const closeModal = () => {
    modal.classList.remove("open");
    document.body.style.overflow = "";
  };

  // ---- events ----
  sceneFilters.addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    document.querySelectorAll("#sceneFilters .chip").forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");
    currentScene = chip.dataset.scene;
    renderSample();
  });

  shuffleBtn.addEventListener("click", renderSample);

  modalClose.addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });

  // Spin toggle + drag-to-rotate
  let dragAngle = 0;
  modalSpin.addEventListener("click", () => {
    const isOn = modalMv.hasAttribute("auto-rotate");
    if (isOn) {
      modalMv.removeAttribute("auto-rotate");
      modalSpin.textContent = "▶ Resume rotation";
    } else {
      modalMv.setAttribute("auto-rotate", "");
      modalSpin.textContent = "⏸ Pause rotation";
    }
  });

  modalCopy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(modalCode.textContent || "");
      const orig = modalCopy.textContent;
      modalCopy.textContent = "Copied!";
      setTimeout(() => (modalCopy.textContent = orig), 1400);
    } catch {
      modalCopy.textContent = "Copy failed";
    }
  });

  // ---- 3D card factory with image fallback if mesh missing ----
  const make3DCard = (scene, category, idx, rps = "20deg") => {
    const mv = document.createElement("model-viewer");
    mv.setAttribute("src", meshUrl(scene, category, idx));
    mv.setAttribute("alt", `${category} ${idx}`);
    mv.setAttribute("auto-rotate", "");
    mv.setAttribute("auto-rotate-delay", "0");
    mv.setAttribute("rotation-per-second", rps);
    mv.setAttribute("interaction-prompt", "none");
    mv.setAttribute("disable-zoom", "");
    mv.setAttribute("disable-pan", "");
    mv.setAttribute("disable-tap", "");
    mv.setAttribute("shadow-intensity", "0.3");
    mv.setAttribute("environment-image", "neutral");
    mv.setAttribute("reveal", "auto");
    mv.setAttribute("loading", "lazy");
    mv.addEventListener("error", () => {
      const img = document.createElement("img");
      img.loading = "lazy";
      img.alt = `${category} ${idx}`;
      img.src = imageUrl(scene, category, idx);
      mv.replaceWith(img);
    });
    return mv;
  };

  // ---- marquee (infinite rotating two-row gallery) ----
  const buildMarquee = () => {
    const top = document.getElementById("marqueeTop");
    const bot = document.getElementById("marqueeBot");
    if (!top || !bot) return;

    // Show every category. Skip categories that have no generated meshes.
    // For each category pick the first variant that isn't on the broken list.
    const pickFor = (scene, category) => {
      for (let i = 1; i <= N; i++) if (!isBroken(scene, category, i)) return i;
      return null;
    };
    const picks = [];
    DATA.indoor.forEach((c) => {
      const idx = pickFor("indoor", c);
      if (idx) picks.push({ scene: "indoor", category: c, idx });
    });
    DATA.outdoor.forEach((c) => {
      const idx = pickFor("outdoor", c);
      if (idx) picks.push({ scene: "outdoor", category: c, idx });
    });

    // Interleave so indoor & outdoor are mixed across rows
    const shuffled = picks.slice().sort((a, b) => (a.category + a.scene).localeCompare(b.category + b.scene));
    const rowA = shuffled.filter((_, i) => i % 2 === 0);
    const rowB = shuffled.filter((_, i) => i % 2 === 1);

    const card = ({ scene, category, idx }) => {
      const el = document.createElement("div");
      el.className = "m-card";
      el.title = `${titleCase(category)} — open variant`;
      el.appendChild(make3DCard(scene, category, idx, "20deg"));
      const label = document.createElement("span");
      label.className = "label";
      label.textContent = titleCase(category);
      el.appendChild(label);
      el.addEventListener("click", () => openVariant(scene, category, idx));
      return el;
    };

    // Duplicate the list for a seamless loop (CSS animates 0 → -50%).
    const fill = (track, list) => {
      const frag = document.createDocumentFragment();
      [...list, ...list].forEach((p) => frag.appendChild(card(p)));
      track.appendChild(frag);
    };
    fill(top, rowA);
    fill(bot, rowB);
  };

  // ---- video presence check (replaces placeholder if asset exists) ----
  const tryLoadVideo = async () => {
    const card = document.getElementById("videoCard");
    if (!card) return;
    const youTube = card.dataset.video;
    if (youTube) {
      const idMatch = youTube.match(/(?:v=|youtu\.be\/|embed\/)([\w-]{6,})/);
      const id = idMatch ? idMatch[1] : null;
      if (id) {
        card.innerHTML = `<iframe src="https://www.youtube.com/embed/${id}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
        return;
      }
    }
    // Try local mp4
    try {
      const r = await fetch("assets/demo.mp4", { method: "HEAD" });
      if (r.ok) {
        card.innerHTML = `<video controls preload="metadata" poster=""><source src="assets/demo.mp4" type="video/mp4"></video>`;
      }
    } catch { /* keep placeholder */ }
  };

  // ---- paper fallback (used by iframe onerror) ----
  window.paperFallbackHTML = () => `
    <div class="pp-fallback">
      <p>The embedded reader couldn't load the PDF inline.</p>
      <p><a href="https://arxiv.org/pdf/2605.00632" target="_blank" rel="noopener">Download the paper from arXiv ↗</a></p>
    </div>
  `;

  // initial render
  renderSample();
  buildMarquee();
  tryLoadVideo();
})();
