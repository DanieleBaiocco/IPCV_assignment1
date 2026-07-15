# Multi-object detection — refactoring OOP

Versione object-oriented del precedente `detect.py` monolitico.
La pipeline algoritmica resta la stessa:

1. SIFT estrae keypoint e descrittori;
2. FLANN 2-NN applica il Lowe ratio test;
3. RANSAC stima l'omografia;
4. `SinglePassDetector` corrisponde alla precedente Track A;
5. `MultiObjectDetector` corrisponde alla Track B e richiama iterativamente la Track A;
6. gli oggetti già trovati vengono mascherati per cercare ulteriori istanze.

## Struttura

```text
multi_object_detection_oop/
├── detect.py                         # wrapper compatibile
├── pyproject.toml
├── requirements.txt
├── README.md
├── src/
│   └── multi_object_detection/
│       ├── __main__.py               # python -m multi_object_detection
│       ├── application.py            # orchestrazione del caso d'uso
│       ├── cli.py                    # argparse e gestione errori
│       ├── config.py                 # DetectionConfig
│       ├── models.py                 # ImageAsset, ImageFeatures, Detection
│       ├── detection/
│       │   ├── single_pass_detector.py
│       │   └── multi_object_detector.py
│       ├── features/
│       │   ├── extractor.py          # SIFT
│       │   └── matcher.py            # FLANN
│       ├── geometry/
│       │   ├── boxes.py
│       │   └── homography.py
│       ├── io/
│       │   └── image_loader.py
│       ├── output/
│       │   ├── annotator.py
│       │   ├── exporters.py
│       │   ├── exporter_factory.py
│       │   └── report_writer.py
│       └── preprocessing/
│           ├── factory.py
│           └── preprocessors.py
└── tests/
    └── test_box_geometry.py
```

## Ruoli delle classi

- `DetectionApplication`: orchestra caricamento, detection e output.
- `ImageLoader`: scopre e carica i file immagine.
- `ScenePreprocessor`: Strategy astratta; implementazioni `NoOpPreprocessor` e `ClahePreprocessor`.
- `SiftFeatureExtractor`: estrae le feature SIFT.
- `FlannMatcher`: esegue 2-NN e Lowe ratio test.
- `HomographyEstimator`: stima e valida l'omografia RANSAC.
- `SinglePassDetector`: ricerca una possibile istanza per ciascun riferimento e rimuove sovrapposizioni.
- `MultiObjectDetector`: ripete il single-pass e maschera le detection già trovate.
- `SceneAnnotator`: disegna box ed etichette sulla scena originale.
- `SceneExporter`: Strategy per il formato di salvataggio.
- `MatplotlibSceneExporter`: salva una figura con margini, assi e coordinate.
- `RawImageExporter`: salva il solo raster OpenCV.
- `CsvReportWriter`: genera `detections.csv` e, opzionalmente, `match_debug.csv`.

Le feature dei riferimenti sono calcolate una sola volta e riutilizzate; quelle della scena vengono ricalcolate a ogni iterazione perché la scena mascherata cambia.

## Installazione

### Windows

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -e .
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

L'installazione `-e .` installa anche le dipendenze e abilita sia
`python -m multi_object_detection` sia il comando `multi-object-detect`.
Per usare soltanto il wrapper `python detect.py` è sufficiente anche:

```bash
python -m pip install -r requirements.txt
```

## Esecuzione

Sono disponibili tre forme equivalenti.

### Modulo Python

```bash
python -m multi_object_detection \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output \
  --cutoff 25
```

### Comando installato

```bash
multi-object-detect \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output \
  --cutoff 25
```

### Wrapper `detect.py`

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output \
  --cutoff 25
```

Il wrapper aggiunge automaticamente la cartella `src` al Python path: dopo aver installato `requirements.txt`, può essere eseguito direttamente senza installazione editable.

## Opzioni

```text
--references PATH
--scenes PATH
--output PATH
--cutoff N
--preprocess none|clahe
--ratio FLOAT
--ransac-threshold FLOAT
--iou-threshold FLOAT
--max-iterations N
--debug-matches
--render-mode figure|image
--figure-dpi N
```

Il preprocessing, quando selezionato, viene applicato solo all'immagine usata per la detection. L'immagine annotata salvata è sempre la scena originale.

La modalità predefinita è `--render-mode figure`: ogni scena viene salvata come una figura Matplotlib con margini, assi e coordinate in pixel, come nella visualizzazione del notebook. Per ottenere il vecchio PNG senza assi usare `--render-mode image`.

## Output

```text
output/
├── scena_1_detected.png
├── scena_2_detected.png
├── detections.csv
└── match_debug.csv       # solo con --debug-matches
```

Il nome del file di riferimento diventa l'etichetta: `coca_cola.png` viene mostrato come `coca cola`.

## Test

Installare pytest, quindi:

```bash
python -m pip install pytest
pytest
```


## Esportazione della scena

La modalità predefinita produce una figura simile a quella mostrata nel
notebook:

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output \
  --render-mode figure \
  --figure-dpi 150
```

La figura contiene:

- l'intera scena originale;
- tutte le bounding box e le etichette;
- margini bianchi;
- assi e coordinate in pixel.

Per salvare soltanto i pixel della scena annotata, senza assi:

```bash
python detect.py \
  --references ./dataset/references \
  --scenes ./dataset/scenes \
  --output ./output \
  --render-mode image
```
