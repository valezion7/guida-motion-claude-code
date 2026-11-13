"""Voce (facoltativa). Prende le battute registrate in <progetto>/voce/01.mp3, 02.mp3… (una per ogni voce di BATTUTE,
fatte con qualunque sintetizzatore o registrate a mano), le pulisce, le unisce e trova il tempo di ogni parola.
Scrive <progetto>/voce/voce.wav e parole.json: da quel momento genera.py usa la voce al posto dei tempi di lettura.

Uso: python voce.py <cartella-progetto>
     python voce.py <cartella-progetto> --edge [VOCE]            (GRATIS, senza chiave: genera le battute con le voci
                                                                  online di Microsoft Edge; serve pip install edge-tts)
     python voce.py <cartella-progetto> --elevenlabs <ID_VOCE>   (a pagamento, più naturale: serve la variabile
                                                                  d'ambiente ELEVENLABS_API_KEY dell'utente)
Serve: pip install faster-whisper"""
import json, os, runpy, subprocess, sys, urllib.request
if len(sys.argv) < 2: raise SystemExit("uso: python voce.py <cartella-progetto> [--edge [VOCE] | --elevenlabs ID_VOCE]")
P = os.path.abspath(sys.argv[1]); V = os.path.join(P, "voce"); os.makedirs(V, exist_ok=True)
battute = runpy.run_path(os.path.join(P, "video.py"), init_globals={"Q": dict})["BATTUTE"]
if "--edge" in sys.argv:   # voce gratuita: nessuna chiave, serve la rete
    try: import asyncio, edge_tts
    except ImportError: raise SystemExit("per la voce gratuita serve edge-tts: pip install edge-tts")
    k = sys.argv.index("--edge"); voce = sys.argv[k + 1] if len(sys.argv) > k + 1 and not sys.argv[k + 1].startswith("--") else "it-IT-GiuseppeMultilingualNeural"
    async def _tutte():
        for i, b in enumerate(battute, 1): await edge_tts.Communicate(b, voce, rate="+7%").save(os.path.join(V, f"{i:02d}.mp3")); print("battuta", i, "registrata")
    asyncio.run(_tutte())
if "--elevenlabs" in sys.argv:
    chiave = os.environ.get("ELEVENLABS_API_KEY"); voce = sys.argv[sys.argv.index("--elevenlabs") + 1]
    if not chiave: raise SystemExit("manca la variabile d'ambiente ELEVENLABS_API_KEY (la chiave è dell'utente: non scriverla nei file)")
    for i, b in enumerate(battute, 1):
        req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voce}", data=json.dumps({"text": b, "model_id": "eleven_multilingual_v2"}).encode(),
                                     headers={"xi-api-key": chiave, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        open(os.path.join(V, f"{i:02d}.mp3"), "wb").write(urllib.request.urlopen(req, timeout=120).read()); print("battuta", i, "registrata")
file = sorted(f for f in os.listdir(V) if f[:2].isdigit() and f.lower().endswith((".mp3", ".wav", ".m4a")))
if len(file) != len(battute): raise SystemExit(f"in {V} ci sono {len(file)} battute audio ma BATTUTE ne ha {len(battute)}: servono 01, 02… una per battuta")
try: from faster_whisper import WhisperModel
except ImportError: raise SystemExit("serve faster-whisper per trovare i tempi delle parole: pip install faster-whisper")
R = lambda *a: subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *a], check=True)
TRIM = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
R("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.22", os.path.join(V, "_gap.wav"))
with open(os.path.join(V, "_lista.txt"), "w") as fh:
    for f in file:
        R("-i", os.path.join(V, f), "-af", TRIM, "-ar", "44100", "-ac", "1", os.path.join(V, "_t" + f[:2] + ".wav")); fh.write(f"file '_t{f[:2]}.wav'\nfile '_gap.wav'\n")
R("-f", "concat", "-safe", "0", "-i", os.path.join(V, "_lista.txt"), "-af", "silenceremove=stop_periods=-1:stop_duration=0.3:stop_threshold=-45dB", os.path.join(V, "voce.wav"))
lingua = runpy.run_path(os.path.join(P, "video.py"), init_globals={"Q": dict}).get("OPZIONI", {}).get("lingua", "it")
segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(os.path.join(V, "voce.wav"), language=lingua, word_timestamps=True)
w = [{"w": x.word.strip(), "s": round(x.start, 2), "e": round(x.end, 2)} for s in segs for x in s.words]
json.dump(w, open(os.path.join(V, "parole.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("voce pronta:", round(w[-1]["e"], 1), "s,", len(w), "parole. Ora rilancia genera.py: le àncore si riagganciano da sole.")
