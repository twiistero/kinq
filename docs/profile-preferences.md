# Création du profil : univers et nuances

Mise à jour du 30 septembre 2026, limitée à l’éditeur `/mon-profil` et à son enregistrement. Le rendu des profils consultés et le matching ne consomment pas encore les nuances.

## Parcours

- Six portes d’entrée ; catalogue complet replié et recherche français/anglais, insensible aux accents. Les synonymes et variantes sont recherchables.
- Une carte repliée par univers sélectionné : uniquement « Ta façon de le vivre », avec une coche distincte « Je répondrai plus tard ». Aucun rôle attribué automatiquement.
- Les mélanges, variantes et suggestions liées ne sont plus proposés dans l’éditeur. Les anciennes données restent compatibles ; retirer un univers retire aussi ses anciens mélanges.
- Catalogue extensible. Les champs d’intérêt, d’expérience par univers et de texte libre ont été retirés de l’interface à la demande du 30 septembre ; le format de sauvegarde reste rétrocompatible.

## Vocabulaire et sources consultées

Les formulations françaises sont des choix éditoriaux KINQ, pas des traductions officielles ni une nomenclature universelle. Les textes restent descriptifs, sans instructions de pratique.

- [NCSF, Statement on Consent et glossaire en annexe](https://ncsfreedom.org/wp-content/uploads/2019/12/Consent-Counts-Statement.pdf) : vocabulaire de rôles et consentement révocable. Ne pas déduire un accord d’une préférence affichée.
- [Anatomie Studio, Talking Shibari](https://www.anatomiestudio.com/blog/talking-shibari-a-guide-to-rope-related-vocabulary) et [Shibari Study, FAQ](https://shibaristudy.com/faq) : rigger, rope bottom ; conserver les termes avec une formulation française claire.
- [Recon, Love Your Rubber](https://www.recon.com/en/blog/article/love-your-rubber-getting-the-best-out-of-your-rubber-gear/366) : usage communautaire de rubber et latex.
- [Recon, Get a taste: Underwear](https://www.recon.com/en/blog/article/get-a-taste-underwear/2588) : sous-familles vestimentaires, dont jockstraps, briefs et long johns.
- [Recon, PupBentley Responds](https://www.recon.com/en/Blog/Article/member-opinion-pupbentley-responds-to-pup-article/2583) : pup, handler et trainer ; témoignage communautaire, pas une définition imposée à tous.

Ne pas confondre rôle par pratique, dynamique dom/sub/switch et position sexuelle. Ni les matières ni les attirances corporelles ne reçoivent automatiquement le vocabulaire donner/recevoir. Les recherches utilisent aussi les anciens noms pour préserver la compatibilité.

## Données et maintenance

`content/profile-kinks.json` est la source des identifiants stables, des anciens noms, des libellés, rôles, variantes et liens transversaux. `scripts/build-page-documents.mjs` synchronise ce catalogue dans la source HTML via `sync-profile-catalogue.mjs`, puis génère les documents React. Ne pas renommer les identifiants déjà stockés sans migration.

Le payload conserve `style` et `practice` pour les consommateurs existants et ajoute `kinkPreferences` :

```json
{"version":1,"items":[{"id":"leather","interest":"favorite","role":"admire","experience":"some","variants":["blousons"]}],"combinations":[],"custom":""}
```

Le modèle FastAPI valide les rôles et variantes selon le catalogue, les liens aux univers sélectionnés, les doublons, les mélanges et les bornes. `model_dump()` stocke un objet JSON dans la colonne de profil existante ; aucune nouvelle table. Le catalogue est déjà inclus par le COPY content du Dockerfile API.

Les réponses explicites de l’ancien formulaire sont reprises : rôle bondage/pup lorsque la correspondance est certaine, anciens champs déjà sauvegardés conservés dans le format de données. La dynamique générale n’est jamais utilisée pour inventer un rôle particulier. Les requêtes de sauvegarde sont sérialisées et le succès n’est affiché qu’après réponse de l’API. La recherche ne déclenche pas d’enregistrement.

## Vérification locale

- `node --check profile-preferences.js`, `node --check mon-profil.js`, `node --check member-profile.js`.
- `.venv/bin/python -m unittest discover -s tests -p 'test_profile_preferences.py'` : ancien format, round-trip, tous les rôles du catalogue, profil complet, rejets des rôles/variantes/mélanges invalides et limites.
- `npm run build`.
- Contrôle navigateur avec compte synthétique et API de test locale validant via le même modèle : choix, variantes, mélange, recherche, rechargement, retrait et largeur mobile. Cette fixture ne prouve pas une connexion réelle ni la persistance PostgreSQL en production.

Pour publier ultérieurement, livrer ensemble catalogue, API, assets et documents régénérés ; l’initialisation existante recharge les documents en base lorsque leur empreinte change.

## Ajustement des catégories

Pieds et tous les anciens choix Corps à corps sont dans Corps. Medical play est dans Univers & imaginaires. Ass play regroupe Sodomie, Toys / plugs, Fisting et Enema play. Les catégories Autres attirances, Pratiques corporelles et Corps à corps sont retirées. Les identifiants des univers existants sont conservés. Les sélecteurs sont rectangulaires à coins arrondis, avec des chevrons SVG espacés des bords.

La dernière simplification conserve uniquement le surtitre « TU PEUX PRÉCISER ? ». Ordre du catalogue : styles, univers, bondage, sensations, contrôle, ass play, impact, corps, dynamique mentale, fluides, pratiques avancées et sensibles. Les listes natives sont en pleine largeur, avec un chevron SVG animé à l’ouverture ; l’animation respecte la préférence de mouvement réduit.

La barre suit le défilement dans l’éditeur de profil, indépendamment des champs remplis. Sept messages évoluent avec le remplissage, par un fondu vertical court désactivé en mouvement réduit. Le sous-titre de la barre est retiré.
