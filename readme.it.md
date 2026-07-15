# Multi-Object Detection con SIFT, FLANN e Omografia

Applicazione Python da linea di comando per individuare più oggetti all'interno
di una o più immagini di scena, utilizzando un insieme di immagini di
riferimento.

Il progetto non utilizza una rete neurale addestrata. Il riconoscimento si basa
su tecniche classiche di computer vision:

1. estrazione dei punti caratteristici con **SIFT**;
2. confronto dei descrittori con **FLANN 2-NN**;
3. filtraggio dei match tramite **Lowe ratio test**;
4. stima dell'omografia con **RANSAC**;
5. proiezione del contorno del riferimento sulla scena;
6. mascheramento degli oggetti trovati e ripetizione della ricerca, per
   individuare più oggetti e più istanze dello stesso oggetto.

Tutte le immagini presenti nella cartella dei riferimenti vengono confrontate
con tutte le immagini presenti nella cartella delle scene.

---

## Esempio di output

Salvare una schermata del risultato con il nome:

```text
docs/images/example_output.png
```

Il README la visualizzerà automaticamente qui:

<p align="center">
  <img
    src="docs/images/example_output.png"
    alt="Esempio di scena elaborata con bounding box ed etichette"
    width="900"
  >
</p>

---

## Caratteristiche principali

- rilevamento di più oggetti nella stessa scena;
- rilevamento di più istanze dello stesso riferimento;
- utilizzo automatico di tutti i riferimenti e di tutte le scene;
- nomi dei file di riferimento utilizzati come etichette;
- preprocessing CLAHE opzionale sulle sole scene;
- esportazione delle scene annotate;
- esportazione di un report CSV delle detection;
- report diagnostico opzionale sui good match SIFT;
- architettura object-oriented suddivisa per responsabilità;
- esecuzione da terminale su Windows, macOS e Linux.

---

## Quando funziona meglio

L'approccio basato su SIFT e omografia è particolarmente adatto a oggetti:

- prevalentemente planari, come libri, confezioni, copertine e poster;
- dotati di testo, loghi, spigoli o texture riconoscibili;
- fotografati con una qualità sufficiente;
- visibili almeno in parte nella scena.

Può essere meno efficace con:

- superfici uniformi e prive di dettagli;
- oggetti fortemente deformabili o tridimensionali;
- forti riflessi, sfocatura o illuminazione molto diversa;
- oggetti molto piccoli nella scena;
- occlusioni estese;
- cambiamenti estremi del punto di vista.

---

## Requisiti

- Python **3.10 o successivo**
- `numpy`
- `opencv-python`
- `matplotlib`

Le dipendenze sono elencate in `requirements.txt` e in `pyproject.toml`.

---

## Struttura del dataset

È consigliata una struttura simile alla seguente:

```text
dataset/
├── references/
│   ├── delitto_e_castigo.jpg
│   ├── la_metamorfosi.png
│   ├── brevi_interviste.jpeg
│   └── ...
└── scenes/
    ├── scrivania_01.jpg
    ├── scaffale_01.png
    └── ...
```

Il nome del file di riferimento, senza estensione, viene utilizzato come
etichetta della detection.

Gli underscore vengono convertiti in spazi:

```text
delitto_e_castigo.jpg  ->  delitto e castigo
```

Non è necessario utilizzare numeri nei nomi dei file.

### Formati supportati

```text
.png
.jpg
.jpeg
