(() => {
  "use strict";

  const content = window.OG_GAUSSIAN_CONTENT || {};
  const viewer = document.getElementById("image-viewer");
  const viewerImage = document.getElementById("viewer-image");
  const viewerCaption = document.getElementById("viewer-caption");
  let imageTrigger = null;
  const videoObserver = "IntersectionObserver" in window
    ? new IntersectionObserver((entries) => {
        entries.forEach(({ target, isIntersecting }) => {
          if (!isIntersecting) target.pause();
        });
      }, { threshold: 0 })
    : null;

  function mediaUrl(value) {
    if (typeof value !== "string" || !value.trim()) return "";
    // The standalone export embeds only these image and video formats.
    const embedded = value.trim();
    if (/^data:(?:image\/(?:png|jpeg|webp|svg\+xml)|video\/(?:mp4|webm));base64,/i.test(embedded)) return embedded;
    try {
      const url = new URL(value.trim(), document.baseURI);
      return ["http:", "https:", "file:"].includes(url.protocol) ? url.href : "";
    } catch {
      return "";
    }
  }

  function icon(kind) {
    const icons = {
      image: '<rect x="3" y="4" width="26" height="24" rx="2"/><circle cx="11" cy="12" r="2.5"/><path d="m4 24 8-8 5 5 4-4 8 8"/>',
      video: '<rect x="3" y="5" width="26" height="22" rx="2"/><path d="m13 11 9 5-9 5z"/>',
      zoom: '<circle cx="13" cy="13" r="8"/><path d="m19 19 8 8M9 13h8m-4-4v8"/>'
    };
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 32 32");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "1.4");
    svg.setAttribute("aria-hidden", "true");
    svg.innerHTML = icons[kind] || icons.image;
    return svg;
  }

  function placeholder(slot, title, type, failed = false) {
    slot.replaceChildren();
    slot.classList.remove("has-media");
    slot.classList.add("is-empty");
    slot.dataset.state = failed ? "unavailable" : "pending";
    const box = document.createElement("div");
    box.className = "media-placeholder";
    const symbol = icon(type);
    symbol.classList.add("placeholder-icon");
    const label = document.createElement("span");
    label.className = "placeholder-label";
    label.textContent = title;
    const note = document.createElement("span");
    note.className = "placeholder-note";
    note.textContent = failed ? "Media unavailable" : (type === "video" ? "Video forthcoming" : "Figure forthcoming");
    box.append(symbol, label, note);
    slot.append(box);
  }

  function openImage(media, title, caption, trigger) {
    viewerImage.src = mediaUrl(media.fullsize) || mediaUrl(media.src);
    viewerImage.alt = media.alt || title;
    setCaption(viewerCaption, caption);
    imageTrigger = trigger;
    viewer.showModal();
    document.body.classList.add("viewer-open");
  }

  function renderMedia(slot, media, title, caption = "") {
    const type = media?.type === "video" ? "video" : "image";
    const src = mediaUrl(media?.src);
    if (!src) {
      placeholder(slot, title, type);
      return;
    }

    slot.replaceChildren();
    slot.classList.remove("is-empty");
    slot.classList.add("has-media");
    slot.classList.toggle("video-slot", type === "video");
    slot.dataset.state = "ready";

    if (type === "video") {
      const video = document.createElement("video");
      video.controls = true;
      video.playsInline = true;
      video.muted = true;
      video.loop = media.loop !== false;
      video.preload = "metadata";
      video.setAttribute("aria-label", title);
      const poster = mediaUrl(media.poster);
      if (poster) video.poster = poster;
      video.addEventListener("error", () => {
        videoObserver?.unobserve(video);
        placeholder(slot, title, type, true);
      }, { once: true });
      slot.append(video);
      video.src = src;
      videoObserver?.observe(video);
      return;
    }

    const button = document.createElement("button");
    button.type = "button";
    button.className = "image-trigger";
    button.setAttribute("aria-label", "Enlarge " + title);
    const img = document.createElement("img");
    img.alt = media.alt || title;
    img.loading = "lazy";
    img.decoding = "async";
    img.addEventListener("error", () => placeholder(slot, title, type, true), { once: true });
    button.append(img);
    // Native dialog provides keyboard dismissal and focus containment.
    if (typeof viewer?.showModal === "function") {
      const hint = document.createElement("span");
      hint.className = "zoom-hint";
      hint.setAttribute("aria-hidden", "true");
      hint.append(icon("zoom"));
      button.append(hint);
      button.addEventListener("click", () => openImage(media, title, caption, button));
      slot.append(button);
    } else {
      slot.append(img);
    }
    img.src = src;
  }

  function setCaption(element, text) {
    element.replaceChildren();
    const parts = Array.isArray(text) ? text : [{ text: text || "" }];
    parts.forEach((part) => {
      const span = document.createElement("span");
      span.textContent = part.text || "";
      if (["initial", "goal"].includes(part.tone)) {
        span.className = "state-color state-color--" + part.tone;
      }
      element.append(span);
    });
    element.hidden = !element.textContent;
  }

  function renderGallery(root, items, prefix, type, slotClass) {
    if (!root || !Array.isArray(items) || !items.length) return;
    root.replaceChildren();
    const tablist = document.createElement("div");
    tablist.className = "task-tabs";
    tablist.setAttribute("role", "tablist");
    tablist.setAttribute("aria-label", root.getAttribute("aria-label"));
    const buttons = [];
    const panels = [];
    const mediaItems = items.map((item) => Array.isArray(item.media) ? item.media : [item.media]);

    function activate(index, focus = false) {
      buttons.forEach((button, i) => {
        const active = i === index;
        button.setAttribute("aria-selected", String(active));
        button.tabIndex = active ? 0 : -1;
        panels[i].hidden = !active;
        if (!active) panels[i].querySelectorAll("video").forEach((video) => video.pause());
      });
      const panel = panels[index];
      if (!panel.dataset.initialized) {
        const item = items[index];
        panel.querySelectorAll(".media-slot").forEach((slot, mediaIndex) => {
          const media = mediaItems[index][mediaIndex];
          const title = mediaItems[index].length > 1 ? item.title + " - Execution " + (mediaIndex + 1) : item.title;
          renderMedia(slot, { ...media, type: media?.type || type }, title, item.caption);
        });
        panel.dataset.initialized = "true";
      }
      if (focus) {
        buttons[index].focus();
        buttons[index].scrollIntoView({ block: "nearest", inline: "nearest" });
      }
    }

    items.forEach((item, index) => {
      const id = prefix + "-" + (item.id || index);
      const button = document.createElement("button");
      button.id = id + "-tab";
      button.type = "button";
      button.className = "task-tab";
      button.textContent = item.title;
      button.setAttribute("role", "tab");
      button.setAttribute("aria-controls", id + "-panel");
      button.addEventListener("click", () => activate(index));
      button.addEventListener("keydown", (event) => {
        let next = index;
        if (event.key === "ArrowRight") next = (index + 1) % items.length;
        else if (event.key === "ArrowLeft") next = (index - 1 + items.length) % items.length;
        else if (event.key === "Home") next = 0;
        else if (event.key === "End") next = items.length - 1;
        else return;
        event.preventDefault();
        activate(next, true);
      });

      const panel = document.createElement("div");
      panel.id = id + "-panel";
      panel.className = "task-panel";
      panel.tabIndex = 0;
      panel.setAttribute("role", "tabpanel");
      panel.setAttribute("aria-labelledby", button.id);
      const figure = document.createElement("figure");
      figure.className = "media-figure";
      const mediaContainer = document.createElement("div");
      if (mediaItems[index].length > 1) mediaContainer.className = "media-grid";
      mediaItems[index].forEach(() => {
        const slot = document.createElement("div");
        slot.className = "media-slot " + slotClass;
        mediaContainer.append(slot);
      });
      const caption = document.createElement("figcaption");
      setCaption(caption, item.caption);
      figure.append(mediaContainer, caption);
      panel.append(figure);
      buttons.push(button);
      panels.push(panel);
      tablist.append(button);
    });
    root.append(tablist, ...panels);
    activate(0);
  }

  const codeLink = document.getElementById("code-link");
  if (typeof content.codeUrl === "string" && /^https:\/\//i.test(content.codeUrl.trim())) {
    const url = mediaUrl(content.codeUrl);
    if (url) {
      codeLink.href = url;
      // New tabs inherit Anonymous GitHub's sandbox; navigate in this tab.
      codeLink.target = "_self";
      codeLink.rel = "noopener noreferrer";
      codeLink.removeAttribute("aria-disabled");
      codeLink.removeAttribute("tabindex");
    }
  }

  renderMedia(document.getElementById("method-media"), { ...content.method, type: "image" }, "Method overview");
  renderGallery(document.getElementById("simulation-gallery"), content.simulation, "simulation", "image", "comparison-slot");
  renderGallery(document.getElementById("real-world-gallery"), content.realWorld, "real-world", "video", "video-slot");

  const toys = content.toyCases || {};
  renderMedia(document.getElementById("multiple-references-media"), toys.multipleReferences || { type: "video" }, "Multi-Reference Configuration", toys.multipleReferences?.caption);
  renderMedia(document.getElementById("unseen-tasks-media"), toys.unseenTasks || { type: "video" }, "Unseen Task Configuration", toys.unseenTasks?.caption);
  setCaption(document.getElementById("multiple-references-caption"), toys.multipleReferences?.caption);
  setCaption(document.getElementById("unseen-tasks-caption"), toys.unseenTasks?.caption);

  document.getElementById("viewer-close").addEventListener("click", () => viewer.close());
  viewer.addEventListener("click", (event) => {
    if (event.target !== viewer) return;
    const rect = viewer.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) viewer.close();
  });
  viewer.addEventListener("close", () => {
    document.body.classList.remove("viewer-open");
    viewerImage.removeAttribute("src");
    imageTrigger?.focus();
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) document.querySelectorAll("video").forEach((video) => video.pause());
  });
})();
