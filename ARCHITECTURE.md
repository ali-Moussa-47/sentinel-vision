# Sentinel Vision --- Architecture

> **Document vivant --- carte actuelle, jamais vérité éternelle.**
>
> Lire d'abord `.claude.md`. Ce document décrit l'architecture **la plus
> simple actuellement justifiée par les besoins et le code réel**. Il ne
> doit jamais figer le projet.
>
> Une architecture saine évolue avec les faits. Si le code, les tests,
> les mesures, une contrainte matérielle ou un besoin métier démontrent
> qu'une décision de ce document est devenue mauvaise, **il faut la
> remettre en question**.
>
> Claude Code, Codex, un développeur humain --- et même le prompt qui a
> produit ce document --- peuvent se tromper. Aucun texte n'a priorité
> sur une preuve reproductible. En revanche, une divergence ne se
> corrige jamais silencieusement : on démontre le problème, on choisit
> la solution la plus simple, on documente la décision durable, puis on
> met à jour ce document.

**Projet :** Sentinel Vision\
**État architectural :** architecture cible minimale du POC\
**Style :** monolithe modulaire local, Clean Architecture légère,
ports/adapters uniquement aux frontières qui varient réellement\
**Bounded Context métier initial :** `Recognition`

------------------------------------------------------------------------

## 0. Rôle de ce document

Ce fichier répond à quatre questions :

1.  **Quelles responsabilités existent aujourd'hui ?**
2.  **Où doivent-elles vivre ?**
3.  **Dans quelle direction les dépendances peuvent-elles aller ?**
4.  **Quels signaux justifieraient une évolution de l'architecture ?**

Il ne doit pas devenir :

-   un journal de session ;
-   une spécification UI ;
-   un catalogue de patterns ;
-   une roadmap spéculative ;
-   une duplication de `.claude.md`.

`.claude.md` définit la constitution d'ingénierie.\
`ARCHITECTURE.md` décrit la structure actuelle et les frontières.\
`DESIGN.md` décrira les décisions de conception détaillées et
l'expérience visuelle.\
`HANDOFF.md` décrira l'état opérationnel courant pour reprendre le
travail.

------------------------------------------------------------------------

# 1. Principe architectural fondamental

Sentinel Vision est actuellement un **POC local de vision par ordinateur
en temps réel**.

L'architecture doit donc optimiser pour :

-   compréhension rapide ;
-   boucle vidéo fluide ;
-   isolation des dépendances IA/vision ;
-   règles de reconnaissance testables sans webcam ;
-   remplacement possible du moteur technique ;
-   comportement déterministe ;
-   diagnostic simple ;
-   faible charge cognitive.

Elle ne doit **pas** optimiser aujourd'hui pour :

-   microservices ;
-   scalabilité horizontale ;
-   cloud distribué ;
-   multi-sites ;
-   multi-caméras ;
-   event streaming ;
-   stockage massif ;
-   orchestration Kubernetes ;
-   architecture « enterprise » hypothétique.

La règle est :

> **Monolithe modulaire d'abord. Extraction seulement lorsqu'une
> frontière réellement autonome apparaît.**

------------------------------------------------------------------------

# 2. Vue système

Flux nominal actuel :

``` text
┌──────────────┐
│   Webcam     │
└──────┬───────┘
       │ frame
       ▼
┌──────────────────┐
│ Frame Source     │  Infrastructure / OpenCV
└──────┬───────────┘
       │ observation visuelle
       ▼
┌──────────────────┐
│ Face Engine      │  Infrastructure / InsightFace
│ detect + embed   │
└──────┬───────────┘
       │ face observations + embeddings
       ▼
┌─────────────────────────────┐
│ Recognition Use Case        │  Application
│ orchestre, ne décide pas    │
└────────┬────────────────────┘
         │
         ├──────────────► Watchlist Port
         │                   │
         │                   ▼
         │              Local Watchlist
         │              Infrastructure
         │
         ▼
┌─────────────────────────────┐
│ Recognition Domain          │  Domain
│ similarity + decision       │
└────────┬────────────────────┘
         │ RecognitionResult
         ▼
┌──────────────────┐
│ Overlay Renderer │  Infrastructure / OpenCV
└────────┬─────────┘
         │
         ▼
     écran local
```

Le flux est linéaire par défaut.

**Aucun bus d'événements, queue, worker pool ou pipeline concurrent
n'est introduit tant qu'une mesure ne démontre pas que ce flux simple
est insuffisant.**

------------------------------------------------------------------------

# 3. Bounded Contexts

## 3.1 BC-01 --- Recognition

**Statut : actif.**

Responsabilité :

> Transformer une observation faciale exploitable en une décision de
> reconnaissance par comparaison avec une watchlist locale explicitement
> constituée pour la démonstration.

Langage métier :

-   `Watchlist`
-   `WatchlistSubject`
-   `FaceEmbedding`
-   `SimilarityScore`
-   `RecognitionThreshold`
-   `RecognitionDecision`
-   `PotentialMatch`
-   `Unknown`

Le BC est propriétaire :

-   de la sémantique d'un score ;
-   de la politique de décision ;
-   de la notion de sujet de watchlist ;
-   du résultat métier `MATCH_POTENTIEL` / `UNKNOWN`.

Le BC **n'est pas propriétaire** :

-   de la webcam ;
-   d'OpenCV ;
-   d'InsightFace ;
-   d'ONNX Runtime ;
-   de l'affichage ;
-   du filesystem ;
-   du format physique d'une image.

## 3.2 Pourquoi un seul BC

À ce stade, séparer `Detection`, `Embedding`, `Watchlist`, `Camera` ou
`UI` en Bounded Contexts serait une erreur de modélisation.

Ce sont actuellement :

-   des étapes techniques ;
-   des adapters ;
-   ou des responsabilités internes du même flux métier.

Un dossier n'est pas un BC.\
Une bibliothèque n'est pas un BC.\
Une étape de pipeline n'est pas automatiquement un BC.

## 3.3 Gate de création d'un nouveau BC

Avant de créer un second BC, documenter au minimum :

1.  son vocabulaire propre ;
2.  ses invariants propres ;
3.  sa raison de changer indépendante ;
4.  la frontière de données avec `Recognition` ;
5.  pourquoi un module interne ne suffit plus ;
6.  le coût concret du maintien dans le BC existant.

Sans démonstration convaincante : rester dans `Recognition`.

------------------------------------------------------------------------

# 4. Couches

## 4.1 Domain

Le domaine est le centre.

Il contient uniquement des concepts et comportements métier purs.

Exemples plausibles :

``` text
recognition/domain/
├── face_embedding.py
├── similarity_score.py
├── recognition_threshold.py
├── recognition_decision.py
├── watchlist_subject.py
└── recognition_policy.py
```

**Ce sont des exemples, pas une obligation de créer tous ces fichiers.**
Créer un fichier seulement lorsqu'un concept réel existe.

Le domaine peut dépendre :

-   de la bibliothèque standard Python ;
-   éventuellement de types mathématiques neutres strictement
    nécessaires, après justification.

Le domaine ne dépend jamais de :

``` text
cv2
insightface
onnxruntime
UI
filesystem
camera
network
framework DI
```

### Invariant d'indépendance

Cette commande conceptuelle doit rester possible :

``` text
tests domaine → aucune webcam → aucun modèle IA → aucun écran
```

Si tester une règle de matching exige de charger InsightFace, la
frontière est mauvaise.

------------------------------------------------------------------------

## 4.2 Application

La couche application orchestre.

Exemples de responsabilités :

-   demander des observations au moteur de visage ;
-   récupérer les sujets de watchlist via un port ;
-   invoquer la politique de reconnaissance ;
-   retourner un résultat utilisable par la présentation.

Elle ne doit pas :

-   calculer elle-même une règle métier qui appartient au domaine ;
-   connaître `cv2.VideoCapture` ;
-   connaître `FaceAnalysis` d'InsightFace ;
-   dessiner des rectangles ;
-   lire directement des dossiers ;
-   choisir arbitrairement un seuil.

Structure possible :

``` text
recognition/application/
├── recognize_frame.py
└── ports/
    ├── face_analysis_port.py
    └── watchlist_port.py
```

Là encore : **pas d'interface cérémonielle**.

Un port est créé lorsqu'il protège réellement le cœur contre une
dépendance externe ou une variation significative.

------------------------------------------------------------------------

## 4.3 Infrastructure

L'infrastructure adapte le monde extérieur aux contrats internes.

Responsabilités initiales possibles :

``` text
recognition/infrastructure/
├── vision/
│   └── insightface_face_analyzer.py
├── watchlist/
│   └── local_watchlist.py
└── presentation/
    └── opencv_overlay_renderer.py

bootstrap/
├── opencv_camera.py
└── main.py
```

La structure exacte peut évoluer si le code réel montre une organisation
plus simple.

L'infrastructure peut connaître :

-   OpenCV ;
-   InsightFace ;
-   ONNX Runtime ;
-   NumPy ;
-   filesystem ;
-   configuration technique.

Elle traduit ces concepts vers le vocabulaire interne.

Elle ne doit jamais faire remonter les objets propres à InsightFace
jusque dans le domaine.

------------------------------------------------------------------------

# 5. Dependency Rule

Direction autorisée :

``` text
presentation/bootstrap ─┐
infrastructure ─────────┼────► application ─────► domain
                       │
                       └──── implémente les ports
```

Direction interdite :

``` text
domain ─X─► application
domain ─X─► infrastructure
application ─X─► infrastructure concrète
application ─X─► OpenCV
application ─X─► InsightFace
```

Le composition root est l'exception volontaire :

``` text
bootstrap/main.py
```

Il connaît les implémentations concrètes afin de les assembler.

**Il ne contient aucune règle métier.**

------------------------------------------------------------------------

# 6. Ports et adapters

## 6.1 Principe

Ports/adapters ne signifie pas « interface partout ».

Un port existe lorsqu'il y a une vraie frontière.

Ports probablement justifiés au départ :

### `FaceAnalyzer`

Pourquoi :

-   InsightFace est une dépendance externe lourde ;
-   son API ne doit pas contaminer l'application ;
-   un moteur différent doit pouvoir être substitué ;
-   les tests applicatifs doivent pouvoir utiliser un fake léger.

Contrat conceptuel :

``` text
frame → FaceObservation[]
```

### `Watchlist`

Pourquoi :

-   le cas d'usage a besoin de sujets connus ;
-   le stockage local est un détail ;
-   le domaine ne doit pas lire le filesystem.

Contrat conceptuel :

``` text
list subjects
```

## 6.2 Ce qui n'a probablement pas besoin d'un port aujourd'hui

Ne pas créer automatiquement :

-   `SimilarityCalculatorPort` si le calcul est pur et interne ;
-   `RecognitionPolicyPort` si la policy est du domaine ;
-   `ConfigRepository` pour trois valeurs ;
-   `EventPublisher`;
-   `UnitOfWork`;
-   `CameraRepository`.

Si un besoin futur le justifie, l'architecture évoluera.

------------------------------------------------------------------------

# 7. Modèle de données interne

## 7.1 FaceEmbedding

Concept :

> représentation numérique d'un visage produite par le moteur technique
> et utilisée pour une comparaison.

Le domaine ne doit pas dépendre du type concret renvoyé par InsightFace.

À la frontière infrastructure/application, convertir vers une
représentation interne stable.

Ne pas exposer :

``` text
insightface.app.common.Face
```

au-delà de l'adapter.

## 7.2 WatchlistSubject

Représente un sujet volontairement enregistré pour la démonstration.

Identité conceptuelle minimale :

``` text
subject_id
display_label
reference_embedding(s)
```

Ne pas ajouter adresse, téléphone, metadata ou profil complet sans
besoin réel.

## 7.3 SimilarityScore

Un score est une mesure, pas une décision.

Invariant :

``` text
score != MATCH
```

La décision résulte de :

``` text
score + politique + seuil
```

## 7.4 RecognitionResult

Le résultat exposé à la présentation doit être suffisamment riche pour
afficher l'information sans recalcul métier.

Exemple conceptuel :

``` text
RecognitionResult
├── decision: POTENTIAL_MATCH | UNKNOWN
├── score
├── subject_id?       # seulement si match potentiel
├── display_label?    # seulement si nécessaire à la démo
└── bounding_box
```

Le `bounding_box` est une information d'observation/presentation ; si
son placement dans le résultat métier alourdit le domaine, il peut
rester dans un DTO applicatif séparé.

**Cette frontière doit être décidée par le code réel, pas figée ici.**

------------------------------------------------------------------------

# 8. Pipeline temps réel

Pipeline minimal :

``` text
1. Acquire frame
2. Validate acquisition
3. Detect faces
4. Extract embeddings
5. Compare against watchlist
6. Decide
7. Render
8. Display
9. Repeat
```

Le pipeline reste **synchrone** tant qu'il respecte la fluidité
nécessaire à la démonstration.

## 8.1 Pas de concurrence préventive

Ne pas introduire par anticipation :

-   thread caméra ;
-   thread inference ;
-   multiprocessing ;
-   async pipeline ;
-   queue de frames ;
-   double buffering maison.

Ces mécanismes augmentent :

-   états concurrents ;
-   latence cachée ;
-   frames périmées ;
-   difficulté de shutdown ;
-   flakiness ;
-   charge cognitive.

### Signal autorisant une évolution

Après mesure, si l'inférence bloque réellement l'acquisition ou le
rendu, une ADR peut comparer :

-   frame skipping ;
-   réduction de résolution ;
-   cadence d'inférence ;
-   thread dédié ;
-   pipeline borné latest-frame-wins.

La solution la plus simple qui satisfait la mesure gagne.

------------------------------------------------------------------------

# 9. Stratégie de watchlist

## 9.1 Version initiale

La watchlist est locale et petite.

Objectif : démonstration contrôlée.

Stockage acceptable initialement :

``` text
data/watchlist/
└── <subject>/
    └── images de référence locales
```

Le format exact sera défini au moment de l'implémentation.

Les vraies données de démonstration :

-   restent locales ;
-   ne sont pas commitées ;
-   ne sont pas téléchargées automatiquement ;
-   ne sont pas enrichies depuis Internet.

## 9.2 Pré-calcul

Si le profilage montre que recalculer les embeddings de référence au
démarrage est inutilement coûteux, un cache local d'embeddings peut être
introduit.

Mais :

> **pas de cache avant d'avoir un coût réel à cacher.**

Si un cache est ajouté, il doit définir clairement :

-   format/version ;
-   invalidation ;
-   compatibilité avec le modèle ;
-   comportement en cas de corruption.

------------------------------------------------------------------------

# 10. Matching

La décision de matching est une règle métier critique.

Séparer strictement :

``` text
distance/similarité mathématique
        ↓
SimilarityScore
        ↓
RecognitionPolicy
        ↓
RecognitionDecision
```

## 10.1 Seuil

Le seuil :

-   a une source unique ;
-   est explicite ;
-   est testable ;
-   n'est pas dupliqué dans l'UI ;
-   n'est pas modifié automatiquement pour améliorer une démonstration.

## 10.2 Plusieurs candidats

Si plusieurs sujets dépassent le seuil, le comportement doit être
déterministe.

La politique exacte sera spécifiée et testée lorsqu'elle devient
nécessaire, par exemple :

``` text
meilleur score valide
```

avec traitement explicite des ambiguïtés si les données réelles montrent
que c'est nécessaire.

Ne pas inventer aujourd'hui un moteur complexe de résolution
d'ambiguïté.

## 10.3 UNKNOWN

`UNKNOWN` signifie :

> aucune correspondance n'a satisfait la politique de reconnaissance.

Cela ne signifie pas :

-   absence de visage ;
-   erreur caméra ;
-   échec d'inférence ;
-   embedding invalide.

Ces états doivent rester distincts.

------------------------------------------------------------------------

# 11. Erreurs

Taxonomie minimale :

``` text
AcquisitionFailure
ModelInitializationFailure
FaceAnalysisFailure
WatchlistLoadFailure
InvalidRecognitionInput
```

Les noms exacts peuvent changer.

Principe plus important que les classes :

> une panne technique ne doit jamais devenir silencieusement un résultat
> métier.

Exemple interdit :

``` text
InsightFace plante → afficher UNKNOWN
```

Cela donne une information fausse à l'utilisateur.

------------------------------------------------------------------------

# 12. Composition root

`bootstrap/main.py` doit rester banal.

Responsabilités :

1.  charger la configuration ;
2.  construire les adapters ;
3.  construire les use cases ;
4.  ouvrir les ressources ;
5.  lancer la boucle ;
6.  assurer le cleanup.

Conceptuellement :

``` text
config
  ↓
InsightFaceAdapter
LocalWatchlistAdapter
RecognitionUseCase
OpenCVCamera
OpenCVRenderer
  ↓
run()
```

Pas de Service Locator global.\
Pas de conteneur DI tant que l'injection explicite reste lisible.

------------------------------------------------------------------------

# 13. Configuration

Configuration initiale possible :

``` text
camera_index
model_name
watchlist_path
recognition_threshold
```

Règles :

-   source unique ;
-   valeurs par défaut explicites ;
-   aucune duplication ;
-   aucune valeur métier critique enfouie dans l'overlay.

Une simple dataclass/configuration Python suffit au départ.

Pas de framework de configuration sans nécessité.

------------------------------------------------------------------------

# 14. Frontière NumPy

NumPy sera probablement nécessaire techniquement.

Il ne faut pas transformer cette réalité en fuite architecturale
incontrôlée.

Décision pragmatique :

-   infrastructure : NumPy librement si nécessaire ;
-   application : représentation neutre ou NumPy uniquement si cela
    évite une copie/coût important démontré ;
-   domaine : préférer des types métier qui cachent le détail de
    représentation.

Ne pas copier des embeddings à chaque couche uniquement pour « purifier
» l'architecture.

**La Dependency Rule protège les responsabilités, pas une pureté
théorique au prix des performances.**

Si une optimisation exige une concession, la mesurer et la documenter.

------------------------------------------------------------------------

# 15. Présentation

La présentation reçoit un résultat déjà décidé.

Elle peut décider :

-   couleur ;
-   texte ;
-   position ;
-   épaisseur ;
-   informations visibles.

Elle ne peut pas décider :

``` text
if score > 0.55: MATCH
```

La présentation ne connaît pas la politique de matching.

Exemple conceptuel :

``` text
POTENTIAL_MATCH → label + score + bounding box
UNKNOWN         → UNKNOWN + bounding box
ERROR           → état technique distinct
```

Les détails visuels appartiendront à `DESIGN.md`.

------------------------------------------------------------------------

# 16. Tests par couche

## Domain

Tests purs :

-   score ;
-   seuil ;
-   match ;
-   unknown ;
-   bornes ;
-   candidats multiples si supportés ;
-   invariants des objets métier.

Aucun mock framework nécessaire pour des objets purs.

## Application

Tester l'orchestration avec fakes/stubs des ports.

Vérifier notamment :

-   zéro visage ;
-   un visage ;
-   plusieurs visages ;
-   watchlist vide ;
-   erreur adapter ;
-   propagation/traduction correcte des erreurs.

## Infrastructure

Tests ciblés :

-   adapter InsightFace ;
-   parsing des résultats ;
-   chargement watchlist ;
-   caméra lorsque matériel disponible ;
-   cleanup OpenCV.

Ne pas faire dépendre `pytest` unitaire d'une webcam physique.

## End-to-end local

Un test manuel reproductible peut être légitime pour :

``` text
webcam réelle → modèle réel → sujet volontaire → overlay réel
```

Il complète les tests automatiques ; il ne les remplace pas.

------------------------------------------------------------------------

# 17. Contrats architecturaux exécutables

Lorsque la structure devient assez stable pour que le bénéfice dépasse
le coût, ajouter des tests automatisés empêchant :

``` text
domain imports cv2
domain imports insightface
application imports infrastructure
```

Ne pas installer un framework architectural lourd uniquement pour cela.

Un test Python simple inspectant les imports peut suffire.

L'architecture doit être protégée **par le moyen le plus simple
adéquat**.

------------------------------------------------------------------------

# 18. Performance

## 18.1 Mesurer le pipeline

Lorsque M6 est atteint, mesurer au minimum :

``` text
capture time
face-analysis time
matching time
render time
frame total
FPS observé
```

Pas besoin d'une plateforme d'observabilité.

Des mesures locales structurées suffisent.

## 18.2 Budget

Aucun chiffre artificiel n'est figé avant mesure sur la machine de
démonstration.

Une cible de performance ne devient contractuelle qu'après :

1.  mesure réelle ;
2.  identification du matériel ;
3.  observation de l'expérience ;
4.  décision documentée.

## 18.3 Optimisation

Ordre préféré :

``` text
algorithme / fréquence d'inférence
        ↓
résolution
        ↓
copies mémoire
        ↓
configuration runtime
        ↓
concurrence
        ↓
accélération GPU spécialisée
```

Ce n'est pas une loi absolue. C'est un ordre de recherche raisonnable
qui doit être contesté si les mesures disent autre chose.

------------------------------------------------------------------------

# 19. Sécurité et confidentialité architecturales

Le POC traite une donnée biométrique sensible.

L'architecture initiale minimise donc volontairement la surface :

``` text
caméra locale
   ↓
processus local
   ↓
watchlist locale consentie
   ↓
affichage local
```

Pas de réseau requis dans le chemin nominal.

Pas de persistance automatique des inconnus.

Pas de journal contenant des embeddings.

Pas de dump de frames dans les logs.

Pas de télémétrie biométrique.

Si une future feature introduit réseau, stockage ou partage, elle exige
une nouvelle analyse architecturale et de confidentialité avant
implémentation.

------------------------------------------------------------------------

# 20. Observabilité

Pour le POC :

-   logs structurés simples ;
-   niveaux cohérents ;
-   aucune donnée biométrique brute ;
-   erreurs techniques actionnables.

Exemples utiles :

``` text
camera opened
model initialized
watchlist loaded: N subjects
frame acquisition failed
face analyzer failed
```

Exemples interdits :

``` text
embedding=[0.1234, ...]
full raw frame dumped
```

Ne pas introduire OpenTelemetry/Prometheus avant besoin réel.

------------------------------------------------------------------------

# 21. Structure cible du dépôt

``` text
sentinel-vision/
├── src/
│   └── sentinel_vision/
│       ├── recognition/
│       │   ├── domain/
│       │   ├── application/
│       │   │   └── ports/
│       │   └── infrastructure/
│       │       ├── vision/
│       │       ├── watchlist/
│       │       └── presentation/
│       └── bootstrap/
├── tests/
│   ├── unit/
│   │   ├── recognition/
│   │   │   ├── domain/
│   │   │   └── application/
│   └── integration/
│       └── recognition/
├── data/
│   └── watchlist/
├── docs/
│   └── adr/
├── .claude.md
├── ARCHITECTURE.md
├── DESIGN.md
├── HANDOFF.md
├── pyproject.toml
└── README.md
```

### Règle importante

Cette arborescence est une **destination logique**, pas un ordre de
créer vingt dossiers vides.

> Un dossier vide n'est pas de l'architecture.

Créer les éléments au rythme du code réel.

------------------------------------------------------------------------

# 22. Dépendances autorisées par zone

  ---------------------------------------------------------------------------------
  Zone                            Peut dépendre de          Ne doit pas dépendre de
  ------------------------------- ------------------------- -----------------------
  `domain`                        stdlib, abstractions      OpenCV, InsightFace,
                                  métier                    ONNX, filesystem, UI

  `application`                   `domain`, ports           adapters concrets,
                                                            OpenCV UI

  `infrastructure/vision`         application/domain        règles métier nouvelles
                                  contracts,                
                                  InsightFace/ONNX/OpenCV   
                                  si nécessaire             

  `infrastructure/watchlist`      application/domain        présentation
                                  contracts, filesystem     

  `infrastructure/presentation`   DTO/résultats             décision de matching
                                  applicatifs, OpenCV       

  `bootstrap`                     toutes les                règles métier
                                  implémentations           
                                  nécessaires à la          
                                  composition               
  ---------------------------------------------------------------------------------

Cette table est un garde-fou, pas une prison.

Une exception peut devenir légitime, mais elle doit être démontrée et
documentée.

------------------------------------------------------------------------

# 23. Architecture Decision Records

Créer une ADR uniquement pour une décision durable et coûteuse à
inverser.

Exemples :

-   passage du pipeline synchrone à un pipeline concurrent ;
-   introduction d'un second BC ;
-   changement du moteur de reconnaissance ;
-   stockage persistant d'embeddings ;
-   introduction d'une API réseau ;
-   ajout GPU/TensorRT ;
-   passage multi-caméras.

Format :

``` text
# ADR-XXX — Titre

## Contexte
Faits et problème observé.

## Forces
Contraintes réelles.

## Options
Options réellement considérées.

## Décision
Choix et justification.

## Conséquences
Bénéfices, coûts, risques.

## Preuves
Tests, benchmarks, mesures ou incident qui motivent la décision.
```

Pas d'ADR pour renommer une variable.

------------------------------------------------------------------------

# 24. Signaux d'évolution

## Vers plusieurs processus

Seulement si :

-   l'isolation du modèle est nécessaire ;
-   les crashes du moteur doivent être contenus ;
-   ou les mesures montrent un bénéfice net.

## Vers GPU

Seulement si :

-   CPU insuffisant mesuré ;
-   matériel cible connu ;
-   bénéfice démontré.

## Vers backend

Seulement si un besoin réel apparaît :

-   administration distante ;
-   synchronisation ;
-   audit centralisé ;
-   configuration distante ;
-   intégration externe.

## Vers base de données

Seulement si le filesystem local ne satisfait plus :

-   volume ;
-   recherche ;
-   intégrité ;
-   concurrence ;
-   audit ;
-   gestion transactionnelle.

## Vers second BC

Seulement selon le gate §3.3.

------------------------------------------------------------------------

# 25. Ce qui doit rester facile à remplacer

Les seams architecturaux les plus importants sont :

``` text
Camera source
Face analysis engine
Watchlist storage
Recognition policy/configuration
Renderer
```

Mais « remplaçable » ne signifie pas nécessairement « interface dédiée
dès maintenant ».

Créer le seam au moment où il protège :

-   une dépendance externe ;
-   un test ;
-   ou une variation réelle.

------------------------------------------------------------------------

# 26. SRP au niveau fichier

Un fichier doit avoir une responsabilité nommable précisément.

Bon :

``` text
insightface_face_analyzer.py
local_watchlist.py
recognize_frame.py
recognition_policy.py
opencv_overlay_renderer.py
```

À surveiller :

``` text
services.py
utils.py
helpers.py
managers.py
vision.py   # si capture + IA + matching + rendu
```

Un fichier n'est pas découpé parce qu'il dépasse arbitrairement N
lignes.

Il est découpé lorsque plusieurs raisons de changer apparaissent.

------------------------------------------------------------------------

# 27. Règle de review architecturale pour Claude Code et Codex

Avant toute modification structurante, l'agent doit vérifier :

``` text
1. Quel problème réel est observé ?
2. Dans quelle responsabilité vit-il ?
3. Est-ce un problème métier ou technique ?
4. Une solution locale suffit-elle ?
5. Introduisons-nous une nouvelle dépendance ?
6. Créons-nous une nouvelle raison de changer ?
7. Le changement traverse-t-il une frontière ?
8. Le test peut-il prouver le comportement ?
9. La mesure peut-elle prouver le besoin de performance ?
10. L'architecture actuelle est-elle réellement le problème ?
```

Puis choisir le plus petit changement correct.

------------------------------------------------------------------------

# 28. Droit explicite de contredire l'architecture

**Cette section est non négociable.**

Claude Code, Codex et les développeurs ont le droit --- et parfois le
devoir --- de dire :

> « Cette règle d'architecture semble incorrecte au regard du code réel.
> »

Mais ils doivent apporter une preuve.

Preuves acceptables :

-   test qui échoue ;
-   cycle de dépendance réel ;
-   duplication réelle ;
-   benchmark ;
-   profilage ;
-   bug reproductible ;
-   invariant métier nouveau ;
-   contrainte de bibliothèque vérifiée ;
-   simplification démontrable ;
-   besoin utilisateur explicite.

Preuves insuffisantes :

-   « c'est plus moderne » ;
-   « c'est une best practice » ;
-   « on fait généralement comme ça » ;
-   « ce sera utile plus tard » ;
-   préférence personnelle ;
-   suggestion non vérifiée d'un LLM.

Procédure :

``` text
Observer
   ↓
Reproduire / mesurer
   ↓
Expliquer la contradiction
   ↓
Proposer la solution minimale
   ↓
Tester
   ↓
ADR si décision durable
   ↓
Mettre ARCHITECTURE.md à jour
```

**Ne jamais tordre le code pour respecter une phrase devenue fausse dans
ce document. Corriger la phrase.**

------------------------------------------------------------------------

# 29. Architecture fitness review

À chaque milestone importante, faire une revue courte :

### Frontières

-   Le domaine reste-t-il indépendant ?
-   InsightFace/OpenCV fuient-ils vers le cœur ?
-   Une responsabilité a-t-elle grossi au point de devenir autonome ?

### Couplage

-   Des imports circulaires sont-ils apparus ?
-   Une feature nécessite-t-elle plusieurs raisons de changer ?
-   Une abstraction a-t-elle plus de coût que de valeur ?

### Tests

-   Les règles métier sont-elles testables sans matériel ?
-   Les adapters lourds sont-ils isolés ?
-   Des tests deviennent-ils lents à cause d'une mauvaise frontière ?

### Performance

-   Où est réellement le temps ?
-   Avons-nous optimisé sans mesurer ?

### Complexité

-   Peut-on expliquer le flux en quelques minutes ?
-   Combien de fichiers faut-il ouvrir pour comprendre une
    reconnaissance ?
-   Avons-nous ajouté un pattern alors qu'une fonction suffisait ?

Si la charge cognitive augmente sans gain démontré, simplifier.

------------------------------------------------------------------------

# 30. Definition of Architectural Done

Un changement architectural est acceptable lorsque :

-   il répond à un problème actuel démontré ;
-   sa responsabilité est claire ;
-   la direction des dépendances reste cohérente ;
-   les frontières sont testables ;
-   le diff ne construit pas des besoins futurs imaginaires ;
-   aucune donnée biométrique supplémentaire n'est exposée sans
    justification ;
-   les performances ont été mesurées si elles motivent le changement ;
-   une solution plus simple a été considérée ;
-   les tests pertinents sont verts ;
-   la documentation reflète le code après le changement ;
-   une ADR existe si le choix est durable/coûteux à inverser.

------------------------------------------------------------------------

# 31. Carte de démarrage rapide

Pour comprendre le projet, suivre cet ordre :

``` text
.claude.md
    ↓
ARCHITECTURE.md
    ↓
recognition/domain
    ↓
recognition/application
    ↓
ports
    ↓
adapters infrastructure
    ↓
bootstrap/main.py
    ↓
tests
```

Pour comprendre un bug, partir du comportement observé et remonter le
flux.

Ne pas commencer par refactorer l'arborescence.

------------------------------------------------------------------------

# 32. Architecture actuelle en une phrase

> **Sentinel Vision est un monolithe modulaire local avec un seul
> Bounded Context `Recognition`, un domaine pur pour la décision de
> reconnaissance, une application qui orchestre, des adapters qui
> encapsulent OpenCV/InsightFace et un composition root minimal ---
> architecture volontairement simple, mesurable, testable et
> explicitement autorisée à évoluer lorsque les faits invalident ses
> hypothèses.**

------------------------------------------------------------------------

# 33. Règle ultime

L'architecture n'est pas le dessin.

L'architecture est l'ensemble des décisions qui rendent les changements
importants faciles, sûrs et compréhensibles.

Par conséquent :

> **ne jamais préserver l'architecture contre la réalité.\
> Préserver les invariants, mesurer les faits, puis faire évoluer
> l'architecture.**

Même ce document doit pouvoir être supprimé, réécrit ou simplifié si le
projet réel démontre qu'il est devenu un obstacle plutôt qu'une aide.
