# Matheus Moreira - matheuseafm - Grupo 17
# =============================================================================
# main.py — Ponto de entrada do programa
#
# Orquestra o pipeline completo de 4 etapas pedidas no enunciado:
#   1. lerArquivo       → ler linhas do arquivo de entrada
#   2. parseExpressao   → tokenizar cada linha (AFD em lexer_fsm.py)
#   3. executarExpressao → avaliar cada expressão em Python (executor.py)
#   4. exibirResultados → mostrar resultados no terminal
#   + salvarTokens      → gravar tokens em _tokens.txt
#   + gerarAssembly     → gerar e gravar código Assembly ARMv7
#
# Uso: python main.py <arquivo_entrada.txt> [arquivo_saida.s]
# =============================================================================

from __future__ import annotations  # Permite anotar tipos com nomes ainda não definidos

import sys           # sys.argv: lista de argumentos da linha de comando
from pathlib import Path  # Manipulação de caminhos de arquivo multiplataforma

# Importa o gerador de Assembly (parser + emissão de código ARMv7)
from assembly_generator import AssemblyGenerator

# Importa o executor Python (avalia as expressões como referência de validação)
from executor import ExpressionExecutor

# Importa as funções de I/O: ler arquivo, escrever arquivo, salvar tokens, exibir resultados
from io_utils import escrever_arquivo, exibir_resultados, ler_arquivo, salvar_tokens

# Importa o analisador léxico (AFD) e a exceção de erro léxico
from lexer_fsm import LexerError, parse_expressao


# main recebe sys.argv como parâmetro para facilitar testes (pode ser chamada com lista customizada)
# Retorna 0 em caso de sucesso ou 1 em caso de erro (convenção Unix de código de saída)
def main(argv: list[str]) -> int:

    # argv[0] é sempre o nome do script (main.py); precisamos de pelo menos argv[1] (arquivo de entrada)
    if len(argv) < 2:
        print("Uso: python main.py <arquivo_entrada.txt> [arquivo_saida.s]")
        return 1  # Retorna 1 sinaliza erro para o sistema operacional

    # Argumento obrigatório: caminho do arquivo .txt com as expressões RPN
    arquivo_entrada = argv[1]

    # Path.stem extrai o nome sem extensão. Ex.: "teste1.txt" → stem = "teste1"
    stem = Path(arquivo_entrada).stem

    # Argumento opcional: arquivo de saída Assembly. Padrão: mesmo nome do input com extensão .s
    arquivo_saida = argv[2] if len(argv) > 2 else f"{stem}.s"

    # Arquivo de saída com a lista de tokens gerados (sempre derivado do nome de entrada)
    arquivo_tokens = f"{stem}_tokens.txt"

    # ----- ETAPA 1: lerArquivo -----
    # Chama ler_arquivo que lê o arquivo UTF-8 e retorna lista de strings (uma por linha).
    # Tratado com try/except para capturar arquivo não encontrado ou caminho inválido.
    try:
        linhas = ler_arquivo(arquivo_entrada)
    except OSError as exc:
        print(f"Erro ao abrir arquivo: {exc}")
        return 1

    # Cria o gerador de Assembly: vai acumular as instruções de cada linha
    gerador = AssemblyGenerator()

    # Cria o executor: mantém o estado entre expressões (memória e histórico de resultados)
    executor = ExpressionExecutor()

    # Lista das linhas não-vazias (textos) que foram avaliadas com sucesso
    # Usada depois para exibir junto com os resultados
    expressoes_avaliadas: list[str] = []

    # Lista de tuplas (número da linha, texto da linha, tokens) para gerar o arquivo de tokens
    tokens_por_linha: list[tuple[int, str, list]] = []

    # Itera pelas linhas do arquivo. enumerate(start=1) começa a contar do 1 (como editores de texto)
    for numero_linha, linha in enumerate(linhas, start=1):

        # Linhas vazias ou com apenas espaços são ignoradas silenciosamente
        if not linha.strip():
            continue

        # Cada linha é processada dentro de try/except para que um erro em uma linha
        # interrompa com mensagem clara indicando qual linha causou o problema
        try:
            # ----- ETAPA 2: parseExpressao -----
            # Executa o AFD sobre a linha e retorna lista de Token.
            # Pode lançar LexerError se houver caractere inválido, parêntese desbalanceado, etc.
            tokens = parse_expressao(linha)

            # Guarda para depois gravar no arquivo de tokens
            tokens_por_linha.append((numero_linha, linha, tokens))

            # ----- ETAPA 3: executarExpressao -----
            # Avalia a expressão em Python usando a AST construída pelo parser.
            # Atualiza o estado interno do executor (memória e histórico de resultados).
            # Pode lançar ExecutionError (divisão por zero, memória não definida, RES inválido).
            executor.executar_expressao(tokens)
            expressoes_avaliadas.append(linha)

            # ----- gerarAssembly -----
            # Converte os tokens em nós de AST e gera a representação intermediária (IR).
            # Não grava nada em disco ainda — apenas acumula as instruções no gerador.
            gerador.adicionar_expressao(tokens, numero_linha)

        except (LexerError, ValueError, RuntimeError) as exc:
            # LexerError: token inválido ou parênteses desbalanceados (vem de lexer_fsm)
            # ValueError: erro no parser ou no gerador de Assembly (vem de assembly_generator)
            # RuntimeError: ExecutionError herda de RuntimeError (vem de executor)
            print(f"Erro na linha {numero_linha}: {exc}")
            return 1  # Interrompe o programa e sinaliza erro

    # ----- ETAPA 4: exibirResultados -----
    # Imprime no terminal cada expressão com seu resultado calculado em Python.
    # Inteiros são exibidos sem ".0"; reais com 1 casa decimal.
    exibir_resultados(executor.resultados, expressoes_avaliadas)

    # ----- salvarTokens -----
    # Grava no arquivo _tokens.txt o relatório de tokens por linha (tipo | lexema).
    salvar_tokens(arquivo_tokens, tokens_por_linha)
    print(f"Tokens salvos em: {arquivo_tokens}")

    # ----- Geração e gravação do Assembly -----
    # gerar_programa() serializa todas as instruções acumuladas em texto Assembly ARMv7.
    # escrever_arquivo salva esse texto no arquivo .s com encoding UTF-8.
    assembly = gerador.gerar_programa()
    escrever_arquivo(arquivo_saida, assembly)
    print(f"Assembly gerado em: {arquivo_saida}")

    return 0  # Código 0 = sucesso


# Bloco de execução direta: só executa main quando este arquivo for rodado diretamente.
# Se fosse importado por outro módulo (ex.: testes), main NÃO seria chamado automaticamente.
if __name__ == "__main__":
    # raise SystemExit propaga o código de retorno (0 ou 1) como código de saída do processo
    raise SystemExit(main(sys.argv))
