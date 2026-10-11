# ADR-006 — Streaming résilient (réseau instable)

## Contexte
Déploiement sur réseau instable (ex. Tchad, Wi‑Fi hésitant). Un flux RTSP peut
bégayer, décrocher, ou pire : `VideoCapture.read()` peut **bloquer
indéfiniment** quand le réseau stalle. Avant, une seule frame ratée détruisait
la session live (écran de reprise affiché en boucle).

## Décision
Deux mécanismes complémentaires dans `bootstrap/frame_source.py` :

1. **Timeouts FFMPEG** sur `StreamSource` : `CAP_PROP_OPEN_TIMEOUT_MSEC` et
   `CAP_PROP_READ_TIMEOUT_MSEC = stream_timeout_ms`. `read()` échoue (CameraError)
   au lieu de bloquer indéfiniment.
2. **`ResilientFrameSource`** (décorateur de `FrameSource`) : sur échec de
   `read()`, reconnexion automatique (fermer + recréer la source) jusqu'à
   `reconnect_attempts` avec `reconnect_backoff` entre les tentatives. Si tout
   échoue → `CameraError` → écran de reprise premium (l'utilisateur garde la
   main). L'ouverture INITIALE n'est pas masquée (fail‑fast → écran).

Défauts conservateurs, configurables (`AppConfig`) :

```
stream_timeout_ms = 5000   reconnect_attempts = 3   reconnect_backoff = 1.0
```

## Conséquences
- Une coupure transitoire (quelques secondes) est absorbée de façon transparente
  sans tuer la session ; une coupure durable bascule proprement sur l'écran de
  reprise.
- Le blocage réseau est borné par le timeout (prouvé : flux injoignable échoue
  en ~2,3 s au lieu de geler).
- Pendant une reconnexion, la fenêtre se fige brièvement (sleep borné) — accepté.
- Décorateur = OCP/SRP : la résilience compose au‑dessus de n'importe quelle
  `FrameSource` sans modifier les adaptateurs.
- Hors périmètre : reconnexion infinie non surveillée (kiosk 24/7) — possible
  évolution (augmenter attempts, ou auto‑retry de l'écran).

## Preuves
Unit : blip→reconnexion+récupération, échec persistant→CameraError après N,
réouverture qui échoue une fois→récupère quand même. Intégration : RTSP
injoignable échoue en ~2,3 s (timeout), erreur propre sans identifiants.
Suite verte (74) au 2026-10-04. ruff/mypy clean.
