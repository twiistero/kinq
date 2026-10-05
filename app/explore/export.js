export async function copyText(text) {
  if (!navigator.clipboard?.writeText) throw new Error('Copie indisponible');
  await navigator.clipboard.writeText(text);
}

export function downloadText(text, filename) {
  downloadBlob(new Blob([text], {type:'text/plain;charset=utf-8'}), filename);
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
