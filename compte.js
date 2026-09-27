document.querySelector('#account-email-form').addEventListener('submit', event => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  document.querySelector('#account-email-status').textContent = 'Dans le vrai service, un lien serait envoyé pour confirmer cette nouvelle adresse. Aucun e-mail n’est envoyé et ton adresse n’est pas modifiée dans cette maquette.';
});

const deleteAccount = document.querySelector('#delete-account');
let deleteArmed = false;
deleteAccount.addEventListener('click', () => {
  if (!deleteArmed) {
    deleteArmed = true;
    deleteAccount.classList.add('is-armed');
    deleteAccount.querySelector('span').textContent = 'Tu es bien sûr ?';
    return;
  }
  deleteAccount.disabled = true;
  deleteAccount.classList.add('is-deleting');
  deleteAccount.querySelector('span').textContent = 'Suppression en cours…';
  setTimeout(() => { location.href = 'connexion.html'; }, 1300);
});
