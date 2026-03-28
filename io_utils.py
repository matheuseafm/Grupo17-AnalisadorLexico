# Matheus Moreira - matheuseafm - Grupo 17
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


def salvar_tokens(
    nome_arquivo: str,
    tokens_por_linha: list[tuple[int, str, list]],
) -> None:
    """Salva os tokens gerados pelo analisador lexico em um arquivo de texto."""
    linhas: list[str] = []
    linhas.append("=" * 60)
    linhas.append("TOKENS GERADOS PELO ANALISADOR LEXICO")
    linhas.append("=" * 60)
    for numero, expressao, tokens in tokens_por_linha:
        linhas.append(f"\nLinha {numero}: {expressao.strip()}")
        linhas.append("-" * 40)
        for token in tokens:
            linhas.append(f"  {token.token_type.value:<12} | {token.lexeme!r}")
    linhas.append("\n" + "=" * 60)
    linhas.append(f"Total de linhas analisadas: {len(tokens_por_linha)}")
    total_tokens = sum(len(t) for _, _, t in tokens_por_linha)
    linhas.append(f"Total de tokens gerados:    {total_tokens}")
    linhas.append("=" * 60)
    linhas.append("")

    caminho = Path(nome_arquivo)
    caminho.write_text("\n".join(linhas), encoding="utf-8")


def exibir_resultados(resultados: list[float], expressoes: list[str]) -> None:
    """Exibe os resultados das expressoes em formato legivel."""
    print("=" * 50)
    print("RESULTADOS DA EXECUCAO")
    print("=" * 50)
    for i, (resultado, expr) in enumerate(zip(resultados, expressoes), start=1):
        if resultado == int(resultado):
            valor_fmt = f"{int(resultado)}"
        else:
            valor_fmt = f"{resultado:.1f}"
        print(f"  Linha {i}: {expr.strip()}")
        print(f"         = {valor_fmt}")
    print("=" * 50)
    print(f"  Total de expressoes avaliadas: {len(resultados)}")
    print("=" * 50)


exibirResultados = exibir_resultados

