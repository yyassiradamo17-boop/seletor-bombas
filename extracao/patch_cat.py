# v12: aba Catálogo — o utilizador importa catálogos PDF e fichas próprias (só na sessão); sai a base embutida, fica um catálogo de exemplo
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
p = 'seletor-bombas.html'; s = open(p, encoding='utf8').read()
assert 'id="c_drop"' not in s, 'já aplicado'

# ---- base embutida → catálogo de exemplo (KSB Etanorm 2900 rpm, tamanhos 050 a 100) ----
i = s.index('const DB='); j = s.index('\n', i)
DB = json.loads(s[i + 9:j].rstrip(';'))
EX = [x for x in DB if x['b'] == 'KSB' and x['s'] == 'Etanorm' and x['n'] == 2900 and re.match(r'Etanorm (050-032|065-0[45]0|080-065|100-080)-', x['m'])]
print('exemplo:', len(EX), 'curvas,', len({x['m'] for x in EX}), 'modelos (de', len(DB), ')')
s = s[:i] + 'const DB=' + json.dumps(EX, ensure_ascii=False, separators=(',', ':')) + ';' + s[j:]

IMP = '''    <section class="panel imp" aria-label="Importar catálogos">
      <label class="drop big" id="c_drop" for="c_file">
        <svg viewBox="0 0 44 54" aria-hidden="true"><path d="M3 2h26l12 12v38H3z" fill="none" stroke="var(--ink)" stroke-width="2.2"/><path d="M29 2v12h12" fill="none" stroke="var(--ink)" stroke-width="2.2"/><path d="M12 25h18M12 41h18M21 25v16" fill="none" stroke="var(--oxide)" stroke-width="2.6"/></svg>
        <span><b>Importar catálogo em PDF</b><small>Clique ou arraste um ou mais ficheiros. O PDF tem de ter texto selecionável (catálogos digitalizados não são lidos).</small></span>
        <input type="file" id="c_file" accept="application/pdf,.pdf,image/png,image/jpeg,image/webp" multiple>
      </label>
      <div class="loaded">
        <div class="row"><p class="lbl" style="margin:0">Catálogos carregados</p><button class="mini" id="c_clear">remover todos</button></div>
        <div id="c_list" class="srcs"></div>
        <p class="hint" id="c_ex"></p>
        <span class="msg" id="c_msg"></span>
      </div>
    </section>
'''
rep = [
('''Catálogo<small>fontes e fichas próprias</small>''', '''Catálogo<small>importar catálogos e fichas</small>'''),
('''  <div class="view" id="v_cat" hidden>
    <div class="cat-grid">''', '''  <div class="view" id="v_cat" hidden>
''' + IMP + '''    <div class="cat-grid">'''),
('''.srcs em{''', '''.imp{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:18px;padding:14px 16px;margin-bottom:18px}
@media (max-width:900px){.imp{grid-template-columns:minmax(0,1fr)}}
.imp .loaded{display:flex;flex-direction:column;gap:10px;min-width:0;padding-top:4px}
.imp .loaded .hint:empty{display:none}
.drop.big{padding:22px 26px;min-height:120px;gap:22px}
.drop.big svg{width:44px;height:54px}
.drop.big b{font-size:22px}
.drop.big small{font-size:13px;max-width:52ch}
.srcs b{overflow-wrap:anywhere}
.srcs em{'''),
('''          <h2>Adicionar ficha técnica</h2>''', '''          <h2>Ficha própria</h2>'''),
('''          <label class="toggle" id="u_share_l"><input type="checkbox" id="u_share"> Partilhar com a equipa (base de dados do artefacto)</label>
''', ''),
('''          <div id="sh_box" style="display:flex;flex-direction:column;gap:6px">
            <div class="row"><p class="lbl" style="margin:0">Fichas da equipa</p><span class="msg" id="sh_msg"></span></div>
            <div id="sh_list" class="srcs"></div>
          </div>
''', ''),
# ---- JS: famílias = catálogos carregados ----
('''const famOf=p=>(FAMS.find(F=>F.f(p))||FAMS.find(F=>F.k==="U")).k;
const famName=k=>FAMS.find(F=>F.k===k).n;''',
 '''const famOf=p=>p.fam||"U";
const famName=k=>(FAMS.find(F=>F.k===k)||{n:"Fichas próprias"}).n;'''),
('''fam:new Set(["KSB","HS","CR","NBK","GSP","SP","EQ","U"]),cfam:new Set(["KSB","HS","CR","NBK","GSP","SP","EQ","U"])''',
 '''fam:new Set(["EX","U"]),cfam:new Set(["EX","U"])'''),
('''function srcOf(p){if(p.shared)return"Ficha da equipa";if(p.user)return"Ficha própria";const F={KSB:"KSB 1311.45/12-EN",HS:"Grundfos HS v5",CR:"Grundfos CR 60 Hz",NBK:"Grundfos NB/NK 50 Hz",GSP:"Grundfos SP 50 Hz",SP:"Speroni 2020 rev.14"}[famOf(p)];return `${F}, pág. ${p.pg}`}''',
 '''function srcOf(p){if(p.user)return"Ficha própria";return `${p.src}, pág. ${p.pg}`}'''),
('''function allPumps(){return DB.concat(st.user,SH.list)}''',
 '''function allPumps(){const L=CATS.flatMap(c=>c.pumps).concat(st.user);return L.length?L:DB}'''),
('''  $("srcs").innerHTML=FAMS.filter(F=>F.k!=="EQ"&&F.k!=="U").map(F=>{const n=DB.filter(F.f).length;const m=new Set(DB.filter(F.f).map(groupKey)).size;return `<div><b>${F.n}</b><span>${F.d}</span><em>${m} mod. · ${n} curvas</em></div>`}).join("");
''', ''),
(''' · só neste navegador</span><span>${SH.col?`<button class="mini" data-shr="${i}">partilhar</button> · `:""}<button class="mini" data-del="${i}">remover</button></span></div>`).join("");''',
 '''</span><button class="mini" data-del="${i}">remover</button></div>`).join("");'''),
('''  $("u_list").querySelectorAll("[data-shr]").forEach(b=>b.onclick=()=>{const p=st.user[+b.dataset.shr];if(!p)return;b.disabled=true;
    SH.col.add(toShared(p)).then(()=>{const i=st.user.indexOf(p);if(i>=0)st.user.splice(i,1);save();$("u_msg").textContent=`Partilhada com a equipa: ${p.m}.`;recompute()})
      .catch(e=>{b.disabled=false;$("u_msg").textContent=`Não foi possível partilhar (${e&&e.code||"erro"}); a ficha continua só neste navegador.`})});
  drawShared();
}''', '''  drawCats();
}'''),
('''  $("u_list").querySelectorAll("[data-del]").forEach(b=>b.onclick=()=>{st.user.splice(+b.dataset.del,1);save();recompute()});''',
 '''  $("u_list").querySelectorAll("[data-del]").forEach(b=>b.onclick=()=>{st.user.splice(+b.dataset.del,1);recompute()});'''),
# ---- ficha própria: construir a bomba (também usado na importação) ----
('''  const hasE=ok.every(r=>r.length>=3&&isFinite(r[2])),hasN=ok.filter(r=>r.length>=4&&isFinite(r[3])).length>=2;
  const p={id:"U"+Date.now().toString(36),b:"__user",user:true,s:brand,m:name,v:"",D:null,n,hz:50,pg:0,t:brand,Q:ok.map(r=>r[0]),H:ok.map(r=>r[1])};
  if(hasE){p.E=ok.map(r=>r[2]);withP(p)}
  if(hasN){const nq=ok.filter(r=>r.length>=4&&isFinite(r[3]));p.N=ok.map(r=>interp(nq.map(x=>x[0]),nq.map(x=>x[3]),r[0]));p.Nq=[nq[0][0],nq[nq.length-1][0]]}
  if($("u_share").checked&&SH.col){$("u_add").disabled=true;$("u_msg").textContent="A partilhar…";
    SH.col.add(toShared(p)).then(()=>{$("u_msg").textContent=`Partilhada com a equipa: ${name}.`;$("u_name").value=""})
      .catch(e=>{st.user.push(p);save();recompute();$("u_msg").textContent=`Não foi possível partilhar (${e&&e.code||"erro"}); guardada só neste navegador.`})
      .finally(()=>{$("u_add").disabled=false});return}
  st.user.push(p);$("u_msg").textContent=`Adicionada: ${name}.`;$("u_name").value="";save();recompute()};''',
 '''  const p=mkPump({id:"U"+Date.now().toString(36),b:"__user",user:true,s:brand,m:name,n,fam:"U"},ok);
  st.user.push(p);$("u_msg").textContent=`Adicionada: ${name}.`;$("u_name").value="";recompute()};
// linhas [Q (m³/h), H, η (%), NPSHr] ordenadas por Q → bomba
function mkPump(o,ok){const p={v:"",D:null,hz:50,pg:0,...o,t:o.t||o.s,Q:ok.map(r=>r[0]),H:ok.map(r=>r[1])};
  if(ok.every(r=>r.length>=3&&r[2]!=null&&isFinite(r[2]))){p.E=ok.map(r=>r[2]);withP(p)}
  const nq=ok.filter(r=>r.length>=4&&r[3]!=null&&isFinite(r[3]));
  if(nq.length>=2){p.N=ok.map(r=>interp(nq.map(x=>x[0]),nq.map(x=>x[3]),r[0]));p.Nq=[nq[0][0],nq[nq.length-1][0]]}
  return p}

// ---------- catálogos importados (só nesta sessão) ----------
const CATS=[];let catN=0;
DB.forEach(p=>{p.fam="EX";p.src="KSB Etanorm 1311.45/12-EN (catálogo de exemplo)"});
function setFams(){FAMS.length=0;
  if(!CATS.length&&!st.user.length)FAMS.push({k:"EX",n:"Catálogo de exemplo",f:p=>p.fam==="EX"});
  CATS.forEach(c=>FAMS.push({k:c.k,n:c.name,f:p=>p.fam===c.k}));
  if(st.user.length)FAMS.push({k:"U",n:"Fichas próprias",f:p=>p.fam==="U"})}
const cmsg=(t,c)=>{$("c_msg").textContent=t;$("c_msg").className="msg"+(c?" "+c:"")};
// tabelas Q–H lidas → bombas (uma por linha H; η, NPSH e P emparelhados pela ordem quando há uma linha por curva)
function pumpsFromTables(T,c,rpm){const out=[],seen=new Set();
  T.forEach((t,ti)=>{const Hs=t.rows.filter(r=>r.kind==="H");const pick=k=>{const L=t.rows.filter(r=>r.kind===k);return h=>L.length===Hs.length?L[Hs.indexOf(h)]:L[0]};
    const fE=pick("E"),fN=pick("N"),fP=pick("P");
    Hs.forEach((h,hi)=>{const E=fE(h),N=fN(h),P=fP(h),ok=[];
      t.Q.forEach((q,k)=>{const H=h.vals[k];if(H==null||H<0)return;const Qm=+(q*t.unit).toPrecision(6);let e=E&&E.vals[k]!=null?E.vals[k]:null;
        if(e==null&&P&&P.vals[k]>0&&Qm>0)e=G*Qm/3.6*H/P.vals[k]/10;if(e==null&&P&&Qm===0)e=0;
        ok.push([Qm,H,e,N&&N.vals[k]!=null?N.vals[k]:null])});
      if(ok.length<3)return;const key=ok.map(r=>r.slice(0,2).join()).join(";");if(seen.has(key))return;seen.add(key);
      const lab=h.label&&h.label!=="H"?h.label:"",base=(t.title||c.name).slice(0,70);
      const m=h.name||(lab&&!base.includes(lab)?`${base} ${lab}`:Hs.length>1&&!lab?`${base} (${hi+1})`:base);
      out.push(mkPump({id:`${c.k}_${ti}_${hi}`,b:c.name,s:c.name,m,v:h.name?"":lab,n:t.rpm||rpm||2900,pg:t.page,fam:c.k,src:c.name},ok))})});
  return out}
async function importFiles(files){
  files=[...files];if(!files.length)return;let nImg=0;
  for(const f of files){
    if(/^image\\//.test(f.type)){nImg++;loadFile(f);continue}
    if(!(/pdf$/i.test(f.type)||/\\.pdf$/i.test(f.name))){cmsg(`Formato não suportado: ${f.name} (use PDF).`,"bad");continue}
    if(!pdfOK){cmsg("O leitor de PDF não carregou: recarregue a página.","bad");return}
    const c={k:"C"+(++catN),name:f.name.replace(/\\.[^.]+$/,""),file:f,pumps:[],pages:0,chars:0};
    try{const pdf=await pdfjsLib.getDocument({data:new Uint8Array(await f.arrayBuffer()),isEvalSupported:false}).promise;c.pages=pdf.numPages;
      const T=[];let txt="";
      for(let i=1;i<=c.pages;i++){if(i%5===1)cmsg(`A ler ${c.name}: pág. ${i} de ${c.pages}…`);
        const pg=await pdf.getPage(i),tc=await pg.getTextContent();const items=tc.items.filter(it=>it.str!=null).map(it=>({s:it.str,x:it.transform[4],y:it.transform[5],w:it.width,h:Math.hypot(it.transform[2],it.transform[3])||8}));
        const ptx=items.map(it=>it.s).join(" ");c.chars+=ptx.replace(/\\s/g,"").length;txt+=ptx+"\\n";
        const m=ptx.match(/(\\d{3,4})\\s*(?:rpm|min-1|min⁻¹|1\\/min|r\\/min)/i),rpm=m&&+m[1]>500&&+m[1]<4000?+m[1]:null;
        findTables(linesFrom(items),i).forEach(t=>{t.rpm=rpm;T.push(t)});pg.cleanup()}
      const m=txt.match(/(\\d{3,4})\\s*(?:rpm|min-1|min⁻¹|1\\/min|r\\/min)/i);
      c.pumps=pumpsFromTables(T,c,m&&+m[1]>500&&+m[1]<4000?+m[1]:null);pdf.destroy()}
    catch(e){console.error(e);cmsg(`Não foi possível ler ${f.name} (${e.message||e}).`,"bad");continue}
    CATS.push(c);st.fam.add(c.k);st.cfam.add(c.k)}
  recompute();
  const last=CATS[CATS.length-1];
  if(files.length===nImg)cmsg("Imagem aberta para digitalizar a curva (em baixo).","ok");
  else if(last&&files.length===1&&!last.pumps.length)cmsg(last.chars<30*last.pages?`${last.name}: PDF sem texto (digitalizado). Use “digitalizar” para marcar a curva com cliques.`:`${last.name}: não há tabelas Q–H com texto. Use “digitalizar” para marcar a curva com cliques.`,"bad");
  else cmsg(`${CATS.reduce((a,c)=>a+c.pumps.length,0)+st.user.length} curvas carregadas. Confirme sempre a seleção final na folha de dados do fabricante.`,"ok")}
function drawCats(){
  const L=CATS.map(c=>{const m=new Set(c.pumps.map(groupKey)).size;
    return `<div><span class="nm"><b>${esc(c.name)}</b><small>${c.pumps.length?`${m} modelos · ${c.pumps.length} curvas`:c.chars<30*c.pages?"PDF sem texto: digitalize as curvas":"sem tabelas Q–H com texto: digitalize as curvas"} · ${c.pages} pág.</small></span><span><button class="mini" data-dig="${c.k}">digitalizar</button> · <button class="mini" data-rm="${c.k}">remover</button></span></div>`});
  if(st.user.length)L.push(`<div><span class="nm"><b>Fichas próprias</b><small>${st.user.length} curva${st.user.length>1?"s":""} introduzida${st.user.length>1?"s":""} à mão ou digitalizada${st.user.length>1?"s":""}</small></span><button class="mini" data-rm="U">remover</button></div>`);
  $("c_list").innerHTML=L.join("")||`<p class="hint" style="margin:0">Nenhum catálogo carregado.</p>`;
  $("c_ex").textContent=L.length?"Os catálogos e fichas ficam só nesta sessão: ao recarregar a página volta o catálogo de exemplo.":`A mostrar o catálogo de exemplo (${new Set(DB.map(groupKey)).size} modelos KSB Etanorm a 2900 rpm). Ao importar um PDF, o exemplo é substituído.`;
  $("c_clear").hidden=!L.length;
  $("c_list").querySelectorAll("[data-rm]").forEach(b=>b.onclick=()=>{const k=b.dataset.rm;if(k==="U")st.user.length=0;else{const i=CATS.findIndex(c=>c.k===k);if(i>=0)CATS.splice(i,1)}st.fam.delete(k);st.cfam.delete(k);cmsg("");recompute()});
  $("c_list").querySelectorAll("[data-dig]").forEach(b=>b.onclick=()=>{const c=CATS.find(c=>c.k===b.dataset.dig);if(c)loadFile(c.file)})}
$("c_clear").onclick=()=>{CATS.length=0;st.user.length=0;cmsg("");recompute()};
$("c_file").onchange=e=>{const F=[...e.target.files];e.target.value="";importFiles(F)};
const cdrop=$("c_drop");["dragenter","dragover"].forEach(ev=>cdrop.addEventListener(ev,e=>{e.preventDefault();cdrop.classList.add("over")}));
["dragleave","drop"].forEach(ev=>cdrop.addEventListener(ev,e=>{e.preventDefault();cdrop.classList.remove("over")}));
cdrop.addEventListener("drop",e=>importFiles(e.dataTransfer.files));'''),
# título da tabela (linha de texto logo acima do cabeçalho Q)
('''    const tb={page,unit:unitOf(lbl),Q:qv,rows:[],y:ln.y,cols};lastHead=tb;''',
 '''    const tb={page,unit:unitOf(lbl),Q:qv,rows:[],y:ln.y,cols,title:titleAbove(L,i)};lastHead=tb;'''),
('''function findTables(L,page){''', '''function titleAbove(L,i){for(let j=i-1;j>=Math.max(0,i-6);j--){const l=L[j];if(l.y-L[i].y>90)break;const t=l.text.trim();
    if(/[A-Za-z]{2}/.test(t)&&!QRE.test(t)&&t.length<=80&&l.t.filter(k=>NUMRE.test(k.t)).length<4)return t}return""}
function findTables(L,page){'''),
('''      tb.rows.push({label:label||(kind==="H"?"H":kind),kind,vals})}''',
 '''      tb.rows.push({label:label||(kind==="H"?"H":kind),kind,vals,name:modelName(left)})}'''),
('''function titleAbove(L,i){''', '''// designação no início da linha (KPM 50, CS 50-200 B, CFM 150 BR CF 150 BR): um inteiro solto só entra se for o 1.º número ou repetir um anterior; pára na 1.ª grandeza (potência, corrente…)
function modelName(T){const o=[];for(const t of T){const n=NUMRE.test(t),seen=o.join(" ").match(/\\d+/g)||[];if(n&&(!/^\\d+$/.test(t)||!o.length||NUMRE.test(o[o.length-1])||(seen.length&&!seen.includes(t))))break;if(!n&&/^(H|\(m\)|H\(m\)|\[m\])$/.test(t))continue;o.push(t)}
  const r=o.join(" ").trim();return /[A-Za-z]/.test(r)&&/\d/.test(r)?r.slice(0,60):""}
function titleAbove(L,i){'''),
('''Curvas digitalizadas dos catálogos KSB Etanorm (50 Hz), Grundfos HS, CR, NB/NK e SP e Speroni 2020. Defina''',
 '''Importe os catálogos de bombas em PDF ou as suas fichas na aba Catálogo (até lá, usa-se um catálogo de exemplo KSB Etanorm). Defina'''),
('''.srcs em{''', '''#c_list>div{grid-template-columns:minmax(0,1fr) auto}
#c_list .nm{display:flex;flex-direction:column;gap:2px;min-width:0}
#c_list .nm small{color:var(--muted)}
.srcs em{'''),
('''recompute(){compute();''', '''recompute(){setFams();compute();'''),
# ---- guardar: catálogos e fichas não ficam no navegador ----
(''',fam:[...st.fam],cfam:[...st.cfam],sort:st.sort,''', ''',sort:st.sort,'''),
(''',price:st.price,user:st.user}))''', ''',price:st.price}))'''),
('''  if(d.fam){st.fam=new Set(d.fam);if(!d.eq)st.fam.add("EQ");if(!d.gf){st.fam.add("NBK");st.fam.add("GSP")}}if(d.cfam){st.cfam=new Set(d.cfam);if(!d.eq)st.cfam.add("EQ");if(!d.gf){st.cfam.add("NBK");st.cfam.add("GSP")}}if(d.sort)''', '''  if(d.sort)'''),
('''if(Array.isArray(d.extra))st.extra=d.extra.slice(0,3);if(Array.isArray(d.user))st.user=d.user;''', '''if(Array.isArray(d.extra))st.extra=d.extra.slice(0,3);'''),
('''compute();autoPick();famChips("fam",st.fam);''', '''setFams();compute();autoPick();famChips("fam",st.fam);'''),
]
for a, b in rep:
    assert s.count(a) == 1, (a[:80], s.count(a)); s = s.replace(a, b)
# recompute aparece em duplicado no original: as duas passam a chamar setFams (inofensivo)
s = s.replace('function recompute(){compute();', 'function recompute(){setFams();compute();')

# FAMS fixo → lista dinâmica
i = s.index('const FAMS=['); j = s.index('];', i) + 2
s = s[:i] + 'const FAMS=[]; // catálogos carregados (setFams)' + s[j:]
# bloco das fichas partilhadas
i = s.index('// ---------- fichas partilhadas'); j = s.index('$("u_add").onclick')
blk = s[i:j]; keep = re.search(r'function withP\(p\)\{.*?\n', blk).group(0)
s = s[:i] + keep + s[j:]
# carregar ficha: sai a zona de largar da ficha (a importação faz isso)
i = s.index('          <label class="drop" id="u_drop"'); j = s.index('<div class="or">ou introduza os pontos</div>\n', i) + len('<div class="or">ou introduza os pontos</div>\n')
s = s[:i] + '''          <span class="hint">Introduza os pontos de uma curva à mão, ou use “digitalizar” num catálogo carregado (ou largue uma imagem da curva na zona de importação) para os marcar com cliques sobre o gráfico.</span>
          <span class="msg" id="f_msg"></span>
''' + s[j:]
i = s.index('$("u_file").onchange='); j = s.index('udrop.addEventListener("drop",e=>loadFile(e.dataTransfer.files[0]));\n') + len('udrop.addEventListener("drop",e=>loadFile(e.dataTransfer.files[0]));\n')
s = s[:i] + s[j:]
# painel Fontes
i = s.index('<h2>Fontes</h2>'); i = s.rindex('        <section', 0, i); j = s.index('</section>\n', i) + len('</section>\n')
s = s[:i] + s[j:]
for bad in ('SH.', 'u_share', 'sh_list', 'sh_msg', 'u_drop', 'u_file', 'id="srcs"', '$("srcs")', 'cleanShared', 'toShared'):
    assert bad not in s, bad
open(p, 'w', encoding='utf8').write(s)
sc = re.findall(r'<script>(.*?)</script>', s, re.S); open('main.js', 'w', encoding='utf8').write(sc[-1])
print('ok', len(s.encode('utf8')) // 1024, 'KB')
