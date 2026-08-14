---
name: build-site
description: Regerar o site estático (content/*.md → dist/). Use após editar conteúdo em content/, o CSS/JS em site/static/ ou o gerador scripts/build.py.
---

# Build do site

1. `py -3 scripts/build.py` (requer `py -3 -m pip install markdown`).
2. `dist/` é regenerado por completo (91+ páginas, uploads e static copiados).
3. Servidor local: `py -3 scripts/serve.py` (porta 8080, sem cache — só recarregar).
4. Publicação AWS: `infra/` (CloudFormation S3+CloudFront + script de deploy).

Formato dos content/*.md: espelho do site original — `content/sicilia.md` é a
referência do template de destino; posts em `content/blog/`. O parser está em
`scripts/build.py` (`parse_destino`, `render_post`, `render_page`).
