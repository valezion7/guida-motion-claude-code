"""Motore della skill short-video: da <progetto>/video.py costruisce il progetto HyperFrames in <progetto>/film.
Uso: python genera.py <cartella-progetto>"""
import json, os, re, shutil, subprocess, sys, unicodedata

def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if c.isalnum())
    return {"cinque": "5", "tre": "3", "quindici": "15", "dieci": "10"}.get(s, s)

class Film:
    def __init__(self, par, wow=1, forme=0):
        self.par, self.wow, self.forme = par, wow, forme
        self.html, self.js, self.n, self.fondo = [], [], 0, 0
    # tempo in cui viene detta ogni parola a schermo, cercandola nel parlato tra t0 e t1
    def tempi(self, parole, t0, t1):
        # margine di 0,3 s all'indietro: se l'àncora del quadro non è la sua prima parola («Una scansione» ancorato a
        # «scansione») la prima parola è detta un attimo prima; senza margine agganciava un «una» più avanti e la riga entrava tardi
        out, last, i0 = [], t0 - 0.3, 0
        cand = [p for p in self.par if t0 - 0.3 <= p["s"] < t1]
        for w in parole:
            k = norm(w); hit = None
            for j in range(i0, len(cand)):
                c = norm(cand[j]["w"])
                if k and (c == k or (len(k) > 3 and c[:4] == k[:4])): hit = j; break
            if hit is not None and cand[hit]["s"] >= last: last = cand[hit]["s"]; i0 = hit + 1
            else: last = last + 0.13
            out.append(round(min(last, t1 - 0.35), 2))
        return out
    def riga(self, sid, k, txt, t0, t1, top, sin=None, larg=940):
        """txt: prefisso s:/m:/g:/tag: + parole; *grassetto* ^arancio^. Ritorna l'altezza occupata."""
        cl = "n"
        m = re.match(r"^(s|m|g|tag):(.*)$", txt)
        if m: cl, txt = m.group(1), m.group(2)
        size = {"s": 54, "n": 64, "m": 104, "g": 156, "tag": 84}[cl]
        nudo = re.sub(r"[*^]", "", txt)
        size = min(size, int(larg / (len(nudo) * (0.50 if cl in "sn" else 0.56))))
        spans, parole, b, o = [], [], False, False
        for tok in re.findall(r"\*|\^|[^\s*^]+", txt):
            if tok == "*": b = not b; continue
            if tok == "^": o = not o; continue
            spans.append(f'<span class="w{" b" if b else ""}{" o" if o else ""}">{tok}</span>'); parole.append(tok)
        rid = f"{sid}r{k}"; tt = self.tempi(parole, t0, t1)
        pos = f"left:{sin}px;width:{larg}px;text-align:left" if sin is not None else "left:0;width:1080px;text-align:center"
        inner = " ".join(spans)
        if cl == "tag": inner = f'<span class="tagbox" id="{rid}b">{inner}</span>'
        self.html.append(f'<div class="riga {cl}" id="{rid}" style="top:{top}px;{pos};font-size:{size}px">{inner}</div>')
        if cl == "tag": self.js.append(f'TAG("#{rid}b",{tt[0]});')
        elif cl in "mg": self.js.append(f'{"G3" if self.wow else "G"}("#{rid} .w",{json.dumps(tt)});')
        else: self.js.append(f'W("#{rid} .w",{json.dumps(tt)});')
        self.fondo = max(self.fondo, top + int(size * 1.2))
        return int(size * (1.24 if cl == "tag" else 1.06 if cl in "mg" else 1.2)) + (22 if cl == "tag" else 8)
    def testo(self, sid, righe, t0, t1, top, **kw):
        for k, r in enumerate(righe): top += self.riga(sid, k, r, t0, t1, top, **kw)
        return top
    def prop(self, sid, k, img, x, y, l, t, dur, da=(0, 160, -30)):
        pid = f"{sid}p{k}"
        dentro = f'<img src="assets/img3d/{img}.png" alt="">'
        self.html.append(f'<div class="prop" id="{pid}" style="left:{x}px;top:{y}px;width:{l}px;height:{l}px">{dentro}</div>')
        self.js.append(f'{"P3" if self.wow else "P"}("#{pid}",{t},{json.dumps(da)},{max(1, int((dur - 0.8) / 1.5))},{16 if k % 2 else -18});')
    def bottone(self, sid, x, y, t):
        self.html.append(f'<div class="bottone" id="{sid}bt" style="left:{x}px;top:{y}px"><div class="stella"></div></div>')
        self.js.append(f'tl.fromTo("#{sid}bt",{{opacity:0,scale:.3}},{{opacity:1,scale:1,duration:.5,ease:"back.out(2)"}},{t});')
    def filo(self, sid, x, y1, y2, t):
        self.html.append(f'<div class="filo" id="{sid}f" style="left:{x - 2}px;top:{y1}px;height:{y2 - y1}px"></div>')
        self.js.append(f'tl.fromTo("#{sid}f",{{scaleY:0}},{{scaleY:1,duration:.45,ease:"power2.out"}},{t});')

    def gag(self, sid, k, g, q, t1):
        """Scenette sopra il quadro, ognuna col suo suono. gag=[("timbro", t, "GRATIS", x, y, rot, colore), ("flash", t),
        ("pioggia", t, "moneta"), ("fluttua", t, "Z z z", x, y), ("conta", t, da, a, "€ ", y)]"""
        tipo, t = g[0], g[1]; gid = f"{sid}x{k}"; S = q.setdefault("suoni", [])
        if tipo == "timbro":
            testo, x, y, rot, col = (list(g[2:]) + [540, 1300, -8, "#ff6a00"][len(g) - 3:])[:5]
            self.html.append(f'<div class="timbro" id="{gid}" style="left:{x}px;top:{y}px;color:{col};border-color:{col}">{testo}</div>')
            self.js.append(f'tl.fromTo("#{gid}",{{xPercent:-50,yPercent:-50,scale:3.4,opacity:0,rotation:{rot - 22}}},{{scale:1,opacity:1,rotation:{rot},duration:.2,ease:"power4.in"}},{t});tl.fromTo("#{sid}in",{{x:0}},{{x:9,duration:.04,yoyo:true,repeat:3}},{round(t + 0.2, 2)});')
            S += [(round(t + 0.17, 2), "timbro")]
            if len(g) > 7: self.js.append(f'tl.to("#{gid}",{{opacity:0,scale:.5,duration:.15}},{g[7]});')  # ottavo valore: quando sparisce
        elif tipo == "flash":
            self.html.append(f'<div class="flashg" id="{gid}"></div>')
            self.js.append(f'tl.fromTo("#{gid}",{{opacity:0}},{{opacity:.95,duration:.05}},{t});tl.to("#{gid}",{{opacity:0,duration:.4,ease:"power2.out"}},{round(t + 0.06, 2)});'); S += [(round(t - 0.05, 2), "scatto")]
        elif tipo == "pioggia":
            for i in range(9):
                x = 60 + (i * 397) % 900; l = 110 + (i * 37) % 70
                self.html.append(f'<div class="prop piov" id="{gid}p{i}" style="left:{x}px;top:-240px;width:{l}px;height:{l}px"><img src="assets/img3d/{g[2]}.png" alt=""></div>')
                self.js.append(f'tl.fromTo("#{gid}p{i}",{{y:0,rotation:{-40 + i * 23}}},{{y:2300,rotation:{200 - i * 55},duration:{1.25 + (i % 3) * 0.18},ease:"power1.in"}},{round(t + i * 0.09, 2)});')
            S += [(round(t + 0.35, 2), "pop"), (round(t + 0.6, 2), "pop"), (round(t + 0.85, 2), "pop"), (round(t + 1.1, 2), "campanella")]
        elif tipo == "fluttua":
            x, y = (list(g[3:]) + [760, 330])[:2]
            for i, ch in enumerate(g[2].split()):
                self.html.append(f'<div class="flut" id="{gid}f{i}" style="left:{x + i * 46}px;top:{y - i * 30}px;font-size:{96 + i * 26}px">{ch}</div>')
                self.js.append(f'tl.fromTo("#{gid}f{i}",{{opacity:0,y:40,scale:.4,rotation:{-14 + i * 12}}},{{opacity:1,y:-60,scale:1,duration:.4,ease:"back.out(2)"}},{round(t + i * 0.24, 2)});tl.to("#{gid}f{i}",{{y:-260,opacity:0,duration:1.1,ease:"power1.in"}},{round(t + i * 0.24 + 0.55, 2)});')
                S += [(round(t + i * 0.24, 2), "pop")]
        elif tipo == "conta":
            da, a, pre, y = (list(g[2:]) + [1330])[:4]
            self.html.append(f'<div class="conta" id="{gid}" style="top:{y}px">{pre}{da}</div>')
            self.js.append(f'(()=>{{const o={{v:{da}}},e=document.querySelector("#{gid}");tl.fromTo("#{gid}",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.3,ease:"back.out(2)"}},{round(t - 0.35, 2)});tl.to(o,{{v:{a},duration:1.1,ease:"power2.inOut",onUpdate:()=>{{e.textContent="{pre}"+Math.round(o.v)}}}},{t});tl.to("#{gid}",{{scale:1.25,color:"#ff6a00",duration:.18,yoyo:true,repeat:1}},{round(t + 1.1, 2)});}})();')
            S += [(round(t + i * 0.13, 2), "tasto") for i in range(8)] + [(round(t + 1.1, 2), "campanella")]

    def quadro(self, q, t1):
        self.n += 1; sid = f"q{self.n}"; t0 = q["t"]; d = round(t1 - t0, 2); tipo = q["tipo"]; R = q.get("righe", [])
        self.html.append(f'<div class="clip sh" id="{sid}" data-start="{t0}" data-duration="{d}" data-layout-allow-overlap data-layout-allow-overflow><div class="cam" id="{sid}cam"><div class="in" id="{sid}in" style="top:@@OFF@@px">')
        segna = len(self.html) - 1; self.fondo = 0
        if self.wow and tipo not in ("segui", "marchio"):
            self.js.append(f'CAM("#{sid}cam",{t0},{d},{self.n});')
            if self.forme:  # raggi arancioni piatti agli angoli, come nel riferimento VRqW0d8-dIU
                if tipo != "titolo" and self.n % 4:
                    for k, (x, y) in enumerate([(-250, -250), (770, 1560)] if self.n % 2 else [(770, -250), (-250, 1560)]):
                        self.html.append(f'<div class="raggi" id="{sid}r{k}x" style="left:{x}px;top:{y}px"></div>')
                        self.js.append(f'tl.fromTo("#{sid}r{k}x",{{scale:0,rotation:{-120 + 240 * k}}},{{scale:1,rotation:0,duration:.6,ease:"back.out(1.7)"}},{round(t0 + 0.05 + 0.1 * k, 2)});tl.to("#{sid}r{k}x",{{rotation:{50 - 100 * k},duration:{d},ease:"none"}},{round(t0 + 0.65 + 0.1 * k, 2)});')
                if q.get("ombra"):  # sagoma grigia gigante dietro il testo
                    self.html.append(f'<div class="raggi ombra" id="{sid}om" style="left:90px;top:430px"></div>')
                    self.js.append(f'tl.fromTo("#{sid}om",{{scale:.2,opacity:0,rotation:-40}},{{scale:1,opacity:1,rotation:0,duration:.7,ease:"expo.out"}},{t0});tl.to("#{sid}om",{{rotation:35,scale:1.12,duration:{d},ease:"none"}},{round(t0 + 0.7, 2)});')
                if q.get("linea"):  # la linea che sale (crescita)
                    self.html.append(f'<div class="linea" id="{sid}li" style="left:60px;top:1380px"></div>')
                    self.js.append(f'tl.fromTo("#{sid}li",{{scaleX:0}},{{scaleX:1,duration:{round(min(2.2, d - 0.4), 2)},ease:"power2.out"}},{round(t0 + 0.2, 2)});')
            elif tipo not in ("titolo", "orbita", "telefono"):  # oggetti sfocati sullo sfondo, per dare profondità
                pool = getattr(self, "pool", ["livelli", "molla", "scintille", "forbici", "tavolozza", "ingranaggi", "fumetto", "catena", "squadra"])
                for k, (x, y, l, dx, dy, r) in enumerate([(-50, 30, 230, 150, 90, 70), (850, 1470, 250, -170, -110, -80), (40, 1580, 190, 130, -70, 110)]):
                    self.html.append(f'<div class="prop sw" id="{sid}s{k}" style="left:{x}px;top:{y}px;width:{l}px;height:{l}px"><img src="assets/img3d/{pool[(self.n * 3 + k) % len(pool)]}.png" alt=""></div>')
                    self.js.append(f'SW("#{sid}s{k}",{round(t0 + k * 0.08, 2)},{d},{dx},{dy},{r});')
        if q.get("lampo"): self.js.append(f'LAMPO({t0});')
        if "passo" in q: self.js.append(f'tl.to("#passi i:nth-child({q["passo"]})",{{backgroundColor:"#ff6a00",scaleX:1.25,duration:.4,ease:"back.out(2)"}},{t0});')
        if tipo == "titolo":
            pos = [(40, 150, 330, (-200, -120, -60)), (690, 170, 340, (220, -140, 40)), (50, 1300, 340, (-220, 160, -30)), (700, 1330, 320, (200, 160, 60))]
            for k, img in enumerate(q["props"]): x, y, l, da = pos[k]; self.prop(sid, k, img, x, y, l, t0 + k * 0.07, d, da)
            self.testo(sid, R, t0, t1, q.get("top", 620))
        elif tipo == "num":
            y = max(760, self.testo(sid, R, t0, t1, 430) + 20)
            self.prop(sid, 0, q["prop"], 300, y, 480, t0 + 0.25, d, (0, 260, 25))
            self.filo(sid, 540, y + 490, y + 680, t0 + 0.5); self.bottone(sid, 454, y + 660, t0 + 0.7)
        elif tipo == "card":
            self.html.append(f'<div class="card" id="{sid}c" style="left:90px;top:300px;width:900px;height:633px"><img src="assets/siti/{q["img"]}.png" alt=""></div>')
            self.js.append(f'CARD("#{sid}c",{t0},{d});')
            if self.wow:  # la scheda si apre in tre strati
                for k in (1, 2):
                    self.html.insert(len(self.html) - 1, f'<div class="card" id="{sid}c{k}" style="left:90px;top:300px;width:900px;height:633px"><img src="assets/siti/{q["img"]}.png" alt=""></div>')
                    self.js.append(f'tl.fromTo("#{sid}c{k}",{{opacity:0,y:200,rotationX:38,transformPerspective:1400}},{{opacity:{0.55 - k * 0.15},y:{-75 * k},scale:{1 - 0.07 * k},rotationX:{10 * k},duration:1,ease:"expo.out"}},{round(t0 + 0.15 * k, 2)});')
            if q.get("prop"): self.prop(sid, 0, q["prop"], 740, 760, 300, t0 + 0.3, d, (200, 80, 40))
            self.testo(sid, R, t0, t1, 1030)
        elif tipo == "grande":
            top = q.get("top", 660)
            if q.get("prop"):
                l = q.get("lato", 430)
                self.prop(sid, 0, q["prop"], 540 - l // 2, 330, l, t0 + 0.1, d, (0, -200, -20)); top = 330 + l + 70
            if q.get("prop2"): self.prop(sid, 1, q["prop2"], 720, 1250, 280, t0 + 0.3, d, (220, 100, 50))
            self.testo(sid, R, t0, t1, top)
        elif tipo == "lista":
            top = 430
            if q.get("barra"):
                self.html.append(f'<div class="barra" id="{sid}ba" style="left:110px;top:300px;width:330px">{q["barra"]}</div>')
                self.js.append(f'tl.fromTo("#{sid}ba",{{opacity:0,x:-300}},{{opacity:1,x:0,duration:.5,ease:"expo.out"}},{t0});'); top = 480
            if q.get("prop"): self.prop(sid, 0, q["prop"], 690, 230, 330, t0 + 0.2, d, (240, -80, 40))
            top = self.testo(sid, R, t0, t1, top, sin=110, larg=600 if q.get("prop") else 860) + 36
            sim = q.get("segno", "→"); y0 = top
            for k, (tt, voce) in enumerate(q["voci"]):
                vid = f"{sid}v{k}"; arr = "o" if voce.startswith("^") else ""; voce = voce.strip("^")
                sz = min(56, int(820 / (len(voce) * 0.5))) if len(voce) > 28 else 56
                self.html.append(f'<div class="voce {arr}" id="{vid}" style="top:{top}px;font-size:{sz}px"><span class="segno">{sim}</span><span>{voce}</span></div>')
                self.js.append(f'L("#{vid}",{tt});'); top += 96
            self.html.append(f'<div class="filo v" id="{sid}f" style="left:141px;top:{y0 + 30}px;height:{max(0, top - y0 - 96)}px"></div>')
            self.js.append(f'tl.fromTo("#{sid}f",{{scaleY:0}},{{scaleY:1,duration:{max(0.3, q["voci"][-1][0] - q["voci"][0][0])},ease:"none"}},{q["voci"][0][0]});')
            if q.get("coda"): self.testo(sid + "z", q["coda"][1:], q["coda"][0], t1, top + 30, sin=110, larg=860)
        elif tipo == "chips":
            for k, (tt, nome, logo) in enumerate(q["chips"]):
                cid = f"{sid}k{k}"; x = 110 + (k % 2) * 450; y = 320 + (k // 2) * 170
                ic = f'<i style="-webkit-mask-image:url(assets/loghi/{logo}.svg);mask-image:url(assets/loghi/{logo}.svg)"></i>' if logo else f'<b>{nome[0]}</b>'
                self.html.append(f'<div class="chip" id="{cid}" style="left:{x}px;top:{y}px">{ic}<span>{nome}</span></div>')
                self.js.append(f'tl.fromTo("#{cid}",{{opacity:0,scale:.4,y:60,rotation:{(-1) ** k * 10}}},{{opacity:1,scale:1,y:0,rotation:{(-1) ** k * 2},duration:.5,ease:"back.out(2)"}},{tt});')
            self.testo(sid, R[1:], R[0], t1, 900)
        elif tipo == "barre":
            for k, tt in enumerate(q["barre"]):
                bid = f"{sid}b{k}"
                self.html.append(f'<div class="barra" id="{bid}" style="left:190px;top:{350 + k * 150}px;width:700px">0{k + 1}</div>')
                self.js.append(f'tl.fromTo("#{bid}",{{opacity:0,y:-120,rotationX:70,transformPerspective:900}},{{opacity:1,y:0,rotationX:0,duration:.55,ease:"back.out(1.6)"}},{tt});')
            self.testo(sid, R, t0, t1, 900)
        elif tipo == "term":
            self.html.append(f'<div class="term" id="{sid}t" style="left:90px;top:300px;width:900px;height:{q.get("alt", 500)}px"><div class="tbar"><i></i><i></i><i></i></div>')
            for k, (tt, riga) in enumerate(q["term"]):
                ok = " ok" if riga.startswith("✓") else ""
                self.html.append(f'<div class="trg{ok}" id="{sid}g{k}">{riga}</div>')
                self.js.append(f'tl.fromTo("#{sid}g{k}",{{clipPath:"inset(0% 100% 0% 0%)"}},{{clipPath:"inset(0% 0% 0% 0%)",duration:{round(len(riga) * 0.022, 2)},ease:"steps({len(riga)})"}},{tt});')
            self.html.append('</div>'); self.js.append(f'CARD("#{sid}t",{t0},{d});')
            if q.get("prop"): self.prop(sid, 0, q["prop"], 730, 620, 300, t0 + 0.3, d, (200, 80, 40))
            self.testo(sid, R, t0, t1, 330 + q.get("alt", 500) + 70)
        elif tipo == "url":
            self.html.append(f'<div class="url" id="{sid}u" style="left:140px;top:290px;width:800px"><i></i><span id="{sid}ut">{q["url"]}</span></div>')
            self.js.append(f'tl.fromTo("#{sid}u",{{opacity:0,y:-80}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},{t0});tl.fromTo("#{sid}ut",{{clipPath:"inset(0% 100% 0% 0%)"}},{{clipPath:"inset(0% 0% 0% 0%)",duration:.7,ease:"steps({len(q["url"])})"}},{t0 + 0.3});')
            self.html.append(f'<div class="card" id="{sid}c" style="left:90px;top:460px;width:900px;height:560px"><img src="assets/siti/{q["img"]}.png" alt=""></div>')
            self.js.append(f'CARD("#{sid}c",{t0 + 1.2},{d - 1.2});')
            self.testo(sid, R, t0, t1, 1100)
        elif tipo == "hub":
            import math
            self.bottone(sid, 454, 630, t0)
            for k, img in enumerate(q["props"]):
                a = -90 + k * 72; cx = 540 + 330 * math.cos(math.radians(a)); cy = 716 + 330 * math.sin(math.radians(a))
                self.html.append(f'<div class="raggio" id="{sid}g{k}" style="left:540px;top:715px;width:230px;transform:rotate({a}deg)"></div>')
                self.js.append(f'tl.fromTo("#{sid}g{k}",{{scaleX:0}},{{scaleX:1,duration:.35,ease:"power2.out"}},{round(t0 + 0.25 + k * 0.12, 2)});')
                self.prop(sid, k, img, int(cx - 105), int(cy - 105), 210, round(t0 + 0.4 + k * 0.12, 2), d, (int((540 - cx) / 2), int((716 - cy) / 2), 40))
            self.testo(sid, R, t0, t1, 1200)
        elif tipo == "orbita":  # giostra di oggetti in 3D sopra il testo + striscia dei fotogrammi sotto
            import math
            N = 24; giri = d / 5.5; passo = round((d - 0.5) / N, 3)
            for k, img in enumerate(q["props"]):
                kf = []
                for i in range(N + 1):
                    a = 2 * math.pi * (k / len(q["props"]) + giri * i / N); z = math.sin(a)
                    kf.append({"x": round(400 * math.cos(a)), "y": round(110 * z), "scale": round(0.8 + 0.4 * z, 2), "opacity": round(0.75 + 0.25 * z, 2), "zIndex": 5 if z > 0 else 1, "rotation": round(-12 * math.cos(a)), "duration": passo, "ease": "none"})
                pid = f"{sid}o{k}"; a0 = {x: kf[0][x] for x in ("x", "y", "zIndex", "rotation")}
                self.html.append(f'<div class="prop" id="{pid}" style="left:430px;top:330px;width:220px;height:220px"><img src="assets/img3d/{img}.png" alt=""></div>')
                self.js.append(f'tl.fromTo("#{pid}",{json.dumps({**a0, "opacity": 0, "scale": 0})},{{opacity:{kf[0]["opacity"]},scale:{kf[0]["scale"]},duration:.5,ease:"back.out(2)"}},{t0});tl.to("#{pid}",{{keyframes:{json.dumps(kf[1:])}}},{round(t0 + 0.5, 2)});')
            self.testo(sid, R, t0, t1, 690)
            self.html.append(f'<div class="striscia" id="{sid}st" style="top:1250px">' + "".join(f'<div class="fot"><img src="assets/siti/fot{i}.jpg" alt=""></div>' for i in range(1, 10)) + '</div>')
            self.js.append(f'tl.fromTo("#{sid}st",{{x:1100,rotationY:-25,transformPerspective:1400}},{{x:-1150,rotationY:20,duration:{d},ease:"none"}},{t0});')
        elif tipo == "telefono":  # il video dentro un telefono che gira in 3D
            self.prop(sid, 0, q["props"][0], 20, 420, 270, t0 + 0.2, d, (-260, 60, -50)); self.prop(sid, 1, q["props"][1], 800, 640, 250, t0 + 0.35, d, (260, 80, 50))
            self.html.append(f'<div class="tel" id="{sid}tl" style="left:330px;top:250px">' + "".join(f'<img id="{sid}f{i}" src="assets/siti/fot{i}.jpg" alt="">' for i in range(1, 8)) + '</div>')
            self.js.append(f'tl.fromTo("#{sid}tl",{{opacity:0,y:600,rotationY:-80,rotationX:25,scale:.6,transformPerspective:1200}},{{opacity:1,y:0,rotationY:-20,rotationX:7,scale:1,duration:.9,ease:"expo.out"}},{t0});tl.to("#{sid}tl",{{rotationY:20,rotationX:-4,y:-24,duration:{round(d - 0.9, 2)},ease:"sine.inOut"}},{round(t0 + 0.9, 2)});')
            for i in range(2, 8): self.js.append(f'tl.fromTo("#{sid}f{i}",{{opacity:0,scale:1.25}},{{opacity:1,scale:1,duration:.18,ease:"power2.out"}},{round(t0 + 0.5 + (i - 1) * (d - 1.2) / 7, 2)});')
            self.testo(sid, R, t0, t1, 1130)
        elif tipo == "giro":
            imgs = q["imgs"]; n = len(imgs); passo = (d - 1.2) / n
            self.html.append(f'<div class="card" id="{sid}c" style="left:90px;top:300px;width:900px;height:633px"><div class="pellicola" id="{sid}pe">' + "".join(f'<img src="assets/siti/{i}.png" alt="">' for i in imgs) + '</div></div>')
            self.js.append(f'CARD("#{sid}c",{t0},{d});')
            for k in range(1, n):
                tt = round(t0 + 0.6 + passo * k, 2)
                self.js.append(f'tl.to("#{sid}pe",{{y:{-633 * k},duration:.7,ease:"power3.inOut"}},{tt});'); q.setdefault("suoni", []).append((tt, "fruscio"))
            self.testo(sid, R, t0, t1, 1030)
        elif tipo == "ruba":
            th = q["mano"]; GUANTO = '<svg viewBox="-10 -14 160 160"><g fill="#fff" stroke="#0b0a09" stroke-width="9" stroke-linejoin="round"><rect x="62" y="14" width="60" height="30" rx="15"/><rect x="70" y="42" width="64" height="30" rx="15"/><rect x="66" y="70" width="60" height="30" rx="15"/><rect x="56" y="96" width="52" height="28" rx="14"/><rect x="40" y="-6" width="30" height="56" rx="15" transform="rotate(-25 55 22)"/><rect x="14" y="20" width="80" height="104" rx="38"/></g></svg>'
            BL = [(24, 76, 392, 44, "#0b0a09"), (24, 136, 392, 190, "#ff6a00"), (24, 344, 120, 130, "#0b0a09"), (160, 344, 120, 130, "#ffb27a"), (296, 344, 120, 130, "#0b0a09"), (24, 492, 250, 34, "#ff6a00")]
            blocchi = "".join(f'<div class="bl" id="{sid}b{k}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"></div>' for k, (x, y, w, h, c) in enumerate(BL))
            self.html.append(f'<div class="fin" id="{sid}fa" style="left:70px;top:330px"><div class="tbar"><i></i><i></i><i></i></div>{blocchi}</div>')
            SITO = ('<div class="bl" style="left:0;top:58px;width:440px;height:236px;border-radius:0;background:linear-gradient(135deg,#ff6a00,#ffb27a)"></div>'
                    '<div class="bl" style="left:26px;top:104px;width:250px;height:28px;background:#fff"></div><div class="bl" style="left:26px;top:146px;width:180px;height:28px;background:#fff"></div>'
                    '<div class="bl" style="left:26px;top:206px;width:136px;height:48px;border-radius:24px;background:#0b0a09"></div><div class="bl" style="left:318px;top:96px;width:96px;height:96px;border-radius:50%;background:#0b0a09"></div>'
                    '<div class="bl" style="left:24px;top:318px;width:120px;height:122px;background:#0b0a09"></div><div class="bl" style="left:160px;top:318px;width:120px;height:122px;background:#ffb27a"></div><div class="bl" style="left:296px;top:318px;width:120px;height:122px;background:#0b0a09"></div>'
                    '<div class="bl" style="left:0;top:464px;width:440px;height:96px;border-radius:0;background:#0b0a09"></div><div class="bl" style="left:26px;top:496px;width:34px;height:34px;border-radius:50%;background:#ff6a00"></div><div class="bl" style="left:76px;top:504px;width:170px;height:18px;background:#4a4540"></div>')
            dentro = f'<img src="assets/siti/{q["img"]}.png" alt="">' if q.get("img") else SITO
            self.html.append(f'<div class="fin" id="{sid}fb" style="left:570px;top:330px"><div class="tbar"><i></i><i></i><i></i></div>{dentro}</div>')
            self.html.append(f'<div class="braccio" id="{sid}br" style="left:460px;top:583px"></div><div class="guanto" id="{sid}gu" style="left:420px;top:540px">{GUANTO}</div>')
            for k, c in enumerate(["#ff6a00", "#0b0a09", "#ffb27a", "#ffffff"]):
                self.html.append(f'<div class="gocc" id="{sid}go{k}" style="left:{730 + k % 2 * 50}px;top:{560 + k // 2 * 50}px;background:{c}"></div>')
                self.js.append(f'tl.fromTo("#{sid}go{k}",{{scale:0}},{{scale:1,duration:.25,ease:"back.out(3)"}},{round(th + 0.78 + k * 0.04, 2)});tl.to("#{sid}go{k}",{{x:{-470 + k * 22},y:{-60 + k * 40},duration:.5,ease:"power3.in"}},{round(th + 1.15 + k * 0.03, 2)});tl.to("#{sid}go{k}",{{scale:0,duration:.2}},{round(th + 1.7, 2)});')
            self.js.append(f'CARD("#{sid}fa",{t0},{d});CARD("#{sid}fb",{round(t0 + 0.12, 2)},{d});')
            self.js.append(f'tl.fromTo("#{sid}br",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"power3.out"}},{th});tl.fromTo("#{sid}gu",{{x:0,scale:.2,opacity:0}},{{x:330,scale:1,opacity:1,duration:.5,ease:"power3.out"}},{th});'
                           f'tl.to("#{sid}gu",{{scale:.74,rotation:-12,duration:.12,yoyo:true,repeat:1}},{round(th + 0.66, 2)});tl.fromTo("#{sid}fb",{{x:0}},{{x:12,duration:.05,yoyo:true,repeat:5}},{round(th + 0.7, 2)});'
                           f'tl.to("#{sid}br",{{scaleX:0,duration:.5,ease:"power3.in"}},{round(th + 1.15, 2)});tl.to("#{sid}gu",{{x:0,scale:.2,opacity:0,duration:.5,ease:"power3.in"}},{round(th + 1.15, 2)});')
            for k, (x, y, w, h, c) in enumerate(BL):
                self.js.append(f'tl.to("#{sid}b{k}",{{backgroundColor:"{c}",duration:.3,ease:"power2.out"}},{round(th + 1.7 + k * 0.13, 2)});tl.fromTo("#{sid}b{k}",{{scale:1}},{{scale:1.08,duration:.12,yoyo:true,repeat:1}},{round(th + 1.7 + k * 0.13, 2)});')
            q.setdefault("suoni", []).extend([(th, "fruscio"), (round(th + 0.68, 2), "molla"), (round(th + 1.15, 2), "fruscio"), (round(th + 1.7, 2), "pop"), (round(th + 1.96, 2), "pop"), (round(th + 2.22, 2), "pop"), (round(th + 2.5, 2), "campanella")])
            self.testo(sid, R, t0, t1, 980)
        elif tipo == "cambia":  # la scheda si gira e diventa un'altra: con due click del cursore, o con lo scatto di una foto
            a = q["a"]; R0 = 'style="left:90px;top:300px;width:900px;height:633px"'
            self.html.append(f'<div class="card" id="{sid}c" {R0}><img src="assets/siti/{q["img"]}.png" alt=""></div><div class="card" id="{sid}d" {R0}><img src="assets/siti/{q["img2"]}.png" alt=""></div>')
            self.js.append(f'CARD("#{sid}c",{t0},{d});tl.set("#{sid}d",{{opacity:0}},0);tl.to("#{sid}c",{{rotationY:88,opacity:0,duration:.24,ease:"power2.in"}},{a});tl.fromTo("#{sid}d",{{rotationY:-88,opacity:0,scale:.9,transformPerspective:1400}},{{rotationY:0,opacity:1,scale:1,duration:.5,ease:"back.out(1.5)"}},{round(a + 0.24, 2)});tl.to("#{sid}d",{{scale:1.04,rotationY:4,duration:{max(0.4, round(t1 - a - 0.8, 2))},ease:"sine.inOut"}},{round(a + 0.75, 2)});')
            suoni = q.setdefault("suoni", [])
            if q.get("flash"):
                self.html.append(f'<div class="card" id="{sid}fl" style="left:90px;top:300px;width:900px;height:633px;opacity:0"></div>')
                self.js.append(f'tl.fromTo("#{sid}fl",{{opacity:0,backgroundColor:"#ffffff"}},{{opacity:1,duration:.06}},{round(a - 0.08, 2)});tl.to("#{sid}fl",{{opacity:0,duration:.35}},{round(a + 0.05, 2)});'); suoni.append((round(a - 0.1, 2), "scatto"))
            else:
                self.html.append(f'<div class="cursore" id="{sid}cu" style="left:520px;top:640px"><svg viewBox="0 0 60 80"><path d="M6 4 L6 62 L22 48 L33 74 L44 69 L33 44 L54 44 Z" fill="#0b0a09" stroke="#fff" stroke-width="5" stroke-linejoin="round"/></svg></div><div class="anello" id="{sid}an" style="left:486px;top:606px"></div>')
                self.js.append(f'tl.fromTo("#{sid}cu",{{opacity:0,x:260,y:300}},{{opacity:1,x:0,y:0,duration:.5,ease:"power3.out"}},{round(a - 1.15, 2)});tl.to("#{sid}cu",{{opacity:0,duration:.2}},{round(a + 0.1, 2)});')
                for c in (0.55, 0.25):
                    self.js.append(f'tl.to("#{sid}cu",{{scale:.8,duration:.07,yoyo:true,repeat:1}},{round(a - c, 2)});tl.fromTo("#{sid}an",{{scale:.2,opacity:.9}},{{scale:1.5,opacity:0,duration:.3,ease:"power2.out"}},{round(a - c, 2)});'); suoni.append((round(a - c, 2), "tasto"))
            suoni += [(a, "fruscio"), (round(a + 0.3, 2), "pop")]
            if q.get("prop"): self.prop(sid, 0, q["prop"], 760, 780, 280, round(a + 0.35, 2), max(1.2, t1 - a), (200, 80, 40))
            self.testo(sid, R, t0, t1, 1030)
        elif tipo in ("segui", "marchio"):
            self.html.append(f'<div class="velo" id="{sid}ve"></div>'); self.js.append(f'tl.fromTo("#{sid}ve",{{opacity:0}},{{opacity:1,duration:.4}},{t0});')
            top = self.testo(sid, R[:2], t0, t1, 450)
            self.html.append(f'<div class="prop" id="{sid}lg" style="left:290px;top:{top + 30}px;width:500px;height:500px"><img src="assets/marca/logo.png" alt=""></div>')
            self.js.append(f'tl.fromTo("#{sid}lg",{{opacity:0,scale:.2,rotationY:540,transformPerspective:1200}},{{opacity:1,scale:1,rotationY:0,duration:1,ease:"expo.out"}},{t0 + 0.3});tl.to("#{sid}lg",{{y:-22,rotation:3,duration:1.1,ease:"sine.inOut",yoyo:true,repeat:{max(1, int(d - 1.4))}}},{t0 + 1.3});')
            self.testo(sid + "z", R[2:], t0, t1, top + 570)
        for k, gg in enumerate(q.get("gag", [])): self.gag(sid, k, gg, q, t1)
        cima = {"ruba": 330, "giro": 300, "cambia": 300, "card": 300, "grande": 330 if q.get("prop") else q.get("top", 660), "lista": 230 if q.get("prop") else 300 if q.get("barra") else 430, "chips": 320, "barre": 350, "term": 300, "url": 290}.get(tipo)
        if tipo == "lista": self.fondo = max(self.fondo, top)
        off = 0 if cima is None else max(0, min(260, 880 - (cima + self.fondo) // 2))
        self.html[segna] = self.html[segna].replace("@@OFF@@", str(off))
        self.html.append('</div></div></div>')
        if self.wow and tipo not in ("segui", "marchio"):  # uscite diverse a rotazione: attraverso lo schermo, frustata, ribaltata
            via = ['scale:1.8,filter:"blur(22px)"', 'x:-1000,skewX:14,filter:"blur(18px)"', 'y:-520,rotationX:65,transformPerspective:1200,filter:"blur(14px)"'][self.n % 3]
            self.js.append(f'tl.to("#{sid}in",{{opacity:0,{via},duration:.26,ease:"power3.in"}},{round(t1 - 0.27, 2)});')
        elif tipo not in ("segui", "marchio"): self.js.append(f'tl.to("#{sid}in",{{opacity:0,scale:1.07,filter:"blur(16px)",duration:.22,ease:"power2.in"}},{round(t1 - 0.23, 2)});')

def trova(par, parola, dopo):
    k = norm(parola)
    for p in par:
        c = norm(p["w"])
        if p["s"] >= dopo and k and (c == k or (len(k) > 3 and c[:4] == k[:4])): return p["s"]
    raise SystemExit(f"àncora «{parola}» non trovata dopo {dopo} s")
def risolvi(Q, par):
    """Sostituisce le àncore a parole (t="Uno:") con il tempo in cui quella parola viene detta: così la scaletta
    resta valida anche quando la voce cambia. I numeri restano numeri."""
    prima = -1.0
    for q in Q:
        if isinstance(q["t"], str): q["t"] = max(0.0, round(trova(par, q["t"], prima + 0.25) - 0.07, 2))
        prima = q["t"]
        for k in ("voci", "term", "chips"):
            if k in q:
                cur, nuovo = prima - 0.1, []
                for v in q[k]:
                    t = round(trova(par, v[0], cur + 0.05), 2) if isinstance(v[0], str) else v[0]; cur = t; nuovo.append((t, *v[1:]))
                q[k] = nuovo
        if "barre" in q:
            cur, nuovo = prima - 0.1, []
            for b in q["barre"]:
                t = round(trova(par, b, cur + 0.05), 2) if isinstance(b, str) else b; cur = t; nuovo.append(t)
            q["barre"] = nuovo
        if "gag" in q: q["gag"] = [(x[0], round(trova(par, x[1], prima), 2) if isinstance(x[1], str) else x[1], *x[2:]) for x in q["gag"]]
        for k in ("a", "mano"):
            if isinstance(q.get(k), str): q[k] = round(trova(par, q[k], prima), 2)
        if q.get("coda") and isinstance(q["coda"][0], str): q["coda"] = [round(trova(par, q["coda"][0], prima), 2), *q["coda"][1:]]
        if q.get("tipo") == "chips" and isinstance(q["righe"][0], str): q["righe"] = [round(trova(par, q["righe"][0], prima), 2), *q["righe"][1:]]


# ====================== coda del motore: dal file video.py al progetto pronto da renderizzare ======================
import runpy
QUI = os.path.dirname(os.path.abspath(__file__)); RADICE = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import sfx
CSS = open(os.path.join(QUI, "stile.css"), encoding="utf-8").read()
JS0 = open(os.path.join(QUI, "gesti.js"), encoding="utf-8").read()

def tempi_lettura(battute):
    """Senza voce le parole entrano a passo di lettura: stesso formato dei tempi di una voce vera."""
    t, out = 0.0, []
    for b in battute:
        for w in b.split():
            d = 0.07 + 0.05 * len(w)
            out.append({"w": w, "s": round(t, 2), "e": round(t + d, 2)}); t += d + 0.04
            if w[-1] in ".!?": t += 1.0      # a fine frase il testo resta a schermo: va letto, non inseguito
            elif w[-1] in ":;": t += 0.45
            elif w[-1] == ",": t += 0.25
        t += 0.25
    return out, round(t, 2)

def chiaro(hexcol, k=0.4):
    r, g, b = (int(hexcol.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(int(c + (255 - c) * k) for c in (r, g, b))

def scheda(src, dst):
    """Porta qualunque immagine al formato della scheda (1800x1266): larga = ritaglio centrato, alta = intera su fondo chiaro."""
    from PIL import Image
    im = Image.open(src).convert("RGB"); W, H = 1800, 1266
    if im.height > im.width * 1.05:
        k = min((H - 80) / im.height, (W - 80) / im.width); im = im.resize((int(im.width * k), int(im.height * k)))
        t = Image.new("RGB", (W, H), "#eeece8"); t.paste(im, ((W - im.width) // 2, (H - im.height) // 2)); im = t
    else:
        k = max(W / im.width, H / im.height); im = im.resize((int(im.width * k) + 1, int(im.height * k) + 1))
        x, y = (im.width - W) // 2, (im.height - H) // 2; im = im.crop((x, y, x + W, y + H))
    im.save(dst)

MODELLO = '''<!doctype html>
<html lang="it">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      @font-face { font-family: "DM Sans"; font-weight: 500; src: url("assets/fonts/dm-sans-500.woff2") format("woff2"); }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #f8f7f4; }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #f8f7f4; }
      #griglia { position: absolute; inset: -60px; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cpath d='M60 53v14M53 60h14' stroke='%23d9d5cf' stroke-width='2'/%3E%3C/svg%3E"); background-size: 120px 120px; }
      #luce { position: absolute; inset: 0; background: radial-gradient(ellipse 70% 55% at 50% 45%, rgba(255,255,255,0.75), rgba(255,255,255,0) 70%); }
      #firma { position: absolute; left: 0; width: 1080px; top: 1716px; text-align: center; font-family: "DM Sans", sans-serif; font-weight: 500; font-size: 34px; letter-spacing: -0.01em; color: #d6d1ca; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="@@TOT@@" data-width="1080" data-height="1920">
      <div id="griglia" data-layout-ignore></div>
      <div id="luce" data-layout-ignore></div>
      <div id="firma" data-layout-ignore>@@FIRMA@@</div>
      <div id="film" data-composition-id="film" data-composition-src="compositions/film.html" data-start="0" data-duration="@@TOT@@" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index: 10"></div>
      @@AUDIO@@
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      tl.fromTo("#griglia", { x: 0, y: 0 }, { x: -60, y: -120, duration: @@TOT@@, ease: "none" }, 0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''

def costruisci(P):
    P = os.path.abspath(P)
    v = runpy.run_path(os.path.join(P, "video.py"), init_globals={"Q": dict})
    for k in ("MARCA", "BATTUTE", "QUADRI"):
        if k not in v: raise SystemExit(f"in video.py manca {k}")
    M, battute, opz = v["MARCA"], v["BATTUTE"], v.get("OPZIONI", {})
    F = os.path.join(P, "film")
    for sub in ("assets/img3d", "assets/siti", "assets/loghi", "assets/fonts", "assets/audio", "assets/marca", "compositions", "renders"): os.makedirs(os.path.join(F, sub), exist_ok=True)
    R = lambda *a: subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *a], check=True)
    A = os.path.join(F, "assets", "audio")
    # voce vera (preparata da voce.py) oppure tempi di lettura e traccia muta
    vj, vw = os.path.join(P, "voce", "parole.json"), os.path.join(P, "voce", "voce.wav"); muta = not (os.path.exists(vj) and os.path.exists(vw))
    if muta:
        par, corpo = tempi_lettura(battute)
    else:
        par = json.load(open(vj, encoding="utf-8"))
        corpo = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vw], capture_output=True, text=True).stdout)
    tot = round(corpo + 2.6, 2)
    if muta: R("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(tot), os.path.join(A, "voce.wav"))
    else: R("-i", vw, "-af", "apad", "-t", str(tot), "-ar", "44100", "-ac", "1", os.path.join(A, "voce.wav"))
    mus = M.get("musica"); mp3 = os.path.join(A, "musica.mp3")
    if mus:
        mus = mus if os.path.isabs(mus) else os.path.join(P, mus)
        if not os.path.exists(mus): raise SystemExit(f"musica non trovata: {mus}")
        R("-stream_loop", "8", "-i", mus, "-t", str(tot), "-af", f"afade=t=out:st={tot - 1.5}:d=1.5", mp3)
    elif os.path.exists(mp3): os.remove(mp3)
    # materiale: caratteri e oggetti della skill, più oggetti, immagini e logo dell'utente
    for d in ("fonts", "img3d"):
        for f in os.listdir(os.path.join(RADICE, "assets", d)): shutil.copy2(os.path.join(RADICE, "assets", d, f), os.path.join(F, "assets", d, f))
    for d, dst in (("oggetti", "img3d"), ("loghi", "loghi")):
        if os.path.isdir(os.path.join(P, d)):
            for f in os.listdir(os.path.join(P, d)): shutil.copy2(os.path.join(P, d, f), os.path.join(F, "assets", dst, f))
    if os.path.isdir(os.path.join(P, "immagini")):
        for f in os.listdir(os.path.join(P, "immagini")):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")): scheda(os.path.join(P, "immagini", f), os.path.join(F, "assets", "siti", os.path.splitext(f)[0] + ".png"))
    logo = M.get("logo") or "logo.png"; logo = logo if os.path.isabs(logo) else os.path.join(P, logo)
    if not os.path.exists(logo): raise SystemExit(f"logo non trovato: {logo} (serve un PNG, meglio quadrato e con fondo trasparente)")
    shutil.copy2(logo, os.path.join(F, "assets", "marca", "logo.png"))

    f = Film(par, opz.get("wow", 1), opz.get("forme", 0)); Qs = [dict(q) for q in v["QUADRI"]]; risolvi(Qs, par)
    if any(a["t"] >= b["t"] for a, b in zip(Qs, Qs[1:])): raise SystemExit("i quadri non sono in ordine di tempo: controlla le àncore " + str([q["t"] for q in Qs]))
    for i, q in enumerate(Qs): f.quadro(q, Qs[i + 1]["t"] if i + 1 < len(Qs) else tot)
    sfx.traccia(Qs, tot, os.path.join(A, "sfx.wav"))
    col = M.get("colore", "#ff6a00").lower(); tinta = chiaro(col)
    COL = lambda s: s.replace("#ff6a00", col).replace("#ff8a3c", tinta).replace("#ffb27a", tinta)
    passi = '<div id="passi">' + "<i></i>" * opz["passi"] + "</div>" if opz.get("passi") else ""
    film = f"""<template>
  <style>{CSS}</style>
  <div id="root" data-composition-id="film" data-width="1080" data-height="1920">
    {passi}
    {chr(10).join(f.html)}
    <div id="lampo" class="clip" data-start="0" data-duration="{tot}" data-layout-ignore></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {JS0}
    {chr(10).join(f.js)}
    window.__timelines["film"] = tl;
  </script>
</template>
"""
    film = COL(film)
    mancanti = sorted({m for m in re.findall(r'assets/(?:img3d|siti|loghi)/[^"\')]+', film) if not os.path.exists(os.path.join(F, m))})
    if mancanti:
        ogg = sorted(x[:-4] for x in os.listdir(os.path.join(F, "assets", "img3d")))
        raise SystemExit("file mancanti: " + ", ".join(mancanti) + "\noggetti disponibili: " + ", ".join(ogg) + "\nle immagini vanno in <progetto>/immagini, gli oggetti tuoi in <progetto>/oggetti")
    open(os.path.join(F, "compositions", "film.html"), "w", encoding="utf-8").write(film)
    audio = f'<audio id="voce" class="clip" src="assets/audio/voce.wav" data-start="0" data-duration="{tot - 0.05}" data-volume="1" data-track-index="6"></audio>'
    if mus: audio += f'\n      <audio id="musica" class="clip" src="assets/audio/musica.mp3" data-start="0" data-duration="{tot}" data-volume="0.2" data-track-index="7"></audio>'
    open(os.path.join(F, "index.html"), "w", encoding="utf-8").write(MODELLO.replace("@@TOT@@", str(tot)).replace("@@FIRMA@@", M.get("sito", "")).replace("@@AUDIO@@", audio))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}}, open(os.path.join(F, "hyperframes.json"), "w"), indent=1)
    json.dump({"name": "short-video", "private": True, "type": "module"}, open(os.path.join(F, "package.json"), "w"), indent=1)
    json.dump({"id": "short-video", "name": M.get("nome", "short-video")}, open(os.path.join(F, "meta.json"), "w"))
    json.dump({"muta": muta, "musica": bool(mus), "tot": tot}, open(os.path.join(F, "mix.json"), "w"))
    print("durata", tot, "s ·", len(Qs), "quadri ·", "senza voce (tempi di lettura)" if muta else "con voce")
    print("FOTOGRAMMI " + ",".join(str(round((Qs[i + 1]["t"] if i + 1 < len(Qs) else tot) - 0.45, 2)) for i in range(len(Qs))))

if __name__ == "__main__":
    if len(sys.argv) < 2: raise SystemExit("uso: python genera.py <cartella-progetto>")
    costruisci(sys.argv[1])
