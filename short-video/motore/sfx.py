"""Effetti sonori sintetizzati (niente file esterni, niente crediti): fruscio sui cambi di quadro, colpo sui lampi,
«pop» sulle voci d'elenco, ticchettio sulle righe battute, campanella sull'invito finale.
traccia(quadri, tot, file) scrive un wav mono 44,1 kHz lungo quanto il video."""
import wave
import numpy as np
SR = 44100
rng = np.random.default_rng(7)  # seme fisso: stesso suono a ogni generazione

def _t(d): return np.arange(int(SR * d)) / SR
def fruscio(d=0.42):
    n = rng.standard_normal(int(SR * d)); t = _t(d) / d
    taglio = 400 + 5200 * np.sin(np.pi * t) ** 2          # il filtro si apre e si richiude: «fwoosh»
    a = np.exp(-2 * np.pi * taglio / SR); y = np.zeros_like(n); z = 0.0
    for i in range(len(n)): z = a[i] * z + (1 - a[i]) * n[i]; y[i] = z
    return y / np.abs(y).max() * np.sin(np.pi * t) ** 2 * 0.5
def colpo(d=0.45):
    t = _t(d); return (np.sin(2 * np.pi * (95 * t - 60 * t * t)) * np.exp(-t * 9) * 0.5 + rng.standard_normal(len(t)) * np.exp(-t * 60) * 0.14)
def pop(d=0.11):
    t = _t(d); return np.sin(2 * np.pi * (620 * t - 1900 * t * t)) * np.exp(-t * 38) * 0.55
def tic(d=0.025):
    t = _t(d); return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 220) * 0.3
def tasto():
    # tasto di tastiera: scatto secco + corpo basso, ogni volta un po' diverso (come una mano vera)
    d = 0.05; t = _t(d); f = 1700 + rng.uniform(-350, 450)
    return (rng.standard_normal(len(t)) * np.exp(-t * 260) * 0.5 + np.sin(2 * np.pi * f * t) * np.exp(-t * 190) * 0.3 + np.sin(2 * np.pi * 160 * t) * np.exp(-t * 70) * 0.35) * rng.uniform(0.7, 1.0) * 0.4   # 11/11: gli effetti di scrittura erano troppo alti
def molla(d=0.5):
    t = _t(d); return np.sin(2 * np.pi * (240 + 160 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 6)) * t) * np.exp(-t * 7) * 0.4
def scatto():
    a = tasto(); b = tasto(); out = np.zeros(int(SR * 0.2)); out[:len(a)] += a * 1.3; i = int(SR * 0.09); out[i:i + len(b)] += b
    return out + rng.standard_normal(len(out)) * np.exp(-_t(0.2) * 30) * 0.12
def timbro():
    c = colpo() * 0.9; a = tasto(); c[:len(a)] += a * 1.4; return c
def campanella(d=0.9):
    t = _t(d); return (np.sin(2 * np.pi * 1046 * t) + 0.6 * np.sin(2 * np.pi * 1568 * t) + 0.3 * np.sin(2 * np.pi * 2093 * t)) * np.exp(-t * 5) * 0.3

def schiocco(d=0.16):
    """Schiocco di dita: uno scatto secco e brillante con una coda corta di stanza."""
    t = _t(d); n = rng.standard_normal(len(t)); r = int(SR * 0.018)
    secco = n * np.exp(-t * 420) * 0.9 + np.sin(2 * np.pi * 2300 * t) * np.exp(-t * 300) * 0.6 + np.sin(2 * np.pi * 1150 * t) * np.exp(-t * 180) * 0.35
    coda = np.concatenate([np.zeros(r), n[: len(t) - r] * np.exp(-t[: len(t) - r] * 60) * 0.12])
    return (secco + coda) * 0.9
def onda(d=0.5):
    """L'onda d'urto dopo lo schiocco: un tono che precipita con un soffio."""
    t = _t(d); f = 950 * np.exp(-t * 8) + 60; ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 6.5) * 0.75 + rng.standard_normal(len(t)) * np.exp(-t * 13) * 0.22) * 0.8
def traccia(quadri, tot, file):
    out = np.zeros(int(SR * (tot + 1)))
    def metti(s, t):
        i = max(0, int(SR * t)); s = s[: len(out) - i]; out[i:i + len(s)] += s
    F, C = fruscio(), colpo()
    for q in quadri:
        t = q["t"]
        if t > 0.2:
            metti(F, t - 0.2)
            if q.get("lampo"): metti(C, t - 0.03)
        for v in q.get("voci", []) + q.get("chips", []): metti(pop(), v[0])
        for k, b in enumerate(q.get("barre", [])): metti(pop(), b)
        for tt, riga in q.get("term", []):   # una battuta ogni due caratteri, niente sugli spazi: tastiera, non mitraglia
            for k, c in enumerate(riga):
                if k % 2 == 0 and c != " " and not riga.startswith("✓"): metti(tasto(), tt + k * 0.022)
            if riga.startswith("✓"): metti(pop(), tt)
        if q.get("tipo") == "url":
            for k in range(0, len(q["url"]), 2): metti(tasto(), t + 0.3 + k * 0.7 / len(q["url"]))
        for tt, nome in q.get("suoni", []):  # suoni chiesti dalla scaletta o dalle scenette (es. la mano che ruba il design)
            metti({"pop": pop, "fruscio": fruscio, "colpo": colpo, "campanella": campanella, "tasto": tasto, "molla": molla, "scatto": scatto, "timbro": timbro, "schiocco": schiocco, "onda": onda}[nome](), tt)
        if q.get("tipo") in ("orbita", "telefono", "titolo"): metti(F, t + 0.05)
        if q.get("campana") or q.get("tipo") in ("segui", "marchio"): metti(campanella(), t + (q.get("campana") or 0.3))
    out = np.clip(out, -1, 1)
    with wave.open(file, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype("<i2").tobytes())

if __name__ == "__main__":  # autoverifica: la traccia esiste, è lunga giusta e non è muta
    import os, tempfile
    f = os.path.join(tempfile.gettempdir(), "sfx_prova.wav")
    traccia([dict(t=0, tipo="titolo"), dict(t=2, lampo=1, voci=[(2.5, "a")], term=[(3, "ciao mondo")]), dict(t=4, tipo="segui")], 6, f)
    w = wave.open(f); d = np.frombuffer(w.readframes(w.getnframes()), "<i2")
    assert abs(w.getnframes() / SR - 7) < 0.01 and np.abs(d).max() > 3000, "traccia sbagliata"
    print("ok", round(w.getnframes() / SR, 2), int(np.abs(d).max()))
