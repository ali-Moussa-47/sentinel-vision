# ADR-010 — Modèle de déploiement et d'échelle (flotte de caméras)

## Contexte
Objectif exprimé : pouvoir exploiter « des milliers de caméras déployées sur
différents serveurs ». Le produit est aujourd'hui un monolithe modulaire local
mono-caméra, sans état global, assemblé au composition root.

La constitution (CLAUDE.md §3, ARCHITECTURE.md §1) interdit explicitement
d'optimiser prématurément pour microservices, multi-caméras, cloud distribué,
event streaming, base de données massive ou orchestration, sans besoin et preuve.

## Forces
- Le pipeline est **sans état partagé** entre caméras : chaque session traite une
  source, une watchlist, ses propres alertes.
- Une caméra = une charge CPU (inférence) essentiellement **indépendante** des
  autres. La vision par ordinateur temps réel est gourmande : agréger des milliers
  de flux dans un seul process est un anti-pattern (contention, pannes corrélées).
- L'isolation des pannes et la simplicité d'exploitation priment pour un parc.

## Décision
**Échelle par réplication, partage-de-rien (shared-nothing).**

- **Unité de déploiement = une instance Sentinel Vision par (1 à quelques)
  caméra(s)**, configurée **déclarativement** (fichier de config par instance).
- **Des milliers de caméras = des milliers d'instances** réparties sur N serveurs
  (VPS, bare-metal), chacune indépendante. Pas de process unique multi-flux.
- Chaque instance est **autonome** : sa source, sa watchlist, ses captures, ses
  alertes, sa rétention. Aucune dépendance inter-instances au runtime.
- L'orchestration de flotte (lancer/superviser N instances) est déléguée à des
  outils **existants et éprouvés** (systemd, Docker/Compose, Nomad/K8s selon le
  parc), **pas** réécrite dans l'application.

**Ce qu'on NE construit PAS maintenant** (YAGNI, jusqu'à preuve d'un besoin réel) :
agrégation centrale inter-caméras, base de données partagée, API multi-tenant,
bus d'événements, tableau de bord flotte. Ces briques seront des ADR dédiées
**quand** une exploitation réelle en démontrera la nécessité.

## Conséquences
- **Positives** : scalabilité horizontale quasi-linéaire par ajout de serveurs ;
  isolation des pannes ; déploiement reproductible ; respect de YAGNI ; le code
  métier reste simple et testable.
- **Enablers requis** (backlog, par ordre) : config par fichier (fait/en cours),
  logs structurés, packaging (Docker), mode service (restart), heartbeat, puis
  — si et seulement si le parc l'exige — une couche d'agrégation optionnelle.
- **Négatives / limites** : pas de vue consolidée « toutes caméras » native ;
  la corrélation inter-caméras (suivre une plaque d'un site à l'autre) n'existe
  pas et ne doit pas être faite par biométrie sans base légale (CLAUDE.md §11).

## Preuve / suivi
- Validation réelle (FPS/latence par instance, nb de caméras par serveur selon
  CPU) : **à mesurer** sur matériel cible — voir `docs/LIMITATIONS.md §5`.
- Dettes techniques associées : test RTSP réel, déploiement VPS Hostinger.
