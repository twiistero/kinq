const loginForm = document.querySelector('#login-form');
const loginCodeForm = document.querySelector('#login-code-form');
const loginStatus = document.querySelector('#login-status');
async function memberLogin(path, body) {
  const response = await fetch('/api/member/auth/' + path, {
    method: 'POST', credentials: 'same-origin',
    headers: {'Content-Type':'application/json'}, body:JSON.stringify(body)
  });
  if (!response.ok) throw Error((await response.json().catch(() => ({}))).detail || 'Une erreur est survenue.');
  return response.json();
}
loginForm.addEventListener('submit', async event => {
  event.preventDefault();
  if (!loginForm.reportValidity()) return;
  const button = loginForm.querySelector('[type=submit]');
  button.disabled = true;
  loginStatus.textContent = '';
  try {
    const result = await memberLogin('request', {email:loginForm.elements.email.value.trim(), purpose:'login'});
    loginCodeForm.hidden = false;
    loginStatus.textContent = result.delivery === 'configured_code' ? 'Saisis le code de connexion configuré pour ce compte.' : 'Si ce compte existe, un code vient d’être envoyé.';
    loginCodeForm.elements.code.focus();
  } catch(error) {loginStatus.textContent = error.message;}
  finally {button.disabled = false;}
});
loginCodeForm.addEventListener('submit', async event => {
  event.preventDefault();
  const button = loginCodeForm.querySelector('[type=submit]');
  button.disabled = true;
  try {
    await memberLogin('verify', {email:loginForm.elements.email.value.trim(), code:loginCodeForm.elements.code.value});
    const next = new URLSearchParams(location.search).get('next') || '';
    location.href = ['/mes-contrats','/compte'].includes(next) ? next : /^\/guides(?:\/[a-z0-9]+(?:-[a-z0-9]+)*)?(?:#commentaires)?$/.test(next) ? next : '/guides';
  } catch(error) {loginStatus.textContent = error.message; button.disabled = false;}
});


const accountNext = new URLSearchParams(location.search).get('next');
if (['/mes-contrats','/compte'].includes(accountNext)) {
  const copy = document.querySelector('.account-flow-copy');
  copy.querySelector('h1').textContent='Retrouve tes contrats.';
  copy.querySelectorAll('p')[0].remove();
  copy.querySelectorAll('p')[0].textContent='Connecte-toi à ton compte Kinq pour conserver tes contrats et les retrouver dans l’app.';
  document.title='Connexion — Kinq';
  const signup = document.querySelector('.account-flow-card a[href="/inscription"], .account-flow-card a[href="inscription.html"]');
  if (signup) signup.href='/inscription?next='+accountNext;
}
