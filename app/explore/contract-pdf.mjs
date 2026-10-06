import {contractSections, modelFor} from './contract-model.mjs';

export async function contractPdf(draft) {
  const [{PDFDocument,rgb},fontkit] = await Promise.all([import('pdf-lib'),import('@pdf-lib/fontkit')]);
  const doc = await PDFDocument.create();
  doc.registerFontkit(fontkit.default);
  const load = async url => {const r = await fetch(url);if (!r.ok) throw new Error('Une ressource du PDF est indisponible. Réessaie.');return r.arrayBuffer();};
  const [titleBytes,bodyBytes,logoBytes] = await Promise.all([
    load('/assets/fonts/BarlowCondensed-Bold.ttf'),load('/assets/fonts/DMSans-Regular.ttf'),load('/assets/kinq-logo-print.png'),
  ]);
  const titleFont = await doc.embedFont(titleBytes,{subset:true});
  const bodyFont = await doc.embedFont(bodyBytes,{subset:true});
  const logo = await doc.embedPng(logoBytes);
  const ink=rgb(.09,.10,.09),muted=rgb(.37,.39,.36),line=rgb(.84,.85,.82);
  const width=595.28,height=841.89,margin=48,available=width-margin*2;
  let page,y;
  function wrap(text,font,size,maxWidth=available) {
    const lines=[];
    for (const paragraph of text.split('\n')) {
      let current='';
      for (const word of paragraph.split(/\s+/).filter(Boolean)) {
        const pieces=[];let piece='';
        for (const char of word) {if (font.widthOfTextAtSize(piece+char,size)>maxWidth) {pieces.push(piece);piece=char;} else piece+=char;}
        if (piece) pieces.push(piece);
        for (const token of pieces) {
          const next=current ? `${current} ${token}` : token;
          if (font.widthOfTextAtSize(next,size)>maxWidth && current) {lines.push(current);current=token;} else current=next;
        }
      }
      lines.push(current);
    }
    return lines;
  }
  function newPage() {
    page=doc.addPage([width,height]);
    const first=doc.getPageCount()===1,top=height-46,brandWidth=108,brandX=width-margin-brandWidth,wordmarkX=brandX+brandWidth*.35;
    const size=first ? 32 : 20,leading=first ? 35 : 24;
    const heading=wrap(modelFor(draft.model).title,titleFont,size,available-167);
    let titleY=top-size;
    for (const text of heading) {page.drawText(text,{x:margin,y:titleY,font:titleFont,size,color:ink});titleY-=leading;}
    page.drawText('Powered by',{x:wordmarkX,y:top-6,font:bodyFont,size:7.5,color:muted});
    page.drawImage(logo,{x:brandX,y:top-13-brandWidth*logo.height/logo.width,width:brandWidth,height:brandWidth*logo.height/logo.width});
    const tagline='Make it kinky.';
    page.drawText(tagline,{x:wordmarkX,y:top-60,font:titleFont,size:brandWidth*18/166,color:ink});
    const url='kinq-app.com';
    page.drawText(url,{x:wordmarkX,y:top-71,font:bodyFont,size:7.5,color:muted});
    const divider=Math.min(titleY+leading-18,top-80);
    page.drawLine({start:{x:margin,y:divider},end:{x:width-margin,y:divider},thickness:.6,color:line});
    y=divider-27;
  }
  function ensure(space) {if (!page || y-space<62) newPage();}
  newPage();
  contractSections(draft).forEach((section,index)=>{
    const heading=wrap(`${String(index+1).padStart(2,'0')} / ${section.title}`,titleFont,16);
    const lines=wrap(section.text,bodyFont,10.5);
    ensure(Math.min(heading.length*18+2+lines.length*14.5+8,170));
    for (const text of heading) {page.drawText(text,{x:margin,y,font:titleFont,size:16,color:ink});y-=18;}
    y-=2;
    for (const text of lines) {ensure(14.5);page.drawText(text,{x:margin,y,font:bodyFont,size:10.5,color:ink});y-=14.5;}
    y-=8;
  });
  const names=[draft.nameA,draft.nameB].map((name,index)=>wrap(name.trim() || `Personne ${index+1}`,bodyFont,10,available/2-20));
  const nameHeight=(Math.max(...names.map(lines=>lines.length))-1)*12;
  ensure(85+nameHeight);
  page.drawText('SIGNATURES',{x:margin,y,font:titleFont,size:18,color:ink});y-=26;
  for (const [index,lines] of names.entries()) {
    const x=margin+index*(available/2+10);
    lines.forEach((name,lineIndex)=>page.drawText(name,{x,y:y-lineIndex*12,font:bodyFont,size:10,color:ink}));
    page.drawText('Date : __________________',{x,y:y-23-nameHeight,font:bodyFont,size:9,color:muted});
    page.drawLine({start:{x,y:y-55-nameHeight},end:{x:x+available/2-20,y:y-55-nameHeight},thickness:.6,color:line});
  }
  for (const [index,p] of doc.getPages().entries()) {
    p.drawLine({start:{x:margin,y:44},end:{x:width-margin,y:44},thickness:.6,color:line});
    p.drawText('Accord personnel de jeu',{x:margin,y:28,font:bodyFont,size:8,color:muted});
    const number=`${index+1} / ${doc.getPageCount()}`;
    p.drawText(number,{x:width-margin-bodyFont.widthOfTextAtSize(number,8),y:28,font:bodyFont,size:8,color:muted});
  }
  doc.setTitle(modelFor(draft.model).title);doc.setAuthor('Kinq');doc.setSubject('Accord personnel à personnaliser');
  return new Blob([await doc.save()],{type:'application/pdf'});
}
