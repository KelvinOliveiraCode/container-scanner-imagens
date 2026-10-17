# BRIEF — container-scanner-imagens

## Projeto
`container-scanner-imagens` — área DevOps/Cloud. Scan simples de imagens Docker com relatorio de vulnerabilidades (MVP).

## Stack
Python 3.9+, docker SDK (opcional, com fallback para a CLI `docker images`), pytest.

## Entregas (arquivos criados)
- `pyproject.toml` — metadados, dependencias e entry point `container-scanner`.
- `src/container_scanner_imagens/__init__.py` — pacote (versao 0.1.0).
- `src/container_scanner_imagens/scanner.py` — `DockerScanner`, `ImageInfo`, `Finding`, `VulnReport`. Lista imagens (SDK ou CLI `docker images`), verifica tags `latest`/desatualizadas e emite relatorio simples de vulnerabilidades por imagem. Deterministico e testavel com mocks.
- `src/container_scanner_imagens/__main__.py` — CLI (`python -m container_scanner_imagens`).
- `tests/test_scanner.py` — 13 testes com mocks (injecao de dependencia via `client`), nenhum exige Docker real.
- `README.md` — bilíngue PT-BR + EN completo (titulo, descricao, como usar, testes, licenca MIT, autor Kelvin Oliveira).
- `BRIEF.md` — este arquivo.

## Critérios de aceitação
- [x] Relatório de vulnerabilidades por imagem (tags `latest`, falta de digest, imagem sem tag, tamanho invalido).
- [x] Testes que passam (gate verify-and-stop).
- [x] README PT/EN completo.

## Como verificar

Comando de teste:
```
PYTHONPATH=src python -m pytest -q
```

Resultado dos testes: **13 passed** (pass/fail = pass).

Caminhos (base: `C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\container-scanner-imagens\`):
- README: `README.md`
- BRIEF: `BRIEF.md`
- Código fonte: `src/container_scanner_imagens/`
- Testes: `tests/test_scanner.py`

## Autor
Kelvin Oliveira — licença MIT.
