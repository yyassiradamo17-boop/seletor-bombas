# Constrói a base de dados de tubos (TUBOS) para o seletor: DN/DE, classe, Ø exterior, espessura, Ø interior e PN
# Fontes: pasta catálogo/Condutas (Politejo PEAD, EN 1452 PVC-U, Saint-Gobain FFD, ASME B36.10M, Flowtite GRP)
import json, sys, re, os, openpyxl
sys.stdout.reconfigure(encoding='utf-8')
H = os.path.dirname(os.path.abspath(__file__))
CAT = os.path.join(H, '..', 'catálogo', 'Condutas', '')
r1 = lambda x: round(x, 1)
T = []

# ---------- PEAD (EN 12201) · espessuras do catálogo Politejo (por SDR) ----------
PE = json.load(open(os.path.join(H, 'pe_sdr.json')))
SDRS = [41, 33, 26, 21, 17, 13.6, 11, 9, 7.4]
PN100 = {41: 4, 33: 5, 26: 6.3, 21: 8, 17: 10, 13.6: 12.5, 11: 16, 9: 20, 7.4: 25}
PN80 = {41: 3.2, 33: 4, 26: 5, 21: 6.3, 17: 8, 13.6: 10, 11: 12.5, 9: 16, 7.4: 20}
for g, m, PN in (('PEAD PE100', 0, PN100), ('PEAD PE80', 1, PN80)):
    cl = []
    for sdr in SDRS:
        rows = sorted((int(od), e) for od, e in PE[str(sdr)].items())
        if g == 'PEAD PE80' and sdr in (41,): continue
        cl.append({'n': f'SDR {str(sdr).replace(".", ",")} · PN {str(PN[sdr]).replace(".", ",")}',
                   'r': [[od, od, e, r1(od - 2*e), PN[sdr]] for od, e in rows]})
    T.append({'g': g, 'm': m, 'de': 1, 'src': 'EN 12201 · catálogo Politejo CD11R02 (2014), pág. 11–12', 'cl': cl})

# ---------- PVC-U (EN 1452) · espessuras mínimas; PN com C = 2,5 (DE ≤ 90) e C = 2,0 (DE ≥ 110) ----------
SD = [41, 34.4, 33, 26, 21, 17, 13.6, 11]
PNs = {2.5: [None, 6, 6, 8, 10, 12.5, 16, 20], 2.0: [6, 7.5, 8, 10, 12.5, 16, 20, 25]}
V = {  # DE: espessuras pela ordem de SD (None = não normalizado)
 12: [None]*7 + [1.5], 16: [None]*7 + [1.5], 20: [None]*6 + [1.5, 1.9], 25: [None]*5 + [1.5, 1.9, 2.3],
 32: [None]*3 + [1.5, 1.6, 1.9, 2.4, 2.9], 40: [None, None, 1.5, 1.6, 1.9, 2.4, 3.0, 3.7], 50: [None, None, 1.6, 2.0, 2.4, 3.0, 3.7, 4.6],
 63: [None, None, 2.0, 2.5, 3.0, 3.8, 4.7, 5.8], 75: [None, None, 2.3, 2.9, 3.6, 4.5, 5.6, 6.8], 90: [None, None, 2.8, 3.5, 4.3, 5.4, 6.7, 8.2],
 110: [2.7, 3.2, 3.4, 4.2, 5.3, 6.6, 8.1, 10.0], 125: [3.1, 3.7, 3.9, 4.8, 6.0, 7.4, 9.2, 11.4], 140: [3.5, 4.1, 4.3, 5.4, 6.7, 8.3, 10.3, 12.7],
 160: [4.0, 4.7, 4.9, 6.2, 7.7, 9.5, 11.8, 14.6], 180: [4.4, 5.3, 5.5, 6.9, 8.6, 10.7, 13.3, 16.4], 200: [4.9, 5.9, 6.2, 7.7, 9.6, 11.9, 14.7, 18.2],
 225: [5.5, 6.6, 6.9, 8.6, 10.8, 13.4, 16.6, None], 250: [6.2, 7.3, 7.7, 9.6, 11.9, 14.8, 18.4, None], 280: [6.9, 8.2, 8.6, 10.7, 13.4, 16.6, 20.6, None],
 315: [7.7, 9.2, 9.7, 12.1, 15.0, 18.7, 23.2, None], 355: [8.7, 10.4, 10.9, 13.6, 16.9, 21.1, 26.1, None], 400: [9.8, 11.7, 12.3, 15.3, 19.1, 23.7, 29.4, None],
 450: [11.0, 13.2, 13.8, 17.2, 21.5, 26.7, 33.1, None], 500: [12.3, 14.6, 15.3, 19.1, 23.9, 29.7, 36.8, None], 560: [13.7, 16.4, 17.2, 21.4, 26.7, None, None, None],
 630: [15.4, 18.4, 19.3, 24.1, 30.0, None, None, None], 710: [17.4, 20.7, 21.8, 27.2, None, None, None, None], 800: [19.6, 23.3, 24.5, 30.6, None, None, None, None],
 900: [22.0, 26.3, 27.6, None, None, None, None, None], 1000: [24.5, 29.2, 30.6, None, None, None, None, None]}
cl = []
for j, sdr in enumerate(SD):
    S = (sdr - 1) / 2
    rows = []
    for od, es in V.items():
        e = es[j]; pn = PNs[2.5 if od <= 90 else 2.0][j]
        if e is None or pn is None: continue
        rows.append([od, od, e, r1(od - 2*e), pn])
    if rows:
        pns = sorted({r[4] for r in rows})
        cl.append({'n': f'SDR {str(sdr).replace(".", ",")} (S {str(round(S, 1)).replace(".", ",")}) · PN {"/".join(str(p).replace(".", ",") for p in pns)}', 'r': rows})
T.append({'g': 'PVC-U', 'm': 2, 'de': 1, 'src': 'EN 1452 (espessuras mínimas; PN com C = 2,5 até DE 90 e C = 2,0 a partir de DE 110)', 'cl': cl})

# ---------- Ferro fundido dúctil · K9/K7 (catálogo Saint-Gobain) e classes C da EN 545 ----------
DE = {60: 77, 65: 82, 80: 98, 100: 118, 125: 144, 150: 170, 200: 222, 250: 274, 300: 326, 350: 378, 400: 429, 450: 480,
      500: 532, 600: 635, 700: 738, 800: 842, 900: 945, 1000: 1048, 1200: 1255}
lin = lambda dn: 3.0 if dn <= 300 else 5.0 if dn <= 600 else 6.0   # revestimento de argamassa de cimento (nominal)
K9 = {80: (6.0, 64), 100: (6.0, 64), 150: (6.0, 64), 200: (6.3, 62), 250: (6.8, 55), 300: (7.2, 49), 350: (7.65, 46), 400: (8.1, 42),
      450: (8.55, 41), 500: (9.0, 38), 600: (9.9, 36), 700: (10.8, 34), 800: (11.7, 32), 900: (12.6, 31), 1000: (13.5, 30), 1200: (15.3, 29)}
K7 = {150: (5.2, 64), 200: (5.4, 53), 250: (5.5, 44), 300: (5.7, 38), 350: (5.95, 34), 400: (6.3, 30), 450: (6.65, 29), 500: (7.0, 28),
      600: (7.7, 26), 700: (8.4, 24), 800: (9.1, 23), 900: (9.8, 23), 1000: (10.5, 22), 1200: (11.9, 21)}
cl = []
for C in (25, 30, 40):
    rows = []
    for dn, de in DE.items():
        emin = max(3.0, C*3*de / (20*420 + C*3))           # EN 545:2010: e_min = PFA·SF·DE/(20·Rm + PFA·SF), SF = 3, Rm = 420 MPa
        e = r1(emin + 1.3 + 0.001*dn)                       # e_nom = e_min + (1,3 + 0,001·DN)
        rows.append([dn, de, e, r1(de - 2*e - 2*lin(dn)), C])
    cl.append({'n': f'EN 545 C{C} · PFA {C} bar', 'r': rows})
for nm, K in (('K9', K9), ('K7', K7)):
    cl.append({'n': f'{nm} (NBR 7675 / ISO 2531) · PSA {min(v[1] for v in K.values())}–{max(v[1] for v in K.values())} bar',
               'r': [[dn, DE[dn], e, r1(DE[dn] - 2*e - 2*lin(dn)), psa] for dn, (e, psa) in K.items()]})
T.append({'g': 'Ferro fundido dúctil', 'm': 3, 'de': 0,
          'src': 'K9/K7: catálogo Saint-Gobain Canalização 2023.1, pág. 47 e 252–253 (e ferro, PSA junta JGS); C25/C30/C40: EN 545:2010 (espessura nominal pela fórmula da norma); Ø int. = DE − 2·e − 2·cimento (3/5/6 mm)', 'cl': cl})

# ---------- Aço (ASME B36.10M) · pressão admissível pela fórmula de Barlow ----------
ws = openpyxl.load_workbook(CAT + 'Tubos aco ASME B36.10M.xlsx', data_only=True).active
ORD = ['10', '20', '30', 'STD', '40', '60', 'XS', '80', '100', '120', '140', '160', 'XXS']
SCH = {k: {} for k in ORD}
for r in ws.iter_rows(min_row=5, values_only=True):
    if r[1] is None or r[1] < 15 or r[1] == 90: continue
    toks = [t.strip() for t in str(r[2]).split('/')]
    for t in toks:
        k = t[:-1] if t in ('10S',) else t     # 10S só onde não há Sch 10
        if k in SCH and (t != '10S' or r[1] not in SCH['10']):
            SCH[k][r[1]] = (r[0], float(r[3]), float(r[4]))
SA = 2/3*235                                         # tensão admissível: 2/3 de ReH (aço L235 / API 5L B), tolerância −12,5 %
cl = []
for k in ORD:
    rows = [[dn, od, t, r1(od - 2*t), int(20*SA*0.875*t/od)] for dn, (nps, od, t) in sorted(SCH[k].items())]
    if len(rows) >= 3: cl.append({'n': ('Sch ' + k if k[0].isdigit() else k) + (' (10S nos pequenos DN)' if k == '10' else ''), 'r': rows})
T.append({'g': 'Aço', 'm': 4, 'de': 0, 'src': 'ASME B36.10M (Ø ext. e espessura); pressão admissível pela fórmula de Barlow com S = 2/3·ReH (L235) e −12,5 % de tolerância, limitada na prática pelas flanges e acessórios', 'cl': cl})

# ---------- PRFV / GRP (Flowtite, EN 1796) ----------
G = json.load(open(os.path.join(H, 'grp.json')))
cl = []
for k in sorted(G, key=lambda k: tuple(int(x) for x in re.findall(r'\d+', k))):
    pn, sn = (int(x) for x in re.findall(r'\d+', k))
    rows = [[int(dn), de, e, r1(de - 2*e), pn] for dn, (de, e) in sorted(G[k].items(), key=lambda x: int(x[0])) if int(dn) <= 2000]
    cl.append({'n': f'SN {sn} · PN {pn}', 'r': rows})
T.append({'g': 'PRFV / GRP', 'm': 8, 'de': 0, 'src': 'Flowtite Standard Pressure Pipe (Amiblu, rev. 1.3, 2020), pág. 5–10', 'cl': cl})

# ---------- Betão (indicativo; sem catálogo) ----------
rows = [[dn, dn + 2*round(dn/12 + 25), round(dn/12 + 25), dn, None] for dn in (300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1400, 1500, 1600, 1800, 2000)]
T.append({'g': 'Betão', 'm': 7, 'de': 0, 'src': 'Indicativo (sem catálogo): Ø int. = DN, espessura ≈ DN/12 + 25 mm; PN conforme o fabricante (tubos com alma de aço, EN 641/642)',
          'cl': [{'n': 'Betão armado · DI = DN (indicativo)', 'r': rows}]})

for t in T:
    print(t['g'], len(t['cl']), 'classes,', sum(len(c['r']) for c in t['cl']), 'linhas')
    for c in t['cl']:
        bad = [r for r in c['r'] if r[3] <= 0 or r[2] <= 0]
        if bad: print('  !!', c['n'], bad)
json.dump(T, open(os.path.join(H, 'tubos.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print('KB', os.path.getsize(os.path.join(H, 'tubos.json'))//1024)
# verificações: defaults do seletor
pe = next(c for c in T[0]['cl'] if c['n'].startswith('SDR 17 '))
print('PE100 SDR17 DE160', [r for r in pe['r'] if r[0] == 160])
st = next(c for c in T[4]['cl'] if c['n'] == 'Sch 40')
print('Aço Sch40 DN150', [r for r in st['r'] if r[0] == 150])
k9 = next(c for c in T[3]['cl'] if c['n'].startswith('K9'))
print('FFD K9 DN200', [r for r in k9['r'] if r[0] == 200], 'C40 DN200', [r for r in T[3]['cl'][2]['r'] if r[0] == 200])
