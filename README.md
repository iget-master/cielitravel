# cielitravel

Base para reconstruir **cielitravel.com** (hoje WordPress + Elementor) como
site estático — rápido e barato de hospedar.

| Onde | O quê |
|---|---|
| [`design.md`](design.md) | Design system levantado do site em produção: paleta, tipografia, componentes e os templates de página |
| [`content/`](content/) | Espelho do conteúdo: 31 páginas + 60 posts em Markdown com frontmatter (`title`, `url`, `description`) |
| [`assets/uploads/`](assets/) | 91 imagens originais, na mesma estrutura ano/mês do WordPress |
| [`CLAUDE.md`](CLAUDE.md) | Diretivas da migração e pendências em aberto |
| [`scripts/`](scripts/) | `build.py` (gera `dist/`), `serve.py` (preview local), `download_uploads.py` |
| [`site/static/`](site/static/) | CSS do design system + JS mínimo |
| [`infra/`](infra/) | CloudFormation (S3 + CloudFront) e `deploy.ps1` |

## Uso rápido

```bash
py -3 -m pip install markdown   # uma vez
py -3 scripts/build.py          # content/ -> dist/
py -3 scripts/serve.py          # http://localhost:8080 (e <hostname>.local:8080 no celular)
```

Publicação na AWS: `.\infra\deploy.ps1` (requer AWS CLI configurada).

Levantado em agosto/2026 a partir do site em produção.
