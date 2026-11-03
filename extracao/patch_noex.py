# v12.1: sem catálogo de exemplo — só as bombas importadas pelo utilizador
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
p='seletor-bombas.html'; s=open(p,encoding='utf8').read()
i=s.index('const DB=');j=s.index('\n',i); s=s[:i]+'const DB=[]; // sem catálogo embutido: as bombas vêm dos catálogos importados e das fichas próprias'+s[j:]
rep=[
('''return L.length?L:DB}''','''return L}'''),
('''DB.forEach(p=>{p.fam="EX";p.src="KSB Etanorm 1311.45/12-EN (catálogo de exemplo)"});\n''',''),
('''  if(!CATS.length&&!st.user.length)FAMS.push({k:"EX",n:"Catálogo de exemplo",f:p=>p.fam==="EX"});\n''',''),
('''fam:new Set(["EX","U"]),cfam:new Set(["EX","U"])''','''fam:new Set(["U"]),cfam:new Set(["U"])'''),
(''' (até lá, usa-se um catálogo de exemplo KSB Etanorm)''',''),
('''"Os catálogos e fichas ficam só nesta sessão: ao recarregar a página volta o catálogo de exemplo.":`A mostrar o catálogo de exemplo (${new Set(DB.map(groupKey)).size} modelos KSB Etanorm a 2900 rpm). Ao importar um PDF, o exemplo é substituído.`''',
 '''"Os catálogos e fichas ficam só nesta sessão: ao recarregar a página é preciso importá-los de novo.":"Importe um catálogo em PDF ou adicione uma ficha própria para começar a seleção."'''),
('''Nenhuma bomba cumpre o ponto com os filtros atuais. Alargue o excesso de caudal admissível, mude o número de bombas em paralelo ou mostre as que não cumprem.''',
 '''${RES.length?"Nenhuma bomba cumpre o ponto com os filtros atuais. Alargue o excesso de caudal admissível, mude o número de bombas em paralelo ou mostre as que não cumprem.":`Ainda não há bombas: importe um catálogo em PDF ou adicione uma ficha própria na aba <button class="mini" data-gocat>Catálogo</button>.`}'''),
('''$("c_txt").addEventListener("input",drawCat);''', '''$("c_txt").addEventListener("input",drawCat);
document.addEventListener("click",e=>{if(e.target.closest("[data-gocat]"))setView("cat")});'''),
]
for a,b in rep:
    assert s.count(a)==1,(a[:60],s.count(a)); s=s.replace(a,b)
open(p,'w',encoding='utf8').write(s)
sc=re.findall(r'<script>(.*?)</script>',s,re.S); open('main.js','w',encoding='utf8').write(sc[-1])
print('ok',len(s.encode('utf8'))//1024,'KB')
