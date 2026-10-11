# Sentinel Vision — Constitution d'ingénierie

> **Statut : règles de travail du dépôt pour Claude Code, Codex et tout contributeur.**
> **Priorités : fiabilité vérifiable, latence réelle, robustesse, crédibilité des résultats, simplicité du code.**
> **Stack existante : Python 3.13, OpenCV, InsightFace, ONNX Runtime, NumPy.**
> **Périmètre : démonstration locale et surveillance d'un espace privé contrôlé, sans identification automatique de personnes non consentantes.**

## 0. Mode opératoire obligatoire

1. Avant toute intervention, lire `CLAUDE.md`, `ARCHITECTURE.md`, `DESIGN_SYSTEM.md`, le handoff disponible et **le code réel**, puis les tests concernés.
2. Ne jamais supposer qu'une fonction est implémentée parce qu'elle apparaît dans un document ou dans `AppConfig`.
3. Distinguer systématiquement : **existant et vérifié**, **existant non vérifié**, **proposé**, **hors périmètre**.
4. **Auditer et proposer avant de coder** si la demande porte sur une architecture, un nouveau moteur IA, un changement de seuil ou une refonte. Ne modifier le dépôt qu'après validation explicite.
5. Pour une correction autorisée : reproduire le défaut, écrire le test, appliquer le changement minimal, exécuter les tests et mesurer les effets.
6. Ne jamais affirmer « testé », « plus rapide », « plus fiable », « compatible » ou « prêt pour la production » sans preuve reproductible.
7. Préserver le fonctionnement actuel ; toute évolution doit être réversible, ciblée et accompagnée de tests de non-régression.
8. En cas de contradiction entre documents, signaler le conflit et demander une décision ; ne pas le résoudre silencieusement.

**Hiérarchie :** demande explicite de l'utilisateur → présent fichier → `ARCHITECTURE.md` → `DESIGN_SYSTEM.md` pour la présentation → handoff → tests et code observés. Le code et les mesures sont les preuves de l'état exécuté ; les documents expriment l'intention et doivent être corrigés lorsqu'ils sont obsolètes.

**Documentation :** ne pas réécrire massivement les documents existants. Toute décision architecturale structurante exige une ADR courte (contexte, options, décision, conséquences, preuve). Les changements triviaux n'en exigent pas.

## 1. Vision produit et vérité métier

Sentinel Vision doit devenir un moteur **local, temps réel, explicable et mesurable** capable :

- de capter une webcam ou un flux de caméra IP **effectivement accessible** ;
- de détecter des personnes et véhicules observables dans un espace privé ;
- de suivre leurs déplacements pendant une séquence vidéo ;
- de détecter un franchissement de ligne ou une entrée dans une zone définie ;
- de produire des événements horodatés, sans répétitions injustifiées ;
- de détecter un visage et, séparément, de proposer une correspondance à une **watchlist volontaire et consentie** ;
- de continuer à détecter une présence même si le visage est caché, flou, de dos ou inexploitable ;
- de montrer clairement la disponibilité et les limites de chaque capacité.

**Trois faits distincts :** `PERSON_DETECTED` ne signifie pas `FACE_DETECTED` ; `FACE_DETECTED` ne signifie pas `IDENTITY_CONFIRMED`. Une similarité faciale n'est pas une probabilité d'identité.

**Contrat de crédibilité :** ne jamais annoncer « intrusion », « identité », « danger », « personne suspecte » ou « conducteur reconnu » sans critère métier explicite et preuve correspondante. Un masque, un turban, un vêtement religieux, une capuche ou une manière de marcher ne prouvent aucune intention. Pour un portail, l'événement factuel est d'abord « franchissement détecté ».

**Aucune promesse de détection parfaite.** Nuit, contre-jour, pluie, reflet, occultation, déplacement rapide, faible définition, angle défavorable, vitres teintées et indisponibilité réseau peuvent empêcher l'observation.

## 2. Non-négociables techniques

- La **source vidéo** est indépendante du domaine. Le domaine n'importe jamais `cv2`, `numpy`, InsightFace, ONNX Runtime ou une bibliothèque YOLO.
- Les adaptateurs techniques ne possèdent pas les décisions métier.
- Le rendu n'infère, ne décide, ne confirme et ne modifie jamais un résultat.
- Une panne technique est **indisponible/dégradée/erreur**, jamais déguisée en `UNKNOWN`.
- Une correspondance faciale reste **potentielle**, sauf procédure indépendante explicitement définie ; aucune action défavorable automatique sur sa seule base.
- Toute confirmation temporelle est liée à **une seule piste physique et à une source donnée**, sans mélange de personnes, de caméras ou de sessions.
- Chaque événement possède au minimum une source, un type, un horodatage pertinent et un identifiant permettant la déduplication.
- Les frames obsolètes ne doivent pas être présentées comme du direct. Le temps de capture et le temps de traitement sont distingués.
- Pas de stockage biométrique, de vidéo permanente, de cloud, de télémétrie ou de capture d'inconnus par défaut. Toute conservation est explicite, limitée et contrôlée.
- Toute référence biométrique réelle requiert l'accord de la personne concernée et une possibilité de suppression.
- Une optimisation est refusée si elle dégrade une métrique critique de fiabilité sans arbitrage documenté.

## 3. Principes d'ingénierie

Appliquer **SOLID, SRP, DIP, OCP, Tell Don't Ask, DDD pragmatique, DRY, KISS, YAGNI et TDD** comme outils de réduction du risque, jamais comme décoration.

- **SRP :** acquisition, inférence, suivi, décision, persistance et affichage ont des raisons de changer distinctes.
- **DIP :** infrastructure → application → domaine. Ports uniquement lorsqu'une frontière externe ou une variation réelle le justifie.
- **OCP :** pouvoir remplacer le détecteur ou l'analyseur facial sans réécrire les règles métier ; ne pas fabriquer dix interfaces fictives.
- **TDA :** placer règles et invariants dans les concepts qui les possèdent ; éviter les objets anémiques avec des décisions dispersées.
- **DRY :** mutualiser la connaissance métier répétée, pas simplement les lignes ressemblantes.
- **KISS :** privilégier une implémentation courte, déterministe et inspectable.
- **YAGNI :** pas de microservices, bus, broker, base de données, backend HTTP, GPU, multi-caméras ou pipeline distribué sans besoin et preuve.
- **DDD :** les bounded contexts suivent les responsabilités métier, pas les packages, bibliothèques ou algorithmes.
- **TDD :** `RED → GREEN → REFACTOR` pour toute règle métier non triviale ; un test qui passe immédiatement ne démontre pas la nouvelle règle.

**Interdits :** god classes ; `utils.py` ou `manager.py` fourre-tout ; héritage artificiel ; `except: pass` ; état global mutable ; I/O depuis le domaine ; configuration cachée ; faux mocks prouvant uniquement leur propre configuration ; refactor massif mélangé à une feature.

## 4. Frontières et évolution DDD

### 4.1 `recognition` — existant, à préserver

Langage actuel : `FaceEmbedding`, `FaceObservation`, `FaceQualityGate`, `Watchlist`, `WatchlistSubject`, `RecognitionPolicy`, `MatchConfirmation`, `RecognitionResult`.

Responsabilité : évaluer la qualité d'une observation faciale, comparer des embeddings à des références consenties, et retourner une décision **prudente et explicable**.

Ne jamais introduire dans ce domaine des concepts tels que portail, véhicule, intrusion, zone, ligne de franchissement ou trajectoire globale.

### 4.2 Détection visuelle — capacité à ajouter après audit

Responsabilité envisagée : observer des catégories telles que `person`, `car`, `motorcycle` et leurs rectangles et scores. Un détecteur YOLO est un **adaptateur**, pas une règle métier ni un bounded context à lui seul.

Définir un modèle d'observation agnostique à YOLO uniquement quand le premier cas d'usage est validé. Ne pas recycler `FaceObservation` pour représenter un véhicule.

### 4.3 Suivi et surveillance — responsabilité distincte

Une capacité de monitoring peut gérer piste temporaire, franchissement directionnel, présence, temporisation et déduplication. Ne créer un nouveau bounded context formel que si ses invariants et son cycle de vie le justifient réellement. Sinon commencer avec un module cohérent dans la couche appropriée.

**Architecture conceptuelle, non ordre de créer tous les dossiers :**

```text
Camera / VideoSource (OpenCV, fichier test, IP si accessible)
                |
                v
      Acquisition horodatée
                |
         +------+------+
         |             |
         v             v
  Object detection  Face recognition
  (YOLO adapter)    (InsightFace adapter)
         |             |
         v             v
  Tracking / rules  Potential match
         |             |
         +------+------+
                v
      Events / UI / optional retention
```

Les deux branches ne sont **pas** obligatoirement exécutées sur chaque frame. Une personne de dos et un véhicule peuvent être observés sans lancer l'analyse faciale.

### 4.4 Composition root

Seul `bootstrap` assemble concrètement les implémentations. L'application dépend de contrats nécessaires, pas de classes InsightFace, YOLO, lecteurs caméra ou rendu OpenCV.

## 5. Audit obligatoire de l'existant avant extension

Inspecter **réellement** l'application et ses tests :

- `recognition/application/recognize_frame.py` et le port `face_analyzer.py` ;
- tracker, association IoU, gestion des pistes perdues et histoires temporelles ;
- boucle vidéo, horodatage, lecture réseau, reconnexion, traitement et rendu ;
- `AppConfig`, valeurs effectives, validation et provenance ;
- `pyproject.toml`, versions, providers ONNX réellement disponibles ;
- tests unitaires, intégration, fixtures, résultats de benchmarks réels.

**Points de vigilance déjà identifiés dans les extraits fournis (à confirmer par audit) :**

1. `MatchConfirmation` compte des matches historiques : prouver que cet historique correspond à **une seule piste** et n'autorise pas de réidentification erronée entre plusieurs visages ; vérifier la gestion des fenêtres, absences et resets.
2. `RecognitionPolicy` n'examine que le meilleur candidat : analyser les cas où les premier et deuxième scores sont presque égaux.
3. `WatchlistSubject.similarity_to()` prend le maximum des références : mesurer l'effet de l'augmentation du nombre de photos sur les faux positifs.
4. `FaceQualityGate` ne vérifie que taille et confiance du détecteur : qualité réelle de l'embedding à étudier (flou, pose, éclairage, occlusion) sans coût excessif.
5. `FaceEmbedding` : vérifier dimension, vecteur nul et contrat de normalisation avant toute optimisation par produit scalaire.
6. `FaceObservation` : vérifier les invariants même lors de la construction directe, pas seulement par `from_bbox()`.
7. `LocalWatchlistLoader` : mesurer le coût d'extraction des embeddings au démarrage ; ne mettre en cache qu'avec invalidation/versionnement corrects.
8. `LocalWatchlistWriter` : éviter d'enregistrer involontairement une référence multi-visages ou inutilisable.
9. `RecognitionResult` : éviter de mélanger « inconnu », « qualité insuffisante », « ambigu » et « moteur indisponible ».
10. `render()` : ne pas afficher `SYSTEM READY` quand une capacité requise par le mode actif est défaillante.

Ne pas transformer cette liste en refactor automatique. Classer chaque point : **confirmé / infirmé / non vérifiable**, gravité, preuve et test proposé.

## 6. Reconnaissance faciale : fiabilité avant taux de match

### 6.1 Pipeline et qualité

Distinguer systématiquement : détection du visage → mesure qualité → extraction d'embedding → comparaison → politique de décision → confirmation temporelle → présentation.

Qualité potentiellement pertinente : surface faciale utile, netteté, mouvement, pose, occlusion, éclairage, confiance du détecteur. Ne pas multiplier les métriques sans démontrer qu'elles améliorent les décisions.

Le score cosinus est une **mesure de proximité mathématique**, pas « 85 % certain ». Pas de précision artificielle, de badge « verified » ou de décision définitive fondée sur un score seul.

### 6.2 Références multi-photos

Conserver plusieurs photos **vérifiées et consenties** par sujet, avec variété utile (âge, angle, éclairage, expression, accessoires). Éviter les doublons proches qui ajoutent du coût sans diversité informative.

Comparer les stratégies sur un jeu de validation indépendant : meilleure référence, agrégation robuste, contrôle de qualité, politique d'ambiguïté. Le simple maximum peut accroître le taux de faux matchs à mesure que les références augmentent.

Les seuils de matching et de qualité sont des **paramètres calibrés**, pas des chiffres magiques à abaisser pour faire apparaître une correspondance.

### 6.3 Photos anciennes, enfance et évolution d'âge — exigence critique

Une photographie d'enfance et un visage adulte peuvent présenter un **écart morphologique majeur**. Aucun modèle, y compris InsightFace, YOLO ou un modèle « age-invariant », ne garantit une correspondance fiable à travers les décennies.

**Objectif légitime :** mesurer et améliorer la robustesse dans la limite des preuves, **pas** forcer la reconnaissance d'une personne à partir d'une photo ancienne.

Protocole exigé :

1. Utiliser uniquement des paires de photos de la **même personne volontaire**, datées/âge approximatif documenté quand disponible, ainsi que des imposteurs consentants pour les négatifs.
2. Regrouper par plages d'écart d'âge et conditions photographiques ; distinguer changement d'âge, dégradation de la photo et échec de détection.
3. Séparer sujets/prises de vue entre réglage des seuils et évaluation finale ; éviter toute fuite de données entre ensembles.
4. Mesurer séparément : taux de visages détectés, taux de faux rejets, taux de fausses acceptations, précision des correspondances proposées et couverture des cas évaluables.
5. Comparer `buffalo_s` et `buffalo_l` **sur le même matériel, avec le même protocole** ; un modèle plus lourd n'est pas automatiquement meilleur sur l'écart d'âge.
6. Ne considérer restauration, super-résolution ou vieillissement synthétique qu'en **expérimentation isolée** : ces traitements peuvent inventer des caractéristiques biométriques et augmenter les faux matchs.
7. Ne jamais enrôler automatiquement une photo restaurée/synthétique comme vérité de référence ; conserver la provenance originale.
8. Si la preuve est insuffisante : retourner `UNKNOWN`, `AMBIGUOUS` ou `INSUFFICIENT_QUALITY` selon la politique validée, puis demander une vérification humaine hors du moteur.

**Une photo ancienne ne doit jamais devenir une preuve d'identité par simple similarité.** Toute affirmation de meilleure performance « age-invariant » doit être étayée sur des écarts d'âge documentés et des négatifs difficiles.

### 6.4 Confirmation temporelle

La confirmation d'une correspondance requiert une association fiable à une piste donnée, une fenêtre bornée, une règle explicite de gestion des frames manquées et une remise à zéro lors d'un changement de piste ou de caméra.

Ne pas additionner les matches de plusieurs personnes. Ne pas retenir seulement le score historique maximal pour décrire la certitude actuelle. Les pistes temporaires ne sont pas des identités biométriques.

## 7. Détection et suivi : jardin, portail, marche, course, véhicules

Le premier objectif du futur module est **l'événement physique observable**, pas l'identité.

Scénarios à vérifier :

- personne marchant, courant, changeant rapidement de direction ;
- personne masquée, portant turban/capuche/casque, de dos ou visage hors champ ;
- personne partiellement occultée, accroupie, passant derrière un obstacle ;
- une et plusieurs personnes, croisements, entrées simultanées, sorties ;
- voiture, moto, passager non visible, vitres teintées, véhicule stationné ;
- accès au jardin sans franchissement du portail, selon la règle configurée ;
- nuit, contre-jour, pluie, compression, faible éclairage, déconnexion et retour du flux.

**Contraintes :** un modèle de détection de personnes ne sait pas nécessairement distinguer les occupants d'une voiture. Détecter une voiture ne permet pas de conclure combien de personnes y sont présentes. Un objet hors champ ou entièrement masqué ne peut pas être détecté à partir d'images qui ne le montrent pas.

**Tracking :** comparer un tracker simple et, seulement si nécessaire, ByteTrack/BoT-SORT ou équivalent. Mesurer pertes de pistes, changements d'ID, trajectoires fragmentées, faux franchissements et duplications. Un ID de piste est temporaire, pas une identité civile.

**Franchissement :** définir géométrie, direction, règle de déclenchement (centre/point d'ancrage/trajectoire), hystérésis anti-oscillation, tolérance aux trous temporels et unicité d'événement. Tester les objets qui restent au voisinage de la ligne.

**Zones :** définir des coordonnées rattachées à la résolution et à l'orientation correctes ; ne pas laisser un redimensionnement invalider silencieusement une zone.

## 8. Temps réel : politique de performance fondée sur la mesure

### 8.1 Mesures obligatoires

Pour chaque configuration et scénario, recueillir si applicable :

- FPS caméra **reçus**, FPS **analysés** et FPS **affichés** ;
- latence bout en bout `capture → événement/alerte`, médiane, P95 et P99 ;
- latence capture/décodage, prétraitement, détection, tracking, analyse faciale, rendu et I/O ;
- âge de la frame affichée, taille des files, frames abandonnées ;
- CPU/GPU, mémoire, temps d'initialisation, stabilité sur durée ;
- rappel des entrées, fausses alertes/heure, alertes dupliquées, pertes et changements d'ID.

Séparer **débit**, **fraîcheur**, **exactitude**, **continuité** et **résilience**. Ne jamais optimiser les seuls FPS au détriment d'une entrée manquée.

### 8.2 Architecture du pipeline

1. Horodater les frames à l'acquisition ; conserver l'identité de la source.
2. Découpler l'acquisition de l'inférence **seulement si les mesures le nécessitent** ; commencer simple.
3. Employer des files **bornées** si une concurrence est introduite. Définir explicitement la stratégie en surcharge (dernière frame, perte contrôlée, mode dégradé).
4. Ne pas supposer qu'un saut de frames est sans conséquence : les traversées rapides peuvent être manquées. Vérifier sur des clips annotés.
5. Ne pas partager sans contrôle des objets NumPy mutables entre threads ; maîtriser durée de vie des buffers.
6. Réutiliser le modèle chargé ; éviter les conversions, copies, synchronisations, lectures disque et allocations répétées inutiles.
7. Ne pas exécuter InsightFace sur toute voiture ou sur toute frame si le besoin ne le justifie pas.
8. Évaluer les fournisseurs ONNX réellement présents et leurs performances **après** benchmark ; pas de présomption CPU/GPU.
9. Limiter les logs par frame ; instrumenter sans perturber de manière significative la latence mesurée.
10. Si le live perd sa fraîcheur, afficher `DEGRADED`/`STALE`, pas `LIVE`.

### 8.3 Objectifs de performance

Ne fixer **aucun FPS, taux de détection ou délai garanti** sans matériel cible et corpus de référence. Formuler des **budgets mesurables** avant l'implémentation, et enregistrer les résultats obtenus. Pour les scénarios rapides, mesurer le taux d'événements manqués, pas seulement la fluidité.

Toute optimisation exige : baseline, hypothèse, changement minimal, profilage comparable avant/après, non-régression fonctionnelle et possibilité de retour arrière.

## 9. Sources vidéo et modes dégradés

- Webcam, fichier vidéo de test et flux IP sont des **adaptateurs de source**, pas des règles du domaine.
- Une adresse IP découverte ou un ping réussi **ne prouvent pas** qu'un flux RTSP/ONVIF est disponible ; ne pas inventer une URL de streaming UBOX.
- Prévoir échec d'ouverture, `read()` faux, frame vide, timeout, coupure, reconnexion, doublons et reprise.
- Toujours relâcher proprement capture vidéo, workers et fenêtres.
- Ne pas déclarer un événement sur une frame périmée après reconnexion.
- Si le moteur facial échoue mais la détection de personnes fonctionne, afficher les **capacités disponibles séparément** ; l'inverse aussi.
- Tester la transition des états `STARTING`, `READY`, `DEGRADED`, `ERROR`, `RECOVERING` sans présenter un échec comme un résultat négatif.

## 10. Validation expérimentale et tests

### 10.1 Tests unitaires (rapides et déterministes)

Invariants de bbox, embeddings, similarité, scores limites, tri des candidats, égalité/ambiguïté, qualité, matching, confirmations, association aux pistes, reset, entrée/sortie, déduplication et erreurs de configuration.

Aucune webcam, réseau, téléchargement de modèles, attente arbitraire ou vrai visage obligatoire dans les tests unitaires.

### 10.2 Tests d'intégration

Chargement de références, erreur de modèle, compatibilité InsightFace/ONNX, caméra simulée ou fichier vidéo, cohérence d'horodatage, reprise après panne, qualité des résultats d'adapters.

Tests matériels et lourds isolés ; aucun téléchargement implicite pendant la suite rapide.

### 10.3 Corpus vidéo reproductible

Constituer avec autorisation un corpus privé de scénarios annotés : marche, course, deux personnes, masque/turban, nuit, véhicule, occlusions, traversée aller/retour, perte du flux. Ajouter des négatifs difficiles : ombres, arbres en mouvement, animaux, véhicules qui passent sans entrer, personnes restant à l'extérieur.

Chaque clip doit définir la vérité terrain : source, début/fin, type d'objet, entrée/sortie et événements attendus. Pour la comparaison faciale, distinguer les vérités terrain d'identité des résultats du modèle.

Mesurer par scénario et globalement : rappel des événements, faux positifs, latence P95, duplications, continuité des pistes et taux d'indisponibilité. Rendre visibles les faibles performances, ne pas les masquer derrière une moyenne.

### 10.4 Expériences sur photos anciennes

Tests isolés avec paires consenties, références contemporaines vs anciennes, imposteurs ressemblants, variations de qualité et écarts d'âge. Rapporter la taille des échantillons et les intervalles d'incertitude lorsqu'ils sont calculables ; aucun pourcentage spectaculaire sur deux photos.

### 10.5 Règle de non-régression

Un changement de modèle, seuil, résolution, tracker ou fréquence d'inférence doit relancer les tests appropriés **et** le benchmark des scénarios critiques. Documenter explicitement toute régression et son arbitrage.

## 11. Données, sécurité et éthique

- Traiter images, embeddings et captures comme des données sensibles.
- Utiliser seulement des références consenties pour la comparaison d'identité ; pas de scraping, recherche dans des bases externes ou enrichissement biométrique caché.
- Ne pas suivre une personne entre plusieurs caméras par biométrie sans objectif, base et consentement appropriés.
- Éviter l'enregistrement continu et la conservation des inconnus par défaut.
- Lorsque la capture est activée : dossier protégé, politique d'expiration, suppression, contrôle d'accès, exclusion Git et minimum nécessaire.
- Protéger les URL de caméra et leurs identifiants : jamais de secret dans les logs, screenshots, tests ou documentation.
- Préférer des alertes factuelles réversibles avec confirmation humaine à des décisions automatiques sur une identité incertaine.
- Surveiller son espace privé en respectant les règles applicables et la vie privée des personnes filmées.

## 12. Interface : crédibilité perceptuelle

`DESIGN_SYSTEM.md` demeure la référence pour les tokens, états, typographie, couleur, espacements et mouvement.

- **Vidéo dominante**, interface dark premium, style MUI discipliné, faible charge cognitive.
- Overlays sobres : bbox stable, label court, informations techniques secondaires.
- Afficher séparément caméra, détection d'objet, suivi et reconnaissance ; éviter un unique voyant vert trompeur.
- Utiliser `POTENTIAL MATCH`, `UNKNOWN`, `INSUFFICIENT QUALITY`, `AMBIGUOUS`, `UNAVAILABLE` selon la politique réellement implémentée ; ne pas simuler un état non pris en charge.
- Afficher la **similarité**, jamais « % certain » ; ne pas déguiser le score en probabilité.
- Ne pas superposer de faux graphiques, FPS inventés, fausses télémétries, effets « sci-fi », clignotements ou animations coûteuses.
- Le rendu n'a jamais le droit de devancer la décision du moteur ni de masquer un flux périmé.

## 13. Configuration et qualité Python

- Python typé ; noms intentionnels ; fonctions cohérentes et effets de bord visibles.
- `AppConfig` reste une configuration technique, pas un fourre-tout de politiques métier ; extraire seulement lorsqu'une vraie pression de complexité le justifie.
- Valider les seuils, tailles, dimensions, chemins, temporisations, URL et combinaisons incompatibles à l'entrée.
- Erreurs explicites à la bonne frontière, diagnostic contextualisé et contrôlé ; jamais `except Exception: pass`.
- Ne pas ajouter de dépendance sans vérifier maintenance, licence (notamment modèles/datasets YOLO et InsightFace), compatibilité Python, coût de distribution et réel bénéfice.
- Ne pas inventer une licence commerciale autorisée pour un modèle pré-entraîné ; vérifier avant redistribution ou usage commercial.
- Favoriser la composition ; tests de comportement ; zéro optimisation non mesurée.

## 14. Plan de livraison par preuves, pas par promesses

**M0 — Audit et baseline.** Cartographier le flux actuel, confirmer les risques du code, exécuter la suite de tests, relever FPS/latence/erreurs. **Aucune refonte** pendant cet audit.

**M1 — Fiabiliser la reconnaissance existante.** Invariants, qualité, confirmations par piste, cas ambigus, références fiables. Valider que les changements ne dégradent pas l'usage actuel.

**M2 — Évaluer les photos anciennes.** Corpus consenti, écart d'âge, vrais négatifs, comparaison de modèles, calibration et compte rendu de limites. Ne pas promettre une identification à travers les décennies.

**M3 — Détection non biométrique.** Intégrer un détecteur de personnes/véhicules derrière un adaptateur minimal, sur vidéos de test avant la caméra IP réelle.

**M4 — Tracking et événements.** Franchissement directionnel, zones, déduplication, passages rapides, occlusion, erreur de piste ; tests déterministes puis vidéos annotées.

**M5 — Performance et résilience.** Profiler bout en bout, réduire latence et frames périmées, tester coupures réseau, surcharge, durée de fonctionnement et récupération.

**M6 — UX et exploitation.** États honnêtes, alertes factuelles, captures explicites, diagnostics et finition selon le Design System.

Une milestone est complète uniquement si ses critères de validation, tests et mesures sont documentés. Ne pas commencer tout M0–M6 en une seule PR.

## 15. Compte rendu attendu de Claude Code

À chaque intervention substantielle, répondre en français avec :

1. **Constat :** ce qui existe réellement, fichiers examinés, comportement reproduit.
2. **Risque :** impact concret, gravité, cas limite et preuve.
3. **Décision :** changement minimal choisi et alternatives écartées.
4. **Tests :** commandes réellement lancées, résultat, limites de couverture.
5. **Performance :** baseline et après, matériel/protocole, ou « non mesurée ».
6. **Diff :** fichiers changés, justification, absence de changements hors périmètre.
7. **Limites :** inconnues, risques résiduels, conditions non vérifiées.
8. **Prochaine étape :** une action prioritaire clairement justifiée.

Si la demande est une **revue** ou une **discussion**, fournir l'analyse et les options **sans modifier aucun fichier**.

## 16. Definition of Done

Une évolution n'est « terminée » que si :

- le comportement demandé fonctionne dans son périmètre annoncé ;
- le comportement préexistant critique reste valide ;
- les invariants métier et les frontières architecturales sont respectés ;
- les tests ciblés puis la suite pertinente ont réellement été exécutés ;
- les scénarios négatifs et dégradés significatifs sont couverts ;
- les résultats sensibles ne prétendent pas à plus de certitude que les données ;
- les mesures de performance nécessaires existent et la latence n'est pas dissimulée ;
- les données et secrets sont protégés ;
- la documentation et le handoff reflètent les changements effectifs ;
- aucun code spéculatif, abstraction gratuite ou régression cachée ne subsiste.

---

> **Règle finale :** une détection crédible vaut mieux qu'une identification forcée ; une alerte mesurée vaut mieux qu'un compteur FPS flatteur ; une architecture simple et prouvée vaut mieux qu'une architecture impressionnante mais non testée.
>
> **Méthode : besoin réel → invariants → test → implémentation minimale → mesure → validation contradictoire → amélioration ciblée.**
