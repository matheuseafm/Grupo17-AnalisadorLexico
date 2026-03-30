# Matheus Moreira - matheuseafm - Grupo 17
# =============================================================================
# io_utils.py — Utilitários de entrada e saída
#
# Contém 4 funções públicas:
#   ler_arquivo      → lê o arquivo de entrada e retorna lista de linhas
#   escrever_arquivo → grava string (código Assembly) em arquivo no disco
#   salvar_tokens    → grava relatório de tokens por linha em arquivo .txt
#   exibir_resultados → imprime resultados das expressões no terminal
# =============================================================================

from __future__ import annotations

# Path: API moderna e multiplataforma para trabalhar com caminhos de arquivo.
# Substitui os.path e open() com uma interface mais legível.
from pathlib import Path


# =============================================================================
# ler_arquivo
# Recebe: nome_arquivo (str) — caminho do arquivo de entrada
# Retorna: list[str] — uma string por linha, sem o \n final
# Lança: FileNotFoundError se o arquivo não existir
#        IsADirectoryError se o caminho for um diretório, não um arquivo
# Uso: chamada na etapa 1 do pipeline (lerArquivo no enunciado)
# =============================================================================
def ler_arquivo(nome_arquivo: str) -> list[str]:
    # Converte a string do caminho em objeto Path para usar os métodos .exists(), .is_file()
    caminho = Path(nome_arquivo)

    # Valida se o arquivo existe antes de tentar abrir (mensagem de erro mais clara)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {nome_arquivo}")

    # Valida que não é um diretório (path pode existir mas ser uma pasta)
    if not caminho.is_file():
        raise IsADirectoryError(f"Caminho nao e arquivo: {nome_arquivo}")

    # read_text lê o arquivo inteiro como string. encoding="utf-8" garante suporte a acentos.
    # splitlines() divide em lista de linhas sem incluir o '\n' (evita linha vazia extra no fim)
    return caminho.read_text(encoding="utf-8").splitlines()


# =============================================================================
# escrever_arquivo
# Recebe: nome_arquivo (str) — caminho de destino
#         conteudo (str) — texto a ser gravado (código Assembly gerado)
# Retorna: None
# Comportamento: sobrescreve o arquivo se já existir (comportamento padrão de write_text)
# =============================================================================
def escrever_arquivo(nome_arquivo: str, conteudo: str) -> None:
    caminho = Path(nome_arquivo)
    # write_text cria o arquivo se não existir ou sobrescreve se já existir
    caminho.write_text(conteudo, encoding="utf-8")


# =============================================================================
# salvar_tokens
# Recebe: nome_arquivo (str) — caminho do arquivo de saída (_tokens.txt)
#         tokens_por_linha (list) — lista de tuplas (numero_linha, texto_linha, lista_de_tokens)
# Retorna: None
# Gera um arquivo legível com os tokens de cada linha listados em formato tabular.
# =============================================================================
def salvar_tokens(
    nome_arquivo: str,
    tokens_por_linha: list[tuple[int, str, list]],
) -> None:
    # Acumula as linhas do arquivo em uma lista (eficiente: concatena ao final)
    linhas: list[str] = []

    # Cabeçalho decorativo do arquivo de tokens
    linhas.append("=" * 60)
    linhas.append("TOKENS GERADOS PELO ANALISADOR LEXICO")
    linhas.append("=" * 60)

    # Para cada linha do arquivo de entrada que teve tokens reconhecidos:
    for numero, expressao, tokens in tokens_por_linha:
        # Exibe o número da linha original e o texto da expressão
        linhas.append(f"\nLinha {numero}: {expressao.strip()}")
        linhas.append("-" * 40)

        # Para cada token da linha, exibe o tipo e o lexema
        for token in tokens:
            # :<12 alinha o tipo à esquerda em 12 caracteres (visual tabular)
            # !r coloca o lexema entre aspas para facilitar leitura (ex.: "'+'")
            linhas.append(f"  {token.token_type.value:<12} | {token.lexeme!r}")

    # Rodapé com totais
    linhas.append("\n" + "=" * 60)
    linhas.append(f"Total de linhas analisadas: {len(tokens_por_linha)}")

    # sum(len(t) for ...) conta todos os tokens de todas as linhas
    total_tokens = sum(len(t) for _, _, t in tokens_por_linha)
    linhas.append(f"Total de tokens gerados:    {total_tokens}")
    linhas.append("=" * 60)
    linhas.append("")  # Linha vazia final

    # Junta tudo em uma única string separada por \n e grava no arquivo
    caminho = Path(nome_arquivo)
    caminho.write_text("\n".join(linhas), encoding="utf-8")


# =============================================================================
# exibir_resultados
# Recebe: resultados (list[float]) — valores calculados pelo executor Python
#         expressoes (list[str]) — textos das expressões (mesma ordem dos resultados)
# Retorna: None
# Imprime no terminal cada expressão com seu resultado, formatado sem decimais
# desnecessárias (ex.: 5.0 → "5", mas 4.5 → "4.5").
# =============================================================================
def exibir_resultados(resultados: list[float], expressoes: list[str]) -> None:
    print("=" * 50)
    print("RESULTADOS DA EXECUCAO")
    print("=" * 50)

    # zip emparelha os resultados com as expressões na mesma ordem
    # enumerate(start=1) conta a partir do 1 para exibir o número da linha
    for i, (resultado, expr) in enumerate(zip(resultados, expressoes), start=1):

        # Se o float é inteiro "puro" (ex.: 5.0 == 5), exibe sem casas decimais
        # Caso contrário, exibe com 1 casa decimal (ex.: 4.5, 5.14 → "5.1")
        if resultado == int(resultado):
            valor_fmt = f"{int(resultado)}"
        else:
            valor_fmt = f"{resultado:.1f}"

        print(f"  Linha {i}: {expr.strip()}")
        print(f"         = {valor_fmt}")

    print("=" * 50)
    print(f"  Total de expressoes avaliadas: {len(resultados)}")
    print("=" * 50)


# Alias exigido pelo enunciado da disciplina (nome em camelCase)
exibirResultados = exibir_resultados
