"""Testes do container-scanner-imagens (mocks, sem Docker real)."""

from __future__ import annotations

from unittest import mock

from container_scanner_imagens.scanner import (
    DockerScanner,
    Finding,
    ImageInfo,
    VulnReport,
    _import_docker,
)


class _FakeImage:
    def __init__(self, attrs: dict) -> None:
        self.attrs = attrs
        # short_id do Docker SDK: remove o prefixo "sha256:" e corta a 12 chars.
        self.short_id = attrs.get("Id", "").replace("sha256:", "")[:12]


class _FakeImages:
    def __init__(self, attrs_lista: list[dict]) -> None:
        self.itens = [_FakeImage(a) for a in attrs_lista]

    def list(self) -> list[_FakeImage]:
        return self.itens


class _FakeClient:
    def __init__(self, attrs_lista: list[dict]) -> None:
        self.images = _FakeImages(attrs_lista)


def _attrs(
    image_id: str = "sha256:aaa",
    tags=None,
    digests=None,
    size: int = 100,
    created: str = "2024-01-01T00:00:00Z",
) -> dict:
    return {
        "Id": image_id,
        "RepoTags": list(tags) if tags is not None else ["nginx:latest"],
        "RepoDigests": list(digests) if digests is not None else ["nginx@sha256:digest"],
        "Size": size,
        "Created": created,
        "Config": {"Labels": {}},
    }


# --- scan_image -----------------------------------------------------------

def test_scan_image_tag_latest_gera_achado_media() -> None:
    imagem = ImageInfo(
        image_id="sha256:abc123",
        short_id="abc123",
        tags=("nginx:latest",),
        digests=("sha256:digest",),
        size=100,
    )
    scanner = DockerScanner()
    report = scanner.scan_image(imagem)
    assert report.has_findings
    titulos = [f.title for f in report.findings]
    assert "Tag 'latest' detectada" in titulos
    medios = [f for f in report.findings if f.severity == "media"]
    assert len(medios) == 1


def test_scan_image_sem_tag_gera_achado_baixa() -> None:
    imagem = ImageInfo(image_id="sha256:x", short_id="x", tags=(), digests=(), size=50)
    scanner = DockerScanner()
    report = scanner.scan_image(imagem)
    assert any("sem tag" in f.title.lower() for f in report.findings)
    assert all(f.severity == "baixa" for f in report.findings if "tag" in f.title.lower())


def test_scan_image_sem_digests_gera_achado_baixa() -> None:
    imagem = ImageInfo(
        image_id="sha256:y", short_id="y", tags=("app:1.0",), digests=(), size=50
    )
    scanner = DockerScanner()
    report = scanner.scan_image(imagem)
    assert any(
        f.severity == "baixa" and "digest" in f.title.lower()
        for f in report.findings
    )


def test_scan_image_tamanho_invalido_gera_achado_baixa() -> None:
    imagem = ImageInfo(image_id="sha256:z", short_id="z", tags=("app:1.0",), digests=("d",), size=0)
    scanner = DockerScanner()
    report = scanner.scan_image(imagem)
    assert any("tamanho" in f.title.lower() for f in report.findings)


def test_scan_image_limpo_sem_achados() -> None:
    imagem = ImageInfo(
        image_id="sha256:z", short_id="z", tags=("app:1.2.3",), digests=("sha256:d",), size=100
    )
    scanner = DockerScanner()
    report = scanner.scan_image(imagem)
    assert not report.has_findings
    assert report.score == 0


def test_score_soma_pesos_dos_achados() -> None:
    imagem = ImageInfo(image_id="i", short_id="i", tags=("x:latest",), digests=(), size=0)
    scanner = DockerScanner()
    report = scanner.scan_image(imagem)
    # media (latest) = 5 + baixa (sem digest) = 1 + baixa (tamanho invalido) = 1
    assert report.score == 7


def test_finding_tem_severidade_titulo_e_descricao() -> None:
    f = Finding(severity="alta", title="T", description="D")
    assert f.severity == "alta"
    assert f.title == "T"
    assert f.description == "D"


# --- list_images (SDK com mock) ------------------------------------------

def test_list_images_sdk_mock_retorna_metadados() -> None:
    attrs_lista = [_attrs(image_id="sha256:aaa", tags=["nginx:latest"], size=100)]
    scanner = DockerScanner(client=_FakeClient(attrs_lista))
    imagens = scanner.list_images()
    assert len(imagens) == 1
    assert imagens[0].image_id == "sha256:aaa"
    assert imagens[0].short_id == "aaa"
    assert imagens[0].tags == ("nginx:latest",)
    assert imagens[0].digests == ("nginx@sha256:digest",)
    assert imagens[0].size == 100
    assert imagens[0].created == "2024-01-01T00:00:00Z"


def test_list_images_sdk_multiplas_imagens() -> None:
    attrs_lista = [
        _attrs(image_id="sha256:aaa", tags=["a:1"]),
        _attrs(image_id="sha256:bbb", tags=["b:2"], size=200),
    ]
    scanner = DockerScanner(client=_FakeClient(attrs_lista))
    imagens = scanner.list_images()
    assert len(imagens) == 2
    assert [i.short_id for i in imagens] == ["aaa", "bbb"]


def test_list_images_sdk_vazio_retorna_lista_vazia() -> None:
    scanner = DockerScanner(client=_FakeClient([]))
    assert scanner.list_images() == []


# --- list_images (sem cliente e sem Docker) ------------------------------

def test_list_images_sem_docker_retorna_lista_vazia() -> None:
    with mock.patch(
        "container_scanner_imagens.scanner._import_docker", return_value=None
    ), mock.patch(
        "container_scanner_imagens.scanner.subprocess.run",
        side_effect=FileNotFoundError("docker nao instalado"),
    ):
        scanner = DockerScanner()
        assert scanner.list_images() == []


# --- scan_all -------------------------------------------------------------

def test_scan_all_retorna_um_relatorio_por_imagem() -> None:
    attrs_lista = [
        _attrs(image_id="sha256:aaa", tags=["a:latest"], size=100),
        _attrs(image_id="sha256:bbb", tags=["b:1.0"], digests=("d",), size=200),
    ]
    scanner = DockerScanner(client=_FakeClient(attrs_lista))
    relatorios = scanner.scan_all()
    assert len(relatorios) == 2
    assert all(isinstance(r, VulnReport) for r in relatorios)
    # primeira tem tag latest -> achado; segunda limpa -> sem achados
    assert relatorios[0].has_findings
    assert not relatorios[1].has_findings


# --- VulnReport -----------------------------------------------------------

def test_vulnreport_expoe_imagem_e_achados() -> None:
    imagem = ImageInfo(image_id="i", short_id="i", tags=("t:1",), digests=("d",), size=10)
    report = VulnReport(image=imagem, findings=())
    assert report.image is imagem
    assert report.findings == ()
    assert not report.has_findings
