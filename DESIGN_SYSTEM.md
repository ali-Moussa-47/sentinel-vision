# DESIGN_SYSTEM.md --- Sentinel Vision

> **Source de vérité du langage visuel, du motion design, de la
> hiérarchie d'information et de la qualité perceptuelle de Sentinel
> Vision.**
>
> Lire d'abord :
>
> ``` text
> .claude.md
> ARCHITECTURE.md
> ```
>
> Ce document définit **comment Sentinel Vision doit paraître, réagir et
> rester lisible pendant une analyse vidéo temps réel**.
>
> Il ne définit pas l'algorithme de reconnaissance, le seuil métier, le
> moteur InsightFace, les ports/adapters ou les Bounded Contexts.
>
> Comme l'architecture, ce Design System est **vivant**. Il peut être
> remis en question lorsqu'un test utilisateur, une contrainte OpenCV,
> une mesure de performance ou le code réel démontre qu'une règle est
> mauvaise.
>
> Claude Code, Codex et ce document peuvent se tromper. Ne jamais
> sacrifier lisibilité, FPS ou compréhension pour respecter aveuglément
> une règle visuelle.

------------------------------------------------------------------------

# 1. Design North Star

Sentinel Vision doit donner la sensation d'un produit de vision assistée
:

``` text
Precise
Calm
Technical
Immediate
Controlled
Premium
Readable
Confident
Smooth
Operational
Low-cognitive-load
```

Le produit doit paraître **haut de gamme sans paraître spectaculaire
pour le plaisir de l'être**.

La sophistication vient de :

``` text
alignment
spacing
typography
contrast
motion quality
information hierarchy
stable geometry
excellent feedback
performance
attention to detail
```

Pas de :

``` text
cyberpunk
neon overload
HUD de film
glow partout
animations permanentes
grilles décoratives
fausses données
effets "hacker"
```

------------------------------------------------------------------------

# 2. Direction visuelle --- MUI / Material premium

La référence principale est un langage proche de :

``` text
Material UI / Material Design 3
+
professional monitoring software
+
modern desktop tooling
+
minimal computer-vision overlay
```

Nous reprenons de MUI :

-   hiérarchie claire des surfaces ;
-   composants prévisibles ;
-   états explicites ;
-   spacing cohérent ;
-   typographie rationnelle ;
-   excellent contraste ;
-   feedback immédiat ;
-   composants accessibles ;
-   elevation utilisée avec discipline.

Nous ne cherchons PAS à reproduire un dashboard MUI générique.

Sentinel Vision doit avoir sa propre identité :

> **Material precision + computer vision restraint.**

------------------------------------------------------------------------

# 3. Product Feeling

Sentinel Vision doit ressembler à :

``` text
premium vision workstation
modern monitoring application
professional AI tool
high-end engineering demo
```

Il ne doit pas ressembler à :

``` text
admin template
Bootstrap dashboard
gaming HUD
military movie interface
crypto dashboard
student OpenCV demo
AI-generated dashboard
collection of random cards
```

------------------------------------------------------------------------

# 4. Three-Second Rule

En moins de trois secondes, l'utilisateur doit comprendre :

``` text
Is the camera running?
Is the system ready?
Is a face detected?
What did the system decide?
How confident is the comparison?
```

Si l'utilisateur doit chercher ces réponses, la hiérarchie est mauvaise.

------------------------------------------------------------------------

# 5. Attention Budget

Une vue live doit avoir au maximum :

``` text
1 dominant surface
→ video

1 dominant status
→ recognition decision

2–4 secondary signals
→ camera / model / FPS / watchlist

everything else
→ quiet
```

La vidéo est toujours dominante.

Le chrome ne doit jamais combattre le flux caméra.

------------------------------------------------------------------------

# 6. Layout principal

Composition desktop recommandée :

``` text
┌──────────────────────────────────────────────────────────────┐
│ Sentinel Vision                           ● SYSTEM READY     │
├───────────────────────────────────────────┬──────────────────┤
│                                           │                  │
│                                           │  LIVE ANALYSIS   │
│                                           │                  │
│              LIVE CAMERA                  │  Status          │
│                                           │  Match           │
│                                           │  Confidence      │
│                                           │  Watchlist       │
│                                           │                  │
│                                           │  ─────────────   │
│                                           │  Diagnostics     │
│                                           │                  │
├───────────────────────────────────────────┴──────────────────┤
│ Camera 0     29 FPS     CPU inference      3 subjects        │
└──────────────────────────────────────────────────────────────┘
```

Répartition cible :

``` text
video
≈ 72–80%

side panel
≈ 20–28%
```

Ne pas faire un dashboard à quatre colonnes.

------------------------------------------------------------------------

# 7. Surface Hierarchy

Niveaux conceptuels :

``` text
Level 0
App background

Level 1
Primary workspace

Level 2
Side panel / toolbar

Level 3
Interactive control

Level 4
Transient overlay / dialog
```

Une elevation plus haute doit signifier une vraie superposition.

Pas de shadow autour de chaque bloc.

------------------------------------------------------------------------

# 8. Palette

Palette initiale premium dark-first :

``` python
COLORS = {
    "background": "#0B0D10",
    "surface": "#111418",
    "surface_subtle": "#171B20",
    "surface_elevated": "#1D2228",

    "primary": "#90CAF9",
    "primary_strong": "#42A5F5",
    "primary_container": "#132C3F",

    "text_primary": "#F5F7FA",
    "text_secondary": "#AEB7C2",
    "text_muted": "#77818D",

    "border": "#252B33",
    "border_strong": "#343C46",

    "success": "#66BB6A",
    "warning": "#FFB74D",
    "error": "#EF5350",
    "info": "#64B5F6",

    "scrim": "rgba(0, 0, 0, 0.52)",
}
```

Ces valeurs sont des tokens initiaux, pas des constantes sacrées.

------------------------------------------------------------------------

# 9. Color Discipline

Répartition :

``` text
neutral dark surfaces
→ 85%+

primary blue
→ controls / system identity

semantic colors
→ verified state only
```

Rouge, vert et orange ne sont jamais décoratifs.

``` text
green
→ operational success / confirmed ready

orange
→ degraded / attention

red
→ error / potential match alert when product semantics require it
```

**Important :** un score faible ou élevé ne reçoit pas automatiquement
une couleur sémantique sans règle produit explicite.

------------------------------------------------------------------------

# 10. Recognition Colors

Le résultat doit être visible sans devenir alarmiste.

Proposition initiale :

``` text
UNKNOWN
→ neutral / cool gray

FACE DETECTED
→ primary blue

POTENTIAL MATCH
→ restrained red emphasis

SYSTEM ERROR
→ red, distinct from recognition result
```

`POTENTIAL MATCH` et `SYSTEM ERROR` ne doivent jamais avoir exactement
la même présentation.

Le premier est un résultat de comparaison.

Le second est un état technique.

------------------------------------------------------------------------

# 11. Dark Mode

Le live camera workspace est **dark-first**.

Pourquoi :

-   réduit la compétition avec la vidéo ;
-   rend les overlays plus lisibles ;
-   convient à une démonstration technique ;
-   facilite une hiérarchie visuelle calme.

Cela ne signifie pas :

``` text
pure black everywhere
```

Préférer plusieurs noirs/gris légèrement différenciés.

------------------------------------------------------------------------

# 12. Typography

Famille recommandée :

``` text
Inter
```

Fallback :

``` text
Segoe UI
system sans-serif
```

Pour les valeurs techniques uniquement, une monospace peut être utilisée
:

``` text
JetBrains Mono
```

mais uniquement si déjà disponible ou justifiée.

Ne jamais transformer toute l'interface en monospace.

------------------------------------------------------------------------

# 13. Typography Scale

``` text
Display
32 / 40 / 700

Title Large
24 / 32 / 700

Title Medium
20 / 28 / 600

Title Small
16 / 24 / 600

Body Large
16 / 24 / 400

Body
14 / 20 / 400

Label
13 / 18 / 600

Caption
12 / 16 / 400

Technical
12–13 / 18 / 500 monospace optional
```

Rôles :

``` text
Display
→ rare major state

Title
→ panels / dialogs

Body
→ explanations

Label
→ controls / statuses

Technical
→ FPS / model / camera / score
```

------------------------------------------------------------------------

# 14. Numeric Readability

Les valeurs temps réel doivent être stables.

Préférer des chiffres tabulaires lorsque possible.

Exemple :

``` text
29 FPS
0.742
CAM 0
3 SUBJECTS
```

Éviter qu'une valeur changeante déplace constamment le layout.

Réserver une largeur suffisante.

------------------------------------------------------------------------

# 15. Spacing

Base : grille de 4 px.

``` text
4   micro
8   xs
12  sm
16  md
20  md+
24  lg
32  xl
40  xxl
48  section
64  major
```

Règle :

> utiliser l'espace avant d'ajouter une bordure.

------------------------------------------------------------------------

# 16. Radius

MUI-like, mais contenu :

``` text
small control     8
button            10
panel             12
dialog            16
pill              999
```

Pas de radius 24--32 partout.

La caméra peut rester presque rectangulaire.

------------------------------------------------------------------------

# 17. Borders

Borders :

``` text
1 px
low contrast
structural
```

Utiliser pour :

-   séparation panel/video ;
-   inputs ;
-   controls ;
-   selected state discret.

Ne pas encadrer chaque métrique.

------------------------------------------------------------------------

# 18. Shadows

Dark UI : les shadows doivent rester rares.

Préférer :

``` text
surface contrast
border
spacing
```

avant :

``` text
shadow
```

Une shadow est acceptable pour :

-   menu ;
-   dialog ;
-   tooltip ;
-   floating control.

------------------------------------------------------------------------

# 19. Glass / Blur

Pas de glassmorphism comme langage principal.

Blur éventuellement autorisé pour :

``` text
temporary floating toolbar
camera overlay label
dialog scrim
```

Seulement si :

``` text
readability improves
AND
FPS remains stable
```

Sinon : surface opaque.

------------------------------------------------------------------------

# 20. Camera Workspace

La caméra est la surface reine.

Elle doit :

-   conserver son ratio ;
-   éviter tout stretching ;
-   être centrée ;
-   ne jamais être recouverte par de gros panneaux ;
-   rester lisible lorsque plusieurs visages sont présents.

Les contrôles permanents dans l'image doivent être minimaux.

------------------------------------------------------------------------

# 21. Bounding Box

La bounding box est une information, pas une décoration.

Style cible :

``` text
1.5–2 px
clean corners
no glow
no pulsing
no animated scanning line
```

Label attaché :

``` text
UNKNOWN
```

ou :

``` text
POTENTIAL MATCH · 0.742
```

Le label doit être lisible sur fonds clairs et sombres.

Utiliser un fond semi-opaque compact.

------------------------------------------------------------------------

# 22. Bounding Box Geometry

Ne pas utiliser de gros rectangle agressif si des corner brackets
suffisent.

Pattern possible :

``` text
┌─                    ─┐
│                      │

       FACE

│                      │
└─                    ─┘
```

Mais si les corner brackets réduisent la compréhension, revenir au
rectangle simple.

Lisibilité \> style.

------------------------------------------------------------------------

# 23. No Sci-Fi Scanner

Interdit par défaut :

``` text
animated scan line
rotating reticle
face mesh permanent
matrix particles
radar sweep
glowing target
crosshair
hexagonal HUD
```

Une démo professionnelle doit sembler crédible, pas cinématographique.

------------------------------------------------------------------------

# 24. Side Panel

Le panneau d'analyse doit répondre à :

``` text
What is happening now?
What was decided?
Is the system healthy?
```

Ordre recommandé :

``` text
LIVE ANALYSIS

Current state
Recognition result
Confidence / similarity

Watchlist context

Divider

SYSTEM
Camera
Model
FPS
```

Les diagnostics restent secondaires.

------------------------------------------------------------------------

# 25. Recognition Result Component

Composition :

``` text
POTENTIAL MATCH
Moussa Demo
Similarity 0.742
```

ou :

``` text
UNKNOWN
No watchlist match
```

Ne pas afficher :

-   dix décimales ;
-   vecteur embedding ;
-   détails du modèle ;
-   jargon inutile.

------------------------------------------------------------------------

# 26. Confidence / Similarity

Le score ne doit jamais prétendre être une probabilité si ce n'en est
pas une.

Afficher :

``` text
Similarity
0.742
```

et non :

``` text
74.2% certain
```

sauf si le modèle et la calibration justifient réellement cette
interprétation.

------------------------------------------------------------------------

# 27. Status Bar

Barre inférieure compacte :

``` text
● Camera 0    29 FPS    CPU    Watchlist 3    Model ready
```

Elle doit être :

``` text
quiet
single-line
stable
diagnostic
```

Pas une deuxième navigation.

------------------------------------------------------------------------

# 28. System Status

États principaux :

``` text
STARTING
READY
DEGRADED
ERROR
```

Affichage :

``` text
● SYSTEM READY
```

Un point de couleur + texte suffit.

Pas d'animation permanente.

------------------------------------------------------------------------

# 29. Buttons

Style MUI-like :

### Primary

Pour l'action principale rare :

``` text
Start camera
Retry
```

### Secondary / outlined

``` text
Settings
Reload watchlist
```

### Text

``` text
Cancel
Close
```

Règles :

-   hauteur 40--44 px desktop ;
-   label court ;
-   icône uniquement si elle aide ;
-   pas de gradient ;
-   pas de shadow lourde.

------------------------------------------------------------------------

# 30. Icon Buttons

Minimum hit target :

``` text
40 × 40 px desktop
```

Une icône seule doit avoir :

-   tooltip ;
-   accessible label ;
-   état hover ;
-   état pressed ;
-   état disabled.

------------------------------------------------------------------------

# 31. Icons

Style :

``` text
Material Symbols / equivalent coherent set
outlined or rounded
single family
```

Ne pas mélanger :

``` text
Font Awesome
emoji
Lucide
Material
custom SVG
```

sans raison.

------------------------------------------------------------------------

# 32. Chips

Usage limité à de vrais états ou filtres.

Acceptable :

``` text
LIVE
CPU
CAM 0
```

si cela améliore le scanning.

Pas de chips pour chaque ligne.

------------------------------------------------------------------------

# 33. Tooltips

Tooltips pour :

-   icon-only actions ;
-   métriques techniques ambiguës ;
-   contrôles secondaires.

Délai court mais non instantané.

Une action essentielle ne doit jamais dépendre d'un tooltip pour être
comprise.

------------------------------------------------------------------------

# 34. Motion Philosophy

Motion explique :

``` text
state
cause/effect
continuity
appearance/disappearance
```

Motion ne sert pas à impressionner.

Le meilleur motion design de Sentinel Vision doit souvent être presque
invisible.

------------------------------------------------------------------------

# 35. Motion Tokens

``` text
instant    80–100 ms
fast       140–180 ms
standard   220–260 ms
slow       320 ms maximum for exceptional transitions
```

Courbe :

``` text
ease-out for entrance
ease-in for exit
standard emphasized easing for state transitions
```

Pas de bounce.

Pas d'elastic.

------------------------------------------------------------------------

# 36. Press Feedback

Au clic :

``` text
immediate
```

Pattern :

``` text
opacity 1 → 0.88
```

ou légère variation de surface.

Pour un bouton desktop, le feedback MUI standard hover/pressed suffit.

Pas de scale spectaculaire.

------------------------------------------------------------------------

# 37. Recognition Motion

Lorsqu'un visage passe :

``` text
no match
→ bounding box appears quickly

potential match
→ label/color transitions once
```

Interdit :

``` text
continuous pulsing red
flashing
shake
repeated zoom
```

Le résultat doit attirer l'attention sans créer du bruit permanent.

------------------------------------------------------------------------

# 38. State Transition

Exemple :

``` text
UNKNOWN
   ↓
POTENTIAL MATCH
```

La transition peut faire :

``` text
color 160 ms
label crossfade 160 ms
```

Pas besoin d'animer la géométrie complète.

------------------------------------------------------------------------

# 39. Performance Is Design

Pour Sentinel Vision :

> **un overlay à 60 FPS visuellement simple est plus premium qu'un
> overlay spectaculaire qui fait chuter la vidéo.**

Chaque effet doit être évalué contre :

``` text
FPS
frame latency
CPU
GPU
memory
capture stability
inference latency
```

------------------------------------------------------------------------

# 40. Frame-Time Discipline

Ne jamais faire dans la boucle de rendu :

-   chargement de police ;
-   lecture disque inutile ;
-   construction répétée d'assets ;
-   recalcul de layout complexe ;
-   allocation massive évitable ;
-   logs verbeux par frame.

Pré-calculer ce qui est stable.

Mais ne pas optimiser sans profilage.

------------------------------------------------------------------------

# 41. Loading

Au démarrage :

``` text
App shell
↓
Initializing camera...
↓
Loading recognition model...
↓
Loading watchlist...
↓
Ready
```

Si l'initialisation est rapide, ne pas artificiellement montrer toutes
les étapes.

Éviter le spinner plein écran sans information.

------------------------------------------------------------------------

# 42. Skeleton

Un skeleton est utile seulement si une géométrie significative attend
des données.

Pour le live camera, préférer un placeholder stable :

``` text
Camera initializing
```

avec ratio déjà réservé.

------------------------------------------------------------------------

# 43. Empty State

Watchlist vide :

``` text
No subjects in the local watchlist.
Add a consented reference subject to test recognition.
```

L'état vide ne doit jamais simuler des données.

------------------------------------------------------------------------

# 44. Camera Failure

État :

``` text
Camera unavailable

Sentinel Vision could not open Camera 0.

Retry
```

Optionnellement, détails techniques dans une zone secondaire.

Ne jamais afficher une stack trace dans l'UI principale.

------------------------------------------------------------------------

# 45. Model Failure

Distinct de Camera Failure :

``` text
Recognition engine unavailable
```

Le système ne doit pas continuer à afficher un faux état `UNKNOWN`.

------------------------------------------------------------------------

# 46. Degraded Mode

Exemple :

``` text
Camera active
Recognition unavailable
```

La vidéo peut rester visible si techniquement possible.

Le statut doit clairement indiquer que la reconnaissance ne fonctionne
pas.

------------------------------------------------------------------------

# 47. Dialogs

Dialogs réservés à :

-   confirmation destructrice ;
-   erreur bloquante ;
-   configuration courte nécessitant focus.

Pas de modal pour chaque information.

------------------------------------------------------------------------

# 48. Settings

Pour la V1, settings minimalistes.

Possibles :

``` text
Camera
Watchlist path
Recognition threshold
Model
```

Mais un paramètre n'est exposé que si l'utilisateur doit réellement le
modifier.

Ne pas transformer la démo en panneau d'administration.

------------------------------------------------------------------------

# 49. Density

Desktop density :

``` text
comfortable
not mobile-spacious
not enterprise-dense
```

Un panel doit pouvoir être lu d'un coup d'oeil.

Éviter 20 lignes de diagnostics visibles simultanément.

------------------------------------------------------------------------

# 50. Progressive Disclosure

Vue live :

``` text
decision first
diagnostics second
advanced details hidden
```

Les informations comme :

-   provider ONNX ;
-   dimensions embedding ;
-   temps détaillé par étape ;
-   chemin modèle ;

doivent vivre dans un panneau diagnostics avancé si elles deviennent
utiles.

------------------------------------------------------------------------

# 51. Accessibility

Même pour un POC :

-   contraste suffisant ;
-   texte jamais transmis uniquement par couleur ;
-   labels explicites ;
-   taille lisible ;
-   focus clavier visible si GUI interactive ;
-   ordre de focus logique ;
-   Reduced Motion si framework GUI futur le permet.

Exemple :

``` text
red box alone
```

est insuffisant.

Préférer :

``` text
red box + POTENTIAL MATCH
```

------------------------------------------------------------------------

# 52. Keyboard

Si une vraie GUI desktop est introduite :

``` text
Space
→ pause/resume only if useful

Esc
→ close transient dialog

Ctrl/Cmd + ,
→ settings only if conventionally supported
```

Ne pas inventer beaucoup de raccourcis pour le POC.

------------------------------------------------------------------------

# 53. Responsive Desktop

Cible initiale :

``` text
1280 × 720 minimum practical demo
1920 × 1080 preferred
```

À largeur réduite :

``` text
video remains dominant
side panel may narrow
nonessential diagnostics collapse
```

Ne jamais réduire la vidéo à une vignette pour préserver des métriques.

------------------------------------------------------------------------

# 54. Fullscreen Demo Mode

Un mode présentation peut être étudié plus tard :

``` text
camera
+
minimal status
+
recognition overlay
```

Pas de side panel si cela améliore la démonstration.

Mais ne pas le construire avant que le besoin existe.

------------------------------------------------------------------------

# 55. OpenCV-Only V1

Si V1 utilise uniquement `cv2.imshow`, le Design System s'applique quand
même.

Priorités :

``` text
clean video
stable overlay
excellent typography within OpenCV limits
minimal status
consistent colors
no fake GUI complexity
```

Ne pas recréer Material UI pixel par pixel avec OpenCV.

OpenCV est un renderer vidéo, pas un framework d'interface complet.

------------------------------------------------------------------------

# 56. GUI Evolution Rule

Si le produit dépasse le POC et nécessite :

-   settings complexes ;
-   watchlist management ;
-   historique ;
-   plusieurs vues ;
-   recherche ;
-   formulaires ;
-   navigation ;

alors réévaluer le renderer.

Options futures à évaluer sur faits :

``` text
PySide6 / Qt
web UI
other desktop shell
```

Aucune migration n'est décidée dans ce document.

------------------------------------------------------------------------

# 57. MUI Look Without MUI Cargo Cult

Le terme "MUI look & feel" signifie ici :

``` text
disciplined surfaces
excellent states
clear typography
controlled radius
predictable controls
subtle elevation
semantic color
fast feedback
accessibility
```

Il ne signifie pas :

``` text
Card everywhere
Paper everywhere
Chip everywhere
blue buttons everywhere
dashboard grid
```

------------------------------------------------------------------------

# 58. Component Vocabulary

Créer seulement si réellement utilisé :

``` text
AppShell
TopBar
LiveViewport
AnalysisPanel
RecognitionStatus
SystemStatus
Metric
StatusBar
PrimaryButton
SecondaryButton
IconButton
Divider
Tooltip
Dialog
EmptyState
ErrorState
```

Ces noms sont conceptuels.

Ne pas créer tous les composants à l'avance.

------------------------------------------------------------------------

# 59. No Universal Components

Interdit :

``` text
UniversalCard
GenericPanel
DynamicWidget
EverythingRenderer
SmartContainer
```

si l'abstraction n'est pas soutenue par plusieurs usages réels.

------------------------------------------------------------------------

# 60. Component API Philosophy

Préférer l'intention :

``` text
RecognitionStatus(result)
```

à une explosion de propriétés :

``` text
Card(
    red=True,
    compact=True,
    icon=True,
    glow=False,
    bold=True,
    ...
)
```

Le composant connaît son rôle visuel.

Le domaine reste propriétaire du sens métier.

------------------------------------------------------------------------

# 61. State Matrix

Toute surface critique doit considérer :

``` text
initial
loading
ready
active
empty
degraded
error
disabled
```

Pour la caméra :

``` text
closed
opening
active
failed
```

Pour la reconnaissance :

``` text
initializing
ready
face_detected
unknown
potential_match
failed
```

Ne pas mélanger les machines d'état.

------------------------------------------------------------------------

# 62. Live Overlay Priority

Ordre visuel :

``` text
1. face location
2. recognition decision
3. subject label if applicable
4. similarity
5. secondary diagnostics
```

Jamais :

``` text
FPS > recognition result
```

dans la hiérarchie visuelle.

------------------------------------------------------------------------

# 63. Multiple Faces

Plusieurs visages doivent rester compréhensibles.

Chaque face :

``` text
bounding box
short label
optional compact score
```

Le side panel ne doit pas devenir une liste animée incontrôlable.

Si nécessaire, il peut montrer :

``` text
3 faces detected
1 potential match
```

avec détail du résultat le plus important.

La politique exacte doit être testée en situation réelle.

------------------------------------------------------------------------

# 64. Occlusion / Mask

Le design ne doit jamais présenter une détection difficile comme
certaine.

Si le moteur fournit une qualité exploitable et que le produit décide de
l'exposer, utiliser un langage prudent.

Ne pas inventer :

``` text
MASK BYPASS SUCCESS
```

ou autre message spectaculaire.

Le design reflète uniquement ce que le moteur et le domaine savent
réellement.

------------------------------------------------------------------------

# 65. No Fake Telemetry

Ne jamais fabriquer :

``` text
accuracy 99.9%
AI confidence
threat level
risk score
scan progress
database hits
```

pour rendre la démo plus impressionnante.

Une interface premium ne ment pas.

------------------------------------------------------------------------

# 66. No Threat Theater

Sentinel Vision ne doit pas afficher automatiquement :

``` text
THREAT
DANGER
HOSTILE
TARGET
SUSPECT
```

Une correspondance de watchlist est une correspondance potentielle, pas
une conclusion sur une personne.

Terminologie UI recommandée :

``` text
POTENTIAL MATCH
UNKNOWN
FACE DETECTED
SYSTEM READY
```

------------------------------------------------------------------------

# 67. Copy Style

Microcopy :

``` text
short
factual
calm
precise
```

Bon :

``` text
Potential match
Camera unavailable
Recognition engine ready
No watchlist match
```

Mauvais :

``` text
WARNING!!! WANTED PERSON DETECTED!!!
AI SCANNING TARGET...
ULTRA SECURE MODE
```

------------------------------------------------------------------------

# 68. Capitalization

Uppercase uniquement pour :

-   états courts ;
-   micro-labels techniques ;
-   signal opérationnel.

Exemple :

``` text
SYSTEM READY
POTENTIAL MATCH
LIVE
```

Pas pour les paragraphes.

------------------------------------------------------------------------

# 69. Hover

Si GUI desktop :

Hover doit apporter une indication subtile :

``` text
surface +4–6% luminance
cursor
tooltip when needed
```

Pas de translation verticale de cartes.

------------------------------------------------------------------------

# 70. Focus

Focus clavier visible :

``` text
2 px primary outline
sufficient offset
```

Ne jamais supprimer le focus sans alternative.

------------------------------------------------------------------------

# 71. Scrollbars

Si panneau scrollable :

-   scrollbar native ou discrète ;
-   pas de scrollbar custom spectaculaire ;
-   contenu essentiel visible sans scroll si possible.

------------------------------------------------------------------------

# 72. Dividers

Divider :

``` text
1 px
border token
```

Utilisé pour séparer :

``` text
recognition
──────────
system diagnostics
```

Pas entre chaque micro-métrique.

------------------------------------------------------------------------

# 73. Metric Pattern

Exemple :

``` text
FPS
29

INFERENCE
31 ms
```

Mais dans une surface compacte :

``` text
29 FPS
31 ms inference
```

est souvent meilleur.

Le nombre de métriques visibles doit rester limité.

------------------------------------------------------------------------

# 74. FPS Display

Le FPS est un diagnostic, pas un KPI marketing.

Ne pas :

-   le rendre énorme ;
-   le colorer vert par défaut ;
-   afficher un graphe sans besoin.

------------------------------------------------------------------------

# 75. Performance Graphs

Aucun chart en V1.

Un graphe FPS/latence n'est introduit que si :

-   diagnostic réel ;
-   profiling ;
-   démonstration technique explicitement demandée.

Sinon il augmente la charge cognitive.

------------------------------------------------------------------------

# 76. Image / Video Stability

La géométrie du viewport ne change pas lorsque :

-   un visage apparaît ;
-   un match apparaît ;
-   le score change ;
-   le side panel se met à jour.

Aucun layout shift dû aux données live.

------------------------------------------------------------------------

# 77. Smoothness Standard

Smoothness signifie :

``` text
I open
→ shell appears immediately

Camera starts
→ viewport stays stable

A face appears
→ overlay appears without jank

Result changes
→ information updates quietly

I interact
→ feedback is immediate

Inference slows
→ UI remains understandable
```

Smoothness ne signifie pas « plus d'animations ».

------------------------------------------------------------------------

# 78. Perceived Performance

Mauvais :

``` text
click
↓
nothing
↓
wait
↓
new state
```

Préférer :

``` text
click
↓
pressed feedback
↓
state transition starts
↓
operation completes
```

Ne jamais afficher un succès avant que l'opération soit réellement
réussie.

------------------------------------------------------------------------

# 79. Reduced Visual Noise

Avant d'ajouter :

``` text
icon
border
shadow
badge
color
animation
```

essayer :

``` text
spacing
alignment
typography
contrast
grouping
```

------------------------------------------------------------------------

# 80. Premium Test

Retirer mentalement :

``` text
motion
shadows
colors
```

Si la hiérarchie devient mauvaise, le design dépend trop des effets.

Un écran premium doit rester excellent en niveaux de gris.

------------------------------------------------------------------------

# 81. MUI Quality Test

Demander :

``` text
Is the hierarchy obvious?

Are surfaces meaningful?

Are component states complete?

Is spacing systematic?

Does semantic color carry real meaning?

Are controls predictable?

Is the typography disciplined?

Could a standard Material pattern solve this better?

Are we using cards only when grouping is real?
```

------------------------------------------------------------------------

# 82. Computer Vision Quality Test

Demander :

``` text
Can I see the video clearly?

Can I locate the detected face instantly?

Can I distinguish detection from recognition?

Can I distinguish unknown from technical failure?

Is the similarity represented honestly?

Does the overlay remain readable on any background?

Does the interface remain calm with multiple faces?
```

------------------------------------------------------------------------

# 83. Motion Review

Avant une animation :

``` text
What does it explain?
Does it improve continuity?
Does it affect FPS?
Could 160 ms solve it?
Would removing it hurt understanding?
```

Si la dernière réponse est non :

``` text
remove it
```

------------------------------------------------------------------------

# 84. Performance Review

Vérifier sur machine réelle :

``` text
camera FPS
inference latency
overlay cost
input latency
CPU
memory
startup
```

Un beau screenshot avec une vidéo saccadée est un mauvais design.

------------------------------------------------------------------------

# 85. Design Review

Avant validation :

``` text
What do I notice first?
Is that intentional?

Can I understand the live state in 3 seconds?

Is video dominant?

Are diagnostics quiet?

Too many panels?
Too many borders?
Too many colors?
Too many metrics?
Too much motion?

Could spacing solve this?
Could typography solve this?

Does UNKNOWN remain calm?
Does POTENTIAL MATCH remain unmistakable?
Does ERROR remain distinct?

Does the UI still look premium without effects?
```

------------------------------------------------------------------------

# 86. Definition of Done --- Live UI

Une vue live est terminée si :

``` text
camera is dominant
layout is stable
recognition state is immediately understandable
technical failure cannot masquerade as UNKNOWN
semantic colors are truthful
overlay is readable on light and dark imagery
multiple faces remain understandable
motion is purposeful
FPS remains acceptable
no fake metrics exist
no unnecessary sci-fi effects exist
```

------------------------------------------------------------------------

# 87. Definition of Done --- Component

Un composant est terminé si :

``` text
responsibility is clear
states are explicit
spacing uses tokens
typography uses roles
color uses semantic tokens
hover/pressed/disabled are considered when relevant
accessibility is considered
it does not own business decisions
it does not create unnecessary abstraction
```

------------------------------------------------------------------------

# 88. Definition of Done --- Premium Quality

``` text
precise
stable
quiet
fast
coherent
controlled
readable
intentional
```

Pas :

``` text
shiny
busy
glowing
animated everywhere
```

------------------------------------------------------------------------

# 89. Token Change Rule

Avant d'ajouter :

``` text
new color
new spacing
new radius
new font role
new motion duration
new elevation
```

demander :

``` text
Does an existing token solve it?
Will this recur?
```

Sinon :

``` text
do not extend the system
```

------------------------------------------------------------------------

# 90. Dependency Rule --- UI

Avant toute nouvelle bibliothèque UI :

1.  identifier le problème ;
2.  vérifier si OpenCV suffit pour la V1 ;
3.  vérifier la stdlib / stack existante ;
4.  mesurer le coût runtime ;
5.  mesurer l'impact packaging ;
6.  vérifier Windows ;
7.  vérifier maintenance ;
8.  seulement ensuite proposer.

Ne jamais ajouter une dépendance pour :

``` text
one pretty animation
one shadow
one icon
```

------------------------------------------------------------------------

# 91. Current Technical Reality

Stack actuelle :

``` text
Python
OpenCV
InsightFace
ONNX Runtime
NumPy
```

Donc :

> **ne pas prétendre que le projet utilise réellement MUI.**

MUI est ici une **référence de langage visuel et d'ergonomie**.

Si une interface web ou Qt est introduite plus tard, le Design System
reste la source de vérité et l'implémentation s'adapte.

------------------------------------------------------------------------

# 92. Design System Change Protocol

Toute évolution significative suit :

``` text
Observe
↓
Identify UX problem
↓
Check existing token/pattern
↓
Prototype smallest change
↓
Test on real live camera
↓
Measure performance impact
↓
Keep / revert
↓
Update DESIGN_SYSTEM.md if durable
```

Pas de changement silencieux.

------------------------------------------------------------------------

# 93. Droit de contredire ce document

Claude Code, Codex ou un développeur peut proposer de violer une règle
si une preuve réelle montre qu'elle nuit au produit.

Preuves acceptables :

``` text
usability test
FPS measurement
render limitation
contrast failure
accessibility issue
real screen-size constraint
implementation complexity disproportionate to value
```

Pas :

``` text
"it looks cooler"
"this is trendy"
"another AI suggested it"
```

------------------------------------------------------------------------

# 94. Final North Star

Sentinel Vision doit produire cette impression :

> **"Je comprends immédiatement ce que le système voit, ce qu'il sait,
> ce qu'il ne sait pas et si le système fonctionne --- sans que
> l'interface cherche à m'impressionner."**

Le niveau haut de gamme vient de la précision.

Le niveau professionnel vient de la retenue.

Le niveau moderne vient de la fluidité.

Le niveau de confiance vient de l'honnêteté de l'information.

Et la règle finale reste :

> **smoothness \> effects\
> hierarchy \> decoration\
> truth \> drama\
> readability \> density\
> measured reality \> design dogma**
