import catalogue from '../../content/contracts.json' with {type: 'json'};

export {catalogue};
export const modelFor = id => catalogue.models.find(model => model.id === id);

export function freshDraft(id = 'bdsm') {
  const model = modelFor(id);
  return {version:catalogue.version, model:id, nameA:'', nameB:'', roleA:model.roles[0], roleB:model.roles[1], start:'', end:'', duration:'À convenir ensemble', fields:Object.fromEntries([...catalogue.common,...model.fields].map(field => [field.id,field.default]))};
}

function date(value) {return value ? value.split('-').reverse().join('/') : 'À préciser';}

export function contractSections(draft) {
  const model = modelFor(draft.model);
  return [
    {title:'Notre accord',text:model.intro},
    {title:'Les personnes et les rôles',text:`${draft.nameA.trim() || '________________________'} : ${draft.roleA.trim() || model.roles[0]}.\n${draft.nameB.trim() || '________________________'} : ${draft.roleB.trim() || model.roles[1]}.`},
    {title:'La durée',text:`Début : ${date(draft.start)}. Fin : ${date(draft.end)}.\n${draft.duration.trim() || 'Durée et renouvellement à convenir ensemble.'}`},
    ...[catalogue.common[0],...model.fields,...catalogue.common.slice(1)].filter(field => draft.fields[field.id]?.trim()).map(field => ({title:field.title,text:draft.fields[field.id].trim()})),
    {title:'Un accord qui reste libre',text:catalogue.closing},
  ];
}

export function contractText(draft) {
  return [modelFor(draft.model).title,...contractSections(draft).map(section => `${section.title}\n${section.text}`),catalogue.poweredBy].join('\n\n');
}

export function formatSignedAt(value) {
  return new Intl.DateTimeFormat('fr-FR',{timeZone:'Europe/Paris',dateStyle:'long',timeStyle:'short'}).format(new Date(value));
}
