# Seletor de bombas — funcionalidades e próximos passos

Estado em 06/11/2026 · versão 14 (exportação para o EPANET; v12: o utilizador importa os catálogos de bombas em PDF; sem curvas embutidas nem catálogo de exemplo; v11: catálogo de tubos; web app autónoma `Seletor de Bombas.html`; v10: Grundfos NB/NK e SP; v9: comparar até 5 bombas; v8: η do rotor aparado; v7: poço de bombagem; v6: golpe de aríete; v5: bombas de reserva; v4: cenários de nível; v3: exportação .docx/PDF, fichas partilhadas, η estimado por Gülich)

Artefacto: https://claude.ai/artifact/UFLBANfUyT7KRLMH65j1dT

## 0. Web app autónoma

- `Seletor de Bombas.html` (pasta do projeto, ~2,7 MB) é a mesma app do artefacto num só ficheiro: abre-se com duplo clique em qualquer navegador (Chrome, Edge, Firefox), sem claude.ai e sem internet. As bibliotecas (pdf.js, JSZip, html2canvas, jsPDF) e as fontes estão embutidas.
- Pode ser copiada para outros computadores, enviada por e-mail ou alojada em qualquer servidor web estático (ex.: SharePoint, GitHub Pages, intranet).
- O projeto em curso fica guardado no navegador (localStorage, por computador e por navegador). Para levar o projeto para outro lado: **Guardar projeto (.json)** e **Abrir projeto** (por baixo dos dados do sistema).
- As exportações .docx e PDF descarregam diretamente para a pasta de transferências.
- Gera-se a partir do artefacto com `extracao/standalone.py` (usa `seletor-bombas.html`, `libs/` e `fonts/`, que estão em `extracao/`); depois de cada nova versão do artefacto basta voltar a correr o script.

## 1. Base de dados

**Desde a v12 estas curvas já não vêm embutidas na app** (ver secção 7): nem catálogo de exemplo. As curvas extraídas e os scripts continuam em `extracao/`, para referência ou para voltar a embutir.

| Fonte | Conteúdo | Dados disponíveis |
|---|---|---|
| KSB Etanorm / Etanorm-R / RSY (50 Hz, cat. 1311.45/12-EN) | 185 páginas, 807 diâmetros de rotor, 2900 / 1450 / 960 rpm | H, P, NPSHr; η calculado a partir de P |
| Grundfos HS (catálogo técnico v5) | 36 modelos, 2, 4 e 6 polos, 180 diâmetros | H, η, P2, NPSHr, gama recomendada |
| Grundfos CR / CRN (60 Hz) | cerca de 140 variantes (CRI/CRN com hidráulica igual à CR foram removidas) | H, η, NPSHr, gama recomendada; P calculado a partir de η |
| Grundfos NB/NK (data booklet NB, NBE, NK, NKE, 50 Hz) | 109 modelos (2, 4 e 6 polos), 465 diâmetros | H, P2, NPSHr (diâmetros máx. e mín., interpolado nos intermédios), gama recomendada; η calculado a partir de P2 |
| Grundfos SP A / SP (data booklet, 50 Hz) | 15 famílias (SP 1A a SP 215), 381 variantes por n.º de andares e rotor reduzido | H, P2, NPSHr (exceto SP A), gama recomendada; η calculado a partir de P2; curvas incluem as perdas da válvula de retenção |
| Speroni (catálogo geral 2020 rev. 14) | 497 modelos | Q–H e potência do motor (sem η nem NPSHr); η estimado por Gülich |

- As curvas foram vetorizadas dos PDF, com 16 pontos por curva e interpolação linear.
- As curvas CR podem ser convertidas de 60 Hz para 50 Hz pelas leis de semelhança (2900/3500).
- NB/NK e SP extraídos dos PDF vetoriais (v10) com os scripts em `extracao/` (PyMuPDF): calibração automática dos eixos pelas etiquetas, troço grosso = gama recomendada, associação etiqueta–curva pela ordem (H e P2 crescem com o diâmetro) e pela proximidade (NPSH, potências SP). No NB/NK o texto dos eixos usa uma fonte com codificação trocada, descodificada no script.
- Validação: NB/NK 125-200 Ø224 dá η<sub>BEP</sub> = 87,8 % a 560 m³/h, igual à linha de rendimento do catálogo; SP 77 ≈ 77 % (curva Eta ≈ 78 %), SP 17 ≈ 74 %, SP 1A ≈ 40 %. Em cada família SP o η é coerente entre variantes; com 1–3 andares é mais baixo porque as curvas incluem as perdas da válvula.
- Velocidades: NB/NK 2900/1450/960 rpm; SP 2870 rpm (motores 4" e 6") e 2900 rpm (SP 77 e acima).

## 2. Dados do sistema (painel esquerdo)

- Caudal de projeto em m³/h ou l/s.
- Cotas: níveis mínimo e máximo de aspiração, níveis máximo e mínimo de descarga, eixo da bomba e pressão residual.
- Condutas de aspiração e de compressão: comprimento, Ø interior, material (preenche a rugosidade, o C e, na compressão, o módulo E), ΣK; na compressão também a espessura da parede e a classe PN.
- Tubo de catálogo (v11): escolhe-se material · classe e depois o DN/DE; preenche Ø interior, material, k, C, espessura, E e PN. No aço e no FFD o PN fica na flange normalizada (6/10/16/25/40) até à pressão admissível do tubo. Alterar o Ø ou a espessura à mão passa a conduta para manual. Por baixo de cada conduta aparece o menor DN/DE da classe com v ≤ 1,5 m/s (aspiração) ou v ≤ v máx. (compressão), com botão para o aplicar. Se o golpe de aríete exceder o PN, a recomendação indica a classe do mesmo material e DN que o cobre.

| Material | Classes | Fonte |
|---|---|---|
| PEAD PE100 / PE80 | SDR 41 a 7,4 (PN 4–25 / 3,2–20), DE 20–2000 | EN 12201, catálogo Politejo CD11R02 |
| PVC-U | SDR 41 a 11, DE 12–1000, PN por linha (C = 2,5 até DE 90; 2,0 a partir de 110) | EN 1452 (tabela da captura de ecrã; corrigido DE 400 SDR 26 = 15,3 mm) |
| Ferro fundido dúctil | K9, K7 (e e PSA do catálogo) e EN 545 C25/C30/C40 (espessura pela fórmula da norma), DN 60–1200 | Saint-Gobain Canalização 2023.1; Ø int. = DE − 2e − 2·cimento (3/5/6 mm) |
| Aço | Sch 10 a 160, STD, XS, XXS, DN 15–600 | ASME B36.10M (folha de cálculo); p. adm. por Barlow, S = 2/3·235 MPa, −12,5 % |
| PRFV / GRP | SN 5000 / 10000 × PN 6–32, DN 300–2000 | Flowtite Standard Pressure Pipe (Amiblu 2020) |
| Betão | DN 300–2000, DI = DN, espessura ≈ DN/12 + 25 mm | indicativo — não havia catálogo de betão na pasta |

- Novos materiais na lista: PEAD PE80 (E = 0,8 GPa) e PRFV (k = 0,029 mm, C = 150, E = 12 GPa). Os projetos guardados antes da v11 abrem com as condutas à mão e os materiais renumerados automaticamente.
- O script `extracao/tubos.py` gera `tubos.json` a partir dos catálogos (`pe_sdr.json` e `grp.json` vêm da extração vetorial dos PDF).
- Perdas de carga por Darcy-Weisbach (Colebrook, iniciado por Swamee-Jain) ou Hazen-Williams.
- Água: temperatura (ρ, ν e pv por tabela) e altitude (p<sub>atm</sub>).
- Bombas em paralelo (1 a 4) ou em série (1 a 3), mais 0 a 2 bombas de reserva (em série, um grupo completo por reserva), com funcionamento alternado ou reserva fixa.
- Critérios editáveis:
  - tolerâncias de caudal;
  - zona preferencial Q/Q<sub>BEP</sub>;
  - margem e relação de NPSH;
  - η estimado fixo, ou estimativa de Gülich por velocidade específica (opção, ligada por omissão);
  - velocidade máxima na compressão.
- Energia e custos: horas por ano, tarifa, moeda, vida útil, taxa de atualização, manutenção anual (% do preço) e vida da bomba em horas de funcionamento.
- Uma faixa de resumo mostra H do sistema, perdas, velocidades, NPSH disponível e potência hidráulica.

## 3. Seleção

- Interseção de cada curva (ou do conjunto em paralelo/série) com a curva do sistema.
- Proposta de rotor aparado, por interpolação entre diâmetros consecutivos do catálogo:
  - Q, H e NPSH<sub>r</sub> interpolados linearmente entre as duas curvas;
  - η pela forma de Moody, 1 − η(D) = (1 − η<sub>hi</sub>)·(D<sub>hi</sub>/D)<sup>n</sup>, com o expoente n ajustado ponto a ponto às duas curvas do catálogo (exato nos dois diâmetros);
  - potência recalculada a partir de η (coerência P–η);
  - os cartões e a memória indicam o aparo face ao diâmetro máximo e a perda de η no BEP.
- Verificações:
  - caudal;
  - NPSH;
  - posição face ao BEP;
  - gama do fabricante;
  - velocidades nas condutas;
  - motor do catálogo.
- Filtros por fabricante, por velocidade e por texto.
- Ordenação por energia por m³, η, proximidade ao BEP, ajuste ao caudal ou potência do motor.
- Escolha das bombas A e B para comparar, e até mais três (C, D, E) com o botão "+" em cada linha da tabela de seleção e do catálogo.

## 3a. Cenários de nível (envolvente de funcionamento)

- O ponto de projeto usa a altura estática máxima (aspiração mín., descarga máx.).
- Com os níveis máx./mín. preenchidos, cada bomba é verificada também em:
  - **H<sub>est</sub> mínima** (aspiração máx., descarga mín.): maior caudal, maior potência, maior NPSH<sub>r</sub>;
  - **NPSH crítico** (aspiração mín., descarga mín.): caudal alto com o menor NPSH disponível;
  - **Aspiração cheia** (aspiração máx., descarga máx.).
- Falha a seleção quando não há ponto de funcionamento num cenário (fora da curva) ou quando o NPSH não verifica num cenário. Fora da zona preferencial na envolvente dá aviso.
- O motor passa a cobrir a potência máxima da envolvente (≥ 1,05 × P<sub>máx</sub>), se esta exceder o motor escolhido com a folga de Azevedo Netto.
- A energia anual continua calculada no ponto de projeto (estimativa conservadora).
- Os cartões mostram o quadro de cenários; os gráficos mostram a curva do sistema com H<sub>est</sub> mínima, o NPSH disponível com aspiração máx. e os pontos de cada cenário.
- A memória de cálculo tem a secção "Envolvente de funcionamento" e a justificativa compara a gama de caudal e a variação de níveis das duas bombas.
- Deixar os níveis máx./mín. vazios desliga os cenários (projetos guardados antes da v4 abrem sem cenários).

## 4. Ponto de funcionamento

- Cartões das bombas A e B com grandezas e verificações.
- Gráficos SVG:
  - H–Q com η, curva do sistema e outros diâmetros do modelo;
  - NPSH disponível e requerido, com a margem;
  - potência absorvida, com a linha da potência do motor.
- Variação de velocidade, com cálculo automático da velocidade que dá o caudal de projeto (variador de frequência).
- Motor IEC escolhido com as folgas de Azevedo Netto e η do motor IE3.

## 5. Comparador (2 a 5 bombas)

- Com A e B apenas, mantém-se a comparação e a justificativa anteriores. Com C–E, a tabela, o veredicto e a justificativa passam a ter uma coluna por bomba; cada bomba extra tem "retirar".
- Pontuação: em cada critério a melhor recebe 10 pontos e as outras na proporção (mesmas regras do par); o veredicto ordena primeiro as que cumprem e depois pela pontuação, com empate se as duas primeiras diferirem menos de 0,15.
- A justificativa para 3 a 5 bombas tem objeto (quadro por bomba), análise (ajuste, rendimento e energia, cavitação, posição na curva, motor), quadro multicritério e conclusão com a ordenação.
- A memória de cálculo pode ser feita para qualquer bomba da comparação (A a E).
- O separador "Ponto de funcionamento" continua a sobrepor só A e B.


- Tabela de grandezas: Q, H, potência, kWh/m³, energia e custo anual, preço de aquisição opcional.
- Análise multicritério com pesos editáveis:
  - custo de ciclo de vida;
  - η;
  - cavitação;
  - BEP;
  - ajuste ao caudal;
  - motor.
- Veredicto com a pontuação ponderada.
- Memória justificativa automática (objeto, análise, quadro multicritério, conclusão), que se pode copiar para o Word.

## 5a. Reserva e custo de ciclo de vida

- Bombas instaladas = (em paralelo + reserva) × em série.
- Funcionamento alternado: as horas anuais repartem-se por todas as bombas (h por bomba = h/ano × N<sub>serviço</sub> / N<sub>instaladas</sub>). Reserva fixa: as bombas de serviço fazem todas as horas e a reserva fica parada (aviso para a exercitar ou alternar).
- Custo de ciclo de vida (valor atual) = aquisição × bombas instaladas + energia + manutenção (% do preço × bombas instaladas × fator de atualização) + substituições.
- Substituições: cada bomba em rotação é substituída ao fim da vida em horas; cada substituição é atualizada ao ano em que ocorre. É aqui que o funcionamento alternado compensa (exemplo: 1 substituição com reserva fixa, 0 com alternância).
- A energia não muda com a reserva (funcionam sempre as mesmas bombas em paralelo).
- Verificação "Bomba de reserva": cumpre com reserva alternada; aviso sem reserva ou com reserva fixa.
- O comparador mostra bombas instaladas, horas por bomba, manutenção e substituições; a memória de cálculo tem a secção "Reserva e custo de ciclo de vida" (o quadro de parcelas aparece quando o preço da bomba está indicado no comparador).

## 5b. Golpe de aríete (estimativa preliminar)

- Caso analisado: paragem brusca das bombas por falha de energia, na conduta de compressão.
- Celeridade: a = √[(K/ρ) / (1 + (K/E)·(D/e))], com K = 2,2 GPa e E de curta duração por material (PE100 1,1; PVC 3,0; FFD 170; aço 210; betão 30 GPa).
- Tempo de paragem pela fórmula de Mendiluce: T = C + K·L·v/(g·H<sub>m</sub>).
- Sobrepressão: Joukowsky ΔH = a·v/g se T ≤ 2L/a; Michaud ΔH = 2·L·v/(g·T) se T > 2L/a.
- p<sub>máx</sub> e p<sub>mín</sub> junto à bomba = p₀ ± ΔH, calculados no ponto de projeto e em cada cenário de nível (fica o pior caso).
- Verificações (aviso, não excluem a bomba): p<sub>máx</sub> ≤ PN da conduta; p<sub>mín</sub> ≥ 0.
- Proteção sugerida: só retenção de fecho rápido + ventosas; reservatório hidropneumático/chaminé com depressão; reservatório, antecipadora de onda ou subir PN com sobrepressão; volante de inércia quando a paragem é rápida; rampas de variador para paragens comandadas.
- Memória de cálculo: secção "Golpe de aríete (estimativa preliminar)" com as fórmulas, o quadro por cenário e a proteção recomendada.
- Exemplo (PEAD DE160, e = 9,5 mm, 1,2 km): a = 268 m/s, ΔH ≈ 36 m, p<sub>máx</sub> 76 m < PN10 (102 m), p<sub>mín</sub> 3,7 m → sem proteção especial. A mesma conduta em aço com e = 5 mm daria a = 1305 m/s e p<sub>mín</sub> = −7,5 m → reservatório hidropneumático.

## 5c. Poço de bombagem e submergência

- Secção "Poço de bombagem e submergência" no painel esquerdo: comando por níveis, arranques máx./hora (vazio = indicativo pela potência do motor: ≤ 4 kW 20; ≤ 11 kW 15; ≤ 37 kW 12; ≤ 110 kW 10; ≤ 250 kW 8; acima 6), área útil em planta, cota da boca de aspiração, Ø da boca/campânula (vazio = Ø da aspiração) e cota do fundo.
- Caudal usado: o maior caudal por bomba na envolvente de níveis.
- Volume útil V = Q/(4·Z); com funcionamento alternado os arranques repartem-se por N<sub>serviço</sub> + N<sub>reserva</sub> bombas (V = Q/(4·Z·n)). Com a área dá a diferença Δh entre paragem e arranque (aviso se < 0,30 m).
- Submergência mínima ANSI/HI 9.8: S = D·(1 + 2,3·F<sub>D</sub>), F<sub>D</sub> = v/√(g·D); disponível = nível mínimo de aspiração − cota da boca. Indica o nível mínimo de paragem (boca + S).
- Verificações (aviso): submergência, velocidade na boca ≤ 2,7 m/s (ideal ≈ 1,7) e folga ao fundo entre 0,3 D e 0,5 D.
- Memória de cálculo: secção "Poço de bombagem e submergência".
- Exemplo: 74 m³/h por bomba, motor 15 kW → Z = 12, 2 bombas alternadas → V ≥ 0,78 m³ (Δh = 0,31 m com 2,5 m²); D = 154 mm → S = 0,47 m, disponível 1,00 m.
- Projetos guardados antes da v7 abrem com esta secção desligada.

## 6. Memória de cálculo

Documento para a bomba A ou B, com:
- dados de base;
- perdas de carga, com fórmulas e quadro;
- curva do sistema;
- curva da bomba;
- ponto de funcionamento, com gráfico;
- potência e motor;
- NPSH, com gráfico;
- energia;
- resumo das verificações;
- referências (EN ISO 9906, ANSI/HI 9.6.1 e 9.6.3, IEC 60034-30-1, Azevedo Netto).

Exportação (memória de cálculo e memória justificativa):
- "Copiar para Word": copia em HTML, com os gráficos como imagem;
- "Descarregar .docx": documento Word nativo (estilos de título, tabelas, equações e gráficos em PNG), A4;
- "Descarregar PDF": A4 com quebras de página entre secções e linhas de tabela e rodapé com paginação.

## 7. Catálogo: importar catálogos e fichas (v12)

- No topo da aba Catálogo, a zona **Importar catálogo em PDF** (clicar ou arrastar um ou mais ficheiros) e a lista **Catálogos carregados**, com "digitalizar" e "remover" em cada um e "remover todos".
- Sem nada carregado não há bombas: a Seleção mostra "Ainda não há bombas" com ligação para a aba Catálogo, e as restantes abas pedem para escolher uma bomba.
- Leitura automática: todas as páginas do PDF são lidas e cada tabela Q–H em texto dá uma curva por linha de H (com η, NPSHr ou P quando a tabela os tem; conversão de l/min, l/s e gpm; velocidade lida da página). A designação do modelo vem do início da linha (ex.: "KPM 50", "CS 50-200 C") ou do título acima da tabela. Teste: Speroni 2020 (306 pág.) dá 512 curvas em cerca de 3 s.
- PDF sem tabelas em texto (curvas desenhadas, como Grundfos e KSB) ou digitalizado: "digitalizar" abre o PDF para marcar a curva com cliques (calibrar o eixo Q, o eixo de cada curva H, η, NPSHr ou P, e marcar os pontos); uma imagem largada na zona de importação abre diretamente na digitalização.
- **Ficha própria**: introduzida à mão (Q, H, η, NPSHr) ou vinda da digitalização; aparece como "Fichas próprias" na lista.
- Cada catálogo carregado é uma família nos filtros da Seleção e do Catálogo. A memória de cálculo indica a fonte como "nome do ficheiro, pág. N".
- **Nada fica guardado:** os catálogos e as fichas valem só para a sessão; ao recarregar a página é preciso importá-los de novo. O projeto (dados do sistema, pesos, preços) continua guardado no navegador e no .json do projeto. Saiu a partilha de fichas pela base de dados do artefacto.

## 7b. Exportar para o EPANET (v14)

Painel **Exportar para EPANET** na aba Catálogo. Unidades de caudal: LPS, CMH, LPM, CMD e MLD (altura sempre em m). Três ficheiros:

| Ficheiro | Para quê | Como usar no EPANET |
|---|---|---|
| Rede pronta a correr (.inp) | Bomba A com as condutas, os níveis, os grupos em paralelo e série, a velocidade e a curva de rendimento do sistema definido | File > Open e Run |
| Curvas para o Curve Editor (.crv, em .zip) | Bombas escolhidas (A a E) ou todas as da tabela, numa rede que já existe | Data > Curves > Add, botão Load, um ficheiro de cada vez |
| Secção [CURVES] (.inp) | As mesmas bombas, de uma só vez | Colar a secção no .inp da rede e voltar a abri-lo |

- File > Import > Network **substitui** a rede, não junta curvas (confirmado no código do EPANET); por isso há as opções .crv e [CURVES].
- A rede tem de usar a mesma unidade de caudal do ficheiro exportado.
- O EPANET recusa curvas em que H não desce sempre (Error 227). O troço à esquerda do pico sobe até ao pico e a app indica quantas curvas mudaram e em quantos metros. O resto da curva não muda.
- Abaixo do primeiro ponto (curvas sem Q = 0) e acima do último, o EPANET extrapola. A app avisa das curvas sem Q = 0.
- Uma curva com 3 pontos que comece em Q = 0 é ajustada pelo EPANET a uma função de potência.
- O NPSH não é exportado: o EPANET não o usa. O rendimento estimado (Gülich) fica assinalado no comentário da curva.
- A rede usa os níveis do caso de projeto (aspiração mínima, descarga máxima); as bombas de reserva não entram.
- IDs: H_modelo e E_modelo, até 31 carateres, sem espaços nem acentos (Ø passa a D).

Validação no motor EPANET 2.2 (via WNTR), com uma ficha de teste com pico:

| Caso | Seletor | EPANET |
|---|---|---|
| Darcy-Weisbach, LPS | 17,65 l/s · 41,82 m | 17,66 l/s · 41,80 m |
| Darcy-Weisbach, CMH | 63,53 m³/h | 63,59 m³/h |
| Hazen-Williams | 16,99 l/s · 42,61 m | 16,99 l/s · 42,61 m |
| 2 em paralelo | 10,92 l/s por bomba · 46,38 m | 10,94 l/s · 46,38 m |
| Velocidade 90 % | 11,95 l/s · 36,81 m | 11,96 l/s · 36,80 m |

As 513 curvas H e as 513 curvas de rendimento do teste (Speroni e ficha) foram aceites pelo motor, em LPS e CMH. O carregamento do .crv segue o código do Curve Editor, mas não foi testado na interface do EPANET.

## 7a. Rendimento estimado (bombas sem curva η)

- η<sub>opt</sub> pela correlação de Gülich (*Centrifugal Pumps*, eq. 3.28) em função de n<sub>q</sub> e Q; para multicelulares usa n<sub>q</sub> por andar (número de andares lido do modelo, p. ex. "RXM 4-6").
- Fator por tipo de rotor: centrífuga radial 0,92 (calibrado nas Etanorm da base de dados: estimativa com mediana 4 pontos abaixo do η real no BEP); multicelular 0,90; autoferrante 0,80; rotor aberto / águas residuais 0,75; vórtice 0,60; jato e periférica 0,50; volumétricas ficam com η fixo.
- Q<sub>BEP</sub> admitido a 70 % do caudal máximo da curva; forma η(Q) = η<sub>opt</sub>·(2x − x²).
- O BEP estimado não gera aviso de zona preferencial (fica "a confirmar"). A memória de cálculo mostra n<sub>q</sub>, η<sub>opt</sub> e o fator usados.
- O motor do catálogo Speroni não serve de limite ao η: é dimensionado com fator de serviço, abaixo da potência no fim da curva.

## 8. Limitações atuais

- Speroni: o catálogo não tem curvas de η nem de NPSHr (confirmado por pesquisa no PDF: só aparece o rendimento dos motores). O η é estimado (Gülich) e o NPSH fica "a confirmar".
- CR: os dados são de 60 Hz e a conversão para 50 Hz é aproximada.
- Rotor aparado: verificado nos dados KSB/HS (736 pares de diâmetros consecutivos) que a perda de η por aparo já está nas curvas do catálogo — mediana de 1,1 pts para aparos até 5 %, 1,6 pts para 5–10 %, 2,9 pts para 10–15 %, 3,9 pts para 15–25 % e 5,8 pts acima. É muito mais do que o efeito de escala de Moody (n ≈ 0,1–0,25; os dados dão n mediano ≈ 0,9), por isso não se aplica penalização adicional. A diferença entre a forma de Moody e a interpolação linear anterior é de 0,01 pts em mediana (máx. 0,4). Não se propõem aparos abaixo do menor diâmetro do catálogo.
- A leitura automática de PDF analisa só as primeiras 40 páginas.
- As definições do projeto ficam só no navegador; as fichas podem ser partilhadas.
- A partilha e a descarga de ficheiros só funcionam com o artefacto aberto em claude.ai (sessão iniciada); fora daí os botões avisam que não estão disponíveis.
- O PDF é rasterizado (texto não selecionável); para editar use o .docx.
- O golpe de aríete é uma estimativa junto à bomba: não considera o perfil da conduta (pontos altos), a inércia real do grupo nem o volume do reservatório hidropneumático.
- O poço de bombagem verifica o volume e a submergência; não verifica a geometria completa da HI 9.8 (distâncias às paredes e entre bombas, defletores, velocidade de aproximação).
- O custo de ciclo de vida não inclui o custo de paragem (indisponibilidade) nem a eliminação/desmantelamento.

## 9. Próximos passos propostos

### Prioridade alta
1. ~~Completar os dados Speroni (η e NPSHr)~~ — o catálogo não contém essas curvas. Feito em alternativa: η estimado por Gülich. Para NPSHr real é preciso a documentação técnica por série (pedir à Speroni) e carregá-la como ficha.
2. Adicionar o catálogo CR a 50 Hz (para substituir a conversão a partir dos 60 Hz). **Pendente:** o `Grundfos_CR_CRI_CRN.pdf` recebido é uma edição antiga (c. 2001–2003, só CR 1 a CR 90, com marca de água de revendedor); aguarda-se o data booklet atual CR/CRI/CRN 50 Hz. Os scripts de `extracao/` servem de base.
3. ~~Exportar a memória de cálculo e a justificativa para .docx ou PDF.~~ Feito (v3).
4. ~~Partilhar as fichas próprias através de uma base de dados do artefacto.~~ Feito (v3); retirado na v12 (catálogos importados por sessão).

### Prioridade média
5. ~~Cenários de nível (mínimo e máximo do reservatório) e curvas do sistema extremas.~~ Feito (v4).
6. ~~Bombas de reserva e funcionamento alternado, incluindo o custo no ciclo de vida.~~ Feito (v5).
7. ~~Golpe de aríete preliminar (Joukowsky e tempo de paragem) e indicação de proteção.~~ Feito (v6). Possível extensão: perfil da conduta e pré-dimensionamento do reservatório hidropneumático.
8. ~~Volume do poço de bombagem (arranques por hora) e submergência mínima (HI 9.8).~~ Feito (v7).
9. ~~Correção do rendimento do rotor aparado (por exemplo, a fórmula de Moody).~~ Feito (v8), com expoente calibrado nos dados do catálogo.

### Melhorias de uso
10. ~~Comparar mais de duas bombas (3 a 5).~~ Feito (v9).
11. Guardar projetos com nome (vários pontos de projeto).
12. Digitalização mais rápida, com deteção automática da curva por cor ou espessura.
13. Mais catálogos: ~~Grundfos NB/NK e bombas submersíveis de furo (Grundfos SP)~~ feitos (v10); desde a v12 os catálogos são importados pelo utilizador. Só os PDF com tabelas Q–H em texto são lidos automaticamente; para catálogos com curvas desenhadas, ver o ponto 12.
14. Catálogo de betão (tubos de pressão com alma de aço) para substituir os valores indicativos.
