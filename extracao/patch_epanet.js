// ---------- exportar para o EPANET ----------
// unidades SI do EPANET (altura em m): fator a partir de m³/h
const EPU={LPS:1/3.6,LPM:1000/60,CMH:1,CMD:24,MLD:0.024};
const EPH={net:"Abre no EPANET com File > Open e corre logo: bomba A, condutas, níveis e rendimento do sistema definido à esquerda.",
  crv:"Para uma rede que já existe: no Curve Editor do EPANET, botão Load, um ficheiro de cada vez. Use a mesma unidade de caudal da rede.",
  inp:"Para uma rede que já existe: cole a secção [CURVES] no .inp da rede e volte a abri-lo (File > Import > Network substitui a rede, não junta curvas). Use a mesma unidade de caudal da rede."};
const ascii=t=>String(t).normalize("NFD").replace(/[̀-ͯ]/g,"").replace(/Ø/g,"D").replace(/η/g,"eta").replace(/[^\x20-\x7e]/g,"?");
// o EPANET exige Q crescente e, na curva da bomba, H sempre a descer: o troço instável à esquerda do pico sobe até ao pico
function epaCurve(c,k){const L=[];
  c.Q.forEach((q,i)=>{const h=c.H[i];if(!(q>=0)||!(h>0))return;const x=+(q*k).toFixed(3);if(L.length&&x<=L[L.length-1].x)return;
    L.push({x,h:Math.round(h*100),h0:h,e:c.E&&isFinite(c.E[i])?clamp(c.E[i],0,100):null})});
  for(let i=L.length-2;i>=0;i--)if(L[i].h<=L[i+1].h)L[i].h=L[i+1].h+1;
  return{L,adj:Math.max(0,...L.map(p=>Math.abs(p.h/100-p.h0)))}}
// IDs do EPANET: até 31 carateres, sem espaços nem ponto e vírgula
function epaItems(list,k){const ids=new Set();
  return list.map(r=>{const{L,adj}=epaCurve(r.c,k);if(L.length<2)return null;const lb=labelOf(r);
    const b=ascii(lb.full).replace(/[^A-Za-z0-9_.-]+/g,"_").replace(/^_+|_+$/g,"").slice(0,26)||"Bomba";let key=b,i=1;while(ids.has(key))key=`${b}_${++i}`;ids.add(key);
    const E=L.filter(p=>p.e!=null);
    return{r,L,E:E.length>=2?E:null,adj,id:"H_"+key,eid:"E_"+key,desc:ascii(`${lb.full}, ${Math.round(r.c.n)} rpm, ${srcOf(r.p)}`).slice(0,150),est:!!r.c.Eest}}).filter(Boolean)}
const epaPts=(a,f)=>a.map(p=>[p.x.toFixed(3),f(p)]);
const epaH=p=>(p.h/100).toFixed(2),epaE=p=>p.e.toFixed(1);
function epaCurves(T,u){const o=["[CURVES]",";ID\tX-Value\tY-Value"];
  T.forEach(t=>{o.push("",`;PUMP: ${t.desc} (Q em ${u}, H em m)`,...epaPts(t.L,epaH).map(([x,y])=>`${t.id}\t${x}\t${y}`));
    if(t.E)o.push("",`;EFFICIENCY: ${t.desc}${t.est?" (eta estimado)":""} (Q em ${u}, eta em %)`,...epaPts(t.E,epaE).map(([x,y])=>`${t.eid}\t${x}\t${y}`))});
  return o}
function epaLib(T,u,hl){return["[TITLE]","Curvas de bombas exportadas do Seletor de Bombas",`Caudal em ${u}, altura em m, rendimento em %`,"",...epaCurves(T,u),"","[OPTIONS]",` Units\t${u}`,` Headloss\t${hl}`,"","[END]",""]}
// rede: reservatório de aspiração → conduta (uma por bomba em paralelo) → bombas → conduta de compressão → reservatório de descarga
function epaNet(t,u,s,hl,sp,op){const J=[],P=[],U=[],EN=[],XY=[],D=(s.Np-1)*100/2,rg=L=>hl==="H-W"?L.C:L.eps;
  const pipe=(id,a,b,L)=>P.push(`${id}\t${a}\t${b}\t${Math.max(L.L,0.1)}\t${L.D}\t${rg(L)}\t${L.K}\tOpen`);
  const node=(id,x,y)=>{J.push(`${id}\t${s.zp}\t0`);XY.push(`${id}\t${x}\t${y}`)};
  node("J_DES",(s.Ns+2)*100,D);
  for(let i=1;i<=s.Np;i++){const y=(i-1)*100;let prev=`J_ASP${i}`;node(prev,100,y);pipe(`P_ASP${i}`,"R_ASP",prev,s.suc);
    for(let j=1;j<=s.Ns;j++){const nx=j===s.Ns?"J_DES":`J_${i}_${j}`;if(j<s.Ns)node(nx,(j+1)*100,y);const id=`B_${i}_${j}`;
      U.push(`${id}\t${prev}\t${nx}\tHEAD ${t.id}${sp!==100?`\tSPEED ${(sp/100).toFixed(3)}`:""}`);if(t.E)EN.push(`Pump ${id} Efficiency ${t.eid}`);prev=nx}}
  pipe("P_DES","J_DES","R_DES",s.dis);
  XY.push(`R_ASP\t0\t${D}`,`R_DES\t${(s.Ns+3)*100}\t${D}`);
  const Qo=op&&op.st==="ok"?` Seletor: Q = ${(op.Qt*EPU[u]).toFixed(2)} ${u}, H = ${op.Hp.toFixed(2)} m.`:"";
  return["[TITLE]",`Rede do Seletor de Bombas: ${t.desc}`.slice(0,79),`${s.Np} em paralelo x ${s.Ns} em serie.${Qo}`.slice(0,79),"",
    "[JUNCTIONS]",";ID\tElev\tDemand",...J,"","[RESERVOIRS]",";ID\tHead",`R_ASP\t${s.zs}`,`R_DES\t${+(s.zd+s.pres).toFixed(3)}`,"",
    "[PIPES]",";ID\tNode1\tNode2\tLength\tDiameter\tRoughness\tMinorLoss\tStatus",...P,"","[PUMPS]",";ID\tNode1\tNode2\tParameters",...U,"",
    ...epaCurves([t],u),"","[ENERGY]"," Global Efficiency\t75",...EN.map(l=>" "+l),"","[TIMES]"," Duration\t0","","[REPORT]"," Status\tYes"," Summary\tNo","",
    "[OPTIONS]",` Units\t${u}`,` Headloss\t${hl}`,` Viscosity\t${(s.W.nu/1.0219e-6).toFixed(3)}`,` Specific Gravity\t${(s.W.rho/1000).toFixed(3)}`," Accuracy\t0.0001"," Trials\t200","",
    "[COORDINATES]",";Node\tX\tY",...XY,"","[END]",""]}
const epaSafe=t=>ascii(t).replace(/[^A-Za-z0-9_.-]+/g,"_").slice(0,40);
async function exportEpa(){const fmt=$("e_fmt").value,u=$("e_u").value,k=EPU[u],hl=S.m==="hw"?"H-W":"D-W",msg=$("e_msg");
  msg.className="msg";msg.textContent="";$("e_note").textContent="";
  const ids=fmt==="net"?[st.A]:[st.A,st.B,...st.extra],list=fmt!=="net"&&$("e_what").value==="tab"?catPumps().map(p=>BY[p.id]):ids.map(id=>BY[id]);
  const T=epaItems(list.filter(Boolean),k);
  if(!T.length){msg.textContent=fmt==="net"?"Escolha primeiro a bomba A.":"Não há bombas para exportar: importe um catálogo ou escolha as bombas.";return}
  const crlf=L=>new Blob([L.join("\r\n")],{type:"text/plain"}),day=new Date().toISOString().slice(0,10);
  if(fmt==="net"){const op=(pick("A")||T[0].r).o;await saveFile(`rede-epanet-${epaSafe(T[0].id.slice(2))}.inp`,crlf(epaNet(T[0],u,S,hl,st.spA,op)),msg)}
  else if(fmt==="inp")await saveFile(`curvas-epanet-${day}.inp`,crlf(epaLib(T,u,hl)),msg);
  else{try{await loadScript("https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js",()=>!!window.JSZip)}catch(e){msg.textContent="Não foi possível preparar o .zip.";return}
    const z=new JSZip(),thin=a=>a.length<=50?a:Array.from({length:50},(_,i)=>a[Math.round(i*(a.length-1)/49)]); // o Curve Editor lê até 50 pontos
    const crv=(ty,d,P)=>["EPANET Curve Data",ty,d,...P.map(([x,y])=>`${x}  ${y}`),""].join("\r\n");
    T.forEach(t=>{z.file(t.id+".crv",crv("PUMP",t.desc,epaPts(thin(t.L),epaH)));if(t.E)z.file(t.eid+".crv",crv("EFFICIENCY",t.desc,epaPts(thin(t.E),epaE)))});
    z.file("LEIA-ME.txt",[`Curvas exportadas do Seletor de Bombas. Caudal em ${u}, altura em m, rendimento em %.`,"H_*.crv: curva da bomba. E_*.crv: curva de rendimento.","No EPANET: Data > Curves > Add, botao Load e escolher o ficheiro. A rede tem de usar a mesma unidade de caudal.",""].join("\r\n"));
    await saveFile(`curvas-epanet-${day}.zip`,await z.generateAsync({type:"blob",compression:"DEFLATE"}),msg)}
  const adj=T.filter(t=>t.adj>0.02),q0=T.filter(t=>t.L[0].x>0),note=[];
  if(adj.length)note.push(`${adj.length} curva${adj.length>1?"s":""} com H a subir ou constante à esquerda do pico: o EPANET não as aceita, por isso esse troço foi ajustado (até ${nf(Math.max(...adj.map(t=>t.adj)),2)} m).`);
  if(q0.length)note.push(`${q0.length} curva${q0.length>1?"s":""} sem ponto em Q = 0: abaixo do primeiro ponto o EPANET extrapola.`);
  $("e_note").textContent=note.join(" ")}
$("e_go").onclick=exportEpa;
$("e_fmt").onchange=()=>{const f=$("e_fmt").value;$("e_hint").textContent=EPH[f];$("e_what_f").style.display=f==="net"?"none":""};
$("e_fmt").onchange();
