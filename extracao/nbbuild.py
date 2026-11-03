# Constrói as entradas NB/NK no formato da base de dados do seletor
import json, statistics as stt, sys
sys.stdout.reconfigure(encoding='utf-8')
R = json.load(open('nb_raw.json'))
G = 9.80665
SPEED = {2: 2900, 4: 1450, 6: 960}

def interp(D, q):
    D = sorted(D)
    if q <= D[0][0]: return D[0][1]
    if q >= D[-1][0]: return D[-1][1]
    for (a, b), (c, e) in zip(D, D[1:]):
        if a <= q <= c: return b + (e-b)*(q-a)/(c-a) if c > a else b

# um gráfico por modelo e velocidade: ferro fundido (ou sem indicação); inox só se for o único
by = {}
for r in R:
    if r['err'] or not r.get('H'): continue
    k = (r['model'], r['poles'])
    pri = {'ff': 0, None: 0, 'inox': 1}[r['mat']]
    if k not in by or pri < by[k][0]: by[k] = (pri, r)

out = []; warn = []
for (model, poles), (_, r) in sorted(by.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    Hs = {float(k): v for k, v in r['H'].items()}; Ps = {float(k): v for k, v in r['P'].items()}; Ns = {float(k): v['all'] for k, v in r['N'].items()}
    Ds = sorted(Hs)
    for D in Ds:
        h = Hs[D]; A = sorted(h['all'])
        qa, qb = max(0.0, A[0][0]), A[-1][0]
        if qb - qa < 1e-6: continue
        Q = [qa + (qb-qa)*i/15 for i in range(16)]
        H = [interp(A, q) for q in Q]
        e = {'b': 'Grundfos', 's': 'NB/NK', 'm': f'NB/NK {model}', 'v': f"Ø{h['txt'][1:]}", 'D': D, 'n': SPEED[poles], 'hz': 50, 'pg': r['page'],
             't': 'Centrífuga normalizada (EN 733), aspiração axial', 'Q': [round(q, 2) for q in Q], 'H': [round(x, 2) for x in H]}
        Dp = min(Ps, key=lambda k: abs(k-D)) if Ps else None
        if Dp is not None and abs(Dp-D) <= 0.02*D and sorted(Ps).index(Dp) == Ds.index(D):  # mesma ordem; tolera etiquetas P2 ligeiramente diferentes
            P = [max(0.01, interp(Ps[Dp], q)) for q in Q]
            E = [0.0 if q <= 0 else 100*G*q/3600*hh/p for q, hh, p in zip(Q, H, P)]
            e['P'] = [round(p, 3) for p in P]; e['E'] = [round(x, 1) for x in E]
        # NPSH: curva do diâmetro, ou interpolação linear entre os diâmetros mínimo e máximo
        if Ns:
            ks = sorted(Ns)
            if D in Ns: f = lambda q: interp(Ns[D], q)
            elif len(ks) >= 2:
                lo, hi = ks[0], ks[-1]; t = min(1, max(0, (D-lo)/(hi-lo)))
                f = lambda q, lo=lo, hi=hi, t=t: interp(Ns[lo], q)*(1-t) + interp(Ns[hi], q)*t
            else: f = lambda q, k=ks[0]: interp(Ns[k], q)
            e['N'] = [round(max(0.1, f(q)), 2) for q in Q]
            nq = [min(p[0] for c in Ns.values() for p in c), max(p[0] for c in Ns.values() for p in c)]
            e['Nq'] = [round(max(qa, nq[0]), 2), round(min(qb, max(nq[1], qb if D in Ns else nq[1])), 2)]
        if h['bold']:
            e['R'] = [round(min(p[0] for p in h['bold']), 2), round(max(p[0] for p in h['bold']), 2)]
        out.append(e)
    # verificações físicas
    for D in Ds:
        x = [e for e in out if e['m'] == f'NB/NK {model}' and e['n'] == SPEED[poles] and e['D'] == D]
        if not x or 'E' not in x[0]: warn.append((model, poles, D, 'sem P')); continue
        Em = max(x[0]['E'])
        if not 35 <= Em <= 92: warn.append((model, poles, D, f'η máx {Em}'))
    hs = [max(e['H']) for e in out if e['m'] == f'NB/NK {model}' and e['n'] == SPEED[poles]]
    if hs != sorted(hs): warn.append((model, poles, 'H não cresce com D', hs))

json.dump(out, open('nb_db.json', 'w'))
print('modelos', len(by), 'curvas', len(out))
print('avisos', len(warn)); [print(w) for w in warn[:30]]
E = [max(e['E']) for e in out if 'E' in e]
print('η máx: min', min(E), 'med', stt.median(E), 'max', max(E))
