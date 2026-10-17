# container-scanner-imagens

## Descrição / Description

PT-BR: Scan simples de imagens Docker. Lista imagens locais (SDK do Docker com fallback para a CLI `docker images`), verifica tags `latest`/desatualizadas e gera um relatório simples de vulnerabilidades por imagem. MVP da área DevOps/Cloud. Os testes usam mocks, portanto não exigem Docker real.

EN: Simple Docker image scanner. Lists local images (Docker SDK with `docker images` CLI fallback), checks for `latest`/outdated tags, and produces a simple per-image vulnerability report. DevOps/Cloud MVP. Tests use mocks, so no real Docker is required.

## Stack

- Python 3.9+
- docker SDK (opcional; quando ausente, cai para a CLI `docker images`)
- pytest para testes

## Como usar / How to use

PT-BR:
```
pip install -e .
PYTHONPATH=src python -m container_scanner_imagens
```

EN:
```
pip install -e .
PYTHONPATH=src python -m container_scanner_imagens
```

Saída de exemplo (sem imagens locais):

PT-BR:
```
Nenhuma imagem Docker local encontrada.
```

EN:
```
No local Docker images found.
```

Saída de exemplo (com imagens):

PT-BR:
```
Imagem: nginx (sha256:aaa123)
  Tags: nginx:latest
  [media] Tag 'latest' detectada: a imagem usa a tag 'latest', que e mutavel e nao garante reprodutibilidade.
----------------------------------------
```

EN:
```
Image: nginx (sha256:aaa123)
  Tags: nginx:latest
  [medium] 'latest' tag detected: the image uses the 'latest' tag, which is mutable and does not guarantee reproducibility.
----------------------------------------
```

## Testes / Testes

PT-BR: Rode a suíte com pytest. Todos os testes usam mocks (injecao de dependencia via parametro `client`); nenhum requer Docker real.

EN: Run the suite with pytest. All tests use mocks (dependency injection via the `client` parameter); none require real Docker.

```
PYTHONPATH=src python -m pytest -q
```

Resultado esperado: todos os testes passam (13 passed).

## Relatório de vulnerabilidades / Vulnerability report

PT-BR: Para cada imagem, o relatorio emite achados simples e determinísticos:

- imagem sem tag -> baixa
- tag `latest` -> media
- sem digest de imagem -> baixa
- tamanho invalido -> baixa

Pontuação: alta = 10, media = 5, baixa = 1. Uma imagem sem achados tem pontuação 0.

EN: For each image, the report emits simple deterministic findings:

- image without tag -> low
- `latest` tag -> medium
- no image digest -> low
- invalid size -> low

Scoring: high = 10, medium = 5, low = 1. An image with no findings scores 0.

## Licença / License

MIT

## Autor / Author

Kelvin Oliveira
