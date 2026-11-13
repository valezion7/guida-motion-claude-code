# Short video: la skill di Studio Beezy per Claude Code

Con questa skill chiedi a Claude uno short verticale per i social e lui lo scrive in codice: testi a tempo,
oggetti 3D, schermate vere, scenette ed effetti sonori. Nessun programma di montaggio.

## Cosa ti serve

- [Claude Code](https://claude.com/claude-code)
- Node 18 o più recente, Python 3.10 o più recente, ffmpeg
- Il logo della tua attività in PNG

Se qualcosa manca, Claude te lo dice al primo avvio insieme al comando per installarlo.

## Come si installa

1. Scarica questo repository.
2. Copia la cartella `short-video` dentro la cartella delle skill di Claude Code:
   - Windows: `C:\Users\<tuo nome>\.claude\skills\`
   - Mac e Linux: `~/.claude/skills/`
3. Riapri Claude Code.

Oppure, più semplice: dai a Claude Code il link del repository e scrivi «segui questa guida». Fa tutto lui.

## Come si usa

Scrivi a Claude:

> /short-video voglio un video per la mia attività

Claude ti fa sette domande veloci (marchio, logo, argomento, invito finale, immagini, musica, voce), ti fa approvare il copione e poi monta il video.
Alla fine trovi `video.mp4` nella cartella del progetto.

## Cosa c'è dentro

- `SKILL.md`: le istruzioni che segue Claude
- `motore/`: il generatore
- `assets/`: caratteri e oggetti 3D cromati
- `esempio/`: un video completo da cui partire

## Voce e musica

Il video funziona anche senza voce (le parole entrano a ritmo di lettura). Se la vuoi: una voce gratuita pronta
subito, le tue registrazioni, oppure ElevenLabs a pagamento, che suona più naturale. Per la musica usa un brano di cui hai i diritti.

Oggetti 3D inclusi: busta, carta, catena, chiave, clessidra, contagocce, database, forbici, fumetto, imbuto, ingranaggi, lente, libro, livelli, luna, molla, moneta, nuvola, salvadanaio, scintille, scontrino, scudo, spina, squadra, tavolozza.

Fatto da [Studio Beezy](https://studiobeezy.com).
