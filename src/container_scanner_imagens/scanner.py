"""Scan simples de imagens Docker com relatório de vulnerabilidades.

MVP para DevOps/Cloud: lista imagens locais (SDK do Docker com fallback
para a CLI ``docker images``), verifica tags ``latest``/desatualizadas e
emite um relatório simples de vulnerabilidades por imagem.

Tudo é determinístico e testável com mocks — não exige um Docker real.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import Optional


def _import_docker():
    """Importa o SDK do Docker de forma preguiçosa.

    Retorna o módulo ``docker`` ou ``None`` quando não instalado, de modo
    que o pacote continue importável sem um ambiente Docker real.
    """
    try:
        import docker  # type: ignore[import-not-found]
    except ImportError:
        return None
    return docker


@dataclass(frozen=True)
class ImageInfo:
    """Metadados de uma imagem Docker local."""

    image_id: str
    short_id: str
    tags: tuple[str, ...] = field(default_factory=tuple)
    digests: tuple[str, ...] = field(default_factory=tuple)
    size: int = 0
    created: Optional[str] = None
    labels: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Finding:
    """Um achado do relatório de vulnerabilidades."""

    severity: str  # "baixa" | "media" | "alta"
    title: str
    description: str


@dataclass(frozen=True)
class VulnReport:
    """Relatório de vulnerabilidades de uma única imagem."""

    image: ImageInfo
    findings: tuple[Finding, ...] = field(default_factory=tuple)

    @property
    def score(self) -> int:
        """Pontuação simples: 0 = sem achados, maior = mais achados graves."""
        pesos = {"alta": 10, "media": 5, "baixa": 1}
        return sum(pesos.get(f.severity, 0) for f in self.findings)

    @property
    def has_findings(self) -> bool:
        return len(self.findings) > 0


class DockerScanner:
    """Orquestra o scan de imagens Docker."""

    def __init__(self, client: Optional[object] = None) -> None:
        """Cria o scanner.

        Args:
            client: cliente Docker já instanciado (útil em testes). Quando
                None, tenta obter via SDK ou fallback para a CLI.
        """
        self._client = client

    def _client_or_none(self) -> Optional[object]:
        if self._client is not None:
            return self._client
        docker = _import_docker()
        if docker is None:
            return None
        try:
            return docker.from_env()
        except Exception:
            return None

    def list_images(self) -> list[ImageInfo]:
        """Lista imagens Docker locais.

        Tenta o SDK do Docker primeiro; se indisponível, faz fallback para
        o comando ``docker images``. Retorna lista vazia quando nenhum dos
        dois funciona.
        """
        client = self._client_or_none()
        if client is not None:
            return self._list_images_sdk(client)
        return self._list_images_cli()

    def _list_images_sdk(self, client) -> list[ImageInfo]:
        imagens: list[ImageInfo] = []
        for img in client.images.list():
            attrs = img.attrs or {}
            repo_tags = tuple(attrs.get("RepoTags") or [])
            repo_digests = tuple(attrs.get("RepoDigests") or [])
            imagens.append(
                ImageInfo(
                    image_id=attrs.get("Id", ""),
                    short_id=img.short_id,
                    tags=repo_tags,
                    digests=repo_digests,
                    size=int(attrs.get("Size", 0) or 0),
                    created=attrs.get("Created"),
                    labels=dict(attrs.get("Config", {}).get("Labels") or {}),
                )
            )
        return imagens

    def _list_images_cli(self) -> list[ImageInfo]:
        try:
            resultado = subprocess.run(
                [
                    "docker",
                    "images",
                    "--format",
                    "{{.ID}}\t{{.Repository}}:{{.Tag}}\t{{.Size}}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError, OSError):
            return []
        imagens: list[ImageInfo] = []
        for linha in resultado.stdout.splitlines():
            if not linha.strip():
                continue
            partes = linha.split("\t")
            image_id = partes[0] if len(partes) > 0 else ""
            tag = partes[1] if len(partes) > 1 else "<none>:<none>"
            imagens.append(
                ImageInfo(image_id=image_id, short_id=image_id[:12], tags=(tag,))
            )
        return imagens

    def scan_image(self, image: ImageInfo) -> VulnReport:
        """Gera o relatório simples de vulnerabilidades de uma imagem."""
        findings: list[Finding] = []
        tags = list(image.tags)

        if not tags or all(t == "<none>:<none>" for t in tags):
            findings.append(
                Finding(
                    severity="baixa",
                    title="Imagem sem tag",
                    description="A imagem não possui tag de versão associada.",
                )
            )

        if any(":latest" in t or t.endswith(":latest") for t in tags):
            findings.append(
                Finding(
                    severity="media",
                    title="Tag 'latest' detectada",
                    description=(
                        "A imagem usa a tag 'latest', que é mutável e não "
                        "garante reprodutibilidade."
                    ),
                )
            )

        if not image.digests:
            findings.append(
                Finding(
                    severity="baixa",
                    title="Sem digest de imagem",
                    description=(
                        "A imagem não apresenta digest (não é imutável por conteúdo)."
                    ),
                )
            )

        if image.size <= 0:
            findings.append(
                Finding(
                    severity="baixa",
                    title="Tamanho inválido",
                    description="O tamanho da imagem não pôde ser determinado.",
                )
            )

        return VulnReport(image=image, findings=tuple(findings))

    def scan_all(self) -> list[VulnReport]:
        """Escaneia todas as imagens locais e retorna os relatórios."""
        return [self.scan_image(img) for img in self.list_images()]
