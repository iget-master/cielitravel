# Design System — cielitravel.com

> Levantado por inspeção direta do site em produção (WordPress + Elementor,
> tema Hello Elementor) em agosto/2026. Este documento é a referência de
> fidelidade visual para a reconstrução do site em páginas estáticas.

## 1. Identidade

- **Marca:** Cieli (Cieli Travel / "Cieli di Toscana") — agência ítalo-brasileira
  de viagens de luxo sob medida (Itália e França).
- **Logo:** manuscrito/caligráfico "Cieli" em creme sobre fundos escuros.
  Arquivo original: `uploads/2026/02/Logo_Cieli.svg`.
- **Tom visual:** editorial de revista de viagem de luxo. Fotografia grande e
  cinematográfica, vídeos de fundo, cores sólidas ousadas em blocos, serifa
  elegante + condensada gótica em caixa alta. Muito espaço em branco (creme).

## 2. Paleta de cores

Cores globais do kit Elementor (nomes originais):

| Token | Hex | Uso |
|---|---|---|
| **Primary / Accent / Text** | `#140059` | Azul-marinho profundo. Cor de texto padrão, títulos em fundo claro, fundos do rodapé/newsletter/CTA, barra de imprensa, card do roteiro dia-a-dia, barra-âncora sticky |
| **Secondary** | `#F2EEE2` | Creme. Fundo padrão do site (`body`), texto sobre fundos escuros |
| Amarelo | `#F8D939` | Painel "Curadoria" (especialidades), acentos |
| Laranja-vermelho | `#FA401A` | Painel "Sob Medida", etiquetas de destino nos depoimentos, ornamento "mancha de tinta", detalhes de destaque |
| Rosa | `#FFBAD6` | Painel "Hospitalidade" (especialidades) |
| Verde | `#52A061` | Faixa de fatos das páginas de destino (melhor período/duração/preço) |
| Preto | `#000000` | Fundo de seções com vídeo/foto (fallback), seção de depoimentos da home |
| Branco | `#FFFFFF` | Cursor do efeito typewriter, logos de imprensa |

Regra geral: **creme sobre navy** e **navy sobre creme**. As cores vivas
(amarelo/rosa/vermelho/verde) aparecem em blocos sólidos de seção inteira ou
detalhes pequenos — nunca em texto corrido.

## 3. Tipografia

Duas famílias (Adobe Fonts/Typekit + fonte própria):

### Sfizia (serifa display — corpo e títulos "editoriais")
- Papel: texto corrido, títulos serifados grandes (estilo revista), navegação
  do menu overlay, dropdowns do buscador.
- **Body:** 18px / line-height 27px / weight 400 / cor `#140059`.
- **Título display (H3/hero de seção):** 40–64px / weight 100–400 / uppercase
  (ex.: "ENCONTRE A VIAGEM IDEAL", "VIAJE MAIS ALÉM", "CURADORIA" ~64px w300).
- Variante itálica usada para palavras estrangeiras (*appassionati*, *nonna*).
- Estilos menores (labels): 12–14px, letter-spacing 1.5px, uppercase;
  18px w200 sublinhado para links "SAIBA +".

### Trade Gothic Next Compressed (sans condensada — títulos "gritados" e UI)
- Papel: H1/H2, botões, etiquetas, menus-âncora, rodapé (títulos de coluna).
- **H1:** 70px / w700 / letter-spacing 2.3px / uppercase.
- **H2 (título de seção):** 40px / w600 / ls 1px / uppercase
  (variação menor: 25–30px / w500–600 / ls 1.3px).
- **Botões:** 20px / w600 / ls 1–2px / uppercase.
- Famílias carregadas no site: trade-gothic-next, -compressed, -condensed,
  tgn-soft-round (pouco uso aparente).

> ⚠️ **Licenciamento:** Trade Gothic Next vem do Adobe Fonts (kit Typekit) e a
> Sfizia é fonte comercial (webfont própria). Para o site estático: manter o
> kit Adobe Fonts (exige conta ativa) e servir a Sfizia self-hosted (woff2 já
> usado hoje), OU substituir por pares visualmente próximos (ex.: serifa
> display + sans condensada bold) — decisão do dono do site.

## 4. Componentes recorrentes

### Header (fixo, transparente sobre o hero)
- Logo à esquerda (~115px de largura).
- Nav central: `DESTINOS` e `EXPERIÊNCIAS` (Trade Gothic, creme, uppercase)
  — ambos abrem **mega-dropdowns**:
  - DESTINOS → 2 cards grandes com foto: ITÁLIA (`bg-itaila-1.webp`) e FRANÇA (`bg-franca-1.webp`).
  - EXPERIÊNCIAS → tabs `COM QUEM` / `QUANDO` / `TIPO DE VIAGEM` com cards
    fotográficos (casal/solo/grupo/família; estações com meses; 11 tipos).
- Botão outline "PLANEJE SUA VIAGEM" (borda creme 1px, texto creme,
  uppercase) → `/contato/`.
- Ícone hambúrguer à direita → overlay de navegação em tela cheia
  (fundo navy, links em Sfizia ~50px creme).
- Em fundo claro o header fica navy sobre creme (mesma estrutura).

### Botões
- **Outline:** borda 1px na cor do texto (creme sobre escuro, navy sobre claro),
  fundo transparente, padding generoso, Trade Gothic 20px w600 uppercase.
- Links de texto: "SAIBA +" (Sfizia, sublinhado), setas de carrossel `<` `>`.

### Ornamento "mancha de tinta"
Pequena forma oval orgânica (pincelada vertical) usada como divisor sob
títulos. Laranja `#FA401A` sobre claro, navy sobre amarelo. Marca registrada
visual do site.

### Cards de destino/roteiro (carrossel "swiper")
- Foto com gradiente escuro na base, título Sfizia uppercase creme,
  resumo de 1 linha, link "SAIBA +". 3 cards por viewport no desktop.
- Carrosséis em loop (os itens se repetem — cuidado ao migrar).

### Ticker "DESTINOS INFINITOS"
Faixa horizontal em rolagem contínua com cards de cidades: etiqueta
"DESTINOS ∞ INFINITOS", nome da cidade e 1 linha de descrição.

### Depoimentos
- Home: seção full-bleed com foto escura, etiqueta do destino em laranja
  (Trade Gothic), citação gigante em Sfizia creme entre aspas, autor em
  versalete, logo Google + 5 estrelas.
- Páginas internas: carrossel com 3 colunas (LOCAL, ANO / texto / — AUTOR).

### Acordeões (FAQ e rodapé mobile)
Numeração `01`, `02`… (Trade Gothic), pergunta em versalete Sfizia,
ícone `+` à direita, linha divisória fina navy.

### Formulários (WPForms hoje)
- Campos com borda fina navy sobre creme, labels uppercase letterspaced.
- Dropdowns do buscador: outline navy, chevron, uppercase.
- Newsletter: campo Email + botão ASSINAR (sobre navy).
- Contato: 2 blocos ("Sobre a sua viagem", "Sobre você") — ver `content/contato.md`
  para todos os campos e opções; telefone com bandeira de país (intl-tel-input);
  checkboxes de política de privacidade/LGPD.

## 5. Estruturas de página (templates)

### 5.1 Home (`/`) — ver `content/home.md`
1. Hero vídeo full-bleed + "CONHEÇA O INFINITO DE" + destinos rotativos.
2. "Paixão profunda" — foto + manifesto (creme).
3. Carrossel de viagens (14 cards).
4. **Seção pinada com vídeo aéreo** (conversível vermelho): 3 mensagens que se
   trocam com o scroll (Viaje mais além / Conte o tempo… / Desvende…).
5. Buscador "Encontre a viagem ideal" — card creme de cantos superiores
   arredondados sobre foto, 3 dropdowns + ENCONTRAR → `/destinos/`.
6. Depoimentos full-bleed (foto escura).
7. Barra de imprensa (navy): Folha, Viagem, Consuelo Blocker (assinatura),
   Roteiros Incríveis, Valor Econômico.
8. **Especialidades — carrossel horizontal pinado** de 3 painéis de cor sólida
   (amarelo Curadoria / rosa Hospitalidade / vermelho Sob Medida), cada um com
   metade em foto.
9. CTA full-bleed (Ponte Rialto) + botão outline.
10. FAQ (acordeão numerado).
11. Newsletter + rodapé (navy).

### 5.2 País (`/italia/`, `/franca/`) — ver `content/italia.md` / `franca.md`
Hero vídeo + subtítulo letterspaced → menu-âncora → intro → citação typewriter
(Verdi / De Gaulle) → carrossel de roteiros → depoimentos → tabs "Que viagem
você quer viver?" → ticker de cidades → diferenciais (5) → galeria "Nossas
histórias favoritas" → serviços (8) → "3 passos" → CTA → FAQ (só na França) →
rodapé.

### 5.3 Destino (`/toscana/`, `/sicilia/`, `/paris/`, `/verao-na-italia/`, etc.)
1. Hero vídeo com **headline typewriter** ("viagem pela Toscana com roteiro sob
   medida") + cursor `|` piscando.
2. **Barra-âncora sticky navy:** Roteiro · Cidades · Depoimentos · Serviços ·
   Diferenciais · Experiências · Galeria · Hospedagens · FAQ.
3. **Faixa de fatos verde `#52A061`:** subtítulo com as cidades + 3 colunas
   (Melhor período / Duração ideal / Preço a partir de) + disclaimer.
4. **Roteiro dia a dia:** card navy com carrossel (foto à esquerda; DIA n,
   título Trade Gothic, texto Sfizia à direita; setas) + CTA "Transforme essa
   viagem na sua".
5. Descrição editorial do destino + citação typewriter (autor varia:
   E.M. Forster na Toscana, etc.).
6. Ticker de cidades, depoimentos, serviços, diferenciais.
7. "Experiências de luxo em/na X" — grid/carrossel de itens (título + linha).
8. Galeria "Nossas histórias favoritas".
9. "Hospedagens de luxo com selo Cieli" — carrossel de hotéis (NOME + cidade).
10. CTA + **FAQ específico do destino** + rodapé.

### 5.4 Institucionais
- **Quem somos:** hero + citação do fundador + história (3 blocos) + equipe
  (CTA) + números (140 cidades / 1500 viajantes / 500 viagens) + manifesto em
  vídeo + galeria + blog em destaque.
- **Contato:** hero + formulário grande em 2 etapas + depoimentos.
- **Equipe / Imprensa / Trabalhe conosco / FAQ:** páginas simples de conteúdo.
- **Destinos (`/destinos/`):** filtro por país/tipo/estação/companhia
  (JetSmartFilters) + grid de cards + "Carregar mais".

### 5.5 Blog
- Listagem `/blog/` + posts individuais (artigo com H2/H3, imagens, CTAs
  intermediários "PLANEJE SUA VIAGEM" e blocos de posts relacionados).

## 6. Rodapé (navy `#140059`, texto creme)

1. Newsletter (título + campo + ASSINAR).
2. Colunas: MENU (8 links) · DESTINOS (França, Itália) · COM QUEM (4) ·
   QUANDO (4) · TIPO DE VIAGEM (11) — no desktop abertas, no mobile acordeão
   com `+`.
3. "CONECTE-SE:" ícones — Instagram (`/cielitravel/`), LinkedIn
   (`/company/cieli-di-toscana`), terceira rede, Google Reviews.
4. Link "POLÍTICA DE PRIVACIDADE".

## 7. Animações e interações

- **Typewriter:** headlines de destino e citações (script próprio
  "cieli-typing-text", cursor `|` piscando, dispara ao entrar na viewport,
  ~60ms/caractere).
- **Headline rotativa** no hero da home (troca de destinos).
- **Seções pinadas com scroll:** vídeo "Nosso jeito" (3 mensagens) e
  especialidades (3 painéis horizontais). *Custo alto de performance — no site
  estático, considerar versões mais leves (scroll-snap/CSS sticky).*
- Carrosséis Swiper em quase toda seção (loop infinito).
- Fade-in dos blocos ao rolar (Elementor motion effects).
- Vídeos de fundo autoplay/muted/loop (hero home, países, destinos, "manifesto").

## 8. Breakpoints e layout

- Container padrão Elementor: conteúdo centrado, largura ~1140–1200px.
- Breakpoints usuais do Elementor: desktop >1024px, tablet 768–1024px,
  mobile <768px (rodapé vira acordeão; carrosséis mostram 1 card).
- Imagens em `.webp` (uploads organizados por ano/mês), vídeos `.mp4`.

## 9. Infra atual (para referência da migração)

- WordPress + **Elementor Pro** (tema Hello Elementor), **JetEngine**
  (CPTs: viagem, depoimento, diferencial, galeria, hospedagem, profissional,
  servico, valor, secao…) e **JetSmartFilters** (página /destinos/),
  **WPForms** (formulários + campo de telefone internacional),
  **Site Kit by Google**. Sitemap: `sitemap_index.xml` (Yoast-style).
- Os CPTs alimentam os carrosséis/tickers — no site estático esse conteúdo
  já está "assado" nos arquivos de `content/`.
- CDN bloqueia fetchers automatizados (User-Agent de bot); requisições com UA
  de navegador funcionam.
- Páginas utilitárias: `/obrigado/` (pós-formulário), `/formulario-b/`
  (variante de formulário), `/pagina-de-links/` (link-in-bio, montada via JS).

## 10. Assets

- Logo: `assets/uploads/2026/02/Logo_Cieli.svg`
- Imagens referenciadas nos conteúdos: `assets/uploads/<ano>/<mês>/<arquivo>`
  (baixadas por `scripts/download_uploads.py`).
- Vídeos de fundo **não** foram baixados (identificar URLs `.mp4` no HTML ao
  montar cada página, ou reexportar dos originais).
- Logos de imprensa: `logo-folha-1.webp`, `consuelo_logo.webp`,
  `roteiros_incr_veis_logo-2.webp`, `valor_econ_mico_logo.webp` (2026/07).
