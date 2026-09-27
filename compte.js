let accountCsrf = '';
const emailForm = document.querySelector('#account-email-form');
const emailStatus = document.querySelector('#account-email-status');
const deleteAccount = document.querySelector('#delete-account');
async function accountApi(path, method='GET', body) {
  const response = await fetch('/api/member/' + path,{
    method, credentials:'same-origin',
    headers:{...(body ? {'Content-Type':'application/json'} : {}),...(accountCsrf ? {'X-CSRF-Token':accountCsrf} : {})},
    body:body ? JSON.stringify(body) : undefined
  });
  if (!response.ok) throw Error((await response.json().catch(() => ({}))).detail || 'Service indisponible');
  return response.json();
}
try {
  const me = await accountApi('me');
  accountCsrf = me.csrf;
  const profile = await accountApi('profile');
  const codeDisplay = [...document.querySelectorAll('*')].find(el => el.children.length === 0 && el.textContent.trim() === 'KQ-••••••');
  if (codeDisplay && profile.code) codeDisplay.textContent = profile.code;
} catch {location.href='/connexion';}
emailForm.addEventListener('submit', async event => {
  event.preventDefault();
  if (!emailForm.reportValidity()) return;
  const email=emailForm.querySelector('input').value.trim();
  try {
    await accountApi('email/request','POST',{email});
    emailStatus.textContent='Un code vient d’être envoyé à la nouvelle adresse.';
    let codeForm=document.querySelector('#account-email-code-form');
    if (!codeForm) {
      codeForm=document.createElement('form');
      codeForm.id='account-email-code-form';
      codeForm.innerHTML='<label for="account-email-code">Code à 6 chiffres</label><input id="account-email-code" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}" maxlength="6" required><button class="button" type="submit">Confirmer la nouvelle adresse</button>';
      emailForm.after(codeForm);
      codeForm.addEventListener('submit',async e=>{
        e.preventDefault();
        try {await accountApi('email/verify','POST',{email:emailForm.querySelector('input').value.trim(),code:codeForm.querySelector('input').value});emailStatus.textContent='Adresse modifiée.';codeForm.remove();emailForm.reset();}
        catch(error){emailStatus.textContent=error.message;}
      });
    }
    codeForm.querySelector('input').focus();
  } catch(error) {emailStatus.textContent=error.message;}
});
let deleteArmed=false;
deleteAccount.addEventListener('click',async()=>{
  if (!deleteArmed) {
    deleteArmed=true;
    deleteAccount.classList.add('is-armed');
    deleteAccount.querySelector('span').textContent='Confirmer la suppression';
    return;
  }
  deleteAccount.disabled=true;
  try {await accountApi('account','DELETE');location.href='/connexion';}
  catch(error){deleteAccount.disabled=false;emailStatus.textContent=error.message;}
});
