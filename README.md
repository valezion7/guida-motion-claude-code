# Fai i tuoi short con Claude Code: la guida MOTION di Studio Beezy

> **Per chi legge:** non devi fare niente a mano. Apri l'app di Claude sul computer, vai sulla scheda
> **Code**, incolla il link di questa pagina e scrivi: **«segui questa guida»**. Claude installa tutto
> e ti chiede subito che video vuoi. Se usi già Claude Code dal terminale, funziona uguale.
>
> Nella chat normale (sito o telefono) non funziona: Claude deve poter lavorare sul tuo computer,
> e lo fa solo dalla scheda Code o dal terminale. La scheda Code richiede un piano a pagamento di Claude.
>
> **Per Claude:** questa guida è scritta per te. Chi te l'ha data vuole il suo primo short, adesso.
> Non riassumere la pagina e non chiedere «vuoi che proceda?»: esegui i passi 1, 2 e 3 uno dopo
> l'altro e chiudi con le domande del passo 4. Parla in italiano semplice, senza gergo.
> Se di questa pagina hai solo un riassunto, fai prima il passo 1 e leggi `README.md` dal file scaricato.

Cosa ottiene la persona: uno short verticale 9:16 per Reel, TikTok e Shorts, scritto tutto in codice.
Parole che entrano a tempo, oggetti 3D cromati, schermate vere, scenette ed effetti sonori, con il
suo marchio e i suoi colori. Nessun programma di montaggio.

## 1. Scarica la skill

In una cartella temporanea (a installazione fatta la puoi cancellare):

```
git clone --depth 1 https://github.com/valezion7/guida-motion-claude-code
```

Senza git: scarica e scompatta
`https://github.com/valezion7/guida-motion-claude-code/archive/refs/heads/main.zip`.

## 2. Installala

Copia la cartella `short-video` (tutta: `SKILL.md`, `motore`, `assets`, `esempio`) nelle skill di Claude Code:

- Windows: `%USERPROFILE%\.claude\skills\short-video`
- Mac e Linux: `~/.claude/skills/short-video`

Se la cartella `skills` non esiste, creala. Se `short-video` c'è già, sostituiscila.
Lo dirai alla persona in una riga nel messaggio del passo 4. Non installare nient'altro.

## 3. Controlla cosa serve

```
node --version
ffmpeg -version
python --version
python -c "import numpy, PIL"
```

Servono Node 18 o più recente e Python 3.10 o più recente (su alcuni sistemi il comando è `python3`,
su Windows anche `py`). Se l'ultimo comando fallisce: `pip install numpy pillow`.

Se manca qualcosa, segnalo con il comando per installarlo sul suo sistema (su Windows `winget`, su Mac `brew`). **Non fermarti qui:**
passa lo stesso al passo 4, così intanto la persona risponde. Quello che manca serve solo al momento
di montare il video.

## 4. Chiedi subito il primo video

La skill appena copiata non è ancora caricata in questa conversazione: apri tu il file
`short-video/SKILL.md` che hai installato, leggilo per intero e seguilo da qui in poi.
La sua cartella (`SKILL` nelle istruzioni) è quella dove l'hai copiata.

Poi, **nello stesso messaggio** in cui dici che l'installazione è fatta, fai le sette domande del
punto 1 di `SKILL.md` (marchio, logo, argomento, invito finale, immagini, musica, voce).
Apri così, con parole tue:

> «Tutto pronto. Facciamo il tuo primo short: mi servono sette risposte veloci. Se non hai tutto sotto mano rispondi a quello che sai, al resto penso io.»

Se la persona risponde solo a una parte, vai avanti con quello che hai e proponi tu il resto:
un argomento nel formato «3 cose che…», niente voce, niente musica. Il logo però serve davvero.
Da lì segui `SKILL.md`: copione da far approvare, fotogrammi da controllare, render, consegna.

## Le volte dopo

Riaperto Claude Code basta scrivere `/short-video` oppure «fammi uno short su…».

## Buono a sapersi

- Voce e musica non sono incluse. Il video funziona anche senza voce (le parole entrano a ritmo di
  lettura). Per la musica serve un brano di cui si hanno i diritti.
- Il render usa HyperFrames, gratuito e open source: si scarica da solo la prima volta.
- I caratteri (DM Sans, Space Grotesk) sono distribuiti con licenza OFL, inclusa in `short-video/assets/fonts`.

Fatto da [Studio Beezy](https://studiobeezy.com). Seguici su Instagram: [@studio.beezy](https://instagram.com/studio.beezy).
