# Matheus Moreira - matheuseafm - Grupo 17
# =============================================================================
# lexer_fsm.py — Analisador léxico implementado como AFD (sem regex)
#
# Princípio: cada estado do autômato é uma função Python.
# O motor do AFD é o loop:
#
#     state = _state_initial
#     while state is not None:
#         state = state(ctx)
#
# Cada função de estado recebe o contexto (ctx), lê o caractere atual,
# emite tokens se necessário, avança a posição e retorna a PRÓXIMA função
# de estado — ou None para sinalizar que a análise terminou.
#
# Estados implementados:
#   _state_initial    → despacho: classifica o caractere e redireciona
#   _state_number     → consome dígitos (e no máximo um ponto decimal)
#   _state_operator   → consome operador de 1 ou 2 caracteres ('/' ou '//')
#   _state_identifier → consome letras maiúsculas (RES ou nome de memória)
# =============================================================================

from __future__ import annotations

# dataclass gera __init__ automático para _FSMContext
from dataclasses import dataclass

from tokens import OPERATORS, Token, TokenType


# LexerError é lançado pelo AFD quando encontra entrada inválida.
# Herda de ValueError para que main.py possa capturá-la junto com erros do parser.
class LexerError(ValueError):
    pass


# _FSMContext guarda todo o estado mutável do AFD durante a análise de UMA linha.
# É passado como argumento para cada função de estado.
@dataclass
class _FSMContext:
    line: str                    # A linha completa que está sendo analisada
    pos: int = 0                 # Índice do próximo caractere a ser lido (cursor)
    paren_balance: int = 0       # Contador: +1 ao abrir '(', -1 ao fechar ')'; deve ser 0 no fim
    tokens: list[Token] | None = None  # Lista onde os tokens reconhecidos são acumulados

    # __post_init__ é chamado automaticamente pelo dataclass após __init__.
    # É necessário porque None como default de campo mutável causaria bug em dataclass.
    def __post_init__(self) -> None:
        if self.tokens is None:
            self.tokens = []  # Inicializa a lista vazia para acumular tokens

    # current_char retorna o caractere na posição atual do cursor.
    # Retorna None quando o cursor passou do fim da linha (sinal de "EOF da linha").
    def current_char(self) -> str | None:
        if self.pos >= len(self.line):
            return None
        return self.line[self.pos]


# =============================================================================
# ESTADO 1: _state_initial
# Função: estado inicial e de retorno. É chamado antes de cada novo token.
# Olha o caractere atual e decide para qual estado transitar:
#   espaço      → permanece em _state_initial (ignora)
#   '('         → emite LPAREN, incrementa paren_balance, volta
#   ')'         → emite RPAREN, decrementa paren_balance, volta
#   dígito      → transita para _state_number
#   +-*/%^      → transita para _state_operator
#   letra       → transita para _state_identifier
#   None (EOF)  → retorna None, encerrando o motor do AFD
#   outro       → lança LexerError (token inválido)
# =============================================================================
def _state_initial(ctx: _FSMContext):
    char = ctx.current_char()

    # None = chegamos ao fim da linha; retornar None para o motor do AFD
    if char is None:
        return None

    # Espaço em branco: avança cursor e fica no mesmo estado (não emite token)
    if char.isspace():
        ctx.pos += 1
        return _state_initial

    # Parêntese de abertura: emite LPAREN e incrementa o contador de balanceamento
    if char == "(":
        ctx.tokens.append(Token(TokenType.LPAREN, char))
        ctx.paren_balance += 1
        ctx.pos += 1
        return _state_initial

    # Parêntese de fechamento: emite RPAREN e decrementa o contador
    # Se paren_balance ficar negativo, ')' apareceu sem um '(' correspondente
    if char == ")":
        ctx.tokens.append(Token(TokenType.RPAREN, char))
        ctx.paren_balance -= 1
        if ctx.paren_balance < 0:
            raise LexerError("Parenteses desbalanceados: ')' sem abertura.")
        ctx.pos += 1
        return _state_initial

    # Dígito: o próximo token é um número inteiro ou real
    if char.isdigit():
        return _state_number  # Transita para o estado de reconhecimento de número

    # Caractere de operador: pode ser simples (+, -, *, %, ^) ou duplo (//)
    if char in "+-*/%^":
        return _state_operator  # Transita para o estado de reconhecimento de operador

    # Letra: pode ser a palavra reservada RES ou um identificador de memória
    if char.isalpha():
        return _state_identifier  # Transita para o estado de reconhecimento de identificador

    # Qualquer outro caractere é inválido nesta linguagem
    raise LexerError(f"Token invalido: '{char}'.")


# =============================================================================
# ESTADO 2: _state_number
# Função: consumir uma sequência de dígitos com no máximo um ponto decimal.
# Reconhece: inteiros (ex.: 42) e reais (ex.: 3.14).
# Erros detectados:
#   - dois pontos decimais (3.14.5)
#   - vírgula no lugar de ponto (3,14)
#   - ponto no início ou fim do número (.5 ou 5.)
# Ao terminar, emite INT se sem ponto ou REAL se com ponto, e volta a _state_initial.
# =============================================================================
def _state_number(ctx: _FSMContext):
    start = ctx.pos   # Guarda a posição inicial para recortar o lexema depois
    has_dot = False   # Flag: já encontramos um '.'? Se sim, segundo '.' é erro.

    # Loop que consome o número caractere a caractere
    while True:
        char = ctx.current_char()

        # Fim da linha: o número termina aqui (sem erro)
        if char is None:
            break

        # Dígito normal: avança e continua consumindo o número
        if char.isdigit():
            ctx.pos += 1
            continue

        # Ponto decimal: aceito apenas uma vez
        if char == ".":
            if has_dot:
                raise LexerError("Numero malformado: ponto decimal duplicado.")
            has_dot = True
            ctx.pos += 1
            continue

        # Vírgula: erro comum de quem usa "3,14" em vez de "3.14"
        if char == ",":
            raise LexerError("Numero malformado: use ponto como separador decimal.")

        # Qualquer outro caractere termina o número (ex.: espaço, parêntese)
        break

    # Recorta o lexema do número a partir da linha original
    lexeme = ctx.line[start:ctx.pos]

    # ".5" ou "5." são mal formados: ponto não pode estar nas extremidades
    if lexeme.startswith(".") or lexeme.endswith("."):
        raise LexerError(f"Numero malformado: '{lexeme}'.")

    # Lexema vazio indicaria bug interno (não deveria acontecer se isdigit() foi checado)
    if not lexeme:
        raise LexerError("Numero malformado.")

    # Decide o tipo do token: REAL se viu '.', INT caso contrário
    token_type = TokenType.REAL if has_dot else TokenType.INT
    ctx.tokens.append(Token(token_type, lexeme))

    # Volta ao estado inicial para reconhecer o próximo token
    return _state_initial


# =============================================================================
# ESTADO 3: _state_operator
# Função: reconhecer operadores de 1 ou 2 caracteres.
# Caso especial: '/' pode ser divisão real '/' ou divisão inteira '//'.
# Para distinguir, faz LOOKAHEAD de 1 posição.
# Todos os demais operadores (+, -, *, %, ^) têm sempre 1 caractere.
# =============================================================================
def _state_operator(ctx: _FSMContext):
    char = ctx.current_char()

    # Não deveria acontecer se _state_initial verificou antes de transitar
    if char is None:
        raise LexerError("Fim inesperado ao ler operador.")

    # Tratamento especial para '/': verificar se o próximo caractere também é '/'
    if char == "/":
        # Lookahead: olha 1 posição à frente sem avançar o cursor ainda
        next_char = ctx.line[ctx.pos + 1] if ctx.pos + 1 < len(ctx.line) else None
        if next_char == "/":
            # É '//' (divisão inteira): emite um único token com lexema "//"
            ctx.tokens.append(Token(TokenType.OPERATOR, "//"))
            ctx.pos += 2  # Avança os 2 caracteres de uma vez
            return _state_initial

    # Operadores de 1 caractere: emite e avança apenas 1 posição
    if char in "+-*/%^":
        ctx.tokens.append(Token(TokenType.OPERATOR, char))
        ctx.pos += 1
        return _state_initial

    # Chegou aqui apenas se char é '/' mas o próximo não é '/' (caso /=)
    raise LexerError(f"Operador invalido: '{char}'.")


# =============================================================================
# ESTADO 4: _state_identifier
# Função: reconhecer sequências de letras.
# Dois resultados possíveis:
#   1. Lexema == "RES" → emite token do tipo RES (palavra reservada)
#   2. Lexema todo maiúsculo → emite token IDENTIFIER (nome de variável de memória)
#   3. Contém minúsculas ou misto → erro (convenção: só maiúsculas)
# =============================================================================
def _state_identifier(ctx: _FSMContext):
    start = ctx.pos  # Posição inicial do identificador

    # Consome letras consecutivas (não aceita dígitos ou outros caracteres aqui)
    while True:
        char = ctx.current_char()
        if char is None:
            break          # Fim da linha: termina o identificador
        if char.isalpha():
            ctx.pos += 1
            continue
        break              # Não-letra: fim do identificador

    # Recorta o lexema reconhecido
    lexeme = ctx.line[start:ctx.pos]

    # "RES" é a única palavra reservada: acessa o resultado de uma linha anterior
    if lexeme == "RES":
        ctx.tokens.append(Token(TokenType.RES, lexeme))
        return _state_initial

    # Qualquer identificador que não seja todo maiúsculo é inválido
    # (ex.: "mem" ou "Total" causariam erro aqui)
    if not lexeme.isupper():
        raise LexerError(
            f"Identificador invalido '{lexeme}': use apenas letras maiusculas."
        )

    # Identificador válido: nome de variável de memória (ex.: TOTAL, X, VALOR)
    ctx.tokens.append(Token(TokenType.IDENTIFIER, lexeme))
    return _state_initial


# =============================================================================
# _validar_tokens — passo de validação pós-AFD
# Percorre todos os tokens já emitidos e confirma que todo OPERATOR tem lexema
# pertencente ao conjunto OPERATORS. Isso é uma "defesa em profundidade":
# o estado _state_operator já filtrou a maioria, mas esta função garante
# consistência caso o código mude no futuro.
# =============================================================================
def _validar_tokens(tokens: list[Token]) -> None:
    for token in tokens:
        if token.token_type == TokenType.OPERATOR and token.lexeme not in OPERATORS:
            raise LexerError(f"Operador invalido: '{token.lexeme}'.")


# =============================================================================
# parse_expressao — ponto de entrada público do módulo
# Recebe uma linha de texto (string) e retorna a lista de tokens reconhecidos.
#
# Passo a passo:
#   1. Cria _FSMContext com a linha
#   2. Inicializa state = _state_initial (primeira função de estado)
#   3. Executa o motor: enquanto state não for None, chama state(ctx)
#      → cada chamada lê o caractere atual, emite token(s) e retorna o próximo estado
#   4. Ao sair do loop, verifica paren_balance (deve ser 0)
#   5. Valida os operadores emitidos
#   6. Retorna ctx.tokens (lista completa de tokens)
#
# Lança LexerError se qualquer etapa detectar entrada inválida.
# =============================================================================
def parse_expressao(linha: str) -> list[Token]:
    ctx = _FSMContext(linha)   # Contexto com cursor em 0, sem tokens ainda
    state = _state_initial     # Estado inicial do AFD

    # Motor do AFD: cada iteração avança pelo menos 1 posição (ou lança erro)
    while state is not None:
        state = state(ctx)     # Executa o estado atual e obtém o próximo

    # Após consumir toda a linha, verifica se todos os parênteses foram fechados
    if ctx.paren_balance != 0:
        raise LexerError("Parenteses desbalanceados.")

    # Validação adicional dos operadores reconhecidos
    _validar_tokens(ctx.tokens)

    return ctx.tokens  # Lista de tokens pronta para o parser e o executor


# Alias para manter o nome exato exigido pelo enunciado da disciplina
parseExpressao = parse_expressao
