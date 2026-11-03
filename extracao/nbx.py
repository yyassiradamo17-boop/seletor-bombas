# Extração vetorial das curvas Grundfos NB/NK (data booklet 50 Hz)
import pymupdf as f, re, json, sys, math
PDF = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'catálogo', 'Bombas Hidráulicas', 'grundfos-nb-nbe-nk-nke-.pdf')
ENC = {'6':'0','=':'1','>':'2','?':'3','@':'4','A':'5','B':'6','C':'7','D':'8','E':'9','4':'.','5':'/','3':'-'}
dec = lambda t: ''.join(ENC.get(c, c) for c in t)
NUM = re.compile(r'^-?\d+(\.\d+)?$')
G = 9.80665
SPEED = {2: 2900, 4: 1450, 6: 960}

def pts_of(dr):
    P = []
    for it in dr['items']:
        if it[0] == 'l':
            a, b = it[1], it[2]
            if not P or abs(P[-1][0]-a.x) > 0.05 or abs(P[-1][1]-a.y) > 0.05: P.append((a.x, a.y))
            P.append((b.x, b.y))
        elif it[0] == 'c':
            a, b = it[1], it[4]
            if not P: P.append((a.x, a.y))
            P.append((b.x, b.y))
    return P

def frames(drs):
    H = [d for d in drs if abs((d.get('width') or 0) - 0.76) < 0.05 and len(d['items']) == 1 and d['items'][0][0] == 'l']
    hor = []; ver = []
    for d in H:
        a, b = d['items'][0][1], d['items'][0][2]
        if abs(a.y - b.y) < 0.2 and abs(a.x - b.x) > 100: hor.append((min(a.x, b.x), max(a.x, b.x), a.y))
        if abs(a.x - b.x) < 0.2 and abs(a.y - b.y) > 40: ver.append((a.x, min(a.y, b.y), max(a.y, b.y)))
    out = []
    for v in ver:
        x, y0, y1 = v
        # moldura: linhas horizontais em y0 e y1 que começam em x, e vertical do lado direito
        top = [h for h in hor if abs(h[0]-x) < 0.5 and abs(h[2]-y0) < 0.5]
        bot = [h for h in hor if abs(h[0]-x) < 0.5 and abs(h[2]-y1) < 0.5]
        if top and bot:
            x1 = top[0][1]
            if any(abs(w[0]-x1) < 0.5 and abs(w[1]-y0) < 0.5 and abs(w[2]-y1) < 0.5 for w in ver):
                out.append((round(x, 1), round(y0, 1), round(x1, 1), round(y1, 1)))
    out = sorted(set(out), key=lambda r: (r[1], r[0]))
    return out

def linfit(pairs):
    n = len(pairs)
    if n < 2: return None
    sx = sum(p[0] for p in pairs); sy = sum(p[1] for p in pairs)
    sxx = sum(p[0]**2 for p in pairs); sxy = sum(p[0]*p[1] for p in pairs)
    den = n*sxx - sx*sx
    if abs(den) < 1e-9: return None
    a = (n*sxy - sx*sy)/den; b = (sy - a*sx)/n
    res = max(abs(a*p[0]+b-p[1]) for p in pairs)
    return a, b, res

def axis_labels(words, fr, side):
    x0, y0, x1, y1 = fr
    L = []
    for w in words:
        cx, cy = (w[0]+w[2])/2, (w[1]+w[3])/2
        if side == 'bottom' and x0-8 <= cx <= x1+8 and y1+2 <= w[1] <= y1+14: L.append((cx, w))
        if side == 'left' and x0-17 <= w[2] <= x0-2 and y0-6 <= cy <= y1+6: L.append((cy, w))
        if side == 'right' and x1+2 <= w[0] <= x1+16 and y0-6 <= cy <= y1+6: L.append((cy, w))
    return L

def calib(L, decf):
    pairs = []
    for pos, w in L:
        t = decf(w[4])
        if NUM.match(t): pairs.append((pos, float(t)))
    if len(pairs) < 3: return None
    fit = linfit(pairs)
    if not fit or fit[2] > 0.02*max(abs(p[1]) for p in pairs) + 1e-6: return None
    return fit

def pick_dec(words, fr):
    L = axis_labels(words, fr, 'bottom')
    for dfun in (dec, lambda t: t):
        c = calib(L, dfun)
        if c and abs(c[1] + c[0]*fr[0]) < 0.5*abs(c[0])*(fr[2]-fr[0]):  # Q≈0 perto da esquerda
            return dfun, c
    return None, None

def curves_in(drs, fr):
    x0, y0, x1, y1 = fr
    C = []
    for d in drs:
        wd = round(d.get('width') or 0, 2)
        if wd not in (0.44, 1.2) or d.get('dashes') not in (None, '[] 0'): continue
        r = d['rect']
        if r.x0 < x0-1 or r.x1 > x1+1 or r.y0 < y0-1 or r.y1 > y1+1: continue
        P = pts_of(d)
        if len(P) < 4 or (r.x1 - r.x0) < 8: continue
        P.sort()
        C.append({'w': wd, 'P': P})
    # juntar troço fino (início) com o grosso que continua
    bold = [c for c in C if c['w'] == 1.2]; thin = [c for c in C if c['w'] == 0.44]
    out = []
    used = set()
    for b in bold:
        st = b['P'][0]; best = None
        for i, t in enumerate(thin):
            if i in used: continue
            e = t['P'][-1]
            dd = math.hypot(e[0]-st[0], e[1]-st[1])
            if dd < 1.5 and (best is None or dd < best[0]): best = (dd, i)
        P = b['P']; Pin = []
        if best:
            used.add(best[1]); Pin = thin[best[1]]['P']
        out.append({'all': Pin + P, 'bold': P})
    # troços finos longos que ficam sozinhos (curvas sem parte recomendada)
    for i, t in enumerate(thin):
        if i not in used and t['P'][-1][0]-t['P'][0][0] > 40:
            out.append({'all': t['P'], 'bold': []})
    return out

def dist_poly(pt, P):
    best = 1e9
    for (ax, ay), (bx, by) in zip(P, P[1:]):
        dx, dy = bx-ax, by-ay; L2 = dx*dx+dy*dy
        t = 0 if L2 == 0 else max(0, min(1, ((pt[0]-ax)*dx+(pt[1]-ay)*dy)/L2))
        best = min(best, math.hypot(pt[0]-ax-t*dx, pt[1]-ay-t*dy))
    return best

LBL = re.compile(r'^/(\d{2,3})(?:-(\d{2,3}))?$')
def labels(words, fr, decf):
    x0, y0, x1, y1 = fr
    out = []
    ws = [w for w in words if x0-2 <= w[0] <= x1+40 and y0-4 <= w[1] <= y1+4]
    for w in ws:
        t = decf(w[4]); m = LBL.match(t)
        if not m: continue
        nxt = [v for v in ws if 0 <= v[0]-w[2] < 6 and abs(v[1]-w[1]) < 2]
        npsh = any('NPSH' in decf(v[4]) or v[4] in ('.fnq`/', '(NPSH)') for v in nxt)
        out.append({'D': (float(m.group(1))+float(m.group(2)))/2 if m.group(2) else float(m.group(1)), 'D2': float(m.group(2)) if m.group(2) else None, 'txt': t, 'npsh': npsh,
                    'pt': ((w[0]+w[2])/2, w[3]), 'box': w[:4]})
    return out

def assign(lbls, curves, key='all'):
    cand = []
    for i, l in enumerate(lbls):
        x0, y0, x1, y1 = l['box']
        probe = [((x0+x1)/2, y1+1), (x0, y1+1), (x1, y1+1), (x0-2, (y0+y1)/2), ((x0+x1)/2, y0-1)]
        for j, c in enumerate(curves):
            dd = min(dist_poly(p, c[key]) for p in probe)
            cand.append((dd, i, j))
    cand.sort(); A = {}; usedc = set()
    for dd, i, j in cand:
        if i in A or j in usedc or dd > 14: continue
        A[i] = j; usedc.add(j)
    return A

def to_data(P, fx, fy):
    return [((x - fx[1]) / fx[0] if False else fx[0]*x + fx[1], fy[0]*y + fy[1]) for x, y in P]

def resample(D, Q):
    D = sorted(D)
    def at(q):
        if q <= D[0][0]: return D[0][1]
        if q >= D[-1][0]: return D[-1][1]
        for (a, b), (c, e) in zip(D, D[1:]):
            if a <= q <= c: return b + (e-b)*(q-a)/(c-a) if c > a else b
    return [at(q) for q in Q]

def page_models(pg):
    d = f.open(PDF); p = d[pg]
    words = p.get_text('words'); drs = p.get_drawings()
    blocks = p.get_text('dict')['blocks']
    titles = []
    for b in blocks:
        for l in b.get('lines', []):
            for s in l['spans']:
                m = re.match(r'^NB, NK (\d+-\d+(?:\.\d)?)$', s['text'].strip())
                if m and 'Bold' in s['font']: titles.append((s['bbox'][1], m.group(1)))
    head = p.get_text()
    pm = re.search(r'Performance curves\s*\n?\s*(\d)-pole', head)
    FR = frames(drs)
    res = []
    i = 0
    while i < len(FR) - 1:
        fh, fp = FR[i], FR[i+1]
        # o gráfico P2 fica logo abaixo do H, com a mesma largura
        if abs(fh[0]-fp[0]) > 1 or abs(fh[2]-fp[2]) > 1 or fp[1]-fh[3] > 40:
            i += 1; continue
        title = [t for t in titles if fh[1]-60 < t[0] < fh[1]]
        mat = None
        reg = ' '.join(w[4] for w in words if fh[1]-25 < w[1] < fh[1] and w[0] > fh[0]+150)
        if 'Stainless' in reg: mat = 'inox'
        elif 'Cast' in reg: mat = 'ff'
        decf, cq = pick_dec(words, fh)
        decp, cqp = pick_dec(words, fp)
        rec = {'page': pg+1, 'model': title[-1][1] if title else None, 'mat': mat, 'poles': int(pm.group(1)) if pm else None, 'frame': fh, 'err': None}
        res.append(rec); i += 2
        if not decf or not decp: rec['err'] = 'eixo Q'; continue
        ch = calib(axis_labels(words, fh, 'left'), decf); cn = calib(axis_labels(words, fh, 'right'), decf); cp = calib(axis_labels(words, fp, 'left'), decp)
        if not ch or not cp: rec['err'] = 'eixo H/P'; continue
        Ch = curves_in(drs, fh); Cp = curves_in(drs, fp)
        Lh = labels(words, fh, decf); Lp = labels(words, fp, decp)
        Hc, Nc, Pc = {}, {}, {}
        # NPSH: pela etiqueta "(NPSH)" mais próxima; as restantes curvas são H
        Ln = [l for l in Lh if l['npsh']]; Lq = [l for l in Lh if not l['npsh']]
        # curvas NPSH: sobem com o caudal (as curvas H descem)
        def rising(c):
            D = to_data(c['bold'] if len(c['bold']) > 3 else c['all'][len(c['all'])//2:], cq, ch); return D[-1][1] > D[0][1]
        npi = [j for j, c in enumerate(Ch) if rising(c)]
        # NPSH quase horizontal: as curvas a mais são as mais baixas do gráfico
        extra = len(Ch) - len(npi) - len(Lq)
        if extra > 0:
            rest = sorted((j for j in range(len(Ch)) if j not in npi), key=lambda j: -sum(p[1] for p in Ch[j]['all'])/len(Ch[j]['all']))
            npi += rest[:extra]
        An = assign(Ln, [Ch[j] for j in npi]); usedN = set()
        for li, k in An.items():
            if cn: Nc[Ln[li]['D']] = {'all': to_data(Ch[npi[k]]['all'], cq, cn)}
            usedN.add(npi[k])
        left = [j for j in npi if j not in usedN]
        Dq = sorted(l['D'] for l in Lq)
        miss = [D for D in (Dq[:1] + Dq[-1:]) if D not in Nc] if Dq else []
        if len(left) == 1 and miss and cn:  # NPSH sem etiqueta legível: é do diâmetro máximo ou mínimo que falta
            Nc[miss[0]] = {'all': to_data(Ch[left[0]]['all'], cq, cn)}
        usedN |= set(npi)
        Hcur = [c for j, c in enumerate(Ch) if j not in usedN]
        # H e P2 por ordem: maior diâmetro → maior H e maior P2 (as etiquetas dos diâmetros ficam muito juntas)
        def order(curves, fy):
            D = [to_data(c['all'], cq if fy is not cp else cqp, fy) for c in curves]
            qa = max(min(p[0] for p in d) for d in D); qb = min(max(p[0] for p in d) for d in D)
            qm = (qa+qb)/2 if qb > qa else qa
            return sorted(range(len(curves)), key=lambda j: resample(D[j], [qm])[0])
        Ds = sorted(Lq, key=lambda l: l['D'])
        if len(Hcur) == len(Ds) and Ds:
            for l, j in zip(Ds, order(Hcur, ch)):
                c = Hcur[j]; Hc[l['D']] = {'all': to_data(c['all'], cq, ch), 'bold': to_data(c['bold'], cq, ch) if c['bold'] else [], 'txt': l['txt']}
        else: rec['err'] = f'H: {len(Ds)} etiquetas, {len(Hcur)} curvas'
        Dp = sorted(Lp, key=lambda l: l['D'])
        if len(Cp) == len(Dp) and Dp:
            for l, j in zip(Dp, order(Cp, cp)): Pc[l['D']] = to_data(Cp[j]['all'], cqp, cp)
        elif Dp: rec['err'] = (rec['err'] or '') + f' P: {len(Dp)} etiquetas, {len(Cp)} curvas'
        rec['H'] = Hc; rec['N'] = Nc; rec['P'] = Pc
        rec['nH'] = (len(Lh) - sum(l['npsh'] for l in Lh), len(Ch)); rec['nP'] = (len(Lp), len(Cp))
    return res

if __name__ == '__main__':
    import pprint
    for pg in map(int, sys.argv[1:]):
        for r in page_models(pg):
            print(r['page'], r['model'], r['mat'], r['poles'], r['err'], 'H', sorted(r.get('H', {})), 'N', sorted(r.get('N', {})), 'P', sorted(r.get('P', {})), r.get('nH'), r.get('nP'))
