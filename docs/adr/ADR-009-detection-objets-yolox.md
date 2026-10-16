# ADR-009 — Détection d'objets non biométrique (YOLOX ONNX)

## Contexte
Le produit doit observer des faits physiques dans un espace privé (personne,
véhicule) indépendamment de toute identité (constitution §1, §4.2, §7). La
reconnaissance faciale ne couvre pas une personne de dos, masquée, ou un
véhicule. Il faut une capacité de détection d'objets, derrière un adaptateur,
testable sans matériel, sans recycler le domaine `recognition`.

## Forces
- La détection est un **moteur IA externe** : adaptateur, pas règle métier
  (§4.2). Le domaine ne doit jamais importer YOLO/ONNX/cv2/numpy (§2).
- Contrainte licence : redistribution et usage commercial possibles seulement
  si le modèle le permet (§11, §13). Les poids `buffalo_*` de `recognition`
  restent recherche-non-commerciale ; la branche détection doit être propre.
- Matériel cible : CPU i7-1355U, sans GPU. Latence à mesurer avant tout choix
  (§8.3).
- `onnxruntime` est déjà une dépendance (via InsightFace) : pas de nouvelle
  dépendance lourde.

## Décision
Nouveau module `detection` (domain / application / infrastructure), cohérent mais
**pas** promu en Bounded Context formel tant que ses invariants ne le justifient
pas (ARCHITECTURE §3.3) :

- `DetectedObject` (domaine, pur) : `label`, bbox entière, `score`, invariants
  validés à la construction directe. **Distinct de `FaceObservation`**.
- `ObjectDetector` (application, Port) : `detect(frame) -> list[DetectedObject]`.
  Frontière externe réelle → port justifié (OCP : remplacer le détecteur sans
  toucher au reste).
- `YoloxOnnxObjectDetector` (infrastructure) : letterbox → ONNX Runtime →
  décodage grille/stride → NMS par classe → rescale → mapping COCO → allow-list
  (`person, bicycle, car, motorcycle, bus, truck` par défaut).
- Post-traitement pur (`yolox_postprocess`: `make_grid`, `decode`, `nms`) isolé
  et testé sans le modèle (TDD, §10.1).

**Modèle :** YOLOX (Megvii-BaseDetection), **licence Apache-2.0** (usage
commercial + redistribution autorisés, vérifié sur le fichier LICENSE officiel).
ONNX pré-exportés officiels `0.1.1rc0`, entrée `[1,3,416,416]`, sortie brute
`[1,3549,85]`. Modèle par défaut **`yolox_nano`** (latence) ; `yolox_tiny`
disponible pour plus de rappel. Modèles non versionnés dans Git (`/models/`).

Détection **désactivée par défaut** (`detection_enabled=False`) ; opt-in par
configuration. Les deux branches (détection / visage) ne tournent pas
obligatoirement sur chaque frame (§4.3). La détection ne confirme aucune
identité ni intrusion : fait physique observable seulement (§1).

## Conséquences
- Positives : capacité personnes/véhicules licence-propre, testable hors
  matériel, substituable, sans contamination du domaine `recognition`.
- Négatives / limites : pas encore câblée dans la boucle live principale (reste
  M12), pas de tracking ni de zones/franchissement (M4), précision non évaluée
  sur corpus annoté (nécessite clips consentis). Le nombre d'occupants d'un
  véhicule n'est pas déductible (§7).

## Preuve (reproductible)
- Smoke-test chargement + inférence sur frame 416² : `nano` 13.8 ms, `tiny`
  26.6 ms (médianes, CPU i7-1355U, CPUExecutionProvider).
- End-to-end sur image canonique (1080×810), seuil 0.3 :
  - `nano` (41 ms) : `bus 0.91` + 3 × `person` (0.69–0.85).
  - `tiny` (51 ms) : `bus 0.95` + 3 × `person` (0.85–0.88).
- Suite : 139 tests OK, ruff clean, mypy clean (55 fichiers).
- Unitaires purs : `make_grid` (3549 ancres, strides 8/16/32), `decode`
  (grille/stride + score obj×cls), `nms` (suppression des recouvrements).
