# Constrói as entradas SP / SP A no formato da base de dados do seletor
import json, re, sys, statistics as stt
sys.stdout.reconfigure(encoding='utf-8')
R = json.load(open('sp_raw.json'))
G = 9.80665

def interp(D, q):
    D = sorted(D)
    if q <= D[0][0]: return D[0][1]
    if q >= D[-1][0]: return D[-1][1]
    for (a, b), (c, e) in zip(D, D[1:]):
        if a <= q <= c: return b + (e-b)*(q-a)/(c-a) if c > a else b

fams = {}
for r in R:
    F = fams.setdefault(r['fam'], {'H': {}, 'P': {}, 'N': None, 'P1': None, 'pg': {}})
    if r['kind'] in ('H', 'P'):
        for k, v in r['cur'].items():
            F[r['kind']][k] = v; F['pg'].setdefault((r['kind'], k), r['page'])
    elif r['kind'] == 'N' and not F['N']: F['N'] = r['cur']
    elif r['kind'] == 'P1' and not F['P1']: F['P1'] = r['cur']

def famnum(f): return int(re.search(r'\d+', f).group())
out = []; warn = []
for fam in sorted(fams, key=famnum):
    F = fams[fam]; small = fam.endswith('A')
    n = 2900 if famnum(fam) >= 77 and not small else 2870  # 4" e 6": 2870 min⁻¹; 8" a 12": 2900 min⁻¹
    for lab, h in F['H'].items():
        z = int(re.match(r'-(\d+)', lab).group(1))
        A = sorted(h['all']); qa, qb = max(0.0, A[0][0]), A[-1][0]
        Q = [qa + (qb-qa)*i/15 for i in range(16)]; H = [interp(A, q) for q in Q]
        e = {'b': 'Grundfos', 's': 'SP', 'm': f'{fam}{lab}', 'v': f'{z} andares' + (' · rotor reduzido' if re.search(r'-[A-C]', lab) else ''),
             'D': None, 'n': n, 'hz': 50, 'pg': F['pg'][('H', lab)], 't': 'Submersível de furo multicelular' + (' (4")' if small else ''),
             'Q': [round(q, 3) for q in Q], 'H': [round(x, 2) for x in H]}
        if lab in F['P']: P = [max(0.005, interp(F['P'][lab], q)) for q in Q]
        elif F['P1']: P = [max(0.0005, z*interp(F['P1'], q)) for q in Q]
        else: P = None
        if P:
            e['P'] = [round(p, 4) for p in P]
            e['E'] = [round(0.0 if q <= 0 else 100*G*q/3600*hh/p, 1) for q, hh, p in zip(Q, H, P)]
        if F['N']:
            e['N'] = [round(max(0.1, interp(F['N'], q)), 2) for q in Q]
            e['Nq'] = [round(max(qa, min(p[0] for p in F['N'])), 3), round(min(qb, max(p[0] for p in F['N'])), 3)]
        if h['bold']: e['R'] = [round(min(p[0] for p in h['bold']), 3), round(max(p[0] for p in h['bold']), 3)]
        out.append(e)
        if 'E' in e and not 25 <= max(e['E']) <= 85: warn.append((e['m'], max(e['E'])))
        if 'P' not in e: warn.append((e['m'], 'sem P'))
    # H a Q=0 deve crescer com o número de andares (variantes sem rotor reduzido)
    full = sorted(((int(re.match(r'-(\d+)', k).group(1)), max(v['all'], key=lambda p: p[1])[1]) for k, v in F['H'].items() if not re.search(r'-[A-C]', k)))
    hs = [x[1] for x in full]
    if hs != sorted(hs): warn.append((fam, 'H não cresce com os andares'))
    per = [x[1]/x[0] for x in full]
    if per and max(per)/min(per) > 1.15: warn.append((fam, 'H por andar varia', round(min(per), 1), round(max(per), 1)))

json.dump(out, open('sp_db.json', 'w'))
print('famílias', len(fams), 'curvas', len(out)); print('avisos', len(warn)); [print(w) for w in warn[:40]]
for fam in ('SP 77', 'SP 1A', 'SP 17'):
    for e in out:
        if e['m'] in (fam + '-5', fam + '-9', fam + '-14'):
            i = max(range(16), key=lambda k: e['E'][k]); print(e['m'], 'H0', e['H'][0], 'Qmax', e['Q'][-1], 'BEP', e['Q'][i], 'η', e['E'][i], 'P@BEP', e['P'][i])
