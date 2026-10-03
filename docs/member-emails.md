# E-mails de compte KINQ

Le site et l’app iOS utilisent les mêmes routes FastAPI `/api/member/auth/request` et `/api/member/auth/verify`. L’inscription et la connexion envoient un code par Resend via `backend/app/mailer.py`, avec le modèle partagé `backend/app/templates/member-code.html`. Le changement d’adresse e-mail réutilise ce modèle.

Le nom d’envoi est toujours **Kinq Team**. `KINQ_RESEND_FROM` conserve l’adresse d’envoi vérifiée (par défaut `connexion@kinq-app.com`), même si une ancienne configuration contient le nom « KINQ ». `KINQ_RESEND_API_KEY` reste une variable secrète côté serveur, jamais dans le site ni l’app. Le domaine de l’adresse doit être vérifié dans Resend.

Le message contient une version HTML anthracite / vert acide `#b2ff1a` et une version texte. Son titre et ses instructions s’adaptent à l’inscription, à la connexion ou au changement d’adresse. Aucune image externe ni police téléchargée n’est nécessaire pour lire le code.

Les codes aléatoires à six chiffres restent à usage unique, valables dix minutes et limités à cinq essais. Un challenge n’est enregistré qu’après acceptation par Resend. Une panne réseau ou un refus de Resend produit une erreur permettant de réessayer ; aucune réussite fictive. L’acceptation API ne prouve pas la réception dans la boîte e-mail.

Le compte de test unique avec identifiant de connexion provisionné conserve le parcours normal et la réponse `configured_code`, sans envoi à son adresse. Les doubles de transport et données isolées se limitent à `tests/test_member_auth_email.py`.

Documentation de l’API d’envoi : <https://resend.com/docs/api-reference/emails/send-email>.
