# cielitravel — migração WordPress → site estático

## Objetivo

Substituir o site atual **cielitravel.com** (WordPress + Elementor, pesado e
cheio de plugins) por **páginas estáticas fiéis ao design atual**, fáceis e
baratas de hospedar (ex.: Cloudflare Pages, Netlify, GitHub Pages ou um bucket
+ CDN).

## Fontes da verdade (nesta ordem)

1. **`design.md`** — design system completo levantado do site em produção:
   paleta, tipografia, componentes, templates de página, animações. Toda página
   estática deve seguir este documento.
2. **`content/*.md`** — espelho do conteúdo do site (1 arquivo por página;
   posts em `content/blog/`). Frontmatter com `title`, `url`, `slug`,
   `description` (usar nas meta tags). O texto é o conteúdo real do site — não
   reescrever, não "melhorar" copy sem pedido explícito.
3. **`assets/uploads/`** — imagens originais do site (estrutura ano/mês igual à
   do WordPress). Referenciadas nos .md como `uploads/...`.
4. O site em produção (https://cielitravel.com) para conferência visual.

## Diretivas de construção

- **Fidelidade primeiro:** replicar o layout, cores (`#140059`, `#F2EEE2`,
  `#F8D939`, `#FA401A`, `#FFBAD6`, `#52A061`), tipografia (Sfizia +
  Trade Gothic Next Compressed) e estrutura de seções descritos no design.md.
- **HTML/CSS/JS vanilla ou gerador estático simples** (ex.: Eleventy/Astro).
  Sem WordPress, sem jQuery, sem page builder. JS mínimo: carrosséis,
  typewriter, acordeões, menu overlay — preferir CSS puro (scroll-snap,
  details/summary) quando o efeito permitir.
- **Performance é motivação da migração:** imagens lazy (`loading="lazy"`),
  `.webp`, vídeos só onde essenciais (poster + `preload="none"`), zero
  bibliotecas pesadas. Meta: Lighthouse 90+.
- **SEO:** preservar as URLs atuais (mesmos paths, ex.: `/toscana/`,
  `/blog/<slug>/`), `title` e `meta description` do frontmatter, sitemap.xml e
  redirects onde necessário.
- **Formulários:** o site estático não terá PHP. Contato/newsletter → serviço
  externo (Formspree, Basin, Cloudflare Workers ou similar) — decidir com o
  dono antes de implementar. Campos: ver `content/contato.md`.
- **Fontes:** Trade Gothic (Adobe Fonts) e Sfizia são licenciadas — confirmar
  com o dono se mantém o kit Adobe ou substitui (ver design.md §3).

## Acesso ao site em produção

- A CDN **bloqueia fetchers automatizados** (WebFetch etc.). Funciona:
  `curl`/scripts locais com User-Agent de navegador
  (`Mozilla/5.0 ... Chrome/139...`), ou o browser do usuário via extensão.
- Sitemap completo: `https://cielitravel.com/sitemap_index.xml`.

## Scripts

- `scripts/download_uploads.py` — baixa para `assets/uploads/` as imagens
  referenciadas em `content/`. (Espelho original feito com script equivalente
  de crawl das páginas do sitemap.)

## Estado / pendências

- [x] design.md, content/ (31 páginas + 61 posts), assets (91 imagens).
- [ ] Vídeos de fundo não baixados (URLs .mp4 a extrair por página).
- [ ] Citações "typewriter" carregadas via JS não capturadas em algumas
  páginas (marcadas nos .md; ex.: citação De Gaulle em franca.md e
  E.M. Forster em toscana.md — conferir no site).
- [ ] `content/pagina-de-links.md` vazia (página link-in-bio montada via JS).
- [ ] Escolher gerador estático + hospedagem; definir solução de formulários.
- [ ] Home/Itália/França/Toscana têm .md editorial detalhado (estrutura de
  seções); os demais destinos são espelho automático — mesma estrutura de
  template (design.md §5.3).
