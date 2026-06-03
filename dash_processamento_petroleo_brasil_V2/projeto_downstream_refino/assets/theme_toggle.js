/**
 * theme_toggle.js
 * ---------------
 * Gerencia o toggle de tema Claro ↔ Escuro do dashboard DOCHMO.
 *
 * Estratégia: CSS puro via atributo `data-theme="dark"` no elemento <html>.
 * Zero callbacks Python — troca instantânea e sem round-trip ao servidor.
 * Preferência persistida no localStorage do navegador.
 */

(function () {
  "use strict";

  /* ------------------------------------------------------------------ */
  /* CONSTANTES                                                           */
  /* ------------------------------------------------------------------ */
  var STORAGE_KEY = "dochmo-theme";
  var DARK        = "dark";

  /* ------------------------------------------------------------------ */
  /* APLICAR TEMA (adiciona/remove data-theme no <html>)                 */
  /* ------------------------------------------------------------------ */
  function aplicarTema(tema) {
    if (tema === DARK) {
      document.documentElement.setAttribute("data-theme", DARK);
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  }

  /* ------------------------------------------------------------------ */
  /* CRIAR O SWITCH PILL ANIMADO                                          */
  /* ------------------------------------------------------------------ */
  function criarSwitch() {
    /*
     * Estrutura injetada:
     *
     * <div class="theme-toggle-wrapper">
     *   <span class="theme-toggle-sun">☀️</span>
     *   <button class="theme-toggle-track" aria-label="Alternar tema">
     *     <span class="theme-toggle-thumb"></span>
     *   </button>
     *   <span class="theme-toggle-moon">🌙</span>
     * </div>
     */
    var wrapper = document.createElement("div");
    wrapper.className = "theme-toggle-wrapper";

    var sun = document.createElement("span");
    sun.className = "theme-toggle-sun";
    sun.textContent = "☀️";

    var track = document.createElement("button");
    track.className = "theme-toggle-track";
    track.setAttribute("aria-label", "Alternar tema claro/escuro");
    track.setAttribute("title", "Alternar tema");

    var thumb = document.createElement("span");
    thumb.className = "theme-toggle-thumb";

    track.appendChild(thumb);

    var moon = document.createElement("span");
    moon.className = "theme-toggle-moon";
    moon.textContent = "🌙";

    wrapper.appendChild(sun);
    wrapper.appendChild(track);
    wrapper.appendChild(moon);

    /* ---- Evento de clique ---- */
    track.addEventListener("click", function () {
      var atual = document.documentElement.getAttribute("data-theme");
      var novo  = atual === DARK ? "light" : DARK;
      aplicarTema(novo);
      localStorage.setItem(STORAGE_KEY, novo);
      track.setAttribute("aria-pressed", novo === DARK ? "true" : "false");
    });

    return wrapper;
  }

  /* ------------------------------------------------------------------ */
  /* INJETAR NO DOM — aguarda Dash renderizar a sidebar                  */
  /* ------------------------------------------------------------------ */
  function injetarSwitch() {
    /* O Dash pode levar alguns ms para montar o layout no React.
     * Usamos MutationObserver para detectar quando .sidebar-accent-line
     * aparece no DOM e só então injetamos o switch. */

    var observer = new MutationObserver(function (mutations, obs) {
      var accentLine = document.querySelector(".sidebar-accent-line");
      if (!accentLine) return;

      /* Evita dupla injeção em hot-reload */
      if (document.querySelector(".theme-toggle-wrapper")) return;

      var sw = criarSwitch();

      /* Insere o switch APÓS a accent-line e ANTES do logo */
      accentLine.parentNode.insertBefore(sw, accentLine.nextSibling);

      /* Aplica estado inicial do aria-pressed */
      var temaAtual = document.documentElement.getAttribute("data-theme");
      var track = sw.querySelector(".theme-toggle-track");
      track.setAttribute("aria-pressed", temaAtual === DARK ? "true" : "false");

      obs.disconnect(); /* Para de observar após injetar */
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  /* ------------------------------------------------------------------ */
  /* INICIALIZAÇÃO                                                        */
  /* ------------------------------------------------------------------ */
  function init() {
    /* 1. Restaura preferência salva */
    var temaSalvo = localStorage.getItem(STORAGE_KEY) || "light";
    aplicarTema(temaSalvo);

    /* 2. Injeta o switch quando o Dash terminar de renderizar */
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", injetarSwitch);
    } else {
      injetarSwitch();
    }
  }

  init();
})();
