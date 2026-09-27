# Events — collecte et publication

Périmètre initial : événements fetish publics en France, et grands rendez-vous européens pertinents pour Kinq. Les petites soirées passent par une validation rapide avant publication.

## Collecte en ligne

- `content/events.json` contient uniquement les événements approuvés et sourcés.
- `python3 scripts/build-events.py` met à jour les cartes HTML de `events.html`.
- `events.js` masque les dates dépassées et filtre France / Europe dans le navigateur.
- `python3 scripts/collect-events.py --write` lit les flux publics structurés de Fetish Lyon et Maspalomas Fetish Pride, ainsi que les soirées datées du programme Darklands. Il conserve les annonces inédites ou modifiées dans `content/event-candidates.json`, avec leur fiche officielle. Les doublons sont comparés par origine, URL, puis nom + ville + date.
- `python3 scripts/check-event-sources.py` surveille les pages non structurées REDZONE et KinkX. Il ajoute un signal dans `content/event-review.json` lorsqu'une page change ; ce signal ne constitue pas une fiche d'événement.
- `.github/workflows/events-collect.yml` lance chaque jour les deux collectes et enregistre les annonces en attente dans le dépôt GitHub. La tâche peut aussi être lancée manuellement dans GitHub Actions. Elle ne modifie jamais `content/events.json` ni `events.html`.

Le workflow utilise l'autorisation `contents: write` du `GITHUB_TOKEN`. Un premier lancement manuel permet de vérifier l'accès des runners aux sites des organisateurs et l'écriture dans la branche principale. La collecte ne peut trouver qu'une annonce publique, datée et accessible depuis une source suivie ; les petites soirées sans page officielle doivent être proposées par leur organisateur.

### Validation

1. Examiner la date, la ville, les conditions d'accès et le lien officiel. Vérifier qu'il ne s'agit pas d'un événement privé ou annulé.
2. Lister les propositions : `python3 scripts/review-event.py list --source fetish-lyon` ou `python3 scripts/review-event.py list --all`.
3. Publier une fiche vérifiée : `python3 scripts/review-event.py approve IDENTIFIANT --summary "Résumé rédigé pour Kinq."`. Corriger au besoin `--kind` ou `--end`.
4. Écarter une fiche : `python3 scripts/review-event.py reject IDENTIFIANT --reason "Motif"`.
5. Le script d'approbation met à jour `content/events.json` et régénère `events.html`. Le déploiement du site suit ensuite le circuit habituel du dépôt/hébergeur.

Une annonce disparue de sa source passe au statut `source_missing` et ne peut pas être approuvée sans nouvelle vérification. Une fiche déjà publiée n'est jamais retirée automatiquement si sa source change : ce contrôle reste éditorial. Les sous-événements d'un festival peuvent être nombreux ; il faut sélectionner ceux qui apportent une information utile à l'agenda plutôt que tout publier.

## Pipeline cible

1. Ajouter les organisateurs locaux ville par ville dans `content/event-sources.json` lorsqu'ils publient un flux daté stable.
2. Créer une file de réception serveur pour le formulaire « proposer un event », avec contrôle anti-spam et anti-doublon. Le formulaire ouvre actuellement un e-mail prérempli à hello@kinq-app.com ; l’envoi dépend de l’application e-mail du visiteur et la modération se fait dans la boîte de réception.
3. Ajouter une revue périodique des annulations et des changements de lieu/conditions pour les fiches déjà publiées.
4. Une page propre par événement pourra être générée après validation, avec date de dernière vérification, données structurées `Event` et inclusion dans un sitemap. Ces données servent à la visibilité dans la recherche ; elles ne découvrent pas de nouveaux événements pour l'agenda.

Ne pas reprendre les affiches, photos ou descriptions complètes sans accord. Les fiches Kinq doivent être courtes et renvoyer vers l’organisateur pour les modalités et les billets.

## Photo du hero

Photo d'ambiance réelle prise pendant Beyond Darklands et publiée par [l'organisateur](https://darklands.be/party/fusion/) (`BD26_Studioworks_Friday_677.jpg`). La page Kinq cite sa source et l'utilise uniquement pour la maquette locale. Aucune licence de réutilisation promotionnelle n'a été trouvée : obtenir l'accord du détenteur des droits ou remplacer cette photo avant une mise en ligne publique. Les personnes photographiées ne sont pas présentées comme membres Kinq ni comme participants à un prochain événement.

Le formulaire « proposer un event » compare nom, ville et date aux fiches déjà publiées, puis ouvre un e-mail prérempli à hello@kinq-app.com. Le visiteur doit envoyer ce message depuis son application e-mail ; Kinq vérifie ensuite la proposition et les doublons reçus avant publication.
