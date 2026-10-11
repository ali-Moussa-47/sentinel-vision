# ADR-005 — Abstraction de source de frames (OCP)

## Contexte
Deux types d'entrée réels existent (webcam par index, flux RTSP), et le besoin
produit est « supporter plusieurs types de caméra, juste une question de
branchement ». Une classe unique avec un `if url:` interne violait l'OCP :
ajouter un type imposait de modifier cette classe.

## Décision
Introduire une frontière explicite dans `bootstrap/frame_source.py` :

- `FrameSource` (Protocol) : contrat `__enter__ / __exit__ / read() -> frame`.
- Adaptateurs : `WebcamSource` (index, CAP_DSHOW) et `StreamSource` (URL/flux,
  CAP_FFMPEG, buffer=1, identifiants masqués).
- Fabrique : `open_frame_source(config) -> FrameSource` — seul endroit qui mappe
  la configuration vers un type de source.

Les composition roots (`main`, `enroll`, `distance_probe`) dépendent de la
fabrique, pas d'une classe concrète.

## Conséquences
- OCP : ajouter un type (fichier vidéo, MJPEG HTTP, SDK propriétaire…) = une
  nouvelle classe implémentant `FrameSource` + une ligne dans la fabrique ; les
  sources existantes ne changent pas.
- Composition, pas héritage : logique commune factorisée en helpers
  (`_opened`, `_read`, `_release`), pas de classe de base.
- Sélection de source testable sans matériel (type retourné par la fabrique).

## Hors périmètre
Un process unique pilotant N caméras simultanément (multi-vues) reste hors
périmètre (CPU-bound ; nécessiterait GPU + ADR). Déploiement multi-caméras =
**une instance par caméra**.

## Preuves
Tests : sélection de source (webcam vs stream) + masquage des identifiants.
Suite verte (69) au 2026-10-04. ruff/mypy clean.
