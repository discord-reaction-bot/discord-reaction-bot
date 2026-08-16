/* ============================================================
   Discord Reaction Bot — script.js
   Etapa 1: carga site.json, arma navbar/hero/footer,
   maneja menú móvil, scroll suave y revelado al hacer scroll.
   ============================================================ */

(async function () {
  let revealObserver = null;

  const DATA_URL = "./data/site.json";
  const COMMANDS_URL = "./data/commands.json";
  const FUNCTIONS_URL = "./data/functions.json";
  const LEGAL_URL = "./data/legal.json";

  let site;
  try {
    const res = await fetch(DATA_URL);
    if (!res.ok) throw new Error(`No se pudo cargar ${DATA_URL} (${res.status})`);
    site = await res.json();
  } catch (err) {
    console.error("Error cargando site.json:", err);
    return; // el HTML ya trae textos de respaldo, así que la página sigue siendo usable
  }

  let commandsData = [];
  try {
    const res = await fetch(COMMANDS_URL);
    if (!res.ok) throw new Error(`No se pudo cargar ${COMMANDS_URL} (${res.status})`);
    const json = await res.json();
    commandsData = Array.isArray(json.commands) ? json.commands : [];
  } catch (err) {
    console.error("Error cargando commands.json:", err);
    // La sección de comandos queda vacía, pero el resto de la página sigue funcionando.
  }

  let functionsData = [];
  try {
    const res = await fetch(FUNCTIONS_URL);
    if (!res.ok) throw new Error(`No se pudo cargar ${FUNCTIONS_URL} (${res.status})`);
    const json = await res.json();
    functionsData = Array.isArray(json.functions) ? json.functions : [];
  } catch (err) {
    console.error("Error cargando functions.json:", err);
    // La sección de funciones queda vacía, pero el resto de la página sigue funcionando.
  }

  let legalData = {};
  const legalPromise = fetch(LEGAL_URL)
    .then((res) => {
      if (!res.ok) throw new Error(`No se pudo cargar ${LEGAL_URL} (${res.status})`);
      return res.json();
    })
    .then((json) => (legalData = json))
    .catch((err) => {
      console.error("Error cargando legal.json:", err);
      return legalData; // queda {}; el resto de la página sigue funcionando
    });

  await legalPromise;

  populateNav(site);
  populateHero(site);
  populateAbout(site);
  populateFunctions(functionsData);
  populateCommands(commandsData);
  populateLegal(legalData);
  populateFooter(site);

  setupNavToggle();
  setupScrollSpy();
  setupReveal();
  setupNavigation();
  setupLangMenu(site);

  document.getElementById("footer-year").textContent = new Date().getFullYear();

  // ---------------------------------------------------------

  function populateNav(site) {
    const { nav } = site;
    if (!nav) return;

    const logoText = document.getElementById("nav-logo-text");
    if (logoText && nav.logoLabel) logoText.textContent = nav.logoLabel;

    // Imagen de logo configurable — si no carga (o no hay ruta),
    // se mantiene el emoji de respaldo que ya trae el HTML.
    const logoImg = document.getElementById("nav-logo-img");
    const logoFallback = document.getElementById("logo-fallback");
    const logoPath = nav.logoImage || site.site?.logo;
    if (logoImg && logoPath) {
      logoImg.onload = () => {
        logoImg.classList.add("is-loaded");
        if (logoFallback) logoFallback.style.display = "none";
      };
      logoImg.onerror = () => {
        logoImg.classList.remove("is-loaded");
      };
      logoImg.src = logoPath;
      logoImg.alt = nav.logoLabel || site.site?.title || "Logo";
    }

    const list = document.getElementById("nav-links-list");
    if (list && Array.isArray(nav.links)) {
      list.innerHTML = "";
      nav.links.forEach((link) => {
        const li = document.createElement("li");
        li.style.display = "contents";
        const a = document.createElement("a");
        a.href = link.href;
        a.textContent = link.label;
        if (link.variant === "secondary") {
          a.classList.add("nav-link-secondary");
        }
        if (link.type === "external") {
          a.target = "_blank";
          a.rel = "noopener noreferrer";
        }
        li.appendChild(a);
        list.appendChild(li);
      });
    }

    const cta = document.getElementById("nav-cta");
    if (cta && nav.cta) {
      cta.textContent = nav.cta.label;
      cta.href = nav.cta.href;
      cta.target = "_blank";
      cta.rel = "noopener noreferrer";
    }
  }

  function populateHero(site) {
    const { hero } = site;
    if (!hero) return;

    setText("hero-eyebrow", hero.eyebrow);
    setText("hero-title", hero.title);
    setText("hero-tagline", hero.subtitle);
    setText("hero-description", hero.description);

    const primary = document.getElementById("hero-btn-primary");
    if (primary && hero.primaryButton) {
      primary.textContent = hero.primaryButton.label;
      primary.href = hero.primaryButton.href;
      primary.target = "_blank";
      primary.rel = "noopener noreferrer";
    }

    const secondary = document.getElementById("hero-btn-secondary");
    if (secondary && hero.secondaryButton) {
      secondary.textContent = hero.secondaryButton.label;
      secondary.href = hero.secondaryButton.href;
      secondary.target = "_blank";
      secondary.rel = "noopener noreferrer";
    }

    const mascot = document.getElementById("mascot-img");
    if (mascot && hero.mascotImage) {
      mascot.src = hero.mascotImage;
      mascot.alt = hero.mascotAlt || mascot.alt;
    }

    if (Array.isArray(hero.reactionIcons)) {
      hero.reactionIcons.forEach((src, i) => {
        const img = document.getElementById(`reaction-icon-${i + 1}`);
        if (img && src) img.src = src;
      });
    }

    if (site.sections && site.sections.funciones) {
      setText("funciones-eyebrow", site.sections.funciones.eyebrow);
      setText("funciones-title", site.sections.funciones.title);
    }

    if (site.sections && site.sections.comandos) {
      setText("comandos-eyebrow", site.sections.comandos.eyebrow);
      setText("comandos-title", site.sections.comandos.title);
    }

    if (site.sections && site.sections.cta) {
      setText("cta-title", site.sections.cta.title);

      const ctaPrimary = document.getElementById("cta-btn-primary");
      if (ctaPrimary && site.sections.cta.primaryButton) {
        ctaPrimary.textContent = site.sections.cta.primaryButton.label;
        ctaPrimary.href = site.sections.cta.primaryButton.href;
        ctaPrimary.target = "_blank";
        ctaPrimary.rel = "noopener noreferrer";
      }

      const ctaSecondary = document.getElementById("cta-btn-secondary");
      if (ctaSecondary && site.sections.cta.secondaryButton) {
        ctaSecondary.textContent = site.sections.cta.secondaryButton.label;
        ctaSecondary.href = site.sections.cta.secondaryButton.href;
        ctaSecondary.target = "_blank";
        ctaSecondary.rel = "noopener noreferrer";
      }
    }
  }

  function populateAbout(site) {
    const about = site.about;
    if (!about) return;

    setText("about-eyebrow", about.eyebrow);
    setText("about-title", about.title);
    setText("about-lead", about.lead);

    const list = document.getElementById("about-highlights");
    if (list && Array.isArray(about.highlights)) {
      list.innerHTML = "";
      about.highlights.forEach((item) => {
        const li = document.createElement("li");
        li.className = "reveal";

        const icon = document.createElement("span");
        icon.className = "highlight-icon";

        const iconImg = document.createElement("img");
        iconImg.src = item.icon || "assets/images/test.png";
        iconImg.alt = "";
        icon.appendChild(iconImg);

        const text = document.createElement("span");
        text.className = "highlight-text";
        text.textContent = item.text || "";

        li.appendChild(icon);
        li.appendChild(text);
        list.appendChild(li);
      });
    }
  }

  function populateFunctions(functions) {
    const grid = document.getElementById("functions-grid");
    if (!grid || !Array.isArray(functions) || !functions.length) return;

    grid.innerHTML = "";
    functions.forEach((fn) => {
      const item = document.createElement("div");
      item.className = "function-item reveal";

      const icon = document.createElement("span");
      icon.className = "function-icon";

      const iconImg = document.createElement("img");
      iconImg.src = fn.icon || "assets/images/test.png";
      iconImg.alt = "";
      icon.appendChild(iconImg);

      const title = document.createElement("h3");
      title.className = "function-title";
      title.textContent = fn.title || "";

      const desc = document.createElement("p");
      desc.className = "function-desc";
      desc.textContent = fn.description || "";

      item.appendChild(icon);
      item.appendChild(title);
      item.appendChild(desc);
      grid.appendChild(item);
    });
  }

  function populateCommands(commands) {
    const list = document.getElementById("commands-list");
    if (!list || !Array.isArray(commands) || !commands.length) return;

    list.innerHTML = "";
    commands.forEach((cmd) => {
      const li = document.createElement("li");
      li.className = "reveal";

      const name = document.createElement("span");
      name.className = "command-name";
      name.textContent = cmd.name || "";

      const desc = document.createElement("span");
      desc.className = "command-desc";
      desc.textContent = cmd.description || "";

      li.appendChild(name);
      li.appendChild(desc);
      list.appendChild(li);
    });
  }

  function populateLegal(legal) {
    renderLegalDoc("privacidad", legal?.privacidad);
    renderLegalDoc("terminos", legal?.terminos);
  }

  function renderLegalDoc(id, doc) {
    if (!doc) return;

    setText(`${id}-title`, doc.title);
    setText(`${id}-intro`, doc.intro);

    const container = document.getElementById(`${id}-sections`);
    if (!container || !Array.isArray(doc.sections)) return;

    container.innerHTML = "";
    doc.sections.forEach((section, i) => {
      const block = document.createElement("article");
      block.className = "legal-block reveal";

      const number = document.createElement("span");
      number.className = "legal-block-number";
      number.textContent = String(i + 1).padStart(2, "0");

      const heading = document.createElement("h3");
      heading.textContent = section.heading || "";

      const body = document.createElement("p");
      body.textContent = section.body || "";

      block.appendChild(number);
      block.appendChild(heading);
      block.appendChild(body);
      container.appendChild(block);
    });
  }

  // Se llama justo antes de mostrar #privacidad o #terminos. Si
  // legal.json ya se renderizó (caso normal), no hace nada. Si por
  // alguna razón el contenido todavía no está en el DOM (por ejemplo,
  // la carga tardó más de lo esperado), espera a que legalPromise
  // resuelva y recién ahí renderiza — así nunca se muestra la vista
  // legal vacía.
  async function ensureLegalRendered(id) {
    const container = document.getElementById(`${id}-sections`);
    if (container && container.children.length > 0) return;

    const data = legalData && Object.keys(legalData).length ? legalData : await legalPromise;
    renderLegalDoc(id, data && data[id]);

    // Este renderizado ocurre después de setupReveal(), así que los
    // bloques nuevos no fueron detectados por su querySelectorAll
    // inicial — hay que sumarlos al observer a mano.
    const freshContainer = document.getElementById(`${id}-sections`);
    if (freshContainer) observeReveal(freshContainer.querySelectorAll(".reveal"));
  }

  function populateFooter(site) {
    const { footer } = site;
    if (!footer) return;

    setText("footer-brand", footer.brand);
    setText("footer-tagline", footer.tagline);

    const list = document.getElementById("footer-links");
    if (list && Array.isArray(footer.links)) {
      list.innerHTML = "";
      footer.links.forEach((link) => {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = link.href;
        a.textContent = link.label;
        if (link.external) {
          a.target = "_blank";
          a.rel = "noopener noreferrer";
        }
        li.appendChild(a);
        list.appendChild(li);
      });
    }
  }

  function setText(id, value) {
    if (!value) return;
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  // ---------------------------------------------------------

  function setupNavToggle() {
    const toggle = document.getElementById("nav-toggle");
    const links = document.getElementById("nav-links");
    const backdrop = document.getElementById("nav-backdrop");
    if (!toggle || !links) return;

    const openMenu = () => {
      links.classList.add("is-open");
      backdrop?.classList.add("is-open");
      toggle.setAttribute("aria-expanded", "true");
      toggle.setAttribute("aria-label", "Cerrar menú");
      document.body.classList.add("nav-open");
    };

    const closeMenu = () => {
      links.classList.remove("is-open");
      backdrop?.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Abrir menú");
      document.body.classList.remove("nav-open");
    };

    toggle.addEventListener("click", () => {
      const isOpen = links.classList.contains("is-open");
      isOpen ? closeMenu() : openMenu();
    });

    backdrop?.addEventListener("click", closeMenu);

    links.querySelectorAll("a").forEach((a) => {
      a.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && links.classList.contains("is-open")) {
        closeMenu();
        toggle.focus();
      }
    });

    // Si la ventana crece más allá del punto de quiebre móvil,
    // asegura que el menú no quede abierto por error.
    window.addEventListener("resize", () => {
      if (window.innerWidth > 760 && links.classList.contains("is-open")) {
        closeMenu();
      }
    });
  }

  function setupScrollSpy() {
    const navbar = document.getElementById("navbar");
    if (!navbar) return;
    const onScroll = () => {
      navbar.classList.toggle("is-scrolled", window.scrollY > 24);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  function setupNavigation() {
    const navHeight = document.getElementById("navbar")?.offsetHeight || 76;
    const viewMain = document.getElementById("view-main");
    const viewLegal = document.getElementById("view-legal");

    function isLegalId(id) {
      return id === "privacidad" || id === "terminos";
    }

    // Muestra la vista principal o la vista legal según el hash.
    // Si corresponde a una página legal, primero garantiza que su
    // contenido ya esté renderizado (ver ensureLegalRendered) para
    // que nunca se vea la vista legal vacía. Devuelve true si quedó
    // activa la vista legal.
    async function applyView(id) {
      if (!viewMain || !viewLegal) return false;
      const legal = isLegalId(id);

      if (legal) {
        await ensureLegalRendered(id);
        activateLegalSection(id);
        revealLegalSection(id);
      }

      viewMain.classList.toggle("is-hidden", legal);
      viewLegal.classList.toggle("is-hidden", !legal);
      return legal;
    }

    // Antes, cuál de las dos secciones legales se mostraba (privacidad
    // vs. términos) lo decidía el CSS con :target. Pero la navegación
    // acá se hace con history.pushState (para no recargar la página),
    // y pushState no dispara :target de forma confiable. Por eso ahora
    // el propio JS activa la sección correcta a mano con esta clase,
    // y desactiva cualquier otra sección legal que haya quedado activa.
    function activateLegalSection(id) {
      viewLegal.querySelectorAll(".legal-page").forEach((section) => {
        section.classList.toggle("is-active", section.id === id);
      });
    }

    // La vista legal aparece de golpe (no con scroll), así que sus
    // bloques .reveal se marcan visibles directamente en vez de
    // esperar al IntersectionObserver: mientras #view-legal tenía
    // display:none, el observer nunca pudo detectarlos como
    // "en pantalla", y quedaban con opacity:0 para siempre aunque
    // después se les quitara el display:none.
    function revealLegalSection(id) {
      const section = document.getElementById(id);
      if (!section) return;
      section.querySelectorAll(".reveal").forEach((el) => {
        el.classList.add("is-visible");
        if (revealObserver) revealObserver.unobserve(el);
      });
    }

    function scrollToId(id) {
      const target = document.getElementById(id);
      if (!target) return;
      const top = target.getBoundingClientRect().top + window.scrollY - navHeight + 1;
      window.scrollTo({ top, behavior: "smooth" });
    }

    // Estado inicial: si la URL ya trae #privacidad o #terminos
    // (por ejemplo, alguien entra con un link compartido), arrancamos
    // directamente en esa vista en lugar de mostrar la landing.
    applyView(window.location.hash.slice(1));

    document.querySelectorAll('a[href^="#"]').forEach((link) => {
      link.addEventListener("click", async (e) => {
        const id = link.getAttribute("href").slice(1);
        const target = document.getElementById(id);
        if (!target) return;

        e.preventDefault();
        history.pushState(null, "", `#${id}`);

        const legal = await applyView(id);
        if (legal) {
          // Página legal: arranca siempre desde arriba, como una pantalla nueva.
          window.scrollTo({ top: 0, behavior: "auto" });
        } else {
          scrollToId(id);
        }
      });
    });

    // Cubre los botones de atrás/adelante del navegador.
    window.addEventListener("hashchange", async () => {
      const id = window.location.hash.slice(1);
      const legal = await applyView(id);
      if (legal) window.scrollTo({ top: 0, behavior: "auto" });
    });
  }

  function setupReveal() {
    const items = document.querySelectorAll(".reveal");
    if (!items.length) return;

    if (!("IntersectionObserver" in window)) {
      items.forEach((el) => el.classList.add("is-visible"));
      return;
    }

    revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );

    items.forEach((el) => revealObserver.observe(el));
  }

  // Suma elementos .reveal creados después del arranque (por ejemplo,
  // si el contenido legal se termina de renderizar tras un cambio de
  // hash) al mismo observer, o los muestra directo si no hay soporte.
  function observeReveal(elements) {
    elements.forEach((el) => {
      if (el.classList.contains("is-visible")) return;
      if (revealObserver) {
        revealObserver.observe(el);
      } else {
        el.classList.add("is-visible");
      }
    });
  }

  function setupLangMenu(site) {
    const current = document.getElementById("lang-current");
    const menu = document.getElementById("lang-menu");
    const langs = site?.footer?.languages;
    if (!current || !menu || !Array.isArray(langs) || !langs.length) return;

    menu.innerHTML = "";
    langs.forEach((lang) => {
      const btn = document.createElement("button");
      btn.textContent = lang.label;
      btn.dataset.lang = lang.code;
      btn.addEventListener("click", () => {
        current.textContent = lang.label;
        localStorage.setItem("preferredLang", lang.code);
        menu.classList.remove("is-open");
        current.setAttribute("aria-expanded", "false");
        // La lógica real de cambio de idioma se añadirá cuando
        // existan varios idiomas en site.json.
      });
      menu.appendChild(btn);
    });

    const saved = localStorage.getItem("preferredLang");
    const savedLang = langs.find((l) => l.code === saved) || langs[0];
    if (savedLang) current.textContent = savedLang.label;

    current.addEventListener("click", () => {
      const isOpen = menu.classList.toggle("is-open");
      current.setAttribute("aria-expanded", String(isOpen));
    });

    document.addEventListener("click", (e) => {
      if (!menu.contains(e.target) && e.target !== current) {
        menu.classList.remove("is-open");
        current.setAttribute("aria-expanded", "false");
      }
    });
  }
})();
