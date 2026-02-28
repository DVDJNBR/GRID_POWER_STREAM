---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
workflowStatus: paused-at-step-7 (steps 8-14 deferred — sufficient for prototype jury)
inputDocuments: ["prd.md", "epics.md", "6-1-dashboard-data-feature-discovery.md", "6-2-dashboard-ux-ui-design-proposals.md"]
---

# UX Design Specification GRID_POWER_STREAM

**Author:** David
**Date:** 2026-02-27

---

<!-- UX design content will be appended sequentially through collaborative workflow steps -->

## Executive Summary

### Project Vision

GRID_POWER_STREAM est un dashboard de monitoring énergétique qui transforme des flux de données complexes (RTE eCO2mix, ERA5, facteurs d'émission) en décisions opérationnelles lisibles en 5 secondes. L'ambition : casser le moule des dashboards utilitaires austères pour offrir une expérience "consumer-grade" sur de la donnée industrielle.

### Target Users

**Marc (Gestionnaire parc éolien)** — Utilisateur opérationnel. 30 secondes entre deux réunions. Besoin immédiat : "ma région sous-performe ?" → action. Lit en mode scanning visuel, pas en mode analyse. Frustration actuelle : consulter 4-5 sites différents pour une décision.

**L'Auditeur Technique (Jury)** — Expert data engineering. Lit le dashboard comme un rapport technique. Cherche la rigueur : fraîcheur des données, traçabilité des sources, cohérence des chiffres. Besoin : confiance dans la donnée, pas juste des beaux graphiques.

**Tension fondamentale :** Ces deux lectures coexistent sur le même écran. La hiérarchie visuelle doit servir les deux sans switcher de mode.

### Key Design Challenges

1. **Deux lectures, un seul écran** — Marc veut l'action immédiate, le Jury veut la rigueur. La solution : une hiérarchie visuelle à 3 niveaux (macro → région → expert) qui satisfait les deux sans vue dédiée.

2. **L'honnêteté des données sparse** — 9 régions sur 12 sans données dans le sample actuel. L'état vide est un moment de design critique : mal géré, il détruit la confiance du jury en 3 secondes.

3. **Time-series lisible à 96 points** — 24h × 15 min × 8 sources empilées. La question n'est pas "quel type de chart" mais "quelle information doit sauter aux yeux en premier".

### Design Opportunities

1. **Impact des 5 premières secondes** — Carte de France colorée par % renouvelable visible dès l'ouverture → le jury comprend l'ambition avant même de lire un chiffre.

2. **Progressive disclosure** — Vue macro (carte + line chart) → vue région (KPIs + mix) → vue expert (facteur de charge, CO₂ détaillé). Chaque niveau satisfait un utilisateur différent.

3. **IA forecasting visible** — Line chart actuals + bande de prédiction (zone shaded) séparées par une barre verticale "maintenant". Langage forecasting standard reconnu immédiatement par le jury.

### Key Design Decisions (validated with David)

**Layout hero :**
```
┌─────────────────────────────────────────────────────────┐
│  ⚡ WATT WATCHER          [Région ▼]  [🔄 Rafraîchir]  │
│                                    Données au 14:45 UTC │
├───────────────────────┬─────────────────────────────────┤
│   CARTE FRANCE        │   LINE CHART                   │
│   choroplèthe         │   production réelle ───        │
│   (% renouvelable)    │   prédiction IA   ···· ░░░     │
│   [clic → drill-down] │   ──────────── NOW              │
├───────────────────────┴─────────────────────────────────┤
│  [KPI Total MW]  [Source dominante]  [CO₂ badge+spark] │
├─────────────────────────────────────────────────────────┤
│         MIX ÉNERGÉTIQUE (donut) + area chart 24h       │
└─────────────────────────────────────────────────────────┘
```

**Décisions validées :**
- Carte choroplèthe France + line chart côte à côte en hero → WHERE et WHEN d'un coup d'œil
- Line chart : actuals (ligne pleine) + prédiction IA (pointillé + bande de confiance shaded) + marqueur "NOW"
- Badge fraîcheur statique "Données au HH:MM" + bouton Rafraîchir manuel (pas de polling/WebSocket)
- CO₂ : badge coloré seuil (vert/orange/rouge) + mini sparkline 24h — pas de jauge demi-cercle isolée
- Facteur de charge : valeur vs référence visible ("50% vs objectif 65%") — pas de barre de progression nue

## Core User Experience

### Defining Experience

L'action fondamentale : ouvrir le dashboard et savoir en 3 secondes si la région monitorée est en équilibre production/consommation. Tout le reste est drill-down.

La question centrale de Marc n'est pas "combien produit-on ?" mais **"est-ce qu'on produit ce que le réseau consomme ?"** Le delta production/consommation est l'information opérationnelle clé — pas la valeur MW brute.

### Platform Strategy

Web desktop-first (1080p minimum). SSO Azure AD transparent — invisible si déjà authentifié. Pas de mobile-first pour le prototype jury.

### Effortless Interactions

- **Sélection région** → mise à jour instantanée de tout le dashboard
- **Lecture état actuel** → carte choroplèthe colorée par delta prod/conso, pas de recherche
- **Compréhension alerte** → code couleur immédiat, pas de calcul mental
- **Rafraîchissement** → 1 clic, 0 friction, badge timestamp statique mis à jour

### Critical Success Moments

- **Marc** : carte rouge sur sa région (sur-production) → décision curtailment préparée en 2 min avant que ça arrive
- **Jury** : line chart prod vs conso avec bande de prédiction IA sur les deux courbes → pipeline crédible et analytiquement rigoureux
- **Échec** : état vide silencieux, données datées sans indication, graphique sans référence consommation

### Experience Principles

1. **L'information cherche l'utilisateur** — l'anomalie est visible sans action (carte colorée dès l'ouverture)
2. **Jamais un chiffre seul** — toujours avec sa référence (prod vs conso, CO₂ vs moyenne nationale)
3. **Honnêteté radicale** — état vide explicite > blanc silencieux ; données manquantes = ⬜ gris affiché
4. **Une action, un résultat, zéro délai perçu** — clic région → mise à jour complète

### Alert Logic (carte choroplèthe)

| État | Couleur | Déclencheur | Action Marc |
|------|---------|-------------|-------------|
| Équilibre | 🟢 Vert | Production ≈ Consommation | Monitoring normal |
| Sous-production | 🟡 Orange | Production < Consommation | Vérification technique/météo |
| Sur-production | 🔴 Rouge | Production > Consommation | Préparation curtailment, risque prix négatifs |
| Données manquantes | ⬜ Gris | Aucune donnée disponible | Honnêteté radicale |

### Chart Hero — Production vs Consommation

Le line chart principal montre **deux courbes** sur 24h :
- **Production** (ligne pleine) + bande de prédiction IA (pointillé + zone shaded)
- **Consommation** (ligne pleine, couleur différente) + bande de prédiction IA
- Zone entre les deux courbes shaded en rouge quand production > consommation
- Marqueur vertical "NOW" séparant réel et prédit

→ Marc voit le **moment d'action futur** : "dans 2h la prod va dépasser la conso"

### Dev Notes pour stories suivantes

- `consommation_mw` existe en Silver mais absent de l'endpoint API actuel → à ajouter avant implémentation du chart hero
- L'IA predictive (production + consommation) est un COULD/futur — le chart doit fonctionner sans les bandes de prédiction dans un premier temps

## Desired Emotional Response

### Primary Emotional Goals

**Marc (Gestionnaire parc éolien) :**
- **Contrôle** — "Je pilote, je ne subis pas." L'information est là avant que la crise arrive. La carte choroplèthe donne ce sentiment de maîtrise spatiale en un regard.
- **Confiance** — "Ces données sont fiables." Badge fraîcheur + source RTE visible = légitimité immédiate. Pas de doute sur la provenance.
- **Efficacité** — "J'ai ce qu'il me faut, maintenant." 3 secondes → décision. Aucun détour.

**L'Auditeur Technique (Jury) :**
- **Impression** — "Ce pipeline est sérieux." La bande de prédiction IA sur le line chart, le badge RTE, la traçabilité des sources → lecture immédiate de la rigueur technique.
- **Confiance dans le pipeline** — "Les données ne sont pas bidouillées." États vides affichés honnêtement, timestamps précis, filtrage des zéros expliqué → pas de magie noire.

### Emotional Journey Mapping

| Moment | Émotion visée | Déclencheur design |
|--------|--------------|-------------------|
| **Ouverture — "Wow"** | Surprise positive, ambition perçue | Carte France colorée visible avant tout scroll — le visuel parle avant le texte |
| **Usage — "Je comprends"** | Clarté, maîtrise cognitive | Hiérarchie visuelle 3 niveaux, aucun calcul mental requis |
| **Alerte — "Je vois, je sais"** | Urgence calme, pas de panique | Couleur rouge sur région + line chart anticipant → action préparée, non subie |
| **État vide — "C'est honnête"** | Confiance maintenue malgré l'absence de données | Région grise explicite + message "Données non disponibles" — jamais de blanc silencieux |
| **Retour — "Mon outil"** | Appartenance, habitude positive | Dernière région sélectionnée mémorisée, timestamp familier, layout stable |

### Micro-Emotions

Les émotions subtiles qui font la différence entre un outil qu'on tolère et un outil qu'on recommande :

| Émotion positive visée | Opposé à éviter | Comment y parvenir |
|------------------------|-----------------|-------------------|
| **Confiance** | Scepticisme | Badge "Source RTE + Licence Ouverte" visible en footer, timestamp précis |
| **Calme** | Anxiété | Palette sobre (pas de rouge clignotant), alertes contextualisées, pas de notifications intrusives |
| **Efficacité** | Frustration | Zéro clic superflu pour atteindre l'info clé, rafraîchissement en 1 clic |
| **Clarté** | Confusion | Chaque chiffre accompagné de sa référence (prod vs conso, CO₂ vs moyenne nationale) |
| **Légitimité** | Doute | Données manquantes affichées ⬜ gris — l'honnêteté inspire plus confiance que le silence |

### Design Implications

| Émotion | Choix UX concret |
|---------|-----------------|
| Contrôle (Marc) | Carte choroplèthe interactive dès le chargement — pas besoin de chercher l'info |
| Confiance (Marc + Jury) | Badge fraîcheur statique "Données au HH:MM UTC" + bouton Rafraîchir manuel visible |
| Impression (Jury) | Line chart prod/conso avec bande de prédiction IA — signal fort de pipeline ML |
| Calme opérationnel | Code couleur vert/orange/rouge → gradient sémantique, pas d'alarme visuelle agressive |
| Honnêteté radicale | Régions sans données = ⬜ gris explicitement labelisé, jamais de case vide muette |
| Efficacité maximale | KPI cards en dessous du hero — lecture en Z : carte → line chart → KPIs → drill-down |

### Emotional Design Principles

1. **Confiance avant beauté** — Un dashboard de données industrielles gagne la confiance par la rigueur, pas par le décor. Chaque choix visuel est justifié par une donnée, pas une esthétique.

2. **L'alerte calme** — Rouge ne signifie pas urgence absolue. Il signifie "prépare-toi". Le design évite le sentiment de crise non-contrôlée. Marc doit se sentir en avance sur l'événement.

3. **Le vide comme signal, pas comme échec** — Une région grise est une information valide. Elle dit "je suis honnête sur ce que je ne sais pas". Ça renforce la crédibilité de ce qui est affiché.

4. **Consumer-grade sur données industrielles** — L'ambition est là : rendre la donnée RTE aussi fluide à lire qu'un tableau de bord Tesla. Pas en sacrifiant la rigueur, mais en l'habillant.

## UX Pattern Analysis & Inspiration

### Inspiring Products Analysis

**Windy.com** — La référence absolue pour de la donnée géo "vivante". Carte animée en temps réel, palette de couleurs sémantiques, zéro UI inutile. Le wow vient du fait que la donnée elle-même EST le visuel — la carte n'illustre pas les données, elle les est. Pattern clé : **la geo-visualisation comme interface principale, pas comme widget secondaire.**

**Tesla Energy App** — Dashboard énergie consumer-grade. Dark mode premium, KPIs énormes avec mini-charts contextuels, flow diagram animé production → batterie → consommation. Le wow vient de l'animation : on ne lit pas un chiffre, on voit de l'énergie bouger. Pattern clé : **chiffres en grand, animation subtile, aucun label superflu.**

**Linear.app** — Pas de données énergie, mais l'aesthetic de référence du SaaS moderne. Ultra-rapide, transitions fluides, couleurs dark/accent très contrôlées. Le wow vient de la vitesse et de la fluidité — chaque interaction répond avant même d'être finalisée. Pattern clé : **la sensation de rapidité EST un choix de design, pas un bénéfice technique passif.**

**Our World in Data** — L'anti-thèse du "beau mais vide". Chaque graphique raconte quelque chose, les titres sont des conclusions pas des labels, le contexte est toujours présent. Pattern clé : **jamais un chiffre seul — le titre du graphique EST la décision.**

### Transferable UX Patterns

**Navigation & Hiérarchie :**
- `Windy` → Carte en full-hero, contrôles flottants en overlay discret — adapter : carte France en hero 50% width, aucune sidebar permanente
- `Linear` → Navigation sans friction, état mémorisé — adapter : dernière région sélectionnée persistée en localStorage

**Interactions & Animations :**
- `Tesla Energy` → Chiffres KPI avec micro-animation au chargement (count-up) — adapter : production MW qui "s'incrémente" à l'arrivée des données
- `Windy` → Couleurs de la carte qui transitionnent doucement lors du changement de région — adapter : choroplèthe avec transition CSS sur les fill colors
- `Linear` → Feedback immédiat sur chaque action — adapter : spinner inline sur le bouton Rafraîchir, pas de page reload

**Visual Design :**
- `Tesla Energy` → Dark mode avec accent color électrique (bleu-cyan ou vert néon), glassmorphism sur les cards — déjà en place dans l'existant story 5-1, à renforcer
- `Our World in Data` → Titres de charts = conclusions, pas labels — adapter : "Production dépasse la consommation depuis 14h45" plutôt que "Production vs Consommation"

### Anti-Patterns to Avoid

- **Le dashboard Bloomberg** — dense, trop d'info simultanée, lisible seulement après formation. Contraire de l'accès 30 secondes de Marc.
- **Les jauges isolées** (demi-cercles) — belles en screenshot, illisibles en usage : l'aiguille ne donne pas de contexte. Déjà rejeté pour CO₂.
- **Le polling visible** — compteur "rafraîchissement dans 47s" qui crée de l'anxiété. Choix validé : bouton manuel, badge timestamp statique.
- **Le blanc silencieux** — données manquantes = case vide. Aucun signal de confiance. Règle d'or : gris + label explicite.
- **L'animation pour l'animation** — rotations 3D de donuts, parallax inutile. Le wow doit servir la compréhension, pas masquer l'absence d'information.

### Design Inspiration Strategy

**Adopter :**
- Carte geo en hero position (Windy) — la carte n'est pas un élément parmi d'autres, c'est l'entrée principale
- Dark mode premium avec accent color contrasté (Tesla) — une couleur accent, utilisée avec parcimonie = impact maximal
- Titres de charts = insights (Our World in Data) — chaque graphique "parle" avant d'être lu

**Adapter :**
- Animation Tesla → version légère : transition de couleur sur choroplèthe + count-up KPIs, pas de flow animé (trop coûteux pour prototype)
- Rapidité Linear → sensation de vitesse via transitions CSS 200ms et skeleton loaders, pas de vraie optimisation réseau nécessaire au stade prototype

**Éviter :**
- Toute densité Bloomberg — une seule information dominante par zone visuelle
- Jauges isolées — le CO₂ badge + sparkline est la bonne direction
- Animations de chargement longues — skeleton placeholder > spinner rotatif

## Design System Foundation

### Design System Choice

**shadcn/ui** (Radix UI primitives + Tailwind CSS) comme fondation principale.
Backup : système CSS custom properties existant (story 5-1) si la courbe d'apprentissage Tailwind ralentit le prototype.

### Rationale for Selection

- **Esthétique wow effect** : shadcn/ui est devenu la référence du SaaS moderne premium (Linear, Vercel, Resend — exactement l'esthétique visée). Le dark mode est natif et soigné.
- **Zéro dépendance externe de design** : les composants shadcn/ui sont copiés dans le projet — pas de version à maintenir, pas de licence, code entièrement contrôlable.
- **Composants de base prêts à l'emploi** : Card, Badge, Button, Dropdown, Skeleton loader — le temps de développement est concentré sur les charts et la logique, pas sur les boutons.
- **Compatible React 18 + Vite** : aucun changement d'outillage nécessaire.
- **Backup réaliste** : les CSS custom properties + glassmorphism existants peuvent coexister ou remplacer Tailwind si besoin — les deux systèmes ne sont pas incompatibles.

### Implementation Approach

1. **Initialiser shadcn/ui** dans le projet React/Vite existant (`npx shadcn-ui@latest init`)
2. **Porter les design tokens existants** (couleurs dark/light, glassmorphism) en variables Tailwind config
3. **Installer les composants au besoin** — uniquement ce qui est utilisé (pas de bundle inutile)
4. **Charts : Recharts reste en place** — shadcn/ui ne couvre pas les dataviz, Recharts ou Nivo s'intègrent parfaitement à côté
5. **Choroplèthe : react-leaflet ou D3** — à confirmer en story 6-3 benchmark

### Customization Strategy

| Token | Valeur actuelle (CSS vars) | Tailwind config |
|-------|---------------------------|-----------------|
| Accent color | `--color-accent` | `colors.accent` |
| Alerte rouge | à définir | `colors.alert.red` |
| Alerte orange | à définir | `colors.alert.orange` |
| Alerte vert | à définir | `colors.alert.green` |
| Background dark | `--bg-primary` | `colors.background` |
| Glassmorphism | `backdrop-filter: blur` | `@layer utilities` custom |

**Règle de fallback** : si un composant Tailwind résiste, implémenter en CSS custom properties — la convention CSS vars reste la source de vérité des couleurs, Tailwind la consomme.

## Core Interaction Design

### Defining Experience

> **"Ouvrir la carte → voir la couleur de ta région → cliquer → comprendre pourquoi → décider."**

Si Tinder c'est "swipe to match" et Spotify c'est "play any song instantly", GRID_POWER_STREAM c'est :

**"Voir l'état du réseau en un regard, comprendre le pourquoi en un clic."**

L'interaction qui, si on la réussit, rend tout le reste secondaire : **la carte choroplèthe qui parle avant qu'on lise un chiffre.** La couleur d'une région EST la décision opérationnelle. Tout ce qui suit est du drill-down.

### User Mental Model

Marc arrive avec un modèle mental de **tableau de bord de surveillance** — comme un pilote qui regarde ses instruments. Il ne veut pas analyser, il veut confirmer ou être alerté. Ce qu'il fait actuellement : ouvre 4-5 onglets (RTE, météo, rapport interne), agrège mentalement. Frustration : le temps de compilation = le temps perdu.

Le Jury arrive avec un modèle mental de **rapport technique interactif** — comme un data analyst qui lit un notebook. Il veut des preuves, de la traçabilité, de la cohérence.

**Résolution :** la même carte sert les deux — Marc y lit une décision, le Jury y lit la couverture des données.

### Success Criteria

| Critère | Indicateur concret |
|---------|-------------------|
| Clarté immédiate | Marc identifie l'état de sa région sans lire un chiffre — couleur suffit |
| Confiance (Jury) | Source et timestamp visibles sans chercher |
| Drill-down fluide | Clic région → mise à jour <500ms perçue, pas de reload de page |
| Alerte anticipée | Line chart montre l'évolution future, pas juste l'état présent |
| Honnêteté | Région sans données = ⬜ gris avec label, jamais de blanc silencieux |

### Novel vs. Established Patterns

**Patterns établis (zéro apprentissage) :**
- Choroplèthe colorée = cartographie thématique classique
- Line chart time-series + marqueur NOW = standard dataviz
- Badge coloré seuil = traffic light system universel

**Innovation dans les patterns établis :**
- Zone shaded entre prod et conso sur le line chart (rouge quand sur-production) — lecture du delta sans calcul mental
- Titre de chart = insight ("Production > Consommation depuis 14h45") plutôt que label neutre

**Pas de pattern inconnu à enseigner** — le wow vient de la qualité d'exécution, pas de la nouveauté de l'interaction.

### Experience Mechanics

```
1. INITIATION
   → Ouverture dashboard : carte France visible immédiatement
   → Couleur choroplèthe chargée dès que les données arrivent
   → Pas d'action requise pour voir l'état global

2. INTERACTION
   → [Optionnel] Clic sur une région → drill-down automatique
   → [Optionnel] Dropdown région → même effet
   → [Optionnel] Bouton Rafraîchir → spinner inline, badge timestamp mis à jour

3. FEEDBACK
   → Couleur région = réponse à "comment va ma région ?"
   → Line chart = réponse à "pourquoi ?" et "dans 2h ?"
   → KPI cards = réponse à "combien exactement ?"

4. COMPLETION
   → Marc : décision prise (curtailment / monitoring normal / alerte météo)
   → Jury : pipeline validé (source RTE visible, timestamp frais, données cohérentes)
   → Retour : région mémorisée, prochain chargement sur le même contexte
```
