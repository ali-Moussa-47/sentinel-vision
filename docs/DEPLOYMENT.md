# Déploiement fiable — strict minimum (VPS Linux, sans écran)

Objectif : faire tourner Sentinel Vision **24/7 sur un serveur sans écran**, qui
**redémarre tout seul** en cas de crash ou de reboot. Une instance = une caméra.

## 1. Installer (une fois par serveur)
```bash
git clone <ton-depot> && cd sentinel-vision
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[plates]"
```

## 2. Configurer la caméra (un fichier par caméra)
Copie `docs/examples/camera.example.json` → `config/portail.json` et édite-le
(URL RTSP, nom, plaques, alertes). Voir le gabarit pour toutes les clés.

## 3. Lancer sans écran (headless)
Sur un serveur il n'y a pas d'affichage : le mode `--headless` est **obligatoire**.
```bash
sentinel-vision --config config/portail.json --headless
```
(Alerte push recommandée sur serveur : `webhook_url` dans le JSON, ou `--webhook`.
WhatsApp a la contrainte des 24 h ; un webhook ntfy marche en continu.)

## 4. Redémarrage automatique (systemd)
Crée `/etc/systemd/system/sentinel-portail.service` :
```ini
[Unit]
Description=Sentinel Vision - portail
After=network-online.target
Wants=network-online.target

[Service]
User=sentinel
WorkingDirectory=/home/sentinel/sentinel-vision
ExecStart=/home/sentinel/sentinel-vision/.venv/bin/sentinel-vision --config config/portail.json --headless
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Active + démarre :
```bash
sudo systemctl enable --now sentinel-portail
```
`Restart=always` = l'app repart seule après un crash ou un reboot.

## 5. Voir les logs (déjà capturés, rien à coder)
systemd enregistre tout ce que l'app affiche :
```bash
journalctl -u sentinel-portail -f          # en direct
journalctl -u sentinel-portail --since today
```

## 6. Plusieurs caméras / plusieurs serveurs (flotte)
Un service systemd **par caméra** (`sentinel-portail`, `sentinel-cour`, …), chacun
avec son fichier `--config`. Pour des milliers de caméras : répéter sur N serveurs
(modèle de réplication, voir `docs/adr/ADR-010`). Aucune brique centrale requise.

## Arrêt propre
`sudo systemctl stop sentinel-portail` envoie SIGTERM : l'app libère la caméra,
vide les files d'alertes et se ferme proprement.

---
Ce qui n'est **pas** inclus (voir `docs/LIMITATIONS.md`) : Docker, supervision
centralisée, base de données partagée, historique consolidé multi-caméras.
À ajouter seulement si une exploitation réelle le justifie.
