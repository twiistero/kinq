# Kinq — home, direction 01

Prototype HTML/CSS/JS responsive, sans dépendance de build.

## NO TABOO — journal

Le journal a sa propre page d’accueil (`guides.html`) et six articles avec URL dédiée. Les cartes de la home ouvrent directement ces articles. L’accueil organise la lecture par curiosité, conversation et rencontre, avec des liens vers les univers, le lexique, les profils et les actions compte/application du prototype.

Le fil d’Ariane est construit une seule fois dans `shell.js`, au même endroit sous l’en-tête sur toutes les pages publiques, y compris l’accueil. Les articles donnent leur rubrique et leur titre via les attributs `data-breadcrumb-*` générés par `build-journal.py`.

Les deux premiers articles conservent leur texte intégral dans `content/no-taboo/`, mis en page par `scripts/render_first_article.py` et `scripts/render_second_article.py`. Leurs métadonnées et les autres articles se trouvent dans `scripts/build-journal.py` : lancer `python3 scripts/build-journal.py` après modification. Le champ optionnel `summary` alimente l’espace sous le titre de chaque carte ; `deck` reste le sous-titre de la page d’article. Ce script régénère l’accueil et les six pages, et maintient les liens des cartes de la home. `scripts/create-pages.py` ne régénère plus le journal.

Démarrage : `python3 -m http.server 4173 --bind 127.0.0.1`

- Home : http://127.0.0.1:4173/
- Sélecteur desktop/mobile : http://127.0.0.1:4173/preview.html
- Captures : previews/home-desktop.png et previews/home-mobile.png

Interactions : filtres d’univers, Hook et Épingles en mémoire de session, fiches de profils fictifs, copie du code, menu mobile, lectures éditoriales et modales de présentation. Aucun compte réel, envoi, géolocalisation ou backend. Liens de relation illustrés sur les profils ; invitations non implémentées. Les codes sont des exemples fixes.

Les photographies de test illustrent des personnages fictifs et ne représentent pas les préférences des personnes photographiées. Sources et contexte détaillés dans la section Direction 02. Polices Google Fonts et photos chargées à distance.

Vérifications : rendu à 1440 px, 390 px et absence de débordement à 360 px ; images chargées ; filtres, Hook, Épingler, fiche de profil, menu mobile et modale d’inscription. Pas de déploiement.

## Direction 02

Identité : monogramme K vectoriel dans `assets/kinq-icon.svg`, repris en favicon et dans le logo. Navigation et symboles SVG partagés dans `shell.js`. Grille d’icônes 24 px, trait 2 px : éclair Hook, punaise Épingles, maillons Relations, code carré Partage.

Pages : accueil, rencontres, kinks, profil détaillé, Events, lieux, guides, lexique et crédits photos. `scripts/create-pages.py` régénère certaines pages secondaires depuis la structure commune de la home ; Events est générée séparément par `scripts/build-events.py`. Le menu plein écran utilise un dialogue natif (focus contenu, fermeture Escape et restitution du focus).

Les Hooks et Épingles fictifs sont conservés dans sessionStorage pendant la session de l’onglet pour naviguer entre les pages. Recherche par pseudo, ville ou code, filtre par ville/kink et onglets de sélection fonctionnels. Les relations affichées sur les profils sont des exemples réciproques fixes, sans invitation serveur. La page Lieux présente des exemples fictifs. La page Events affiche des annonces réelles sourcées et renvoie vers les organisateurs ; voir `docs/events-workflow.md` pour la collecte et la validation.

Photographies de test remplacées par des sources fetish : Mike Ruiz / PhotoBook, Ben Orson Leather, MR. Riegillio, Invincible Rubber et SCALLYCHAV. Voir `docs/photo-sources.md` et `credits.html`. Ces photographies sont chargées à distance ; aucune licence de publication commerciale n’est acquise.

Vérification direction 02 : nouveau menu desktop/mobile, profils et recherche par code, filtres Épingles et état vide, navigation vers profil et lexique ; géométrie des pages à 360/390 px et contrôle desktop à 1440 px. Les pages restent des prototypes locaux.


## Direction 03

Style des cartes éditoriales explicitement validé et documenté dans `docs/identite-editoriale.md`. Nouveau symbole de deux liens horizontaux entrelacés en SVG, favicon carrée. Signature proposée : « Tes kinks. Tes codes. Tes rencontres. ». Terminologie Hook et Pin / Mes Pins.

La home affiche maintenant un diaporama Cuir / Puppy / Latex / Sport avec sélection directe et pause, ainsi qu’une tapisserie de photos décorative à cinq colonnes (trois visibles sur mobile), avec contenu fixe au premier plan. Animations suspendues hors écran, en onglet masqué et pour la préférence de réduction du mouvement. Les boutons changent uniquement de couleur au survol/clic.

Promesses de concept demandées : accès sécurisé, entièrement gratuit, profils privés ; le prototype reste sans authentification ni backend. Sources photo ajoutées : Army of Men pour Puppy et MR. Riegillio pour le duo Sport.


## Direction 04

Étoile commune au logo et aux séparateurs. Hero épuré : quatre puces, sans surtitre, cartouche ni pause. Bénéfices avec pictogrammes bouclier, étiquette et cadenas. Sur la tapisserie, l’action principale invite à créer un compte. Les fonctions Hook et Pin restent disponibles sur les pages de profils.

Boutons à remplissage progressif de gauche à droite ; liens simples et titres d’articles à soulignement animé, sans changement de couleur. Menu coulissant depuis la gauche avec fermeture inverse. Bouton « Télécharger l’app » dans l’en-tête : il ouvre une présentation indiquant que l’app est en préparation, sans faux lien de téléchargement.

Mise en page responsive revue : en-tête mobile, titres, texte de réassurance et mot-symbole final dans le flux, sans chevauchement du contenu. Cartes éditoriales conservées.

Vérification direction 04 : home rendue à 320, 390, 768 et 1440 px sans débordement horizontal ; espacements du bloc final et du texte de réassurance contrôlés. Remplissage des boutons, couleur et soulignement des liens, ouverture/fermeture du menu, navigation vers Sans tabou et modal de téléchargement vérifiés. Les quatre images du hero sont chargées. Syntaxe JavaScript validée.

## Direction 05

Home épurée et nouvelle présentation de Kinq sur ordinateur/iPhone, avec accès aux stores indiqués « bientôt ». Menu sans sous-titres, barre de valeurs animée lentement, contrastes des boutons sur fond acide corrigés. Soulignement mesuré sur les lignes de texte réelles pour exclure les icônes et animer chaque ligne successivement. Espacement des titres mobiles revu.

Contrôles : rendu et débordement à 320, 390, 768 et 1440 px ; menu compact ; remplissage noir avec bordure persistante ; titres d’articles sur plusieurs lignes et séquence de soulignement ; syntaxe JavaScript. Les appareils illustrent le futur produit et ne constituent pas des applications distribuées.

## Direction 06

NO TABOO, le journal Kinq, dispose de son encart propre sur la home ; les cartes d’articles sont conservées. Les engagements respect/sécurité/bienveillance sont répartis en trois blocs avec pictogrammes. L’étoile tourne au survol et périodiquement (2 s toutes les 16 s), avec respect du mouvement réduit. Les soulignements restent séquentiels et durent 210 ms. L’espacement du titre du journal est corrigé aussi sur desktop.

## Direction 07

Ruban de 11 cartes illustrées, pleine largeur et défilement vers la droite. Dessins SVG locaux pour dix univers et étoile pour « Et tout le reste ». Commandes de pause et déplacement, défilement tactile et préférence de mouvement réduit. Menu mobile corrigé, deux actions compte/application ; textes des engagements et bouton du journal ajustés.

## Direction 08

Univers en navigation manuelle : glisser de souris, molette, tactile et flèches. Aucun mouvement automatique ni commande de lecture. Icônes SVG minimalistes et extensibles, grille 64 × 64, trait uniforme, noir/gris/vert acide. NO TABOO passe à six articles et retire l’introduction. Les trois nouveaux sujets sont la vie privée, la première rencontre et l’aftercare. La bienveillance utilise un pictogramme de maillons.

Vérifications : déplacement par glisser et flèche, molette, absence d’ouverture de fiche après glissement, ruban immobile sans interaction ; six cartes éditoriales et ouverture d’un nouvel article. Syntaxe JavaScript validée.

## Atelier des pictogrammes

`atelier-pictos.html` propose une direction en silhouettes pleines : les 74 kinks de la maquette v11 et un harnais pour la home. Comparatif avant/après, recherche et familles, fonds gris/acide/noir, tailles de lecture, sélection locale et export SVG. Sources originales dans `scripts/build-pictos.py`, SVG dans `assets/pictos/`, règles dans `docs/pictogrammes.md`. La home conserve ses pictos actuels pendant cet atelier.

Atelier 02 : les 75 signes sont redessinés avec des contours ouverts et des objets plus reconnaissables. Leather utilise une casquette de cruising, Puppy un masque K9 de trois quarts, Harnais une construction bulldog et Shibari un losange hishi. Recherche de références documentée dans `docs/pictogrammes.md`, tracés dans `scripts/pictos_v2.py`. Comparaison avec la première proposition et pack SVG mis à jour.

Atelier 03 : les 75 pictos sont reconstruits en flat design sur une grille 128 px, avec trois encres, douze exemples visibles en tête de page et comparaison V2/V3 après le catalogue. Direction visuelle explorée avec Imagegen puis redessinée en SVG. Sources dans `scripts/pictos_v3.py`, règles et prompt de recherche dans `docs/`.

### Atelier pictos — collection 04

Refonte suivant la bande de pictogrammes fournie le 24 septembre : 75 symboles monochromes, grille 24 × 24, trait 1,5, sans textures ni reflets. L’atelier démarre à 48 px en vert acide sur noir ; les IDs et les sélections restent conservés. La collection 03 est archivée pour le comparateur. Sources dans `scripts/pictos_v4.py`, génération avec `python3 scripts/build-pictos.py`.

Vérification : 75 SVG et 75 symboles valides, export SVG avec encre figée, recherche, inspecteur, absence de débordement à 390 px. Captures dans `previews/atelier-pictos-v4-desktop.png` et `previews/atelier-pictos-v4-mobile.png`.

### Repasse ciblée 04.1

Neuf signes affinés sur retour utilisateur : wrestling, feet, shibari, restraints, doll, belly, harness, sounding et fisting. Suppression des personnages bâtons sur les deux pictos concernés, pied de profil, poing fermé, objets mieux définis. Les neuf sont présentés en tête de l’atelier ; les 66 autres dessins restent inchangés. Archive SVG régénérée et vérifiée. Planche de contrôle : `previews/pictos-refinement-nine.png`.
