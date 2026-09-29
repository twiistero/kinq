"""Render the approved editorial text for the first NO TABOO article."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "content/no-taboo/premiers-pas.txt"

# The full editorial copy lives in SOURCE. These are presentation metadata only.
SECTIONS = [
    ("Qu’est-ce qui t’attire, exactement ?", "attirance", "Ce qui t’attire", "t’attire"),
    ("Ce qui te fait fantasmer n’est pas forcément ce que tu veux vivre", "fantasme", "Fantasme et réalité", "veux vivre"),
    ("Dom, sub, switch : tu n’es pas obligé de choisir tout de suite", "roles", "Dom, sub, switch", "pas obligé"),
    ("Dire que tu débutes sans t’excuser pendant dix minutes", "debuter", "Dire que tu débutes", "sans t’excuser"),
    ("Et si c’est à ton partenaire que tu aimerais en parler ?", "partenaire", "En parler à ton partenaire", "à ton partenaire"),
    ("Cherche un mec avec qui tu peux parler normalement", "bon-mec", "Trouver le bon mec", "parler normalement"),
    ("Parler de tes limites sans plomber l’ambiance", "limites", "Parler de tes limites", "tes limites"),
    ("Pour une première rencontre, fais simple", "rencontre", "La première rencontre", "fais simple"),
    ("Tu n’as pas besoin du look parfait pour commencer", "look", "Le look parfait ?", "look parfait"),
    ("Tu peux aussi découvrir le milieu sans chercher un plan", "milieu", "Découvrir le milieu", "sans chercher un plan"),
    ("Rester discret sans te couper de tous les échanges", "discretion", "Rester discret", "Rester discret"),
    ("Après une expérience, laisse-toi le temps de voir ce que tu en penses", "apres", "Après une expérience", "le temps"),
    ("Et si tu préfères finalement en rester là ?", "en-rester-la", "En rester là", "en rester là"),
]

PHOTOS_AFTER = {
    0: ("https://armyofmen.com/cdn/shop/files/head-harness-pup-scout-blue-model-front.jpg?v=1757678289&width=1200", "Homme adulte portant une cagoule puppy bleue", "PUPPY", ""),
    2: ("https://www.invinciblerubber.com/image/cache/catalog/SU056_h-840x840.jpg", "Homme adulte en tenue de latex", "LATEX", " nt-editorial-photo-wide"),
    5: ("https://mr-riegillio.com/cdn/shop/articles/sylven-meets-rj-585763.jpg?v=1607874225&width=1200", "Deux hommes adultes en tenue fetish sportswear", "SPORTSWEAR", ""),
    8: ("https://www.scallychav.co.uk/cdn/shop/files/FDCA6A7D-D889-4DFA-AD34-30F6174243C3.jpg?v=1778270620&width=1445", "Homme adulte en tenue sportswear", "STYLE", " nt-editorial-photo-wide"),
    10: ("https://mr-riegillio.com/cdn/shop/files/MR_R62699_copy.jpg?v=1770812952&width=1600", "Deux hommes adultes en tenue sportswear fetish", "RENCONTRE", ""),
}


def heading_html(title, emphasized):
    before, after = title.split(emphasized, 1)
    return f"{escape(before)}<em>{escape(emphasized)}</em>{escape(after)}"


def render():
    blocks = [block.strip() for block in SOURCE.read_text().split("\n\n") if block.strip()]
    assert len(blocks) > 70 and blocks[4] == SECTIONS[0][0], "Unexpected article source structure"
    toc = "".join(
        f'<li><a href="#{slug}">{escape(short)} <svg aria-hidden="true"><use href="#arrow"/></svg></a></li>'
        for _, slug, short, _ in SECTIONS
    )
    body = ['<div class="nt-editorial-body nt-user-article"><div class="nt-editorial-intro"><p class="eyebrow">POUR COMMENCER</p>']
    for index, paragraph in enumerate(blocks[:4]):
        klass = ' class="nt-dropcap"' if index == 0 else ''
        body.append(f'<p{klass}>{escape(paragraph)}</p>')
    body.append('</div>')

    cursor = 4
    headings = {title for title, _, _, _ in SECTIONS}
    for index, (title, slug, _, emphasized) in enumerate(SECTIONS):
        assert blocks[cursor] == title, f"Unexpected heading at block {cursor}: {blocks[cursor]}"
        cursor += 1
        body.append(f'<section class="nt-editorial-section" id="{slug}"><h2>{heading_html(title, emphasized)}</h2>')
        while cursor < len(blocks) and blocks[cursor] not in headings:
            body.append(f'<p>{escape(blocks[cursor])}</p>')
            cursor += 1
        body.append('</section>')
        if index in PHOTOS_AFTER:
            src, alt, label, modifier = PHOTOS_AFTER[index]
            body.append(f'<figure class="nt-editorial-photo{modifier}"><img src="{escape(src, quote=True)}" alt="{escape(alt)}, photo d’illustration" loading="lazy"><figcaption><span>{label} · PHOTO D’ILLUSTRATION</span> Les personnes photographiées ne sont pas des membres Kinq.</figcaption></figure>')
    assert cursor == len(blocks), "Not all editorial copy was rendered"
    body.append('''<aside class="nt-editorial-sources"><span>REPÈRES CITÉS DANS L’ARTICLE</span><p><a href="https://prep.sexosafe.fr/ma-sexualite/pratiques-sexuelles/bdsm-entre-hommes-attache-moi" target="_blank" rel="noopener">Sexosafe · BDSM entre hommes</a> · <a href="https://prep.sexosafe.fr/ma-sexualite/pratiques-sexuelles/pratiquer-le-sexe-hard-en-restant-safe" target="_blank" rel="noopener">Sexosafe · Pratiquer le sexe hard en restant safe</a> · <a href="https://cnil.fr/fr/sites-et-applications-de-rencontres-comment-proteger-votre-intimite" target="_blank" rel="noopener">CNIL · Protéger votre intimité sur les applications de rencontres</a></p></aside></div>''')

    return f'''<div class="nt-site nt-reading nt-editorial wrap">
<header class="nt-masthead"><a href="guides.html" aria-label="NO TABOO, accueil du journal"><strong>NO TABOO<span>.</span></strong><small>LE JOURNAL KINQ</small></a></header>
<article><header class="nt-editorial-hero"><div class="nt-editorial-hero-copy"><p class="eyebrow">NO TABOO / PREMIERS PAS · 26 MIN DE LECTURE</p><h1>Curieux, mais<br>pas sûr de toi&nbsp;?<br><em>Tu es au bon<br>endroit.</em></h1><p>Un profil te plaît, une tenue te fait de l’effet, une pratique revient dans tes recherches.</p><div class="nt-hero-actions"><a href="#sommaire" class="nt-editorial-scroll">Lire l’article <svg aria-hidden="true"><use href="#arrow"/></svg></a><span id="journal-comment-count"></span></div></div><figure class="nt-editorial-hero-photo"><img src="https://images.squarespace-cdn.com/content/v1/5c55184293a6324e1f793b37/1643420235677-MR0J2B9DH8N8NK1K9LEW/Raif%2B%26%2BMark.jpg" alt="Deux hommes adultes en tenue de cuir, photo d’illustration" fetchpriority="high"><figcaption>PHOTO D’ILLUSTRATION · PAS DES PROFILS KINQ</figcaption></figure></header>
<nav class="nt-editorial-toc" id="sommaire" aria-label="Sommaire de l’article"><div><h2>SOMMAIRE</h2></div><ol>{toc}</ol></nav>
{''.join(body)}
</article><section class="nt-next"><p class="eyebrow">CONTINUER À LIRE</p><div><a href="aftercare.html"><small>À LIRE AUSSI</small><strong>L’aftercare : la connexion continue après.</strong></a><a href="parler-de-ses-limites.html"><small>ARTICLE SUIVANT</small><strong>Parler de ses limites sans casser le feeling.</strong></a></div></section>
<aside class="nt-end"><p class="eyebrow">TES KINKS. TES CODES. TES RENCONTRES.</p><h2>Envie d’aller<br><em>plus loin ?</em></h2><div><a class="button" href="rencontres.html">Explorer les rencontres <svg aria-hidden="true"><use href="#up"/></svg></a><button class="button light" data-modal="join">Créer mon compte <svg aria-hidden="true"><use href="#up"/></svg></button></div></aside></div>'''
