# HANDOFF.md --- Sentinel Vision

> **Mémoire opérationnelle vivante du projet.**
>
> Ce fichier sert de point de reprise pour **Claude Code, Codex, ChatGPT
> ou tout autre agent** qui intervient sur Sentinel Vision.
>
> Il doit permettre à un nouvel agent de comprendre rapidement :
>
> -   ce qu'est le produit ;
> -   les décisions déjà prises ;
> -   l'architecture réellement en place ;
> -   ce qui est terminé ;
> -   ce qui reste à faire ;
> -   les contraintes à ne pas casser ;
> -   les validations réellement effectuées ;
> -   le prochain travail à reprendre.
>
> **Le code existant reste la preuve finale de ce qui est réellement
> implémenté.** Ce document est une mémoire de passation, pas une
> autorité supérieure au code.

------------------------------------------------------------------------

# 0. Règle de reprise

Avant toute modification :

``` text
READ
↓
INSPECT
↓
UNDERSTAND
↓
VERIFY AGAINST CODE
↓
IDENTIFY REDUNDANCY
↓
REUSE
↓
SIMPLIFY
↓
IMPLEMENT
↓
VALIDATE
↓
UPDATE HANDOFF
```

Ne jamais commencer à coder uniquement à partir de ce fichier.

------------------------------------------------------------------------

# 1. À lire en premier

Lire entièrement, dans cet ordre :

``` text
1. CLAUDE.md
2. ARCHITECTURE.md
3. DESIGN_SYSTEM.md
4. HANDOFF.md
5. README.md
6. configuration agent éventuelle (.claude/, AGENTS.md, etc.)
7. code réel
```

Si certains fichiers n'existent pas :

``` text
ne pas les inventer
ne pas créer automatiquement un remplacement
inspecter d'abord le dépôt
```

Après lecture de la documentation, inspecter au minimum :

``` text
project tree
entry point
domain
application/use cases
ports
adapters
infrastructure
camera pipeline
recognition pipeline
watchlist
presentation/UI
tests
configuration
dependencies
```

------------------------------------------------------------------------

# 2. Hiérarchie de vérité

En cas de contradiction :

``` text
1. comportement réellement vérifié
2. code actuel
3. tests actuels
4. architecture documentée
5. HANDOFF
6. hypothèses anciennes
```

Mais :

> une divergence entre le code et la documentation doit être signalée.

Ne jamais modifier silencieusement l'architecture pour faire
correspondre le code à une documentation devenue obsolète.

------------------------------------------------------------------------

# 3. Contexte produit

**Sentinel Vision** est une application locale de vision assistée
destinée à démontrer une chaîne de traitement vidéo temps réel :

``` text
camera
↓
face detection
↓
face representation / embedding
↓
comparison against a local watchlist
↓
recognition decision
↓
live visual feedback
```

Le produit doit permettre de comprendre immédiatement :

``` text
Is the camera running?
Is the recognition engine ready?
Is a face detected?
Is there a potential watchlist match?
What similarity value supports the result?
Is the system healthy?
```

------------------------------------------------------------------------

# 4. Positionnement produit

Sentinel Vision doit être :

``` text
local-first
fast
clear
controlled
demonstrable
maintainable
technically honest
low-cognitive-load
```

Ce n'est pas :

``` text
a cinematic surveillance HUD
a social profiling system
a generic admin dashboard
a cloud platform by default
a collection of AI effects
a fake threat scoring system
```

------------------------------------------------------------------------

# 5. Stack connue actuellement

La stack connue au moment de cette passation est :

``` text
Python
OpenCV
InsightFace
ONNX Runtime
NumPy
```

Cette liste doit être vérifiée dans le dépôt avant toute décision.

Ne jamais ajouter une dépendance simplement parce qu'elle serait
pratique.

Avant toute nouvelle dépendance :

``` text
problem
↓
existing stack capability
↓
stdlib capability
↓
smallest viable implementation
↓
dependency cost
↓
runtime / packaging / Windows impact
↓
user validation if required
```

------------------------------------------------------------------------

# 6. Direction architecture

Le projet doit conserver une séparation claire entre :

``` text
Domain
Application
Ports
Adapters
Infrastructure
Presentation
Composition
```

Le domaine ne doit pas dépendre de :

``` text
OpenCV
InsightFace
ONNX Runtime
filesystem implementation
GUI framework
camera implementation
```

Les technologies externes doivent rester derrière des frontières
explicites lorsque cette séparation existe réellement dans le code.

Ne pas créer une Clean Architecture cérémonielle avec des couches vides.

------------------------------------------------------------------------

# 7. Pipeline conceptuel

Le pipeline cible est :

``` text
Frame source
↓
Face detector / recognition engine
↓
Face observations
↓
Watchlist comparison
↓
Recognition policy
↓
Recognition result
↓
Presentation
```

Les responsabilités ne doivent pas être mélangées.

Exemple :

``` text
camera adapter
≠ recognition policy

recognition engine
≠ watchlist repository

renderer
≠ business decision
```

------------------------------------------------------------------------

# 8. Vocabulaire métier

Préférer un vocabulaire explicite :

``` text
FaceObservation
FaceEmbedding
WatchlistSubject
SimilarityScore
RecognitionResult
PotentialMatch
Unknown
```

Les noms exacts doivent suivre le code existant.

Ne pas renommer massivement un modèle déjà cohérent pour correspondre à
cette liste.

------------------------------------------------------------------------

# 9. Sémantique de reconnaissance

Une similarité n'est pas automatiquement une probabilité.

Ne jamais transformer sans preuve :

``` text
0.742 similarity
```

en :

``` text
74.2% certain
```

Le domaine doit être propriétaire :

-   du seuil ;
-   de la comparaison ;
-   de la décision ;
-   de la signification de `UNKNOWN` ;
-   de la signification de `POTENTIAL MATCH`.

La présentation affiche la décision.

Elle ne la recalcule pas.

------------------------------------------------------------------------

# 10. Terminologie UI

Terminologie recommandée :

``` text
SYSTEM READY
FACE DETECTED
UNKNOWN
POTENTIAL MATCH
CAMERA UNAVAILABLE
RECOGNITION ENGINE UNAVAILABLE
```

Éviter :

``` text
THREAT
HOSTILE
TARGET
SUSPECT
DANGER
AI CERTAINTY
```

Une correspondance technique ne doit pas être présentée comme une
conclusion sur une personne.

------------------------------------------------------------------------

# 11. Design System

La source de vérité visuelle est :

``` text
DESIGN_SYSTEM.md
```

Direction :

``` text
MUI / Material Design 3 inspired
premium
dark-first
professional
smooth
calm
minimal
computer-vision focused
```

MUI est actuellement une **référence de langage visuel**, pas
nécessairement une dépendance du projet.

Ne pas introduire React/MUI uniquement pour reproduire ce style.

------------------------------------------------------------------------

# 12. UX North Star

En moins de trois secondes, l'utilisateur doit pouvoir déterminer :

``` text
camera status
system status
face detection state
recognition decision
similarity
```

Priorité visuelle :

``` text
1. live video
2. recognition result
3. detected face
4. similarity
5. system diagnostics
```

La vidéo reste dominante.

------------------------------------------------------------------------

# 13. Motion

Motion :

``` text
short
purposeful
non-blocking
smooth
rare
```

Éviter :

``` text
scanner line
continuous pulse
glowing reticle
radar
shake
bounce
decorative particles
```

La fluidité de la vidéo est plus importante qu'une animation.

------------------------------------------------------------------------

# 14. Performance

La performance fait partie du produit.

Toujours surveiller lorsque pertinent :

``` text
camera FPS
inference latency
frame latency
CPU
memory
startup time
render/overlay cost
```

Ne pas optimiser sur intuition.

Mesurer avant une optimisation significative.

------------------------------------------------------------------------

# 15. Boucle temps réel

Éviter dans une boucle par frame :

``` text
disk reads
model loading
font loading
repeated asset construction
unbounded allocations
verbose logging
expensive layout calculation
configuration parsing
watchlist reload
```

Pré-calculer uniquement ce qui est réellement stable.

------------------------------------------------------------------------

# 16. Watchlist

La watchlist doit rester distincte du moteur de reconnaissance.

Responsabilités conceptuelles :

``` text
storage
→ repository / adapter

comparison
→ recognition/application logic

decision
→ domain policy

display
→ presentation
```

Ne pas laisser OpenCV ou le renderer devenir propriétaire de la
watchlist.

------------------------------------------------------------------------

# 17. Données et honnêteté

Ne jamais fabriquer pour embellir une démo :

``` text
accuracy
confidence
threat score
risk score
database hits
scan progress
identity
telemetry
```

Une donnée affichée doit provenir d'une donnée réellement calculée ou
d'un état réel du système.

------------------------------------------------------------------------

# 18. Erreurs

Différencier obligatoirement :

``` text
UNKNOWN
```

de :

``` text
camera failure
model failure
watchlist failure
pipeline failure
```

Un problème technique ne doit jamais devenir silencieusement un résultat
métier.

------------------------------------------------------------------------

# 19. États importants

Caméra :

``` text
closed
opening
active
failed
```

Moteur :

``` text
initializing
ready
failed
```

Reconnaissance :

``` text
no_face
face_detected
unknown
potential_match
```

Les noms exacts dépendent du code.

Ne pas créer ces enums si le projet possède déjà une représentation
correcte.

------------------------------------------------------------------------

# 20. Plusieurs visages

Le système doit rester compréhensible avec plusieurs visages.

Chaque observation peut avoir :

``` text
bounding box
short result label
optional similarity
```

Le renderer ne doit pas transformer plusieurs détections en surcharge
visuelle.

La politique métier pour plusieurs correspondances doit rester hors du
renderer.

------------------------------------------------------------------------

# 21. Sécurité et confidentialité

Ne jamais journaliser inutilement :

``` text
raw embeddings
full face images
personal identifiers
watchlist content
```

Si ces données doivent être persistées pour le fonctionnement réel :

``` text
document why
document where
document lifecycle
document access assumptions
```

Ne pas introduire de stockage supplémentaire sans besoin explicite.

------------------------------------------------------------------------

# 22. Standards de code

Principes :

``` text
KISS
YAGNI
DRY knowledge
SOLID pragmatic
SRP
Tell Don't Ask where useful
explicit naming
small cohesive units
composition over speculative frameworks
```

Éviter :

``` text
God classes
Manager classes with everything
Utils dumping grounds
premature generic repositories
universal components
unnecessary factories
unnecessary interfaces
abstraction for one implementation without boundary value
```

------------------------------------------------------------------------

# 23. Commentaires

Préférer :

``` text
clear names
small functions
explicit types
good boundaries
```

aux commentaires expliquant du code confus.

Les commentaires restent acceptables lorsqu'ils expliquent réellement :

``` text
why
external constraint
non-obvious algorithmic reason
measured workaround
```

Ne pas utiliser les commentaires pour compenser un mauvais nommage.

------------------------------------------------------------------------

# 24. Règle de refactoring

Avant de créer quelque chose :

``` text
search
↓
inspect
↓
reuse
↓
extend
↓
create only if necessary
```

Avant de conserver une duplication :

``` text
same knowledge?
same reason to change?
```

Si oui :

``` text
consider consolidation
```

Si seulement la syntaxe se ressemble :

``` text
do not force DRY
```

------------------------------------------------------------------------

# 25. Règle de changement

Une tâche doit normalement produire :

``` text
smallest coherent vertical change
```

Éviter :

``` text
feature request
+
global architecture rewrite
+
dependency migration
+
UI redesign
+
unrelated cleanup
```

dans la même intervention.

------------------------------------------------------------------------

# 26. Git Discipline

Avant modification :

``` text
git status
git diff
```

Comprendre les changements non commités.

Ne jamais écraser le travail existant d'un autre agent.

Ne jamais :

``` text
git reset --hard
git clean -fd
force push
delete unexplained files
```

sans instruction explicite.

Après modification :

``` text
git diff
git diff --check
```

si le dépôt utilise Git.

------------------------------------------------------------------------

# 27. Validation

Ne jamais dire :

``` text
tested
working
validated
```

sans préciser ce qui a réellement été exécuté.

Distinguer :

``` text
static inspection
unit test
integration test
runtime test
camera test
visual test
performance measurement
manual test
```

Une importation Python réussie ne prouve pas que la caméra fonctionne.

------------------------------------------------------------------------

# 28. Validation minimale après changement

Adapter au dépôt réel, mais vérifier au minimum :

``` text
syntax/imports
tests available
application startup
changed execution path
error path
git diff
```

Pour toute modification du pipeline caméra :

``` text
real camera test when available
```

Pour toute modification de reconnaissance :

``` text
known reference
unknown reference
no face
multiple faces when relevant
```

Pour toute modification UI :

``` text
normal state
loading/startup
unknown
potential match
technical error
multiple faces
```

------------------------------------------------------------------------

# 29. Performance Validation

Pour une modification touchant la boucle live :

comparer si possible :

``` text
before
vs
after
```

sur la même machine et le même scénario.

Mesures utiles :

``` text
FPS
inference ms
CPU
memory
startup
```

Ne pas annoncer une amélioration de performance uniquement parce que le
code semble plus rapide.

------------------------------------------------------------------------

# 30. Documentation vivante

Après une tranche significative :

mettre à jour ce fichier.

Ne pas y recopier tout le code.

Documenter seulement :

``` text
decision
implementation state
important architecture change
important dependency
validation
known issue
next action
```

------------------------------------------------------------------------

# 31. État réel du projet

> **À maintenir à chaque session.**

État connu au moment de la création de ce HANDOFF :

``` text
Product direction
→ defined

Architecture principles
→ defined in project documentation

Premium MUI-inspired design system
→ defined in DESIGN_SYSTEM.md

Runtime stack known
→ Python + OpenCV + InsightFace + ONNX Runtime + NumPy

Exact current implementation state
→ MUST be re-verified from repository before coding

Exact automated test status
→ MUST be re-verified

Exact camera/runtime validation status
→ MUST be re-verified

Exact packaging/deployment status
→ MUST be re-verified
```

Aucune information non vérifiée ne doit être transformée en état
terminé.

------------------------------------------------------------------------

# 32. Tableau de reprise

Mettre à jour ce tableau à la fin de chaque intervention :

  ------------------------------------------------------------------------
  Zone              État              Dernière          Notes
                                      validation        
  ----------------- ----------------- ----------------- ------------------
  Architecture      Implémentée M0-M6 2026-10-03       Monolithe modulaire,
                                                        domain pur isolé

  Camera            Implémentée       2026-10-03        OpenCVCamera (CAP_DSHOW).
                    non testée live   (code + imports)  Webcam réelle PAS testée

  Detection         Fonctionnelle     2026-10-03        InsightFace analyzer,
                                      (image sample)    6 visages sur t1.jpg

  Embeddings        Fonctionnels      2026-10-03        normed_embedding 512-d,
                                      (image sample)    norme 1.0

  Watchlist         Fonctionnelle     2026-10-03        Loader local, 1 ref/
                                      (image sample)    sujet detecte

  Matching          Calibre + qualite 2026-10-03        seuil 0.45 (marge 0.26 /
                                      (image sample)    imposteurs) + porte 112px

  Live UI           Overlay M6 fait   2026-10-03        MATCH/UNKNOWN verifie
                                      (rendu image)     image ; live non testé

  Error states      Premium + honnete 2026-10-03        Ecrans Retry camera/
                                      (rendu image)     moteur ; degraded != UNKNOWN

  Tests             33 unit verts     2026-10-03        pytest -q : 33 passed

  Performance       Mesurée (CPU)     2026-10-03        buffalo_s ~14 FPS 1
                                                        visage ; voir ADR-001

  Packaging         pyproject + src   2026-10-03        pip install -e . ;
                    layout            (imports OK)      entry point défini
  ------------------------------------------------------------------------

------------------------------------------------------------------------

# 33. Décisions durables

Décisions connues :

``` text
D001
Live video remains visually dominant.

D002
MUI / Material is a visual and interaction reference, not a mandatory dependency.

D003
The UI must distinguish recognition results from technical failures.

D004
Similarity must not be presented as probability without calibration evidence.

D005
No fake telemetry or threat theater.

D006
Smoothness and live performance have priority over decorative motion.

D007
External technologies should remain outside the domain boundary.

D008
The existing code is the final proof of implementation state.

D009
Documentation may be challenged when measurements or code reality contradict it.

D010
HANDOFF.md must be updated after meaningful development sessions.
```

------------------------------------------------------------------------

# 34. Known Issues

À remplir uniquement avec des problèmes réellement observés.

Format :

``` text
KI-001
Status:
Area:
Observed:
Reproduction:
Impact:
Workaround:
Next action:
```

Ne jamais créer de faux Known Issues pour remplir la documentation.

------------------------------------------------------------------------

# 35. Current Work

À maintenir pendant chaque session.

``` text
Current objective:
<fill from actual task>

Why:
<business / technical reason>

Scope:
<exact scope>

Out of scope:
<explicit exclusions>

Files touched:
<actual files>

Validation planned:
<actual commands/tests>
```

------------------------------------------------------------------------

# 36. Last Completed Work

Après chaque session significative :

``` text
Date: 2026-10-03
Agent: Claude Code (Opus 4.8)

Implemented:
- M0 toolchain: pyproject.toml (src layout, entry point sentinel-vision,
  pytest/ruff/mypy config), .gitignore (watchlist + model cache excluded), README.
- M1 camera: OpenCVCamera context manager (bootstrap/camera.py), CAP_DSHOW,
  explicit CameraError on open/read failure (no silent fallback).
- M2 detection: InsightFaceDetector adapter (detection-only module), translates
  to domain FaceObservation; DetectorInitializationError / FaceDetectionError.
- Domain: FaceObservation value object (bbox clamping + no-area invariant),
  pure, no cv2/insightface.
- Presentation: overlay.py (boxes + quiet bottom status bar) per DESIGN_SYSTEM.
- Composition root: bootstrap/main.py live loop (model load once before loop,
  EMA FPS, q/Esc/window-close exit).

Removed / Simplified:
- No FaceAnalyzer port / Protocol yet: one implementation, no use case consumes
  it. Add the seam at M5/M6 when a testable use case exists (YAGNI).
- Detection-only model load (no embedding) until M4 — lighter + honest for M2.

Architecture:
- Dependency rule holds: domain imports nothing external (verified: detection
  returns sentinel_vision...FaceObservation, not an insightface type).
- Single BC Recognition, layers domain/infrastructure/bootstrap. No empty dirs
  beyond what code uses.

UX / UI:
- Overlay matches DESIGN_SYSTEM: dark panel, primary-blue boxes, muted
  right-aligned diagnostics, green SYSTEM READY dot, no sci-fi, video dominant.

Performance:
- First detect() on 1280x886 sample = 661 ms (cold warmup, graph opt included).
  Steady-state and live FPS NOT yet measured (needs the live loop on real cam).
- Detector init 134 s on first run = one-time model download, not per-start cost.

Validation:
- pytest -q -> 3 passed. ruff check . -> clean. mypy -> clean (13 files).
- Import smoke test of main + overlay -> OK.
- Headless end-to-end through real code on insightface sample t1.jpg ->
  6 faces detected, overlay rendered to PNG, visually confirmed.

Manual test:
- Live webcam window NOT run (no interactive camera/display session available
  to the agent). Needs user: `sentinel-vision`, confirm window + boxes + FPS.

Known limitations:
- Live camera + real-time FPS unverified.
- det_score is detection confidence only; intentionally not shown (would be
  confused with recognition similarity, which does not exist yet).
- CAP_DSHOW is Windows-only.

Dependencies:
- No new runtime deps (opencv/insightface/onnxruntime/numpy already present).
  pyproject declares them + dev extras (pytest/ruff/mypy, already installed).
- onnxruntime providers available: Azure, CPU. No GPU/CUDA. Runs CPU.

Next:
- M3 watchlist loading, then M4 embeddings, M5 recognition decision (TDD on
  threshold / UNKNOWN / POTENTIAL MATCH), M6 wire into the live loop.
- Before M3: user runs the live webcam loop once to confirm M1/M2 on hardware.
```

Écrire uniquement des faits.

------------------------------------------------------------------------

# 37. Session Journal

Ajouter une entrée courte.

Format :

``` text
## YYYY-MM-DD — <short title>

Goal:
-

Changes:
-

Decisions:
-

Validation:
-

Remaining:
-
```

Le journal ne doit pas devenir une transcription complète de la session.

## 2026-10-03 — Recognition core M3-M6 + clean code

Goal:
- Recognition de bout en bout (watchlist -> embedding -> decision -> overlay).
- Code sans commentaires (clean code auto-descriptif), tests = contrats (une
  fonctionnalite par test).

Changes:
- Domain: FaceEmbedding (similarite cosinus), WatchlistSubject, Watchlist
  (recognize = meilleur score vs seuil -> POTENTIAL_MATCH/UNKNOWN),
  RecognitionResult/Decision.
- Application: port FaceAnalyzer + AnalyzedFace ; use case RecognizeFrame.
- Infra: InsightFaceFaceAnalyzer (detection+recognition, remplace l'ancien
  detector) ; LocalWatchlistLoader (data/watchlist/<sujet>/*.img, 1 visage/ref).
- Overlay: MATCH (rouge mesure) / UNKNOWN (gris froid), barre de statut +
  nb sujets. Bootstrap recable sur le use case.
- Tous les commentaires et docstrings retires du code source existant.
- Config par defaut: buffalo_s + det_size (320,320) (ADR-001).

Decisions:
- ADR-001: pack buffalo_s par defaut (perf CPU ~14 FPS vs ~1 FPS buffalo_l).
- Port FaceAnalyzer introduit maintenant (un use case reel le consomme + fake
  en test) ; pas de port Watchlist (charge une fois au bootstrap).

Validation:
- pytest -q -> 24 passed. ruff -> clean. mypy -> clean (21 fichiers).
- Headless via code reel (image t1.jpg): watchlist 1 sujet, sujet enrole
  -> POTENTIAL_MATCH 0.96, 5 autres -> UNKNOWN (max 0.13). Overlay rendu PNG
  verifie visuellement (rouge match / gris unknown).
- Perf CPU mesuree: buffalo_l 1 visage ~1.0 FPS ; buffalo_s det320 ~14 FPS.
- Contrat d'architecture teste: domaine n'importe ni cv2 ni insightface.

Remaining:
- Webcam live + FPS reel non testes (pas de camera/affichage cote agent).
- Seuil 0.35 non calibre (marge large observee mais a calibrer sur vraies
  donnees de demo).
- Si plusieurs visages live ralentissent (N embeddings/frame), envisager
  recognition toutes les N frames (mesure d'abord, ADR si durable).
- data/watchlist/ vide: ajouter des sujets volontaires pour la demo.

## 2026-10-03 — Enrolement webcam + robustesse demarrage

Goal:
- Rendre la demo reellement demontrable (watchlist vide => aucun MATCH) et
  fiabiliser le demarrage/console.

Changes:
- Application: use case EnrollSubject + port ReferenceWriter (regle = un seul
  visage par capture).
- Infra: LocalWatchlistWriter (data/watchlist/<label normalise>/ref_N.png,
  index sequentiel, pas d'ecrasement).
- Bootstrap: entry point sentinel-vision-enroll <label> (apercu live, capture
  SPACE sur frame propre non annotee, ESC annule).
- main.py: wrapper main() traduisant CameraError /
  FaceAnalyzerInitializationError / WatchlistLoadError en message propre +
  SystemExit(1). Entry point -> main:main.
- Filtre du FutureWarning scikit-image estimate (bruit console) aux 2 entrees.

Validation:
- pytest -q -> 31 passed. ruff -> clean. mypy -> clean (24 fichiers).
- Round-trip reel (t1.jpg): frame 6 visages -> enrolement REJETE ; crop 1
  visage -> ref_1.png sauve ; recharge 1 sujet ; reconnu POTENTIAL_MATCH 0.958.
- Live confirme par l'utilisateur: sentinel-vision ouvre la boucle.

Remaining:
- Capture webcam interactive non testee sur camera reelle par l'agent (regle
  un-visage et ecriture testees headless).
- Echec camera EN COURS de boucle remonte encore en exception ; ecran d'erreur
  OpenCV propre (DESIGN_SYSTEM §44-46) non fait.
- Seuil non calibre ; FPS live reel non mesure.

## 2026-10-03 — Etats d'erreur premium + garde d'honnetete

Goal:
- Une panne technique ne doit jamais devenir UNKNOWN (invariant CLAUDE §11).
- Ecrans d'erreur premium (camera / moteur) avec Retry, sans stack trace.

Changes:
- FaceAnalysisError deplace de l'infra vers le port application/face_analyzer
  (DIP: le port possede son contrat d'erreur). L'adapter InsightFace le leve.
- RecognizeFrame retourne FrameRecognition (faces + recognition_available) et
  traduit FaceAnalysisError -> FrameRecognition.unavailable() (garde testee).
- overlay.render(frame, outcome, fps, size): etat DEGRADED distinct
  ("RECOGNITION UNAVAILABLE", point d'alerte, aucune box) vs READY.
- status_screen.py: StatusScreen.ask (fenetre + Retry/Quit) + render_status pur.
- main.py: reprise -> _initialize_analyzer (retry moteur), _run_live_sessions
  (retry camera, couvre l'echec camera EN COURS de boucle), _run_live_session.
  main() ne garde plus que WatchlistLoadError (erreur de configuration).

Decisions:
- Garde d'honnetete dans la couche application (testable), pas dans bootstrap.
- Pas d'ADR (raffinement interne aux frontieres existantes).

Validation:
- pytest -q -> 33 passed (dont available / unavailable-not-unknown).
- ruff clean, mypy clean (25 fichiers).
- Rendu headless verifie visuellement: overlay DEGRADED (video visible, aucune
  box) et ecran "Camera unavailable" (rouge retenu + Retry/Quit, sans trace).

Remaining:
- Reprise interactive (Retry) verifiee par inspection ; parties pures testees ;
  boucle complete non testable en headless (fenetre/camera).
- enroll.py: analyze du preview non garde (echec par-frame improbable post-init).
- Webcam live + FPS reel ; calibration du seuil : cote utilisateur.

## 2026-10-03 — Calibration du seuil + porte de qualite (fiabilite)

Goal:
- Fiabilite "precision d'abord": aucun faux positif, aucune alerte sur un
  visage que le systeme ne peut pas evaluer (trop loin / trop petit / peu net).

Changes (TDD reel: RED observe puis GREEN):
- Mesure imposteurs (t1.jpg, buffalo_s): cosinus max 0.192, moyenne 0.044.
- Domaine (SRP, unite par unite):
  - FaceQualityGate(min_face_pixels, min_detection_score).is_reliable(obs).
  - RecognitionPolicy(match_threshold).decide(candidate) -> match/unknown.
  - Watchlist.recognize -> Watchlist.best_match(probe) -> Candidate | None
    (separation score vs decision, CLAUDE §10).
  - RecognitionResult.insufficient_quality() + Decision.INSUFFICIENT_QUALITY.
- Application: RecognizeFrame(analyzer, watchlist, gate, policy) applique la
  porte avant la comparaison ; EnrollSubject refuse une capture non fiable.
- Overlay: 3e etat "MOVE CLOSER" (ambre), distinct de UNKNOWN (gris) et MATCH.
- Config calibree: recognition_threshold 0.35 -> 0.45, min_face_pixels 112,
  min_detection_score 0.65. ADR-002.

Decisions:
- Seuil 0.45 = plafond imposteur mesure (0.19) + grande marge, sous la plage
  genuine ArcFace (~0.4-0.7). Precision prioritaire.
- Porte de qualite partagee (DRY) entre reconnaissance et enrolement.
- Pas de garde de marge top-2 (YAGNI; le seuil + la porte couvrent le besoin).

Validation:
- pytest -q -> 43 passed (gate, policy, best_match, insufficient-quality,
  enrolement refus qualite). ruff clean, mypy clean (27 fichiers).
- Bout-en-bout (code reel, image): visages fiables -> 1 MATCH 0.96 + 5 UNKNOWN
  (imposteur max 0.13) ; visages lointains -> INSUFFICIENT_QUALITY. Overlays
  3 etats verifies visuellement.

Remaining:
- Rappel (acceptation vrais positifs a 0.45) non calibre sur vraies paires
  multi-photos : a valider sur volontaires ; si trop strict, descendre vers
  0.40 en remesurant la marge imposteur.
- Webcam live + FPS reel : cote utilisateur.

## 2026-10-04 — Corrections suite revue senior (Codex)

Goal:
- Corriger les defauts confirmes de la revue (CODEX_REVIEW_PROMPT.md + rapport).

Changes (chaque defaut confirme dans le code puis corrige, avec test):
- [correctness] FaceEmbedding rejette NaN/inf ; l'adapter traduit un embedding
  invalide en FaceAnalysisError -> RECOGNITION UNAVAILABLE (plus de faux UNKNOWN).
- [securite] LocalWatchlistWriter: _subject_id assaini (a-z0-9_-), rejet si vide,
  garde "chemin enfant de la racine" (plus de path traversal) ; _next_index =
  max(index)+1 (plus d'ecrasement sur trou de numerotation).
- [honnetete] overlay.render recoit camera_index + provider_label reels
  (plus de "CAM 0 / CPU" fabrique).
- [fiabilite] LocalWatchlistLoader applique FaceQualityGate aux references
  manuelles et traduit FaceAnalysisError -> WatchlistLoadError.
- [design/perf] EnrollSubject.enroll(label, frame, faces) : ne possede plus
  l'analyzer, plus de double analyse a la capture ; message honnete (taille +
  detection, pas "clarte"). enroll.py gere OSError/ValueError/FaceAnalysisError.
- [tests] +10 tests : non-finite embedding, path traversal, numbering gap,
  loader (gate skip / reliable / FaceAnalysisError->WatchlistLoadError),
  enroll faces, contrat application !-> infrastructure.
- [docs] README + ADR-002 : calibration qualifiee "provisoire", pas de promesse
  "no false positives" ; porte = taille + confiance seulement.

Decisions:
- Un embedding invalide est une panne technique (RECOGNITION UNAVAILABLE), pas
  un resultat metier.
- Porte de qualite appliquee partout ou une reference entre (loader + enrol).

Validation:
- pytest -q -> 53 passed. ruff clean. mypy clean (27 fichiers).
- Runtime (code reel, image): reference trop petite -> skip "face too small";
  reference fiable -> chargee ; reconnaissance 1 MATCH 0.956 + 5 UNKNOWN ;
  provider_label CUDA/CPU honnete.

Remaining:
- Non corrige volontairement (hors defaut / YAGNI): pas de metrique nettete/pose
  (a ajouter seulement si elle ameliore FAR/FRR mesure) ; pas de marge top-2.
- Calibration FAR/FRR sur volontaires ; webcam live : cote utilisateur.

## 2026-10-04 — Sonde de distance + confirmation temporelle

Changes:
- bootstrap/distance_probe.py (CLI `sentinel-vision-probe`, --width/--height/
  --det-size) : mesure sur vraie camera la taille px / det_score par visage et
  RECO OK (>=112px) vs DETECT ONLY. Entry point ajoute (pyproject).
- Fiabilite distance : FaceObservation.iou ; domain/match_confirmation.py
  (N-of-M pur) ; application/face_tracking.py (FaceTracker greedy IoU, etat par
  session). main.py applique le tracker aux frames disponibles. Defauts
  conservateurs dans AppConfig (confirm_frames=3, window=5, iou=0.3, misses=15).
  ADR-003. Un pic 1-frame ne confirme plus un MATCH (teste).

Validation:
- pytest -q -> 65 passed. ruff clean. mypy clean (30 fichiers).
- distance_probe: draw verifie headless (RECO OK vert / DETECT ONLY ambre).

Remaining:
- Tuning confirm_frames/window/iou + seuil par tranche de distance : requiert
  mesures sonde/terrain (cote utilisateur).
- Source camera RTSP/IP pour deploiement : petite extension (nouvel adapter de
  frames) quand necessaire ; GPU (onnxruntime-gpu) pour 4K/multi-cam.

## 2026-10-04 — Arret propre Ctrl+C + source camera RTSP

Changes:
- Ctrl+C (KeyboardInterrupt) capture dans main/enroll/probe -> "Stopped.",
  plus de traceback (evite aussi les process zombies qui verrouillaient l'exe).
- Source camera reseau : AppConfig.camera_url ; OpenCVCamera ouvre RTSP via
  CAP_FFMPEG (buffersize=1) sinon index local ; identifiants masques
  (mask_credentials, teste). --source URL sur les 3 CLIs (prioritaire sur
  --camera). Overlay: "CAM NET" si source reseau. ADR-004.

Validation:
- pytest -q -> 67 passed. ruff clean. mypy clean (30 fichiers).
- --source expose sur main/enroll/probe (--help).
- Ouverture RTSP reelle : a valider par l'utilisateur (URL testable dans VLC).

Note env:
- Un `pip install -e .` peut echouer (WinError 32) si un `sentinel-vision.exe`
  tourne encore -> fermer la fenetre / tuer le PID, nettoyer les dist-info `~*`,
  reinstaller. Le fix Ctrl+C reduit ce risque.

## 2026-10-04 — Abstraction source de frames (OCP)

Changes:
- bootstrap/frame_source.py : FrameSource (Protocol) + WebcamSource +
  StreamSource + open_frame_source(config). Remplace OpenCVCamera (camera.py
  supprime). Helpers _opened/_read/_release (composition, pas heritage).
- main/enroll/distance_probe utilisent open_frame_source. ADR-005.
- Ajouter un type de camera = nouvelle classe FrameSource + 1 ligne dans la
  fabrique ; sources existantes inchangees (OCP).

Decisions:
- Multi-cameras (N par etage) = UNE instance par camera (documente README).
  Un process pilotant N cameras reste hors perimetre (CPU; GPU+ADR requis).

Validation:
- pytest -q -> 69 passed (dont selection de source + masquage identifiants).
  ruff clean, mypy clean (30 fichiers).

## 2026-10-04 — Streaming resilient (reseau instable)

Changes:
- StreamSource: timeouts FFMPEG (OPEN/READ_TIMEOUT_MSEC = stream_timeout_ms) ->
  read() echoue au lieu de bloquer indefiniment.
- ResilientFrameSource (decorateur FrameSource) : reconnexion auto sur echec de
  read (close+recreate) jusqu'a reconnect_attempts avec reconnect_backoff, sinon
  CameraError -> ecran de reprise. Ouverture initiale fail-fast (non masquee).
- create_frame_source(config) = selection OCP (webcam/stream, testee) ;
  open_frame_source = enveloppe resiliente. Config: stream_timeout_ms=5000,
  reconnect_attempts=3, reconnect_backoff=1.0. ADR-006.

Validation:
- pytest -q -> 74 passed (blip/persistent/reopen-fail + selection + masquage).
  ruff clean, mypy clean (30 fichiers).
- Break-test integration: RTSP injoignable (10.255.255.1) -> CameraError propre
  en ~2.3s (timeout), pas de blocage.

Remaining:
- Reconnexion infinie non surveillee (kiosk 24/7) : hors scope (augmenter
  attempts ou auto-retry de l'ecran si besoin reel).
- Pendant une reconnexion, la fenetre se fige brievement (sleep borne).

## 2026-10-04 — Durcissement securite + validation config

Changes:
- Securite : identifiants RTSP via env SENTINEL_CAMERA_URL (evite le mot de
  passe dans l'historique shell / liste des process). resolve_camera_config
  (DRY, 3 CLIs) : --source > env > --camera ; env vide ignore. Deja masque
  dans les messages.
- Fiabilite : AppConfig.__post_init__ valide les invariants (seuil dans [-1,1],
  min_detection_score dans [0,1], min_face_pixels>=1, confirmation_window>=
  confirm_frames, reconnect_attempts/backoff/timeout>=0, dimensions>0) ->
  echec rapide au lieu d'un comportement silencieux casse.

Validation:
- pytest -q -> 85 passed (resolution source + env + validation config).
  ruff clean, mypy clean (30 fichiers).
- Env e2e : URL lue depuis SENTINEL_CAMERA_URL, masquee rtsp://***@... .

## 2026-10-04 — Contrat anti-fuite + prompt review deploiement

Changes:
- tests/unit/test_no_sensitive_logging.py : scanne tout src, echoue si une
  interpolation (f-string/print/raise) emet un embedding brut
  (embedding/.values/tolist/det_score) ou une URL avec identifiants sans
  mask_credentials. Detecteur verifie non-vacant (fire sur 4 cas bad, clean sur
  3 cas good).
- CODEX_REVIEW_PROMPT.md reecrit : a jour (tracking, frame_source OCP, streaming
  resilient, RTSP, validation config, env creds, anti-fuite) et axe sur la
  camera reelle Wi-Fi + rue/municipale (reconnexion, latence, codec, IP DHCP,
  RTSP en clair, multi-cam, nuit/IR/WDR, limite juridique espace public).

Validation:
- pytest -q -> 88 passed. ruff clean, mypy clean (30 fichiers).

## 2026-10-04 — Correction bug bloquant (heritage d'identite) + revue croisee

Contexte: revue senior (Codex) a trouve un bug BLOQUANT confirme par repro :
une nouvelle personne (UNKNOWN) dans la bbox d'un match precedent heritait de
l'identite confirmee. Corrections faites (moi + Codex, etat disque fusionne) :
- match_confirmation.confirm ancre sur le sujet de la frame COURANTE : un MATCH
  confirme est annule si la frame courante est UNKNOWN/INSUFFICIENT ou un autre
  sujet (plus d'heritage). Teste.
- FaceTracker.reset() ; main reinitialise le tracker a la reconnexion
  (ResilientFrameSource.reconnect_count). ADR-003 corrige (claim "monotone"
  retire, limites IoU documentees).
- Validation config etendue : det_threshold [0,1], det_size>0,
  track_iou_threshold [0,1], track_max_misses>=0.
- Sonde : "RECO OK" -> "SIZE OK" (eligibilite geometrique, pas reconnaissance).
- Enrolement : "ready" seulement si porte qualite OK ; messages n'exposent plus
  le chemin contenant le nom du sujet (print path.name / image_path.name).

Validation (etat disque fusionne verifie sur cette machine) :
- pytest -q -> 99 passed. ruff clean. mypy clean (30 fichiers).
- Repro apres fix : nouvelle UNKNOWN meme bbox -> UNKNOWN ; apres reset ->
  reconfirmation obligatoire ; sujet genuine soutenu -> POTENTIAL_MATCH correct.

Limites honnetes (non resolues, hors scope mesure) : association de pistes
purement IoU (croisements possibles) ; FAR/FRR non calibres ; pas d'anti-spoofing
(camera RGB) ; aucun test webcam/RTSP physique.

## 2026-10-04 — Capture locale d'instantane sur match (opt-in)

Contexte: usage prive (cameras perso de l'utilisateur, ex. jardin), 1re tranche
choisie = "capture photo auto seulement", local.

Changes:
- application/match_snapshot_alerter.py : SnapshotWriter (port) +
  MatchSnapshotAlerter (anti-spam : 1 capture/sujet/cooldown, horloge injectee,
  matches confirmes seulement). Pur, teste.
- infrastructure/capture/local_snapshot_writer.py : recadrage (+30% marge) de la
  frame PROPRE, ecrit data/captures/<sujet>/<ts>_<camera>_<score>.jpg.
- infrastructure/paths.py : safe_subject_id partage (DRY avec watchlist writer).
- Config : capture_enabled(False), capture_dir, capture_cooldown_seconds(30),
  camera_name. --capture (opt-in) dans main ; capture AVANT overlay (frame
  propre). data/captures/ git-ignore. ADR-007.
- Localisation = metadonnee camera (camera_name), pas de GPS.

Validation:
- pytest -q -> 109 passed. ruff clean, mypy clean (34 fichiers).
- E2E headless : 1 match -> 1 fichier moussa_demo/..._garden_0.93.jpg ; UNKNOWN
  ignore ; re-capture bloquee pendant le cooldown.

Hors scope (volontaire): envoi reseau (email/Telegram), journal d'audit, espace
public. Envoi = Phase 2, decision/ADR separee.

## 2026-10-04 — BC Communication (notification email) + sinks OCP

Changes:
- Nouveau BC communication (inspire du BC Java de l'utilisateur) :
  domain EmailAddress/EmailMessage (VO valides + erreurs) ; application port
  EmailSender (+ EmailSendingError) ; infra SmtpEmailSender (stdlib, timeout),
  MailSettings.from_env (secrets SENTINEL_SMTP_*), BackgroundEmailSender
  (decorateur non bloquant : file + thread demon, echecs via on_error).
- Integration OCP : MatchSnapshotAlerter -> MatchAlerter(sinks) + MatchSink.
  SnapshotSink (capture) + EmailAlertSink (bootstrap, glue recognition<->comm).
  Un match debounce declenche N sinks. BCs decouples ; glue au composition root.
- Config notify_enabled ; --notify ; BackgroundEmailSender.close() au shutdown ;
  MailSettingsError -> message propre. ADR-008.

Validation:
- pytest -q -> 127 passed. ruff clean, mypy clean (46 fichiers).
- Fan-out e2e headless : 1 match -> 1 snapshot + 1 email (score+camera) ;
  re-declenchement bloque en cooldown.

Hors scope (volontaire): retry durable d'email (best-effort ; snapshot = preuve
durable), piece jointe, autres canaux (Telegram/webhook = nouvel adapter + sink),
espace public.

## 2026-10-14 — M11 Detection d'objets (YOLOX ONNX, Apache-2.0)

Goal:
- Debloquer la branche non biometrique : detecter personnes/vehicules derriere
  un adaptateur, sans recycler `recognition`, sur modele licence-propre.

Changes:
- Nouveau module `detection` : `domain/detected_object.py` (VO pur, invariants),
  `application/object_detector.py` (Port + `ObjectDetectionError`),
  `infrastructure/yolox_postprocess.py` (pur : make_grid/decode/nms),
  `infrastructure/yolox_onnx_detector.py` (adapter letterbox+ORT+NMS+rescale+allow-list).
- `bootstrap/object_probe.py` + script `sentinel-vision-detect` (apercu visuel).
- Config : `detection_enabled` (False), `detection_model_path` (yolox_nano),
  `detection_score_threshold` (0.3), `detection_nms_threshold` (0.45) + validation.
- `pyproject` : mypy override `onnxruntime.*` ; modeles dans `/models/` (gitignore).
- ADR-009.

Decisions:
- YOLOX Apache-2.0 (commercial + redistribution OK, LICENSE verifiee). Defaut
  `yolox_nano` (latence) ; `yolox_tiny` pour plus de rappel.
- Module coherent, PAS de BC formel (gate ARCHITECTURE §3.3 non franchi).
- Detection desactivee par defaut ; pas encore cablee dans la boucle live (M12),
  pas de tracking/zones (M4). Fait physique seulement, aucune identite/intrusion.

Validation:
- 139 tests OK, ruff clean, mypy clean (55 fichiers).
- Baseline CPU i7-1355U : nano 13.8ms / tiny 26.6ms (frame 416²).
- End-to-end image 1080×810 seuil 0.3 : nano (41ms) bus 0.91 + 3 person ;
  tiny (51ms) bus 0.95 + 3 person. Mapping/allow-list/rescale corrects.

Remaining:
- M12 : cabler la detection dans la boucle live + overlay honnete (capacites
  separees). M4 : tracking objets, zones, franchissement directionnel.
- Precision non evaluee sur corpus annote (clips consentis requis).

## 2026-10-14 — M12 Cablage live de la detection (capacites separees)

Goal:
- Integrer la detection d'objets dans la boucle principale, en affichant les
  capacites separement (pas un unique voyant vert trompeur, §9/§12).

Changes:
- `main.py` : `_initialize_detector` (opt-in, degrade proprement si modele
  absent/echec), boucle `_detect` + `object_overlay.draw` + `_object_status`,
  flag CLI `--detect`. Detection independante de la reco (branches §4.3).
- Boxes objets dessinees APRES `alerter.process` → le snapshot-preuve reste
  propre (sans overlay).
- `overlay.render` : parametre optionnel `object_status` (chaine, aucun couplage
  BC) ajoute au bandeau ; present aussi quand la reco est UNAVAILABLE.
- `detection/infrastructure/presentation/object_overlay.py` : rendu des boxes
  (personne/vehicule), partage par `main` et `object_probe` (DRY).

Decisions:
- Statut detection = mots explicites : absent si desactive, `DETECT n` si actif,
  `DETECT UNAVAILABLE` si init echoue ou erreur en flux. Jamais masque en reco.
- Detection + visage sur CHAQUE frame pour ce premier cablage (simple, correct) ;
  plafond perf a revisiter par mesure (skip/intervalle) — non premature.

Validation:
- 143 tests OK (dont `_object_status` : 4 etats honnetes), ruff + mypy clean (57).
- Smoke live-path headless (image reelle) : detecteur construit, 4 objets,
  statut `DETECT 4`, frame annotee. Snapshot non pollue (boxes apres alerter).
- Usage : `sentinel-vision --detect` (webcam) ; `--source <rtsp>` pour flux IP.

Remaining:
- M4 : tracking objets (IoU/ByteTrack), zones, franchissement directionnel,
  deduplication d'evenements.
- Mesure latence live avec les 2 branches actives + strategie de skip.
- Precision detection sur corpus annote (clips consentis).

## 2026-10-14 — M4a Tracking d'objets (IDs stables)

Goal:
- Transformer les detections par-frame en pistes stables avec identifiant,
  prerequis des evenements (franchissement, zones) a venir.

Changes:
- `DetectedObject.iou()` (pur, miroir de `FaceObservation.iou`).
- `TrackedObject` (domaine) : `track_id` + `observation` (composition, DRY).
- `ObjectTracker` (application, pur) : association IoU greedy **meme label**,
  IDs monotones, vieillissement/suppression des pistes absentes, `reset()`.
- `object_overlay.draw_tracked` (`#id label score`) ; `_draw_box` factorise
  (DRY) ; le probe garde `draw` (detections brutes, sans id).
- `main.py` : `ObjectTracker` dans la boucle live, `reset()` sur reconnexion,
  statut `DETECT n` base sur le nombre de pistes.

Decisions:
- Reutilise `track_iou_threshold` / `track_max_misses` (meme concept que les
  visages) ; pas de nouvelle config tant qu'un besoin mesure ne l'impose pas.
- Association restreinte au meme label (une voiture ne devient pas une personne).
- Sortie = pistes vues cette frame (pas de prediction/coasting : YAGNI).
- Un ID de piste est temporaire, PAS une identite civile (§7).

Validation:
- 154 tests OK (iou, TrackedObject, 6 scenarios tracker : id, perte, reset,
  labels distincts, independance), ruff + mypy clean (59 fichiers).
- Smoke headless (image reelle, 2 frames) : IDs #1-#4 stables frame->frame ;
  overlay pistes annote la frame.

Remaining:
- M4b : zones + ligne de franchissement directionnel (hysteresis, unicite
  d'evenement, deduplication) -> evenements horodates.
- Mesure latence live 2 branches + strategie de skip.
- Precision/continuite des pistes sur corpus annote (changements d'ID, pertes).

## 2026-10-14 — BC `plate` : lecture de plaque (ANPR) comme les visages

Goal:
- Lire les plaques et comparer a une watchlist de plaques a surveiller (impayes),
  en miroir du flux visages ; testable sur PC. Format generique (multi-pays).

Changes:
- Nouveau bounded context `plate` (ne recycle ni recognition ni detection) :
  - domaine pur : `PlateNumber` (normalisation generique AB-123 -> AB123),
    `PlateReading`, `PlateWatchlist`, `PlateReadingPolicy` -> `PlateRecognitionResult`
    etats honnetes `WATCHED` / `SEEN` / `LOW_CONFIDENCE`.
  - application : port `PlateReader` + `AnalyzedPlate`, use case `RecognizePlate`.
  - infra : adapter `FastAlprPlateReader` (fast-alpr), `ocr_confidence` (pur,
    agrege la liste par-caractere via le MIN = conservateur), loader watchlist
    fichier texte, overlay plaque.
- `main.py` : `--plates`, init opt-in degradable, lecture + overlay (apres alerter),
  statut capacites combine (`DETECT n   PLATES n`) via `_capability_status`.
- Config : `plates_enabled`, `plate_detector_model`, `plate_ocr_model`,
  `plate_min_confidence` (valide), `plate_watchlist_path`.
- Dependance : `fast-alpr` 0.4.0 (code MIT) ; mypy override `fast_alpr.*`.
  Conflit cv2 resolu (desinstalle opencv-python-headless, reinstalle opencv-python).

Decisions:
- Usage = POC LOCAL sur sa propre propriete/cameras RTSP (espace prive controle).
  Licence des POIDS non confirmee (detecteur YOLOv9/GPL) -> a revalider AVANT
  toute distribution/vente. Ne pas inventer de licence (§13).
- Plaque = donnee personnelle (§11) : watchlist = fichier texte local ; pas de
  stockage auto d'inconnus ; retention a cadrer avant tout code de capture plaque.
- Format generique (OCR `cct-xs-v2-global`), pas de regle pays stricte.

Validation:
- 170 tests OK (domaine, use case, ocr_confidence, loader), ruff + mypy clean (75).
- Smoke reel (image plaque) : lue `5AU5341`, decision WATCHED sur watchlist,
  box (307,187,387,210). Modeles telecharges en cache utilisateur (hors repo).
- PERF MESUREE : ANPR ~390 ms/frame (CPU) -> ~2.5 FPS si lu a chaque frame.

Remaining (justifie par la mesure):
- Throttle ANPR (toutes N frames) ou lecture uniquement sur piste vehicule, +
  confirmation temporelle par piste (reduire faux positifs OCR).
- Masque/vitre teintee : reconnaissance faciale non fiable (barriere physique) ;
  presence detectee, identite non.
- Enrolement plaque (si besoin) ; aujourd'hui = editer data/plate_watchlist.txt.

## 2026-10-14 — ANPR optimise : lecture sur piste vehicule + confirmation

Goal:
- Rendre l'ANPR utilisable en live (mesure precedente : 390 ms/frame) : lire
  seulement les crops de pistes vehicules, throttle, confirmation par piste.

Changes:
- `VehiclePlateReader` (application, etat par piste) : recoit `(track_id, crop)`
  (BC-clean, aucun type `detection`), reutilise `RecognizePlate` (DRY), throttle
  `read_interval`, confirmation `confirm_count` lectures coherentes dans `window`,
  cache du resultat confirme entre lectures, oubli des pistes absentes, `reset()`.
- `plate_overlay.draw_on_vehicles` : libelle plaque attache a la box du vehicule
  (coords simples) ; ancien `draw(RecognizedPlate)` supprime (plus de code mort).
- `main.py` : `_VEHICLE_LABELS`, crop des pistes vehicules, `_read_vehicle_plates`,
  `_plate_entries`, `reset()` sur reconnexion ; ANPR ne tourne plus sur toute la frame.
- Config : `plate_read_interval` (5), `plate_confirm_count` (3), `plate_confirm_window`
  (5) + validation.

Decisions:
- Plaque lue uniquement sur car/motorcycle/bus/truck (pas person/bicycle).
- Confirmation = meme numero lu N fois sur la MEME piste vehicule avant affichage
  (tue les faux positifs OCR ponctuels) ; resultat = lecture courante (honnete).
- Confirmation geree dans l'application (fenetre par piste), pas de nouveau VO
  domaine (KISS/YAGNI), testee avec un faux lecteur.

Validation:
- 175 tests OK (5 scenarios VehiclePlateReader : confirmation, throttle, cache,
  oubli, seen-vs-watched), ruff + mypy clean (76 fichiers).
- Preuve modele reel (read_interval=2, confirm=2) : lecture frame1/3/5, 0 ms
  frames 2/4/6, WATCHED 5AU5341 confirme frame 3, oubli quand piste absente.
  Cout amorti ~30 ms/frame (read_interval=5) si vehicule present, 0 sinon.

Remaining:
- Mesure latence live des 3 branches ensemble sur vraie camera.
- Eventuel evenement horodate + dedup quand une plaque WATCHED est confirmee
  (ex. capture/notification, en reutilisant MatchAlerter/sinks).

## 2026-10-16 — ANPR auto + fiabilite-d'abord (vehicule rapide)

Goal:
- `--plates` active la detection automatiquement ; maximiser la capture d'un
  vehicule rapide/fuyant tout en restant temps reel.

Changes:
- Politique de lecture revue dans `VehiclePlateReader` : tant qu'une piste n'est
  PAS confirmee, lecture a CHAQUE frame pendant `plate_burst_attempts` (burst =
  capture max dans la courte fenetre d'un vehicule rapide) ; au-dela, backoff a
  `plate_read_interval` ; des confirmation, ARRET des lectures (cout -> 0).
- Config : `plate_burst_attempts` (8) + validation ; garde
  `plates_enabled requires detection_enabled`.
- CLI : `--plates` implique la detection (`detection_enabled = detect or plates`).

Decisions:
- Fiabilite-d'abord sur pistes neuves/rapides (lecture par frame), cout borne
  (backoff si durablement illisible, arret si confirme).
- Limite PHYSIQUE assumee (constitution §1/§7/§8) : flou de bouge, breve
  visibilite, obturateur/resolution/lumiere/angle camera -> aucune garantie de
  lire une plaque rapide. Le logiciel maximise, il ne promet pas 100 %.

Validation:
- 177 tests OK (burst chaque frame, backoff, arret a la confirmation, oubli,
  SEEN/WATCHED, garde config), ruff + mypy clean (76 fichiers).
- Preuve modele reel (defaults burst=8/confirm=3) : lecture frames 1-2-3
  (327/185/189 ms), WATCHED 5AU5341 confirme frame 3, 0 ms ensuite.

Remaining:
- Camera reelle : regler burst/confirm/min_confidence selon obturateur et debit.
- Evenement horodate quand une plaque WATCHED est confirmee (reutiliser sinks).

## 2026-10-16 — Alerte + capture horodatee sur plaque WATCHED

Goal:
- Declencher une capture horodatee (et email optionnel) quand une plaque de la
  watchlist est confirmee, en miroir du flux visages, sans coupler les BC.

Changes:
- `PlateAlerter` (plate/application) : dedup par numero de plaque + cooldown,
  declenche UNIQUEMENT sur WATCHED confirme, horloge injectee (testable).
- `PlateSnapshotSink` + port `PlateSnapshotWriter` (plate/application) ;
  `LocalPlateSnapshotWriter` (plate/infrastructure/capture) : crop du vehicule,
  dossier par-plaque, fichier horodate `AAAAMMJJTHHMMSS_mmm_camera.jpg`.
- `PlateEmailAlertSink` (bootstrap, pont vers communication).
- `main.py` : email sender PARTAGE entre visages et plaques ; `_build_alerter`
  scinde en `_build_face_alerter` + `_build_plate_alerter` ; alerte plaque sur
  frame PROPRE (avant overlay) ; reutilise `--capture` / `--notify`.

Decisions:
- Alerte seulement sur WATCHED (pas SEEN) : pas de spam pour chaque voiture.
- Dedup par numero de plaque (pas par piste) : une plaque ne re-alerte pas avant
  `capture_cooldown_seconds`, meme si re-detectee.
- Captures plaques sous `capture_dir/plates/<plaque>/` (separe des visages).
- Sinks plaques distincts des sinks visages (BC-clean) ; seul `communication`
  (EmailSender) est mutualise, via le composition root.

Validation:
- 182 tests OK (PlateAlerter: WATCHED/SEEN/cooldown/apres-cooldown ;
  LocalPlateSnapshotWriter), ruff + mypy clean (81 fichiers).
- Preuve end-to-end : WATCHED 5AU5341 -> snapshot
  plates/5AU5341/<stamp>_jardin.jpg ; 2e appel debounce -> 1 seul fichier.

Remaining:
- Camera reelle : regler cooldown/retention ; politique de purge des captures.
- Option : joindre l'image de la plaque a l'email (aujourd'hui texte seul).

## 2026-10-16 — Strict minimum deploiement : mode headless + recette systemd

Goal:
- Rendre l'app deployable 24/7 sur VPS SANS ecran, avec redemarrage auto.
  (Logs structures juges NON necessaires : journald capture deja stdout.)

Changes:
- Config `headless` (+ CLI `--headless`). En headless : aucune fenetre OpenCV,
  dessin des overlays saute (inutile), boucle arretee par SIGINT/SIGTERM via
  `_install_stop()` -> arret PROPRE (camera relachee, files d'alertes videes).
  Alertes/captures tournent normalement (sur frame propre, avant tout dessin).
- `docs/DEPLOYMENT.md` : install, 1 fichier config/camera, `--headless`, unite
  systemd `Restart=always`, logs via `journalctl`, modele flotte (1 service/camera).

Decisions:
- La fenetre OpenCV etait OBLIGATOIRE -> bloquait tout deploiement serveur. Corrige.
- Minimum reel pour un deploiement fiable = headless + restart auto (systemd) +
  journald. Docker/logs structures/historique = confort, repousses (LIMITATIONS).

Validation:
- 211 tests OK, ruff + mypy clean (94 fichiers). (Boucle headless = chemin
  materiel, non couvert par les tests unitaires.)

## 2026-10-16 — Cap deploiement flotte : limites documentees + config fichier

Goal:
- Rendre l'app deployable sur une flotte (milliers de cameras / N serveurs) SANS
  reecriture distribuee ; documenter honnetement toutes les limites.

Decision d'architecture (ADR-010):
- Echelle = REPLICATION partage-de-rien : 1 instance = 1 (ou quelques) camera(s),
  configuree par FICHIER ; des milliers de cameras = des milliers d'instances sur
  N serveurs, chacune autonome. PAS de process multi-flux, PAS d'orchestrateur /
  DB / API centrale (YAGNI jusqu'a preuve de besoin). Orchestration deleguee a
  systemd/Docker/K8s.

Changes:
- `docs/LIMITATIONS.md` : limites PHYSIQUE / NON VALIDE / NON IMPLEMENTE / DETTE
  pour reco, detection, plaque, notifications, perf/echelle, exploitation, privacy.
- `docs/adr/ADR-010-modele-deploiement-echelle.md`.
- `bootstrap/config_file.load_app_config` : charge un AppConfig depuis un JSON
  (strict : cles inconnues rejetees ; listes -> tuples ; validation via __post_init__).
- `main.py` : option `--config fichier.json` (base declarative) ; les drapeaux CLI
  s'AJOUTENT (OR) et ne desactivent jamais ce que le fichier a active.
- `docs/examples/camera.example.json` (gabarit par camera).

DETTES TECHNIQUES actees (dependent d'elements externes) :
- Test sur vrai RTSP ; deploiement VPS Hostinger ; setup reel WhatsApp/Telegram.

Validation:
- 211 tests OK (loader : overrides, tuples, cle inconnue, valeur invalide, garde
  plates->detection, JSON malforme), ruff + mypy clean (94 fichiers).
- camera.example.json charge et valide.

Backlog de finalisation ORDONNE (sans materiel, prochaine etapes) :
  P1 logs structures -> P2 packaging Docker + mode service -> P3 confirmation
  plaque robuste (vote majoritaire) -> P4 historique d'evenements persistant
  (JSONL par instance) -> P5 feedback qualite a l'enrolement visage -> P6 Telegram.

## 2026-10-16 — Notifications push : chaine generique + WhatsApp Cloud API

Goal:
- Alerter l'operateur absent via push telephone, canal interchangeable (OCP),
  WhatsApp Cloud officiel en premier, Telegram trivial a ajouter ensuite.

Changes:
- communication/domain : `Alert` + `AlertImage` (purs, valides).
- communication/application : port `AlertNotifier` + `NotificationError`.
- communication/infrastructure :
  - `http_client` : port `HttpClient` + `UrllibHttpClient` (stdlib, multipart
    encode a la main) = transport HTTP GENERIQUE reutilise par tous les canaux.
  - `WhatsAppCloudChannel` (depend du port HttpClient -> testable sans reseau) :
    upload media puis message image+caption, ou texte seul ; `WhatsAppSettings.from_env`.
  - `HttpWebhookChannel` : POST JSON {title, body, image_base64} vers une URL (ntfy/Slack/custom).
  - `CompositeNotifier` (fan-out multi-canaux) ; `BackgroundNotifier` (file + thread,
    non bloquant, retry/log — miroir de BackgroundEmailSender).
- bootstrap : `NotifyingMatchSink` + `NotifyingPlateSink` (evenement -> Alert ->
  notifier) ; `image_jpeg.encode_jpeg` partage (DRY : email plaque refactore dessus).
- config : `whatsapp_enabled`, `webhook_url`. CLI : `--whatsapp`, `--webhook URL`.
  Email sender ET notifier fermes proprement en fin de run.

Decisions:
- Le canal d'alerte = un AlertNotifier derriere la meme file resiliente -> ajouter
  Telegram = un seul fichier, zero changement ailleurs (OCP/DIP).
- Email (SMTP) laisse tel quel (transport different) ; seuls les NOUVEAUX canaux
  HTTP partagent Alert/AlertNotifier/HttpClient.
- WhatsAppCloudChannel teste via faux HttpClient (texte, image 2-etapes, erreurs).

Validation:
- 205 tests OK, ruff + mypy clean (93 fichiers).

LIMITE IMPORTANTE (WhatsApp Cloud API):
- L'envoi FORME LIBRE (texte/image) n'est accepte par Meta que dans la fenetre
  de 24 h apres un message entrant du destinataire. Hors fenetre, Meta EXIGE un
  message "template" pre-approuve. L'implementation actuelle envoie en forme
  libre -> fiable si le destinataire a ecrit au numero business recemment, sinon
  il faudra ajouter le support des templates (TODO si besoin always-on).

DETTE TECHNIQUE (WhatsApp) — a date 2026-10-16 :
- Creation de l'app Meta + recuperation token/phone_id EN COURS (cote utilisateur).
- Envoi reel via l'API Cloud JAMAIS teste contre Meta (seulement via faux HttpClient).
- Forme libre limitee a la fenetre 24 h -> templates requis pour always-on : NON fait.
- File d'alertes en memoire : perdue si l'appli redemarre (pas de persistance).

Remaining:
- Telegram channel (meme port AlertNotifier).
- Option templates WhatsApp pour push always-on hors fenetre 24 h.

## 2026-10-16 — Image jointe a l'email + purge/retention des captures

Goal:
- (a) Joindre l'image de la plaque a l'email d'alerte. (b) Purger
  automatiquement les captures au-dela d'une duree de retention.

Changes (a) piece jointe:
- `EmailAttachment` (communication/domain, pur : filename, content_type,
  content bytes + validation ; proprietes maintype/subtype).
- `EmailMessage.attachments` (tuple, defaut vide -> texte seul inchange, OCP).
- `build_mime` ajoute chaque piece via `add_attachment`.
- `PlateEmailAlertSink` : crop vehicule -> `cv2.imencode` JPEG -> EmailAttachment.
- `image_crop.crop_box` partage par le writer de capture ET l'email (DRY).

Changes (b) retention:
- `CaptureRetention` (bootstrap) : `purge()` supprime les fichiers plus vieux
  que `max_age_seconds` sous `capture_dir` ; predicat pur `is_expired`, horloge
  injectee (testable).
- Config `capture_retention_seconds` (0 = desactive) + validation.
- `main.py` : purge au demarrage de session + periodique (toutes 300 s) via
  `_purge` / `_purge_if_due` ; actif seulement si capture activee et retention>0.

Decisions:
- EmailAttachment leve ValueError (pas d'import vers email_message) -> aucun
  cycle d'import dans le domaine.
- Purge throttlee (pas chaque frame) ; empty dirs laisses (YAGNI).
- Retention desactivee par defaut (0) : on ne supprime jamais les donnees de
  l'utilisateur sans choix explicite ; recommander une valeur en prod (§11).

Validation:
- 191 tests OK (EmailAttachment, build_mime texte/piece jointe, is_expired,
  purge selon mtime, root absent), ruff + mypy clean (84 fichiers).
- Preuve : email WATCHED 5AU5341 porte plate_5AU5341.jpg (image/jpeg, 2245 o) ;
  purge supprime le vieux fichier et garde le recent.

Remaining:
- Camera reelle : calibrer retention/cooldown et mesurer latence live.

------------------------------------------------------------------------

# 38. Handoff Update Checklist

Avant de quitter une session importante :

``` text
[ ] current objective updated
[ ] implementation state updated
[ ] decisions updated if necessary
[ ] validation recorded exactly
[ ] known issues updated
[ ] dependencies recorded
[ ] next action explicit
[ ] no unverified success claim
[ ] prompt de reprise still accurate
```

------------------------------------------------------------------------

# 39. Prompt de reprise universel

Copier ce prompt dans Claude Code, Codex ou un autre agent :

``` text
Tu reprends le développement de Sentinel Vision.

Travaille avec une rigueur de niveau senior et ne suppose rien sur l'état du
projet.

AVANT TOUT CODE :

1. Lis entièrement CLAUDE.md.
2. Lis entièrement ARCHITECTURE.md.
3. Lis entièrement DESIGN_SYSTEM.md.
4. Lis entièrement HANDOFF.md.
5. Lis README.md et les autres documents directement pertinents.
6. Inspecte git status et git diff.
7. Inspecte l'arborescence et le code réel.
8. Vérifie que la documentation correspond encore au code.

Le code actuel et les tests réellement exécutés sont la preuve finale.
HANDOFF.md est une mémoire de passation, pas une raison de supposer qu'une
fonctionnalité existe.

Principes obligatoires :

- KISS.
- YAGNI.
- DRY sur la connaissance, pas sur la simple ressemblance syntaxique.
- SOLID pragmatique.
- SRP.
- Tell Don't Ask lorsque cela améliore réellement le modèle.
- Clean Architecture sans cérémonial inutile.
- Le domaine ne dépend pas d'OpenCV, InsightFace, ONNX Runtime ou du renderer.
- Ne crée aucune abstraction spéculative.
- Ne crée aucune dépendance sans nécessité démontrée.
- Ne réécris pas une zone saine sans raison liée à la tâche.
- Ne fabrique aucune donnée, métrique, score ou état.
- Ne présente jamais une similarité comme une probabilité sans preuve.
- UNKNOWN doit rester distinct d'une panne technique.
- La vidéo live est prioritaire sur les effets UI.
- Performance et smoothness font partie du design.
- Respecte DESIGN_SYSTEM.md : look & feel premium inspiré MUI/Material,
  dark-first, calme, précis, faible charge cognitive, motion courte et utile,
  aucun HUD cyberpunk.
- Ne dégrade jamais les FPS pour une animation décorative.

Méthode :

READ
→ INSPECT
→ UNDERSTAND
→ VERIFY
→ IDENTIFY REDUNDANCY
→ REUSE
→ SIMPLIFY
→ IMPLEMENT
→ VALIDATE

Avant de modifier un fichier, comprends sa responsabilité et ses dépendances.

Avant d'ajouter une classe, interface, helper, abstraction ou dépendance,
cherche si le problème est déjà résolu dans le projet.

Travaille en tranche verticale minimale. Ne mélange pas une feature avec une
refonte générale non demandée.

Validation :

- exécute les tests et outils réellement disponibles dans le dépôt ;
- vérifie les imports et le démarrage ;
- teste le chemin modifié ;
- teste les états d'erreur pertinents ;
- si la boucle vidéo change, mesure l'impact lorsque possible ;
- si la reconnaissance change, vérifie au minimum no-face, unknown et
  potential-match avec des données autorisées ;
- si l'UI change, vérifie lisibilité, stabilité du layout et absence de
  régression de fluidité ;
- inspecte git diff et git diff --check si Git est utilisé.

Ne dis jamais qu'un test est réussi s'il n'a pas réellement été exécuté.
Distingue clairement inspection statique, test automatisé, test runtime,
test caméra, test visuel et mesure de performance.

À LA FIN :

1. Mets à jour HANDOFF.md avec uniquement les faits nouveaux.
2. Mets à jour Current Work / Last Completed Work.
3. Ajoute les décisions durables seulement si une vraie décision a été prise.
4. Ajoute les Known Issues réellement observés.
5. Indique précisément les validations exécutées et leurs résultats.
6. Indique ce qui n'a PAS pu être testé.
7. Donne la prochaine action recommandée.
8. Laisse le dépôt dans un état compréhensible pour l'agent suivant.

Compte rendu final attendu :

Implemented
Removed / Simplified
Architecture
UX / UI
Performance
Validation
Manual Test
Known Limitations
Dependencies
Remaining
```

------------------------------------------------------------------------

# 40. Règle finale pour tous les agents

Un agent qui reprend Sentinel Vision ne doit jamais chercher à montrer
qu'il peut produire beaucoup de code.

Il doit chercher à laisser le projet :

``` text
simpler
clearer
more coherent
more testable
more truthful
more maintainable
at least as fast as before
```

La meilleure reprise est celle où le prochain agent peut comprendre :

``` text
what exists
why it exists
what changed
what was tested
what remains
```

sans devoir reconstruire l'histoire du projet depuis les conversations
précédentes.

> **HANDOFF.md est la mémoire opérationnelle. Le code est la réalité.
> Les tests sont la preuve.**
