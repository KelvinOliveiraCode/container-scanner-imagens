# container-scanner-imagens

## Descrição

Scan simples de imagens Docker com relatório de vulnerabilidades (MVP). Lista as imagens Docker locais usando o SDK do Docker, com fallback para o comando `docker images` da CLI quando o SDK não está disponível. Para cada imagem, verifica itens determinísticos como tag `latest`, ausência de tag, ausência de digest e tamanho inválido, e emite um relatório simples com achados classificados por severidade.

Destinado a ambientes DevOps/Cloud. Os testes usam mocks, portanto não exigem um Docker real para rodar.

## Stack

- Python 3.9+
- docker SDK (opcional; quando ausente, o programa usa a CLI `docker images`)
- pytest (testes)

## Instalação

```bash
pip install -e .
```

## Uso

Execute o scanner sobre as imagens locais:

```bash
PYTHONPATH=src python -m container_scanner_imagens
```

O entry point `container-scanner` também fica disponível após a instalação.

Exemplo de saída sem imagens locais:

```
Nenhuma imagem Docker local encontrada.
```

Exemplo de saída com imagens:

```
Imagem: nginx (sha256:aaa123)
  Tags: nginx:latest
  [media] Tag 'latest' detectada: a imagem usa a tag 'latest', que é mutável e não garante reprodutibilidade.
----------------------------------------
```

## Relatório de vulnerabilidades

Para cada imagem, o relatório emite achados simples e determinísticos:

- imagem sem tag -> baixa
- tag `latest` -> media
- sem digest de imagem -> baixa
- tamanho inválido -> baixa

Pontuação por imagem: alta = 10, media = 5, baixa = 1. Uma imagem sem achados tem pontuação 0.

## Testes

Execute a suíte com pytest. Todos os testes usam mocks (injeção de dependência via parâmetro `client`); nenhum requer Docker real.

```bash
PYTHONPATH=src python -m pytest -q
```

Resultado: 13 testes aprovados.

## Licença

MIT

## Autor

Kelvin Oliveira
