import PageEffects from '../legacy-scripts';

export const metadata = {
  title: 'L’application Kinq — Profils, rencontres et messages',
  description: 'Crée ton compte sur le site, puis retrouve ton profil, tes rencontres et tes messages dans l’application Kinq. Bientôt sur iOS et Android.',
};
const bodyAttrs = {'data-page':'application'};
const scripts = [{src:'/shell.js'}, {src:'/app.js'}];

export default async function ApplicationPage({searchParams}) {
  const code = (await searchParams).profil;
  const sharedCode = typeof code === 'string' && /^KQ-[A-F0-9]{8}$/.test(code) ? code : null;
  return <>
    <link rel="stylesheet" href="/styles.css"/>
    <div id="site-header"/>
    <main id="page-main"><section className="wrap account-flow app-continuation">
      <div className="account-flow-copy"><p className="eyebrow">KINQ / L’APPLICATION</p><h1>Le feeling se vit<br/><span>dans l’app.</span></h1><p>Ton profil, les rencontres, les Pins, les Hooks et les messages : tout se passe dans Kinq.</p><p>Le site te présente notre univers, accueille NO TABOO et te permet de créer ton compte.</p><a className="button" href="/inscription">Créer mon compte <svg aria-hidden="true"><use href="#arrow"/></svg></a></div>
      <div className="account-flow-card"><p className="eyebrow">TON UNIVERS. DANS TA POCHE.</p><h2>La suite,<br/>à ton rythme.</h2><p>Crée ton compte sur le site, puis connecte-toi dans l’app avec la même adresse e-mail. Tu pourras y compléter et modifier ton profil, découvrir les membres et discuter.</p>
        {sharedCode && <div className="app-shared-profile"><p>Pour retrouver le profil partagé, recherche ce code dans l’app :</p><strong>{sharedCode}</strong></div>}
        <p className="app-availability">Bientôt sur iOS et Android.</p><p>Le téléchargement sera disponible au lancement.</p><a className="button light" href="/guides">En attendant, explore NO TABOO <svg aria-hidden="true"><use href="#arrow"/></svg></a>
      </div>
    </section></main>
    <div id="site-footer"/>
    <dialog id="dialog"><button className="dialog-close" aria-label="Fermer"><svg><use href="#close"/></svg></button><div id="dialog-content"/></dialog>
    <div id="toast" role="status" aria-live="polite"/>
    <PageEffects bodyAttrs={bodyAttrs} scripts={scripts}/>
  </>;
}
