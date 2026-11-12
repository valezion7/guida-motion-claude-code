# Esempio completo: copia questa cartella, cambia marchio, battute e quadri. Q(...) è un dizionario.
MARCA = dict(
    nome="Orto Verde",            # come si chiama l'attività
    sito="ortoverde.example",     # la scritta piccola in basso
    colore="#0f766e",             # colore d'accento (al posto dell'arancio)
    logo="logo.png",              # PNG, meglio quadrato; compare nel finale
    musica=None,                  # percorso di un brano di cui hai i diritti, oppure None
)
OPZIONI = dict(wow=1, passi=3)    # passi = tacche della barra in alto (una per punto dell'elenco)

# Il parlato, una battuta per riga. Senza voce diventa il ritmo di lettura; con la voce sono i testi da registrare.
BATTUTE = [
    "Tre motivi per fare la spesa da Orto Verde, anche se di solito vai al supermercato!",
    "Uno: la verdura è raccolta la mattina stessa. Niente frigo, niente viaggi di una settimana.",
    "Due: ordini dal telefono con due tocchi, e passi a ritirare quando vuoi.",
    "Tre: spendi meno di quanto pensi. Una cassetta mista costa dodici euro, e basta per una settimana!",
    "Prova Orto Verde!",
]

# I quadri. t = 0 per il primo, poi la PAROLA con cui il quadro deve cominciare (àncora): la cerca nel parlato.
QUADRI = [
    Q(t=0.0, tipo="titolo", props=["scintille", "moneta", "lente", "libro"], top=640, righe=["g:3 motivi", "per fare la spesa da", "tag:Orto Verde"]),
    Q(t="anche", tipo="grande", prop="lente", lato=300, righe=["s:anche se di solito", "g:vai al", "g:^supermercato!^"]),
    Q(t="Uno:", tipo="lista", lampo=1, passo=1, segno="✕", prop="clessidra",
      gag=[("timbro", "settimana.", "FRESCA", 700, 1130, 8)],   # sotto l'elenco: in alto a destra c'è l'oggetto
      righe=["s:Uno: raccolta", "m:la mattina", "m:stessa."], voci=[("frigo,", "niente frigo"), ("viaggi", "niente viaggi di una settimana")]),
    Q(t="Due:", tipo="term", lampo=1, passo=2, alt=330,
      term=[("ordini", "> una cassetta mista, grazie"), ("ritirare", "✓ pronta dalle 17")],
      righe=["s:Due: ordini dal telefono", "con *due tocchi,*", "m:e passi ^quando vuoi.^"]),
    Q(t="Tre:", tipo="grande", lampo=1, passo=3, prop="salvadanaio", lato=300,
      gag=[("conta", "cassetta", 30, 12, "€ ", 1160), ("pioggia", "dodici", "moneta")],
      righe=["s:Tre: spendi", "g:meno", "di quanto *pensi.*"]),
    Q(t="euro,", tipo="chips", chips=[("euro,", "Zucchine", None), ("e", "Pomodori", None), ("basta", "Insalata", None), ("una", "Uova", None)],
      righe=["settimana!", "m:una cassetta,", "m:^una settimana.^"]),
    Q(t="Prova", tipo="marchio", lampo=1, righe=["s:Prova", "g:Orto Verde", "s:ortoverde.example", "m:^la spesa di stamattina^"]),
]
