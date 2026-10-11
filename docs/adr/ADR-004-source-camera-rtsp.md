# ADR-004 — Source caméra réseau (RTSP)

## Contexte
Besoin réel : une caméra Wi‑Fi/IP déjà installée (diffusion temps réel via son
app). `OpenCVCamera` ne supportait qu'un index local (webcam/USB, CAP_DSHOW).
Une caméra réseau se consomme en **RTSP** (URL, pas un index).

## Forces
- La constitution (§19) impose une analyse avant d'introduire le réseau dans le
  chemin nominal.
- Une URL RTSP contient souvent des identifiants (`rtsp://user:pass@ip`).
- CPU only ; la latence/FPS dépendent du flux choisi (main vs sub-stream).

## Décision
`AppConfig.camera_url: str | None`. Si défini, `OpenCVCamera` ouvre
`cv2.VideoCapture(url, CAP_FFMPEG)` avec `CAP_PROP_BUFFERSIZE=1` (latence mini,
dernière frame) ; sinon index local inchangé. `--source URL` sur les trois CLIs
(prioritaire sur `--camera`). Les identifiants sont **masqués** dans tout
message (`mask_credentials`, testé). L'overlay affiche `CAM NET` pour une source
réseau.

## Conséquences
- L'app consomme une caméra IP existante sur le **LAN** (pull, lecture seule) ;
  l'app d'origine peut continuer d'enregistrer en parallèle.
- Réseau introduit UNIQUEMENT en entrée locale : pas de cloud, pas de stockage,
  pas de télémétrie ; aucun identifiant journalisé.
- Débit/portée dépendent du flux : sous-flux (SD) pour le FPS, flux principal
  (HD/4K) pour la portée — à mesurer avec la sonde.

## Preuves
`mask_credentials` couvert par test ; suite verte (67). Ouverture réseau réelle
à valider par l'utilisateur sur sa caméra (URL testable d'abord dans VLC).
