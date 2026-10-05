'use client';

import {useEffect} from 'react';

// Keep native details/summary semantics and React-owned content intact.
export default function Disclosures() {
  useEffect(() => {
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const active = new Map();

    function settle(details, state, expanded = state.expanded) {
      if (active.get(details) !== state) return;
      state.animation.onfinish = null;
      state.animation.cancel();
      details.open = expanded;
      Object.assign(details.style, state.original);
      delete details.dataset.disclosureExpanded;
      active.delete(details);
    }

    function toggle(details) {
      const previous = active.get(details);
      const expanded = !(previous?.expanded ?? details.open);
      const start = details.getBoundingClientRect().height;
      const original = previous?.original || {
        height: details.style.height,
        overflow: details.style.overflow,
        boxSizing: details.style.boxSizing,
      };
      if (previous) {
        previous.animation.onfinish = null;
        previous.animation.cancel();
      }

      Object.assign(details.style, original);
      details.style.boxSizing = 'border-box';
      details.open = expanded;
      const end = details.getBoundingClientRect().height;
      // Keep the content rendered until the closing animation is complete.
      details.open = true;
      details.dataset.disclosureExpanded = String(expanded);
      details.style.height = `${start}px`;
      details.style.overflow = 'hidden';
      const animation = details.animate(
        [{height: `${start}px`}, {height: `${end}px`}],
        {duration: 300, easing: 'cubic-bezier(.22,1,.36,1)', fill: 'both'},
      );
      const state = {animation, original, expanded};
      active.set(details, state);
      animation.onfinish = () => settle(details, state);
    }

    function onClick(event) {
      if (event.defaultPrevented || !(event.target instanceof Element)) return;
      const summary = event.target.closest('summary');
      const details = summary?.parentElement;
      if (details?.tagName !== 'DETAILS' || details.querySelector(':scope > summary') !== summary) return;
      if (event.target.closest('a,button,input,select,textarea,label')) return;
      if (motion.matches || typeof details.animate !== 'function') return;
      event.preventDefault();
      toggle(details);
    }

    function onToggle(event) {
      const details = event.target;
      const state = active.get(details);
      // Respect an external close, e.g. a search filter or exclusive group.
      if (state && !details.open) settle(details, state, false);
    }

    function settleAll() {
      for (const [details, state] of active) settle(details, state);
    }

    document.addEventListener('click', onClick);
    document.addEventListener('toggle', onToggle, true);
    window.addEventListener('resize', settleAll);
    motion.addEventListener('change', settleAll);
    return () => {
      document.removeEventListener('click', onClick);
      document.removeEventListener('toggle', onToggle, true);
      window.removeEventListener('resize', settleAll);
      motion.removeEventListener('change', settleAll);
      settleAll();
    };
  }, []);
  return null;
}
