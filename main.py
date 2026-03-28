# Matheus Moreira - matheuseafm - Grupo 17
from __future__ import annotations

import sys
from pathlib import Path

from assembly_generator import AssemblyGenerator
from executor import ExpressionExecutor
from io_utils import escrever_arquivo, exibir_resultados, ler_arquivo, salvar_tokens
from lexer_fsm import LexerError, parse_expressao


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Uso: python main.py <arquivo_entrada.txt> [arquivo_saida.s]")
        return 1

    arquivo_entrada = argv[1]
    stem = Path(arquivo_entrada).stem
    arquivo_saida = argv[2] if len(argv) > 2 else f"{stem}.s"
    arquivo_tokens = f"{stem}_tokens.txt"

    # 1. lerArquivo
    try:
        linhas = ler_arquivo(arquivo_entrada)
    except OSError as exc:
        print(f"Erro ao abrir arquivo: {exc}")
        return 1

    gerador = AssemblyGenerator()
    executor = ExpressionExecutor()
    expressoes_avaliadas: list[str] = []
    tokens_por_linha: list[tuple[int, str, list]] = []

    for numero_linha, linha in enumerate(linhas, start=1):
        if not linha.strip():
            continue
        try:
            # 2. parseExpressao
            tokens = parse_expressao(linha)
            tokens_por_linha.append((numero_linha, linha, tokens))

            # 3. executarExpressao
            executor.executar_expressao(tokens)
            expressoes_avaliadas.append(linha)

            # gerarAssembly (acumula instruções)
            gerador.adicionar_expressao(tokens, numero_linha)
        except (LexerError, ValueError, RuntimeError) as exc:
            print(f"Erro na linha {numero_linha}: {exc}")
            return 1

    # 4. exibirResultados
    exibir_resultados(executor.resultados, expressoes_avaliadas)

    # 5. Salvar tokens gerados
    salvar_tokens(arquivo_tokens, tokens_por_linha)
    print(f"Tokens salvos em: {arquivo_tokens}")

    # 6. Gerar e salvar Assembly
    assembly = gerador.gerar_programa()
    escrever_arquivo(arquivo_saida, assembly)
    print(f"Assembly gerado em: {arquivo_saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
