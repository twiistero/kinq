const profileForm = document.querySelector('#my-profile-form');
const profileStatus = document.createElement('p');
profileStatus.setAttribute('role','status');
profileStatus.className = 'demo-note';
profileStatus.textContent = 'Chargement de ton profil…';
profileForm.after(profileStatus);
let profileCsrf = '';
let saveTimer = 0;
let readyToSave = false;
let saveQueue = Promise.resolve();
let revision = 0;
async function profileApi(path, options={}) {
  const response = await fetch('/api/member/' + path, {credentials:'same-origin',...options});
  if (!response.ok) {const detail = (await response.json().catch(() => ({}))).detail; throw Error(typeof detail === 'string' ? detail : 'Vérifie les informations de ton profil.');}
  return response.json();
}
function profilePayload() {
  const formData = new FormData(profileForm);
  const values = Object.fromEntries([...formData].filter(([key]) => !key.startsWith('kp-')));
  values.style = formData.getAll('style');
  values.practice = formData.getAll('practice');
  for (const name of ['invisible','discreet','hideCity','hideLimits']) values[name] = formData.has(name);
  values.kinkPreferences = window.kinqPreferences.getData();
  delete values.relationConfirm;
  return values;
}
function saveProfile() {
  clearTimeout(saveTimer);
  if (!readyToSave) {profileStatus.textContent = 'Connecte-toi pour enregistrer ton profil.'; return Promise.resolve(false);}
  if (!profileForm.reportValidity()) {profileStatus.textContent = 'Vérifie les champs signalés avant d’enregistrer.'; return Promise.resolve(false);}
  const body = JSON.stringify({data:profilePayload()}); const savedRevision = revision;
  profileStatus.textContent = 'Enregistrement…';
  saveQueue = saveQueue.then(async () => {
    try {
      await profileApi('profile',{method:'PUT',headers:{'Content-Type':'application/json','X-CSRF-Token':profileCsrf},body});
      if (savedRevision === revision) {
        profileStatus.textContent = 'Profil enregistré.';
        const validate = document.querySelector('#validate-profile'); validate.classList.add('is-validated');validate.querySelector('span').textContent='Profil enregistré';
      }
      return true;
    } catch(error) {profileStatus.textContent = 'Enregistrement impossible : ' + error.message; return false;}
  });
  return saveQueue;
}
window.kinqSaveProfile = saveProfile;
function restoreProfile(data) {
  for (const [name,value] of Object.entries(data)) {
    const fields = [...profileForm.querySelectorAll('input,select,textarea')].filter(field => field.name === name);
    for (const field of fields) {
      if (field.type === 'checkbox') field.checked = Array.isArray(value) ? value.includes(field.value) : Boolean(value);
      else if (!Array.isArray(value)) field.value = String(value ?? '');
    }
  }
  // Match by stable legacy name even if its catalogue category has changed.
  const names = [...(data.style || []), ...(data.practice || [])];
  for (const field of profileForm.querySelectorAll('#kink-picker input')) field.checked = names.includes(field.value);
  window.kinqPreferences.restore(data);
  profileForm.dispatchEvent(new Event('input',{bubbles:true}));
}
profileForm.inert = true;
try {
  const me = await profileApi('me');
  profileCsrf = me.csrf;
  const profile = await profileApi('profile');
  if (Object.keys(profile.data).length) restoreProfile(profile.data);
  profileStatus.textContent = 'Tes modifications sont enregistrées automatiquement.';
  readyToSave = true;
  const scheduleSave = event => {
    if (event.target.id === 'kink-search' || event.target.dataset?.mix) return;
    revision++; profileStatus.textContent='Modifications en cours…';clearTimeout(saveTimer);saveTimer=setTimeout(saveProfile,700);
  };
  profileForm.addEventListener('input',scheduleSave);
  profileForm.addEventListener('change',scheduleSave);
  profileForm.addEventListener('reset',()=>{revision++;clearTimeout(saveTimer);});
  const upload = document.createElement('label');
  upload.className = 'underlink';
  upload.textContent = 'Ajouter une photo (validation avant publication) ';
  const input = document.createElement('input');
  input.type='file'; input.accept='image/jpeg,image/png,image/webp'; input.name='member-photo';
  upload.append(input); profileStatus.after(upload);
  input.addEventListener('change',async()=>{
    if (!input.files[0]) return;
    const body = new FormData(); body.append('photo',input.files[0]);
    profileStatus.textContent='Envoi de la photo…';
    try {await profileApi('photos',{method:'POST',headers:{'X-CSRF-Token':profileCsrf},body});profileStatus.textContent='Photo envoyée en modération. Elle sera invisible avant validation.';}
    catch(error){profileStatus.textContent=error.message;}
    input.value='';
  });
} catch {
  profileStatus.textContent = 'Connecte-toi pour enregistrer ton profil, ou réessaie si le service est indisponible.';
} finally {profileForm.inert = false;}
