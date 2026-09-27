'use client';

import {useEffect} from 'react';

export default function PageEffects({bodyAttrs, scripts}) {
  useEffect(() => {
    for (const [name, value] of Object.entries(bodyAttrs || {})) document.body.setAttribute(name, value);
    let cancelled = false;
    const loaded = [];
    (async () => {
      for (const item of scripts || []) {
        if (cancelled) break;
        await new Promise(resolve => {
          const element = document.createElement('script');
          element.src = item.src;
          if (item.type) element.type = item.type;
          element.async = false;
          element.onload = resolve;
          element.onerror = resolve;
          document.body.appendChild(element);
          loaded.push(element);
        });
      }
    })();
    return () => {
      cancelled = true;
      for (const element of loaded) element.remove();
      for (const name of Object.keys(bodyAttrs || {})) document.body.removeAttribute(name);
    };
  }, [bodyAttrs, scripts]);
  return null;
}
