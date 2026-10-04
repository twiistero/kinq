import fs from 'node:fs';

// A recognisable editorial selection, using the shared profile pictograms.
const icons = [
  'leather', 'rubber', 'harness', 'bondage',
  'restraints', 'shibari', 'pup', 'collar',
  'spanking', 'flogging', 'blindfold', 'gas-mask',
  'boots', 'paddling', 'sportswear', 'underwear',
  'socks', 'sneakers', 'chastity', 'toys',
];
const drawings = new Map();
for (const icon of icons) {
  if (!fs.existsSync(new URL(`../assets/pictos/${icon}.svg`, import.meta.url))) {
    throw new Error(`Missing homepage kink pictogram: ${icon}`);
  }
  // Inline SVG inherits the tile's ink. External images cannot inherit CSS variables.
  const svg = fs.readFileSync(new URL(`../assets/pictos/${icon}.svg`, import.meta.url), 'utf8')
    .replace(/\sstyle="[^"]*"/g, '')
    .replace(/<title>[\s\S]*?<\/title>/g, '')
    .replace('<svg ', '<svg aria-hidden="true" focusable="false" ');
  drawings.set(icon, svg);
}

function field(columns, variant) {
  return `<div class="hero-kink-field hero-kink-field--${variant}">` + Array.from({length: columns}, (_, column) => {
    // Desktop's exposed right half starts with leather, latex, harness and bondage.
    // On mobile those same icons recur just below the title and signup buttons.
    const first = columns === 8 ? (column < 4 ? column + 8 : column - 4) : column;
    const items = Array.from({length: 16}, (_, row) => icons[(first + row * 4) % icons.length]);
    const group = `<div class="hero-kink-group">${items.map(icon => `<span class="hero-kink-tile" data-kink-icon="${icon}">${drawings.get(icon)}</span>`).join('')}</div>`;
    return `<div class="hero-kink-column"><div class="hero-kink-track">${group}</div></div>`;
  }).join('') + '</div>';
}

const source = new URL('../legacy-pages/index.html', import.meta.url);
const html = fs.readFileSync(source, 'utf8');
const slot = /(<div class="hero-kink-tapestry" aria-hidden="true">)[\s\S]*?(<!-- \/hero-kink-tapestry -->)/;
if (!slot.test(html)) throw new Error('Homepage kink tapestry slot not found');
fs.writeFileSync(source, html.replace(slot, (_, start, end) => `${start}${field(8, 'desktop')}${field(4, 'mobile')}</div>${end}`));
console.log(`Prepared homepage tapestry with ${icons.length} kink pictograms`);
