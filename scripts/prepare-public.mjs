import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const target = path.join(root, 'public');
fs.mkdirSync(target, {recursive: true});
for (const name of fs.readdirSync(root)) {
  if (/\.(css|js|svg|png|jpe?g|webp|ico|txt)$/i.test(name)) {
    fs.copyFileSync(path.join(root, name), path.join(target, name));
  }
}
fs.cpSync(path.join(root, 'assets'), path.join(target, 'assets'), {recursive: true});
fs.mkdirSync(path.join(target, 'admin'), {recursive: true});
for (const name of ['style.css', 'app.js']) fs.copyFileSync(path.join(root, 'admin', name), path.join(target, 'admin', name));
