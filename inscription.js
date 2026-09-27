const signupForm = document.querySelector('#signup-form');
const signupFormView = document.querySelector('#signup-form-view');
const signupNextView = document.querySelector('#signup-next-view');
signupForm.addEventListener('submit', event => {
  event.preventDefault();
  if (!signupForm.reportValidity()) return;
  document.querySelector('#signup-email-preview').textContent = signupForm.elements.email.value.trim();
  signupFormView.hidden = true;
  signupNextView.hidden = false;
  signupNextView.querySelector('h2').focus?.();
});
document.querySelector('#signup-back').addEventListener('click', () => {
  signupNextView.hidden = true;
  signupFormView.hidden = false;
  signupForm.elements.email.focus();
});
