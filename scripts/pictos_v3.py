"""KINQ / Flat gear. 128-unit masters, deliberate silhouettes and three inks."""

def p(d,c='ink'):
    return f'<path d="{d}" fill="var(--{c})" stroke="none"/>'
def l(d,c='ink',w=7):
    return f'<path d="{d}" fill="none" stroke="var(--{c})" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
def c(x,y,r,color='ink'):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--{color})" stroke="none"/>'
def e(x,y,rx,ry,color='ink'):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="var(--{color})" stroke="none"/>'
def ring(x,y,r,color='muted',w=6):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="var(--{color})" stroke-width="{w}"/>'
def r(x,y,w,h,rad=3,color='ink'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rad}" fill="var(--{color})" stroke="none"/>'
def rot(body,a):return f'<g transform="rotate({a} 64 64)">{body}</g>'

V3={}
def add(id,body,cue=None,symbol=None):
    V3[id]=dict(body=body,viewBox='0 0 128 128',version=3)
    if cue:V3[id]['cue']=cue
    if symbol:V3[id]['symbol']=symbol

# The foundation: asymmetry, ample negative space, no outline around filled shapes.
add('leather',
    p('M49 70 97 59Q102 71 114 87 115 93 103 95 77 98 49 70Z')+
    p('M17 58Q61 49 103 40L103 64Q72 83 25 80Z')+
    p('M19 63Q61 58 103 47V58Q69 76 23 75Z','accent')+
    p('M13 57Q20 43 47 31 82 14 101 29 110 38 100 46 65 64 22 66Q15 65 13 57Z')+
    p('M61 72Q88 76 105 90L95 89Q72 84 61 72Z','muted')+
    r(25,65,9,11,2),
    'Une casquette de cuir de trois quarts : calotte souple, bande acide et visière distincte.', 'Casquette de cruising')

add('harness',
    p('M39 17Q22 20 21 44L26 95 40 90 35 45Q34 35 45 30Z')+
    p('M89 17Q106 20 107 44L102 95 88 90 93 45Q94 35 83 30Z')+
    p('M37 23 61 61 51 70 29 34ZM91 23 67 61 77 70 99 34Z')+
    p('M28 66Q45 61 56 63V77Q41 76 30 81ZM100 66Q83 61 72 63V77Q87 76 98 81Z')+
    ring(64,70,12,'accent',7)+
    r(24,43,17,12,2,'muted')+r(87,43,17,12,2,'muted')+
    r(28,46,9,6,1)+r(91,46,9,6,1),
    'Deux sangles d’épaule, une bande pectorale et un anneau : le harnais reste ouvert et lisible.', 'Harnais bulldog')

add('pup',
    p('M31 45 25 14Q28 9 33 16L52 32Q68 25 83 40L99 58 107 72 94 92 78 100 70 114H42L29 99 21 68Z')+
    p('M69 40 77 10Q80 6 85 15L94 46 85 63Z')+
    p('M79 23 85 43 80 52 75 38Z','muted')+
    p('M29 28 41 41 31 49Z','muted')+
    p('M85 64 108 69Q116 76 108 85L94 97 79 94 70 82Z','accent')+
    p('M101 68 112 73 109 81 99 79Z')+
    p('M46 55Q52 46 64 50L61 61Q51 65 46 55Z','cut')+
    c(83,87,4)+p('M42 103 73 102 68 111H45Z','muted'),
    'Un masque K9 de trois quarts, avec un vrai museau saillant et des oreilles construites.', 'Masque K9')

add('boots',
    p('M35 13H74L71 62Q75 74 94 79 107 81 108 97H26V76L34 64Z')+
    p('M29 17H36V35H29Z','muted')+
    p('M28 97H110V108H96V113H83V108H61V113H48V108H26Z')+
    l('M47 29H61M47 43H61M46 57H60','accent',5)+
    p('M37 71Q51 75 57 94H48Q44 81 33 81Z','muted'),
    'Une botte montante, trois lacets nets et une semelle crantée.', 'Botte lacée')

add('sneakers',
    p('M15 66 20 46Q24 40 29 47L42 59 62 42 79 63 101 73Q112 76 113 90L103 98H16Z')+
    p('M17 83Q37 90 55 86L84 83 112 85 114 96Q98 108 66 100L41 97 17 99 12 94Z','accent')+
    p('M41 60 52 56 78 73 67 80Z','muted')+
    l('M57 52 66 61M64 47 73 56','cut',4)+
    p('M24 68Q36 69 43 80H21Z','muted'),
    'Une sneaker de profil : semelle acide, panneau latéral et deux lacets.', 'Sneaker')

add('shibari',
    ring(63,52,30,'ink',14)+
    p('M45 71 59 79 36 111 24 103ZM72 71 61 83 96 105 104 92Z')+
    p('M44 75 72 65 81 78 50 89Z','accent')+
    l('M51 67 73 87','cut',7)+l('M51 67 73 87','ink',5),
    'Une boucle de corde, un croisement noué et deux brins libres. La structure se lit sans déchiffrer un symbole abstrait.', 'Corde nouée')

add('underwear',
    p('M24 43H104L98 65 82 97Q64 105 46 97L30 65Z')+
    p('M24 51 42 57 47 83 40 86 31 66ZM104 51 86 57 81 83 88 86 97 66Z','cut')+
    p('M45 50H83Q80 83 64 105 48 83 45 50Z')+
    p('M21 27Q64 37 107 27L103 47Q64 57 25 47Z','accent')+
    e(64,27,43,8)+p('M58 58H63L59 86 56 80Z','muted'),
    'Un jockstrap de face : ceinture large, poche centrale et deux ouvertures latérales.', 'Jockstrap')

add('gas-mask',
    p('M40 19Q64 9 88 19L105 42 100 84 80 110H48L28 84 23 42Z')+
    r(18,60,13,23,5,'muted')+r(97,60,13,23,5,'muted')+
    p('M35 40Q50 32 57 43L54 60Q39 71 33 53Z','muted')+
    p('M93 40Q78 32 71 43L74 60Q89 71 95 53Z','muted')+
    c(64,86,23,'accent')+c(64,86,16)+
    l('M55 80H73M55 91H73','accent',4),
    'Deux verres inclinés et un grand filtre frontal : trois masses, aucun décor.', 'Masque à gaz')

add('restraints',
    rot(r(15,24,35,49,8)+r(78,24,35,49,8)+
    e(32.5,28,13,4,'muted')+e(95.5,28,13,4,'muted')+
    r(21,48,23,9,2,'accent')+r(84,48,23,9,2,'accent')+
    l('M43 70 58 86Q64 92 70 86L85 70','muted',7)+
    ring(48,75,7,'muted',5)+ring(80,75,7,'muted',5),-12),
    'Deux manchettes épaisses et une courte chaîne ; le contraste se concentre sur les attaches.', 'Manchettes liées')

add('blindfold',
    l('M27 49Q5 53 20 73L31 76M101 49Q123 53 108 73L97 76','muted',8)+
    p('M24 44Q64 30 104 44L101 72Q96 89 81 83L64 69 47 83Q32 89 27 72Z')+
    p('M33 45Q64 37 95 45L94 51Q64 45 34 51Z','accent'),
    'Un bandeau moulé et ses deux attaches, avec une seule bande d’accent.', 'Bandeau')

add('wax',
    r(36,48,46,62,4,'accent')+e(59,48,23,7,'muted')+
    p('M59 12Q83 38 61 43 40 40 59 12Z')+
    p('M65 50H75V78Q70 89 65 78Z')+
    p('M97 68Q80 89 97 94 112 89 97 68Z'),
    'Une bougie en aplat et une goutte séparée ; la flamme noire reste lisible sur tous les fonds.', 'Cire')

add('discipline',
    rot(p('M55 16Q64 8 73 16L75 35 64 44 53 35Z')+
    r(61,41,6,57,3)+r(57,88,14,24,4,'accent'),35),
    'Une cravache fine, une palette pleine, un manche contrasté.', 'Cravache')

add('rubber',
    p('M47 17H81L84 28 107 38 119 72 105 78 89 50 83 63 91 110H72L64 78 56 110H37L45 63 39 50 23 78 9 72 21 38 44 28Z')+
    p('M30 40 44 34 41 54 29 67 22 63Z','muted')+
    p('M47 23H81V31H47Z','accent')+
    r(61,32,6,29,2,'accent'),
    'Une combinaison ajustée, manches longues, col et zip. Un seul panneau gris dessine la matière.', 'Catsuit')

add('sportswear',
    p('M39 16H91L96 39 84 113H65L67 67 53 113H33L41 48Z')+
    p('M40 16H91V29H39Z','muted')+
    p('M46 36 52 38 44 105H38ZM80 35 86 37 78 105H72Z','accent')+
    l('M61 24 58 37M67 24 70 35','cut',3),
    'Un pantalon de survêtement légèrement décalé, ceinture large et deux bandes latérales.', 'Track pants')

add('uniform',
    p('M36 22 55 17 64 33 73 17 92 22 111 42 98 59 89 51V110H39V51L30 59 17 42Z')+
    p('M36 22 55 17 64 33 47 50ZM92 22 73 17 64 33 81 50Z','muted')+
    p('M59 36H69L72 45 68 51 76 87 64 98 52 87 60 51 56 45Z','accent')+
    r(78,59,11,5,0,'muted'),
    'Une chemise d’uniforme, deux pointes de col et une cravate centrale.', 'Uniforme')

add('socks',
    p('M53 15H87V66L53 107Q40 120 25 107 14 97 26 85L50 61Z')+
    r(53,24,34,7,0,'accent')+r(53,37,34,6,0,'accent')+
    p('M26 85 42 102 35 113Q20 108 21 96Z','muted')+
    p('M72 70 87 66 69 88 61 80Z','muted'),
    'Une chaussette haute avec deux bandes et un talon renforcé.', 'Chaussette haute')

add('hood',
    p('M64 12Q33 12 30 43L34 79Q40 102 64 116 88 102 94 79L98 43Q95 12 64 12Z')+
    p('M43 16Q29 38 35 70L44 82 40 49Q40 27 52 15Z','muted')+
    e(48,53,9,6,'cut')+e(80,53,9,6,'cut')+
    r(49,84,30,6,3,'accent')+
    p('M58 79H62V94H58ZM67 79H71V94H67Z'),
    'Une cagoule pleine, deux œillets et une bouche zippée, sans expression de personnage.', 'Cagoule zippée')
add('denim',
    p('M35 14H89L93 111H72L65 64 56 111H35L41 54Z')+
    p('M36 14H89V29H36Z','muted')+
    l('M46 31Q47 47 37 51M77 31Q76 47 90 51','accent',5)+
    l('M65 29V50','muted',4)+c(47,22,2,'accent')+c(78,22,2,'accent'),
    'Un jean droit, deux poches courbes et une braguette discrète.', 'Jean')
add('lycra',
    p('M36 15H50V37Q64 52 78 37V15H92L85 62 97 110H72L64 83 56 110H31L43 62Z')+
    p('M36 15H43L49 59 38 101H31L43 62ZM85 15H92L85 62 97 110H89L78 60Z','accent')+
    p('M49 66Q64 74 79 66L80 77Q64 83 48 77Z','muted'),
    'Un singlet décolleté, emmanchures ouvertes et panneaux latéraux.', 'Singlet')
add('gloves',
    p('M34 113 41 77 26 53Q21 44 29 40L42 50V27Q42 18 49 22L54 45V17Q58 9 64 17L66 43 72 23Q76 16 82 23L79 48 87 34Q94 30 98 38L87 74 79 83 86 113Z')+
    p('M40 91H82L86 113H35Z','accent')+
    r(48,94,25,8,2),
    'Un gant à manchette longue : la silhouette de la main et une fermeture sobre.', 'Gant long')

# Reworked after the first rendered contact sheet.
add('shibari',
    l('M51 81C23 73 15 43 37 27 54 13 85 18 98 37 115 62 91 83 72 78',w=14)+
    l('M51 81Q62 100 78 76',w=13)+
    l('M61 87 48 108M73 86 91 101',w=10)+
    p('M29 32 34 27 44 38 39 42ZM53 17 59 17 67 31 60 32ZM82 23 88 27 84 42 79 39ZM101 49 101 56 87 59 88 53ZM37 72 30 67 36 55 42 61Z','muted')+
    p('M50 75 72 67 82 83 61 93Z','accent')+
    l('M61 77 69 89',w=3.5),
    'Une corde lovée, une ligature contrastée et deux brins courts.', 'Corde nouée')
add('underwear',
    p('M23 39 34 38 43 91Q47 98 55 94L60 102Q44 115 34 100ZM105 39 94 38 85 91Q81 98 73 94L68 102Q84 115 94 100Z')+
    p('M45 45H83Q81 85 64 109 47 85 45 45Z')+
    p('M21 27Q64 37 107 27L103 47Q64 57 25 47Z','accent')+
    e(64,27,43,8)+p('M56 59H61L59 84 54 74Z','muted'),
    'Un jockstrap de face : ceinture large, poche centrale et deux sangles continues.', 'Jockstrap')

add('bondage',
    p('M21 34Q64 19 107 34V69Q64 88 21 69Z')+
    e(64,34,43,11,'muted')+e(64,33,32,6,'cut')+
    p('M25 47Q64 60 103 47V61Q64 75 25 61Z','accent')+
    ring(64,85,16,'ink',9)+r(59,60,10,24,3),
    'Une large sangle fermée et un anneau de retenue. Sa forme horizontale la distingue des manchettes.', 'Sangle à anneau')
add('mummification',
    p('M32 28Q45 13 64 20L93 35V74Q77 62 62 70L59 111 40 102 39 58Z')+
    e(43,43,22,27)+e(43,43,13,17,'accent')+e(43,43,6,9)+
    p('M59 76Q75 70 93 81L84 105 62 111Z','muted'),
    'Un rouleau de bande et une large portion déroulée, en trois plans francs.', 'Bande de contrainte')
add('spanking',
    p('M38 97 23 69Q18 59 26 53L40 63V35Q40 26 47 30L52 52V23Q57 16 62 25L65 50 73 30Q78 24 83 32L80 56 90 43Q96 39 100 47L88 81 76 103H45Z')+
    p('M39 96H80L78 112H41Z','accent')+
    l('M18 34 25 41M105 25 98 33','muted',6),
    'Une main ouverte, poignet acide et deux petits signes de contact.', 'Paume')
add('flogging',
    rot(r(56,13,16,37,5)+r(53,43,22,11,3,'accent')+
    l('M57 55Q36 79 28 106M62 57Q57 89 48 114M69 57Q80 83 72 109M74 55Q94 79 98 98',w=8),-22),
    'Un manche compact et quatre lanières séparées, avec un mouvement souple.', 'Flogger')
add('paddling',
    rot(r(42,13,44,63,18)+r(56,66,16,45,5)+
    r(44,19,7,45,3,'muted')+c(64,31,4,'accent')+c(64,45,4,'accent')+c(64,59,4,'accent'),28),
    'Une palette pleine à trois perforations, manche long et profil incliné.', 'Paddle')
add('caning',
    l('M23 108 86 24Q93 16 101 24',w=6)+
    l('M23 108 40 85',w=14)+
    l('M32 88 40 94','accent',5),
    'Une canne longue et fine, munie d’une poignée courte.', 'Canne')
add('electro',
    l('M30 91V70Q30 55 50 57M98 91V70Q98 55 80 57','muted',6)+
    c(30,96,16)+c(98,96,16)+c(30,96,6,'accent')+c(98,96,6,'accent')+
    p('M65 13 43 58H59L53 82 87 39H68L78 13Z','accent'),
    'Deux électrodes rondes encadrent une impulsion centrale.', 'Électrodes')
add('orgasm-control',
    ring(52,53,29,'ink',13)+
    rot(r(72,56,10,48,2)+r(73,88,22,8,2)+r(73,74,18,8,2),-38)+
    c(52,53,10,'accent'),
    'Un anneau et une clé allongée pour symboliser le contrôle confié.', 'Anneau & clé')
add('humiliation',
    p('M18 36Q39 33 48 24 58 20 64 30 70 20 80 24 89 33 110 36L88 52H40Z')+
    p('M25 57H103Q85 83 64 82 43 83 25 57Z')+
    p('M71 91 91 99 83 111 67 101Z','accent'),
    'Des lèvres et un éclat de parole : une métaphore du jeu verbal.', 'Parole')
add('objectification',
    p('M47 17H81L78 35 92 50 82 84H46L36 50 50 35Z')+
    p('M48 58Q64 64 80 58L77 73H51Z','accent')+
    r(60,83,8,21,2,'muted')+r(39,105,50,8,3),
    'Un mannequin réduit à son buste et son pied : la fonction devient le signe.', 'Mannequin')
add('praise',
    p('M64 61C21 39 38 12 56 26L64 35 72 26C90 12 107 39 64 61Z','accent')+
    p('M16 86 34 76H57Q70 76 70 84L53 90H83L104 72Q114 76 106 86L87 105H44L28 113Z')+
    p('M9 81 24 75 38 105 27 115Z','muted'),
    'Un cœur franc au-dessus d’une main ouverte, avec deux silhouettes distinctes.', 'Cœur offert')
add('feet',
    p('M45 46Q70 33 82 48 89 60 74 78 68 86 74 108H44Q30 92 34 75Z')+
    e(83,28,12,15)+e(58,24,8,10)+e(40,30,7,8)+e(28,44,6,7)+e(24,60,5,6)+
    p('M55 64Q47 83 55 96H46Q37 80 48 63Z','accent'),
    'Une empreinte asymétrique, cinq orteils et un creux de voûte plantaire.', 'Empreinte')
add('neoprene',
    p('M46 16H82L87 29 107 40 98 68 85 60 89 109H70L64 82 58 109H39L43 60 30 68 21 40 41 29Z')+
    p('M42 28 49 43H79L86 28 98 35 84 58H44L30 35Z','muted')+
    r(60,18,8,38,2,'accent'),
    'Un shorty à manches courtes avec un large empiècement d’épaule.', 'Shorty néoprène')
add('pet',
    p('M19 29Q64 14 109 29V53Q64 70 19 53Z')+
    e(64,29,45,10,'muted')+e(64,27,33,5,'cut')+
    c(64,89,23,'accent')+r(60,58,8,18,2)+
    p('M52 99Q51 88 64 84 77 88 76 99Z')+c(52,81,4)+c(64,76,4)+c(76,81,4),
    'Un collier large et une médaille à empreinte, distinct du masque puppy.', 'Collier à médaille')
add('scenarios',
    p('M17 21 77 27 72 65Q46 85 23 59Z','muted')+
    p('M45 44 111 28 104 86Q85 119 57 99Z')+
    p('M57 59 72 61 68 70 56 68ZM84 54 99 49 96 59 84 64Z','accent')+
    l('M72 86Q83 94 91 81','muted',5),
    'Deux masques superposés ; une seule expression, découpée en vert.', 'Masques de rôle')
add('exhibition',
    p('M17 17H43L35 72 43 111H17ZM111 17H85L93 72 85 111H111Z')+
    p('M33 65Q64 32 95 65 64 98 33 65Z','accent')+
    c(64,65,13)+c(68,61,4,'cut'),
    'Un regard entre deux pans de rideau : voir et être vu.', 'Œil & rideaux')
add('suspension',
    ring(64,29,16,'ink',10)+
    l('M61 46 28 91M67 46 100 91',w=7)+
    l('M28 91Q64 115 100 91','accent',13),
    'Un anneau porteur, deux lignes tendues et un support suspendu.', 'Anneau de suspension')
add('breath',
    p('M52 20H76L99 55 90 97Q64 116 38 97L29 55Z')+
    l('M38 39 20 32M90 39 108 32M35 81 20 97M93 81 108 97','muted',7)+
    c(64,75,22,'accent')+c(64,75,12)+
    r(57,46,14,8,3,'muted'),
    'Un masque respiratoire sans oculaires, pour le distinguer du masque à gaz.', 'Masque respiratoire')

add('muscle',
    p('M17 86 32 53 37 20 57 15 71 32 55 44 52 66Q76 44 94 68L112 90Q86 115 51 105Z')+
    p('M36 21 57 15 69 29 51 37 36 33Z','accent')+
    l('M57 74Q70 63 80 75','muted',6),
    'Un bras fléchi, une masse de biceps lisible et un seul pli.', 'Biceps')
add('body-hair',
    p('M34 110V77L20 48 35 17H63V32H46L38 49 53 65 77 49 106 66 96 110Z')+
    p('M38 49 53 65 63 58 75 74 54 91 43 80Z','muted')+
    l('M52 72 58 78M60 65 67 72M68 59 75 66','accent',4),
    'Un bras levé, une aisselle en aplat et trois signes de pilosité.', 'Aisselle')
add('scent',
    p('M71 18Q66 41 56 51L46 67Q43 75 60 75L72 71 71 83 89 84 89 105H73Q65 94 63 86H54Q29 84 37 67L50 47 55 18Z')+
    l('M24 50Q13 43 24 32M27 87Q16 80 27 69','accent',6),
    'Un nez de profil et deux volutes : un signe olfactif, distinct des gouttes.', 'Odeur')
add('belly',
    p('M43 17H85L82 39Q112 63 98 95H30Q16 63 46 39Z')+
    p('M43 37Q27 63 34 82L44 89Q33 64 53 40Z','muted')+
    p('M29 98Q64 110 99 98V112H29Z')+
    r(54,98,20,17,3,'accent')+r(60,102,8,9,1)+
    l('M58 71Q64 77 70 71','muted',4),
    'Un ventre arrondi et une ceinture basse, sans caricature de personnage.', 'Ventre & ceinture')
add('watersports',
    p('M64 13Q35 48 30 69 23 99 54 108 83 118 97 90 108 66 64 13Z')+
    p('M46 64Q36 85 50 94L58 90Q44 80 52 67Z','accent')+
    l('M34 116H94','muted',5),
    'Une goutte étirée et une onde basse.', 'Goutte & onde')
add('spit',
    p('M14 37 41 21Q52 16 64 30 76 16 87 21L114 37 86 52H42Z')+
    p('M24 58H104Q81 85 64 82 47 85 24 58Z')+
    p('M94 75Q72 101 93 110 116 102 94 75Z','accent'),
    'Des lèvres en deux aplats et une goutte décalée.', 'Lèvres & goutte')
add('messy',
    p('M48 35Q33 9 23 25 20 37 36 49 15 44 14 59 17 73 38 69 22 94 39 104 54 111 63 85 73 109 91 100 103 90 82 74 110 81 114 62 116 43 86 48 106 27 93 19 76 14 66 38Z')+
    p('M50 53Q65 38 79 56 88 74 65 80 40 78 50 53Z','accent')+
    c(17,101,5,'muted')+c(110,22,4,'muted'),
    'Une tache organique, un cœur acide et deux projections isolées.', 'Éclaboussure')
add('scat',
    p('M50 40Q45 23 66 16 62 31 81 40L76 50H45Z')+
    p('M40 55H83Q99 62 88 76H34Q24 62 40 55Z')+
    p('M29 81H93Q112 91 98 108H28Q10 95 29 81Z')+
    r(48,63,29,5,2,'accent'),
    'Un signe de matière en trois strates, sans représentation de scène.', 'Matière')
add('diaper',
    p('M26 28H102L96 78Q87 96 73 110H55Q40 102 32 78Z')+
    p('M26 28H102L100 42H28Z','muted')+
    r(23,43,27,20,4,'accent')+r(78,43,27,20,4,'accent')+
    p('M34 78Q49 76 54 103L44 98ZM94 78Q79 76 74 103L84 98Z','muted'),
    'Une protection adulte structurée par sa ceinture et deux larges attaches.', 'Protection à attaches')
add('pony',
    ring(25,64,16,'ink',9)+ring(103,64,16,'ink',9)+
    l('M41 64 55 57 73 71 87 64',w=10)+
    ring(64,64,9,'accent',6)+
    p('M19 15H30V44H19ZM98 15H109V44H98Z','muted'),
    'Un mors articulé suspendu à deux courroies, différent du masque K9.', 'Mors')
add('doll',
    p('M64 15Q33 15 32 45L37 77Q43 99 64 109 85 99 91 77L96 45Q95 15 64 15Z')+
    p('M35 47Q64 28 93 47L89 28Q64 4 39 28Z','muted')+
    r(42,58,13,5,2,'cut')+r(73,58,13,5,2,'cut')+
    r(56,84,16,5,2,'accent')+ring(64,114,5,'accent',3),
    'Un masque inexpressif, une bouche courte et une articulation au cou.', 'Masque articulé')
add('wrestling',
    l('M36 48V34Q36 16 64 16 92 16 92 34V48',w=11)+
    r(21,43,28,46,12)+r(79,43,28,46,12)+
    r(30,53,10,26,5,'accent')+r(88,53,10,26,5,'accent')+
    l('M42 94Q64 118 86 94','muted',9),
    'Un casque de lutte à deux protections d’oreilles et mentonnière.', 'Casque de lutte')
add('medical',
    l('M28 24V48Q28 70 52 70 76 70 76 48V24',w=8)+
    l('M52 70V86Q52 110 80 108 102 106 102 87','muted',8)+
    r(22,16,13,22,5,'accent')+r(69,16,13,22,5,'accent')+
    c(102,76,15)+c(102,76,7,'accent'),
    'Un stéthoscope à deux embouts et pavillon contrasté.', 'Stéthoscope')
add('chastity',
    p('M35 45H93L86 94Q64 119 42 94Z')+
    l('M49 57 52 92M64 57V100M79 57 76 92','cut',6)+
    r(47,27,34,24,5,'accent')+
    l('M54 27V20Q64 8 74 20V27',w=6)+
    c(64,38,4),
    'Une cage ajourée, trois ouvertures régulières et un petit verrou.', 'Cage & verrou')
add('cbt',
    ring(64,35,23,'ink',10)+
    l('M49 56 43 82M79 56 85 82','muted',7)+
    c(39,97,18)+c(89,97,18)+
    r(34,80,10,8,2,'accent')+r(84,80,10,8,2,'accent'),
    'Un anneau portant deux poids, sans détail anatomique.', 'Anneau lesté')
add('fisting',
    p('M36 57V33Q40 23 51 31 58 21 68 31 81 24 87 36 99 32 102 46V68L86 90V112H43V92L26 72Q19 59 29 52Z')+
    l('M51 37V54M68 36V54M85 41V55','cut',5)+
    p('M42 99H86V113H42Z','accent')+
    p('M27 58 39 67 46 76 39 81 27 69Z','muted'),
    'Un poing fermé, articulations en réserve et manchette acide.', 'Poing ganté')
add('sounding',
    l('M46 20V99Q46 114 63 111L82 103V20',w=10)+
    l('M47 20H81','muted',7)+
    r(39,19,14,16,6,'accent')+r(75,19,14,16,6,'accent'),
    'Une sonde double à extrémités arrondies, représentée comme un objet technique.', 'Sonde double')
add('enema',
    p('M52 50V28Q52 16 66 16H95V28H69V51Z')+
    p('M48 48Q26 59 25 84 24 111 62 116 97 111 98 84 96 57 74 48Z','accent')+
    r(48,42,29,14,4)+
    p('M38 72Q30 93 48 104L52 99Q39 89 44 75Z','muted'),
    'Une poire souple, une bague de raccord et une canule courbe.', 'Poire & canule')
add('findom',
    c(51,76,34)+
    p('M58 53Q33 49 31 72 29 96 57 98V89Q39 92 39 76 39 59 58 62Z','accent')+
    r(27,68,28,5,1,'accent')+r(27,79,25,5,1,'accent')+
    l('M82 17Q70 17 70 31V48Q70 60 84 60 98 60 98 46V31Q98 17 86 17','muted',9),
    'Une pièce et un maillon, pour distinguer argent et simple verrou.', 'Pièce & lien')
add('predicament',
    p('M64 56 88 105H40Z')+
    l('M24 42 104 66',w=11)+
    l('M28 43V25M98 65V92','muted',6)+
    ring(28,20,10,'accent',6)+ring(98,103,10,'accent',6),
    'Un point d’équilibre, une barre oblique et deux attaches opposées.', 'Équilibre contraint')

add('vacuum',
    r(23,13,82,102,5)+r(32,22,64,84,2,'muted')+
    p('M36 27 62 43 92 27 81 63 92 100 62 85 36 100 46 63Z')+
    p('M54 54 64 64 76 52 70 68 61 73Z','accent')+
    r(104,82,12,10,3),
    'Un cadre épais et une membrane tendue, avec un raccord latéral.', 'Vacuum bed')
add('straitjacket',
    p('M45 18H83L105 39 96 112H32L23 39Z')+
    p('M33 40 94 84 85 98 27 55Z','muted')+
    p('M95 40 34 84 43 98 101 55Z')+
    r(55,62,19,16,2,'accent')+r(60,66,9,8,1)+
    r(48,26,32,8,2,'muted'),
    'Une veste avec deux manches croisées ; une boucle centrale donne la lecture de contrainte.', 'Manches croisées')
add('tickling',
    p('M100 13Q40 10 26 62L34 89Q88 91 100 13Z')+
    p('M100 13 34 89Q87 88 100 13Z','accent')+
    l('M23 112 81 39',w=7)+
    p('M45 43 60 58 53 63 40 50ZM59 27 73 41 68 47 54 34Z','cut'),
    'Une plume asymétrique : deux aplats et une tige nette.', 'Plume')
add('clamps',
    p('M21 16H47L40 62H29ZM81 16H107L99 62H88Z')+
    l('M29 24 21 52M40 24 47 52M89 24 81 52M100 24 107 52','accent',5)+
    l('M34 62V83Q34 111 64 111 94 111 94 83V62','muted',7),
    'Deux pinces fines à ressort reliées par une courbe de chaîne.', 'Pinces reliées')
add('scratching',
    p('M35 16Q51 51 20 110L13 105Q36 54 28 22ZM67 12Q81 52 50 116L42 110Q68 54 59 18ZM99 19Q114 53 81 111L74 104Q100 54 92 24Z')+
    p('M64 33 68 35 65 60 58 73Z','accent'),
    'Trois traces de griffure : même tension, longueurs décalées.', 'Griffures')
add('edging',
    l('M18 98H34L49 66 63 81 89 26',w=11)+
    r(104,20,9,92,3)+
    p('M72 24 95 17 96 42 86 34Z','accent'),
    'Une montée qui approche une limite sans la franchir.', 'Seuil')
add('collar',
    p('M13 31Q46 19 79 31V61Q46 75 13 61Z')+
    e(46,31,33,8,'muted')+e(46,30,23,4,'cut')+
    ring(46,84,14,'accent',7)+r(41,60,10,17,3)+
    l('M60 84Q109 115 110 69V23Q102 11 94 23V45','muted',7),
    'Un collier à anneau et une laisse prolongée par sa poignée.', 'Collier & laisse')
add('primal',
    p('M21 28Q64 46 107 28L99 47Q64 60 29 47Z')+
    p('M30 47 52 53 42 104ZM76 53 98 47 86 104Z')+
    p('M34 49 40 50 38 77Z','accent')+
    p('M88 50 94 48 89 73Z','accent'),
    'Deux crocs longs issus d’une seule courbe, pour l’instinct et la morsure.', 'Crocs')
add('furry',
    p('M29 113Q11 86 35 65L72 43Q85 33 83 13 118 40 102 72 89 99 56 93 41 92 45 112Z')+
    p('M83 13Q112 33 108 53L92 44 83 58 78 46Q89 31 83 13Z','accent')+
    p('M30 81Q23 99 41 109L45 112H29Q16 94 30 81Z','muted'),
    'Une queue en S, avec une pointe de fourrure acide.', 'Queue touffue')
add('balloon',
    p('M64 14Q28 14 29 46 31 76 58 89L53 99H75L70 89Q98 76 99 46 100 14 64 14Z')+
    p('M49 28Q34 37 40 58L47 54Q43 41 55 33Z','accent')+
    l('M64 99Q83 113 60 119','muted',4),
    'Un ballon tendu, un seul reflet en aplat, un nœud court.', 'Ballon')
add('toys',
    p('M64 14Q40 41 34 66 29 83 55 93V101H33V113H95V101H73V93Q99 83 94 66 88 41 64 14Z')+
    p('M56 41Q45 58 45 73L52 79Q51 58 64 44Z','muted')+
    r(33,103,62,10,4,'accent'),
    'Une forme conique, un col dégagé et une base acide nettement visible.', 'Plug')
add('cnc',
    p('M18 18 48 44 62 60 46 76 18 49ZM110 18 80 44 66 60 82 76 110 49Z')+
    p('M47 76 34 109H18L35 68ZM81 76 94 109H110L93 68Z','muted')+
    r(48,48,32,30,9,'accent')+r(56,55,16,16,4),
    'Deux poignets retenus par un lien commun ; la résistance est représentée sans scène.', 'Poignets & lien')
add('roughhousing',
    p('M16 39 38 31 61 53 78 40 104 56 115 81 98 93 74 73 57 88 32 75Z')+
    p('M61 53 78 40 90 46 69 67 57 65Z','accent')+
    l('M39 50 57 67M83 62 98 74','cut',5),
    'Deux mains imbriquées, paumes et poignets regroupés en trois aplats.', 'Prise de mains')
add('submission-wrestling',
    p('M17 94 41 56H76Q104 56 104 83V104H72V91H86V82Q86 73 75 73H50L33 103Z')+
    r(60,22,14,58,5,'accent')+r(23,74,51,14,5,'accent')+
    c(29,39,13)+r(20,114,88,7,2,'muted'),
    'Une prise basse : deux bras imbriqués et une ligne de sol.', 'Prise au sol')
add('needle',
    rot(r(56,14,16,39,4)+r(53,46,22,10,3,'accent')+
    p('M61 56H67L65 109 64 118 62 109Z'),34),
    'Une aiguille seule, avec une embase acide. Pas de détails anatomiques.', 'Aiguille')
add('blood',
    p('M64 13Q35 48 30 69 23 99 54 108 83 118 97 90 108 66 64 13Z')+
    p('M40 88 79 43 89 52 50 99Z','accent')+
    p('M40 88 50 99 33 105Z','muted'),
    'Une goutte et une lancette diagonale, pour la distinguer des autres fluides.', 'Goutte & lancette')
add('fire',
    p('M69 11Q85 36 64 54 89 53 97 33 125 71 99 99 72 129 39 108 9 85 32 49 31 74 48 69 69 49 69 11Z')+
    p('M65 63Q39 88 60 105 88 110 87 79 77 91 70 82Z','accent'),
    'Une flamme asymétrique en deux aplats, sans petits éclats.', 'Flamme')

assert len(V3) == 75, len(V3)

# Optical placement measured on the rendered SVG masters.
# Centres and maximum dimensions use common margins; geometry stays editable.
OPTICAL = {
    'leather': (-1.376, 3.675, 1.02892),
    'harness': (-13.395, -3.721, 1.20930),
    'pup': (-1.722, 3.333, 0.98830),
    'boots': (-6.720, -1.520, 1.04000),
    'sneakers': (-0.235, -10.024, 1.01961),
    'shibari': (0, -1, 1),
    'underwear': (-9.956, -9.956, 1.15556),
    'gas-mask': (-5.333, -3.167, 1.08333),
    'restraints': (4.627, 10.120, 0.95088),
    'blindfold': (-2.452, 0.888, 1.03832),
    'wax': (-10.551, -0.735, 1.06122),
    'discipline': (-7.671, -4.606, 1.10013),
    'rubber': (3.491, 3.964, 0.94545),
    'sportswear': (-5.155, -5.155, 1.07216),
    'uniform': (-6.809, -6.255, 1.10638),
    'socks': (7.650, -3.838, 1.05584),
    'hood': (0.000, 0.000, 1.00000),
    'denim': (-4.619, -3.010, 1.07216),
    'lycra': (-6.063, -4.421, 1.09474),
    'gloves': (0.520, -1.520, 1.04000),
    'bondage': (-13.395, -10.977, 1.20930),
    'mummification': (1.600, -5.516, 1.09474),
    'spanking': (-5.475, -10.523, 1.12967),
    'flogging': (9.439, 8.549, 0.86762),
    'paddling': (0.991, 3.616, 0.97028),
    'caning': (-9.273, -11.636, 1.18182),
    'electro': (-2.560, -1.000, 1.04000),
    'orgasm-control': (-14.562, -2.170, 1.15485),
    'humiliation': (-8.348, -11.658, 1.13043),
    'objectification': (-5.333, -6.417, 1.08333),
    'praise': (2.692, -6.921, 1.03425),
    'feet': (1.600, -2.232, 1.09474),
    'neoprene': (-7.570, -5.892, 1.11828),
    'pet': (-7.570, -9.247, 1.11828),
    'scenarios': (-6.809, -6.558, 1.10638),
    'exhibition': (-6.809, -6.809, 1.10638),
    'suspension': (-9.956, -3.022, 1.15556),
    'breath': (-11.636, -10.750, 1.18182),
    'muscle': (-6.611, -3.248, 1.09474),
    'body-hair': (-6.452, -7.011, 1.11828),
    'scent': (-0.253, -9.517, 1.19540),
    'belly': (-3.918, -6.041, 1.06122),
    'watersports': (-0.576, -1.126, 1.00971),
    'spit': (-2.560, -3.436, 1.04000),
    'messy': (-0.220, 0.862, 1.01836),
    'scat': (-5.625, -6.087, 1.13043),
    'diaper': (-17.171, -23.512, 1.26829),
    'pony': (3.491, 19.091, 0.94545),
    'doll': (0.000, -3.000, 1.00000),
    'wrestling': (-9.956, -6.489, 1.15556),
    'medical': (-12.084, -3.958, 1.09474),
    'chastity': (-7.957, -3.741, 1.12432),
    'cbt': (-0.621, -0.117, 1.00971),
    'fisting': (-10.783, -19.080, 1.19540),
    'sounding': (-7.957, -9.362, 1.12432),
    'enema': (0.053, -4.640, 1.04000),
    'findom': (-0.301, -7.011, 1.11828),
    'predicament': (0.388, 1.903, 1.00971),
    'vacuum': (-6.863, -1.255, 1.01961),
    'straitjacket': (-6.809, -7.915, 1.10638),
    'tickling': (-0.499, -1.462, 1.04877),
    'clamps': (-6.063, -5.516, 1.09474),
    'scratching': (5.656, 0.000, 1.00000),
    'edging': (-7.705, -6.611, 1.09474),
    'collar': (-1.938, 2.351, 1.07216),
    'primal': (-13.395, -15.814, 1.20930),
    'furry': (-3.481, -1.520, 1.04000),
    'balloon': (0.610, -1.867, 0.99048),
    'toys': (-3.232, -2.707, 1.05051),
    'cnc': (-8.348, -7.783, 1.13043),
    'roughhousing': (-4.808, -1.131, 1.05051),
    'submission-wrestling': (-1.131, -11.111, 1.05051),
    'needle': (-2.378, -5.309, 1.05560),
    'blood': (-4.127, -1.848, 1.06523),
    'fire': (-1.728, 1.171, 0.98441),
}
for _id, (_x, _y, _scale) in OPTICAL.items():
    V3[_id]["body"] = f'<g transform="translate({_x} {_y}) scale({_scale})">{V3[_id]["body"]}</g>'
