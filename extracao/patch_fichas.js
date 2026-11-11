// ---------- fichas técnicas: curvas desenhadas em vetor (KSB, Grundfos, …) lidas sem cliques ----------
// 1) traços do PDF (pdf.js, operator list) com cor e espessura; 2) eixos pelas etiquetas numéricas em progressão aritmética;
// 3) painel de cada eixo (H, P, NPSH, η) pelo texto ao lado; 4) curvas: traços unidos pela cor, contínuos em Q; 5) Ø pela legenda (cor) ou pela etiqueta junto à curva
const FLOWRE=/m[3³]\s*\/\s*h|\bl\/s\b|\bgpm\b/i;
const VNUM=/^-?\d+(?:[.,]\d+)?$/;
async function vecPaths(pg){
  const ol=await pg.getOperatorList(),O=pdfjsLib.OPS,U=pdfjsLib.Util,out=[],texts=[];
  let g={m:[1,0,0,1,0,0],lw:1,col:"#000000",fc:"#000000"},stack=[],path=[],cur=null;
  const P=(x,y)=>{const m=g.m;return[m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]]};
  const hex=a=>typeof a[0]==="string"?a[0]:"#"+Array.from(a).slice(0,3).map(v=>Math.round(v).toString(16).padStart(2,"0")).join("");
  const emit=()=>{const k=Math.sqrt(Math.abs(g.m[0]*g.m[3]-g.m[1]*g.m[2]))||1;
    for(const s of path)if(s.length>=2)out.push({p:s,col:g.col.toLowerCase(),lw:+(g.lw*k).toFixed(2)});path=[];cur=null};
  for(let i=0;i<ol.fnArray.length;i++){const fn=ol.fnArray[i],a=ol.argsArray[i];
    if(fn===O.save)stack.push({...g});
    else if(fn===O.restore){if(stack.length)g=stack.pop()}
    else if(fn===O.transform)g.m=U.transform(g.m,a);
    else if(fn===O.paintFormXObjectBegin){stack.push({...g});if(a&&a[0])g.m=U.transform(g.m,a[0])}
    else if(fn===O.paintFormXObjectEnd){if(stack.length)g=stack.pop()}
    else if(fn===O.setLineWidth)g.lw=a[0];
    else if(fn===O.setStrokeRGBColor)g.col=hex(a);
    else if(fn===O.setFillRGBColor)g.fc=hex(a).toLowerCase();
    else if(fn===O.showText||fn===O.showSpacedText){const gl=fn===O.showText?a[0]:a[0].filter(x=>typeof x!=="number");texts.push({s:gl.map(x=>x&&x.unicode||"").join(""),fc:g.fc})}
    else if(fn===O.constructPath){const ops=a[0],c=a[1];let j=0;
      for(const op of ops){
        if(op===O.moveTo){cur=[P(c[j],c[j+1])];path.push(cur);j+=2}
        else if(op===O.lineTo){if(!cur){cur=[];path.push(cur)}cur.push(P(c[j],c[j+1]));j+=2}
        else if(op===O.curveTo){if(cur){cur.push(P((c[j]+c[j+2])/2*0.75+c[j+4]*0.25,(c[j+1]+c[j+3])/2*0.75+c[j+5]*0.25));cur.push(P(c[j+4],c[j+5]))}j+=6}
        else if(op===O.curveTo2||op===O.curveTo3){if(cur)cur.push(P(c[j+2],c[j+3]));j+=4}
        else if(op===O.rectangle){const[x,y,w,h]=c.slice(j,j+4);cur=[P(x,y),P(x+w,y),P(x+w,y+h),P(x,y+h),P(x,y)];path.push(cur);cur=null;j+=4}
        else if(op===O.closePath){if(cur&&cur.length)cur.push(cur[0])}}}
    else if(fn===O.stroke||fn===O.closeStroke||fn===O.fillStroke||fn===O.eoFillStroke||fn===O.closeFillStroke||fn===O.closeEOFillStroke)emit();
    else if(fn===O.fill||fn===O.eoFill||fn===O.endPath){path=[];cur=null}}
  return{paths:out,texts}}
// texto letra a letra (PDFium e outros) → palavras: junta os pedaços seguidos na mesma linha
function vecMerge(items){const L=[...items].filter(it=>it.s!=null).sort((a,b)=>b.y-a.y||a.x-b.x),out=[];
  for(const it of L){const p=out[out.length-1],h=it.h||8;
    if(!String(it.s).trim()){if(p&&Math.abs(p.y-it.y)<0.3*h&&!/\s$/.test(p.s))p.s+=" ";continue} // espaços: alguns PDF dão-lhes larguras absurdas
    if(p&&Math.abs(p.y-it.y)<0.3*h&&it.x>=p.x+p.w-0.3*h&&it.x-(p.x+p.w)<0.12*h){p.s+=it.s;p.w=Math.max(p.w,it.x+it.w-p.x)}
    else out.push({...it})}
  return out}
// junta os traços da mesma cor que continuam uns nos outros (os programas partem as curvas em pedaços)
function vecJoin(S){const by=new Map();S.forEach(s=>{const k=s.col;if(!by.has(k))by.set(k,[]);by.get(k).push({p:s.p.slice(),col:s.col,lw:s.lw})});
  const d=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]),out=[];
  for(const L of by.values()){
    let ch=true;while(ch){ch=false;
      for(let i=0;i<L.length;i++)for(let j=0;j<L.length;j++){if(i===j)continue;const A=L[i],B=L[j],ae=A.p[A.p.length-1];
        if(d(ae,B.p[0])<1.2){A.p.push(...B.p.slice(1));A.lw=Math.max(A.lw,B.lw);L.splice(j,1);ch=true;break}
        if(d(ae,B.p[B.p.length-1])<1.2&&B.p.length>2){A.p.push(...B.p.slice(0,-1).reverse());A.lw=Math.max(A.lw,B.lw);L.splice(j,1);ch=true;break}}}
    out.push(...L)}
  return out}
// eixos: números alinhados cujo valor é linear na posição (RANSAC sobre pares vizinhos)
function vecAxes(tok,dir){ // dir "y": colunas alinhadas à direita; "x": linhas
  const key=t=>dir==="y"?t.x1:t.y,pos=t=>dir==="y"?t.y:t.x,groups=[];
  [...tok].sort((a,b)=>key(a)-key(b)).forEach(t=>{const g=groups.find(g=>Math.abs(g.k-key(t))<(dir==="y"?2.5:2));if(g)g.t.push(t);else groups.push({k:key(t),t:[t]})});
  const axes=[];
  for(const g of groups){let L=g.t.filter((t,i,a)=>a.findIndex(u=>u.v===t.v&&Math.abs(pos(u)-pos(t))<1)===i).sort((a,b)=>pos(a)-pos(b));
    while(L.length>=2){let best=null;
      for(let i=0;i+1<L.length;i++){const a=L[i],b=L[i+1];if(a.v===b.v||Math.abs(pos(b)-pos(a))<3)continue;const s=(b.v-a.v)/(pos(b)-pos(a)),tol=Math.abs(b.v-a.v)*0.04;
        const m=L.filter(t=>Math.abs(a.v+s*(pos(t)-pos(a))-t.v)<=tol);if(!best||m.length>best.m.length)best={m,s,a}}
      if(!best||best.m.length<2)break;
      let m=best.m;
      if(m.length>=4){const ps=m.map(pos).sort((a,b)=>a-b),gs=ps.slice(1).map((v,i)=>v-ps[i]).sort((a,b)=>a-b),g=gs[gs.length>>1];
        const ms=[...m].sort((a,b)=>pos(a)-pos(b)),seg=[[ms[0]]];for(let i=1;i<ms.length;i++){if(pos(ms[i])-pos(ms[i-1])>1.8*g)seg.push([]);seg[seg.length-1].push(ms[i])}
        m=seg.reduce((a,b)=>b.length>a.length?b:a)} // só os números seguidos: uma etiqueta solta de outro eixo não entra
      if(m.length>=2&&(dir==="x"||best.s>0))axes.push({dir,k:g.k,s:best.s,v0:best.a.v-best.s*pos(best.a),lo:Math.min(...m.map(pos)),hi:Math.max(...m.map(pos)),n:m.length,t:m});
      L=L.filter(t=>!m.includes(t))}}
  return axes}
function vecTokens(items){const T=[];
  for(const it of items){const s=String(it.s||"").replace(/\s+$/,"");if(!s.trim())continue;const cw=it.w/Math.max(s.length,1),re=/\S+/g;let m;
    while((m=re.exec(s))){if(!(cw>0&&cw<1.2*(it.h||8))){T.push({t:m[0],x0:it.x,x1:it.x+0.55*(it.h||8)*m[0].length,x:it.x+0.275*(it.h||8)*m[0].length,y:it.y+(it.h||8)*0.35,h:it.h||8});continue}
      T.push({t:m[0],x0:it.x+cw*m.index,x1:it.x+cw*(m.index+m[0].length),x:it.x+cw*(m.index+m[0].length/2),y:it.y+(it.h||8)*0.35,h:it.h||8})}}
  T.forEach(t=>{if(VNUM.test(t.t))t.v=parseFloat(t.t.replace(",","."))});return T}
const vecKind=s=>{s=s.toLowerCase();if(/\bft\b|\[ft\]|\bhp\b|psi|\[%\]/.test(s))return null;if(/npsh/.test(s))return"N";if(/eta|η|eff|rend/.test(s)&&!/\bh\b/.test(s))return"E";if(/\bp\s*2?\b|\bp2\b|kw|power|pot[eê]ncia|leistung/.test(s))return"P";if(/\bh\b|head|altura|förderh/.test(s))return"H";return null};
async function vecRead(pg,items0,page,ptx){
  const ln=items0.map(it=>String(it.s).trim().length).filter(Boolean).sort((a,b)=>a-b),perChar=ln.length&&ln[ln.length>>1]<=1;
  const items=perChar?vecMerge(items0):items0,T=vecTokens(items),nums=T.filter(t=>t.v!=null),words=T.filter(t=>t.v==null);
  // eixo dos caudais: linha de números com unidade de caudal na mesma linha
  let qx=null;
  for(const a of vecAxes(nums,"x")){if(a.n<3)continue;const row=words.filter(w=>Math.abs(w.y-a.k)<4).map(w=>w.t).join(" ");
    const u=/m[3³]\s*\/\s*h|m[3³]h/i.test(row)?1:/l\/s/i.test(row)?3.6:/us\.?\s*gpm/i.test(row)?0.22712:/gpm/i.test(row)?0.272765:null;
    if(u==null)continue;const sc={...a,u};if(!qx||(sc.u===1)>(qx.u===1)||((sc.u===1)===(qx.u===1)&&sc.n>qx.n))qx=sc}
  if(!qx)return[];
  const Qof=x=>(qx.v0+qx.s*x)*qx.u,xMin=qx.lo-0.6*(qx.hi-qx.lo)/Math.max(qx.n-1,1),xMax=qx.hi+0.6*(qx.hi-qx.lo)/Math.max(qx.n-1,1);
  // painéis: eixos verticais à esquerda do gráfico, com o tipo lido no texto ao lado
  const panels=[];
  for(const a of vecAxes(nums,"y")){if(a.k>qx.lo+0.25*(qx.hi-qx.lo))continue;const step=(a.hi-a.lo)/Math.max(a.n-1,1);
    // título por cima da escala (KSB: "H / m") ou ao lado, a meia altura (catálogos: "H [m]")
    const th=a.t[0].h||8,above=words.filter(w=>w.x0<a.k+40&&w.x1>a.k-90&&w.y>a.hi+1&&w.y<a.hi+3.6*th).map(w=>w.t).join(" "),
      side=words.filter(w=>w.x1<=a.k+2&&w.x1>a.k-90&&w.y>=a.lo-2&&w.y<=a.hi+2).map(w=>w.t).join(" ");
    const kind=vecKind(above)||vecKind(side)||(/\[m\]|\/\s*m/.test(above+" "+side)?"H":null);if(!kind)continue;if(a.n<3&&kind!=="N")continue;
    panels.push({kind,a,y0:a.lo-0.7*step,y1:a.hi+0.7*step,V:y=>a.v0+a.s*y})}
  if(!panels.some(p=>p.kind==="H"))return[];
  const VP=await vecPaths(pg),raw=VP.paths,lines=vecJoin(raw.filter(s=>s.p.length>=2));
  // legenda por cor: Ø ao lado de um traço curto da mesma cor
  const diaRe=/[øØ⌀]\s*(\d+(?:[.,]\d+)?)/,dia=[];
  items.forEach(it=>{const m=String(it.s).match(diaRe);if(m)dia.push({D:parseFloat(m[1].replace(",",".")),lab:it.s.trim(),x:it.x,y:it.y+(it.h||8)*0.35,x1:it.x+it.w})});
  const legend=new Map(),norm=s=>String(s).replace(/[\s—–-]+/g,"");
  dia.forEach(t=>{const x=VP.texts.find(x=>norm(x.s)===norm(t.lab)||norm(x.s).endsWith(norm(t.lab).replace(/^[^øØ⌀]*/,"")));if(x&&!legend.has(x.fc))legend.set(x.fc,t)});
  raw.forEach(s=>{if(s.p.length!==2&&s.p.length!==3)return;const[a,b]=[s.p[0],s.p[s.p.length-1]];if(Math.abs(a[1]-b[1])>1||Math.abs(a[0]-b[0])>45||Math.abs(a[0]-b[0])<4)return;
    const xr=Math.max(a[0],b[0]),t=dia.find(t=>t.x>xr-2&&t.x<xr+14&&Math.abs(t.y-a[1])<5);if(t&&!legend.has(s.col))legend.set(s.col,t)});
  const grey=c=>{const r=parseInt(c.slice(1,3),16),g=parseInt(c.slice(3,5),16),b=parseInt(c.slice(5,7),16);return Math.max(r,g,b)-Math.min(r,g,b)<20};
  const curves=[];
  for(const pn of panels){
    let C=lines.map(l=>{const pts=l.p.filter(p=>p[1]>=pn.y0-2&&p[1]<=pn.y1+2&&p[0]>=xMin-2&&p[0]<=xMax+2);if(pts.length<4||pts.length<0.9*l.p.length)return null;
        let back=0;for(let i=1;i<pts.length;i++)if(pts[i][0]<pts[i-1][0])back+=pts[i-1][0]-pts[i][0];
        const xs=pts.map(p=>p[0]),span=Math.max(...xs)-Math.min(...xs);if(span<0.2*(xMax-xMin)||back>0.03*span)return null;
        const ys=pts.map(p=>p[1]);if(Math.max(...ys)-Math.min(...ys)<0.015*(pn.y1-pn.y0))return null; // linhas horizontais (grelha, marcações)
        const s=[...pts].sort((p,q)=>p[0]-q[0]),Q=s.map(p=>Qof(p[0])),V=s.map(p=>pn.V(p[1]));
        if(pn.kind==="H"&&!(V[V.length-1]<V[0]-0.02*Math.abs(V[0])))return null;
        if((pn.kind==="P"||pn.kind==="N")&&!(V[V.length-1]>V[0]))return null;
        return{col:l.col,lw:l.lw,Q,V,pts:s,kind:pn.kind}}).filter(Boolean);
    if(C.some(c=>!grey(c.col)))C=C.filter(c=>!grey(c.col));else{const mx=Math.max(0,...C.map(c=>c.lw));C=C.filter(c=>c.lw>=0.8*mx)}
    // etiqueta: legenda pela cor ou Ø mais perto da curva
    C.forEach(c=>{let t=legend.get(c.col);
      if(!t){let bd=26;dia.forEach(d=>{const e=c.pts[c.pts.length-1],dd=Math.min(Math.hypot(d.x-e[0],d.y-e[1]),...c.pts.filter((_,i)=>i%3===0).map(p=>Math.min(Math.hypot(d.x-p[0],d.y-p[1]),Math.hypot(d.x1-p[0],d.y-p[1]))));if(dd<bd){bd=dd;t=d}})}
      c.D=t?t.D:null;c.lab=t?t.lab.replace(/^[\s—–-]+/,"").replace(/\s+/g," ").replace(/^[øØ⌀]\s+/,"Ø"):""});
    curves.push(...C)}
  const H=curves.filter(c=>c.kind==="H");if(!H.length)return[];
  // modelo e velocidade
  const L=linesFrom(items),title=(()=>{const a=L.find(l=>/pump type|tipo de bomba|baureihe/i.test(l.text));if(a)return a.text.replace(/.*?(pump type|tipo de bomba|baureihe)\s*:?\s*/i,"");
      const b=L.find(l=>/,\s*n\s*=\s*\d+/i.test(l.text));if(b)return b.text.split(",")[0];return""})().trim().slice(0,70);
  const rm=items.map(it=>it.s).join(" ").match(/(\d{3,4}(?:[.,]\d+)?)\s*(?:rpm|1\/min|min-1|min⁻¹|r\/min)/i),rpm=rm&&+rm[1].replace(",",".")>300&&+rm[1].replace(",",".")<4000?+rm[1].replace(",","."):null;
  // P, NPSH e η de cada Ø: pela cor da legenda; com curvas todas da mesma cor, pelo caudal final mais próximo (as curvas de um Ø acabam no mesmo Q)
  const byCol=legend.size&&H.every(h=>legend.has(h.col)),match={};
  for(const k of["P","N","E"]){const K=curves.filter(c=>c.kind===k);match[k]=new Map();
    if(byCol)H.forEach(h=>{const c=K.find(c=>c.col===h.col);if(c)match[k].set(h,c)});
    else{const pairs=[];H.forEach(h=>K.forEach(c=>pairs.push([Math.abs(c.Q[c.Q.length-1]-h.Q[h.Q.length-1])/h.Q[h.Q.length-1],h,c])));pairs.sort((a,b)=>a[0]-b[0]);
      const uh=new Set(),uc=new Set();for(const[d,h,c]of pairs){if(d>0.08||uh.has(h)||uc.has(c))continue;match[k].set(h,c);uh.add(h);uc.add(c)}}}
  return H.map((h,i)=>({page,title,rpm,D:h.D,lab:h.lab,idx:i,H:h,P:match.P.get(h),N:match.N.get(h),E:match.E.get(h)}))}
// curvas lidas → bombas (16 pontos entre o primeiro e o último caudal da curva H)
function pumpsFromVec(V,c,rpm0){const out=[],at=(cv,q)=>cv&&q>=cv.Q[0]-1e-9&&q<=cv.Q[cv.Q.length-1]+1e-9?interp(cv.Q,cv.V,q):null;
  V.forEach((v,vi)=>{const h=v.H,q0=Math.max(0,h.Q[0]),q1=h.Q[h.Q.length-1],n=16,ok=[];
    const pCov=v.P?(Math.min(q1,v.P.Q[v.P.Q.length-1])-Math.max(q0,v.P.Q[0]))/(q1-q0):0;
    for(let i=0;i<n;i++){const q=+(q0+(q1-q0)*i/(n-1)).toFixed(3),H=interp(h.Q,h.V,q);let e=null;
      if(v.E)e=interp(v.E.Q,v.E.V,q);else if(v.P&&pCov>0.9){const p=interp(v.P.Q,v.P.V,q);e=q>0&&p>0?G*q/3.6*H/p/10:0}
      ok.push([q,+H.toFixed(3),e==null?null:+clamp(e,0,95).toFixed(2),v.N?at(v.N,q):null])}
    const name=v.title||c.name,lab=v.lab||(v.D!=null?"Ø"+v.D:"");
    out.push(mkPump({id:`${c.k}_v${vi}`,b:c.name,s:c.name,m:name,v:lab,D:v.D,n:v.rpm||rpm0||2900,pg:v.page,fam:c.k,src:c.name+" (curva lida do gráfico)"},ok))});
  return out}
