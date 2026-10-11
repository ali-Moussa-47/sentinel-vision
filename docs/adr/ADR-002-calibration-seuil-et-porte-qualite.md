# ADR-002 — Calibration du seuil et porte de qualité

## Contexte
Le seuil de reconnaissance (0.35) n'était pas calibré et aucune garde de
qualité n'existait : un visage lointain, petit ou peu net était comparé puis
classé UNKNOWN ou POTENTIAL MATCH, ce qui peut produire de fausses alertes
(embedding peu fiable extrait d'un crop upscalé). L'exigence produit est la
fiabilité d'abord : aucune fausse correspondance, pas d'alerte sur un visage
que le système ne peut pas évaluer de façon fiable.

## Forces
- Webcam 2D + ArcFace : pas de profondeur/IR (≠ FaceID) ; on ne vise pas la
  sécurité FaceID mais une DÉCISION fiable, précision prioritaire sur le rappel.
- Modèle buffalo_s, entrée du modèle de reconnaissance = 112×112.
- CPU, watchlist de démonstration de volontaires.
- Pas de jeu de données étiqueté génuine/imposteur disponible au moment présent.

## Mesure
Distribution d'imposteurs sur les 6 visages distincts de l'image d'exemple
`t1.jpg` (15 paires, buffalo_s, det_size 320) :

```
cosinus imposteur: max 0.192  moyenne 0.044  (toutes <= 0.19)
det_score visages nets: 0.80 - 0.89
taille min-cote des visages (photo de groupe): 95 - 117 px
```

## Décision
Trois règles, séparées (SRP) et testées sans matériel :

1. Porte de qualité `FaceQualityGate(min_face_pixels=112, min_detection_score=0.65)`.
   Un visage dont le plus petit côté < 112 px (sous la résolution d'entrée du
   modèle → upscaling → embedding non fiable) OU dont le det_score < 0.65 est
   jugé non fiable. Appliquée AVANT toute comparaison, à la reconnaissance ET à
   l'enrôlement.
2. Résultat distinct `INSUFFICIENT_QUALITY` (UI « MOVE CLOSER ») — ni UNKNOWN,
   ni POTENTIAL MATCH. Le système n'affirme rien quand il ne peut pas évaluer.
3. Seuil de décision `RecognitionPolicy(match_threshold=0.45)` sur un visage
   fiable : >= 0.45 → POTENTIAL MATCH, sinon UNKNOWN.

Choix de 0.45 : marge ~0.26 au-dessus du plafond imposteur mesuré (0.192),
sous la plage génuine typique d'ArcFace (~0.4-0.7). Priorité à la précision.

## Conséquences
- Vérification de bout en bout (sujet enrôlé depuis un crop, imposteurs = autres
  personnes) :
  - visages fiables : 1 POTENTIAL MATCH (0.96) + 5 UNKNOWN (imposteur max 0.13) ;
    aucun faux positif SUR CET ÉCHANTILLON (marge ~0.83). Ce n'est pas une preuve
    de FAR nul : FAR/FRR ne sont pas établis.
  - visages lointains (<112 px) : INSUFFICIENT_QUALITY (« MOVE CLOSER »), jamais
    une fausse correspondance ni un faux UNKNOWN.
- Calibration PROVISOIRE : fondée sur 15 paires d'imposteurs d'une seule photo,
  aucune paire genuine multi-session. Variations de pose/éclairage/flou/occlusion
  non mesurées ; la porte ne mesure que taille + confiance de détection.
- Le rappel (taux d'acceptation des vrais positifs à 0.45) n'est PAS encore
  calibré sur de vraies paires multi-photos par personne : à valider sur des
  volontaires réels (voir §4 du protocole dans CODEX_REVIEW_PROMPT.md). Si le
  rappel est trop faible, abaisser vers 0.40 en revérifiant la marge imposteur.
  Ne jamais abaisser le seuil pour « faire marcher la démo » sans remesurer.
- La porte de qualité s'applique aussi au chargement de références manuelles et
  à l'enrôlement (une référence non fiable est refusée, pas enregistrée).
- Les seuils sont configurables (`AppConfig`), source unique.

## Preuves
Mesures et vérification exécutées via le code réel (`InsightFaceFaceAnalyzer`,
`LocalWatchlistLoader`, `RecognizeFrame`) sur l'image d'exemple InsightFace,
2026-10-03. Règles couvertes par tests unitaires (FaceQualityGate,
RecognitionPolicy, RecognizeFrame, EnrollSubject).
