"""KINQ 02: object-led symbols, open curves, consistent optical weight.
References concern the object vocabulary, not copied proprietary icon paths.
"""

def s(d,c='ink',w=4.5):
    return f'<path d="{d}" fill="none" stroke="var(--{c})" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
def f(d,c='ink'):
    return f'<path d="{d}" fill="var(--{c})"/>'
def o(x,y,r,c='ink',w=4.5):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="var(--{c})" stroke-width="{w}"/>'
def dot(x,y,r=2.5,c='ink'):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--{c})"/>'
def box(x,y,w,h,r=3,c='ink',sw=4.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="var(--{c})" stroke-width="{sw}"/>'
def rot(body,a):return f'<g transform="rotate({a} 48 48)">{body}</g>'

V2={}
def add(id,cue,body,symbol,ref=None):V2[id]=dict(cue=cue,body=body,symbol=symbol,reference=ref,version=2)

CAP='https://www.mr-s-leather.com/cruising-cap'
HARNESS='https://www.mr-s-leather.com/bulldog-harness'
PUP='https://www.mr-s-leather.com/neoprene-k9-hood-build-your-own'
ROPE='https://shibaristudy.com/glossary'
GEAR='https://regulation.co.uk/collections/hoods-headgear'
CUFFS='https://regulation.co.uk/collections/bondage-cuffs-collars?order=manufacturer'

# Restraint: actual object construction rather than abstract crossings.
add('bondage','Une sangle refermée sur son anneau d’attache.',s('M21 29Q48 17 75 29V57Q48 72 21 57Z')+s('M21 29Q48 43 75 29')+o(48,67,11)+s('M31 43H40','accent'), 'Sangle & anneau',CUFFS)
add('shibari','Le losange hishi : un code de corde identifiable, sans silhouette de corps.',s('M48 12 25 43 48 73 71 43Z')+s('M15 34 81 34M15 48 81 48')+s('M48 73V86','accent'), 'Losange hishi',ROPE)
add('restraints','Deux manchettes arrondies reliées par une courte chaîne.',rot(box(9,32,25,33,7)+box(62,32,25,33,7)+s('M34 48H62','accent')+s('M17 43H26M70 54H78',w=3.5),-25), 'Manchettes liées',CUFFS)
add('mummification','Un rouleau de bande dont l’extrémité se déroule.',o(35,36,20)+o(35,36,8)+s('M55 36V65Q55 80 78 75L74 58Q63 60 63 48V36')+s('M23 22Q35 16 46 23','accent',3.5), 'Bande enroulée')
# Impact: restrained tool profiles.
add('spanking','Une paume ouverte, sans traits de mouvement décoratifs.',s('M27 72 17 54Q14 47 20 44L31 52V29Q31 22 37 25L40 45V18Q40 12 46 15L49 43 53 20Q54 14 60 18L58 47 65 30Q68 25 73 30L67 60 58 76H35Z')+s('M35 83H56','accent'), 'Paume')
add('flogging','Un manche long, une virole et trois lanières souples.',rot(box(42,13,12,28,3)+s('M42 44Q25 58 24 81M48 44Q43 65 46 84M54 44Q65 60 71 76')+s('M42 39H54','accent'),-22), 'Flogger')
add('paddling','Le profil allongé d’un paddle, réduit à son contour.',rot(s('M39 55Q27 50 29 29 29 11 48 11 67 11 67 29 69 50 57 55H53V82H43V55Z')+dot(48,28,3,'accent'),32), 'Paddle')
add('caning','Une canne souple à poignée courte.',s('M21 79 66 20Q71 12 78 19')+s('M21 79 34 62',w=8)+s('M27 68 31 71','accent',3), 'Canne')
# Sensations: a single tactile or sensory cue.
add('blindfold','Un bandeau enveloppant, fermé sur le nez.',f('M16 34Q48 25 80 34L75 56Q63 66 49 52 35 66 21 56Z')+s('M7 39 16 41M80 41 89 39',w=3.5)+s('M26 39Q46 35 63 38','cut',3), 'Bandeau opaque',GEAR)
add('electro','Une impulsion entre deux électrodes.',o(24,66,10)+o(72,66,10)+s('M24 56V40H36M72 56V40H63')+f('M51 12 36 43H47L43 61 62 31H51L57 12Z'), 'Électrodes')
add('wax','Une bougie courte et une goutte détachée.',s('M30 43V80H57V43Z')+f('M43 12Q29 30 43 35 57 30 43 12Z')+s('M33 43V53Q39 62 43 51V44')+f('M73 53Q60 70 73 75 86 70 73 53Z','accent'), 'Bougie & goutte')
add('orgasm-control','Une clé traversant un anneau : le contrôle est confié.',o(36,38,19)+s('M49 52 75 78M64 67 70 61M72 75 79 69')+dot(36,38,3,'accent'), 'Anneau & clé')
# Psychological categories remain metaphors, identified as such in the inspector.
add('humiliation','Des lèvres et une parole tranchante : symbole du jeu verbal.',s('M13 37 32 26Q42 23 48 30 54 23 64 26L83 37Q67 58 48 58 29 58 13 37Z')+s('M13 37Q48 43 83 37')+s('M56 67 66 79M70 61 83 65','accent',3.5), 'Parole',None)
add('discipline','Une cravache droite et sa palette étroite.',rot(s('M43 17H53L55 32 48 39 41 32Z')+s('M48 39V83')+s('M48 70V84',w=8),32), 'Cravache')
add('objectification','Un corps de mannequin sur son socle.',s('M35 14H61L58 27 69 39 61 64H35L27 39 38 27Z')+s('M48 64V80M31 82H65')+s('M36 48Q48 53 60 48','accent',3.5), 'Mannequin')
add('praise','Un cœur posé dans une main ouverte.',s('M48 44C24 31 32 13 44 22L48 27 52 22C64 13 72 31 48 44Z')+s('M13 67 27 57H49Q57 57 57 64L43 69H64L80 54Q88 56 82 64L67 80H32L20 86')+s('M9 64 23 84','accent'), 'Cœur offert')
# Fetish clothing: outline derives from recognisable garment proportions.
add('leather','La casquette de cruising : calotte basse, bande et visière.',s('M15 38Q19 22 45 21 66 21 81 33L75 47H23Z')+s('M23 47H75V54H23Z')+f('M24 58H74Q59 77 42 71 32 67 24 58Z')+s('M29 42H67','accent',3), 'Casquette de cruising',CAP)
add('rubber','Un catsuit cintré et un zip central : la seconde peau.',s('M37 12H59V23L73 29 82 59 73 62 62 38 59 54 65 84H53L48 63 43 84H31L37 54 34 38 23 62 14 59 23 29 37 23Z')+s('M48 18V45','accent',3.5)+s('M59 31 62 43',w=3), 'Catsuit zippé')
add('sportswear','Un bas de survêtement, deux bandes, une coupe nette.',s('M29 14H67L72 82H55L48 43 41 82H24Z')+s('M29 24H67')+s('M35 29 30 75M61 29 66 75','accent',3.5), 'Track pants')
add('uniform','Une cravate encadrée par deux pointes de col.',s('M20 21 37 15 48 31 59 15 76 21 68 46 48 31 28 46Z')+f('M43 36H53L57 45 51 52 59 76 48 87 37 76 45 52 39 45Z'), 'Col & cravate')
add('boots','Une botte haute de profil avec trois croisements de lacets.',s('M27 13H57L54 52Q61 62 77 65 83 66 83 77H20V62L26 54Z')+s('M20 83H83M37 23 47 29M47 23 37 29M37 36 47 42M47 36 37 42','accent',3.5)+s('M21 77V84M79 77V84'), 'Botte lacée')
add('sneakers','Le profil d’une sneaker et sa semelle à bulle.',s('M13 42 27 38 39 46 52 34 64 52 81 59Q87 64 83 75H12Z')+s('M13 65H81M42 45 47 50M49 41 54 47',w=3.5)+s('M30 70H48','accent',3), 'Sneaker')
add('socks','Une chaussette montante à deux bandes.',s('M41 13H66V57L37 81Q24 89 17 78 12 71 20 64L41 46Z')+s('M42 24H65M42 33H65','accent',3.5), 'Chaussette haute')
add('feet','Un pied en profil, courbe du talon et voûte plantaire.',s('M36 13 32 44Q31 53 20 66 11 79 25 81H75Q85 79 80 73L61 65Q53 58 56 44L61 15')+s('M32 73Q44 65 58 71','accent',3.5), 'Pied de profil')
add('underwear','Un jockstrap, son triangle frontal et ses deux sangles.',s('M16 20H80V32H16Z')+s('M24 32Q30 59 48 70 66 59 72 32M19 34 24 78 40 66M77 34 72 78 56 66')+s('M33 26H63','accent',3), 'Jockstrap')
add('hood','Une cagoule à œillets ovales et ouverture ronde.',s('M48 12Q24 12 24 38L28 65Q34 81 48 84 62 81 68 65L72 38Q72 12 48 12Z')+f('M31 39Q36 32 42 39 36 45 31 39ZM54 39Q60 32 65 39 60 45 54 39Z')+o(48,63,8,'accent',3.5), 'Cagoule',GEAR)
add('pup','Un masque K9 de trois quarts : oreille pliée et museau saillant.',s('M28 31 24 13 40 23Q52 17 65 29L72 42 85 49 83 62 64 70 58 82H32L23 66 18 47Z')+s('M28 31 34 20M65 48 56 59 63 70M31 82H56',w=3.5)+f('M39 39 51 37 48 45H40Z')+f('M73 47 84 50 79 57H72Z')+dot(38,64,3,'accent'), 'Masque K9',PUP)
add('pet','Un collier et sa médaille, sans personnage animal.',s('M15 27Q48 17 81 27V43Q48 54 15 43Z')+s('M15 27Q48 38 81 27')+o(48,65,15)+s('M48 50V45')+dot(48,65,3,'accent'), 'Collier à médaille',CUFFS)
add('scenarios','Deux masques de rôle, réduits à leurs contours.',s('M17 20 63 25 58 56Q36 69 22 45Z')+s('M36 45 80 32 81 61Q71 81 53 80Z')+s('M27 34 34 36M45 37 52 39M48 57 55 54M66 51 73 48','accent',3.5), 'Masques de rôle')
add('exhibition','Un œil dans une ouverture de rideau.',s('M22 15Q38 36 22 80M74 15Q58 36 74 80')+s('M27 48Q48 26 69 48 48 70 27 48Z')+o(48,48,7,'accent'), 'Œil entre les rideaux')
add('suspension','Un anneau suspendu et deux cordes tendues.',o(48,22,10)+s('M48 33 23 71M48 33 73 71')+s('M23 71Q48 84 73 71','accent',5), 'Anneau de suspension')
add('breath','Un masque couvrant bouche et nez, raccord au centre.',s('M40 20H56L72 46 66 72Q48 84 30 72L24 46Z')+s('M29 36 16 28M67 36 80 28M30 66 17 74M66 66 79 74',w=3.5)+o(48,57,12)+s('M43 57H53','accent'), 'Masque respiratoire',GEAR)
# Bodies stay non-graphic: a curve or crop rather than a caricature.
add('muscle','Un bras fléchi et une seule courbe de biceps.',s('M15 66 25 46 29 19 44 16 52 28 42 37 38 54Q56 36 70 51L81 67Q60 84 37 77Z')+s('M43 57Q51 50 58 57','accent',3.5), 'Biceps')
add('body-hair','Une aisselle suggérée par le bras levé et trois traits.',s('M26 82V58L15 36 28 15H46V25H35L28 37 40 50 57 39 76 51 70 82')+s('M38 59 45 65M44 53 52 60M51 48 59 55','accent',3.5), 'Aisselle')
add('scent','Un nez de profil et deux volutes : l’odeur comme signe.',s('M55 16Q48 30 42 38L34 51Q32 56 43 57L51 55M51 68Q60 73 67 65')+s('M22 71Q13 64 22 57M15 44Q6 37 15 30','accent',3.5), 'Nez & odeur')
add('belly','Une courbe de ventre et une ceinture basse.',s('M31 15Q39 31 26 44 14 58 25 76H72Q82 56 68 43 57 31 65 15')+s('M25 76Q48 83 72 76')+s('M44 55Q48 59 52 55','accent',3.5), 'Ventre & ceinture')
add('neoprene','Une combinaison à manches courtes et panneau d’épaule.',s('M37 13H59L63 24 77 30 71 50 62 44 65 82H53L48 58 43 82H31L34 44 25 50 19 30 33 24Z')+s('M33 26 39 36H57L63 26','accent')+s('M48 17V31',w=3), 'Shorty néoprène')
add('lycra','Un singlet : décolleté plongeant et deux jambes courtes.',s('M27 13H37V30Q48 44 59 30V13H69L64 46 73 81H55L48 63 41 81H23L32 46Z')+s('M30 56Q48 63 66 56','accent',3.5), 'Singlet')
add('denim','Une poche de jean, couture et deux rivets.',s('M22 25H74L69 68 48 80 27 68Z')+s('M27 36H69M29 43 47 53 67 43','accent',3.5)+dot(30,31,2)+dot(66,31,2), 'Poche de jean')
add('gloves','Un gant à poignet long et pouce décalé.',s('M30 83 34 62 23 45 16 39Q13 33 19 32L31 40V21Q31 15 37 19L40 37V16Q44 10 48 17V39L54 21Q57 15 61 21L58 43 65 29Q71 25 72 32L65 61 60 66 64 83Z')+s('M34 72H61','accent'), 'Gant long')
add('gas-mask','Deux oculaires ronds et une cartouche basse.',s('M31 17Q48 10 65 17L75 34 70 64 59 78H37L26 64 21 34Z')+o(35,36,9)+o(61,36,9)+o(48,64,12)+s('M42 64H54','accent',3.5), 'Masque à gaz',GEAR)
# Matter: iconic sign, no literal scene.
add('watersports','Une goutte, une onde. Aucun détail ajouté.',s('M48 14Q21 44 26 61 33 82 53 77 81 68 65 39Z')+s('M30 85H66','accent',3.5), 'Goutte & onde')
add('spit','Des lèvres entrouvertes et une goutte.',s('M13 32 33 23Q41 22 48 28 55 22 63 23L83 32Q66 50 48 50 30 50 13 32Z')+s('M14 32Q48 38 82 32',w=3.5)+f('M63 59Q49 78 63 82 77 78 63 59Z','accent'), 'Lèvres & goutte')
add('messy','Une flaque irrégulière et deux projections.',s('M25 37Q18 22 35 25L45 31Q59 16 64 29L63 41Q85 38 80 54L65 60Q68 82 52 76L39 66Q20 82 17 65L23 53Q8 42 25 37Z')+dot(77,20,3,'accent')+dot(13,80,3), 'Éclaboussure')
add('scat','Trois couches de matière, sous forme de signe conventionnel.',s('M39 34Q37 21 52 16 51 29 61 34M31 50Q21 39 39 34H59Q74 38 65 50M27 67Q13 56 31 50H65Q82 56 70 67M24 67H72Q84 78 70 82H25Q12 79 24 67Z'), 'Matière')
add('diaper','Une protection adulte : deux attaches latérales, forme sobre.',s('M18 26H78L74 61 60 77H36L22 61Z')+s('M19 31H34V44H21M77 31H62V44H75')+s('M27 57Q37 57 40 75M69 57Q59 57 56 75','accent',3.5), 'Protection à attaches')
add('pony','Un mors articulé et ses deux anneaux.',o(18,47,11)+o(78,47,11)+s('M29 47 42 42 54 52 67 47')+o(48,47,6,'accent',3.5), 'Mors')
add('doll','Un masque lisse, traits neutres et articulation au cou.',s('M48 13Q23 13 25 39L29 62Q36 78 48 78 60 78 67 62L71 39Q73 13 48 13Z')+s('M33 40H41M55 40H63M42 59H54',w=3.5)+o(48,85,5,'accent',3), 'Masque articulé')
# Wrestling: familiar equipment and simplified grappling gestures.
add('wrestling','Un casque de lutte à deux protections d’oreilles.',s('M27 43V31Q27 13 48 13 69 13 69 31V43M32 69Q48 89 64 69')+box(17,36,20,30,9)+box(59,36,20,30,9)+s('M38 24H58','accent',3.5), 'Casque de lutte')
add('medical','Un stéthoscope, symbole médical immédiatement lisible.',s('M24 17V39Q24 56 43 56 62 56 62 39V17M43 56V67Q43 83 63 82 77 81 77 67')+o(77,57,10)+s('M24 16V22M62 16V22','accent',7), 'Stéthoscope')
add('chastity','Une cage ajourée fermée par un petit verrou.',s('M29 37H67L62 68Q48 86 34 68Z')+s('M40 46 42 70M54 46 53 70',w=3.5)+box(37,21,22,16,3)+s('M42 21V16Q48 8 54 16V21')+dot(48,29,2,'accent'), 'Cage & verrou')
add('cbt','Un anneau de contrainte et deux poids, sans anatomie.',o(48,27,15)+s('M40 41 33 61M56 41 63 61')+o(30,71,10)+o(66,71,10)+s('M43 27H53','accent',3.5), 'Anneau lesté')
add('fisting','Un poing fermé, au rebord de gant discret.',s('M28 46V28Q31 21 38 27 43 19 50 26 58 21 63 29 73 26 75 35V52L62 68V81H32V67L20 53Q16 43 24 40Z')+s('M38 29V41M50 29V41M63 32V42',w=3.5)+s('M34 74H60','accent',3.5), 'Poing ganté')
add('sounding','Une sonde à embout arrondi, courbe et fine.',s('M38 16V77Q38 86 48 82L56 77V16',w=5)+s('M38 17H56','accent',3.5), 'Sonde double')
add('enema','Une poire et sa canule courbe.',s('M35 37V27Q35 16 49 16H62M43 38V28H62')+s('M43 38Q62 42 64 58 67 81 42 83 17 80 20 59 21 43 35 37Z')+s('M28 59Q25 70 34 75','accent',3.5), 'Poire & canule')
add('findom','Une pièce dans un maillon : argent et emprise.',o(37,57,23)+s('M61 14H72Q83 14 83 26V36Q83 48 72 48H61Q50 48 50 36V26Q50 14 61 14Z')+s('M41 44Q25 44 25 57 25 70 41 70M21 54H38M21 61H36','accent',3), 'Pièce & lien')
add('predicament','Une barre en déséquilibre, tenue à ses deux extrémités.',s('M18 37 78 56M48 48V79M33 80H63M21 38V22M75 55V73')+o(21,16,6,'accent',3.5)+o(75,79,6,'accent',3.5), 'Équilibre sous tension')
add('vacuum','Un cadre de vacuum bed et une membrane aspirée.',box(18,13,60,70,3)+s('M27 24Q48 42 69 24M27 72Q48 54 69 72M27 25Q37 48 27 71M69 25Q59 48 69 71',w=3.5)+s('M78 65H87','accent'), 'Cadre & membrane')
add('straitjacket','Une veste dont les manches se croisent et se ferment.',s('M35 16H61L75 30 69 82H27L21 30Z')+s('M24 39 66 67M72 39 30 67',w=7)+box(42,46,12,12,1,'accent',3)+s('M39 24H57',w=3.5), 'Manches croisées')
add('tickling','Une seule plume effilée.',s('M21 82 67 18M30 68Q17 35 72 12 77 62 30 68Z')+s('M43 40 49 47M52 28 58 35','accent',3.5), 'Plume')
add('clamps','Deux pinces articulées reliées par une chaîne.',s('M17 18 30 46M31 18 18 46M65 18 78 46M79 18 66 46M24 48V62Q24 82 48 82 72 82 72 62V48')+o(24,33,4,'accent',3)+o(72,33,4,'accent',3), 'Pinces reliées')
add('scratching','Trois griffures souples et parallèles.',s('M31 18Q36 43 20 77M50 14Q55 40 39 81M69 18Q74 43 58 77',w=5), 'Griffures')
add('edging','Un pic interrompu juste avant la limite.',s('M15 69H26L39 49 48 57 65 24')+s('M78 18V77')+s('M60 22 68 19 69 28','accent',3.5), 'Seuil interrompu')
add('collar','Un collier à anneau et une laisse retenue en boucle.',s('M13 31Q37 22 61 31V48Q37 58 13 48ZM13 31Q37 42 61 31')+o(37,63,10)+s('M47 64Q77 89 81 54V19Q72 11 70 22V39','accent',4), 'Collier & laisse',CUFFS)
add('primal','Deux crocs aiguisés, signe de l’instinct.',s('M20 25Q48 34 76 25')+f('M24 29 38 32 30 70ZM58 32 72 29 66 70Z')+s('M39 79Q48 82 57 79','accent',3), 'Crocs')
add('furry','Une queue courbe et sa pointe de fourrure.',s('M24 81Q14 58 37 47 64 35 64 14 88 31 75 54 62 74 41 67 30 65 32 81Z')+s('M62 26 72 37 61 41 65 50','accent',3.5), 'Queue touffue')
add('balloon','Un ballon ovale, un nœud et un fil.',s('M48 12Q22 12 23 35 24 56 44 64L40 72H56L52 64Q72 56 73 35 74 12 48 12ZM48 72Q61 82 44 86')+s('M35 23Q29 29 32 38','accent',3.5), 'Ballon')
add('toys','Un plug à base évasée, en contour simple.',s('M48 13Q33 30 29 48 26 61 42 66V74H27V83H69V74H54V66Q70 61 67 48 63 30 48 13Z')+s('M43 32 37 46','accent',3.5), 'Plug')
add('cnc','Deux poignets retenus par un lien central : résistance convenue.',s('M15 15 33 35 43 45 34 55 13 35M81 15 63 35 53 45 62 55 83 35M34 55 25 80M62 55 71 80')+box(36,37,24,22,6,'accent',4), 'Poignets & lien')
add('roughhousing','Deux mains qui se saisissent.',s('M12 34 26 28 42 43 53 33 75 45 84 63 72 71 54 54 42 64 26 55Z')+s('M29 40 44 54M55 44 65 53','accent',3.5), 'Prise de mains')
add('submission-wrestling','Deux bras imbriqués dans une prise au sol.',s('M16 68 34 44 57 44Q75 44 75 62V76H53M20 83H78')+s('M47 22V62H21','accent',6)+o(22,31,9), 'Prise au sol')
add('needle','Une aiguille fine et son embase, sans effet superflu.',rot(s('M48 37V84',w=3)+box(43,14,10,23,2)+s('M41 37H55','accent',3),35), 'Aiguille')
add('blood','Une goutte coupée par une fine lancette.',s('M48 14Q21 44 26 61 33 82 53 77 81 68 65 39Z')+s('M32 66 67 31','cut',9)+s('M32 66 67 31','accent',3.5), 'Goutte & lancette')
add('fire','Une flamme à deux courbes, cœur évidé.',s('M52 13Q60 31 45 42 64 43 70 29 87 56 69 74 48 94 28 72 12 53 33 33 28 51 39 53 54 41 52 13Z')+s('M47 62Q37 72 48 79','accent',3.5), 'Flamme')
add('harness','Un harnais bulldog : deux épaules ouvertes, une sangle pectorale.',s('M30 15Q15 24 19 52L26 77 36 73 29 48 39 22ZM66 15Q81 24 77 52L70 77 60 73 67 48 57 22Z')+s('M31 49H65M33 58H63')+o(48,62,7,'accent',3.5), 'Harnais bulldog',HARNESS)

assert len(V2)==75
