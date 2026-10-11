# ADR-001 — Modèle de reconnaissance par défaut : buffalo_s

## Contexte
La première tranche de reconnaissance de bout en bout (watchlist → embedding →
décision → overlay) fonctionne. Mesure sur la machine de démonstration
(CPUExecutionProvider, pas de GPU disponible) avec le pack `buffalo_l`
(détection RetinaFace + reconnaissance ResNet50 ArcFace) :

```
analyze() 1 visage  @640x480  det_size 640  ~1039 ms  -> ~1.0 FPS
analyze() 6 visages @1280x886 det_size 640  ~2256 ms  -> ~0.4 FPS
```

À ~1 FPS le flux live n'est pas fluide, ce qui contredit un objectif produit
central (démonstration temps réel fluide).

## Forces
- CPU uniquement (onnxruntime providers : Azure, CPU ; aucun GPU).
- Le produit doit rester fluide pendant la démonstration.
- La watchlist de démonstration est petite et constituée de volontaires.
- Le seuil de décision n'est pas encore calibré.

## Options
1. Garder `buffalo_l`, ajouter du frame-skipping / un thread d'inférence.
2. Réduire `det_size` uniquement.
3. Passer au pack `buffalo_s` (détection SCRFD + reconnaissance MobileFaceNet).

Mesures :

```
buffalo_l det_size 320  1 visage  ~648 ms  -> ~1.5 FPS
buffalo_s det_size 320  1 visage  ~71 ms   -> ~14 FPS
```

Le goulot dominant est l'inférence du modèle de reconnaissance ResNet50, pas la
détection : réduire `det_size` seul ne suffit pas (option 2 rejetée).
L'option 1 ajoute de la concurrence et de la complexité d'état non justifiées
tant qu'une solution plus simple satisfait la mesure (reportée).

Discrimination vérifiée avec `buffalo_s` (sujet enrôlé vs cinq autres
personnes, même frame) :

```
match 0.958   autres: 0.130, 0.071, -0.011, -0.012, -0.020
```

La séparation reste large ; le seuil 0.35 tombe dans un grand écart.

## Décision
Pack par défaut = `buffalo_s`, `det_size` = (320, 320). Le pack reste
configurable via `AppConfig.model_name` ; `buffalo_l` demeure disponible pour
un besoin de précision supérieure démontré.

## Conséquences
- Flux live ~14 FPS sur un visage (CPU) : démonstration fluide.
- Précision de reconnaissance théoriquement inférieure à ResNet50 ; acceptable
  pour une watchlist de démonstration de volontaires, et la séparation mesurée
  reste nette.
- Le seuil (0.35) n'est toujours pas calibré ; il devra l'être sur des données
  réelles de démonstration avant toute conclusion quantitative.

## Preuves
Mesures ci-dessus exécutées sur la machine de démonstration via le code réel
(`InsightFaceFaceAnalyzer`), image d'exemple InsightFace `t1.jpg`, 2026-10-03.
