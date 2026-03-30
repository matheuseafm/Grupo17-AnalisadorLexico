# Matheus Moreira - matheuseafm - Grupo 17
# Ponto de entrada: orquestra leitura, lexer, executor, geração de Assembly e saída.

from __future__ import annotations  # Permite anotações de tipo com nomes ainda não definidos (ex.: list[str] em Python 3.10+)

import sys  # Acesso a sys.argv (argumentos da linha de comando)
from pathlib import Path  # Extrai nome base do arquivo (stem) para nomes de saída

from assembly_generator import AssemblyGenerator  # Parser + gerador ARMv7
from executor import ExpressionExecutor  # Avalia expressões em Python (referência)
from io_utils import escrever_arquivo, exibir_resultados, ler_arquivo, salvar_tokens
from lexer_fsm import LexerError, parse_expressao  # AFD léxico + exceção de erro


def main(argv: list[str]) -> int:
    # argv[0] é o nome do script; precisamos de pelo menos o arquivo de entrada
    if len(argv) < 2:
        print("Uso: python main.py <arquivo_entrada.txt> [arquivo_saida.s]")
        return 1  # Código de saída de erro (convenção Unix)

    arquivo_entrada = argv[1]  # Primeiro argumento obrigatório: caminho do .txt
    stem = Path(arquivo_entrada).stem  # Nome sem extensão (ex.: "teste1" de "teste1.txt")
    # Segundo argumento opcional: onde gravar o .s; senão, <stem>.s
    arquivo_saida = argv[2] if len(argv) > 2 else f"{stem}.s"
    arquivo_tokens = f"{stem}_tokens.txt"  # Saída auxiliar com lista de tokens por linha

    # Etapa 1 do enunciado: lerArquivo — lê UTF-8, retorna lista de linhas
    try:
        linhas = ler_arquivo(arquivo_entrada)
    except OSError as exc:  # FileNotFoundError, permissão, etc.
        print(f"Erro ao abrir arquivo: {exc}")
        return 1

    gerador = AssemblyGenerator()  # Acumula IR e depois serializa Assembly
    executor = ExpressionExecutor()  # Estado: memória + histórico de resultados (RES)
    expressoes_avaliadas: list[str] = []  # Só linhas não vazias, na ordem, para exibir no fim
    tokens_por_linha: list[tuple[int, str, list]] = []  # (nº linha, texto, tokens) para salvar_tokens

    # enumerate(..., start=1): número da linha começa em 1 (como editores e mensagens de erro)
    for numero_linha, linha in enumerate(linhas, start=1):
        if not linha.strip():  # Ignora linhas só com espaços
            continue
        try:
            # Etapa 2: parseExpressao — AFD em lexer_fsm; retorna list[Token]
            tokens = parse_expressao(linha)
            tokens_por_linha.append((numero_linha, linha, tokens))

            # Etapa 3: executarExpressao — parse_tokens + avaliação da AST; atualiza memória/resultados
            executor.executar_expressao(tokens)
            expressoes_avaliadas.append(linha)

            # gerarAssembly — adiciona IR desta linha ao gerador (não grava arquivo ainda)
            gerador.adicionar_expressao(tokens, numero_linha)
        except (LexerError, ValueError, RuntimeError) as exc:
            # LexerError: léxico; ValueError: parser/codegen; RuntimeError: ExecutionError herda
            print(f"Erro na linha {numero_linha}: {exc}")
            return 1

    # Etapa 4: exibirResultados — imprime no stdout os valores calculados em Python
    exibir_resultados(executor.resultados, expressoes_avaliadas)

    # Etapa 5: salvarTokens — grava relatório legível dos tokens (<stem>_tokens.txt)
    salvar_tokens(arquivo_tokens, tokens_por_linha)
    print(f"Tokens salvos em: {arquivo_tokens}")

    # Etapa 6: gera o texto Assembly completo e escreve no disco
    assembly = gerador.gerar_programa()
    escrever_arquivo(arquivo_saida, assembly)
    print(f"Assembly gerado em: {arquivo_saida}")
    return 0  # Sucesso


if __name__ == "__main__":
    # SystemExit com o código retornado por main (0 = ok, 1 = erro)
    raise SystemExit(main(sys.argv))
