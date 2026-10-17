"""CLI do container-scanner-imagens."""

from __future__ import annotations

import sys
from typing import Optional

from .scanner import DockerScanner, VulnReport


def _format_report(report: VulnReport) -> str:
    linhas = [
        f"Imagem: {report.image.short_id} ({report.image.image_id})",
    ]
    if report.image.tags:
        linhas.append(f"  Tags: {', '.join(report.image.tags)}")
    if not report.has_findings:
        linhas.append("  Nenhum achado de vulnerabilidade.")
    else:
        for f in report.findings:
            linhas.append(f"  [{f.severity}] {f.title}: {f.description}")
    return "\n".join(linhas)


def main(argv: Optional[list[str]] = None) -> int:
    """Executa o scan de todas as imagens locais e imprime os relatórios."""
    scanner = DockerScanner()
    reports = scanner.scan_all()
    if not reports:
        print("Nenhuma imagem Docker local encontrada.")
        return 0
    for report in reports:
        print(_format_report(report))
        print("-" * 40)
    return 0


if __name__ == "__main__":
    sys.exit(main())
