/* Run with: node --test tests/c2-visual.test.cjs */
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const R = path.resolve(__dirname, "..");
const C = require(path.join(R, "demo/c2-core.js"));

function sample(n, points) {
  const a = new Float64Array(n*n);
  for (const [x,y,value=1] of points) a[y*n+x]=value;
  return a;
}
function eq(a,b,tol=1e-12) {
  assert.equal(a.length,b.length);
  for(let i=0;i<a.length;i++) assert.ok(Math.abs(a[i]-b[i])<=tol, "Mismatch at "+i+": "+a[i]+" vs "+b[i]);
}

test("R² = identity for interior data on an integer pixel centre", () => {
  const n=11, source=sample(n,[[2,3],[7,4,.4],[5,5]]);
  const rotated=C.rotate(source,n,5.5,5.5);
  assert.equal(rotated.clipped,0);
  eq(C.rotate(rotated.pixels,n,5.5,5.5).pixels,source);
});

test("C2 even stays invariant and odd changes sign",()=>{
  const n=11, source=sample(n,[[2,3],[4,5,.2],[8,7,.8]]);
  const d=C.decompose(source,n,5.5,5.5);
  eq(C.rotate(d.even,n,5.5,5.5).pixels,d.even);
  const flipped=C.rotate(d.odd,n,5.5,5.5).pixels;
  for(let i=0;i<flipped.length;i++) assert.ok(Math.abs(flipped[i]+d.odd[i])<1e-12);
  eq(C.interpolate(d,1),source);
  eq(C.interpolate(d,-1),d.rotated);
  eq(C.interpolate(d,0),d.even);
});

test("perfectly symmetric and asymmetric shapes have distinct metrics",()=>{
  const n=9;
  const symmetric=sample(n,[[2,3],[6,5]]);
  const s=C.decompose(symmetric,n,4.5,4.5);
  assert.equal(s.relativeDifference,0);
  assert.equal(s.binaryIoU,1);
  const single=sample(n,[[2,3]]);
  const a=C.decompose(single,n,4.5,4.5);
  assert.equal(a.relativeDifference,1);
  assert.equal(a.binaryIoU,0);
});

test("moving the centre changes overlap but preserves interior C2 involution",()=>{
  const n=13, source=sample(n,[[4,6],[8,6]]);
  const centered=C.decompose(source,n,6.5,6.5);
  const shifted=C.decompose(source,n,7.5,6.5);
  assert.equal(centered.binaryIoU,1);
  assert.ok(shifted.binaryIoU < 1);
  eq(C.rotate(C.rotate(source,n,7.5,6.5).pixels,n,7.5,6.5).pixels,source);
});

test("cropped rotational ink is surfaced, never silently interpreted as perfect",()=>{
  const n=9, source=sample(n,[[0,0],[7,7]]);
  const r=C.rotate(source,n,6.5,6.5);
  assert.ok(r.clipped>0);
  const d=C.decompose(source,n,6.5,6.5);
  assert.ok(d.clipped>0);
});

test("inputs are validated and empty field is C2 symmetric by convention",()=>{
  assert.throws(()=>C.rotate([1,2],2,1,1),/square raster/);
  assert.throws(()=>C.interpolate({source:[1],even:[1],odd:[0]},2),/[-]1, 1/);
  const d=C.decompose(new Float64Array(9),3,1.5,1.5);
  assert.equal(d.relativeDifference,0);
  assert.equal(d.binaryIoU,1);
});

test("shared KanjiVG geometry, local static assets and tri-language labels",()=>{
  const catalogue=fs.readFileSync(path.join(R,"demo/kanjivg-geometry.js"),"utf8");
  const globals={window:{}};
  vm.runInNewContext(catalogue,globals,{timeout:1000});
  const paths=globals.window.SINOGRAM_KANJIVG_PATHS;
  assert.equal(Object.keys(paths).length,20);
  for(const c of ["甲","由","回","田","目","国","上","下","昌","吉","王","玉"]){
    assert.ok(Array.isArray(paths[c]) && paths[c].length>0,"Missing "+c);
    assert.ok(paths[c].every(s=>typeof s==="string" && s[0]==="M"));
  }
  const oldPage=fs.readFileSync(path.join(R,"demo/index.html"),"utf8");
  assert.match(oldPage,/src="kanjivg-geometry.js"/);
  assert.match(oldPage,/const PATHS=window.SINOGRAM_KANJIVG_PATHS/);
  const html=fs.readFileSync(path.join(R,"demo/c2/index.html"),"utf8");
  const app=fs.readFileSync(path.join(R,"demo/c2/app.js"),"utf8");
  const start=app.indexOf("  const UI = "), end=app.indexOf("\n  let lang =",start);
  assert.ok(start!==-1 && end>start);
  const ui=vm.runInNewContext("("+app.slice(start+"  const UI = ".length,end).replace(/;\s*$/,"")+")",{}, {timeout:1000});
  const keys=Object.keys(ui.en).sort();
  for(const language of ["zh","ja"]) assert.deepEqual(Object.keys(ui[language]).sort(),keys);
  for(const [,key] of html.matchAll(/data-i18n="([^"]+)"/g))
    assert.ok(Object.hasOwn(ui.en,key),"Missing translation key: "+key);
  for(const file of ["demo/kanjivg-geometry.js","demo/c2-core.js","demo/c2/app.js",
                     "demo/c2/style.css","demo/c2/index.html"])
    assert.ok(fs.statSync(path.join(R,file)).size>100,file+" absent");
  for(const [,target] of html.matchAll(/(?:src|href)="([^"]+)"/g)){
    if(/^(https?:|#)/.test(target))continue;
    assert.ok(fs.existsSync(path.resolve(R,"demo/c2",target.split("?")[0])),
              "Broken local link: "+target);
  }
});
