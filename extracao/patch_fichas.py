# v15: fichas técnicas e páginas de curvas em PDF — curvas desenhadas em vetor lidas sem cliques
import re, sys, os
sys.stdout.reconfigure(encoding='utf-8')
H = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(H, 'seletor-bombas.html')
s = open(p, encoding='utf8').read()
assert 'function vecRead' not in s, 'já aplicado'
JS = open(os.path.join(H, 'patch_fichas.js'), encoding='utf8').read()
rep = [
('''async function importFiles(files){''', JS + '''async function importFiles(files){'''),
('''      const T=[];let txt="";''', '''      const T=[],V=[];let txt="";'''),
('''        findTables(linesFrom(items),i).forEach(t=>{t.rpm=rpm;T.push(t)});pg.cleanup()}''',
 '''        const tb=findTables(linesFrom(items),i);tb.forEach(t=>{t.rpm=rpm;T.push(t)});
        if(!tb.length&&FLOWRE.test(ptx.replace(/\s+/g,"")))try{V.push(...await vecRead(pg,items,i,ptx))}catch(e){console.warn(e)} // sem tabela: curvas desenhadas
        pg.cleanup()}'''),
('''      c.pumps=pumpsFromTables(T,c,m&&+m[1]>500&&+m[1]<4000?+m[1]:null);pdf.destroy()}''',
 '''      const rpm0=m&&+m[1]>500&&+m[1]<4000?+m[1]:null;c.pumps=pumpsFromTables(T,c,rpm0).concat(pumpsFromVec(V,c,rpm0));c.vec=V.length;pdf.destroy()}'''),
('''<span><b>Importar catálogo em PDF</b><small>Clique ou arraste um ou mais ficheiros. O PDF tem de ter texto selecionável (catálogos digitalizados não são lidos).</small></span>''',
 '''<span><b>Importar catálogo ou ficha técnica</b><small>Clique ou arraste um ou mais PDF: catálogos, fichas técnicas ou páginas de curvas. As tabelas Q–H e as curvas desenhadas (H, potência, NPSH, por diâmetro do rotor) são lidas sem cliques. PDF digitalizados e imagens abrem-se para marcar a curva à mão.</small></span>'''),
('''<label class="drop big" id="c_drop" for="c_file">''', '''<label class="drop big" id="c_drop" for="c_file" title="Importar catálogo ou ficha técnica">'''),
('''${c.pumps.length?`${m} modelos · ${c.pumps.length} curvas`:c.chars<30*c.pages?"PDF sem texto: digitalize as curvas":"sem tabelas Q–H com texto: digitalize as curvas"}''',
 '''${c.pumps.length?`${m} modelo${m>1?"s":""} · ${c.pumps.length} curva${c.pumps.length>1?"s":""}${c.vec?` (${c.vec} lida${c.vec>1?"s":""} do gráfico)`:""}`:c.chars<30*c.pages?"PDF sem texto: digitalize as curvas":"sem tabelas nem curvas legíveis: digitalize as curvas"}'''),
(''':`${last.name}: não há tabelas Q–H com texto. Use “digitalizar” para marcar a curva com cliques.`''',
 ''':`${last.name}: não há tabelas Q–H nem curvas desenhadas que se consigam ler. Use “digitalizar” para marcar a curva com cliques.`'''),
('''Importe os catálogos de bombas em PDF ou as suas fichas na aba Catálogo.''', '''Importe catálogos, fichas técnicas ou páginas de curvas em PDF na aba Catálogo.'''),
]
for a, b in rep:
    assert s.count(a) == 1, (a[:80], s.count(a)); s = s.replace(a, b)
open(p, 'w', encoding='utf8', newline='\n').write(s)
sc = re.findall(r'<script>(.*?)</script>', s, re.S); open(os.path.join(H, 'main.js'), 'w', encoding='utf8').write(sc[-1])
print('ok', len(s.encode('utf8')) // 1024, 'KB')
