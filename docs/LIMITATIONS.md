# Sentinel Vision — Limites connues et périmètre honnête

> Ce document liste ce que le produit **ne garantit pas**, et pourquoi.
> Règle du projet : une détection crédible vaut mieux qu'une identification forcée.
> Mis à jour : 2026-10-16.

Légende statut : **PHYSIQUE** (limite du monde réel, aucun logiciel ne la lève) ·
**NON VALIDÉ** (possible mais non prouvé sur matériel/corpus) ·
**NON IMPLÉMENTÉ** (fonctionnalité absente) · **DETTE** (prévu, à faire).

---

## 1. Reconnaissance faciale

- **PHYSIQUE** — Un visage masqué, de dos, dans un véhicule, derrière une vitre
  teintée, flou de mouvement, de nuit ou à contre-jour peut être **impossible à
  reconnaître**. On détecte alors une *présence*, pas une *identité*.
- **PHYSIQUE / NON VALIDÉ** — Photo d'enfance vs adulte, grands écarts d'âge :
  aucune garantie de correspondance. Protocole d'évaluation (M2/M8) **non réalisé**
  (nécessite des paires datées consenties).
- **NON VALIDÉ** — Stratégie multi-photos par sujet (max des similarités) : peut
  augmenter les faux positifs à mesure que les références croissent ; **non
  calibré** sur jeu de validation indépendant.
- **NON VALIDÉ** — Les seuils (0.45) et la porte qualité (112 px, det 0.65) sont
  des valeurs de départ, **non calibrées** sur ta caméra ni ton éclairage.
- Une correspondance reste **POTENTIELLE** : jamais une preuve d'identité ni une
  décision défavorable automatique.

## 2. Détection d'objets / suivi

- **PHYSIQUE** — Un objet hors champ, entièrement occulté ou trop petit n'est pas
  détectable. Le nombre d'occupants d'un véhicule n'est **pas** déductible.
- **NON VALIDÉ** — Recall, faux positifs, changements d'ID, pertes de piste **non
  mesurés** sur corpus annoté (marche/course/nuit/2 personnes/occlusions).
- Le suivi est un tracker IoU simple ; un ID de piste est **temporaire**, pas une
  identité civile. Pas de ByteTrack/BoT-SORT (non justifié par mesure à ce jour).

## 3. Lecture de plaque (ANPR)

- **PHYSIQUE** — Véhicule rapide (peu de frames), flou de mouvement, plaque sale,
  angle fort, nuit sans éclairage adapté : lecture **non garantie**. Dépend de
  l'obturateur, de la résolution et de l'éclairage de la caméra.
- **NON VALIDÉ** — Précision non mesurée sur de vraies plaques à distance/angle.
- **NON IMPLÉMENTÉ** — La confirmation exige N lectures **identiques** ; une plaque
  lue tantôt `3BU` tantôt `8BU` ne se confirme jamais (pas d'agrégation robuste /
  vote majoritaire tolérant). *(voir backlog : confirmation robuste)*
- **Licence** — Code fast-alpr MIT ; licence des **poids** non confirmée (détecteur
  basé YOLOv9/GPL) → **usage commercial à revalider avant distribution**.

## 4. Notifications / alertes

- **DETTE** — WhatsApp Cloud : envoi réel non testé contre Meta ; forme libre
  limitée à la fenêtre 24 h → **templates requis** pour un push always-on.
- **NON IMPLÉMENTÉ** — Telegram, SMS, secours hors-ligne.
- **NON IMPLÉMENTÉ** — La file d'alertes est **en mémoire** : perdue si le process
  redémarre (pas de persistance/retry durable).
- **PHYSIQUE** — Tout canal (WhatsApp/email/webhook) envoie vers un **serveur
  externe** ; donnée personnelle qui sort de la machine.

## 5. Performance et échelle

- **NON VALIDÉ** — FPS / latence des 3 branches ensemble sur un vrai flux RTSP :
  **jamais mesurés**. ANPR ~150–400 ms/lecture (CPU) ; InsightFace ~70 ms ; YOLOX
  ~14 ms. Budgets réels à établir sur matériel cible.
- **Modèle d'échelle** — « milliers de caméras » = **réplication** (1 instance par
  caméra, N instances sur N serveurs), PAS un process unique multi-flux.
  Voir `docs/adr/ADR-010`.
- **NON IMPLÉMENTÉ** — Il n'y a **pas** d'orchestrateur central, de base de données
  partagée, d'API multi-tenant, ni d'agrégation inter-caméras. Volontaire (YAGNI) :
  à construire seulement quand une exploitation réelle de flotte le prouvera.

## 6. Exploitation / déploiement

- **DETTE** — Pas encore testé sur VPS (Hostinger) ni sur vraie caméra RTSP.
- **EN COURS** — Config par fichier (déploiement déclaratif par instance).
- **NON IMPLÉMENTÉ** — Logs structurés, mode service (démarrage auto/restart),
  packaging (Docker), supervision/heartbeat, historique d'événements persistant.

## 7. Sécurité / vie privée

- Les captures (visages, plaques) sont des **données personnelles**. Rétention
  configurable + purge automatique disponibles, mais **désactivées par défaut**.
- La conformité (base légale, signalétique, durée de conservation, droit à
  l'effacement) est une responsabilité **d'exploitation**, hors code.
- Secrets via variables d'environnement ; pas de coffre à secrets intégré.
