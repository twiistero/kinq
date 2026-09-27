"""KINQ 04: original, single-ink symbols on a 24-unit grid.

Keep the identifying contour; omit texture, highlights and decoration.
All strokes share a 1.5-unit weight and rounded joins/caps.
"""

def line(d):
    return f'<path d="{d}" fill="none" stroke="var(--ink)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'

def solid(d):
    return f'<path d="{d}" fill="var(--ink)" stroke="none"/>'

def circle(x, y, r):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="var(--ink)" stroke-width="1.5"/>'

def rect(x, y, w, h, r=1.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="var(--ink)" stroke-width="1.5"/>'

V4 = {}
def add(key, cue, *parts):
    V4[key] = dict(body=''.join(parts), viewBox='0 0 24 24', version=4,
                   cue=cue, reference=None)

add('bondage', 'Deux maillons liés.',
    line('M10 14 14 10M9 16l-2 2a3.5 3.5 0 0 1-5-5l4-4a3.5 3.5 0 0 1 5 0M15 8l2-2a3.5 3.5 0 0 1 5 5l-4 4a3.5 3.5 0 0 1-5 0'))
add('shibari', 'Une corde enroulée, nouée au centre, avec deux brins libres.',
    line('M6 10V7a6 6 0 0 1 12 0v3M9 10V7a3 3 0 0 1 6 0v3M6 14v2a6 6 0 0 0 12 0v-2M9 14v2a3 3 0 0 0 3 3M15 14l1 7M12 14l-1 8'),
    rect(4.5, 10, 15, 4, 1))
add('restraints', 'Deux anneaux reliés par un seul trait.',
    circle(6.5, 16, 4.5), circle(17.5, 8, 4.5), line('M10.15 13.35l3.7-2.7'))
add('mummification', 'Une silhouette enveloppée de bandes.',
    line('M8 4q4-3 8 0l2 7-3 10H9L6 11ZM8 7h8M7 11h10M8 15h8M9 18h6'))
add('spanking', 'Une main ouverte.',
    line('M8 21v-4l-4-6q-1-2 1-2l3 3V5a1 1 0 0 1 2 0v5-7a1 1 0 0 1 2 0v7-6a1 1 0 0 1 2 0v6-4a1 1 0 0 1 2 0v7q0 4-2 5v3'))
add('flogging', 'Un manche et trois lanières.',
    line('m4 20 6-6 2 2-6 6ZM11 15c0-7 7-3 8-11M11 15c-4-6 7-6 4-12M11 15c6 1 10-4 10-10'))
add('paddling', 'Une paddle, sans texture.',
    line('m5 21-2-2 6-6-1-1a2 2 0 0 1 0-3l6-6a2 2 0 0 1 3 0l4 4a2 2 0 0 1 0 3l-6 6a2 2 0 0 1-3 0l-1-1Z'))
add('caning', 'Une canne souple.', line('M5 21 16 4q2-3 4-1t0 3M4 18l3 2'))
add('blindfold', 'Un bandeau pour les yeux.',
    line('M3 8q9-3 18 0v7q-4 3-7-1h-4q-3 4-7 1ZM1 10h2M21 10h2'))
add('electro', 'Un éclair.', solid('M13 2 5 14h6l-1 8 9-13h-6Z'))
add('wax', 'Une bougie et sa flamme.',
    rect(7, 11, 10, 10), line('M12 2c-5 5-3 7 0 7s5-2 0-7ZM7 14h4v3q2 2 3 0v-3'))
add('orgasm-control', 'Le symbole pause.', rect(6, 4, 4, 16, 1), rect(14, 4, 4, 16, 1))
add('humiliation', 'Une bulle de parole barrée.',
    line('M5 5h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-8l-5 3v-3H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2ZM9 9l6 5M15 9l-6 5'))
add('discipline', 'Une règle graduée.',
    rect(8, 3, 8, 18, 1), line('M8 7h3M8 11h4M8 15h3M8 19h4'))
add('objectification', 'Une étiquette attachée.',
    line('M3 4h9l9 9-8 8-10-10Z'), circle(8, 9, 1))
add('praise', 'Une couronne.',
    line('m3 7 5 4 4-7 4 7 5-4-2 12H5ZM6 16h12'))
add('leather', 'Une casquette à visière.',
    line('M4 11 3 9q9-9 18 0l-1 2ZM5 11v3h14v-3M6 14q6 7 12 0'))
add('rubber', 'Une cagoule de latex, deux ouvertures.',
    line('M6 20V9a6 6 0 0 1 12 0v11Z M8 11h2M14 11h2'))
add('sportswear', 'Un maillot de sport.',
    line('m8 3-5 4 3 4 2-1v11h8V10l2 1 3-4-5-4q-4 5-8 0Z'))
add('uniform', 'Une cravate.', line('M9 3h6l-1 4 2 11-4 4-4-4 2-11ZM10 7h4'))
add('boots', 'Une botte haute.',
    line('M5 3h8v11l6 2q2 1 2 4H5ZM5 17h5M8 6h2M8 9h2'))
add('sneakers', 'Une sneaker de profil.',
    line('M3 9q4 4 7-3l5 6 5 2q2 1 1 5H3ZM3 16h18M11 9l-2 2M14 12l-2 2'))
add('socks', 'Une chaussette.',
    line('M10 3h8v11q0 2-2 3l-7 4q-5 2-6-2-1-2 2-4l5-3ZM10 6h8'))
add('feet', 'Une empreinte adulte allongée, avec cinq orteils et une voûte marquée.',
    line('M9 10c2-2 6-2 7 0 2 3-3 5-3 8 0 5-6 5-6 0-1-3-1-6 2-8Z'),
    circle(17, 4, 1.8), circle(12.4, 3, 1.15), circle(8.5, 4.1, .95),
    circle(5.6, 6.6, .7), circle(4.8, 9.8, .55))
add('underwear', 'Un slip, réduit à sa coupe.', line('M3 6h18v5q-6 1-7 9h-4q-1-8-7-9ZM3 10h18'))
add('hood', 'Une cagoule zippée.',
    line('M6 20V9a6 6 0 0 1 12 0v11ZM9 10h6M12 14v4M10 16h4'))
add('pup', 'Un os.',
    line('M7 9h10c2-5 7-2 4 1 3 3-2 6-4 1H7c-2 5-7 2-4-1-3-3 2-6 4-1Z'))
add('pet', 'Une patte.',
    line('M8 13q4-5 8 0l2 3q2 5-6 3-8 2-6-3Z'), circle(5, 10, 1.5), circle(9, 5, 1.5), circle(15, 5, 1.5), circle(19, 10, 1.5))
add('scenarios', 'Un masque de théâtre.',
    line('M4 5q8 4 16 0v7q0 6-8 9-8-3-8-9ZM7 10h3M14 10h3M9 15q3 3 6 0'))
add('exhibition', 'Un œil.', line('M2 12q10-14 20 0-10 14-20 0Z'), circle(12, 12, 3))
add('suspension', 'Un anneau suspendu.', line('M5 3h14M12 3v9'), circle(12, 16, 5))
add('breath', 'Un souffle.',
    line('M3 9h13q5 0 5-4t-5 0M3 13h10q5 0 5 4t-5 0M3 17h4'))
add('muscle', 'Un bras fléchi.',
    line('M4 16 7 5h5l1 4H9l-1 5q4-4 8-2 5 2 4 7-9 4-16-3Z'))
add('body-hair', 'Trois mèches courbes.',
    line('M5 20c-5-8 7-8 3-16M11 20c-5-8 7-8 3-16M17 20c-5-8 7-8 3-16'))
add('scent', 'Un nez et une trace de parfum.',
    line('M13 3 8 14q-1 3 3 3h2M13 20q4 0 4-3M20 5q-3 2 0 4t0 4'))
add('belly', 'Un torse large, un ventre arrondi et son nombril.',
    line('M8 3Q7 5 4 5l2 5C1 19 5 21 12 21s11-2 6-11l2-5q-3 0-4-2M7 9q2 1 3 0M14 9q1 1 3 0M12 15v1'))
add('neoprene', 'Une combinaison à manches courtes.',
    line('M9 3 3 7l3 4 2-1-1 11h4l1-6 1 6h4l-1-11 2 1 3-4-6-4q-3 3-6 0ZM12 6v5'))
add('lycra', 'Un cuissard.', line('M5 4h14l2 16h-7l-2-9-2 9H3ZM5 7h14'))
add('denim', 'Un jean et ses poches.',
    line('M6 3h12l1 18h-5l-2-11-2 11H5ZM6 6h12M9 6q0 4-3 4M15 6q0 4 3 4'))
add('gloves', 'Un gant.',
    line('M8 21v-4l-4-6q-1-2 1-2l3 3V5a1 1 0 0 1 2 0v5-7a1 1 0 0 1 2 0v7-6a1 1 0 0 1 2 0v6-4a1 1 0 0 1 2 0v7q0 4-2 5v3ZM8 18h6'))
add('gas-mask', 'Un masque à gaz et son filtre.',
    line('M8 20q-4-3-4-10a8 8 0 0 1 16 0q0 7-4 10'), circle(8, 10, 2), circle(16, 10, 2), rect(9, 15, 6, 6, 2))
add('watersports', 'Une goutte.', line('M12 3C10 7 5 11 5 15a7 7 0 0 0 14 0c0-4-5-8-7-12Z'))
add('spit', 'Une goutte projetée.',
    line('M19 8c-4 1-9 2-10 5a4 4 0 0 0 7 4c2-2 2-6 3-9ZM4 7l3 2M8 3l2 3'))
add('messy', 'Une éclaboussure.',
    line('M9 8c-5-8-8-3-4 1-6 2-3 6 1 5-3 7 3 8 5 3 4 7 8 3 4-1 7 1 8-5 2-5 4-6-2-8-5-3Z'))
add('scat', 'Un symbole de matière en trois niveaux.',
    line('M6 15h12a3 3 0 0 1 0 6H6a3 3 0 0 1 0-6ZM7 15q-4-5 2-6h6q6 1 2 6M9 9q6-1 4-6 6 2 2 6'))
add('diaper', 'Une couche, deux attaches.',
    line('M3 7h18l-2 10q-7 7-14 0ZM3 10h4v4H4M21 10h-4v4h3'))
add('pony', 'Une tête de cheval de profil.',
    line('M7 21V11l-3 2-2-4 5-4 1-3 4 4q8 1 8 15ZM8 8h1'))
add('doll', 'Une poupée aux cheveux longs, avec un visage articulé.',
    line('M8 21H3L4 9a8 8 0 0 1 16 0l1 12h-5M7 9q4-1 5-4 2 3 5 4v3q0 5-5 7-5-2-5-7ZM9 11h1M14 11h1M10 15h4M10 15v3M14 15v3'))
add('wrestling', 'Un singlet de lutte à larges emmanchures.',
    line('M5 3h3v3a4 4 0 0 0 8 0V3h3v5l-2 4 2 9h-6l-1-6-1 6H5l2-9-2-4Z'))
add('medical', 'Une croix médicale.', solid('M9 3h6v6h6v6h-6v6H9v-6H3V9h6Z'))
add('chastity', 'Un cadenas fermé.',
    rect(5, 10, 14, 11, 2), line('M8 10V7a4 4 0 0 1 8 0v3M12 14v3'))
add('cbt', 'Un anneau de contrainte.',
    rect(3, 7, 18, 11, 3), circle(12, 12.5, 3.5), line('M3 12.5h5M16 12.5h5'))
add('fisting', 'Un poing fermé.',
    line('M7 21v-4l-3-4V7q0-2 2-2h10q3 0 3 3v6l-3 4v3M8 5v4M12 5v4M16 5v5M4 11l4-2 6 3q1 2-1 3l-4-2'))
add('sounding', 'Deux sondes courbes, à bouts arrondis.',
    line('M6 21V7q0-4 4-4h1v2h-1q-2 0-2 2v14ZM15 21V9q0-4 4-4h1v2h-1q-2 0-2 2v12Z'))
add('enema', 'Une poire et sa canule.',
    line('M14 10V4q0-2 3-2M10 10V6h4M10 10c-8 5-6 11 2 11s10-6 2-11Z'))
add('findom', 'Une carte de paiement.', rect(3, 5, 18, 14, 2), line('M3 10h18M6 15h4'))
add('predicament', 'Une balance en tension.',
    line('M12 3v18M5 21h14M3 7h18M6 7l-4 8h8ZM18 7l-4 8h8Z'))
add('vacuum', 'Un cadre souple et sa valve.',
    rect(5, 3, 14, 18, 1), line('M8 8q4 2 8 0M8 16q4-2 8 0M19 12h3'))
add('straitjacket', 'Une veste aux manches croisées.',
    line('M8 3 4 6 3 17l5 2v2h8v-2l5-2-1-11-4-3q-4 4-8 0ZM6 10l11 7M18 10 7 17'))
add('tickling', 'Une plume.',
    line('M4 21 18 5M7 17C0 7 14 1 21 3c0 8-4 17-14 14ZM11 13h5'))
add('clamps', 'Une pince à ressort.',
    line('M3 13 18 4l3 3-9 14-3-2 4-9-8 5Z'), circle(15.5, 8.5, 1))
add('scratching', 'Trois griffures.',
    line('M7 3 3 18M14 4 9 21M21 6l-5 14'))
add('edging', 'Un sablier.',
    line('M6 3h12M6 21h12M7 3v5l5 4-5 4v5M17 3v5l-5 4 5 4v5'))
add('collar', 'Un collier à anneau.',
    rect(3, 6, 18, 7, 2), circle(12, 16, 4))
add('primal', 'Trois griffes.',
    solid('M7 3 5 16l-3 5 1-10ZM14 2l-2 15-4 5 2-13ZM21 4l-2 13-4 4 2-12Z'))
add('furry', 'Une queue de renard.',
    line('M6 21C-1 7 19 14 18 3c9 15-4 19-12 18ZM6 21l4-4 2 3'))
add('balloon', 'Un ballon et son fil.',
    line('M12 17C2 12 5 3 12 3s10 9 0 14Zm0 0-1 2h2ZM12 19q-3 1 0 3'))
add('toys', 'Un plug, réduit à sa silhouette.',
    line('m10 3-5 10v4h14v-4L14 3ZM10 17v4M14 17v4M7 21h10'))
add('cnc', 'Deux flèches opposées : résistance et accord.',
    line('M3 8h16l-4-4M21 16H5l4 4'))
add('roughhousing', 'Deux poings qui se rencontrent.',
    line('M2 8h5l4 4v5H5l-3-3M22 8h-5l-4 4v5h6l3-3M5 8v4M19 8v4'))
add('submission-wrestling', 'Un tapis de lutte.', rect(3, 3, 18, 18, 1), circle(12, 12, 6), line('M10 12h4'))
add('needle', 'Une aiguille et son chas.',
    line('M3 21 15 4q3-3 5-1t-1 5ZM16 7l2-2'))
add('blood', 'Une poche de prélèvement.',
    rect(6, 5, 12, 14, 2), line('M10 5V2h4v3M12 19v3M9 13h6M12 10v6'))
add('fire', 'Une flamme.',
    line('M12 2c1 7-6 6-6 12a7 7 0 0 0 14 0c0-4-3-6-3-6s1 4-2 4c-2 0 1-6-3-10Z'))
add('harness', 'Un harnais spartiate en H : deux sangles parallèles et une bande de poitrine.',
    line('M4 4q2-2 4 0v6h8V4q2-2 4 0v17h-4v-7H8v7H4ZM4 7h4M16 7h4'))
V4['harness']['reference'] = 'https://www.homeose.fr/harnais/6640-25448-harnais-cuir-noir.html'
