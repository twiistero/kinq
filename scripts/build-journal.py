"""Build the standalone NO TABOO journal from one editorial source."""
from pathlib import Path
from html import escape
import re
from render_first_article import render as render_first_article
from render_second_article import render as render_second_article

ROOT = Path(__file__).resolve().parent.parent / "legacy-pages"
HOME = ROOT / "index.html"
SHELL = (ROOT / "guides.html").read_text()

ARTICLES = [
    dict(slug="premiers-pas", key="start", category="Premiers pas", time="26 min", art="art-one", poster="FIRST<br><em>TIME?</em>", title="Curieux, mais pas sûr de toi ? Tu es au bon endroit.", deck="Un profil te plaît, une tenue te fait de l’effet, une pratique revient dans tes recherches.", sections=[
        ("La curiosité suffit", "Une matière, un mot ou une dynamique t’intrigue ? Tu n’as pas besoin d’une étiquette pour t’y intéresser. Regarder, lire et discuter sont déjà des façons d’explorer. Tu peux avancer à ton rythme et changer d’avis en chemin."),
        ("Dire où tu en es", "Un message simple vaut mieux qu’un rôle joué : « Je découvre cet univers. Qu’est-ce qu’il représente pour toi ? » Tu peux préciser ce qui te plaît, ce que tu ne sais pas encore et ce que tu préfères garder pour plus tard."),
        ("Une rencontre se construit à deux", "Un kink commun donne un sujet de conversation, pas un scénario obligatoire. Écoute la réponse de l’autre, parle de tes limites et laisse de la place au feeling. Le droit de dire non reste entier à chaque étape.")], links=[("Découvrir les univers", "kinks.html"), ("Voir les profils", "rencontres.html")]),
    dict(slug="parler-de-ses-limites", key="limits", category="Entre nous", time="25 min", art="art-two", poster="YES.<br>NO.<br><em>MAYBE.</em>", title="Parler de ses limites sans casser le feeling.", deck="Le mec te plaît, la conversation se passe bien. Comment dire ce que tu ne veux pas sans refroidir l’échange ?", sections=[
        ("Commencer sans grand discours", "Tu peux demander : « Qu’est-ce qui te tente ? Qu’est-ce qu’on laisse de côté ? » Dire « je ne sais pas encore » est aussi une réponse. Cette discussion peut avoir lieu bien avant de se voir."),
        ("Oui, non, peut-être", "Distingue ce dont tu as envie, ce qui demande une discussion et ce que tu refuses. Un « peut-être » ne devient pas un oui par insistance. Un oui peut être retiré, même si la conversation ou la rencontre a déjà commencé."),
        ("Garder le lien", "Reformule ce que tu as compris et vérifie avec l’autre. Une préférence sur un profil Kinq ouvre une conversation ; elle ne vaut jamais consentement. Le respect des limites est une façon très concrète de créer du feeling.")], links=[("Lire le lexique", "lexique.html"), ("Explorer les rencontres", "rencontres.html")]),
    dict(slug="les-mots-pour-se-comprendre", key="words", category="Le lexique", time="4 min", art="art-three", poster="DOM.<br>SUB.<br><em>ET TOI ?</em>", title="Les mots pour te comprendre. Pas pour t’enfermer.", deck="Quelques repères pour poser les bonnes questions.", sections=[
        ("Des mots, pas des cases", "Dom et sub parlent de rôles dans une dynamique de domination et de soumission consentie. Switch peut désigner une personne qui apprécie plusieurs rôles. Aucun de ces mots ne résume une personnalité ou une position sexuelle."),
        ("Chacun a ses nuances", "Deux personnes peuvent employer le même mot pour des envies différentes. Demande ce qu’il signifie pour ton interlocuteur. Tu peux aussi décrire ce que tu ressens avec tes propres mots, sans choisir d’étiquette."),
        ("Continuer la conversation", "Le lexique Kinq donne des repères simples. Une définition aide à comprendre ; elle ne remplace pas l’échange, les limites exprimées et le consentement de chacun.")], links=[("Ouvrir le lexique", "lexique.html"), ("Découvrir les univers", "kinks.html")]),
    dict(slug="profil-et-vie-privee", key="privacy", category="Vie privée", time="4 min", art="art-two", poster="PRIVATE.<br>BY <em>CHOICE.</em>", title="Ton profil, tes règles. Tu choisis ce que tu partages.", deck="Se montrer à son rythme peut aussi faire partie du jeu.", sections=[
        ("Choisir ce qu’on montre", "Un profil n’a pas à tout raconter. Une photo, quelques mots et tes centres d’intérêt peuvent suffire pour commencer. Garde pour toi les informations que tu ne veux pas partager publiquement."),
        ("Prendre le temps", "Avant d’envoyer des coordonnées ou des images privées, apprends à connaître la personne. Une demande n’est pas une obligation. Tu peux dire non sans donner d’explication."),
        ("Rester maître de tes choix", "La version complète de Kinq prévoit une visibilité choisie, des albums sur autorisation, ainsi que des outils de blocage et de signalement. Ces fonctions ne sont pas encore actives dans ce prototype. Pour l’instant, les profils présentés sont fictifs.")], links=[("Voir l’approche Kinq", "index.html#engagements"), ("Explorer les profils", "rencontres.html")]),
    dict(slug="premiere-rencontre", key="meet", category="Rencontres", time="5 min", art="art-one", poster="IRL.<br><em>ET ALORS ?</em>", title="Du premier message à la première rencontre.", deck="Passer du chat au réel, sans brûler les étapes.", sections=[
        ("Dire ce qu’on imagine", "Un premier rendez-vous peut être un verre, une promenade ou simplement une discussion. Propose un cadre qui te convient et demande à l’autre ce qu’il attend. Aucun échange en ligne n’engage à aller plus loin."),
        ("Garder de la marge", "Choisis un lieu où tu te sens à l’aise, organise ton retour et garde la possibilité de partir. Prévenir une personne de confiance de ton programme peut aider à te sentir plus serein."),
        ("Laisser une place au réel", "Le feeling peut changer lorsqu’on se rencontre. Tu peux ralentir, poser une question ou dire non, même après des messages enthousiastes. Une bonne rencontre laisse cette liberté aux deux personnes.")], links=[("Découvrir les rencontres", "rencontres.html"), ("Lire les limites", "parler-de-ses-limites.html")]),
    dict(slug="aftercare", key="after", category="Entre nous", time="4 min", art="art-three", poster="ET<br><em>APRÈS ?</em>", title="L’aftercare : la connexion continue après.", deck="L’attention portée à l’autre a plusieurs formes.", sections=[
        ("Après, on fait quoi ?", "L’aftercare désigne l’attention portée à chacun après un moment partagé. Certaines personnes souhaitent parler ou rester proches ; d’autres préfèrent du calme ou de l’espace. Il n’existe pas de rituel universel."),
        ("En parler avant", "Demande ce qui ferait du bien à l’autre et exprime aussi tes besoins. N’imagine pas que vous attendez la même chose. Un accord sur une pratique ne dit rien, à lui seul, de ce que chacun souhaite ensuite."),
        ("Un message peut suffire", "Plus tard, un mot pour prendre des nouvelles peut ouvrir un échange sincère, si vous en avez tous les deux envie. Respecter une demande d’espace fait aussi partie de l’attention.")], links=[("Parler des limites", "parler-de-ses-limites.html"), ("Rencontrer sur Kinq", "rencontres.html")]),
]

BY_KEY = {article["key"]: article for article in ARTICLES}
HERO_PHOTOS = {
    "limits": ("https://mr-riegillio.com/cdn/shop/articles/sylven-meets-rj-585763.jpg?v=1607874225&width=1200", "Deux hommes adultes en tenue fetish sportswear"),
    "words": ("https://www.invinciblerubber.com/image/cache/catalog/SU056_h-840x840.jpg", "Homme adulte en tenue de latex"),
    "privacy": ("https://www.scallychav.co.uk/cdn/shop/files/FDCA6A7D-D889-4DFA-AD34-30F6174243C3.jpg?v=1778270620&width=1445", "Homme adulte en tenue sportswear"),
    "meet": ("https://mr-riegillio.com/cdn/shop/files/MR_R62699_copy.jpg?v=1770812952&width=1600", "Deux hommes adultes en tenue sportswear fetish"),
    "after": ("https://armyofmen.com/cdn/shop/files/head-harness-pup-scout-blue-model-front.jpg?v=1757678289&width=1200", "Homme adulte portant une cagoule puppy bleue"),
}
def icon(name="up"):
    return f'<svg aria-hidden="true"><use href="#{name}"/></svg>'

def card(article):
    anchor = {"limits": "entre-nous", "words": "les-mots", "privacy": "vie-privee", "meet": "rencontres"}.get(article["key"])
    anchor = f' id="{anchor}"' if anchor else ""
    return (f'<a class="article nt-card"{anchor} href="{article["slug"]}.html">'
            f'<div class="article-art {article["art"]}"><span>{article["poster"]}</span>{icon()}</div>'
            f'<p class="eyebrow">{article["category"].upper()} · {article["time"].upper()}</p>'
            f'<h3><span class="link-label">{escape(article["title"])}</span></h3>'
            f'<p class="nt-card-summary">{escape(article.get("summary", ""))}</p></a>')

def write_page(filename, title, description, body, category=None):
    if category:
        slug = Path(filename).stem
        marker = '<section class="nt-next">'
        if marker not in body:
            raise ValueError(f"Missing article footer in {filename}")
        body = body.replace(marker, f'<section id="journal-comments" data-article-slug="{slug}"></section>' + marker, 1)
    page = re.sub(r'<main id="page-main">.*?</main>', f'<main id="page-main">{body}</main>', SHELL, flags=re.S)
    if category:
        page = page.replace('<script type="module" src="/journal-dynamic.js"></script>', '')
    attrs = 'data-page="journal"'
    if category:
        attrs += f' data-breadcrumb-category="{escape(category, quote=True)}" data-breadcrumb-title="{escape(title, quote=True)}"'
    page = re.sub(r'<body[^>]*>', f'<body {attrs}>', page, count=1)
    page = re.sub(r'<title>.*?</title>(?:<meta name="description" content="[^"]*">)?', f'<title>{escape(title)} — NO TABOO, Kinq</title><meta name="description" content="{escape(description, quote=True)}">', page, count=1)
    (ROOT / filename).write_text(page)

landing = '''<div class="nt-site wrap"><header class="nt-masthead"><a href="guides.html" aria-label="NO TABOO, accueil du journal"><strong>NO TABOO<span>.</span></strong><small>LE JOURNAL KINQ</small></a></header>
<section class="nt-hero"><div><h1>Rien que pour toi.<br><em>Juste entre nous.</em></h1><p>Toutes les réponses aux questions que tu n'oses pas toujours poser.</p><a class="button" href="#a-la-une">Commencer à lire ''' + icon("arrow") + '''</a></div><div class="nt-hero-mark" aria-hidden="true"><span>NO<br>TABOO.</span><svg><use href="#brand"/></svg></div></section>
<nav class="nt-topics" aria-label="Rubriques du journal"><a href="#a-la-une">À la une</a><a href="#a-la-une">Premiers pas</a><a href="#entre-nous">Entre nous</a><a href="#les-mots">Les mots</a><a href="#rencontres">Rencontres</a></nav>
<section class="nt-feature" id="a-la-une"><div class="nt-feature-head"><p class="eyebrow">À LA UNE / PREMIERS PAS</p><h2><a class="nt-title-link" data-ink-link href="premiers-pas.html"><span class="ink-label">Curieux, mais pas sûr de toi ? Tu es au bon endroit.</span></a></h2></div><a class="nt-feature-art" href="premiers-pas.html" aria-label="Lire Curieux, mais pas sûr de toi ?"><span>FIRST<br><em>TIME?</em></span>''' + icon() + '''</a><div class="nt-feature-summary"><p>Une envie n’a pas besoin d’un mode d’emploi. Trouve tes mots, puis le bon moment pour en parler.</p><a class="button" href="premiers-pas.html">Lire l’article ''' + icon("up") + '''</a></div></section>
<section class="nt-section" id="premiers-pas"><div class="nt-heading"><h2>LES AUTRES ARTICLES</h2></div><div class="articles nt-grid">''' + card(ARTICLES[1]) + card(ARTICLES[2]) + card(ARTICLES[3]) + card(ARTICLES[4]) + card(ARTICLES[5]) + '''</div></section>
<aside class="nt-bridge"><div><p class="eyebrow">DU JOURNAL À LA RENCONTRE</p><h2>Une question en tête ?<br><em>Un profil peut y répondre.</em></h2></div><a class="button" href="rencontres.html">Explorer les rencontres ''' + icon("up") + '''</a></aside>
<div class="nt-paths"><a href="lexique.html"><p class="eyebrow">UN MOT T’INTRIGUE ?</p><h2>Le lexique ''' + icon() + '''</h2><p>Des repères pour ouvrir la discussion.</p></a><a href="kinks.html"><p class="eyebrow">UNE ENVIE SE DESSINE ?</p><h2>Les univers ''' + icon() + '''</h2><p>Découvre ce qui te parle.</p></a></div>
<section class="nt-end nt-end-wall" id="journal-suite"><div class="nt-end-copy"><p class="eyebrow">TES KINKS. TES CODES. TES RENCONTRES.</p><h2>La suite se vit<br><em>sur Kinq.</em></h2><div class="nt-end-actions"><a class="button" href="rencontres.html">Voir les profils ''' + icon("arrow") + '''</a><button class="button light" data-modal="join">Créer mon compte ''' + icon("up") + '''</button></div><span class="nt-app-note">L’app Kinq, bientôt disponible ''' + icon("download") + '''</span></div><div class="nt-end-tapestry" aria-hidden="true"><div class="wall-background"></div></div></section></div>'''
write_page("guides.html", "Le journal kink", "NO TABOO, le journal kink de Kinq : envies, mots, limites et rencontres.", landing)

for index, article in enumerate(ARTICLES):
    if article["key"] == "start":
        write_page(article["slug"] + ".html", article["title"], article["deck"], render_first_article(), article["category"])
        continue
    if article["key"] == "limits":
        write_page(article["slug"] + ".html", article["title"], article["deck"], render_second_article(), article["category"])
        continue
    previous = ARTICLES[(index - 1) % len(ARTICLES)]
    following = ARTICLES[(index + 1) % len(ARTICLES)]
    sections = ''.join(f'<section><h2>{escape(heading)}</h2><p>{escape(paragraph)}</p></section>' for heading, paragraph in article["sections"])
    links = ''.join(f'<a href="{href}">{escape(label)} {icon()}</a>' for label, href in article["links"])
    photo, photo_alt = HERO_PHOTOS[article["key"]]
    body = f'''<div class="nt-site nt-reading wrap"><header class="nt-masthead"><a href="guides.html" aria-label="NO TABOO, accueil du journal"><strong>NO TABOO<span>.</span></strong><small>LE JOURNAL KINQ</small></a></header>
    <article class="nt-story"><header class="nt-editorial-hero nt-editorial-hero-generic"><div class="nt-editorial-hero-copy"><p class="eyebrow">NO TABOO / {escape(article["category"].upper())} · {article["time"].upper()} DE LECTURE</p><h1>{escape(article["title"])}</h1><p>{escape(article["deck"])}</p><div class="nt-hero-actions"><a class="nt-editorial-scroll" href="#article">Lire l’article {icon("arrow")}</a><span id="journal-comment-count"></span></div></div><figure class="nt-editorial-hero-photo"><img src="{escape(photo, quote=True)}" alt="{escape(photo_alt, quote=True)}, photo d’illustration" fetchpriority="high"><figcaption>PHOTO D’ILLUSTRATION · PAS UN PROFIL KINQ</figcaption></figure></header><div class="nt-story-layout" id="article"><aside><span>À GARDER EN TÊTE</span><p>Le feeling se construit dans l’échange. Tes envies et tes limites comptent autant que celles de l’autre.</p><a href="guides.html">Retour au journal {icon("up")}</a></aside><div class="nt-prose">{sections}<div class="nt-story-cta"><p class="eyebrow">PASSER DE LA LECTURE À L’ÉCHANGE</p><h2>La conversation<br>continue.</h2><div>{links}</div></div></div></div></article>
    <section class="nt-next"><p class="eyebrow">CONTINUER À LIRE</p><div><a href="{previous["slug"]}.html"><small>ARTICLE PRÉCÉDENT</small><strong>{escape(previous["title"])}</strong></a><a href="{following["slug"]}.html"><small>ARTICLE SUIVANT</small><strong>{escape(following["title"])}</strong></a></div></section><aside class="nt-end"><p class="eyebrow">TES KINKS. TES CODES. TES RENCONTRES.</p><h2>Envie d’aller<br><em>plus loin ?</em></h2><div><a class="button" href="rencontres.html">Explorer les rencontres {icon("up")}</a><button class="button light" data-modal="join">Créer mon compte {icon("up")}</button></div></aside></div>'''
    write_page(article["slug"] + ".html", article["title"], article["deck"], body, article["category"])

# Keep the six approved home cards, but take readers to their own articles.
home = HOME.read_text()
start, end = home.index('<section class="journal section'), home.index('</section>', home.index('<section class="journal section')) + len('</section>')
fragment = home[start:end]
for key, article in BY_KEY.items():
    fragment = fragment.replace(f'<button class="article" data-article="{key}">', f'<a class="article" href="{article["slug"]}.html">')
fragment = fragment.replace('</button>', '</a>')
HOME.write_text(home[:start] + fragment + home[end:])
