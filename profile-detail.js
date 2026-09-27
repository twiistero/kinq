const detail = document.querySelector('#profile-detail');
const requestedId = new URLSearchParams(location.search).get('id');
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const symbol = name => `<svg aria-hidden="true"><use href="#${name}"/></svg>`;
const [identityResponse, profilesResponse, signalsResponse] = await Promise.all([
  fetch('/api/member/me'), fetch('/api/profiles'), fetch('/api/member/signals')
]);
if (!identityResponse.ok || !profilesResponse.ok || !signalsResponse.ok) {
  detail.textContent = 'Ce profil est indisponible pour le moment.';
} else {
  const identity = await identityResponse.json();
  const profiles = await profilesResponse.json();
  const signals = await signalsResponse.json();
  const profile = profiles.find(item => item.id === requestedId);
  if (!profile) {
    detail.innerHTML = '<a class="underlink" href="/rencontres">Retour aux rencontres</a><p>Profil introuvable.</p>';
  } else {
    const isMember = profile.id.startsWith('member-');
    const pins = new Set(signals.pins);
    const hooks = new Set(signals.hooks);
    const tags = (profile.kinks || []).slice(0, 12);
    const label = isMember ? 'MEMBRE KINQ' : 'PROFIL FICTIF';
    const photo = profile.photo
      ? `<img class="profile-main-photo" src="${esc(profile.photo)}" alt="${isMember?'Photo du membre':'Photo d’illustration'} ${esc(profile.name)}">`
      : `<div class="private-album">${symbol('lock')}<p>Photo sur demande</p></div>`;
    detail.innerHTML = `<a class="underlink" href="/rencontres">Retour aux rencontres</a><div class="profile-layout"><div>${photo}<div class="private-album">${symbol('lock')}<p>Album privé<br><strong>À partager, à ton rythme.</strong></p><button class="underlink" data-modal="album">Demander l’accès</button></div></div><div class="profile-info"><p class="eyebrow">${label} / ${esc(String(profile.city||'').toUpperCase())}</p><h1>${esc(profile.name)}, ${Number(profile.age)||18}</h1><p>${tags.map(esc).join(' · ')}</p><div class="profile-actions"><button class="button" data-modal="message">${symbol('message')} Message</button><button class="hook-button" data-profile-hook aria-pressed="${hooks.has(profile.id)}">${symbol('hook')}${hooks.has(profile.id)?'Envoyé':'Hook'}</button><button class="pin-inline" data-profile-pin aria-pressed="${pins.has(profile.id)}">${symbol('pin')} ${pins.has(profile.id)?'Enregistré':'Pin'}</button></div><div class="profile-block"><h2>Le feeling d’abord.</h2><p>${esc(profile.bio)}</p></div><div class="profile-block"><h2>Son univers</h2><div class="profile-kinks">${tags.map(tag=>`<span>${esc(tag)}</span>`).join('')}</div></div><div class="profile-block"><h2>Envies & limites</h2><p>${esc(profile.quote || 'Prendre le temps de se découvrir et parler de ses envies.')}</p></div><div class="profile-block profile-code"><div><h2>Code Kinq</h2><p>${esc(profile.code)}</p></div><button data-profile-copy>${symbol('code')} Copier le code</button></div><p class="demo-note">${isMember?'Ce profil appartient à un membre KINQ.':'Identité et préférences inventées pour la maquette. La personne photographiée n’est pas membre de KINQ.'}</p></div></div>`;
    async function saveSignal(kind, active) {
      const response = await fetch('/api/member/signals', {method:'PUT',headers:{'Content-Type':'application/json','X-CSRF-Token':identity.csrf},body:JSON.stringify({kind,target_id:profile.id,active})});
      if (!response.ok) throw Error('Ce choix n’a pas pu être enregistré.');
    }
    detail.addEventListener('click', async event => {
      const button = event.target.closest('button');
      if (!button) return;
      if (button.hasAttribute('data-profile-copy')) {
        try {await navigator.clipboard.writeText(profile.code);button.textContent='Code copié';} catch {button.textContent=profile.code;}
      }
      for (const [attribute, kind, set] of [['data-profile-pin','pin',pins],['data-profile-hook','hook',hooks]]) {
        if (!button.hasAttribute(attribute)) continue;
        const active = !set.has(profile.id);
        button.disabled = true;
        try {await saveSignal(kind,active);active?set.add(profile.id):set.delete(profile.id);button.setAttribute('aria-pressed',String(active));button.innerHTML = symbol(kind)+(kind==='pin'?(active?' Enregistré':' Pin'):(active?'Envoyé':'Hook'));}
        catch (error) {button.textContent=error.message;}
        finally {button.disabled=false;}
      }
    });
  }
}
