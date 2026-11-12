"""Renderizza il progetto e fa il mix finale: voce (se c'è) davanti, musica sotto che si abbassa quando parla la voce,
effetti sonori sopra. Uso: python render.py <cartella-progetto> [--solo-audio]
--solo-audio riusa il render già fatto e rifà solo il mix (utile dopo aver cambiato musica, voce o effetti)."""
import json, os, subprocess, sys
if len(sys.argv) < 2: raise SystemExit("uso: python render.py <cartella-progetto> [--solo-audio]")
P = os.path.abspath(sys.argv[1]); F = os.path.join(P, "film"); A = os.path.join(F, "assets", "audio"); raw = os.path.join(F, "renders", "render.mp4")
if not os.path.exists(os.path.join(F, "mix.json")): raise SystemExit("prima lancia: python genera.py " + sys.argv[1])
mix = json.load(open(os.path.join(F, "mix.json")))
if "--solo-audio" not in sys.argv:
    r = subprocess.run("npx --yes hyperframes@0.9.26 render --quality high --workers 2 --output renders/render.mp4", cwd=F, shell=True)
    if r.returncode: raise SystemExit("render fallito: leggi l'errore qui sopra (di solito manca Node o Chrome)")
if not os.path.exists(raw): raise SystemExit("render mancante: rilancia senza --solo-audio")
ing = ["-i", raw, "-i", os.path.join(A, "voce.wav")]; f = "[1:a]highpass=f=85,acompressor=threshold=-20dB:ratio=3:attack=8:release=160:makeup=2,aecho=0.8:0.3:42:0.13,volume=0.9,asplit=2[v][k];"
piste = ["[v]"]; n = 2
if mix["musica"]:
    ing += ["-i", os.path.join(A, "musica.mp3")]; f += f"[{n}:a]volume={0.55 if mix['muta'] else 0.14}[m0];[m0][k]sidechaincompress=threshold=0.03:ratio=3.5:attack=15:release=380[m];"; piste.append("[m]"); n += 1
else: f += "[k]anullsink;"
ing += ["-i", os.path.join(A, "sfx.wav")]; f += f"[{n}:a]volume={0.3 if mix['muta'] else 0.22}[s];"; piste.append("[s]")
f += "".join(piste) + f"amix=inputs={len(piste)}:normalize=0:duration=longest,loudnorm=I=-14:TP=-1.2:LRA=11,apad[a]"
fin = os.path.join(P, "video.mp4"); ant = os.path.join(P, "anteprima-720p.mp4")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *ing, "-filter_complex", f, "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", fin], check=True)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", fin, "-vf", "scale=720:-2", "-c:v", "libx264", "-crf", "24", "-c:a", "aac", "-b:a", "128k", ant], check=True)
print("FATTO", fin, round(os.path.getsize(fin) / 1e6, 1), "MB · anteprima:", ant)
