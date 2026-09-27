# Events — collecte et publication

Périmètre initial : événements fetish publics en France, et grands rendez-vous européens pertinents pour Kinq. Les petites soirées passent par une validation rapide avant publication.

## Ce que fait la maquette

- `content/events.json` contient uniquement les événements approuvés et sourcés.
- `python3 scripts/build-events.py` met à jour les cartes HTML de `events.html`.
- `events.js` masque les dates dépassées et filtre France / Europe dans le navigateur.
- `python3 scripts/check-event-sources.py --baseline` initialise le suivi des titres et balises de date de quelques pages d’organisateurs. Les exécutions suivantes ajoutent un signal à `content/event-review.json` si ces éléments changent. Elles ne publient rien.

Le suivi n’est pas planifié sur un serveur. Sans tâche récurrente et sans déploiement, la découverte ne tourne pas seule. Un changement de page peut aussi être sans lien avec un événement, et une petite soirée qui n’a pas de page publique ne sera pas découverte.

## Pipeline cible

1. Catalogue d’organisateurs et de sources officielles : flux iCal/RSS ou API quand disponibles, sinon suivi de pages publiques autorisées. Ajouter les organisateurs locaux ville par ville.
2. Formulaire « proposer un event » pour les organisateurs et la communauté. Enregistrer en file d’attente, avec lien source obligatoire et contact de l’organisateur.
3. Normalisation : nom, dates et fuseau, ville, type, public et conditions d’accès, URL officielle, date de dernière vérification. Détecter les doublons par URL et par nom + ville + date.
4. Validation rapide des événements locaux ; contrôle périodique des changements et annulations. Publication automatique possible uniquement pour des sources partenaires fiables et structurées.
5. Génération des pages d’événement et de l’agenda depuis les données approuvées. Sur un vrai hébergement, prévoir une tâche quotidienne, un stockage persistant, des notifications de revue et un déploiement.

Une page propre par événement pourra recevoir les données structurées `Event` et entrer dans un sitemap. Les données structurées et l’indexation Google concernent la visibilité dans la recherche ; elles ne découvrent pas de nouveaux événements pour l’agenda. Ne pas créer de fiche `Event` pour une soirée privée, accessible uniquement sur invitation, ou sans date et lieu confirmés.

Ne pas reprendre les affiches, photos ou descriptions complètes sans accord. Les fiches Kinq doivent être courtes et renvoyer vers l’organisateur pour les modalités et les billets.

## Photo du hero

Photo d'ambiance réelle prise pendant Beyond Darklands et publiée par [l'organisateur](https://darklands.be/party/fusion/) (`BD26_Studioworks_Friday_677.jpg`). La page Kinq cite sa source et l'utilise uniquement pour la maquette locale. Aucune licence de réutilisation promotionnelle n'a été trouvée : obtenir l'accord du détenteur des droits ou remplacer cette photo avant une mise en ligne publique. Les personnes photographiées ne sont pas présentées comme membres Kinq ni comme participants à un prochain événement.

Le formulaire « proposer un event » de la maquette conserve les propositions dans la session du navigateur. Il compare nom, ville et date aux fiches déjà publiées et aux propositions de cette session. Il n’envoie encore aucune donnée et n’effectue aucune modération réelle.
