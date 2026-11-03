import pymupdf as f, json, re, sys
sys.path.insert(0,'.')
import nbx
d=f.open(nbx.PDF)
pages=[i for i in range(d.page_count) if re.search(r'NB, NK \d+-\d+', d[i].get_text()) and 'Performance curves' in d[i].get_text()]
R=[]
for pg in pages:
    try: R+=nbx.page_models(pg)
    except Exception as e: print('ERR',pg+1,e)
ok=[r for r in R if not r['err'] and r.get('H')]
print('paginas',len(pages),'graficos',len(R),'ok',len(ok))
for r in R:
    flag='' if (r.get('nH') and r['nH'][0]==len(r.get('H',{})) and r['nP'][0]==len(r.get('P',{})) and len(r.get('N',{}))>=1) else ' <<<'
    if flag or r['err']: print(r['page'],r['model'],r['mat'],r['poles'],r['err'],'H',sorted(r.get('H',{})),'N',sorted(r.get('N',{})),'P',sorted(r.get('P',{})),r.get('nH'),r.get('nP'),flag)
json.dump(R,open('nb_raw.json','w'),default=list)
