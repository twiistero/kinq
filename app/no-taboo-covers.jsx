export const journalCovers = {
  'premiers-pas': {lines:['FIRST','TIME?'],theme:'lime'},
  'parler-de-ses-limites': {lines:['YES.','NO.','MAYBE.'],theme:'dark'},
  'les-mots-pour-se-comprendre': {lines:['DOM.','SUB.','ET TOI ?'],theme:'lime'},
  'profil-et-vie-privee': {lines:['PRIVATE.','BY CHOICE.'],theme:'dark'},
  'premiere-rencontre': {lines:['IRL.','ET ALORS ?'],theme:'lime'},
  aftercare: {lines:['ET','APRÈS ?'],theme:'lime'},
};
export function coverFor(slug, words) { return journalCovers[slug] || (words?.length ? {lines:words,theme:'lime'} : {lines:['NO','TABOO.'],theme:'lime'}); }
export function CoverWords({slug, words}) {
  const {lines}=coverFor(slug, words);
  return <div className="nt-cover-words">{lines.map((line,index)=><span className={index===lines.length-1?'nt-cover-last':undefined} key={line}>{line}</span>)}</div>;
}
