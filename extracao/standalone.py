# Gera a versão autónoma do seletor (um só .html, sem claude.ai e sem internet) a partir do artefacto
import sys, re, os
sys.stdout.reconfigure(encoding='utf-8')
H = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(H, 'seletor-bombas.html'), encoding='utf8').read()
lib = lambda n: open(os.path.join(H, 'libs', n), encoding='utf8').read()
for n in os.listdir(os.path.join(H, 'libs')): assert '</script' not in lib(n).lower(), n

INL = ''.join(f'<script>/* {n} */\n{lib(n)}\n</script>\n' for n in ('pdf.min.js', 'jszip.min.js', 'html2canvas.min.js', 'jspdf.umd.min.js'))
INL += f'<script type="text/plain" id="pdfWorker">{lib("pdf.worker.min.js")}</script>\n'

i0 = s.index('<link rel="preconnect" href="https://fonts.googleapis.com">'); i1 = s.index('\n', s.index('<link rel="stylesheet" href="https://fonts.googleapis.com')) + 1
L4 = s[i0:i1]
FONTS = '<style>/* fontes embutidas (latin, latin-ext) */\n' + open(os.path.join(H, 'fonts', 'fonts_inline.css'), encoding='utf8').read() + '\n</style>\n' 
rep = [
(L4, FONTS),
('<meta name="claude:viewport-fit-sides" content="cover">\n', ''),
('<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>\n', INL),
# pdf.js: trabalhador a partir do código embutido
('pdfjsLib.GlobalWorkerOptions.workerSrc="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js"',
 'pdfjsLib.GlobalWorkerOptions.workerSrc=URL.createObjectURL(new Blob([$("pdfWorker").textContent],{type:"text/javascript"}))'),
# descargas pelo próprio navegador
('''  if(!dl){msg.className="msg";msg.textContent="A descarga de ficheiros não está disponível nesta vista.";return}''',
 '''  if(!dl){try{const u=URL.createObjectURL(blob),a=document.createElement("a");a.href=u;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),4000);
    msg.className="msg ok";msg.textContent="Ficheiro descarregado: "+filename}catch(e){msg.className="msg";msg.textContent="Não foi possível descarregar o ficheiro."}return}'''),
# projeto em ficheiro (o armazenamento do navegador é local a cada computador)
('''<div class="row"><button class="mini" id="reset">Repor exemplo</button>''',
 '''<div class="row" style="justify-content:flex-start;gap:14px"><button class="mini" id="pj_save">Guardar projeto (.json)</button><button class="mini" id="pj_open">Abrir projeto</button><input type="file" id="pj_file" accept=".json,application/json" hidden><span class="msg" id="pj_msg"></span></div>
  <div class="row"><button class="mini" id="reset">Repor exemplo</button>'''),
('''load();$("sort").value=st.sort;''', '''// ---------- versão autónoma: projeto em ficheiro ----------
const readJSON=f=>new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>{try{res(JSON.parse(r.result))}catch(e){rej(e)}};r.onerror=rej;r.readAsText(f)});
const stamp=()=>new Date().toISOString().slice(0,10);
$("pj_save").onclick=()=>{save();const d=localStorage.getItem(KEY)||"{}";saveFile(`projeto-bombas-${stamp()}.json`,new Blob([JSON.stringify({app:"seletor-bombas",ver:12,estado:JSON.parse(d)},null,1)],{type:"application/json"}),$("pj_msg"))};
$("pj_open").onclick=()=>$("pj_file").click();
$("pj_file").onchange=async e=>{const f=e.target.files[0];e.target.value="";if(!f)return;
  try{const d=await readJSON(f);if(!d||d.app!=="seletor-bombas"||typeof d.estado!=="object")throw 0;localStorage.setItem(KEY,JSON.stringify(d.estado));location.reload()}
  catch(_){$("pj_msg").className="msg";$("pj_msg").textContent="Ficheiro de projeto inválido."}};
load();$("sort").value=st.sort;'''),
]
for a, b in rep:
    assert s.count(a) == 1, (a[:70], s.count(a)); s = s.replace(a, b)
assert 'src="https://' not in s and 'pdf.worker.min.js"' not in s, 'CDN restante'
out = os.path.join(H, 'Seletor de Bombas.html')
open(out, 'w', encoding='utf8', newline='\n').write(s)
sc = re.findall(r'<script>(.*?)</script>', s, re.S); open(os.path.join(H, 'main_sa.js'), 'w', encoding='utf8').write(sc[-1])
print('ok', os.path.getsize(out)//1024, 'KB')
