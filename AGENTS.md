<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

## Compte de test unique et données réelles

Instruction du propriétaire du 30 septembre 2026 : les vérifications web et iOS utilisent toujours le même compte membre enregistré dans PostgreSQL, via les API normales. Aucun écran de démonstration autonome, profil local inventé, jeu de profils embarqué, sauvegarde simulée, connexion automatique de test ou repli sur des fixtures en cas d’erreur réseau.

- Environnement : **production**, `https://kinq-app.com`.
- Adresse de connexion : **test@kinq-app.com** (choisie par le propriétaire).
- Pseudo : **Test KINQ** ; identifiant membre : **3** (`member-3`).
- Code public du profil : **KQ-5483BE34**. Ce code n’est pas un mot de passe.
- Compte créé et relu dans PostgreSQL le 30 septembre 2026 ; tables ordinaires `members` et `member_profiles` ; statut `active`, aucun accès administrateur.
- Identifiant : **test@kinq-app.com**. Code de connexion fixe : **123456**, expressément demandé par le propriétaire. Cette adresse ne correspond pas à une boîte e-mail ; ne pas y envoyer de code et ne pas demander au propriétaire de relever ses e-mails pour ce compte.
- Connexion : ouvrir « J’ai déjà un compte » sur iOS ou `/connexion` sur le web, saisir cette adresse, continuer puis saisir **123456**. Refaire ces étapes à chaque nouvelle session.
- API identique aux autres membres : `POST /api/member/auth/request` avec `purpose=login`, puis `POST /api/member/auth/verify`. La demande crée le challenge normal de 10 minutes, limité à 5 tentatives ; la vérification le consomme et crée la session/CSRF ordinaires. Une nouvelle demande permet de réutiliser le code fixe.
- Le digest du code est provisionné uniquement pour ce membre dans `member_login_codes`. Aucun code fixe global, route dédiée, session fabriquée ou raccourci dans les clients. Tous les autres comptes conservent le code aléatoire par e-mail.
- Ne pas inscrire de code éphémère, cookie, secret PostgreSQL, Resend, OAuth ou clé de service dans ce fichier, dans le code, les captures ou les journaux.
- Réutiliser ce membre ; ne pas le supprimer ni le suspendre lors des tests. Les tests destructifs nécessitent un périmètre distinct explicitement demandé. Ne pas envoyer de Hooks/messages aux vrais membres pour les besoins d’une démonstration.
- Le profil est clairement identifié comme compte de test, sans portrait de tiers. Ville et limites masquées, mode discret actif. Les modifications passent par `PUT /api/member/profile` ; vérifier ensuite leur relecture par l’API et leur persistance.
- Les catalogues d’univers/pictogrammes/options restent des ressources de configuration partagées, pas des profils. Les doubles de test unitaires restent confinés aux cibles de tests, jamais utilisés pour les écrans ou la validation d’un parcours réel.
- `backend/scripts/ensure_test_member.py` est un outil d’administration idempotent exécuté dans le conteneur API : il crée ce membre/profil et son digest de connexion si absents, préserve les données existantes et utilise ensuite exclusivement les routes normales.
