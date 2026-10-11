# Sentinel Vision --- Constitution d'ingénierie

**Statut : document de référence opposable pour le dépôt.**\
Toute modification de code, test, dépendance, structure ou comportement
doit respecter ce document. En cas de conflit entre une préférence
d'agent, un commentaire ponctuel ou une implémentation improvisée et ce
document, ce document prévaut jusqu'à amendement explicite.

**Projet :** Sentinel Vision\
**Nature actuelle :** POC local de vision par ordinateur en temps réel,
destiné à une démonstration avec des personnes volontaires.\
**Langage :** Python 3.13\
**Stack initiale autorisée :** OpenCV, InsightFace, ONNX Runtime, NumPy
et dépendances transitives strictement nécessaires.\
**Principe directeur :** qualité d'ingénierie élevée, complexité
minimale.

------------------------------------------------------------------------

## 0. Gouvernance

Ce document définit les règles de travail de Claude Code, Codex et de
tout autre agent intervenant sur le dépôt.

### 0.1 Hiérarchie des sources

Ordre d'autorité :

1.  exigences explicites de l'utilisateur ;
2.  `.claude.md` ;
3.  `ARCHITECTURE.md` ;
4.  `DESIGN.md` ;
5.  `HANDOFF.md` ;
6.  tests exécutables ;
7.  code existant ;
8.  commentaires et préférences d'implémentation.

Un document inférieur ne peut pas contredire un document supérieur.

### 0.2 Amendements

Ne jamais modifier une règle structurante silencieusement.

Toute décision qui change une frontière, une dépendance majeure, un
invariant, une stratégie de test ou une règle de ce document doit être
justifiée par une ADR courte :

-   contexte concret ;
-   problème observé ;
-   options réellement considérées ;
-   décision ;
-   conséquences ;
-   date.

Pas d'ADR pour une décision locale triviale.

### 0.3 Preuve avant affirmation

Un agent ne doit jamais annoncer :

-   « ça compile » sans l'avoir exécuté ;
-   « les tests passent » sans les avoir exécutés ;
-   « cette dépendance est nécessaire » sans démontrer le besoin ;
-   « cette architecture est meilleure » sans expliquer le problème
    concret qu'elle résout.

Le dépôt réel et les commandes exécutées sont la source de vérité.

------------------------------------------------------------------------

# 1. Vision du produit

Sentinel Vision est d'abord un **POC local et démontrable**.

Objectif initial :

> Capturer un flux webcam en temps réel, détecter les visages présents
> et comparer leurs représentations biométriques à une petite watchlist
> de démonstration constituée de personnes volontaires afin d'afficher
> `MATCH POTENTIEL` ou `UNKNOWN`.

Le produit doit privilégier :

-   fluidité du flux vidéo ;
-   simplicité d'installation ;
-   déterminisme ;
-   lisibilité du résultat ;
-   faible latence ;
-   comportement explicable ;
-   faible charge cognitive du code ;
-   capacité à remplacer un composant technique sans contaminer le
    métier.

## 1.1 Hors périmètre actuel

Tant qu'un besoin concret ne le justifie pas, ne pas construire :

-   backend HTTP ;
-   FastAPI ;
-   frontend React ;
-   base de données ;
-   Kafka/RabbitMQ ;
-   Redis ;
-   Docker/Kubernetes ;
-   microservices ;
-   authentification ;
-   cloud ;
-   DeepStream/TensorRT/CUDA ;
-   stockage vidéo permanent ;
-   reconnaissance de plaques ;
-   détection de véhicules ;
-   multi-caméras ;
-   système distribué ;
-   infrastructure de police ;
-   scraping ou collecte de données biométriques ;
-   identification de personnes non consentantes.

Ces capacités ne sont pas « prévues d'avance ». Elles sont **absentes**
jusqu'à apparition d'un besoin réel.

YAGNI est une contrainte architecturale.

------------------------------------------------------------------------

# 2. Invariants fonctionnels initiaux

Les règles suivantes sont non négociables pour la première version.

1.  La caméra est une source de frames, pas une dépendance du domaine.
2.  Le domaine ne connaît ni `cv2`, ni InsightFace, ni ONNX Runtime.
3.  Une identité de démonstration est explicitement enregistrée dans la
    watchlist locale.
4.  Une détection sans correspondance suffisante produit `UNKNOWN`.
5.  Une correspondance n'est jamais présentée comme une certitude
    absolue.
6.  Le score brut et le seuil de décision sont deux concepts distincts.
7.  Le seuil ne doit jamais être abaissé arbitrairement pour « faire
    marcher la démo ».
8.  Une frame illisible, un visage trop petit ou une erreur technique ne
    doit pas être transformé artificiellement en match.
9.  Une erreur de caméra ou de modèle échoue explicitement ; pas de
    `except: pass`.
10. Aucun visage, embedding ou frame n'est persisté par défaut.
11. Le POC fonctionne localement sans dépendre d'un service cloud.
12. Les personnes de la watchlist de démonstration doivent être
    volontaires.
13. Le moteur de reconnaissance doit être remplaçable sans réécrire le
    cas d'usage.
14. Le rendu visuel ne décide jamais du résultat métier ; il ne fait que
    l'afficher.
15. Une optimisation ne peut pas changer silencieusement le comportement
    fonctionnel.

------------------------------------------------------------------------

# 3. Philosophie d'architecture

L'objectif n'est pas d'obtenir « le plus d'architecture possible ».

L'objectif est :

> **le minimum d'architecture capable de protéger les vraies
> responsabilités du système.**

Les principes SOLID, DDD, TDA, DRY, YAGNI, KISS, SRP, OCP et TDD sont
des moyens, jamais des objectifs décoratifs.

## 3.1 KISS

Toujours chercher la solution correcte la plus simple.

Avant d'ajouter :

-   une interface ;
-   une classe abstraite ;
-   un pattern ;
-   un bus ;
-   un événement ;
-   une factory ;
-   un repository ;
-   un service ;
-   une couche ;

l'agent doit pouvoir répondre :

> Quel problème réel, actuel et vérifiable cette abstraction résout-elle
> ?

Sans réponse concrète : ne pas l'ajouter.

## 3.2 YAGNI

Ne jamais construire une extension uniquement parce qu'elle « pourrait
servir plus tard ».

Une extension future doit rester possible grâce à de bonnes frontières,
pas grâce à du code mort anticipatif.

## 3.3 SRP

Une unité de code possède une seule raison métier ou technique cohérente
de changer.

Exemples :

-   acquisition caméra : acquisition uniquement ;
-   moteur InsightFace : adaptation InsightFace uniquement ;
-   matching : décision de similarité uniquement ;
-   overlay : présentation uniquement ;
-   use case : orchestration uniquement.

Une classe qui capture la caméra, reconnaît, décide, dessine et
sauvegarde viole SRP.

## 3.4 OCP

OCP signifie ici :

> un changement raisonnablement attendu doit pouvoir être introduit
> principalement par addition ou remplacement derrière une frontière
> stable.

Exemple légitime : remplacer InsightFace par un autre moteur sans
modifier le cas d'usage.

OCP ne justifie pas dix interfaces pour une seule fonction stable.

## 3.5 DIP

Les dépendances pointent vers le cœur.

``` text
Infrastructure ──────► Application ──────► Domain
      │
      └──── implémente les ports définis vers l'intérieur
```

Interdictions :

-   `domain -> infrastructure`
-   `domain -> cv2`
-   `domain -> insightface`
-   `domain -> onnxruntime`
-   `application -> classe concrète InsightFace`
-   `application -> interface graphique`

## 3.6 Tell, Don't Ask

Les objets métier doivent protéger leurs propres invariants.

Éviter :

``` python
if match.score >= threshold:
    match.status = "MATCH"
```

Préférer une abstraction métier qui exprime la décision elle-même.

Mais ne pas transformer chaque donnée triviale en objet cérémoniel. TDA
protège un comportement ; il ne sert pas à multiplier les wrappers.

## 3.7 DRY

DRY concerne la duplication de **connaissance**, pas la simple
ressemblance syntaxique.

Deux lignes identiques ne justifient pas automatiquement une
abstraction.

Règle pratique :

-   première occurrence : écrire simplement ;
-   deuxième : observer ;
-   troisième avec même raison de changer : envisager l'extraction.

## 3.8 DDD pragmatique

Le projet utilise le vocabulaire métier là où il apporte de la clarté :

-   `Watchlist`
-   `WatchlistSubject`
-   `FaceEmbedding`
-   `SimilarityScore`
-   `RecognitionDecision`
-   `PotentialMatch`

Ne pas créer artificiellement :

-   aggregate root sans invariant ;
-   repository sans persistance ;
-   domain event sans consommateur réel ;
-   bounded context pour chaque dossier.

DDD sert à maîtriser la complexité métier. Il ne doit pas créer la
complexité qui n'existe pas.

------------------------------------------------------------------------

# 4. Bounded Contexts

## 4.1 Décision initiale

**Un seul Bounded Context métier est justifié aujourd'hui :
`Recognition`.**

Responsabilité :

> décider si l'observation faciale issue d'une frame correspond
> potentiellement à un sujet explicitement présent dans la watchlist de
> démonstration.

La caméra et l'UI sont des préoccupations d'infrastructure, pas des BC.

## 4.2 Condition de création d'un nouveau BC

Un nouveau BC n'est créé que si au moins plusieurs des signaux suivants
sont présents :

-   vocabulaire métier réellement distinct ;
-   invariants propres ;
-   cycle de vie propre ;
-   modèle qui diverge du BC existant ;
-   équipe ou cadence d'évolution indépendante ;
-   frontière d'intégration explicite ;
-   risque réel de collision conceptuelle.

« Cela pourrait devenir gros » n'est pas un signal DDD.

------------------------------------------------------------------------

# 5. Architecture cible minimale

Structure initiale recommandée :

``` text
sentinel-vision/
├── src/
│   └── sentinel_vision/
│       ├── recognition/
│       │   ├── domain/
│       │   ├── application/
│       │   └── infrastructure/
│       └── bootstrap/
├── tests/
│   ├── unit/
│   └── integration/
├── data/
│   └── watchlist/
├── .gitignore
├── pyproject.toml
├── README.md
├── .claude.md
├── ARCHITECTURE.md
├── DESIGN.md
└── HANDOFF.md
```

Ne pas créer tous les fichiers ou sous-dossiers à vide. Ils apparaissent
lorsqu'un besoin réel existe.

## 5.1 Domain

Le domaine contient uniquement :

-   concepts métier ;
-   invariants ;
-   décisions pures ;
-   types sans dépendance framework.

Le domaine doit pouvoir être testé sans caméra, sans modèle IA et sans
filesystem.

## 5.2 Application

La couche application :

-   orchestre les cas d'usage ;
-   dépend du domaine ;
-   définit les ports nécessaires à l'extérieur ;
-   ne contient pas de logique OpenCV/InsightFace ;
-   ne dessine rien à l'écran.

## 5.3 Infrastructure

La couche infrastructure contient les adapters :

-   webcam OpenCV ;
-   moteur InsightFace ;
-   chargement local de watchlist ;
-   overlay OpenCV ;
-   configuration technique.

Les frameworks restent ici.

## 5.4 Bootstrap

Le bootstrap est le **composition root**.

Il peut connaître les implémentations concrètes et les assembler.

Aucune logique métier dans `main.py`.

------------------------------------------------------------------------

# 6. Politique de dépendances

Une dépendance externe est un coût.

Avant tout `pip install`, vérifier :

1.  le besoin est réel ;
2.  la bibliothèque n'est pas déjà couverte par une dépendance présente
    ;
3.  elle est maintenue ;
4.  son rôle est précis ;
5.  elle ne force pas une architecture disproportionnée.

Dépendances initiales acceptées :

-   `opencv-python`
-   `insightface`
-   `onnxruntime`

Les dépendances transitives ne deviennent pas automatiquement des APIs
autorisées du projet.

Ne pas importer une dépendance transitive directement sans décision
explicite.

------------------------------------------------------------------------

# 7. TDD --- discipline obligatoire

Pour tout comportement métier non trivial :

``` text
RED → GREEN → REFACTOR
```

## 7.1 RED

Écrire d'abord un test qui exprime le comportement attendu et vérifier
qu'il échoue pour la bonne raison.

Un test qui passe immédiatement ne prouve pas le nouveau comportement.

## 7.2 GREEN

Écrire le minimum de code correct pour faire passer le test.

Pas de refactor opportuniste massif pendant GREEN.

## 7.3 REFACTOR

Améliorer le design seulement lorsque la suite est verte.

Après refactor :

-   relancer les tests concernés ;
-   relancer la suite complète avant de conclure.

## 7.4 Priorité des tests

Prioriser :

1.  invariants et décision de matching ;
2.  erreurs et frontières ;
3.  orchestration des use cases ;
4.  adapters critiques ;
5.  intégration caméra/modèle ;
6.  présentation.

Ne pas chercher 100 % de couverture pour flatter une métrique.

Chercher 100 % de confiance sur les règles critiques.

------------------------------------------------------------------------

# 8. Propriétés des tests

Les tests doivent tendre vers FIRST :

-   **Fast**
-   **Independent**
-   **Repeatable**
-   **Self-validating**
-   **Timely**

Et A-TRIP :

-   **Automatic**
-   **Thorough**
-   **Repeatable**
-   **Independent**
-   **Professional**

Interdictions :

-   dépendre d'un ordre d'exécution ;
-   dépendre de la webcam dans un test unitaire ;
-   télécharger un modèle dans un test unitaire ;
-   `sleep()` pour synchroniser un test si une condition déterministe
    est possible ;
-   tester une méthode privée directement ;
-   mocker le domaine pur ;
-   tester seulement que « ça ne plante pas ».

------------------------------------------------------------------------

# 9. Stratégie de tests

## 9.1 Unit tests

Domaine et application purs.

Ils doivent être très rapides.

## 9.2 Integration tests

Pour :

-   adapter InsightFace ;
-   chargement de watchlist ;
-   acquisition caméra si l'environnement le permet ;
-   compatibilité modèle/runtime.

Les tests nécessitant matériel ou modèle lourd doivent être clairement
séparés de la suite unitaire.

## 9.3 Characterization tests

Avant de corriger un comportement existant mal compris :

1.  reproduire ;
2.  écrire un test qui capture le comportement ;
3.  confirmer le défaut ;
4.  corriger ;
5.  prouver la non-régression.

------------------------------------------------------------------------

# 10. Qualité Python

## 10.1 Typage

Le code applicatif et domaine doit être typé.

Éviter `Any` sauf frontière technique réellement dynamique et justifiée.

## 10.2 Nommage

Le nom doit révéler l'intention.

Préférer :

``` text
RecognitionDecision
SimilarityScore
WatchlistSubject
recognize_observation()
```

Éviter :

``` text
Manager
Helper
Utils
Processor
Data
Common
do_stuff()
handle()
```

sauf si le terme exprime réellement le rôle.

## 10.3 Fonctions

Une fonction :

-   fait une chose cohérente ;
-   reste courte par nécessité conceptuelle, pas par quota arbitraire ;
-   évite les booléens qui changent complètement son comportement ;
-   évite les effets de bord cachés.

## 10.4 Exceptions

Pas de :

``` python
except Exception:
    pass
```

Une exception doit être :

-   traitée ;
-   traduite à une frontière ;
-   ou propagée explicitement.

Ne jamais transformer une panne technique en `UNKNOWN` si cela
masquerait l'erreur.

## 10.5 État global

Pas d'état global mutable.

Les dépendances sont construites au composition root et injectées
explicitement.

## 10.6 Configuration

Les valeurs techniques configurables ne sont pas dispersées dans le
code.

Le seuil de matching, l'index caméra ou le chemin de watchlist doivent
avoir une source de configuration claire lorsqu'ils deviennent
configurables.

Ne pas introduire un framework de configuration tant que quelques
constantes explicites suffisent.

------------------------------------------------------------------------

# 11. Faible charge cognitive

La qualité principale recherchée est la **compréhensibilité**.

Un développeur doit pouvoir suivre un flux sans ouvrir quinze fichiers.

Règles :

-   profondeur d'imbrication faible ;
-   early return lorsqu'il clarifie ;
-   noms explicites ;
-   pas de magie ;
-   pas de métaprogrammation sans nécessité ;
-   pas d'héritage pour partager trois lignes ;
-   composition préférée à l'héritage ;
-   dépendances visibles ;
-   comportement local prévisible ;
-   abstractions peu nombreuses et fortes.

Une architecture « propre » qui exige de traverser huit interfaces pour
comprendre un POC est une mauvaise architecture.

------------------------------------------------------------------------

# 12. Performance

La performance est importante parce que le traitement est temps réel,
mais l'optimisation doit être mesurée.

Ordre :

1.  code correct ;
2.  mesure ;
3.  identification du goulot ;
4.  optimisation ciblée ;
5.  nouvelle mesure ;
6.  test de non-régression.

Ne jamais optimiser sur intuition seule.

Métriques futures possibles lorsqu'elles deviennent utiles :

-   FPS ;
-   latence moyenne par frame ;
-   latence P95 ;
-   temps d'inférence ;
-   consommation mémoire ;
-   nombre de visages traités.

Pas de TensorRT/CUDA/threads complexes avant preuve que le chemin simple
est insuffisant.

------------------------------------------------------------------------

# 13. Règles spécifiques au traitement vidéo

1.  Ne pas coupler la boucle caméra au moteur métier.
2.  Toujours libérer la caméra proprement.
3.  Toujours fermer les fenêtres OpenCV proprement.
4.  Ne pas supposer que `read()` réussit.
5.  Une frame est une donnée éphémère.
6.  Ne pas copier les frames inutilement.
7.  Ne pas effectuer de conversion de format multiple sans nécessité.
8.  Toute optimisation de frame skipping doit être mesurée.
9.  Le rendu overlay ne doit pas ralentir silencieusement la
    reconnaissance sans mesure.
10. La résolution et le framerate doivent être explicites lorsqu'ils
    deviennent contractuels.

------------------------------------------------------------------------

# 14. Règles spécifiques à la reconnaissance

Le système de démonstration doit distinguer :

-   détection d'un visage ;
-   extraction d'un embedding ;
-   calcul de similarité ;
-   décision de matching ;
-   présentation du résultat.

Ne jamais fusionner ces concepts dans une unique fonction « recognize ».

Le domaine ne doit pas connaître la structure interne du modèle
InsightFace.

Un embedding est traité comme une représentation mathématique opaque
fournie par un port technique.

Les décisions doivent rester déterministes pour les mêmes entrées et la
même configuration.

------------------------------------------------------------------------

# 15. Données et confidentialité du POC

Le projet actuel est une démonstration locale avec consentement.

Par défaut :

-   pas d'envoi cloud ;
-   pas de télémétrie ;
-   pas de stockage permanent des frames ;
-   pas de stockage automatique des inconnus ;
-   pas de collecte silencieuse ;
-   pas de base biométrique externe.

Le dossier `data/watchlist/` ne doit pas être commité avec de vraies
photos.

Ajouter les données locales sensibles au `.gitignore`.

Les tests utilisent des fixtures synthétiques ou explicitement
autorisées.

------------------------------------------------------------------------

# 16. Git et discipline de changement

Chaque changement doit être :

-   petit ;
-   cohérent ;
-   testable ;
-   réversible ;
-   limité au besoin demandé.

Avant modification :

1.  lire les fichiers concernés ;
2.  comprendre le comportement actuel ;
3.  identifier les tests existants ;
4.  déterminer la plus petite surface de changement.

Après modification :

1.  exécuter les tests ciblés ;
2.  exécuter la suite pertinente ;
3.  inspecter le diff ;
4.  supprimer code mort/imports inutiles ;
5.  vérifier qu'aucune abstraction spéculative n'a été introduite ;
6.  mettre à jour la documentation uniquement si le comportement ou
    l'architecture ont réellement changé.

Ne jamais mélanger une feature et un refactor massif sans nécessité.

------------------------------------------------------------------------

# 17. Politique pour Claude Code et Codex

## 17.1 Avant de coder

L'agent doit :

1.  lire `.claude.md` ;
2.  lire les documents directement concernés ;
3.  inspecter le code réel ;
4.  inspecter les tests ;
5.  reformuler intérieurement le besoin ;
6.  rechercher la solution minimale compatible avec les invariants.

Ne pas inventer l'état du dépôt.

## 17.2 Pendant le codage

L'agent doit :

-   respecter les frontières ;
-   écrire le test avant le comportement métier ;
-   garder le diff minimal ;
-   éviter les changements non demandés ;
-   arrêter une abstraction dès qu'elle devient spéculative ;
-   préférer une fonction claire à un pattern inutile.

## 17.3 Après le codage

L'agent doit effectuer une auto-revue adversariale :

-   qu'ai-je cassé ?
-   quelle entrée limite ai-je oubliée ?
-   ai-je introduit une duplication de connaissance ?
-   ai-je violé SRP ?
-   ai-je importé un framework vers le cœur ?
-   ai-je créé une abstraction sans variation réelle ?
-   le test vérifie-t-il réellement ce qu'il prétend ?
-   ai-je exécuté les commandes que j'affirme vertes ?

Puis seulement produire le compte rendu.

------------------------------------------------------------------------

# 18. Patterns de conception

Aucun pattern n'est obligatoire.

Un pattern est accepté uniquement lorsqu'une variation réelle le
justifie.

Exemples potentiellement légitimes, **uniquement si le besoin apparaît**
:

-   Strategy : plusieurs politiques de matching réellement coexistantes
    ;
-   Adapter : encapsuler InsightFace/OpenCV ;
-   Factory : construction réellement variable/complexe ;
-   Observer : plusieurs consommateurs réels d'un événement.

Interdit :

> « ajoutons Strategy/Factory/EventBus au cas où ».

Le pattern le plus simple est souvent l'absence de pattern.

------------------------------------------------------------------------

# 19. Anti-patterns interdits

-   God class.
-   `utils.py` fourre-tout.
-   `manager.py` sans responsabilité précise.
-   logique métier dans `main.py`.
-   logique métier dans l'overlay.
-   import InsightFace dans le domaine.
-   accès filesystem depuis le domaine.
-   dépendance circulaire.
-   héritage artificiel.
-   interface avec une seule implémentation sans frontière ou variation
    justifiable.
-   repository sans persistance.
-   event bus sans consommateur.
-   exception avalée.
-   valeur magique dupliquée.
-   configuration cachée.
-   mock de tout.
-   test qui teste l'implémentation plutôt que le comportement.
-   optimisation non mesurée.
-   commentaires qui compensent un mauvais nommage.
-   `TODO` utilisé pour accepter une violation d'invariant.
-   code « future proof » sans besoin actuel.

------------------------------------------------------------------------

# 20. Definition of Done

Une tâche n'est terminée que si les points applicables sont vrais :

### Comportement

-   besoin demandé implémenté ;
-   cas nominal vérifié ;
-   cas d'erreur pertinents vérifiés ;
-   aucun comportement hors scope ajouté.

### Architecture

-   Dependency Rule respectée ;
-   SRP respecté ;
-   pas de nouveau couplage injustifié ;
-   pas d'abstraction spéculative ;
-   BC respecté.

### Tests

-   RED observé pour une nouvelle règle métier ;
-   GREEN obtenu ;
-   tests ciblés verts ;
-   suite pertinente verte ;
-   aucun test désactivé pour obtenir du vert.

### Code

-   typage cohérent ;
-   noms intentionnels ;
-   pas de duplication de connaissance évitable ;
-   pas de dead code ;
-   pas d'import inutile ;
-   exceptions explicites ;
-   complexité cognitive raisonnable.

### Documentation

-   documentation mise à jour seulement si nécessaire ;
-   `HANDOFF.md` mis à jour à la fin d'une session substantielle ;
-   ADR ajoutée si et seulement si une décision architecturale durable a
    réellement changé.

------------------------------------------------------------------------

# 21. Critères de succès de la première milestone

La première milestone n'est pas « une plateforme de surveillance ».

Elle est réussie lorsque :

1.  le projet démarre par une commande documentée ;
2.  la webcam s'ouvre et se ferme proprement ;
3.  un visage peut être détecté en direct ;
4.  une petite watchlist locale peut être chargée ;
5.  une observation peut être comparée à cette watchlist ;
6.  `UNKNOWN` et `MATCH POTENTIEL` sont distingués proprement ;
7.  le résultat est affiché sans mélanger présentation et décision ;
8.  le flux reste suffisamment fluide pour une démonstration ;
9.  les règles de décision sont couvertes par tests ;
10. le cœur métier peut être exécuté sans caméra et sans InsightFace.

Tout le reste attend un besoin réel.

------------------------------------------------------------------------

# 22. Ordre de construction

Ordre obligatoire tant qu'aucun fait nouveau ne le remet en cause :

``` text
M0 — Toolchain propre
     pyproject.toml / tests / lint-type-check minimal

M1 — Camera acquisition
     ouvrir, lire, fermer proprement

M2 — Face detection
     détecter sans reconnaître

M3 — Watchlist loading
     charger des sujets de démonstration

M4 — Embedding extraction
     produire les représentations

M5 — Recognition decision
     similarité + seuil + UNKNOWN/MATCH POTENTIEL

M6 — Live composition
     brancher caméra + moteur + décision

M7 — Presentation
     overlay lisible et faible charge cognitive

M8 — Measurement
     FPS / latence seulement lorsque le flux complet existe

M9 — Optimization
     uniquement sur goulot mesuré
```

Ne pas sauter directement à M9.

------------------------------------------------------------------------

# 23. Règle finale

À chaque décision, appliquer cette séquence :

> **Besoin réel → invariant → test → solution la plus simple → mesure →
> refactor éventuel.**

Pas :

> framework → pattern → abstraction → problème à chercher.

Sentinel Vision doit rester un projet que l'on peut expliquer
rapidement, tester facilement, modifier sans peur et optimiser
uniquement lorsque les mesures le demandent.
