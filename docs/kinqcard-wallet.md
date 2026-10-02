# KinqCard et Apple Wallet

La carte iOS est accessible depuis **Mon profil → Ma carte**. Elle utilise la projection authentifiée du profil et son lien court `https://kinq-app.com/p/CODE`. Aucun e-mail, kink, âge, position ni photo privée n’entre dans l’image partagée. Sans portrait public accessible, la silhouette remplace la photo. Le partage est une action explicite du propriétaire ; il ne supprime pas les protections des autres surfaces de profil.

L’image et le QR fonctionnent sans compte Apple configuré. L’intégration Wallet utilise `PKAddPassesViewController` avec le fichier signé de `GET /api/member/kinqcard/pass`. Le statut provient de `GET /api/member/kinqcard/wallet`, dans la session ordinaire du membre. Aucune carte non signée n’est présentée comme ajoutable.

## Activation côté serveur

Créer un **Pass Type ID** dans le compte développeur Apple, puis son certificat et sa clé privée. Installer le certificat intermédiaire Apple WWDR correspondant. Monter ces fichiers comme secrets en lecture seule dans le conteneur API Coolify ; la clé privée ne doit jamais être placée dans Git ni dans l’app.

Variables de configuration dans Coolify :

- `KINQ_WALLET_PASS_TYPE_ID` : identifiant effectivement enregistré chez Apple, commençant par `pass.`.
- `KINQ_WALLET_TEAM_ID` : équipe du certificat Pass Type ID.
- `KINQ_WALLET_CERT_PATH` : chemin du certificat PEM ou DER dans le conteneur.
- `KINQ_WALLET_KEY_PATH` : chemin de sa clé privée PEM.
- `KINQ_WALLET_WWDR_PATH` : chemin de l’intermédiaire Apple WWDR PEM ou DER.
- `KINQ_WALLET_KEY_PASSWORD` : secret facultatif si la clé PEM est chiffrée.

Le serveur vérifie les dates des certificats, l’équipe, l’identifiant, la correspondance clé/certificat et la signature par l’intermédiaire avant d’activer le bouton. Sans configuration valide, le statut est `available: false` et la route de téléchargement répond 503. Les deux routes nécessitent la session active et ne mettent rien en cache.

Le pass générique Wallet contient pseudo, code, QR, marque et portrait public approuvé si disponible. Son placement est celui d’Apple Wallet : la carte personnalisée au format bancaire reste la présentation dans l’app et l’image partagée. Le même numéro de série remplace un ancien pass lors d’un nouvel ajout ; aucune mise à jour automatique ni notification push Wallet n’est annoncée.

Après configuration, vérifier sur un iPhone réel : statut disponible, ajout dans Wallet, lecture du QR, remplacement après modification du profil. Les tests de signature isolés utilisent des certificats temporaires de test ; ils ne prouvent pas l’acceptation par Apple Wallet.

Références : [certificats Wallet](https://developer.apple.com/help/account/capabilities/create-wallet-identifiers-and-certificates), [format et signature d’un pass](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html).
