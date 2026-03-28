# Matheus Moreira - matheuseafm
from __future__ import annotations

import sys
from pathlib import Path

from assembly_generator import AssemblyGenerator
from io_utils import escrever_arquivo, ler_arquivo
from lexer_fsm import LexerError, parse_expressao


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Uso: python main.py <arquivo_entrada.txt> [arquivo_saida.s]")
        return 1

    arquivo_entrada = argv[1]
    arquivo_saida = argv[2] if len(argv) > 2 else f"{Path(arquivo_entrada).stem}.s"

    try:
        linhas = ler_arquivo(arquivo_entrada)
    except OSError as exc:
        print(f"Erro ao abrir arquivo: {exc}")
        return 1

    gerador = AssemblyGenerator()

    for numero_linha, linha in enumerate(linhas, start=1):
        if not linha.strip():
            continue
        try:
            tokens = parse_expressao(linha)
            gerador.adicionar_expressao(tokens, numero_linha)
        except (LexerError, ValueError) as exc:
            print(f"Erro na linha {numero_linha}: {exc}")
            return 1

    assembly = gerador.gerar_programa()
    escrever_arquivo(arquivo_saida, assembly)
    print(f"Assembly gerado em: {arquivo_saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

