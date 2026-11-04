# CIEL Log Insight

[**Voir le rapport de démonstration · données fictives**](https://itztov4r.github.io/ciel-log-insight/)

**Transformer un fichier de logs HTTP en rapport HTML autonome et lisible.**

Python 3.10+, bibliothèque standard uniquement. Projet pédagogique préparé avec assistance IA pour le portfolio de Mehdi Hmaiss.

## Essayer

```bash
python analyze.py examples/access.log --output report.html --json report.json
python -m unittest discover -s tests -v
```

Ouvrir `report.html`. Le dossier `examples/` contient un journal fictif et les rapports reproductibles : **6 requêtes reconnues, 2 erreurs HTTP et 1 ligne ignorée**. `index.html` présente ce rapport fictif comme démonstration statique ; le traitement Python s’exécute localement.

## Fonctions

| Fonction | Comportement |
| --- | --- |
| Formats | Apache Common ou Combined standard, IP numérique IPv4/IPv6 |
| Réponses HTTP | Comptage par code, erreurs 4xx/5xx et pourcentage |
| Activité | Regroupement horaire après conversion en UTC |
| Chemins | Top 10 ; paramètres de requête et fragments retirés |
| Sources | Top 10 des réseaux /24 IPv4 et /48 IPv6, sans afficher les IP exactes |
| Qualité | Lignes non reconnues comptabilisées ; 10 motifs d’erreur au maximum |
| Export | HTML autonome et JSON optionnel |

Les valeurs sont échappées avant affichage HTML. Le fichier d’entrée ne peut pas être écrasé par une sortie. Aucune donnée n’est envoyée à un service distant par cet outil.

```bash
python analyze.py examples/access.log --fail-on-errors
```

Codes de sortie : 0 pour traitement terminé ; avec `--fail-on-errors`, 1 si erreurs HTTP **ou** lignes ignorées ; 2 pour une erreur de fichier ou d’arguments.

## Tests et structure

- `analyze.py` : parsing, agrégation, CLI et rendu.
- `report_theme.py` : composants HTML, tableaux, barres et CSS responsive embarqué.
- `tests/test_analyze.py` : 7 tests couvrant formats, erreurs, UTC, IPv6, paramètres d’URL, échappement HTML et lignes invalides.
- `.github/workflows/tests.yml` : CI Python.

## Limites

Pas de détection d’attaque ni de diagnostic automatique. Les formats personnalisés, les champs contenant des guillemets échappés et les lignes de requête `"-"` ne sont pas pris en charge et sont comptabilisés comme ignorés. Les chemins peuvent encore contenir des informations sensibles ; l’agrégation ne constitue pas une anonymisation garantie. Seules des données fictives sont publiées ici. La mémoire dépend du nombre de chemins, heures et réseaux distincts ; outil prévu pour des fichiers de démonstration ou de taille modérée.

Pour l’entretien : expliquer la regex, les compteurs, la conversion UTC, les erreurs HTTP et la différence entre statistiques et preuve d’un incident.

Licence MIT — voir [LICENSE](LICENSE).
