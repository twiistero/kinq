const profileForm = document.querySelector('#my-profile-form');
const profileStatus = document.createElement('p');
profileStatus.setAttribute('role','status');
profileStatus.className = 'demo-note';
profileStatus.textContent = 'Chargement de ton profil…';
profileForm.after(profileStatus);
let profileCsrf = '';
let saveTimer = 0;
async function profileApi(path, options={}) {
  const response = await fetch('/api/member/' + path, {credentials:'same-origin',...options});
  if (!response.ok) throw Error((await response.json().catch(() => ({}))).detail || 'Service indisponible');
  return response.json();
}
function profilePayload() {
  const formData = new FormData(profileForm);
  const values = Object.fromEntries(formData);
  values.style = formData.getAll('style');
  values.practice = formData.getAll('practice');
  for (const name of ['invisible','discreet','hideCity','hideLimits']) values[name] = formData.has(name);
  delete values.relationConfirm;
  return values;
}
async function saveProfile() {
  try {
    await profileApi('profile',{method:'PUT',headers:{'Content-Type':'application/json','X-CSRF-Token':profileCsrf},body:JSON.stringify({data:profilePayload()})});
    profileStatus.textContent = 'Profil enregistré.';
  } catch(error) {profileStatus.textContent = 'Enregistrement impossible : ' + error.message;}
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
  profileForm.dispatchEvent(new Event('input',{bubbles:true}));
}
try {
  const me = await profileApi('me');
  profileCsrf = me.csrf;
  const profile = await profileApi('profile');
  if (Object.keys(profile.data).length) restoreProfile(profile.data);
  profileStatus.textContent = 'Tes modifications sont enregistrées automatiquement.';
  profileForm.addEventListener('input',()=>{profileStatus.textContent='Enregistrement…';clearTimeout(saveTimer);saveTimer=setTimeout(saveProfile,700)});
  profileForm.addEventListener('change',()=>{profileStatus.textContent='Enregistrement…';clearTimeout(saveTimer);saveTimer=setTimeout(saveProfile,700)});
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
  profileStatus.textContent = 'Connecte-toi pour enregistrer ton profil.';
}
