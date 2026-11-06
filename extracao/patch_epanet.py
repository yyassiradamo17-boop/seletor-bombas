# v14: exportar curvas para o EPANET (rede .inp, curvas .crv e secção [CURVES])
import re, sys, os
sys.stdout.reconfigure(encoding='utf-8')
H = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(H, 'seletor-bombas.html')
s = open(p, encoding='utf8').read()
assert 'id="e_go"' not in s, 'já aplicado'
PANEL = open(os.path.join(H, 'patch_epanet_panel.html'), encoding='utf8').read()
JS = open(os.path.join(H, 'patch_epanet.js'), encoding='utf8').read()
rep = [
('''          <h2>Ficha própria</h2>''', None),
('''  for(const p of allPumps()){if(!st.cfam.has(famOf(p)))continue;if(q&&!(p.m+" "+p.t).toLowerCase().includes(q))continue;const k=groupKey(p);if(!groups.has(k))groups.set(k,[]);groups.get(k).push(p)}''',
 '''  for(const p of catPumps()){const k=groupKey(p);if(!groups.has(k))groups.set(k,[]);groups.get(k).push(p)}'''),
('''function drawCat(){
  const q=$("c_txt").value.trim().toLowerCase();
''', '''const catPumps=()=>{const q=$("c_txt").value.trim().toLowerCase();return allPumps().filter(p=>st.cfam.has(famOf(p))&&(!q||(p.m+" "+p.t).toLowerCase().includes(q)))};
function drawCat(){
'''),
('''// ---------- separadores ----------''', JS + '''
// ---------- separadores ----------'''),
]
for a, b in rep:
    assert s.count(a) == 1, (a[:70], s.count(a))
    if b is not None: s = s.replace(a, b)
i = s.index('<h2>Ficha própria</h2>'); i = s.rindex('        <section', 0, i)
s = s[:i] + PANEL + s[i:]
open(p, 'w', encoding='utf8', newline='\n').write(s)
sc = re.findall(r'<script>(.*?)</script>', s, re.S); open(os.path.join(H, 'main.js'), 'w', encoding='utf8').write(sc[-1])
print('ok', len(s.encode('utf8')) // 1024, 'KB')
