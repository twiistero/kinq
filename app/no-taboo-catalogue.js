export const historicArticles = [
  {slug:'premiers-pas',title:'Curieux, mais pas sûr de toi ? Tu es au bon endroit.',category:'Premiers pas',summary:'Une première porte pour explorer à ton rythme.'},
  {slug:'parler-de-ses-limites',title:'Parler de ses limites sans casser le feeling.',category:'Entre nous',summary:'Trouver les mots pour dire ce qui te va, et ce qui ne te va pas.'},
  {slug:'les-mots-pour-se-comprendre',title:'Les mots pour te comprendre. Pas pour t’enfermer.',category:'Le lexique',summary:'Des repères simples, sans te mettre dans une case.'},
  {slug:'profil-et-vie-privee',title:'Ton profil, tes règles. Tu choisis ce que tu partages.',category:'Vie privée',summary:'Garder la main sur ce que tu dévoiles.'},
  {slug:'premiere-rencontre',title:'Du premier message à la première rencontre.',category:'Rencontres',summary:'Passer du chat au réel, à ton rythme.'},
  {slug:'aftercare',title:'L’aftercare : la connexion continue après.',category:'Entre nous',summary:'L’attention portée à l’autre ne s’arrête pas au moment partagé.'},
];

export function journalCatalogue(published = []) {
  const seen = new Set();
  return [...published, ...historicArticles].filter(item => {
    if (seen.has(item.slug)) return false;
    seen.add(item.slug);
    return true;
  }).map(item => ({...item, href:`/guides/${item.slug}`}));
}
