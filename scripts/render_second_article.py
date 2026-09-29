"""Render the user-supplied copy for the second NO TABOO article."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "content/no-taboo/parler-de-ses-limites.txt"

# Headings, anchors and visual emphasis only. The article's wording stays in SOURCE.
SECTIONS = [
    ("Trouver le moment sans annoncer une conversation grave", "le-moment", "Trouver le moment", "le moment"),
    ("Parle aussi de ce qui te plaît", "tes-envies", "Parler de tes envies", "ce qui te plaît"),
    ("« Pas trop hard » ne dit pas encore grand-chose", "etre-precis", "Être précis", "Pas trop hard"),
    ("Faire la différence entre « non », « pas cette fois » et « je ne sais pas »", "oui-non-peut-etre", "Non, pas cette fois, je ne sais pas", "pas cette fois"),
    ("Les limites ne concernent pas uniquement les pratiques", "le-cadre", "Préciser le cadre", "pas uniquement les pratiques"),
    ("Tu peux expliquer une limite sans raconter toute ton histoire", "sans-se-justifier", "Sans tout raconter", "sans raconter toute ton histoire"),
    ("Être soumis ne t’oblige pas à rester dans ton rôle pendant la discussion", "hors-jeu", "Parler hors jeu", "rester dans ton rôle"),
    ("Pendant la rencontre, tu peux parler beaucoup plus simplement", "pendant", "Pendant la rencontre", "beaucoup plus simplement"),
    ("N’attends pas le milieu de la séance pour proposer ce qui avait été écarté", "ne-pas-renegocier", "Ne pas renégocier en séance", "milieu de la séance"),
    ("Quand c’est lui qui pose une limite, ne lui fais pas gérer ta déception", "sa-limite", "Quand il pose une limite", "gérer ta déception"),
    ("Reconnaître le moment où la discussion devient de l’insistance", "insistance", "Reconnaître l’insistance", "devient de l’insistance"),
    ("Avec un partenaire régulier, les habitudes méritent aussi d’être discutées", "habitudes", "Avec un partenaire régulier", "les habitudes"),
    ("Après, un retour précis vaut mieux qu’un « tout était parfait » automatique", "apres", "Après la rencontre", "un retour précis"),
    ("Si une limite n’a pas été respectée, ce n’est plus une question de bonne formulation", "limite-ignoree", "Si une limite est ignorée", "pas été respectée"),
    ("Et si, finalement, vos envies ne se rejoignent pas ?", "envies-differentes", "Si vos envies diffèrent", "vos envies ne se rejoignent pas"),
]

PHOTOS_AFTER = {
    1: ("https://mr-riegillio.com/cdn/shop/files/MR_R62699_copy.jpg?v=1770812952&width=1600", "Deux hommes adultes en tenue sportswear fetish", "RENCONTRE", ""),
    4: ("https://www.invinciblerubber.com/image/cache/catalog/SU056_h-840x840.jpg", "Homme adulte en tenue de latex", "LATEX", " nt-editorial-photo-wide"),
    7: ("https://armyofmen.com/cdn/shop/files/head-harness-pup-scout-blue-model-front.jpg?v=1757678289&width=1200", "Homme adulte portant une cagoule puppy bleue", "PUPPY", ""),
    10: ("https://images.squarespace-cdn.com/content/v1/5c55184293a6324e1f793b37/1643420235677-MR0J2B9DH8N8NK1K9LEW/Raif%2B%26%2BMark.jpg", "Deux hommes adultes en tenue de cuir", "ENTRE NOUS", " nt-editorial-photo-wide"),
    12: ("https://www.scallychav.co.uk/cdn/shop/files/FDCA6A7D-D889-4DFA-AD34-30F6174243C3.jpg?v=1778270620&width=1445", "Homme adulte en tenue sportswear", "À TON RYTHME", ""),
}


def heading_html(title, emphasized):
    before, after = title.split(emphasized, 1)
    return f"{escape(before)}<em>{escape(emphasized)}</em>{escape(after)}"


def render():
    blocks = [block.strip() for block in SOURCE.read_text().strip().split("\n\n") if block.strip()]
    assert len(blocks) == 95 and blocks[0] == "Parler de ses limites sans casser le feeling"
    assert blocks[6] == SECTIONS[0][0], "Unexpected article source structure"
    headings = {heading for heading, _, _, _ in SECTIONS}
    toc = "".join(
        f'<li><a href="#{slug}">{escape(short)} <svg aria-hidden="true"><use href="#arrow"/></svg></a></li>'
        for _, slug, short, _ in SECTIONS
    )
    body = ['<div class="nt-editorial-body nt-user-article"><div class="nt-editorial-intro"><p class="eyebrow">POUR COMMENCER</p>']
    for index, paragraph in enumerate(blocks[1:6]):
        klass = ' class="nt-dropcap"' if index == 0 else ''
        body.append(f'<p{klass}>{escape(paragraph)}</p>')
    body.append('</div>')
    cursor = 6
    for index, (heading, slug, _, emphasized) in enumerate(SECTIONS):
        assert blocks[cursor] == heading, f"Unexpected heading at block {cursor}"
        cursor += 1
        body.append(f'<section class="nt-editorial-section" id="{slug}"><h2>{heading_html(heading, emphasized)}</h2>')
        while cursor < len(blocks) and blocks[cursor] not in headings:
            body.append(f'<p>{escape(blocks[cursor])}</p>')
            cursor += 1
        body.append('</section>')
        if index in PHOTOS_AFTER:
            src, alt, label, modifier = PHOTOS_AFTER[index]
            body.append(f'<figure class="nt-editorial-photo{modifier}"><img src="{escape(src, quote=True)}" alt="{escape(alt)}, photo d’illustration" loading="lazy"><figcaption><span>{label} · PHOTO D’ILLUSTRATION</span> Les personnes photographiées ne sont pas des membres Kinq.</figcaption></figure>')
    assert cursor == len(blocks), "Not all editorial copy was rendered"
    body.append('''<aside class="nt-editorial-sources"><span>REPÈRES CITÉS DANS L’ARTICLE</span><p><a href="https://ncsfreedom.org/wp-content/uploads/2023/06/Negotiation-Guide.pdf" target="_blank" rel="noopener">NCSF · Guide de préparation</a> · <a href="https://ncsfreedom.org/wp-content/uploads/2025/09/Is-this-Assault-Updated.pdf" target="_blank" rel="noopener">NCSF · Limites et consentement</a> · <a href="https://prep.sexosafe.fr/ma-sexualite/pratiques-sexuelles/bdsm-entre-hommes-attache-moi" target="_blank" rel="noopener">Sexosafe · BDSM entre hommes</a> · <a href="https://www.questionsexualite.fr/lutter-contre-les-violences-et-discriminations/le-consentement/dire-non-a-une-relation-ou-a-une-pratique-sexuelle" target="_blank" rel="noopener">QuestionsSexualité · Dire non</a> · <a href="https://cnil.fr/fr/sites-et-applications-de-rencontres-comment-proteger-votre-intimite" target="_blank" rel="noopener">CNIL · Protéger votre intimité</a></p></aside></div>''')

    return f'''<div class="nt-site nt-reading nt-editorial wrap">
<header class="nt-masthead"><a href="guides.html" aria-label="NO TABOO, accueil du journal"><strong>NO TABOO<span>.</span></strong><small>LE JOURNAL KINQ</small></a></header>
<article><header class="nt-editorial-hero"><div class="nt-editorial-hero-copy"><p class="eyebrow">NO TABOO / ENTRE NOUS · 25 MIN DE LECTURE</p><h1>Parler de ses<br><em>limites</em> sans<br>casser le feeling.</h1><p>Le mec te plaît, la conversation se passe bien. Comment dire ce que tu ne veux pas sans refroidir l’échange ?</p><div class="nt-hero-actions"><a href="#sommaire" class="nt-editorial-scroll">Lire l’article <svg aria-hidden="true"><use href="#arrow"/></svg></a><span id="journal-comment-count"></span></div></div><figure class="nt-editorial-hero-photo"><img src="https://mr-riegillio.com/cdn/shop/articles/sylven-meets-rj-585763.jpg?v=1607874225&width=1200" alt="Deux hommes adultes en tenue fetish sportswear, photo d’illustration" fetchpriority="high"><figcaption>PHOTO D’ILLUSTRATION · PAS DES PROFILS KINQ</figcaption></figure></header>
<nav class="nt-editorial-toc" id="sommaire" aria-label="Sommaire de l’article"><div><h2>SOMMAIRE</h2></div><ol>{toc}</ol></nav>
{''.join(body)}
</article><section class="nt-next"><p class="eyebrow">CONTINUER À LIRE</p><div><a href="premiers-pas.html"><small>ARTICLE PRÉCÉDENT</small><strong>Curieux, mais pas sûr de toi ? Tu es au bon endroit.</strong></a><a href="les-mots-pour-se-comprendre.html"><small>ARTICLE SUIVANT</small><strong>Les mots pour te comprendre. Pas pour t’enfermer.</strong></a></div></section>
<aside class="nt-end"><p class="eyebrow">TES KINKS. TES CODES. TES RENCONTRES.</p><h2>Envie d’aller<br><em>plus loin ?</em></h2><div><a class="button" href="rencontres.html">Explorer les rencontres <svg aria-hidden="true"><use href="#up"/></svg></a><button class="button light" data-modal="join">Créer mon compte <svg aria-hidden="true"><use href="#up"/></svg></button></div></aside></div>'''
