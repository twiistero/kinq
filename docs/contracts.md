# Les contrats Kinq — première version

## Contenu et parcours

`content/contracts.json` est la source des dix modèles et de leurs guides : BDSM,
domination/soumission, chasteté, séance, bondage, discipline, pup play, service,
collier et exclusivité. Chaque modèle comporte quatre clauses
spécifiques, neuf clauses communes et un texte de clôture. Les champs sont
facultatifs pour un modèle imprimé, mais les deux noms/pseudos et deux adresses
distinctes sont requis pour une version numérique.

Le navigateur personnalise les modèles en mémoire et produit le PDF vierge ou
personnalisé avec les polices et le logo Kinq. Aucune note n'est sauvegardée
localement. `/kit-rencontre` redirige définitivement vers `/contrats`.

## Signature privée

- Création d'une version immutable et de deux invitations aléatoires.
- Invitation placée dans le fragment du lien, sans contenu du contrat dans l'URL.
- Code e-mail à usage unique : dix minutes, cinq essais, une minute entre envois,
  cinq demandes par destinataire et par heure, y compris entre contrats.
- Vérification des deux adresses séparément, accès de deux heures.
- Signature par saisie du nom/pseudo attendu et validation de la version exacte.
- Dates enregistrées côté serveur ; affichage Europe/Paris dans le PDF.
- PDF définitif créé après les deux signatures, enregistré une fois et envoyé
  séparément aux deux destinataires. Aucun e-mail dans le PDF.
- Réessais des copies en attente, au maximum six tentatives ; déduplication par
  clé d'idempotence Resend. Une erreur d'envoi ne supprime aucune signature.

Les liens expirent après quatorze jours sans les deux signatures, ou trente jours
après la signature complète. Le retrait révoque les invitations et accès et
efface le contenu, les adresses et le PDF côté serveur. Il ne rappelle pas les
copies déjà téléchargées ou reçues par e-mail.

## Stockage et exploitation

Tables ordinaires distinctes, créées par `app.init_db` : `private_contracts`,
`private_contract_signers`, `private_contract_code_dispatches`. Le contenu,
les e-mails, signatures et PDF sont chiffrés au repos avec une clé dérivée de
`KINQ_SESSION_SECRET`. Une rotation de ce secret sans migration rendrait ces
documents illisibles : conserver le secret pendant leur durée de rétention.
Les empreintes des invitations et codes utilisent un HMAC, pas les valeurs brutes.

Le service reprend `KINQ_PUBLIC_ORIGIN`, `KINQ_SESSION_SECRET`, le PostgreSQL et
`KINQ_RESEND_API_KEY` existants. Aucun abonnement à un prestataire de signature.
Le coût et les quotas restent ceux de l'hébergement, du stockage et des e-mails.
Le Dockerfile API embarque les polices et le logo transparent ; le symbole vert
repose sur un carré gris Kinq pour rester lisible à petite taille. ReportLab
produit le PDF signé.

Les routes privées sont sans cache et sans indexation ; le parcours ne charge
pas la mesure d'audience. Les journaux de traitement ne contiennent ni document,
ni token, ni destinataire. L'accord est personnel et révocable ; la vérification
d'une boîte e-mail ne certifie pas une identité civile.

## Validation et activation

Tests isolés :

```sh
python -m unittest tests.test_contracts tests.test_member_auth_email
npm run build
```

Ils remplacent uniquement le transport e-mail dans la cible de tests. Aucun
destinataire, contrat, profil ou code de test n'est embarqué dans le parcours.

L'aperçu local utilise l'API publiée actuelle, qui ne contient pas encore ces
routes. La personnalisation et les PDF y fonctionnent. Après déploiement du web
et de l'API, vérifier un contrat à deux avec deux adresses expressément fournies
par le propriétaire : réception des codes, liens et QR, signatures, PDF identique
reçu dans les deux boîtes, et retrait. L'acceptation Resend ne prouve pas à elle
seule une réception en boîte.

Chaque modèle a une page `/contrats/{modele}` et une FAQ. Les en-têtes web et PDF
placent le titre à gauche et « Powered by » avec le logo officiel transparent,
« Make it kinky. » et le domaine alignés sous le début du mot-symbole, dans un
bloc compact à droite. Le SVG utilise les contours DM Sans 800
et le symbole partagé ; sa version PNG transparente sert au PDF serveur.

Le catalogue utilise dix pictogrammes distincts, sans numéros de catégories.
Chaque champ conserve une consigne et une aide « Exemple et conseils » repliée
par défaut ; elle permet de reprendre la formulation proposée en un clic.

## Mes contrats — compte web et iOS

Les copies personnelles sont enregistrées chiffrées dans `member_contract_copies`.
Une version à imprimer est conservée sur demande, avec un PDF généré par le serveur.
Les signatures terminées conservent exactement le PDF signé canonique, sans en
régénérer la date. Les comptes existants des deux signataires reçoivent leur copie ;
un nouveau compte peut retrouver l'accord via son adresse vérifiée ou revendiquer
sa copie avec son accès de signataire vérifié.

Les copies du compte restent accessibles après l'expiration du lien privé, jusqu'à
leur retrait ou la suppression du compte. Retirer sa copie de Mes contrats ne
retire pas la copie de l'autre personne. Retirer l'accord depuis sa page de signature
efface aussi ses copies conservées côté serveur ; les PDF déjà exportés restent
chez leurs destinataires.

Après un PDF ou une impression, l'encart propose la connexion/inscription et conserve
le document chiffré pendant 24 heures dans `contract_account_drafts`. Le navigateur
ne conserve qu'un jeton opaque de retour, à usage unique. Aucun texte de contrat
n'est placé dans l'URL ou dans le stockage du navigateur. Le retour de connexion
est limité à `/compte`, `/mes-contrats` et aux chemins éditoriaux déjà autorisés.

Les routes `/api/member/contracts` réutilisent la session membre et la protection
CSRF ordinaires. Lecture, PDF et retrait vérifient systématiquement le propriétaire.
La rubrique native iOS utilise les mêmes routes, les mêmes documents et les dates
serveur, sans modèles de données de démonstration ni copie locale en repli.
