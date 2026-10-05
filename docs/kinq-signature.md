# KINQ SIGNATURE et pages Explorer / Découvrir

Routes : /comment-ca-marche, /kinqcard, /rencontrer-en-confiance, /profil-fetish, /univers-fetish, /kit-rencontre. Pages React avec le shell partagé, sans appels membres depuis le web.

## Version 3 — affinités et texte à copier-coller

- 36 univers, une seule affirmation personnelle par univers. Pas de distinction entre attirance personnelle et rencontre souhaitée.
- Huit affirmations sur domination, soumission, sadisme, masochisme, provocation, réponse à la provocation, découverte et concentration sur un kink. 44 questions facultatives, onze étapes.
- Labels, identifiants, rôles, aide et pictogrammes issus de content/profile-kinks.json. Le répertoire reprend les 90 univers du même catalogue.
- Échelle 0–4 : Pas du tout / Un peu / Assez / Beaucoup / À fond. Chaque réponse donne 0, 25, 50, 75 ou 100 % d’affinité déclarée. Les questions passées/inconnues restent nulles, distinctes de zéro.
- Expérience et rôles par pratique restent facultatifs, sans effet sur le score.
- Dom et Sub proviennent uniquement de leurs affirmations directes, jamais des kinks. Switch nécessite les deux scores renseignés et au moins 50 % pour chacun ; son score est leur minimum. Un score de douleur ne crée pas un score de domination ou soumission.
- Brat, Brat tamer, Sadique et Masochiste ont des affirmations séparées. Explorateur et Fetishiste ciblé décrivent les deux autres tendances.
- Le titre reprend les trois univers les plus forts à partir de 50 %, avec leurs noms concrets : « Bondage · Cordes · Cuir ». Aucun nom de profil composé ni catégorie générique comme « Sans hiérarchie · Contrainte ». Sans univers marqué, les tendances BDSM les plus fortes prennent le relais. Sans affinité forte, « Tes affinités restent à découvrir » invite à compléter le questionnaire.
- Les cinq univers les plus forts sont affichés en premier ; tous les autres scores restent accessibles dans une liste dépliable. Les tendances BDSM gardent leurs noms et leurs scores indépendants, sans priorité artificielle de rôle.
- Seuil positif : 50 %. Départage à score égal par identifiant. Les cinq scores les plus forts, univers et tendances confondus, sont cochés par défaut pour la copie. La sélection peut être changée.
- Tous les indices sont indépendants. Pas de score global de compatibilité ni de validation psychométrique.

Vocabulaire de référence : [BDSM Test — Info](https://bdsmtest.org/info?s=09) pour les termes communautaires Dom/Sub/Switch/Brat/Brat tamer, sans reprendre ses questions ou son calcul.

Le questionnaire est présenté comme un divertissement, sans remarques sur le consentement dans ses questions, son résultat ou son partage. L’accès reste réservé aux adultes.

## Style partagé

Les six pages utilisent les classes button, text-button, underlink et eyebrow, le surlignage de titre et le sprite SVG de shell.js. Le sélecteur des boutons NO TABOO dans styles.css est étendu à .kx : même remplissage de gauche à droite, dimensions, bordures, couleurs et adaptation à Réduire les animations. explore.css conserve les mises en page et les champs propres aux outils, sans deuxième système de boutons.

Tous les details/summary du site utilisent le SVG disclosure-plus.svg et le contrôleur commun app/disclosures.jsx, monté dans le layout racine. Ouverture et fermeture sur la hauteur réelle en 300 ms, clics rapides réversibles, restauration des styles après animation et fonctionnement natif sans mouvement avec Réduire les animations. Aucun déplacement des enfants gérés par React. Le centre d’aide conserve sa recherche et ses ancres ; son ancienne animation locale est retirée. Le sommaire mobile des articles utilise aussi details/summary et reste ouvert sur desktop.

## Confidentialité et partage

Réponses et notes exclusivement en mémoire React dans l’onglet : aucun envoi, cookie, stockage persistant, URL contenant une réponse ou profil inventé. Le rechargement efface les données. Mesure d’audience désactivée sur /profil-fetish et /kit-rencontre, même avec le consentement analytics du site.

Le partage est exclusivement du texte brut, avec une ligne par affinité sélectionnée, dans l’ordre décroissant des scores. Le titre reste « Ma KINQ Signature » : aucun nom décoché ne subsiste dans le texte. Ni expérience ni rôle détaillé ni réponse brute ne sont copiés. La dernière ligne est exactement « Powered by Kinq - Rencontres fetish - kinq-app.com ».

Le texte est sélectionné au focus et le bouton « Copier mes résultats » utilise le presse-papiers. Il reste désactivé sans affinité cochée. Un refus de presse-papiers affiche une invitation à copier manuellement le texte. Aucun export PNG, canvas de carte ou téléchargement de carte ne subsiste. Aucune publication ou sauvegarde automatique dans l’app.

Le kit conserve des notes privées, un partage sélectif et un effacement confirmé. Ses cases préparent une discussion, sans certifier un accord.

## Vérification

node --test tests/signature-model.test.mjs puis npm run build. Vérification navigateur des choix, résultat par affinités, partage sélectif en texte et du style partagé sur desktop/mobile. Les scénarios du questionnaire restent locaux et ne touchent aucun compte membre.
