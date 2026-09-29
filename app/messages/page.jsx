import PageEffects from '../legacy-scripts';
import MessagesClient from './messages-client';
import './messages.css';

export const metadata = {
  title: 'Messages — KINQ',
  description: 'Aperçu interactif de la messagerie KINQ.',
  robots: {index: false, follow: false},
};
const bodyAttrs = {class: 'kinq-space', 'data-page': 'messages'};
const scripts = [{src:'/shell.js'}, {src:'/app.js'}];

export default function MessagesPage() {
  return <>
    <link rel="stylesheet" href="/styles.css"/>
    <link rel="stylesheet" href="/rencontres.css"/>
    <div id="site-header"/>
    <MessagesClient/>
    <div id="site-footer"/>
    <dialog id="dialog"><button className="dialog-close" aria-label="Fermer"><svg><use href="#close"/></svg></button><div id="dialog-content"/></dialog>
    <div id="toast" role="status" aria-live="polite"/>
    <PageEffects bodyAttrs={bodyAttrs} scripts={scripts}/>
  </>;
}
