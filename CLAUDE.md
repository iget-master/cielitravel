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

## Build, preview e deploy

- **Build:** `py -3 scripts/build.py` → gera `dist/` (91+ páginas).
  Requer `py -3 -m pip install markdown`. Comando do Claude: **`/build-site`**
  (neste repo) ou **`/build-cielitravel`** (no projeto leituras-acs).
- **Preview local:** `py -3 scripts/serve.py` → `http://localhost:8080` e, na
  rede local (celular), `http://desktop-esoares.local:8080` (mDNS) ou
  `http://<IP-da-máquina>:8080`. Precisa de regra de firewall liberando a
  porta 8080 (uma vez, como admin):
  `netsh advfirewall firewall add rule name="cielitravel-local-8080" dir=in action=allow protocol=TCP localport=8080`
- **AWS:** `infra/cloudformation.yml` (S3 privado + CloudFront com OAC +
  function de rewrite `/x/` → `/x/index.html`). Publicação:
  `.\infra\deploy.ps1` (deploy da stack + `aws s3 sync dist/` + invalidação).
  Requer AWS CLI configurada. Domínio próprio: ver comentários no template
  (ACM em us-east-1 + Aliases).

## Arquitetura do gerador (scripts/build.py)

- `content/*.md` (formato espelho) → parsers por template:
  `render_home` (bespoke, usa content/home.md editorial), `render_destino`
  (país e destinos — `parse_destino` lê fatos/roteiro DIA n/cidades/
  depoimentos/seções), `render_post` (blog), `render_page` (institucionais,
  com acordeão automático p/ FAQs), `render_contato` (formulário).
- `content/sicilia.md` é a referência do formato destino. Manter o formato ao
  editar; o índice do blog é gerado do frontmatter dos posts (blog.md ignorado).
- Shell comum (header + mega-dropdown + overlay + footer) em `header()`/
  `footer()`; estilos em `site/static/css/main.css` (tokens do design.md);
  JS mínimo em `site/static/js/main.js`.

## Scripts

- `scripts/build.py` — gera o site em `dist/`.
- `scripts/serve.py` — servidor local (porta 8080, sem cache).
- `scripts/download_uploads.py` — baixa para `assets/uploads/` as imagens
  referenciadas em `content/`.

## Estado / pendências

- [x] design.md, content/ (31 páginas + 61 posts), assets (91 imagens).
- [x] Gerador estático próprio (Python stdlib + pacote `markdown`).
- [x] Infra AWS (CloudFormation) + script de deploy — **stack ainda não criada**.
- [ ] Fontes: usando substitutas livres (EB Garamond ↔ Sfizia,
  Oswald ↔ Trade Gothic Next Compressed) — trocar em `--font-serif`/
  `--font-cond` no CSS se licenciar as originais.
- [ ] Vídeos de fundo não baixados; heros usam frames .webp estáticos.
- [ ] Formulários (contato/newsletter) sem backend — alertam "integração
  pendente"; escolher serviço (Formspree/Workers/etc.).
- [ ] /destinos/ renderiza como página simples (sem filtros interativos).
- [ ] Citações typewriter de franca/toscana sem o texto original (via JS no
  site antigo); `content/pagina-de-links.md` vazia (link-in-bio via JS).
