import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {affinity,buildSignature,chapters,questionCount,signatureText,universeCount} from '../app/explore/signature-model.mjs';
const catalogue = JSON.parse(fs.readFileSync(new URL('../content/profile-kinks.json',import.meta.url),'utf8'));

test('unknown and missing are distinct from an explicit zero',()=>{
  assert.equal(affinity([null,undefined,NaN,5,-1]),null);
  assert.equal(affinity([0]),0);
  assert.equal(affinity([3]),75);
  const empty=buildSignature({leather:{kiff:null}},catalogue);
  assert.equal(empty.answered.length,0);
  assert.equal(empty.responseCount,0);
  assert.equal(empty.title,'Tes affinités restent à découvrir');
});

test('one personal answer determines affinity; experience and roles add no points',()=>{
  const missing=buildSignature({leather:{attraction:4,place:4,role:'wear',experience:'regular'}},catalogue);
  assert.equal(missing.answered.length,0);
  const result=buildSignature({leather:{kiff:2,experience:'regular',role:'wear'}},catalogue);
  assert.equal(result.answered[0].score,50);
  assert.equal(result.answered[0].experience,'Dans mes habitudes');
  assert.equal(result.answered[0].role,'J’aime en porter');
  assert.equal(result.lead,null);
});

test('the title lists strongest fetish affinities without assigning a BDSM role',()=>{
  const result=buildSignature({'rubber-latex':{kiff:4},leather:{kiff:3},bondage:{kiff:0}},catalogue);
  assert.equal(result.title,'Rubber · Cuir');
  assert.equal(result.answered.length,3);
  assert.deepEqual(result.ranked.map(item=>item.score),[100,75]);
  assert.equal(result.positiveTraits.length,0);
  assert.equal(result.traits.find(item=>item.key==='switch').score,null);
});

test('Dom, Sub and Switch follow direct power answers instead of fetish preferences',()=>{
  const kinks={leather:{kiff:4},bondage:{kiff:3}};
  const dom=buildSignature({...kinks,dynamics:{lead:4,follow:0}},catalogue);
  assert.equal(dom.title,'Cuir · Bondage');
  assert.equal(dom.lead,100);
  assert.equal(dom.follow,0);
  const sub=buildSignature({...kinks,dynamics:{lead:1,follow:3}},catalogue);
  assert.equal(sub.positiveTraits.find(item=>item.key==='follow').score,75);
  assert.equal(sub.positiveTraits.some(item=>item.key==='lead'),false);
  const both=buildSignature({...kinks,dynamics:{lead:4,follow:3}},catalogue);
  assert.equal(both.traits.find(item=>item.key==='switch').score,75);
  assert.equal(both.responseCount,4);
});

test('pain and provocation produce separate names without silently assigning Dom or Sub',()=>{
  const maso=buildSignature({dynamics:{lead:0,follow:0,masochism:4}},catalogue);
  assert.equal(maso.title,'Masochiste');
  assert.equal(maso.follow,0);
  const sadist=buildSignature({dynamics:{sadism:3}},catalogue);
  assert.equal(sadist.title,'Sadique');
  const brat=buildSignature({dynamics:{follow:2,brat:4}},catalogue);
  assert.equal(brat.title,'Brat · Sub');
  const tamer=buildSignature({dynamics:{lead:2,tamer:4}},catalogue);
  assert.equal(tamer.title,'Brat tamer · Dom');
});

test('empty and weak answers stay descriptive without an invented profile name',()=>{
  for(const answers of [{},{leather:{kiff:0}},{leather:{kiff:1}},{dynamics:{curiosity:3}},{leather:{kiff:4}}]){
    const result=buildSignature(answers,catalogue);
    assert.ok(result.title.trim());
    assert.doesNotMatch(result.title,/hiérarchie|hierarchie/);
  }
  assert.equal(buildSignature({dynamics:{curiosity:3}},catalogue).title,'Explorateur');
});

test('selective sharing excludes other universes, traits and raw answers',()=>{
  const result=buildSignature({leather:{kiff:4},bondage:{kiff:3},dynamics:{lead:4,follow:0}},catalogue);
  const text=signatureText(result,['leather']);
  assert.match(text,/Ma KINQ Signature/);
  assert.match(text,/100 %/);
  assert.doesNotMatch(text,/Bondage|Dom|Sub|lead|kiff:|attraction|place/);
  assert.match(text,/Powered by Kinq - Rencontres fetish - kinq-app\.com$/);
  assert.doesNotMatch(text,/consent|PNG|carte|Déjà|habitudes/);
  const traits=signatureText(result,['trait-lead']);
  assert.match(traits,/Dom : 100 %/);
  assert.doesNotMatch(traits,/Cuir|Bondage/);
});

test('the constraint regression names the actual strongest kinks, not their family',()=>{
  const result=buildSignature({bondage:{kiff:4},'rope-shibari':{kiff:3},'privation-sensorielle':{kiff:2},dynamics:{lead:0,follow:0}},catalogue);
  assert.equal(result.title,'Bondage · Cordes · Privation sensorielle');
  assert.doesNotMatch(result.title,/hiérarchie|Contrainte|Signature libre/);
  assert.deepEqual(result.ranked.map(item=>item.score),[100,75,50]);
});

test('the initial text selection contains at most five strongest scores in descending order',()=>{
  const result=buildSignature({leather:{kiff:4},bondage:{kiff:3},'rubber-latex':{kiff:2},sportswear:{kiff:0},feet:{kiff:null},dynamics:{lead:4,follow:3,brat:1}},catalogue);
  assert.equal(result.topScores.length,5);
  assert.deepEqual(result.topScores.map(item=>item.score),[100,100,75,75,75]);
  assert.equal(result.topScores.some(item=>['sportswear','feet','trait-brat'].includes(item.id)),false);
  const text=signatureText(result,result.topScores.map(item=>item.id));
  assert.doesNotMatch(text,/Sportswear|Pieds|Brat|Latex/);
  assert.equal(text.split('\n').length,8);
});

test('the expanded questionnaire keeps shared catalogue IDs, roles and pictograms',()=>{
  for(const item of catalogue) assert.ok(fs.existsSync(new URL('../assets/pictos/'+item.icon+'.svg',import.meta.url)),item.id);
  const ids=chapters.flatMap(chapter=>chapter.items.map(item=>item.id));
  assert.equal(new Set(ids).size,ids.length);
  for(const id of ids) assert.ok(catalogue.some(item=>item.id===id),id);
  assert.equal(universeCount,36);
  assert.equal(questionCount,44);
});
