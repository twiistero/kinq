const signupForm = document.querySelector('#signup-form');
const signupFormView = document.querySelector('#signup-form-view');
const signupNextView = document.querySelector('#signup-next-view');
const signupStatus = document.querySelector('#signup-status');
async function memberAuth(path, body) {
  const response = await fetch('/api/member/auth/' + path, {
    method: 'POST', credentials: 'same-origin',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  });
  if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail || 'Une erreur est survenue.');
  return response.json();
}
signupForm.addEventListener('submit', async event => {
  event.preventDefault();
  if (!signupForm.reportValidity()) return;
  const button = signupForm.querySelector('[type=submit]');
  button.disabled = true;
  try {
    await memberAuth('request', {
      email: signupForm.elements.email.value.trim(),
      purpose: 'signup', adult: signupForm.elements.adult.checked,
      terms: signupForm.elements.terms.checked, charter: signupForm.elements.charter.checked
    });
    document.querySelector('#signup-email-preview').textContent = signupForm.elements.email.value.trim();
    signupFormView.hidden = true;
    signupNextView.hidden = false;
    document.querySelector('#signup-code').focus();
  } catch (error) { alert(error.message); }
  finally { button.disabled = false; }
});
document.querySelector('#signup-code-form').addEventListener('submit', async event => {
  event.preventDefault();
  const button = event.currentTarget.querySelector('[type=submit]');
  button.disabled = true;
  signupStatus.textContent = '';
  try {
    await memberAuth('verify', {email: signupForm.elements.email.value.trim(), code: event.currentTarget.elements.code.value});
    location.href = '/mon-profil';
  } catch (error) { signupStatus.textContent = error.message; button.disabled = false; }
});
document.querySelector('#signup-back').addEventListener('click', () => {
  signupNextView.hidden = true;
  signupFormView.hidden = false;
  signupForm.elements.email.focus();
});
