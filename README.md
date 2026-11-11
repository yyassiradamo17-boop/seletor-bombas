# Seletor de Bombas

Ferramenta para selecionar bombas hidráulicas a partir dos catálogos dos fabricantes. A partir dos dados do sistema, calcula a curva do sistema, cruza-a com cada bomba, verifica o NPSH e prepara a memória de cálculo e o comparativo entre bombas.

**Abrir a app online:** https://yyassiradamo17-boop.github.io/seletor-bombas/

## Como usar

Abra o endereço acima, ou descarregue `Seletor de Bombas.html` e abra-o num navegador (Chrome, Edge ou Firefox). É um só ficheiro, funciona sem internet e não precisa de instalação.

1. Defina o sistema no painel esquerdo: caudal, cotas, condutas (com catálogo de tubos PEAD, PVC-U, FFD, aço, PRFV e betão), poço e outros dados.
2. Na aba **Catálogo**, importe catálogos, fichas técnicas (ex.: KSB EasySelect) ou páginas de curvas em PDF. As tabelas Q–H e as curvas desenhadas em vetor (H, potência e NPSH por diâmetro do rotor) são lidas automaticamente; PDF digitalizados e imagens digitalizam-se com cliques. Também pode introduzir fichas próprias à mão.
3. Use as abas **Seleção**, **Ponto de funcionamento**, **Comparador** e **Memória de cálculo**. A memória exporta-se para .docx ou PDF.
4. Na aba **Catálogo**, use **Exportar para EPANET** para obter uma rede .inp pronta a correr, curvas .crv ou a secção [CURVES].

Os catálogos importados ficam só na sessão. O projeto pode guardar-se e abrir-se como ficheiro .json.

## Conteúdo

| Caminho | O que é |
|---|---|
| `Seletor de Bombas.html` | a app autónoma, com as bibliotecas e as fontes embutidas |
| `Seletor de bombas — funcionalidades e próximos passos.md` | descrição das funcionalidades, métodos de cálculo e próximos passos |
| `extracao/seletor-bombas.html` | a fonte da app (versão para claude.ai) |
| `extracao/standalone.py` | gera a app autónoma a partir da fonte (`python extracao/standalone.py` cria `extracao/Seletor de Bombas.html`, que depois se copia para a raiz) |
| `extracao/tubos.py`, `tubos.json` | catálogo de tubos usado nas condutas |
| `extracao/patch_fichas.*` | leitura das curvas desenhadas nas fichas técnicas, aplicada à fonte da app |
| `extracao/patch_epanet.*` | exportação para o EPANET, aplicada à fonte da app |
| `extracao/*.py` | scripts de extração de curvas e de alteração da app |
| `extracao/libs/`, `extracao/fonts/` | pdf.js, JSZip, html2canvas, jsPDF e as fontes IBM Plex e Barlow Condensed (licenças livres próprias) |

Os PDF dos fabricantes e a bibliografia não estão no repositório, porque têm direitos de autor.

## Aviso

Os resultados são de pré-dimensionamento. Confirme sempre a seleção final na documentação técnica do fabricante.
