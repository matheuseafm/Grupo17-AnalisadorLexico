from __future__ import annotations

from pathlib import Path


def ler_arquivo(nome_arquivo: str) -> list[str]:
    caminho = Path(nome_arquivo)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {nome_arquivo}")
    if not caminho.is_file():
        raise IsADirectoryError(f"Caminho nao e arquivo: {nome_arquivo}")

    return caminho.read_text(encoding="utf-8").splitlines()


def escrever_arquivo(nome_arquivo: str, conteudo: str) -> None:
    caminho = Path(nome_arquivo)
    caminho.write_text(conteudo, encoding="utf-8")

