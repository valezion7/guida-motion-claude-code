---
name: short-video
description: Crea short verticali 9:16 per i social (Reel, TikTok, Shorts) tutti in codice, nello stile «fondo chiaro» di Studio Beezy - parole che entrano a tempo, oggetti 3D cromati, schermate vere, scenette ed effetti sonori. Da usare quando l'utente chiede un video breve, uno short, un reel o un video per i social per il proprio marchio.
---

# Short video «fondo chiaro»

Fai uno short verticale (1080×1920, 30 fps) scritto interamente in codice e renderizzato con HyperFrames.
Tu scrivi un solo file, `video.py`; il motore di questa skill fa il resto. Non scrivere HTML a mano.

La cartella di questa skill è quella che contiene questo file: sotto la chiamo `SKILL`.

## 0 · Controlla cosa serve (una volta)

Controlla uno per volta se sul computer c'è tutto quello che serve:

```
node --version
python --version
ffmpeg -version
ffprobe -version
python -c "import numpy, PIL"
```

Servono **Node 18 o più recente**, **Python 3.10 o più recente** (su alcuni sistemi il comando è `python3`,
su Windows anche `py`), **ffmpeg** (con ffprobe) e le librerie Python **numpy** e **pillow**.
Su Windows, se `python` apre il Microsoft Store invece di rispondere, Python non è installato.

Poi fai alla persona un resoconto chiaro, una riga per strumento: «c'è» oppure «manca».
Per ogni cosa che manca dille cos'è in parole semplici e chiedile di installarla, offrendoti di farlo tu
se ti dà l'ok. I comandi:

| Manca | Windows | Mac | Linux (Debian, Ubuntu) |
|---|---|---|---|
| Node | `winget install OpenJS.NodeJS.LTS` | `brew install node` | `sudo apt install nodejs npm` |
| Python | `winget install Python.Python.3.12` | `brew install python` | `sudo apt install python3 python3-pip` |
| ffmpeg | `winget install Gyan.FFmpeg` | `brew install ffmpeg` | `sudo apt install ffmpeg` |
| numpy, pillow | `pip install numpy pillow` | `pip3 install numpy pillow` | `pip3 install numpy pillow` |

Su Mac, se manca `brew`, mandala su https://brew.sh. Dopo un'installazione spesso bisogna chiudere e
riaprire l'app di Claude (o il terminale) perché il comando nuovo venga trovato: diglielo.
A installazione fatta rilancia i controlli e conferma che ora c'è tutto. Non montare il video finché
manca qualcosa.

Intanto fai lo stesso le domande del punto 1: quello che manca serve solo dal punto 4 in poi.
HyperFrames si scarica da solo al primo render (`npx hyperframes@0.9.26`): è gratuito e open source.

## 1 · Chiedi all'utente (prima di scrivere qualunque cosa)

Fai queste domande tutte insieme, in un solo messaggio. Senza queste risposte il video esce generico.

1. **Marchio**: come si chiama l'attività, il sito, il colore principale (un codice tipo `#0f766e`, oppure «prendilo dal sito»).
2. **Logo**: un file PNG (meglio quadrato, fondo trasparente). L'utente può trascinarlo nella finestra o dirti dove si trova sul computer; vale lo stesso per immagini e musica. Se non ce l'ha, prendilo dal suo sito oppure aspetta che te lo dia: senza logo non si fa il finale. Non usare mai `esempio/logo.png` per il video di un utente.
3. **Di cosa parla il video**: l'argomento e a chi parla. Aiutalo con un formato che funziona: «3 cose che puoi fare con…», «5 errori che…», «3 modi per…», «Quello che nessuno ti dice su…».
4. **Cosa deve fare chi guarda, alla fine**: seguire, commentare una parola, andare sul sito.
5. **Immagini vere**: schermate del prodotto o del sito, foto. Se ha un sito puoi catturarle tu. Non inventare schermate finte.
6. **Musica**: un brano di cui ha i diritti (file mp3). Se non ne ha, il video esce con i soli effetti sonori: diglielo.
7. **Voce**: sì o no. Senza voce il video funziona lo stesso (le parole entrano a ritmo di lettura). Con la voce servono le battute registrate, oppure la sua chiave ElevenLabs.

## 2 · Scrivi il copione e fallo approvare

Il copione è la lista `BATTUTE`: una battuta per riga, 5-9 battute, 35-70 secondi in tutto.

- Tono umano, da persona che spiega a un amico. Frasi con slancio, non elenchi puntati letti ad alta voce.
- La prima battuta è l'aggancio: dice subito cosa si guadagna a guardare.
- Struttura a punti numerati («Uno: … Due: … Tre: …»): ogni punto un beneficio concreto, con un dettaglio vero.
- L'ultima battuta è l'invito («Prova …», «Segui …», «Commenta …»).
- Scrivi solo cose vere. Numeri, prezzi e funzioni li verifichi (sul sito dell'utente o chiedendo): niente promesse di guadagni o di tempi inventate.
- I termini ormai d'uso restano in inglese (vibe coder, render, prompt).

**Mostra il copione all'utente e aspetta il suo sì prima di montare.** Cambiare il testo dopo costa un altro render.

## 3 · Prepara la cartella del video

Creala in un posto che l'utente ritrova (il Desktop o Documenti, mai una cartella di sistema), con un nome parlante, e digli dov'è. Qui sotto la chiamo `mio-video`.

```
mio-video/
  video.py        ← lo scrivi tu (parti da SKILL/esempio/video.py)
  logo.png        ← il logo dell'utente
  immagini/       ← schermate e foto (qualunque misura: il motore le adatta)
  oggetti/        ← facoltativo: altri PNG trasparenti da usare come oggetti
  musica.mp3      ← facoltativo
```

### Com'è fatto `video.py`

Tre cose obbligatorie: `MARCA`, `BATTUTE`, `QUADRI`. `OPZIONI` è facoltativo: `wow=1` (animazioni spinte, già attivo se non lo scrivi) e `passi=N` (N tacche nella barra in alto: una per ogni punto numerato del copione).
`Q` non va importato: lo fornisce il motore, ed è solo un modo comodo di scrivere un dizionario.
Guarda `SKILL/esempio/video.py`: è un video completo e funzionante.

**Ogni quadro** è `Q(t=…, tipo=…, righe=[…], …)` e dura fino all'inizio del quadro dopo.

- `t`: `0.0` per il primo. Per gli altri **la parola con cui il quadro comincia** (`t="Uno:"`): si chiama àncora. Così i tempi restano giusti anche se poi aggiungi la voce.
  - **Come viene cercata**: maiuscole, accenti e punteggiatura non contano, e per le parole più lunghe di 3 lettere contano solo le prime 4. Quindi `"torte"` aggancia anche «torta» e `"Ordina"` aggancia anche «ordini».
  - **Da dove parte la ricerca**: l'àncora `t` di un quadro si cerca dopo l'inizio del quadro precedente. Le àncore dentro un quadro (`voci`, `term`, `chips`, `barre`, `gag`, `a`, `mano`, `coda`) si cercano dall'inizio di quel quadro, e in `voci`, `term`, `chips`, `barre` ognuna dopo la precedente.
  - Per questo scegli una parola che non compaia (nemmeno con le stesse 4 lettere iniziali) tra il punto di partenza e il punto che vuoi.
- `righe`: il testo a schermo, una riga per elemento. Le parole entrano quando vengono dette, quindi **usa le stesse parole delle battute, nello stesso ordine** (puoi saltarne, non inventarne troppe).
  - prefisso `s:` riga piccola grigia · nessun prefisso: normale · `m:` media · `g:` gigante · `tag:` targhetta nera
  - `*così*` grassetto nero · `^così^` nel colore del marchio
  - Massimo 4 righe per quadro, 2-5 parole per riga. Una riga `g:` regge 10-12 lettere.
- `lampo=1`: lampo bianco all'ingresso (usalo all'inizio di ogni punto numerato). `passo=N`: accende la tacca N della barra in alto.

**Tipi di quadro**

| tipo | cosa mostra | parametri |
|---|---|---|
| `titolo` | apertura con 4 oggetti agli angoli | `props=[4 oggetti]`, `top=640` |
| `grande` | oggetto in alto e testo grande sotto | `prop`, `lato=300` (grandezza), `top` |
| `lista` | titolo a sinistra, elenco che entra voce per voce; l'oggetto `prop` sta in alto a destra | `voci=[("àncora", "testo")…]`, `segno="✓"` (o `✕`, `+`, `→`), `prop`, `coda=["àncora", "m:riga", "s:riga"]`: nella coda **solo il primo elemento è un'àncora**, gli altri sono righe che compaiono sotto l'elenco |
| `card` | un'immagine vera in una scheda, testo sotto | `img="nome"` (file in `immagini/`, senza estensione) |
| `cambia` | la scheda si gira e diventa un'altra | `img`, `img2`, `a="àncora del momento"`, `flash=1` per lo scatto di una foto (senza: due click del cursore) |
| `giro` | la scheda scorre tra più immagini, come uno scroll: per mostrare più sezioni dello stesso sito invece della solita home | `imgs=["nome1", "nome2", "nome3"]` (2-4 immagini) |
| `ruba` | da un sito vuoto esce una mano e prende colori e design dal sito accanto (disegnato, stilizzato) | `mano="àncora"`; `img` facoltativo, solo se vuoi una schermata vera al posto del sito disegnato |
| `term` | terminale con righe battute a tastiera | `term=[("àncora", "> testo")…]`, `alt=330`; le righe che iniziano con `✓` compaiono come conferma |
| `chips` | pillole bianche su due colonne, con un nome ciascuna (strumenti, marchi, opzioni) | `chips=[("àncora", "Nome", None)…]`: nome di **12 caratteri al massimo**, meglio in numero pari (2, 4 o 6); il terzo valore è `None`, oppure il nome di un logo SVG messo in `loghi/` nella cartella del video. `righe=["àncora", "riga", "riga"]`: **solo il primo elemento è un'àncora** (quando compare il testo sotto le pillole), gli altri sono righe normali |
| `barre` | tre barre nere con scritto solo «01», «02», «03», per annunciare tre livelli o tre passi; il testo va in `righe`, sotto | `barre=["àncora", "àncora", "àncora"]` |
| `marchio` | finale col logo | `righe=["s:Prova", "g:Nome", "s:sito", "m:^invito^"]` (esattamente 4 righe; l'ultima al massimo 26 caratteri) |

**Oggetti 3D disponibili** (per `prop`, `props`, e per la pioggia): busta, carta, catena, chiave, clessidra, contagocce, database, forbici, fumetto, imbuto, ingranaggi, lente, libro, livelli, luna, molla, moneta, nuvola, salvadanaio, schiocco, schiocco-a, schiocco-b, scintille, scontrino, scudo, spina, squadra, st-arcade, st-blueprint, st-fumetto, st-terminale, tavolozza.
Scegli quelli che c'entrano con la frase. Oggetti dell'utente: PNG trasparenti in `oggetti/`.

**Scenette** (`gag=[…]` dentro un quadro): 2 o 3 in tutto il video, nei punti dove la frase si presta. Ognuna ha già il suo suono.

- `("timbro", "àncora", "TESTO", x, y, rotazione, "#colore")`: un timbro che sbatte. Testo corto, maiuscolo. `x, y` sono il centro del timbro. Rotazione e colore sono facoltativi (se mancano: −8 gradi e il colore del marchio).
- `("conta", "àncora", da, a, "€ ", y)`: un numero che scorre da un valore all'altro.
- `("pioggia", "àncora", "moneta")`: nove oggetti che cadono dall'alto.
- `("fluttua", "àncora", "Z z z", x, y)`: lettere che salgono e svaniscono.
- `("flash", "àncora")`: lampo e scatto di macchina fotografica.

Lo schermo è 1080×1920: `x` da 0 a 1080 (da sinistra), `y` da 0 a 1920 (dall'alto).
**Le coordinate sono quelle prima della centratura**: ogni quadro viene poi spostato in basso (fino a 260 px) per stare al centro, e timbri e contatori si spostano con lui. Dove finiscono davvero lo vedi solo nel fotogramma: controllalo sempre.
Posizioni di partenza che di solito restano libere:

- `lista` con `prop`: l'oggetto occupa l'angolo in alto a destra (x 690-1020, y 230-560), il testo sta a sinistra. Timbro sotto l'elenco, per esempio `x=700, y=1130`.
- `grande`: testo al centro. Timbro o contatore sotto il testo, `y` tra 1100 e 1200.
- `card`, `term`: la scheda sta in alto, il testo sotto. Timbro sull'angolo della scheda (`x=800, y=380`) o contatore a `y=1320`.
- Non scendere mai sotto `y=1250` con il centro di un timbro o di un contatore: più giù c'è la scritta del sito.

## 4 · Genera e controlla i fotogrammi

```
python SKILL/motore/genera.py mio-video
```

Lancialo dalla cartella che contiene `mio-video` (oppure passa il percorso completo). Il progetto pronto finisce in `mio-video/film/`.

Se un'àncora non si trova o manca un file, il messaggio dice quale: correggi `video.py` e rilancia.
Alla fine stampa `FOTOGRAMMI t1,t2,…`. Scattali e **guardali**:

```
cd mio-video/film && npx --yes hyperframes@0.9.26 snapshot --at t1,t2,…
```

Il comando indica una o più immagini riassuntive (`contact-sheet-1.jpg`, `-2.jpg`…): aprile tutte. Se in una griglia un dettaglio è troppo piccolo per giudicare, apri il fotogramma singolo `frame-NN-…png` nella stessa cartella. Se il comando non stampa nessuna immagine, rilancialo senza filtrare l'output e leggi l'errore.
Controlla, quadro per quadro:

- nessun testo tagliato ai bordi o sopra un altro;
- nessuna parola rimasta sfocata (il quadro è troppo corto: accorcia il testo o unisci due quadri);
- timbri e contatori non coprono le parole importanti;
- le immagini sono quelle giuste e leggibili.

Correggi e rigenera finché è pulito. Non renderizzare senza aver guardato.

## 5 · Voce (solo se l'utente la vuole)

Le battute registrate vanno in `mio-video/voce/01.mp3`, `02.mp3`… una per battuta, nello stesso ordine. Poi:

```
pip install faster-whisper
python SKILL/motore/voce.py mio-video
python SKILL/motore/genera.py mio-video
```

Con una chiave ElevenLabs dell'utente (variabile d'ambiente `ELEVENLABS_API_KEY`, mai scritta nei file):
`python SKILL/motore/voce.py mio-video --elevenlabs <ID_VOCE>`.
Dopo la voce ricontrolla i fotogrammi: i tempi cambiano.

## 6 · Render e consegna

```
python SKILL/motore/render.py mio-video
```

Esce `mio-video/video.mp4` (più `anteprima-720p.mp4`). Per rifare solo l'audio: aggiungi `--solo-audio`.
Consegna il file e di' in due righe cosa non hai potuto verificare (di solito: non hai ascoltato l'audio).
Poi chiedi se vuole cambiare qualcosa o farne un altro.

## Errori tipici

- **«àncora non trovata»**: la parola non c'è nelle battute dopo l'inizio del quadro precedente. Scegli una parola che lì compare davvero.
- **«i quadri non sono in ordine»**: un'àncora ha preso una parola più avanti. Scegline una più specifica.
- **Parole che entrano tutte insieme o in ritardo**: le `righe` usano parole diverse dalle battute. Riallineale.
- **Render lento o bloccato**: è normale che ci metta qualche minuto. Non interromperlo.
