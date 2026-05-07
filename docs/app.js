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
  const modalImgWrap = document.getElementById("modalImgWrap");
  const modalSpin = document.getElementById("modalSpin");
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
      const imgUrl = `${HF}/${scene}/${category}/image${i}.png`;
      v.innerHTML = `
        <div class="img-wrap"><img loading="lazy" src="${imgUrl}" alt="${category} ${i}" /></div>
        <div class="meta"><strong>Variant ${i}</strong><span>${scene}</span></div>
      `;
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
    modalTitle.textContent = `${titleCase(category)} — Variant ${idx}`;
    modalDesc.textContent = "Loading description…";
    modalCode.textContent = "Loading code…";
    modalCode.removeAttribute("data-highlighted");
    modalCode.className = "language-python";
    modalImgDl.href = imgUrl;
    modalCodeDl.href = codeUrl;
    modal.classList.add("open");
    document.body.style.overflow = "hidden";
    // restart rotation each time a variant is opened
    modalImgWrap.classList.remove("drag");
    modalImgWrap.classList.add("spinning");
    modalImg.style.transform = "";
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
    const spinning = modalImgWrap.classList.toggle("spinning");
    if (spinning) {
      modalImgWrap.classList.remove("drag");
      modalImg.style.transform = "";
      modalSpin.textContent = "⏸ Pause rotation";
    } else {
      modalImgWrap.classList.add("drag");
      modalImg.style.transform = `rotateY(${dragAngle}deg)`;
      modalSpin.textContent = "▶ Resume rotation";
    }
  });

  // Drag horizontally to rotate when paused
  let dragging = false; let startX = 0; let startAngle = 0;
  const onDown = (e) => {
    if (!modalImgWrap.classList.contains("drag")) return;
    dragging = true;
    startX = (e.touches ? e.touches[0].clientX : e.clientX);
    startAngle = dragAngle;
    e.preventDefault();
  };
  const onMove = (e) => {
    if (!dragging) return;
    const x = (e.touches ? e.touches[0].clientX : e.clientX);
    dragAngle = startAngle + (x - startX) * 0.6;
    modalImg.style.transform = `rotateY(${dragAngle}deg)`;
  };
  const onUp = () => { dragging = false; };
  modalImg.addEventListener("mousedown", onDown);
  modalImg.addEventListener("touchstart", onDown, { passive: false });
  window.addEventListener("mousemove", onMove);
  window.addEventListener("touchmove", onMove, { passive: false });
  window.addEventListener("mouseup", onUp);
  window.addEventListener("touchend", onUp);

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

  // ---- marquee (infinite rotating two-row gallery) ----
  const buildMarquee = () => {
    const top = document.getElementById("marqueeTop");
    const bot = document.getElementById("marqueeBot");
    if (!top || !bot) return;

    // Curated picks across categories for visual variety
    const picks = [];
    const indoorPicks = ["chair", "sofa", "lamp", "bed", "table", "armchair", "wardrobe", "plant", "frame", "rug", "fridge", "candle"];
    const outdoorPicks = ["tree", "fountain", "car", "bench", "gazebo", "cactus", "street_lamp", "stoplight", "rock", "humanoid_statue", "skyscrapers", "bell_tower"];
    indoorPicks.forEach((c, i) => picks.push({ scene: "indoor", category: c, idx: (i % 10) + 1 }));
    outdoorPicks.forEach((c, i) => picks.push({ scene: "outdoor", category: c, idx: (i % 10) + 1 }));

    const half = Math.ceil(picks.length / 2);
    const rowA = picks.slice(0, half);
    const rowB = picks.slice(half).concat(picks.slice(0, 2)); // pad a bit

    const card = ({ scene, category, idx }) => {
      const url = `${HF}/${scene}/${category}/image${idx}.png`;
      const el = document.createElement("div");
      el.className = "m-card";
      el.title = `${titleCase(category)} — open variant`;
      el.innerHTML = `
        <img src="${url}" loading="lazy" alt="${category}" />
        <span class="label">${titleCase(category)}</span>
      `;
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
