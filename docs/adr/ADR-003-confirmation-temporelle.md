# ADR-003 — Confirmation temporelle (fiabilité, notamment à distance)

## Contexte
À distance (visage proche de la taille minimale), le score de similarité d'une
SEULE frame est bruité : un visage peut franchir le seuil sur une frame isolée
puis repasser en dessous. Décider sur une frame unique produit du scintillement
et, surtout, des faux positifs ponctuels — contraire à l'exigence « aucune
fausse alerte ».

## Forces
- Pipeline temps réel : plusieurs frames par seconde du même visage sont
  disponibles « gratuitement ».
- Un door-camera observe généralement une personne qui approche (séquence
  temporelle cohérente).
- La constitution (ARCHITECTURE §8.1) exige mesure + ADR pour toute évolution
  vers un pipeline avec état.

## Décision
Ajouter une couche de confirmation temporelle, à état mais locale à la session :

- `FaceObservation.iou` (géométrie pure) pour associer un visage à sa piste.
- `FaceTracker` (application) : associe chaque visage courant à une piste par IoU
  (greedy), maintient une fenêtre bornée des résultats récents par piste, fait
  vieillir et supprime les pistes absentes.
- `MatchConfirmation` (domaine, pur) : un POTENTIAL MATCH n'est affiché que si le
  résultat de la frame COURANTE est un match pour un sujet S **et** que S a été
  reconnu dans au moins `confirm_frames` des `confirmation_window` dernières
  frames de la piste. Si la frame courante est UNKNOWN / INSUFFICIENT_QUALITY, la
  confirmation ne s'applique pas (pas d'hystérésis sur une frame dégradée). Cet
  ancrage sur la frame courante empêche une nouvelle personne d'hériter de
  l'identité confirmée de la précédente dans la même bbox. Le score affiché reste
  un score réellement mesuré (meilleur score récent du sujet) — aucune donnée
  fabriquée.
- Reconnexion : `ResilientFrameSource` masque les reconnexions mais expose un
  `reconnect_count` ; la boucle live **réinitialise le tracker** (`reset()`)
  quand ce compteur change, pour qu'aucune piste ne survive à une discontinuité
  de flux.

Défauts CONSERVATEURS (dans `AppConfig`, source unique) :

```
confirm_frames = 3        confirmation_window = 5
track_iou_threshold = 0.3 track_max_misses = 15
```

Ces défauts sont prudents mais **non calibrés**. La confirmation ne réduit les
faux positifs que si l'association de pistes est correcte et si les erreurs ne
sont pas corrélées dans le temps — à valider sur séquences multi-personnes
(croisements, remplacement dans la même zone), pas supposé « monotone ».

## Conséquences
- Un pic de similarité sur une frame isolée ne déclenche plus d'alerte (prouvé
  par test : `test_single_frame_spike_is_not_confirmed`).
- Une nouvelle personne (UNKNOWN) dans la bbox d'un match précédent n'hérite pas
  de l'identité (prouvé : `test_confirmed_identity_is_not_inherited_by_a_new_unknown_person`).
- Un MATCH confirmé apparaît après quelques frames (latence courte, souhaitable
  pour une porte ; négligeable à la démo).
- État local à la session, réinitialisé à la reconnexion détectée ; injecté au
  composition root ; pas d'état global.
- Limite connue : l'association reste purement géométrique (IoU). Deux visages
  qui se croisent peuvent échanger de piste ; une association IoU + embedding
  serait plus robuste mais doit être mesurée avant d'être ajoutée.

## À calibrer (données requises)
`confirm_frames`, `confirmation_window`, `track_iou_threshold` doivent être
ajustés avec des mesures réelles (sonde de distance + séquences terrain) : au
FPS cible, combien de frames de confirmation donnent le meilleur compromis
latence / robustesse par tranche de distance. Ne pas assouplir la confirmation
pour « accélérer la démo » sans remesurer le taux de faux positifs.

## Preuves
Tests unitaires : `test_match_confirmation.py`, `test_face_tracking.py`,
`test_face_observation.py` (IoU). Suite complète verte (65 tests) au 2026-10-04.
