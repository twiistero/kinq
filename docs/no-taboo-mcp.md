# NO TABOO depuis ChatGPT

Le serveur MCP éditorial est exposé à `https://kinq-app.com/mcp`. Dans ChatGPT, ajouter cette URL comme connecteur MCP personnalisé, puis autoriser la connexion avec un compte Google Workspace `@theethercompany.com`. Le rôle `moderator` ou `admin` est requis pour écrire ; les autres membres de l’équipe peuvent lire. Les jetons expirent après 30 jours et la connexion doit alors être renouvelée.

Outils : `list_articles`, `get_article`, `save_article_draft`, `publish_article`, `remove_article`. Une modification reste en brouillon tant que `publish_article` n’est pas appelé. `remove_article` retire immédiatement la page publique et conserve l’enregistrement en base pour restauration. Les opérations de modification, publication et retrait utilisent une révision pour éviter d’écraser un changement concurrent.

Les six articles historiques issus de `scripts/build-journal.py` conservent leur mise en page et restent gérés dans le code. Le MCP gère les articles créés dans PostgreSQL.

Chaque nouvel article est publié sous `https://kinq-app.com/{slug}` et rejoint la grille des articles sur `/guides`. L’ancienne adresse `/journal/{slug}` redirige vers cette URL. Le titre et le résumé sont du texte brut. Le corps accepte des paragraphes et intertitres HTML simples ; les SVG et les images intégrées au texte sont refusés. La rubrique `category` reprend l’une des rubriques visibles sur `/guides` et alimente le fil d’Ariane. La couverture utilise le même encart typographique que les autres articles, avec `art_words` : 2 ou 3 mots courts en majuscules, par exemple `MUSK.`, `PITS.`, `WORN.`. La durée de lecture affichée est calculée à partir du texte.
