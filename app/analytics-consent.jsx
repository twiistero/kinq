'use client';

import {useEffect, useState} from 'react';
import {usePathname} from 'next/navigation';

const storageKey = 'kinq_analytics_consent';

export default function AnalyticsConsent({siteId}) {
  const pathname = usePathname();
  const privateTool = ['/profil-fetish','/kit-rencontre'].includes(pathname) || pathname.startsWith('/contrats');
  const [choice, setChoice] = useState(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let saved = null;
    try { saved = localStorage.getItem(storageKey); } catch {}
    setChoice(saved);
    setOpen(saved !== 'accepted' && saved !== 'refused');
  }, []);

  useEffect(() => {
    if (privateTool) {
      window.Analytics?.consent(false);
      document.querySelector('script[data-kinq-analytics]')?.remove();
      return;
    }
    if (!siteId || choice !== 'accepted') {
      window.Analytics?.consent(false);
      return;
    }
    const activate = () => window.Analytics?.consent(true);
    let script = document.querySelector('script[data-kinq-analytics]');
    if (script && script.dataset.site !== siteId) {
      window.Analytics?.consent(false);
      script.remove();
      script = null;
    }
    if (!script) {
      script = document.createElement('script');
      script.defer = true;
      script.src = 'https://analytics.theethercompany.com/pixel.js';
      script.dataset.site = siteId;
      script.dataset.kinqAnalytics = '';
      document.head.append(script);
    }
    script.addEventListener('load', activate);
    activate();
    return () => script.removeEventListener('load', activate);
  }, [siteId, choice, privateTool]);

  function decide(value) {
    try { localStorage.setItem(storageKey, value); } catch {}
    setChoice(value);
    setOpen(false);
    if (value === 'refused') window.Analytics?.consent(false);
  }

  return <>
    {open && <div className="kinq-consent-wrap"><section className="kinq-consent" role="dialog" aria-label="Choix des cookies" aria-modal="false">
      <div><h2>Ta vie privée, ton choix.</h2><p>Avec ton accord, une mesure d’audience nous aide à comprendre ce qui plaît sur KINQ. Tu peux refuser ou changer d’avis à tout moment.</p><a href="/confidentialite">En savoir plus sur tes données</a></div>
      <div className="kinq-consent-actions"><button type="button" onClick={() => decide('accepted')}>Accepter la mesure</button><button type="button" onClick={() => decide('refused')}>Continuer sans mesure</button></div>
    </section></div>}
    {!open && choice && <button className="kinq-consent-reopen" type="button" onClick={() => setOpen(true)}>Cookies</button>}
  </>;
}
