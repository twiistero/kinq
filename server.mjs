import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const api = process.env.KINQ_API_URL || 'http://127.0.0.1:8000';
const port = Number(process.env.PORT || 4173);
const mime = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.json':'application/json'};
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
http.createServer(async (req,res) => {
  let pathname;
  try {pathname = decodeURIComponent(new URL(req.url,'http://localhost').pathname);}
  catch {res.writeHead(400);res.end('Adresse invalide');return;}
  if (pathname.startsWith('/api/')) {
    try {
      const upstream = await fetch(api + req.url,{method:req.method,headers:{...req.headers,host:new URL(api).host},body:['GET','HEAD'].includes(req.method)?undefined:req,duplex:'half',redirect:'manual'});
      const headers = Object.fromEntries(upstream.headers);
      delete headers['transfer-encoding'];
      res.writeHead(upstream.status,headers);
      if (upstream.body) for await (const chunk of upstream.body) res.write(chunk);
      res.end();
    } catch {res.writeHead(502);res.end('API indisponible');}
    return;
  }
  if (pathname.startsWith('/journal/')) {
    const slug = pathname.slice('/journal/'.length);
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {res.writeHead(404);res.end('Introuvable');return;}
    try {
      const [articleResponse,pageResponse] = await Promise.all([
        fetch(api + '/api/articles/' + slug,{signal:AbortSignal.timeout(8000)}),
        fetch(api + '/api/pages/journal-article.html',{signal:AbortSignal.timeout(8000)})
      ]);
      if (!articleResponse.ok || !pageResponse.ok) {res.writeHead(articleResponse.status===404 ? 404 : 502);res.end('Article indisponible');return;}
      const article = await articleResponse.json();
      const template = (await pageResponse.json()).html;
      const paragraphs = String(article.body).split(/\n\s*\n/).map(p => '<p>' + escapeHtml(p).replaceAll('\n','<br>') + '</p>').join('');
      const story = '<header class="nt-masthead"><a href="/guides.html"><strong>NO TABOO<span>.</span></strong><small>LE JOURNAL KINQ</small></a></header><article class="nt-story"><header class="nt-editorial-hero"><div class="nt-editorial-hero-copy"><p class="eyebrow">NO TABOO / JOURNAL</p><h1>' + escapeHtml(article.title) + '</h1><p>' + escapeHtml(article.summary) + '</p></div></header><div class="nt-prose">' + paragraphs + '</div><a class="button" href="/guides.html">Retour au journal</a></article>';
      const html = template.replace('<title>NO TABOO — KINQ</title>','<title>' + escapeHtml(article.title) + ' — NO TABOO, KINQ</title>').replace('<div id="dynamic-story" class="nt-site nt-reading wrap"></div>','<div id="dynamic-story" class="nt-site nt-reading wrap">' + story + '</div>');
      res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','X-Content-Type-Options':'nosniff'});res.end(html);
    } catch {res.writeHead(502);res.end('Article indisponible');}
    return;
  }
  const name = pathname === '/admin' || pathname === '/admin/' ? 'admin/index.html' : pathname === '/' ? 'index.html' : pathname.slice(1);
  if (name.endsWith('.html') && !name.startsWith('admin/')) {
    if (!/^[a-z0-9-]+\.html$/.test(name) || name === 'preview.html') {res.writeHead(404);res.end('Introuvable');return;}
    try {
      if (['compte.html','mon-profil.html','rencontres.html','profil.html'].includes(name)) {
        const identity = await fetch(api + '/api/member/me',{headers:{cookie:req.headers.cookie || ''},signal:AbortSignal.timeout(5000)});
        if (identity.status === 401) {res.writeHead(302,{Location:'/connexion.html'});res.end();return;}
        if (!identity.ok) {res.writeHead(502);res.end('Espace membre indisponible');return;}
      }
      const response = await fetch(api + '/api/pages/' + name, {signal:AbortSignal.timeout(8000)});
      if (!response.ok) {res.writeHead(response.status === 404 ? 404 : 502);res.end('Page indisponible');return;}
      const page = await response.json();
      res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','X-Content-Type-Options':'nosniff'});
      res.end(page.html);
    } catch {res.writeHead(502);res.end('Page indisponible');}
    return;
  }
  const full = path.resolve(root,name);
  if (!full.startsWith(root + path.sep) || /(^|\/)(\.|backend|content|docs|scripts|previews|node_modules)(\/|$)/.test(name) || !Object.hasOwn(mime,path.extname(full)) || !fs.existsSync(full) || !fs.statSync(full).isFile()) {res.writeHead(404);res.end('Introuvable');return;}
  res.writeHead(200,{'Content-Type':mime[path.extname(full)]||'application/octet-stream','X-Content-Type-Options':'nosniff',...(name.startsWith('admin/')?{'Cache-Control':'no-store','Content-Security-Policy':"default-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'"}:{})});
  fs.createReadStream(full).pipe(res);
}).listen(port,'0.0.0.0',()=>console.log(`KINQ listening on ${port}`));
