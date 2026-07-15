# Multi-Object Detection con SIFT, FLANN e Omografia

Questo progetto è un'applicazione Python da linea di comando che cerca più
oggetti all'interno di una o più fotografie.

L'utente fornisce due cartelle:

- una cartella di **immagini di riferimento**, contenente un'immagine per ogni
  oggetto che si vuole riconoscere;
- una cartella di **scene**, contenente le fotografie nelle quali cercare tali
  oggetti.

Il programma confronta automaticamente ogni riferimento con ogni scena,
localizza gli oggetti riconosciuti e salva una nuova versione di ciascuna scena
con bounding box ed etichette.

Un possibile caso d'uso è il riconoscimento di libri appoggiati su una
scrivania: nella cartella dei riferimenti si inseriscono le immagini delle
singole copertine, mentre nella cartella delle scene si inseriscono le foto
della scrivania. Il risultato è una copia della scena sulla quale ogni libro
riconosciuto è evidenziato con il proprio nome.

## Esempio di risultato

Aggiungere un'immagine di esempio in:

```text
docs/images/example_output.png
```

Il file verrà mostrato automaticamente nel README:

<p align="center">
  <img
    src="docs/images/example_output.png"
    alt="Esempio di scena elaborata"
    width="900"
  >
</p>

---

## Come funziona

Il progetto usa tecniche classiche di computer vision e non richiede alcun
addestramento.

Per ogni immagine di riferimento vengono estratti punti caratteristici e
descrittori tramite **SIFT**. Gli stessi descrittori vengono calcolati sulla
scena e confrontati tramite **FLANN**.

Il confronto produce molti match candidati. Il **Lowe ratio test** elimina
quelli ambigui, mantenendo soltanto le corrispondenze nelle quali il miglior
match è nettamente più convincente del secondo.

Quando rimane un numero sufficiente di corrispondenze, il programma tenta di
stimare un'omografia con **RANSAC**. L'omografia descrive la trasformazione
prospettica che porta il riferimento nella sua posizione all'interno della
scena. I quattro angoli del riferimento vengono quindi proiettati nella scena
per costruire la bounding box.

La ricerca multi-oggetto avviene in più passaggi:

1. tutti i riferimenti vengono cercati nella scena;
2. le detection sovrapposte vengono filtrate;
3. gli oggetti trovati vengono mascherati;
4. la ricerca viene ripetuta sulla scena modificata.

Questo permette di trovare sia oggetti diversi sia più istanze dello stesso
oggetto.

L'approccio funziona particolarmente bene con oggetti ricchi di dettagli e
approssimativamente planari, ad esempio:

- copertine di libri;
- confezioni;
- poster;
- etichette;
- documenti;
- loghi e prodotti con texture riconoscibili.

Può essere meno efficace con superfici uniformi, oggetti fortemente
deformabili, immagini molto sfocate, oggetti minuscoli oppure cambi di
prospettiva estremi.

---

# Preparazione del dataset

Una struttura tipica è:

```text
dataset/
├── references/
│   ├── delitto_e_castigo.jpg
│   ├── la_metamorfosi.png
│   ├── brevi_interviste.jpeg
│   └── ...
└── scenes/
    ├── scrivania_01.jpg
    ├── scrivania_02.jpg
    └── ...
```

Il nome del file di riferimento viene usato come etichetta. L'estensione viene
rimossa e gli underscore vengono convertiti in spazi:

```text
delitto_e_castigo.jpg
```

diventa:

```text
delitto e castigo
```

Non è necessario numerare i file.

Sono supportati i formati:

```text
.png  .jpg  .jpeg  .bmp  .tif  .tiff  .webp
```

Le immagini devono trovarsi direttamente nelle cartelle indicate. Le
sottocartelle non vengono analizzate ricorsivamente.

---

# Installazione

Il progetto richiede Python 3.10 o successivo.

Aprire un terminale nella cartella principale del progetto, quella che contiene
`detect.py`, `requirements.txt`, `pyproject.toml` e la cartella `src`.

È consigliato usare un ambiente virtuale.

## Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

## Windows Prompt dei comandi

```bat
py -m venv .venv
.venv\Scripts\activate.bat
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

## macOS e Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

Le dipendenze principali sono OpenCV, NumPy e Matplotlib.

---

# Primo utilizzo

Il comando minimo richiede soltanto le cartelle dei riferimenti, delle scene e
dell'output:

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output
```

Su Windows PowerShell lo stesso comando può essere scritto così:

```powershell
py detect.py `
  --references ".\dataset\references" `
  --scenes ".\dataset\scenes" `
  --output ".\output"
```

Il programma:

1. carica tutte le immagini di riferimento;
2. carica tutte le scene;
3. esegue la detection su ogni scena;
4. salva una scena annotata per ogni immagine di input;
5. genera `detections.csv`.

L'output avrà una struttura simile a:

```text
output/
├── scrivania_01_detected.png
├── scrivania_02_detected.png
└── detections.csv
```

Anche quando non viene trovato alcun oggetto, la scena viene comunque salvata.

---

# Esempi di utilizzo

## 1. Esecuzione standard

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output
```

Questa configurazione usa:

- cutoff pari a `40`;
- nessun preprocessing;
- Lowe ratio pari a `0.7`;
- soglia RANSAC pari a `5.0`;
- output in formato figura con assi e coordinate.

È il punto di partenza consigliato quando non si conoscono ancora i parametri
adatti al proprio dataset.

## 2. Detection più permissiva

Se alcuni oggetti reali non vengono rilevati, si può abbassare il cutoff:

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output_cutoff_20 \
  --cutoff 20
```

Con `--cutoff 20` il programma tenta l'omografia già a partire da 20 good
match. Questo può recuperare oggetti piccoli o difficili, ma può anche
aumentare i falsi positivi.

È preferibile non abbassarlo alla cieca: la modalità di debug descritta più
avanti permette di vedere quanti match vengono realmente prodotti.

## 3. Scene con poco contrasto

Quando le immagini di riferimento sono nitide ma le scene hanno illuminazione
irregolare o contrasto debole, si può provare il preprocessing CLAHE:

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output_clahe \
  --preprocess clahe
```

Il CLAHE viene applicato soltanto alla copia della scena usata per la
detection. L'immagine annotata viene sempre costruita sulla scena originale.

Non è detto che CLAHE migliori ogni dataset. È utile confrontare i risultati
con e senza preprocessing.

## 4. Analisi dei match prima di scegliere il cutoff

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output_debug \
  --debug-matches
```

Oltre alle immagini annotate e a `detections.csv`, verrà creato:

```text
match_debug.csv
```

Questo file contiene il numero di keypoint e good match per ogni coppia
riferimento-scena.

Un possibile flusso di calibrazione è:

1. eseguire il programma con `--debug-matches`;
2. aprire `match_debug.csv`;
3. osservare quanti match producono le coppie corrette;
4. osservare quanti match producono le coppie errate;
5. scegliere un cutoff che separi il più possibile i due gruppi.

Per esempio, se i riferimenti realmente presenti producono tra 28 e 70 match,
mentre quelli assenti rimangono quasi sempre sotto 12, un cutoff tra 18 e 25
può essere un buon punto di partenza.

## 5. Salvare una figura come quella mostrata nel notebook

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output \
  --render-mode figure \
  --figure-dpi 200
```

La modalità `figure` salva:

- l'intera scena;
- bounding box ed etichette;
- margini;
- assi e coordinate in pixel.

`--figure-dpi 200` aumenta la definizione rispetto al valore predefinito di
150 DPI.

## 6. Salvare soltanto l'immagine annotata

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output_raw \
  --render-mode image
```

Questa modalità non aggiunge assi o margini. L'immagine risultante conserva la
stessa risoluzione della scena originale.

## 7. Configurazione completa

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output \
  --cutoff 25 \
  --preprocess none \
  --ratio 0.7 \
  --ransac-threshold 5.0 \
  --iou-threshold 0.5 \
  --max-iterations 50 \
  --debug-matches \
  --render-mode figure \
  --figure-dpi 180
```

Questo esempio esplicita tutte le opzioni disponibili ed è utile come base per
uno script o per una pipeline automatizzata.

---

# Opzioni della linea di comando

Per vedere l'elenco direttamente dal programma:

```bash
python detect.py --help
```

## `--references`

```bash
--references PATH
```

Parametro obbligatorio. Indica la cartella che contiene le immagini degli
oggetti da cercare.

Esempio:

```bash
--references ./dataset/references
```

Tutti i file immagine validi presenti nella cartella vengono caricati. Le
feature SIFT dei riferimenti vengono calcolate una sola volta e riutilizzate
per tutte le scene.

## `--scenes`

```bash
--scenes PATH
```

Parametro obbligatorio. Indica la cartella delle immagini da analizzare.

Esempio:

```bash
--scenes ./dataset/scenes
```

Ogni file produce una scena annotata separata.

## `--output`

```bash
--output PATH
```

Parametro obbligatorio. Indica la cartella nella quale salvare risultati e
report.

Esempio:

```bash
--output ./output
```

Se la cartella non esiste viene creata automaticamente.

## `--cutoff`

```bash
--cutoff N
```

Valore predefinito:

```text
40
```

Definisce il numero minimo di good match necessario per tentare la stima
dell'omografia.

Un valore basso rende il sistema più permissivo:

```bash
--cutoff 15
```

Questo può aiutare con oggetti piccoli, parzialmente visibili o con pochi
dettagli, ma aumenta il rischio di falsi positivi.

Un valore alto rende il sistema più selettivo:

```bash
--cutoff 60
```

Questo riduce i candidati deboli, ma può perdere oggetti realmente presenti.

Il superamento del cutoff non implica automaticamente una detection. I match
devono anche essere geometricamente coerenti e permettere a RANSAC di stimare
un'omografia valida.

## `--preprocess`

```bash
--preprocess none
```

oppure:

```bash
--preprocess clahe
```

Valore predefinito:

```text
none
```

`none` usa le scene senza modificarle.

`clahe` migliora localmente il contrasto del canale di luminosità. Può essere
utile con ombre, illuminazione disomogenea o immagini poco contrastate.

Le immagini di riferimento non vengono preprocessate.

CLAHE non è sempre vantaggioso: su scene già nitide può introdurre dettagli
artificialmente enfatizzati e modificare il numero dei match.

## `--ratio`

```bash
--ratio VALUE
```

Valore predefinito:

```text
0.7
```

Il parametro controlla il Lowe ratio test. Per ogni descrittore, FLANN trova i
due vicini più prossimi. Il match migliore viene accettato soltanto se è
sufficientemente migliore del secondo.

Un valore più basso è più severo:

```bash
--ratio 0.6
```

Vengono conservati meno match, generalmente più distintivi.

Un valore più alto è più permissivo:

```bash
--ratio 0.8
```

Vengono conservati più match, ma aumenta la probabilità di corrispondenze
ambigue.

Intervalli pratici da provare:

```text
0.60 - 0.65   molto selettivo
0.70          valore iniziale consigliato
0.75 - 0.80   più permissivo
```

Conviene regolare `ratio` e `cutoff` insieme. Aumentare il ratio produce in
genere più good match, quindi può richiedere un cutoff più alto.

## `--ransac-threshold`

```bash
--ransac-threshold VALUE
```

Valore predefinito:

```text
5.0
```

È la soglia di errore di riproiezione, espressa in pixel, usata durante la
stima dell'omografia.

Con un valore basso:

```bash
--ransac-threshold 3.0
```

RANSAC accetta soltanto punti molto coerenti con la trasformazione stimata.

Con un valore più alto:

```bash
--ransac-threshold 8.0
```

la stima tollera più rumore e imprecisione, ma può accettare corrispondenze
meno affidabili.

In genere conviene modificare questo parametro solo dopo aver osservato che i
match sono plausibili ma l'omografia viene spesso rifiutata o produce box
instabili.

## `--iou-threshold`

```bash
--iou-threshold VALUE
```

Valore predefinito:

```text
0.5
```

Controlla quando due bounding box vengono considerate sovrapposte.

La IoU, Intersection over Union, misura il rapporto tra l'area di
sovrapposizione e l'area complessiva dei due box.

Con un valore basso:

```bash
--iou-threshold 0.3
```

la rimozione delle detection sovrapposte è più aggressiva.

Con un valore alto:

```bash
--iou-threshold 0.8
```

più box vicini possono essere mantenuti.

Se lo stesso oggetto viene disegnato più volte quasi nella stessa posizione,
conviene abbassare la soglia. Se due oggetti reali molto vicini vengono
erroneamente fusi, può essere utile aumentarla.

## `--max-iterations`

```bash
--max-iterations N
```

Valore predefinito:

```text
50
```

La multi-object detection lavora per iterazioni. Dopo ogni passaggio gli
oggetti trovati vengono mascherati e la ricerca ricomincia.

Il processo termina quando non vengono trovati altri oggetti oppure quando
raggiunge il limite indicato.

Un esempio più prudente:

```bash
--max-iterations 15
```

Un limite più basso riduce il tempo massimo di elaborazione e protegge da
detection ripetitive. Un limite più alto può essere necessario in scene che
contengono molte istanze.

## `--debug-matches`

```bash
--debug-matches
```

È un flag: non richiede un valore.

Quando è presente, il programma genera `match_debug.csv`.

Il report contiene, per ogni coppia riferimento-scena:

- numero di keypoint del riferimento;
- numero di keypoint della scena;
- numero di good match;
- indicazione del superamento del cutoff.

È l'opzione più utile per capire perché un oggetto non viene rilevato e per
calibrare `--cutoff` e `--ratio`.

Il report rappresenta il confronto con la scena completa iniziale. Non descrive
tutte le successive iterazioni dopo il mascheramento.

## `--render-mode`

```bash
--render-mode figure
```

oppure:

```bash
--render-mode image
```

Valore predefinito:

```text
figure
```

`figure` usa Matplotlib e salva una rappresentazione simile a quella del
notebook, con margini, assi e coordinate.

`image` usa OpenCV e salva il solo raster annotato, senza assi. Questa modalità
è preferibile quando il file deve essere utilizzato successivamente da un altro
programma.

## `--figure-dpi`

```bash
--figure-dpi N
```

Valore predefinito:

```text
150
```

Controlla la risoluzione delle figure salvate in modalità `figure`.

Esempi:

```text
100   file più leggero
150   valore predefinito
200   immagine più definita
300   adatto a documenti o stampe, ma più pesante
```

Non produce alcun effetto quando si usa:

```bash
--render-mode image
```

---

# Interpretare i risultati

## `detections.csv`

Il file contiene una riga per ogni istanza rilevata.

Le colonne principali sono:

- `scene`: file della scena;
- `reference`: nome dell'oggetto riconosciuto;
- `instance`: numero progressivo dell'istanza dello stesso oggetto;
- `center_x`, `center_y`: centro della bounding box;
- `width_px`, `height_px`: dimensioni approssimative del box;
- `good_matches`: match sopravvissuti al Lowe ratio test;
- `ransac_inliers`: match coerenti con l'omografia.

Il numero di `ransac_inliers` è spesso più significativo del solo numero di
good match. Per esempio, 35 good match con 5 inlier sono meno convincenti di 22
good match con 18 inlier.

## `match_debug.csv`

Viene creato soltanto con `--debug-matches`.

Serve principalmente per capire la separazione tra riferimenti presenti e
assenti. Se entrambe le categorie producono numeri simili, modificare soltanto
il cutoff potrebbe non essere sufficiente: può essere necessario migliorare i
riferimenti, regolare il ratio o verificare la qualità delle scene.

---

# Una procedura pratica di calibrazione

Per un nuovo dataset è consigliato partire con:

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./calibration_output \
  --cutoff 20 \
  --debug-matches \

