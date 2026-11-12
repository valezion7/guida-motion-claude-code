    // parola che entra grigia e sfocata, poi prende il suo colore: il gesto dell'originale
    const W = (sel, times) => document.querySelectorAll(sel).forEach((el, i) => { const fine = getComputedStyle(el).color;
      tl.fromTo(el, { opacity: 0, y: 24, x: 10, filter: "blur(10px)", color: "#b9b3ab" }, { opacity: 1, y: 0, x: 0, filter: "blur(0px)", duration: 0.3, ease: "power3.out" }, times[i]);
      tl.to(el, { color: fine, duration: 0.35, ease: "power1.out" }, times[i] + 0.2);
    });
    // parola grande: arriva da vicino e si mette a fuoco
    const G = (sel, times) => document.querySelectorAll(sel).forEach((el, i) =>
      tl.fromTo(el, { opacity: 0, scale: 1.5, filter: "blur(14px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.28, ease: "power4.out" }, times[i]));
    // targhetta nera che si stende da sinistra
    const TAG = (sel, t) => { tl.fromTo(sel, { clipPath: "inset(0% 100% 0% 0% round 20px)", rotation: -3 }, { clipPath: "inset(0% 0% 0% 0% round 20px)", rotation: 0, duration: 0.42, ease: "expo.out" }, t);
      tl.fromTo(sel + " .w", { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.35, stagger: 0.06, ease: "power3.out" }, t + 0.06); };
    // oggetto 3D: vola dentro e poi galleggia
    const P = (sel, t, da, giri, bob) => { tl.fromTo(sel, { opacity: 0, scale: 0.35, x: da[0], y: da[1], rotation: da[2] }, { opacity: 1, scale: 1, x: 0, y: 0, rotation: 0, duration: 0.7, ease: "back.out(1.6)" }, t);
      tl.to(sel, { y: bob, rotation: bob / 4, duration: 1.5, ease: "sine.inOut", yoyo: true, repeat: giri }, t + 0.7); };
    // scheda: si raddrizza in 3D, poi scivola piano
    const CARD = (sel, t, d) => { tl.fromTo(sel, { opacity: 0, y: 260, rotationX: 38, scale: 0.9, transformPerspective: 1400 }, { opacity: 1, y: 0, rotationX: 0, scale: 1, duration: 0.8, ease: "expo.out" }, t);
      tl.to(sel, { rotationY: -5, rotationX: 3, scale: 1.035, y: -14, duration: Math.max(0.5, d - 0.8), ease: "sine.inOut" }, t + 0.8); };
    const L = (sel, t) => { tl.fromTo(sel, { opacity: 0, x: -44, filter: "blur(8px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.34, ease: "power3.out" }, t);
      tl.fromTo(sel + " .segno", { scale: 0, rotation: -120 }, { scale: 1, rotation: 0, duration: 0.42, ease: "back.out(2.4)" }, t); };
    const LAMPO = (t) => { if (t < 0.2) return; tl.fromTo("#lampo", { opacity: 0 }, { opacity: 0.85, duration: 0.07, ease: "none" }, t - 0.07); tl.to("#lampo", { opacity: 0, duration: 0.3, ease: "power2.out" }, t); };

    // versione spinta: gli oggetti entrano avvitandosi e poi dondolano in 3D
    const P3 = (sel, t, da, giri, bob) => { tl.fromTo(sel, { opacity: 0, scale: 0.1, x: da[0] * 1.6, y: da[1] * 1.6, rotationY: 540, rotation: da[2] * 2, transformPerspective: 1000 }, { opacity: 1, scale: 1, x: 0, y: 0, rotationY: 0, rotation: 0, duration: 0.9, ease: "back.out(2.2)" }, t);
      tl.to(sel, { y: bob * 1.8, rotation: bob / 2, rotationY: bob * 1.7, scale: 1.08, duration: 1.1, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.round(giri * 1.4)) }, t + 0.9); };
    // parola grande che si alza ribaltandosi
    const G3 = (sel, times) => document.querySelectorAll(sel).forEach((el, i) =>
      tl.fromTo(el, { opacity: 0, rotationX: -95, y: 70, scale: 1.25, transformPerspective: 700, transformOrigin: "50% 100%", filter: "blur(12px)" }, { opacity: 1, rotationX: 0, y: 0, scale: 1, filter: "blur(0px)", duration: 0.34, ease: "back.out(2.4)" }, times[i]));
    // la «camera»: ogni quadro avanza e ruota piano nello spazio
    const CAM = (sel, t, d, k) => tl.fromTo(sel, { scale: 0.93, rotationY: k % 2 ? 7 : -7, rotationX: 3, transformPerspective: 1500 }, { scale: 1.06, rotationY: k % 2 ? -5 : 5, rotationX: -2, duration: d, ease: "sine.inOut" }, t);
    const SW = (sel, t, d, dx, dy, r) => { tl.fromTo(sel, { opacity: 0, scale: 0.3 }, { opacity: 0.5, scale: 1, duration: 0.6, ease: "back.out(1.6)" }, t);
      tl.fromTo(sel, { x: 0, y: 0, rotation: 0 }, { x: dx, y: dy, rotation: r, duration: d, ease: "none" }, t); };
