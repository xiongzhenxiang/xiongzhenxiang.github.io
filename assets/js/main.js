"use strict";

(function () {
    const root = document.documentElement;
    root.classList.add("js");
    const toggle = document.querySelector(".theme-toggle");
    const themeColor = document.querySelector('meta[name="theme-color"]');
    const storedTheme = localStorage.getItem("theme");
    const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

    function applyTheme(theme) {
        const isDark = theme === "dark";
        root.dataset.theme = theme;
        toggle.setAttribute("aria-pressed", String(isDark));
        toggle.setAttribute("aria-label", isDark ? "切换浅色模式" : "切换深色模式");
        themeColor.setAttribute("content", isDark ? "#101319" : "#f7f8f3");
    }

    applyTheme(storedTheme || (systemPrefersDark ? "dark" : "light"));

    toggle.addEventListener("click", function () {
        const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
        localStorage.setItem("theme", nextTheme);
        applyTheme(nextTheme);
    });

    document.querySelector("#current-year").textContent = new Date().getFullYear();

    const revealElements = document.querySelectorAll(".reveal");
    if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    const delay = entry.target.dataset.delay || 0;
                    entry.target.style.transitionDelay = delay + "ms";
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });

        revealElements.forEach(function (element) { observer.observe(element); });
    } else {
        revealElements.forEach(function (element) { element.classList.add("is-visible"); });
    }

    const navLinks = document.querySelectorAll(".site-nav a");
    const sections = document.querySelectorAll("main section[id]");
    const navObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                navLinks.forEach(function (link) {
                    link.classList.toggle("active", link.getAttribute("href") === "#" + entry.target.id);
                });
            }
        });
    }, { rootMargin: "-35% 0px -60% 0px" });

    sections.forEach(function (section) { navObserver.observe(section); });

    const gameHero = document.querySelector(".game-hero");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (gameHero && !reduceMotion && window.matchMedia("(pointer: fine)").matches) {
        gameHero.addEventListener("pointermove", function (event) {
            const rect = gameHero.getBoundingClientRect();
            const x = (event.clientX - rect.left) / rect.width - 0.5;
            const y = (event.clientY - rect.top) / rect.height - 0.5;
            gameHero.style.setProperty("--world-x", (x * -18).toFixed(1) + "px");
            gameHero.style.setProperty("--world-y", (y * -10).toFixed(1) + "px");
            gameHero.style.setProperty("--player-x", (x * 12).toFixed(1) + "px");
            gameHero.style.setProperty("--player-y", (y * 7).toFixed(1) + "px");
        });

        gameHero.addEventListener("pointerleave", function () {
            gameHero.style.setProperty("--world-x", "0px");
            gameHero.style.setProperty("--world-y", "0px");
            gameHero.style.setProperty("--player-x", "0px");
            gameHero.style.setProperty("--player-y", "0px");
        });
    }
}());
