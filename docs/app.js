(() => {
  const HF = window.HF_BASE;
  const DATA = window.DATASET;
  const N = window.VARIANTS_PER_CATEGORY;

  const catGrid = document.getElementById("catGrid");
  const explorerView = document.getElementById("explorerView");
  const sceneFilters = document.getElementById("sceneFilters");
  const searchInput = document.getElementById("searchInput");

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
  let currentSearch = "";
  let openCategory = null; // {scene, category}

  // ---- helpers ----
  const titleCase = (s) => s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  const allCategories = () => {
    const list = [];
    for (const cat of DATA.indoor) list.push({ scene: "indoor", category: cat });
    for (const cat of DATA.outdoor) list.push({ scene: "outdoor", category: cat });
    return list;
  };

  const filtered = () => {
    return allCategories().filter((c) => {
      if (currentScene !== "all" && c.scene !== currentScene) return false;
      if (currentSearch && !c.category.toLowerCase().includes(currentSearch)) return false;
      return true;
    });
  };

  // ---- views ----
  const renderCategoryGrid = () => {
    openCategory = null;
    const items = filtered();
    explorerView.innerHTML = "";
    const grid = document.createElement("div");
    grid.className = "cat-grid";
    if (items.length === 0) {
      explorerView.innerHTML = '<p class="loading">No categories match your filters.</p>';
      return;
    }
    items.forEach(({ scene, category }) => {
      const el = document.createElement("div");
      el.className = "cat";
      el.innerHTML = `
        <span class="name">${titleCase(category)}</span>
        <span class="scene">${scene}</span>
      `;
      el.addEventListener("click", () => openCategoryView(scene, category));
      grid.appendChild(el);
    });
    explorerView.appendChild(grid);
  };

  const openCategoryView = (scene, category) => {
    openCategory = { scene, category };
    explorerView.innerHTML = `
      <div class="cat-header">
        <div>
          <button class="back-btn" id="backBtn">← All categories</button>
          <h3 style="margin:6px 0 0; text-transform:capitalize;">${titleCase(category)} <span style="font-size:13px; color: var(--muted); font-weight:400; text-transform:uppercase; letter-spacing:0.08em; margin-left:8px;">${scene}</span></h3>
        </div>
        <span class="tag">${N} variants</span>
      </div>
      <div class="variant-grid" id="variantGrid"></div>
    `;
    document.getElementById("backBtn").addEventListener("click", renderCategoryGrid);
    const vg = document.getElementById("variantGrid");
    for (let i = 1; i <= N; i++) {
      const v = document.createElement("div");
      v.className = "variant";
      const wrap = document.createElement("div");
      wrap.className = "img-wrap";
      wrap.appendChild(make3DCard(scene, category, i, "25deg"));
      const meta = document.createElement("div");
      meta.className = "meta";
      meta.innerHTML = `<strong>Variant ${i}</strong><span>${scene}</span>`;
      v.appendChild(wrap); v.appendChild(meta);
      v.addEventListener("click", () => openVariant(scene, category, i));
      vg.appendChild(v);
    }
    window.scrollTo({ top: document.getElementById("explorer").offsetTop - 60, behavior: "smooth" });
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
    if (openCategory) renderCategoryGrid(); else renderCategoryGrid();
  });

  searchInput.addEventListener("input", () => {
    currentSearch = searchInput.value.trim().toLowerCase();
    renderCategoryGrid();
  });

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
    const MISSING = new Set(["outdoor/grass"]); // categories where every variant is missing
    const picks = [];
    DATA.indoor.forEach((c, i) => {
      if (MISSING.has(`indoor/${c}`)) return;
      picks.push({ scene: "indoor", category: c, idx: (i % 10) + 1 });
    });
    DATA.outdoor.forEach((c, i) => {
      if (MISSING.has(`outdoor/${c}`)) return;
      picks.push({ scene: "outdoor", category: c, idx: (i % 10) + 1 });
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
  renderCategoryGrid();
  buildMarquee();
  tryLoadVideo();
})();
