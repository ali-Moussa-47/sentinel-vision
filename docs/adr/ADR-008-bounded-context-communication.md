# ADR-008 — Bounded Context Communication (notification email)

## Contexte
Après capture locale (ADR-007), l'utilisateur veut être notifié d'un match sur
ses propres caméras (usage privé). Envoyer un email est une nouvelle
responsabilité, avec un vocabulaire et un cycle de vie distincts de la
reconnaissance → gate de création d'un BC (ARCHITECTURE §3.3) satisfait.

## Forces
- Le réseau peut être instable (ex. Tchad) ; un envoi SMTP bloque plusieurs
  secondes → interdit dans la boucle live (14 FPS).
- Identifiants SMTP = secrets.
- Rester simple, sans framework ni nouvelle dépendance.

## Décision
Nouveau BC `communication`, découplé de `recognition` :
- **Domaine** : `EmailAddress`, `EmailMessage` (VO validés, invariants en
  `__post_init__`, miroir des records Java d'origine) + erreurs métier.
- **Application** : port `EmailSender` (+ `EmailSendingError`).
- **Infrastructure** : `SmtpEmailSender` (stdlib `smtplib`/`email`, timeout,
  erreurs traduites) ; `MailSettings.from_env` (secrets via
  `SENTINEL_SMTP_HOST/PORT/USER/PASSWORD/FROM/TO/TLS`, jamais en CLI/defaults) ;
  `BackgroundEmailSender` (décorateur `EmailSender` : file + thread démon →
  `send()` non bloquant, échecs journalisés via `on_error`).
- **Intégration** (composition root, pas dans les BCs) : le match déclenche des
  **sinks** (`MatchSink`) via `MatchAlerter` (anti-spam partagé, OCP) ;
  `SnapshotSink` (capture) et `EmailAlertSink` (bootstrap, traduit un match en
  `EmailMessage` et appelle `EmailSender`) coexistent. Les BCs restent
  indépendants ; seul le composition root connaît les deux.
- **Opt-in** : `--notify` (défaut off). `BackgroundEmailSender.close()` au
  shutdown pour vider la file.

## Conséquences
- La boucle live n'est jamais bloquée par SMTP (envoi en arrière-plan).
- Ajouter un canal (Telegram, webhook) = nouvel adaptateur `EmailSender`-like +
  un sink, sans toucher la reconnaissance (OCP).
- **Best-effort** : en cas de panne réseau, l'email est journalisé comme échec,
  pas réessayé ; la preuve durable reste le **snapshot local** (ADR-007). Une
  livraison durable (file persistée + retry) serait une évolution (nouvelle ADR).
- Secrets hors ligne de commande/historique.

## Hors périmètre
Retry durable, pièce jointe image, espace public, autres canaux.

## Preuves
Tests : email_address/email_message (validation), smtp build_mime (en-têtes/corps),
background_email_sender (livraison + échec non propagé), mail_settings (env,
requis manquant, destinataire invalide), match_alerter (sinks/anti-spam),
snapshot_sink, email_alert_sink. Fan-out e2e headless : 1 match → 1 snapshot +
1 email (score+caméra), re-déclenchement bloqué en cooldown. Suite verte (127)
au 2026-10-04 ; ruff/mypy clean (46 fichiers).
