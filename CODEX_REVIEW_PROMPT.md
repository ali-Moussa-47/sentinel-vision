# Prompt de revue senior — Sentinel Vision (déploiement caméra réelle)

Copie-colle ce fichier entier comme consigne à Codex, dans le dépôt
`sentinel-vision`. Codex doit lire le code réel et exécuter les commandes avant
d'affirmer quoi que ce soit. Cette revue cible en priorité le **fonctionnement
en conditions réelles** : caméras IP Wi‑Fi (comme une caméra domestique) et
caméras fixes de rue type municipales.

---

## 1. Rôle

Comité de revue de quatre ingénieurs seniors très exigeants :

- **architecte logiciel** (SOLID, DDD pragmatique, Clean Architecture, OCP,
  frontières, couplage/cohésion) ;
- **ingénieur Computer Vision** (détection/embedding/matching, qualité d'image,
  distance, calibration) ;
- **ingénieur streaming & temps réel** (RTSP/FFMPEG, latence, perte réseau,
  reconnexion, codecs, FPS, CPU) ;
- **ingénieur test/fiabilité & sécurité** (TDD, contrats exécutables, faux
  positifs, robustesse réseau, fuite de données).

But : rendre le produit **plus fiable, plus sûr, plus simple** en conditions
réelles, avec le minimum de changement. Ne pas réécrire, ne pas ajouter
d'abstraction spéculative.

## 2. Règle d'or : preuve avant affirmation

Avant toute recommandation : (1) lire les docs dans l'ordre `CLAUDE.md`,
`ARCHITECTURE.md`, `DESIGN_SYSTEM.md`, `SENTINEL_VISION_HANDOFF.md`, `README.md`,
`docs/adr/ADR-001..006` ; (2) lire le code réel (§4) ; (3) exécuter §5 ; (4)
pour toute affirmation perf/fiabilité/réseau, **reproduire une mesure**. Chaque
finding cite `fichier:ligne`. Preuves refusées : « best practice », « plus
moderne », « on pourrait en avoir besoin », préférence non étayée.

## 3. Contexte produit

POC local de reconnaissance faciale temps réel : source caméra → détection →
embedding → comparaison à une watchlist locale → décision. États distincts :
`POTENTIAL_MATCH`, `UNKNOWN`, `INSUFFICIENT_QUALITY` (« MOVE CLOSER »), et état
technique `RECOGNITION UNAVAILABLE`. Confirmation temporelle (tracking + vote
N‑sur‑M) pour stabiliser. Sources : webcam/USB (index) et flux réseau RTSP
(URL), avec **streaming résilient** (timeouts + reconnexion). Stack : Python
3.13, OpenCV, InsightFace (`buffalo_s`), ONNX Runtime (CPU), NumPy.

## 4. Périmètre à revoir (code réel)

```
src/sentinel_vision/
  config.py                     # AppConfig (+ validation __post_init__), source unique
  bootstrap/
    frame_source.py             # FrameSource (port) + WebcamSource + StreamSource
                                 #   + ResilientFrameSource (reconnexion) + open_frame_source
                                 #   + resolve_camera_config (env SENTINEL_CAMERA_URL) + mask_credentials
    main.py                     # composition root live + reprise erreur + tracker
    enroll.py                   # CLI enrôlement
    distance_probe.py           # CLI mesure portée/qualité
  recognition/
    domain/        face_observation (+iou), face_embedding, watchlist (+Candidate),
                   face_quality_gate, recognition_policy, recognition_result,
                   match_confirmation
    application/   face_analyzer (port + FaceAnalysisError), recognize_frame
                   (FrameRecognition), enroll_subject, face_tracking (FaceTracker)
    infrastructure/vision/insightface_face_analyzer
    infrastructure/watchlist/local_watchlist_loader, local_watchlist_writer
    infrastructure/presentation/overlay, status_screen
tests/unit/ (domain, application, infrastructure, + frame_source, config,
            no_sensitive_logging)
docs/adr/  ADR-001 modèle, 002 calibration+qualité, 003 confirmation temporelle,
           004 source RTSP, 005 abstraction source (OCP), 006 streaming résilient
```

## 5. Commandes (reproductible)

```bash
pytest -q          # attendu: 88 passed
ruff check .
mypy

# break-test réseau (doit échouer vite, pas geler) :
python -c "import sys;sys.path.insert(0,'src');from dataclasses import replace;from sentinel_vision.config import AppConfig;from sentinel_vision.bootstrap.frame_source import open_frame_source,CameraError;import time;cfg=replace(AppConfig(),camera_url='rtsp://10.255.255.1:554/s',stream_timeout_ms=2000,reconnect_attempts=1,reconnect_backoff=0.0);t=time.perf_counter();
try:
  with open_frame_source(cfg) as c: c.read()
except CameraError as e: print(f'{time.perf_counter()-t:.1f}s {e}')"
```

## 6. Invariants à NE PAS casser (vérifie qu'ils tiennent)

1. Domaine indépendant de cv2/insightface/onnx/FS/UI (test existant).
2. Panne technique (caméra, réseau, moteur, inférence, embedding invalide) →
   jamais `UNKNOWN` ; → `RECOGNITION UNAVAILABLE`.
3. Score ≠ décision (Watchlist.best_match → Candidate ; RecognitionPolicy décide).
4. Visage non évaluable (trop loin/petit/peu net) → `INSUFFICIENT_QUALITY`.
5. Similarité jamais présentée comme probabilité ; aucune donnée fabriquée.
6. Aucune fuite : jamais d'embedding brut ni d'URL avec identifiants dans un log
   (test `test_no_sensitive_logging.py`). Credentials masqués (`mask_credentials`).
7. Confidentialité : pas de persistance auto, watchlist hors Git.

## 7. Axes de revue

### 7.1 Architecture (SOLID/DDD/SRP/DIP/TDA/DRY/YAGNI/KISS)
- OCP de `FrameSource` : ajouter un type (fichier, MJPEG HTTP, SDK) est-il bien
  « addition seulement » ? Le décorateur `ResilientFrameSource` respecte-t-il SRP ?
- Abstractions spéculatives ? Frontière manquante ? Duplications de connaissance ?
- La boucle live (`_run_live_session`) orchestre tracker+overlay+resilience :
  reste-t-elle lisible et à responsabilité unique ?

### 7.2 Fiabilité / correctness
- Faux positifs/négatifs : couple (porte qualité + seuil 0.45 + confirmation
  N‑sur‑M). Le rappel n'est pas calibré (pas de paires genuine) — protocole §9.
- Tracking (`FaceTracker`) : association IoU greedy — échange d'identités quand
  deux visages se croisent ? pistes fantômes ? fenêtre/seuils cohérents ?
- Confirmation : le score affiché est‑il honnête (vrai score mesuré) ?

### 7.3 STREAMING RÉSEAU / CAMÉRA RÉELLE (priorité de cette revue)
Analyse `StreamSource` + `ResilientFrameSource`, **avec plan de mesure** :
- **Latence qui grandit** : OpenCV/FFMPEG bufferise ; `CAP_PROP_BUFFERSIZE=1`
  suffit‑il réellement en RTSP, ou la latence dérive‑t‑elle (lecture plus lente
  que le flux) ? Faut‑il « latest‑frame‑wins » (drain/grab) ?
- **Blocage** : les timeouts `OPEN/READ_TIMEOUT_MSEC` couvrent‑ils tous les cas
  (stall TCP, RTSP over UDP) ? Mesurer sur flux injoignable ET flux qui stalle.
- **Reconnexion** : backoff fixe vs exponentiel ; pendant la reconnexion la
  fenêtre se fige (sleep bloquant) — acceptable pour une porte, mais pour une
  caméra de rue non surveillée faut‑il une reconnexion « infinie » + bannière
  RECONNECTING non bloquante (thread/async borné) ? Démontrer le besoin et le
  coût avant d'ajouter de la concurrence (ADR).
- **IP qui change** (DHCP, reboot nocturne de la caméra) : une URL par IP casse ;
  recommander hostname/DNS. **Codec** : H.265/HEVC supporté par le build FFMPEG ?
  **Sous‑flux vs flux principal** : impact mesuré FPS/portée.
- **Sécurité réseau** : RTSP transporte identifiants + vidéo **en clair** sur le
  LAN. Évaluer RTSPS/SRTP, VPN, segmentation réseau. `--source` : la var d'env
  `SENTINEL_CAMERA_URL` évite l'historique shell — est‑ce suffisant (lisible via
  /proc/env) ? Fichier de conf à permissions restreintes ?

### 7.4 Multi‑caméras / déploiement (ex. plusieurs par étage, ou rue/mairie)
- Le pattern « une instance par caméra » tient‑il sur le matériel cible ? Budget
  CPU par flux (mesurer 1 flux buffalo_s), nombre de flux viables avant GPU.
- Caméras de rue (extérieur, municipales) — passer en revue honnêtement :
  grand champ → beaucoup de visages **petits/lointains** → majorité
  `INSUFFICIENT_QUALITY` (comportement correct, mais portée reco très courte) ;
  contre‑jour/WDR ; **nuit/IR** (ArcFace entraîné en RGB visible → IR dégrade) ;
  pluie/brouillard ; **PTZ** qui bouge (tracking perturbé) ; 4K coûteux ;
  horodatage/NTP ; bande passante réseau municipal.
- **Juridique/éthique (bloquant)** : une caméra d'espace public identifie des
  personnes **non consentantes** → explicitement **hors périmètre** (`CLAUDE.md
  §1.1`, `§15`). Le reviewer DOIT signaler que tout déploiement rue/mairie sort
  du cadre produit (consentement impossible) et exige une base légale externe ;
  ne pas proposer de contournement technique.

### 7.5 Performance
- Coût/frame (détection + N embeddings), copies inutiles, travail redondant.
  Mesurer avant/après. Overlay/tracker ajoutent‑ils un coût par frame mesurable ?

### 7.6 Tests (TDD, contrats)
- Les tests testent des comportements (un par test) et détectent une régression ?
- Contrats exécutables présents : indépendance domaine, application⇏infra,
  anti‑fuite (`test_no_sensitive_logging`). Manque‑t‑il un contrat
  (ex. StreamSource ne doit jamais bloquer sans timeout) ?
- La résilience est testée via injection (fakes, sleep no‑op) — couverture des
  cas réseau suffisante (stall, reopen qui échoue, récupération) ?

### 7.7 Sécurité / confidentialité
- Fuites (embedding/visage/URL) dans logs/exceptions/fichiers — vérifier au‑delà
  du test de contrat (chemins non couverts ?).
- Décodage d'images watchlist (libjpeg/png) sur fichiers locaux ; symlinks dans
  `data/watchlist/` ? Téléchargement du modèle au 1er lancement (chaîne
  d'appro) : intégrité/épinglage ?

## 8. Contraintes de la revue
- Pas de nouvelle dépendance sans besoin démontré (runtime/packaging/Windows).
- Pas de réécriture massive ni d'abstraction spéculative. Respecter le hors‑scope
  (`CLAUDE.md §1.1`). Décision durable → proposer une **ADR** courte.

## 9. Plan de calibration & distance (rappel)
Protocole FAR/FRR sur volontaires consentants (20 sujets, 5 captures/sessions
séparées, distances en mètres + taille px, séparation enrôlement/test) ; choisir
le seuil par FAR cible ; rapporter par tranche de taille (<80, 80‑111, 112‑159,
≥160 px). Pour la distance : benchmark croisé résolution × det_size × taille
bbox AVANT toute super‑résolution/tracking additionnel.

## 10. Format de sortie attendu
1. **Résumé exécutif** (santé, risques majeurs).
2. **Vérification reproduite** : sorties réelles pytest/ruff/mypy + break‑test
   réseau + toute mesure refaite.
3. **Findings priorisés** :
   ```
   [Sévérité: bloquant | majeur | mineur | nit] Titre
   Fichier:ligne
   Problème (fait + preuve) :
   Impact :
   Correctif minimal :
   Risque / coût :
   ```
   Groupés : (a) fiabilité, (b) streaming/réseau réel, (c) sécurité/privacy,
   (d) architecture, (e) perf, (f) tests. Trié par sévérité.
4. **Déploiement caméra réelle** : recommandations concrètes et mesurables pour
   une caméra Wi‑Fi domestique ; et constat honnête + limites pour un contexte
   rue/municipal (technique ET juridique).
5. **Ce qu'il NE faut PAS changer**.

## 11. Checklist avant de rendre
- [ ] Docs + code réels lus, pas supposés.
- [ ] pytest/ruff/mypy exécutés et cités ; break‑test réseau refait.
- [ ] Chaque affirmation réseau/perf appuyée par une mesure reproduite.
- [ ] Chaque finding : fichier:ligne + plus petit correctif.
- [ ] Aucun invariant §6 cassé ; pas d'abstraction spéculative.
- [ ] Limite juridique rue/municipale explicitement signalée.
