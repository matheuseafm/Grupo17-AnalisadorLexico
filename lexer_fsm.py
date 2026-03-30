# Matheus Moreira - matheuseafm - Grupo 17
# Analisador léxico: AFD com estados implementados como funções (sem regex).

from __future__ import annotations

from dataclasses import dataclass

from tokens import OPERATORS, Token, TokenType


class LexerError(ValueError):
    # Erros de tokenização; ValueError permite captura junto com parser no main
    pass


@dataclass
class _FSMContext:
    line: str  # Linha inteira sendo analisada
    pos: int = 0  # Índice do caractere atual (cursor)
    paren_balance: int = 0  # +1 por '(', -1 por ')'; no fim deve ser 0
    tokens: list[Token] | None = None  # Lista acumulada de tokens emitidos

    def __post_init__(self) -> None:
        # Inicializa lista mutável (default mutável em campo dataclass seria bug)
        if self.tokens is None:
            self.tokens = []

    def current_char(self) -> str | None:
        # None = fim da linha (EOF da linha)
        if self.pos >= len(self.line):
            return None
        return self.line[self.pos]


def _state_initial(ctx: _FSMContext):
    # Estado inicial e de retorno: classifica o próximo caractere e despacha
    char = ctx.current_char()
    if char is None:
        return None  # Fim da linha: motor do AFD para
    if char.isspace():
        ctx.pos += 1  # Consome espaço e permanece neste estado
        return _state_initial
    if char == "(":
        ctx.tokens.append(Token(TokenType.LPAREN, char))
        ctx.paren_balance += 1
        ctx.pos += 1
        return _state_initial
    if char == ")":
        ctx.tokens.append(Token(TokenType.RPAREN, char))
        ctx.paren_balance -= 1
        if ctx.paren_balance < 0:
            raise LexerError("Parenteses desbalanceados: ')' sem abertura.")
        ctx.pos += 1
        return _state_initial
    if char.isdigit():
        return _state_number  # Transição para reconhecer literal numérico
    if char in "+-*/%^":
        return _state_operator  # Pode ser / ou início de //
    if char.isalpha():
        return _state_identifier  # RES ou identificador MEM
    raise LexerError(f"Token invalido: '{char}'.")


def _state_number(ctx: _FSMContext):
    # Consome sequência [0-9]+ ('.' [0-9]*)? no máximo um ponto
    start = ctx.pos  # Início do lexema numérico
    has_dot = False  # Se já vimos '.' (segundo ponto = erro)

    while True:
        char = ctx.current_char()
        if char is None:
            break  # Fim da linha: termina o número
        if char.isdigit():
            ctx.pos += 1
            continue
        if char == ".":
            if has_dot:
                raise LexerError("Numero malformado: ponto decimal duplicado.")
            has_dot = True
            ctx.pos += 1
            continue
        if char == ",":
            raise LexerError("Numero malformado: use ponto como separador decimal.")
        break  # Outro caractere: fim do token número

    lexeme = ctx.line[start:ctx.pos]  # Fatia [start, pos)
    if lexeme.startswith(".") or lexeme.endswith("."):
        raise LexerError(f"Numero malformado: '{lexeme}'.")
    if not lexeme:
        raise LexerError("Numero malformado.")

    token_type = TokenType.REAL if has_dot else TokenType.INT
    ctx.tokens.append(Token(token_type, lexeme))
    return _state_initial  # Volta ao despacho principal


def _state_operator(ctx: _FSMContext):
    # Um caractere de operador ou '//' (dois caracteres)
    char = ctx.current_char()
    if char is None:
        raise LexerError("Fim inesperado ao ler operador.")

    if char == "/":
        # Lookahead de 1: se próximo for '/', emite divisão inteira
        next_char = ctx.line[ctx.pos + 1] if ctx.pos + 1 < len(ctx.line) else None
        if next_char == "/":
            ctx.tokens.append(Token(TokenType.OPERATOR, "//"))
            ctx.pos += 2  # Consome os dois '/'
            return _state_initial

    if char in "+-*/%^":
        ctx.tokens.append(Token(TokenType.OPERATOR, char))
        ctx.pos += 1
        return _state_initial

    raise LexerError(f"Operador invalido: '{char}'.")


def _state_identifier(ctx: _FSMContext):
    # Uma ou mais letras consecutivas: RES ou IDENTIFIER (só maiúsculas)
    start = ctx.pos
    while True:
        char = ctx.current_char()
        if char is None:
            break
        if char.isalpha():
            ctx.pos += 1
            continue
        break

    lexeme = ctx.line[start:ctx.pos]
    if lexeme == "RES":
        ctx.tokens.append(Token(TokenType.RES, lexeme))
        return _state_initial

    if not lexeme.isupper():
        raise LexerError(
            f"Identificador invalido '{lexeme}': use apenas letras maiusculas."
        )

    ctx.tokens.append(Token(TokenType.IDENTIFIER, lexeme))
    return _state_initial


def _validar_tokens(tokens: list[Token]) -> None:
    # Garante que todo OPERATOR está em OPERATORS (defesa em profundidade)
    for token in tokens:
        if token.token_type == TokenType.OPERATOR and token.lexeme not in OPERATORS:
            raise LexerError(f"Operador invalido: '{token.lexeme}'.")


def parse_expressao(linha: str) -> list[Token]:
    # Motor do AFD: estado inicial; cada estado retorna o próximo ou None
    ctx = _FSMContext(linha)
    state = _state_initial

    while state is not None:
        state = state(ctx)

    if ctx.paren_balance != 0:
        raise LexerError("Parenteses desbalanceados.")

    _validar_tokens(ctx.tokens)
    return ctx.tokens


# Alias para manter nomenclatura solicitada no enunciado
parseExpressao = parse_expressao
