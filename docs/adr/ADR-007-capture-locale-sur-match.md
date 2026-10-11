# ADR-007 — Capture locale d'instantané sur match confirmé

## Contexte
Besoin produit (déploiement privé, caméras personnelles de l'utilisateur, ex.
jardin) : après un `POTENTIAL MATCH` confirmé, enregistrer automatiquement une
photo de la personne pour preuve/consultation. La constitution interdit la
persistance automatique par défaut (§15) ; il faut donc une décision explicite,
en opt-in et local-only.

## Forces
- Persister une image d'une personne = donnée biométrique sensible.
- La boucle live ne doit pas être ralentie (écriture I/O).
- Spam : une personne reste dans le champ plusieurs secondes → des centaines de
  frames.
- Usage privé déclaré (caméras de l'utilisateur, aucun espace public).

## Décision
- **Opt-in** : désactivé par défaut (`capture_enabled=False`) ; activé par
  `--capture`. Comportement par défaut inchangé (reconnaissance pure).
- **Anti-spam** (`MatchSnapshotAlerter`, application, pur et testé) : une capture
  par sujet par `capture_cooldown_seconds` (défaut 30 s), horloge injectée.
  Déclenché sur les résultats CONFIRMÉS (post-tracker), uniquement `POTENTIAL_MATCH`.
- **Écriture locale** (`LocalSnapshotWriter`, infra) : recadrage du visage (+30 %
  de marge) depuis la frame PROPRE (avant overlay), sauvegarde sous
  `data/captures/<sujet>/<horodatage>_<caméra>_<score>.jpg`. Identifiant de sujet
  et nom de caméra assainis (`safe_subject_id`, partagé avec le watchlist writer,
  DRY) ; pas de sortie du dossier racine.
- **Localisation = métadonnée caméra** (`camera_name`, ou label index/NET), pas
  de GPS : une caméra fixe a une position connue et figée.
- `data/captures/` est git-ignoré.

## Conséquences
- Preuve locale par personne, sans réseau ni cloud.
- Coût par frame négligeable (capture rare, recadrage d'une région déjà décodée).
  Si un cooldown très court ou de nombreux sujets simultanés rendaient l'I/O
  bloquante, déporter l'écriture hors boucle (worker) — à mesurer d'abord.
- Donnée biométrique persistée localement : l'utilisateur est responsable de la
  rétention, de l'accès et de la base légale. Reste local-only ; l'envoi réseau
  (email/Telegram) serait une décision séparée (Phase 2, nouvelle ADR).

## Hors périmètre
Envoi réseau/notifications, journal d'audit structuré, espace public.

## Preuves
Tests : `test_match_snapshot_alerter.py` (anti-spam/cooldown, matches seulement),
`test_local_snapshot_writer.py` (fichier écrit, recadrage lisible, traversal
contenu). Vérif e2e headless : 1 match → 1 fichier `moussa_demo/..._garden_0.93.jpg`,
UNKNOWN ignoré, re-capture bloquée en cooldown. Suite verte (109) au 2026-10-04.
