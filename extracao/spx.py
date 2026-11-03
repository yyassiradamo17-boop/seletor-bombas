# Extração vetorial das curvas Grundfos SP / SP A (data booklet 50 Hz)
import pymupdf as f, re, json, sys, math
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, "."); import nbx
PDF = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'catálogo', 'Bombas Hidráulicas', 'Grundfos-SP-book.pdf')
ident = lambda t: t
LBL = re.compile(r'^-(\d{1,3})(-[A-C]{1,2})?$')

def curves(drs, fr):
    x0, y0, x1, y1 = fr; C = []
    for d in drs:
        wd = d.get('width') or 0
        if not (0.40 <= wd <= 0.46 or 1.15 <= wd <= 1.25) or d.get('dashes') not in (None, '[] 0'): continue
        r = d['rect']
        if r.x0 < x0-1 or r.x1 > x1+1 or r.y0 < y0-1 or r.y1 > y1+1: continue
        P = nbx.pts_of(d)
        if len(P) < 4 or (r.x1-r.x0) < 8: continue
        P.sort(); C.append({'w': 'b' if wd > 1 else 't', 'P': P})
    bold = [c for c in C if c['w'] == 'b']; thin = [c for c in C if c['w'] == 't']
    out = []; used = set()
    for b in bold:
        P = b['P']; pre = []; post = []
        for i, t in enumerate(thin):
            if i in used: continue
            if math.dist(t['P'][-1], P[0]) < 1.5: pre = t['P']; used.add(i)
            elif math.dist(t['P'][0], P[-1]) < 1.5: post = t['P']; used.add(i)
        out.append({'all': pre + P + post, 'bold': P})
    return out

def labels(words, fr, side):
    x0, y0, x1, y1 = fr; L = []
    for w in words:
        m = LBL.match(w[4])
        if not m: continue
        cx, cy = (w[0]+w[2])/2, (w[1]+w[3])/2
        if side == 'left' and x0 <= w[0] <= x0+40 and y0-4 <= cy <= y1: L.append((cy, w[4]))
        if side == 'right' and x0+0.6*(x1-x0) <= w[0] <= x1+30 and y0 <= cy <= y1+4: L.append((cy, w[4], w[0]))
    return sorted(L)

def family(text):
    m = re.search(r'Submersible pumps\s*\n\s*(SP \d+A?)\b', text)
    return m.group(1) if m else None

def page(pg, d):
    p = d[pg]; words = p.get_text('words'); drs = p.get_drawings(); text = p.get_text()
    fam = family(text); FR = nbx.frames(drs); res = []
    kind = 'P' if 'Power curves' in text else 'H' if 'Performance curves' in text else None
    if not kind or not fam: return []
    for fr in FR:
        dq = nbx.calib(nbx.axis_labels(words, fr, 'bottom'), ident)
        dy = nbx.calib(nbx.axis_labels(words, fr, 'left'), ident)
        if not dq or not dy: continue
        C = curves(drs, fr)
        if kind == 'H' and (fr[3]-fr[1]) > 200:
            L = labels(words, fr, 'left')
            # ordem vertical: etiqueta mais acima ↔ curva com maior H no início
            Cs = sorted(C, key=lambda c: c['all'][0][1])
            res.append({'fam': fam, 'kind': 'H', 'page': pg+1, 'n': (len(L), len(Cs)),
                        'cur': {lab: {'all': nbx.to_data(c['all'], dq, dy), 'bold': nbx.to_data(c['bold'], dq, dy)} for (_, lab), c in zip(L, Cs)} if len(L) == len(Cs) else {}})
        elif kind == 'H':
            # gráfico pequeno: Eta (eixo direito) e NPSH (eixo esquerdo)
            ws = [w for w in words if fr[0] < w[0] < fr[2] and fr[1] < w[1] < fr[3]]
            for key, kd in (('NPSH', 'N'), ('P2', 'P1')):  # P1: P2 por andar (SP A)
                ln = [w for w in ws if w[4] == key]
                if ln and C:
                    w = ln[0]
                    c = min(C, key=lambda c: min(nbx.dist_poly(q, c['all']) for q in (((w[0]+w[2])/2, w[1]-1), ((w[0]+w[2])/2, w[3]+1))))
                    res.append({'fam': fam, 'kind': kd, 'page': pg+1, 'cur': nbx.to_data(c['all'], dq, dy)})
        elif kind == 'P':
            L = labels(words, fr, 'right')
            # cada etiqueta fica logo à direita do fim da sua curva: associação pela distância (as curvas podem cruzar-se)
            cand = sorted((math.dist((lx, ly), C[j]['all'][-1]), i, j) for i, (ly, _, lx) in enumerate(L) for j in range(len(C)))
            A = {}; uj = set()
            for dd, i, j in cand:
                if i in A or j in uj: continue
                A[i] = j; uj.add(j)
            # curvas que terminam no mesmo ponto: a etiqueta de cima fica com a curva mais alta em média
            inv = {j: i for i, j in A.items()}; seen = set()
            for j in list(inv):
                grp = [k for k in inv if math.dist(C[k]['all'][-1], C[j]['all'][-1]) < 2.0]
                if len(grp) < 2 or j in seen: continue
                seen |= set(grp)
                ls = sorted((inv[k] for k in grp), key=lambda i: L[i][0])
                cs = sorted(grp, key=lambda k: sum(p[1] for p in C[k]['all'])/len(C[k]['all']))
                for i, k in zip(ls, cs): A[i] = k
            res.append({'fam': fam, 'kind': 'P', 'page': pg+1, 'n': (len(L), len(C)),
                        'cur': {L[i][1]: nbx.to_data(C[j]['all'], dq, dy) for i, j in A.items()} if len(L) == len(C) else {}})
    return res

if __name__ == '__main__':
    d = f.open(PDF); R = []
    for pg in range(15, 73): R += page(pg, d)
    for r in R:
        print(r['fam'], r['kind'], r['page'], r.get('n'), len(r['cur']) if r['kind'] in 'HP' else '1 curva', '' if r['kind'] not in 'HP' or r['n'][0] == r['n'][1] else '<<<')
    json.dump(R, open('sp_raw.json', 'w'))
